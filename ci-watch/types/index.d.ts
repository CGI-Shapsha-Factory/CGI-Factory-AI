export type CiBucket = 'pass' | 'fail' | 'pending' | 'skipping' | 'cancel'

export type CiCheck = {
  key: string
  workflow: string
  name: string
  bucket: CiBucket
  link: string
  runId?: string
  jobId?: string
}

export type CiPr = { number: number; url: string; title: string; repo: string }

export type CiSummary = { status: 'loading' | 'done' | 'error'; text: string }

export type CiTicket = {
  status: 'loading' | 'none' | 'found'
  number?: number
  title?: string
  url?: string
  isOpen?: boolean
  labels?: string[]
  assignees?: string[]
  project?: { title: string; url: string; status?: string }
  needsProjectScope?: boolean
  summary?: string
  summaryStatus?: 'none' | 'loading' | 'done' | 'error'
  summaryError?: string
}

export type CiWatch = {
  pr: CiPr | null
  checks: CiCheck[]
  isWatching: boolean
  startedAt: number
  lastPoll: string | null
  error: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'ci-watch': {
      watch: CiWatch
      selected: string | null
      summaries: Record<string, CiSummary>
      ticket: CiTicket
    }
  }
}
