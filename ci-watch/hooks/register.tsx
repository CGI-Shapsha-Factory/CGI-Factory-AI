import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { CiCheck, CiPr, CiSummary, CiTicket, CiWatch } from '../types'
import type { GhIssue, TimelineNode } from './ci'
import { barSegments, COLOR, countBuckets, debugPrompt, ICON, progressSvg, verdictOf, isFinished, issueFromBranch, issueQuery, pickIssue, ticketQuery, isPrCreate, parsePrUrl, toChecks, trimLog } from './ci'

const PANE = 'ci-watch'
const TITLE = 'CI GitHub Actions'
const POLL_MS = 12_000
const MAX_WATCH_MS = 3 * 60 * 60 * 1000

const IDLE: CiWatch = { pr: null, checks: [], isWatching: false, startedAt: 0, lastPoll: null, error: null }

const watch = atom({ plugin: 'ci-watch', key: 'watch' } as const, IDLE)
const selected = atom({ plugin: 'ci-watch', key: 'selected' } as const, null as string | null)
const ticket = atom({ plugin: 'ci-watch', key: 'ticket' } as const, { status: 'none' } as CiTicket)
const summaries = atom({ plugin: 'ci-watch', key: 'summaries' } as const, {} as Record<string, CiSummary>)

function statusLine(w: CiWatch): string | undefined {
  if (!w.pr) return undefined
  const n = w.checks.length
  const fail = w.checks.filter(c => c.bucket === 'fail').length
  const done = w.checks.filter(c => c.bucket !== 'pending').length
  if (n === 0) return `CI #${w.pr.number} : en attente…`
  if (!isFinished(w.checks)) return `CI #${w.pr.number} : ${done}/${n}${fail ? ` · ${fail} ✗` : ''}`
  return fail ? `CI #${w.pr.number} : ✗ ${fail} échec(s)` : `CI #${w.pr.number} : ✓ verte`
}

