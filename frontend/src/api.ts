import type { AttendanceRow, ContributionCard, Counterfactual, DropoutResult, EvalReport, ExtractionResult, LedgerEntry, LedgerVerification, RosterBoth, RosterOptions, RosterResult, TaskSpec, Volunteer } from './types'
import { mockHandler } from './mock'

export const MOCK = ['true', '1'].includes(import.meta.env.VITE_MOCK ?? '') || new URLSearchParams(location.search).has('mock')
let demoRole = localStorage.getItem('sewa-role') || 'organiser'
export function setDemoRole(role: string) { demoRole = role }
export class ApiError extends Error { status: number; constructor(status: number, message: string) { super(message); this.status = status } }

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  if (MOCK) return mockHandler(method, path, body) as Promise<T>
  const response = await fetch('/api' + path, { method, headers: { 'X-Demo-Role': demoRole, ...(body === undefined ? {} : { 'Content-Type': 'application/json' }) }, body: body === undefined ? undefined : JSON.stringify(body) })
  if (!response.ok) { let detail = response.statusText; try { detail = (await response.json()).detail ?? detail } catch { /* API may return plain text */ } throw new ApiError(response.status, String(detail)) }
  return response.json() as Promise<T>
}

export const defaultOptions: RosterOptions = { fairness: true, resilience: true, mentor_pairing: true, forced_in: [], forced_out: [], opted_in_only: true, time_limit_s: 10, seed: 7 }
export const api = {
  health: () => call<{ ok: boolean; disclaimer: string; model: string; llm_mode: string }>('GET', '/health'),
  meta: () => call<{ disclaimer: string; skills: Record<string, string> }>('GET', '/meta'),
  tasks: () => call<TaskSpec[]>('GET', '/tasks'),
  tasksLang: (lang: string) => call<TaskSpec[]>('GET', `/tasks?lang=${lang}`),
  capabilities: (role = demoRole) => call<{ role: string; actions: string[]; screens?: string[]; demo_only?: boolean; note?: string }>('GET', `/capabilities?role=${role}`),
  geo: () => call<Record<string, unknown>>('GET', '/geo/tree'),
  driveStatus: () => call<Record<string, unknown>>('GET', '/drive/status'),
  share: (task_id: string) => call<{ share_key: string; path: string }>('POST', '/drive/share', { task_id }),
  drive: (key: string) => call<Record<string, unknown>>('GET', `/drive/${key}`),
  volunteers: () => call<Volunteer[]>('GET', '/volunteers'),
  extract: (brief_text: string) => call<ExtractionResult>('POST', '/extract-roles', { brief_text }),
  roster: (task: TaskSpec, options: RosterOptions, lang = 'en') => call<RosterBoth>('POST', '/roster', { task, options, lang }),
  whyNot: (task: TaskSpec, roster: RosterResult, volunteer_id: string, options: RosterOptions) => call<Counterfactual>('POST', '/roster/why-not', { task, roster, volunteer_id, options }),
  dropout: (task: TaskSpec, roster: RosterResult, dropped_volunteer_id: string, options: RosterOptions) => call<DropoutResult>('POST', '/roster/dropout', { task, roster, dropped_volunteer_id, options }),
  draft: (task: TaskSpec, host_notes: string, attendance_rows: AttendanceRow[], assignments: unknown[]) => call<ContributionCard[]>('POST', '/evidence/draft', { task, host_notes, attendance_rows, assignments }),
  cards: () => call<ContributionCard[]>('GET', '/evidence/cards'),
  decide: (id: string, action: 'confirm' | 'correct' | 'reject' | 'request_revision', claimed_hours?: number, reason?: string) => call<ContributionCard>('POST', `/evidence/${id}/${action}`, { actor: 'host', ...(claimed_hours === undefined ? {} : { claimed_hours }), ...(reason === undefined ? {} : { reason }) }),
  revision: (id: string, reason: string) => call<ContributionCard>('POST', `/evidence/${id}/request_revision`, { actor: 'host', reason }),
  ledger: () => call<LedgerEntry[]>('GET', '/ledger'),
  verify: () => call<LedgerVerification>('GET', '/ledger/verify'),
  credential: (id: string) => call<Record<string, unknown>>('GET', `/export/credential/${id}`),
  evalReport: () => call<EvalReport>('GET', '/eval'),
  reset: () => call<{ ok: boolean }>('POST', '/demo/reset'),
}
