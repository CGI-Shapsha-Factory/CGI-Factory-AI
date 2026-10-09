import { expect, test } from 'claude-code/testing'

import { debugPrompt, isFinished, issueFromBranch, pickIssue, isPrCreate, parsePrUrl, toChecks, trimLog } from '../hooks/ci'

const PR = 'https://github.com/acme/app/pull/42'
const ISSUE = {
  number: 12,
  title: 'Exporter le diagnostic en PDF',
  url: 'https://github.com/acme/app/issues/12',
  state: 'OPEN',
  body: 'Court.',
  labels: { nodes: [{ name: 'feature' }] },
  assignees: { nodes: [{ login: 'jcholet' }] },
}
const CHECKS = JSON.stringify([
  { name: 'lint', workflow: 'CI', bucket: 'pass', link: 'https://github.com/acme/app/actions/runs/7/job/70' },
  { name: 'tests', workflow: 'CI', bucket: 'fail', link: 'https://github.com/acme/app/actions/runs/7/job/71' },
])

test('helpers read gh output', async () => {
  expect(isPrCreate('git push && gh pr create --fill')).toBe(true)
  expect(isPrCreate('gh pr view')).toBe(false)
  expect(issueFromBranch('feature/12-export')).toBe(12)
  const mention = { __typename: 'CrossReferencedEvent', source: { ...ISSUE, number: 64 } }
  const manual = { __typename: 'ConnectedEvent', subject: { ...ISSUE, number: 70 } }
  expect(pickIssue(undefined, [mention])?.number).toBe(64)
  expect(pickIssue(undefined, [manual, mention])?.number).toBe(70)
  expect(pickIssue(ISSUE, [manual])?.number).toBe(12)
  expect(pickIssue(undefined, [{ __typename: 'CrossReferencedEvent', source: {} }])).toBeUndefined()
  expect(issueFromBranch('fix/ano-lot3')).toBeUndefined()
  expect(parsePrUrl(`Created ${PR}\n`)).toEqual({ repo: 'acme/app', number: 42, url: PR })
  const checks = toChecks(CHECKS)
  expect(checks[1]).toMatchObject({ bucket: 'fail', runId: '7', jobId: '71', workflow: 'CI' })
  expect(isFinished(checks)).toBe(true)
  const prompt = debugPrompt({ number: 42, url: PR, title: '', repo: 'acme/app' }, checks[1]!, '- boom')
  expect(prompt).toContain('gh run view 7 -R acme/app --job 71 --log-failed')
  expect(prompt).toContain('- boom')
  expect(prompt).toContain('Ne commite pas')
  expect(trimLog('tests\tRun npm test\t2026-10-09T10:00:00.123Z Error: boom')).toBe('[Run npm test] Error: boom')
})

test('gh pr create starts the watch and a red job gets a French summary', async ($, on) => {
  const ran: string[][] = []
  const toasts: string[] = []
  const submitted: string[] = []
  on('prompt.submit', ($, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', ($, e) => {
    toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.open', () => ({ value: { isOpen: true } }) as never)
  on('tool.call', { tool: 'Bash' }, () => ({ result: { stdout: PR, stderr: '', interrupted: false }, text: PR }) as never)
  on('process.run', ($, e) => {
    ran.push([...e.argv])
    const out = e.argv[1] === 'pr' ? CHECKS : 'tests\tRun npm test\t2026-10-09T10:00:00Z Error: expected 1 to be 2'
    if (e.argv[1] === 'api') {
      const q = e.argv.find(x => x.startsWith('query=')) ?? ''
      const stdout = q.includes('projectItems')
        ? JSON.stringify({ errors: [{ type: 'INSUFFICIENT_SCOPES', message: 'read:project' }] })
        : JSON.stringify({
            data: { repository: { pullRequest: { headRefName: '12-export', closingIssuesReferences: { nodes: [ISSUE] } } } },
          })
      return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
    }
    return { value: { exitCode: 0, stdout: out, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('model.complete', () => ({
    value: {
    isAnswered: true as const,
    text: '- Étape **Run npm test** : `expected 1 to be 2`',
    usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 },
    },
  }))

  await $.tool.call({ tool: 'Bash', command: 'gh pr create --fill' })
  expect(ran.some(a => a.join(' ').startsWith('gh pr checks 42 -R acme/app'))).toBe(true)
  expect(toasts.some(t => t.includes('1 job(s) en échec'))).toBe(true)

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'ci-watch', surface, component: 'Pane', requestId: 'ci-watch', props: {} as never })
    expect(await ui.find({ text: /CI en échec \(1 job\)/ })).toBeDefined()
    expect(await ui.find({ text: /#12  Exporter le diagnostic en PDF/ })).toBeDefined()
    expect(await ui.find({ text: /gh auth refresh -s read:project/ })).toBeDefined()
    await ui.press({ key: 'job:71:tests' })
    expect(await ui.find({ text: /expected 1 to be 2/ })).toBeDefined()
    expect(ran.some(a => a.includes('--log-failed') && a.includes('71'))).toBe(true)
    await ui.press({ key: 'debug:71:tests' })
    expect(submitted.at(-1)).toContain('« tests »')
    await ui.press({ key: 'job:71:tests' })
    await ui.unmount()
  }
})

for (const [label, body, expected, absent] of [
  ['long body, model fails', 'x'.repeat(400), /Résumé indisponible \(api-error 529/, /Résumé en cours/],
  ['empty body', '', undefined, /Résumé (en cours|indisponible)/],
] as const) {
  test(`ticket summary: ${label}`, async ($, on) => {
    on('tool.call', { tool: 'Bash' }, () => ({ result: { stdout: PR, stderr: '', interrupted: false }, text: PR }) as never)
    on('ui.status', () => ({ value: undefined }))
    on('ui.toast', () => ({ value: undefined }))
    on('ui.open', () => ({ value: { isOpen: true } }) as never)
    on('process.run', ($, e) => {
      const issue = { ...ISSUE, body }
      const stdout =
        e.argv[1] === 'api'
          ? JSON.stringify({ data: { repository: { pullRequest: { headRefName: 'x', closingIssuesReferences: { nodes: [issue] } } } } })
          : CHECKS
      return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
    })
    on('model.complete', () => ({
      value: {
        isAnswered: false as const,
        reason: 'api-error' as const,
        status: 529,
        error: 'overloaded' as never,
        usage: { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 },
      },
    }) as never)

    await $.tool.call({ tool: 'Bash', command: 'gh pr create --fill' })
    const ui = await $.ui.mount({ plugin: 'ci-watch', surface: 'desktop', component: 'Pane', requestId: 'ci-watch', props: {} as never })
    expect(await ui.find({ text: /#12  Exporter le diagnostic en PDF/ })).toBeDefined()
    for (let i = 0; i < 50 && expected && !(await ui.find({ text: expected })); i++) await ui.redraw()
    if (expected) expect(await ui.find({ text: expected })).toBeDefined()
    expect(await ui.find({ text: absent })).toBeUndefined()
    await ui.unmount()
  })
}
