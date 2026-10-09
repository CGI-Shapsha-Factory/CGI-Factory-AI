import type { CiBucket, CiCheck, CiPr } from '../types'

export const LOG_CHARS = 14_000

const PR_URL = /https:\/\/github\.com\/([\w.-]+\/[\w.-]+)\/pull\/(\d+)/
const GH_PR_CREATE = /(^|[;&|\s(])gh\s+pr\s+create\b/
const JOB_LINK = /\/actions\/runs\/(\d+)(?:\/job\/(\d+))?/

export const ICON: Record<CiBucket, string> = { pass: '✓', fail: '✗', pending: '●', skipping: '–', cancel: '⊘' }
export const LABEL: Record<CiBucket, string> = {
  pass: 'Réussi',
  fail: 'Échec',
  pending: 'En cours',
  skipping: 'Ignoré',
  cancel: 'Annulé',
}
export const COLOR: Record<CiBucket, string> = {
  pass: 'success',
  fail: 'error',
  pending: 'warning',
  skipping: 'inactive',
  cancel: 'inactive',
}

export function parsePrUrl(text: string): { repo: string; number: number; url: string } | undefined {
  const m = PR_URL.exec(text)
  return m?.[1] ? { repo: m[1], number: Number(m[2]), url: m[0] } : undefined
}

export function isPrCreate(command: string): boolean {
  return GH_PR_CREATE.test(command)
}

type GhCheck = { name?: string; workflow?: string; bucket?: string; link?: string }

export function toChecks(json: string): CiCheck[] {
  const raw = JSON.parse(json) as GhCheck[]
  return raw.map((c, i) => {
    const link = c.link ?? ''
    const m = JOB_LINK.exec(link)
    const bucket = (['pass', 'fail', 'pending', 'skipping', 'cancel'] as const).find(b => b === c.bucket) ?? 'pending'
    return {
      key: `${m?.[2] ?? m?.[1] ?? i}:${c.name ?? ''}`,
      workflow: c.workflow || 'Autres checks',
      name: c.name ?? '?',
      bucket,
      link,
      runId: m?.[1],
      jobId: m?.[2],
    }
  })
}

export function isFinished(checks: readonly CiCheck[]): boolean {
  return checks.length > 0 && checks.every(c => c.bucket !== 'pending')
}

const ERROR_LINE = /##\[error\]|\bFAILED\b|^E\s{2,}|Traceback|\b\w*(Error|Exception)\b|\berror\b|exit code [1-9]/i
const CONTEXT = 12
const TAIL = 40

/**
 * Extrait la partie utile d'un log `--log-failed` : sans horodatage ni préfixe de job, sans le
 * nettoyage qui suit la dernière `##[error]`, et, s'il reste trop long, les blocs autour des
 * lignes d'erreur plus la fin.
 */
export function trimLog(log: string): string {
  let lines = log
    .split('\n')
    .map(l => {
      const parts = l.split('\t')
      const step = parts[1] ?? ''
      const body = parts.length >= 3 ? parts.slice(2).join('\t') : l
      const prefix = parts.length >= 3 && step !== 'UNKNOWN STEP' ? `[${step}] ` : ''
      return prefix + body.replace(/^﻿?\d{4}-\d\d-\d\dT[\d:.]+Z\s?/, '')
    })
    .filter(l => l.trim() !== '' && !/Node\.js \d+ (is|actions are) deprecated/.test(l))

  const lastError = lines.findLastIndex(l => l.includes('##[error]'))
  if (lastError >= 0) lines = lines.slice(0, lastError + 1)

  const whole = lines.join('\n')
  if (whole.length <= LOG_CHARS) return whole

  const keep = new Set<number>()
  lines.forEach((l, i) => {
    if (!ERROR_LINE.test(l)) return
    for (let j = Math.max(0, i - CONTEXT); j <= Math.min(lines.length - 1, i + CONTEXT); j++) keep.add(j)
  })
  for (let j = Math.max(0, lines.length - TAIL); j < lines.length; j++) keep.add(j)

  const out: string[] = []
  let prev = -1
  for (const i of [...keep].sort((a, b) => a - b)) {
    if (prev >= 0 && i > prev + 1) out.push('…')
    out.push(lines[i] ?? '')
    prev = i
  }
  const excerpt = out.join('\n')
  return excerpt.length > LOG_CHARS ? excerpt.slice(-LOG_CHARS) : excerpt
}

export function debugPrompt(pr: CiPr, check: CiCheck, summary: string | undefined): string {
  const job = check.jobId ? ` --job ${check.jobId}` : ''
  return [
    `La CI de la PR #${pr.number} (${pr.repo}) échoue sur le job « ${check.name} » du workflow « ${check.workflow} ».`,
    summary ? `\nPremier résumé de l'erreur :\n${summary}` : '',
    `\nDébugue cet échec :`,
    `1. Lis les logs d'échec complets : \`gh run view ${check.runId} -R ${pr.repo}${job} --log-failed\`.`,
    `2. Retrouve la cause dans le code de ce dépôt (le test, le fichier et la ligne en cause).`,
    `3. Reproduis l'échec en local si c'est faisable rapidement.`,
    `4. Explique la cause et propose un correctif, puis applique-le si tu es sûr de toi.`,
    `Ne commite pas et ne pousse rien sans me demander.`,
    `Logs sur GitHub : ${check.link}`,
  ]
    .filter(Boolean)
    .join('\n')
}

export type Tally = { pass: number; fail: number; pending: number; other: number; done: number }

export function countBuckets(checks: readonly CiCheck[]): Tally {
  const t: Tally = { pass: 0, fail: 0, pending: 0, other: 0, done: 0 }
  for (const c of checks) {
    if (c.bucket === 'pass') t.pass++
    else if (c.bucket === 'fail') t.fail++
    else if (c.bucket === 'pending') t.pending++
    else t.other++
  }
  t.done = checks.length - t.pending
  return t
}

export function verdictOf(total: number, t: Tally, finished: boolean): { title: string; color: string } {
  if (total === 0) return { title: 'En attente des premiers checks…', color: 'warning' }
  if (!finished) return { title: t.fail ? 'CI en cours, déjà des échecs' : 'CI en cours…', color: t.fail ? 'error' : 'warning' }
  return t.fail
    ? { title: `CI en échec (${t.fail} job${t.fail > 1 ? 's' : ''})`, color: 'error' }
    : { title: 'CI verte', color: 'success' }
}

const ORDER: CiBucket[] = ['pass', 'fail', 'pending', 'skipping', 'cancel']

/** Barre de progression en caractères pleins, un segment coloré par état. */
export function barSegments(checks: readonly CiCheck[], width: number): { bucket: CiBucket; text: string }[] {
  const n = checks.length
  if (n === 0) return []
  const segs = ORDER.map(b => ({ bucket: b, count: checks.filter(c => c.bucket === b).length })).filter(s => s.count)
  let used = 0
  return segs.map((s, i) => {
    const len = i === segs.length - 1 ? width - used : Math.max(1, Math.round((s.count / n) * width))
    used += len
    return { bucket: s.bucket, text: (s.bucket === 'pending' || s.bucket === 'skipping' || s.bucket === 'cancel' ? '░' : '█').repeat(Math.max(0, len)) }
  })
}

const HEX: Record<CiBucket, string> = {
  pass: '#2da44e',
  fail: '#cf222e',
  pending: '#d4a72c',
  skipping: '#8c959f',
  cancel: '#8c959f',
}

/** Même barre en SVG pour le desktop : segments arrondis, une petite marge entre eux. */
export function progressSvg(checks: readonly CiCheck[]): string {
  const W = 300
  const gap = 2
  const n = Math.max(1, checks.length)
  const sorted = [...checks].sort((a, b) => ORDER.indexOf(a.bucket) - ORDER.indexOf(b.bucket))
  const seg = (W - gap * (n - 1)) / n
  const rects = sorted
    .map((c, i) => {
      const x = (i * (seg + gap)).toFixed(2)
      const opacity = c.bucket === 'pending' ? ' opacity="0.55"' : ''
      return `<rect x="${x}" y="0" width="${seg.toFixed(2)}" height="8" rx="4" fill="${HEX[c.bucket]}"${opacity}/>`
    })
    .join('')
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} 8" preserveAspectRatio="none">${rects}</svg>`
}