let polling = false

  async function poll($: EngineInterface): Promise<void> {
    const w = await read($, watch)
    if (!w.isWatching || !w.pr || polling) return
    polling = true
    try {
      const { exitCode, stdout, stderr } = await $.process.run(
        ['gh', 'pr', 'checks', String(w.pr.number), '-R', w.pr.repo, '--json', 'name,workflow,bucket,link'],
        { timeoutMs: 30_000 },
      )
      let checks: CiCheck[] = w.checks
      let error: string | null = null
      if (stdout.trim().startsWith('[')) checks = toChecks(stdout)
      else if (!/no checks reported/i.test(stderr) && exitCode !== 0) error = stderr.trim().slice(0, 300) || `gh a échoué (${exitCode})`

      const finished = isFinished(checks)
      const timedOut = Date.now() - w.startedAt > MAX_WATCH_MS
      const next: CiWatch = {
        ...w,
        checks,
        error,
        lastPoll: new Date().toLocaleTimeString('fr-FR'),
        isWatching: !finished && !timedOut,
      }
      await update($, watch, () => next)
      $.ui.status(statusLine(next))

      if (finished) {
        const fail = checks.filter(c => c.bucket === 'fail').length
        $.ui.toast(
          fail
            ? `CI de la PR #${w.pr.number} : ${fail} job(s) en échec. Clique dessus dans le panneau pour le résumé.`
            : `CI de la PR #${w.pr.number} : tout est vert ✓`,
        )
      } else if (timedOut) {
        $.ui.toast(`CI de la PR #${w.pr.number} : suivi arrêté après 3 h.`)
      }
    } catch (err) {
      await update($, watch, cur => ({ ...cur, error: String(err).slice(0, 300) }))
    } finally {
      polling = false
    }
  }

  async function startWatch($: EngineInterface, pr: CiPr, openPane: boolean): Promise<void> {
    await update($, watch, () => ({ ...IDLE, pr, isWatching: true, startedAt: Date.now() }))
    await update($, selected, () => null)
    await update($, summaries, () => ({}))
    await update($, ticket, () => ({ status: 'none' }))
    $.ui.status(`CI #${pr.number} : en attente…`)
    if (openPane) $.ui.open({ id: PANE, title: TITLE }).catch(() => undefined)
    await Promise.all([poll($), loadTicket($, pr)])
  }

  async function resolvePr($: EngineInterface, arg: string): Promise<CiPr | string> {
    const fromUrl = parsePrUrl(arg)
    const target = fromUrl ? [fromUrl.url] : arg ? [arg] : []
    const { exitCode, stdout, stderr } = await $.process.run(
      ['gh', 'pr', 'view', ...target, '--json', 'number,url,title'],
      { timeoutMs: 30_000 },
    )
    if (exitCode !== 0) return stderr.trim() || 'Aucune PR trouvée pour la branche courante.'
    const v = JSON.parse(stdout) as { number: number; url: string; title: string }
    const parsed = parsePrUrl(v.url)
    if (!parsed) return `URL de PR inattendue : ${v.url}`
    return { number: v.number, url: v.url, title: v.title, repo: parsed.repo }
  }

  async function graphql(
    $: EngineInterface,
    query: string,
    vars: Record<string, string | number>,
  ): Promise<{ data?: unknown; isScopeMissing: boolean }> {
    const argv = ['gh', 'api', 'graphql', '-f', `query=${query}`]
    for (const [k, v] of Object.entries(vars)) argv.push('-F', `${k}=${v}`)
    const { stdout, stderr } = await $.process.run(argv, { timeoutMs: 30_000 })
    const isScopeMissing = /INSUFFICIENT_SCOPES|read:project/.test(stdout + stderr)
    try {
      const parsed = JSON.parse(stdout) as { data?: unknown; errors?: unknown[] }
      return { data: parsed.errors?.length ? undefined : parsed.data, isScopeMissing }
    } catch {
      return { isScopeMissing }
    }
  }

  /** Cherche l'issue liée : d'abord celles que la PR ferme, sinon le numéro porté par la branche. */
  async function findIssue($: EngineInterface, pr: CiPr, withProject: boolean): Promise<{ issue?: GhIssue; isScopeMissing: boolean }> {
    const [o, r] = pr.repo.split('/') as [string, string]
    const first = await graphql($, ticketQuery(withProject), { o, r, pr: pr.number })
    if (first.isScopeMissing) return { isScopeMissing: true }
    type PrData = {
      repository?: {
        pullRequest?: {
          headRefName?: string
          closingIssuesReferences?: { nodes: GhIssue[] }
          timelineItems?: { nodes: TimelineNode[] }
        }
      }
    }
    const prData = (first.data as PrData | undefined)?.repository?.pullRequest
    const linked = pickIssue(prData?.closingIssuesReferences?.nodes[0], prData?.timelineItems?.nodes ?? [])
    if (linked) return { issue: linked, isScopeMissing: false }
    const n = issueFromBranch(prData?.headRefName ?? '')
    if (n === undefined) return { isScopeMissing: false }
    const second = await graphql($, issueQuery(withProject), { o, r, n })
    if (second.isScopeMissing) return { isScopeMissing: true }
    return { issue: (second.data as { repository?: { issue?: GhIssue } } | undefined)?.repository?.issue, isScopeMissing: false }
  }

  async function loadTicket($: EngineInterface, pr: CiPr): Promise<void> {
    await update($, ticket, () => ({ status: 'loading' }))
    try {
      let found = await findIssue($, pr, true)
      const needsProjectScope = found.isScopeMissing
      if (needsProjectScope) found = await findIssue($, pr, false)
      const issue = found.issue
      if (!issue) {
        await update($, ticket, () => ({ status: 'none' }))
        return
      }
      const item = issue.projectItems?.nodes.find(n => n.project)
      const body = (issue.body ?? '').trim()
      await update($, ticket, () => ({
        status: 'found' as const,
        number: issue.number,
        title: issue.title,
        url: issue.url,
        isOpen: issue.state === 'OPEN',
        labels: issue.labels?.nodes.map(l => l.name) ?? [],
        assignees: issue.assignees?.nodes.map(a => a.login) ?? [],
        project: item?.project ? { ...item.project, status: item.fieldValueByName?.name } : undefined,
        needsProjectScope,
        summary: body.length > 0 && body.length <= 280 ? body : undefined,
      }))
      if (body.length > 280) void summarizeTicket($, issue.number, issue.title, body)
    } catch {
      await update($, ticket, () => ({ status: 'none' }))
    }
  }

  async function summarizeTicket($: EngineInterface, n: number, title: string, body: string): Promise<void> {
    const r = await $.model.complete({
      model: 'haiku',
      maxTokens: 200,
      system:
        "Résume ce ticket en français en 2 phrases courtes : ce qu'il faut faire et pourquoi. " +
        'Pas de liste, pas de titre, pas de reformulation du titre.',
      prompt: `Ticket #${n} : ${title}\n\n${body.slice(0, 8000)}`,
    })
    if (r.isAnswered) await update($, ticket, t => (t.number === n ? { ...t, summary: r.text.trim() } : t))
  }

  async function summarize($: EngineInterface, check: CiCheck): Promise<void> {
    const w = await read($, watch)
    const have = (await read($, summaries))[check.key]
    if (!w.pr || have?.status === 'loading' || have?.status === 'done') return
    const set = (s: CiSummary) => update($, summaries, all => ({ ...all, [check.key]: s }))
    if (!check.runId) {
      await set({ status: 'error', text: `Pas un job GitHub Actions (lien : ${check.link || 'aucun'}).` })
      return
    }
    await set({ status: 'loading', text: 'Lecture des logs et résumé en cours…' })
    try {
      const job = check.jobId ? ['--job', check.jobId] : []
      const base = ['gh', 'run', 'view', check.runId, '-R', w.pr.repo, ...job]
      let { stdout } = await $.process.run([...base, '--log-failed'], { timeoutMs: 90_000 })
      if (!stdout.trim()) stdout = (await $.process.run([...base, '--log'], { timeoutMs: 90_000 })).stdout
      const log = trimLog(stdout)
      if (!log) {
        await set({ status: 'error', text: 'Logs vides ou indisponibles (run encore en cours, ou logs expirés).' })
        return
      }
      const r = await $.model.complete({
        model: 'haiku',
        maxTokens: 500,
        system:
          "Tu analyses des logs d'échec GitHub Actions. Réponds en français, en Markdown, 3 à 5 puces très courtes : " +
          "l'étape qui échoue, le message d'erreur clé (cité tel quel, entre backticks), le fichier:ligne s'il apparaît, " +
          'la cause probable et une piste de correction. Aucune introduction ni conclusion.',
        prompt: `Workflow : ${check.workflow}\nJob : ${check.name}\n\nLogs (fin) :\n${log}`,
      })
      await set(
        r.isAnswered
          ? { status: 'done', text: r.text.trim() }
          : { status: 'error', text: `Le résumé a échoué (${r.reason}). Réessaie.` },
      )
    } catch (err) {
      await set({ status: 'error', text: `Impossible de lire les logs : ${String(err).slice(0, 200)}` })
    }
  }

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'ci',
      description: 'Suit la CI de la PR de la branche courante (/ci [n° ou URL], /ci stop)',
      argumentHint: '[n° de PR | URL | stop]',
    })
    $.clock.every(POLL_MS, () => void poll($))
    const w = await read($, watch)
    $.ui.status(statusLine(w))
    return next(e)
  })

  on('command.run', { command: 'ci' }, async ($, e) => {
    const arg = e.args.trim()
    if (arg === 'stop') {
      await update($, watch, w => ({ ...w, isWatching: false }))
      $.ui.status(undefined)
      return { text: 'Suivi de la CI arrêté.' }
    }
    const pr = await resolvePr($, arg)
    if (typeof pr === 'string') return { text: `ci-watch : ${pr}` }
    await startWatch($, pr, false)
    await $.ui.open({ id: PANE, title: TITLE })
    return { text: `Suivi de la CI de la PR #${pr.number} (${pr.repo}).` }
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    if (ran.deny !== undefined || ran.isError || !isPrCreate(e.command)) return ran
    const found = parsePrUrl(ran.text ?? '')
    if (found) {
      await startWatch($, { number: found.number, url: found.url, title: '', repo: found.repo }, true)
    }
    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Markdown, Link } = $.ui.resolve(e)
    const w = await read($, watch)
    const sel = await read($, selected)
    const sums = await read($, summaries)
    const tk = await read($, ticket)
    const width = Math.max(20, (e.props.bodyColumns ?? 40) - 2)

    if (!w.pr) {
      return (
        <Box flexDirection="column" paddingX={1} gap={1}>
          <Text bold>Aucune PR suivie</Text>
          <Text dimColor>La CI s'affiche ici dès que Claude crée une PR (gh pr create).</Text>
          <Text dimColor>Ou tape /ci, /ci 42 ou /ci &lt;url de PR&gt;.</Text>
        </Box>
      )
    }

    const pr = w.pr
    const tally = countBuckets(w.checks)
    const finished = isFinished(w.checks)
    const workflows = [...new Set(w.checks.map(c => c.workflow))]
    const verdict = verdictOf(w.checks.length, tally, finished)

    const bar =
      w.checks.length === 0 ? null : e.surface === 'desktop' ? (
        (() => {
          const { Svg } = $.ui.resolve(e)
          return <Svg source={progressSvg(w.checks)} alt={`${tally.done} sur ${w.checks.length} checks terminés`} height={8} />
        })()
      ) : (
        <Box flexDirection="row">
          {barSegments(w.checks, Math.min(width, 48)).map(seg => (
            <Text color={COLOR[seg.bucket]}>{seg.text}</Text>
          ))}
        </Box>
      )

    return (
      <Box flexDirection="column" paddingX={1} paddingY={1} gap={2}>
        <Box flexDirection="column">
          <Link href={pr.url}>{`#${pr.number}${pr.title ? `  ${pr.title}` : ''}`}</Link>
          <Text dimColor>{pr.repo}</Text>
        </Box>

        {tk.status === 'found' && tk.url && (
          <Box flexDirection="column" borderStyle="round" borderColor="suggestion" paddingX={2} paddingY={1} gap={1}>
            <Box flexDirection="row" justifyContent="space-between">
              <Text dimColor>Ticket lié</Text>
              <Text color={tk.isOpen ? 'success' : 'merged'}>{tk.isOpen ? '● Ouvert' : '● Fermé'}</Text>
            </Box>
            <Link href={tk.url}>{`#${tk.number}  ${tk.title ?? ''}`}</Link>
            {(tk.project || (tk.assignees?.length ?? 0) > 0) && (
              <Box flexDirection="row" gap={3} flexWrap="wrap">
                {tk.project && (
                  <Text color="suggestion">{`▦ ${tk.project.title}${tk.project.status ? ` · ${tk.project.status}` : ''}`}</Text>
                )}
                {(tk.assignees?.length ?? 0) > 0 && <Text dimColor>{`@${tk.assignees?.join(', @')}`}</Text>}
              </Box>
            )}
            {(tk.labels?.length ?? 0) > 0 && <Text dimColor>{tk.labels?.map(l => `#${l}`).join('  ')}</Text>}
            {tk.summary ? (
              <Text>{tk.summary}</Text>
            ) : (
              <Text dimColor italic>Résumé en cours…</Text>
            )}
            {tk.needsProjectScope && (
              <Text dimColor>Statut du Project masqué : lance gh auth refresh -s read:project</Text>
            )}
          </Box>
        )}

        <Box flexDirection="column" borderStyle="round" borderColor={verdict.color} paddingX={2} paddingY={1} gap={1}>
          <Box flexDirection="row" justifyContent="space-between">
            <Text bold color={verdict.color}>{verdict.title}</Text>
            {w.checks.length > 0 && <Text dimColor>{`${tally.done}/${w.checks.length}`}</Text>}
          </Box>
          {bar}
          {w.checks.length > 0 && (
            <Box flexDirection="row" gap={3}>
              {tally.pass > 0 && <Text color="success">{`✓ ${tally.pass} réussi${tally.pass > 1 ? 's' : ''}`}</Text>}
              {tally.fail > 0 && <Text color="error">{`✗ ${tally.fail} en échec`}</Text>}
              {tally.pending > 0 && <Text color="warning">{`● ${tally.pending} en cours`}</Text>}
              {tally.other > 0 && <Text dimColor>{`– ${tally.other} ignoré${tally.other > 1 ? 's' : ''}`}</Text>}
            </Box>
          )}
        </Box>

        {w.error && <Text color="error">{`⚠ ${w.error}`}</Text>}

        {workflows.map(wf => {
          const jobs = w.checks.filter(c => c.workflow === wf)
          const wfDone = jobs.filter(c => c.bucket !== 'pending').length
          return (
            <Box flexDirection="column" gap={1}>
              <Box flexDirection="row" justifyContent="space-between" marginBottom={1}>
                <Text bold>{wf}</Text>
                <Text dimColor>{`${wfDone}/${jobs.length}`}</Text>
              </Box>
              {jobs.map(c => {
                const s = sums[c.key]
                const open = sel === c.key
                return (
                  <Box flexDirection="column">
                    <Box flexDirection="row" justifyContent="space-between" paddingLeft={2}>
                      <Text color={c.bucket === 'fail' ? 'error' : undefined} dimColor={c.bucket === 'skipping' || c.bucket === 'cancel'} wrap="truncate-end">
                        {c.name}
                      </Text>
                      {c.bucket === 'fail' ? (
                        <Button
                          key={`job:${c.key}`}
                          plain
                          label={open ? 'Masquer ▴' : "Voir l'erreur ▾"}
                          onPress={() => {
                            void update($, selected, cur => (cur === c.key ? null : c.key))
                            void summarize($, c)
                          }}
                        />
                      ) : (
                        <Text color={COLOR[c.bucket]} bold>{ICON[c.bucket]}</Text>
                      )}
                    </Box>
                    {open && s && (
                      <Box flexDirection="column" borderStyle="round" borderColor="error" paddingX={2} paddingY={1} marginLeft={2} marginTop={1} gap={1}>
                        <Text bold color="error">{`Pourquoi « ${c.name} » échoue`}</Text>
                        {s.status === 'done' ? (
                          <Markdown text={s.text} />
                        ) : (
                          <Text color={s.status === 'error' ? 'error' : 'warning'} italic={s.status === 'loading'}>
                            {s.status === 'loading' ? '● Analyse des logs en cours…' : s.text}
                          </Text>
                        )}
                        <Box flexDirection="row" gap={2} alignItems="center">
                          {c.runId && (
                            <Button
                              key={`debug:${c.key}`}
                              variant="primary"
                              label="Débuguer avec Claude"
                              onPress={() => {
                                void $.prompt.submit({
                                  text: debugPrompt(pr, c, s.status === 'done' ? s.text : undefined),
                                  asUser: true,
                                })
                                $.ui.toast(`Débogage de « ${c.name} » envoyé à Claude.`)
                              }}
                            />
                          )}
                          {c.link && <Link href={c.link}>Logs GitHub ↗</Link>}
                        </Box>
                      </Box>
                    )}
                  </Box>
                )
              })}
            </Box>
          )
        })}

        <Box flexDirection="row" justifyContent="space-between" alignItems="center" marginTop={1}>
          <Text dimColor>
            {w.isWatching ? `● Suivi actif · ${w.lastPoll ?? '—'}` : `Suivi terminé · ${w.lastPoll ?? '—'}`}
          </Text>
          <Box flexDirection="row" gap={1}>
            <Button
              key="refresh"
              label="Rafraîchir"
              onPress={async () => {
                await update($, watch, cur => ({ ...cur, isWatching: true, startedAt: Date.now() }))
                await poll($)
              }}
            />
            {w.isWatching && (
              <Button
                key="stop"
                label="Arrêter"
                onPress={() => {
                  void update($, watch, cur => ({ ...cur, isWatching: false }))
                }}
              />
            )}
          </Box>
        </Box>
      </Box>
    )
  })
}
