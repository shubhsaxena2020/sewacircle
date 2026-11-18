import type {
  AttendanceRow, ContributionCard, Counterfactual, DropoutResult, EvalReport, ExtractionResult, LedgerEntry,
  LedgerVerification, RosterBoth, RosterOptions, RosterResult, TaskSpec, Volunteer,
} from './types'
import { mockHandler } from './mock'

export const MOCK = new URLSearchParams(location.search).has('mock')

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  if (MOCK) return mockHandler(method, path, body) as Promise<T>
  const r = await fetch('/api' + path, {
    method,
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!r.ok) {
    let detail = r.statusText
    try { detail = (await r.json()).detail ?? detail } catch { /* ignore */ }
    throw new ApiError(r.status, String(detail))
  }
  return r.json() as Promise<T>
}

export const defaultOptions: RosterOptions = {
  fairness: true, resilience: true, mentor_pairing: true, forced_in: [], forced_out: [], time_limit_s: 10, seed: 7,
}

export const api = {
  health: () => call<{ ok: boolean; disclaimer: string; model: string; llm_mode: string }>('GET', '/health'),
  meta: () => call<{ disclaimer: string; skills: Record<string, string> }>('GET', '/meta'),
  tasks: () => call<TaskSpec[]>('GET', '/tasks'),
  volunteers: () => call<Volunteer[]>('GET', '/volunteers'),
  extract: (brief_text: string) => call<ExtractionResult>('POST', '/extract-roles', { brief_text }),
  roster: (task: TaskSpec, options: RosterOptions) => call<RosterBoth>('POST', '/roster', { task, options }),
  whyNot: (task: TaskSpec, roster: RosterResult, volunteer_id: string, options: RosterOptions) =>
    call<Counterfactual>('POST', '/roster/why-not', { task, roster, volunteer_id, options }),
  dropout: (task: TaskSpec, roster: RosterResult, dropped_volunteer_id: string, options: RosterOptions) =>
    call<DropoutResult>('POST', '/roster/dropout', { task, roster, dropped_volunteer_id, options }),
  draft: (task: TaskSpec, host_notes: string, attendance_rows: AttendanceRow[], assignments: unknown[]) =>
    call<ContributionCard[]>('POST', '/evidence/draft', { task, host_notes, attendance_rows, assignments }),
  cards: () => call<ContributionCard[]>('GET', '/evidence/cards'),
  decide: (id: string, action: 'confirm' | 'correct' | 'reject', claimed_hours?: number) =>
    call<ContributionCard>('POST', `/evidence/${id}/${action}`, { actor: 'host', claimed_hours }),
  ledger: () => call<LedgerEntry[]>('GET', '/ledger'),
  verify: () => call<LedgerVerification>('GET', '/ledger/verify'),
  credential: (id: string) => call<Record<string, unknown>>('GET', `/export/credential/${id}`),
  evalReport: () => call<EvalReport>('GET', '/eval'),
}