/** Numéro d'issue porté par une branche créée depuis GitHub (« 12-titre », « feature/12-titre »). */
export function issueFromBranch(branch: string): number | undefined {
  const m = /(?:^|\/)(\d+)-/.exec(branch)
  return m ? Number(m[1]) : undefined
}

const ISSUE_FIELDS = 'number title url state body labels(first:5){nodes{name}} assignees(first:3){nodes{login}}'
const PROJECT_FIELDS =
  'projectItems(first:3){nodes{project{title url} fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}'

export function ticketQuery(withProject: boolean): string {
  const issue = withProject ? `${ISSUE_FIELDS} ${PROJECT_FIELDS}` : ISSUE_FIELDS
  return (
    'query($o:String!,$r:String!,$pr:Int!){repository(owner:$o,name:$r){pullRequest(number:$pr){headRefName ' +
    `closingIssuesReferences(first:1){nodes{${issue}}} ` +
    'timelineItems(last:20,itemTypes:[CONNECTED_EVENT,CROSS_REFERENCED_EVENT]){nodes{__typename ' +
    `... on ConnectedEvent{subject{... on Issue{${issue}}}} ` +
    `... on CrossReferencedEvent{source{... on Issue{${issue}}}}}}}}}`
  )
}

export function issueQuery(withProject: boolean): string {
  const issue = withProject ? `${ISSUE_FIELDS} ${PROJECT_FIELDS}` : ISSUE_FIELDS
  return `query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){${issue}}}}`
}

export type GhIssue = {
  number: number
  title: string
  url: string
  state: string
  body?: string
  labels?: { nodes: { name: string }[] }
  assignees?: { nodes: { login: string }[] }
  projectItems?: { nodes: { project?: { title: string; url: string }; fieldValueByName?: { name?: string } | null }[] }
}

export type TimelineNode = { __typename?: string; subject?: Partial<GhIssue>; source?: Partial<GhIssue> }

/**
 * L'issue liée à la PR, par ordre de confiance : celle qu'elle ferme, un lien manuel (section
 * Development), puis la dernière issue qui la mentionne.
 */
export function pickIssue(closing: GhIssue | undefined, timeline: readonly TimelineNode[]): GhIssue | undefined {
  if (closing) return closing
  const isIssue = (i: Partial<GhIssue> | undefined): i is GhIssue => typeof i?.number === 'number' && !!i.url
  const connected = [...timeline].reverse().find(n => n.__typename === 'ConnectedEvent' && isIssue(n.subject))
  if (connected) return connected.subject as GhIssue
  const mentioned = [...timeline].reverse().find(n => n.__typename === 'CrossReferencedEvent' && isIssue(n.source))
  return mentioned?.source as GhIssue | undefined
}
