// FIXTURES ONLY (?mock=1). Not real results. The UI shows a permanent MOCK banner whenever these are in use.
import type {
  Assignment, ContributionCard, EvalReport, ExtractionResult, LedgerEntry, RosterBoth, RosterResult, TaskSpec, Volunteer,
} from './types'

const roles = [
  ['role-01', 'Team lead', ['team_leadership', 'event_coordination']],
  ['role-02', 'Local-language liaison', ['dialect_awadhi', 'community_mobilisation']],
  ['role-03', 'First-aid support', ['first_aid']],
  ['role-04', 'Logistics and supplies', ['logistics_supplies', 'driving_transport']],
  ['role-05', 'Hygiene educator', ['hygiene_promotion', 'health_education']],
  ['role-06', 'Documentation', ['documentation_reporting', 'photography_video']],
] as const

export const mockTask: TaskSpec = {
  id: 't1', title: 'Water and hygiene camp (mock)', brief_text: '', language: 'hi', slot: 'sat_morning',
  district: 'Kanpur Dehat', block: 'Bilhaur', lat: 26.85, lon: 80.07, team_size: 6, max_travel_km: 15,
  allow_minors: true, synthetic: true,
  roles: roles.map(([id, role, skills]) => ({
    id, role, count: 1, required_skills: [...skills], min_level: 1, priority: 'must' as const,
    needs_experienced: id === 'role-03', evidence_span: '', confidence: 'high' as const,
  })),
}

const names = ['Volunteer A', 'Volunteer B', 'Volunteer C', 'Volunteer D', 'Volunteer E', 'Volunteer F', 'Volunteer G', 'Volunteer H']
export const mockVolunteers: Volunteer[] = names.map((n, i) => ({
  id: `v${i + 1}`, display_name: n, age: [21, 19, 22, 20, 17, 23, 24, 19][i], gender: ['M', 'F', 'F', 'M', 'F', 'M', 'F', 'M'][i],
  district: 'Kanpur Dehat', block: 'Bilhaur', lat: 26.8, lon: 80.1, skills: {}, self_declared_skills: [],
  languages: ['hi'], available_slots: ['sat_morning'], has_vehicle: i === 3, past_drives: [6, 2, 4, 1, 0, 3, 7, 2][i],
  times_picked_last_90d: [4, 0, 1, 0, 0, 2, 5, 1][i], guardian_consent: i === 4 ? true : null, synthetic: true,
}))

const reasonsFor: Record<string, string[]> = {
  'role-01': ['Led 6 past drives', 'Free Saturday morning', '6 km away'],
  'role-02': ['Awadhi speaker (self-declared)', 'Lives in the block', 'Has not been picked in 90 days'],
  'role-03': ['First-aid certificate (self-declared, host to confirm)', 'Needs an experienced person: mentors the novice'],
  'role-04': ['Owns a vehicle', '9 km away', 'Morning only: matches the slot'],
  'role-05': ['Health-science student', 'Guardian consent on file', 'Novice paired with an experienced mentor'],
  'role-06': ['Design and photography skills', 'Photography needs site approval'],
}
const assigned: Assignment[] = [
  ['role-01', 'v1'], ['role-02', 'v2'], ['role-03', 'v3'], ['role-04', 'v4'], ['role-05', 'v5'], ['role-06', 'v6'],
].map(([role_id, vid], i) => ({
  role_id, slot_index: 0, volunteer_id: vid, volunteer_name: names[Number(vid.slice(1)) - 1], score: 0.8 - i * 0.03,
  distance_km: [6, 3, 9, 9, 4, 12][i], reasons: reasonsFor[role_id],
  flags: [i === 1 || i === 2 ? 'self_declared_skill' : '', i === 4 ? 'novice' : '', i === 4 ? 'minor_guardian_consent' : ''].filter(Boolean),
}))

const base = { task_id: 't1', synthetic: true, explanations: [] as string[], unfilled_role_ids: [] as string[] }
export const mockCp: RosterResult = {
  ...base, method: 'cp_sat', assignments: assigned,
  standby: [
    { volunteer_id: 'v7', volunteer_name: 'Volunteer G', covers_role_ids: ['role-01', 'role-04'], reason: 'Covers team lead or logistics if either drops out' },
    { volunteer_id: 'v8', volunteer_name: 'Volunteer H', covers_role_ids: ['role-02', 'role-06'], reason: 'Awadhi speaker and documentation backup' },
  ],
  metrics: { role_coverage: 1, slots_filled: 6, slots_required: 6, robustness: 1, repeat_pick_share: 0.17, exposure_gini: 0.31,
    district_spread: 1, novices: 1, mentor_pairs: 1, solve_ms: 420, solver_status: 'OPTIMAL' },
}
export const mockBase: RosterResult = {
  ...base, method: 'nearest_skill', unfilled_role_ids: ['role-03', 'role-06'],
  assignments: assigned.filter((a) => !['role-03', 'role-06'].includes(a.role_id)).map((a) => ({ ...a, reasons: ['Nearest volunteer with a matching skill'], flags: [] })),
  standby: [],
  metrics: { role_coverage: 0.67, slots_filled: 4, slots_required: 6, robustness: 0, repeat_pick_share: 0.5, exposure_gini: 0.52,
    district_spread: 1, novices: 0, mentor_pairs: 0, solve_ms: 3, solver_status: 'n/a' },
}

export const mockExtraction: ExtractionResult = {
  roles: roles.map(([, role, skills], i) => ({
    role, count: 1, required_skills: [...skills], evidence_span: ['120 लोग आएँगे', 'स्थानीय बोली', 'प्राथमिक उपचार', 'सामान', 'हाथ धोने की जागरूकता', 'पोस्टर'][i],
    confidence: i < 4 ? 'high' : 'medium', reason: 'Mock fixture',
  })),
  needs_decision: ['Is photography allowed at this site?'], language_detected: 'hi', model: 'mock', cached: true, redactions: 0, notes: [],
}

const mkCard = (id: string, vid: string, role: string, claimed: number, recorded: number | null, flags: ContributionCard['flags'], status: ContributionCard['status']): ContributionCard => ({
  id, task_id: 't1', volunteer_id: vid, role, claimed_hours: claimed, recorded_hours: recorded, summary: 'Mock draft card from host notes',
  evidence_refs: ['host_note', `attendance_row_${vid}`], status, flags, drafted_by: 'ai', confirmed_by: null, created_at: new Date().toISOString(), synthetic: true,
})
let cards: ContributionCard[] = []
let ledger: LedgerEntry[] = []
const hash = (s: string) => Array.from(s).reduce((h, c) => ((h << 5) - h + c.charCodeAt(0)) | 0, 7).toString(16).padStart(8, '0') + 'a41f9c2e'
function log(action: string, c: ContributionCard, actor: string) {
  const prev = ledger.length ? ledger[ledger.length - 1].entry_hash : '0'.repeat(16)
  const payload_hash = hash(JSON.stringify(c))
  ledger.push({ index: ledger.length, ts: new Date().toISOString(), action, card_id: c.id, actor, payload_hash, prev_hash: prev, entry_hash: hash(prev + payload_hash + action) })
}

export const mockEval: EvalReport = {
  n_tasks: 10, n_volunteers: 40, synthetic: true, generated_by: 'MOCK FIXTURE - not a real run', misses: ['mock: example miss on t7'],
  rows: [],
  summary: {
    cp_sat: { role_coverage: 0.97, robustness: 0.9, repeat_pick_share: 0.15, exposure_gini: 0.3 },
    nearest_skill: { role_coverage: 0.7, robustness: 0.05, repeat_pick_share: 0.45, exposure_gini: 0.5 },
    manual_greedy: { role_coverage: 0.85, robustness: 0.4, repeat_pick_share: 0.4, exposure_gini: 0.45 },
    random_feasible: { role_coverage: 0.6, robustness: 0.1, repeat_pick_share: 0.3, exposure_gini: 0.4 },
  },
  ci95: {},
}

const delay = <T,>(v: T, ms = 350) => new Promise<T>((r) => setTimeout(() => r(v), ms))

export async function mockHandler(method: string, path: string, body: unknown): Promise<unknown> {
  const b = (body ?? {}) as Record<string, any> // eslint-disable-line @typescript-eslint/no-explicit-any
  if (path === '/health') return { ok: true, disclaimer: 'SYNTHETIC DATA - illustrative, no real people', model: 'mock', llm_mode: 'mock' }
  if (path === '/meta') return { disclaimer: 'SYNTHETIC', skills: {} }
  if (path === '/tasks') return [mockTask]
  if (path === '/volunteers') return mockVolunteers
  if (path === '/extract-roles') return delay(mockExtraction, 900)
  if (path === '/roster') return delay<RosterBoth>({ cp_sat: mockCp, nearest_skill: mockBase }, 700)
  if (path === '/roster/why-not') {
    const v = mockVolunteers.find((x) => x.id === b.volunteer_id)
    return delay({ volunteer_id: b.volunteer_id, volunteer_name: v?.display_name ?? '', feasible: true, delta_role_coverage: 0, delta_robustness: -0.17,
      displaced_volunteer_ids: ['v6'], blocking_reasons: [], narrative: 'MOCK: Forcing this volunteer in displaces Volunteer F and lowers dropout robustness by 17 points.' })
  }
  if (path === '/roster/dropout') {
    const after: RosterResult = { ...mockCp, assignments: mockCp.assignments.map((a) => (a.volunteer_id === b.dropped_volunteer_id ? { ...a, volunteer_id: 'v7', volunteer_name: 'Volunteer G', reasons: ['Promoted from standby'], flags: [] } : a)) }
    return delay({ task_id: 't1', dropped_volunteer_id: b.dropped_volunteer_id, healed_with_standby: true, replacement_volunteer_id: 'v7', uncovered_role_ids: [], roster_after: after }, 500)
  }
  if (path === '/evidence/draft') {
    cards = [
      mkCard('c1', 'v3', 'First-aid support', 5, 5, [{ code: 'self_declared_skill_unconfirmed', severity: 'info', message: 'First-aid skill is self-declared; host should confirm.' }], 'draft'),
      mkCard('c2', 'v6', 'Documentation', 8, 5, [{ code: 'hours_exceed_recorded', severity: 'warn', message: 'Claimed 8 h but the attendance sheet shows 5 h.' }], 'flagged'),
      mkCard('c3', 'v2', 'Local-language liaison', 5, 5, [], 'draft'),
    ]
    ledger = []
    cards.forEach((c) => log(c.status === 'flagged' ? 'flag' : 'draft', c, 'system'))
    return delay(cards, 900)
  }
  if (path === '/evidence/cards') return cards
  const m = path.match(/^\/evidence\/(\w+)\/(confirm|correct|reject)$/)
  if (m) {
    const c = cards.find((x) => x.id === m[1])!
    if (m[2] === 'correct' && b.claimed_hours != null) c.claimed_hours = b.claimed_hours
    c.status = m[2] === 'confirm' ? 'confirmed' : m[2] === 'correct' ? 'corrected' : 'rejected'
    if (c.status !== 'rejected') c.confirmed_by = 'host'
    log(m[2], c, 'host')
    return delay({ ...c }, 200)
  }
  if (path === '/ledger') return ledger
  if (path === '/ledger/verify') return { ok: true, entries: ledger.length, first_bad_index: null, note: 'Hash chain shows edits, not truth; truth comes from host confirmation.' }
  if (path.startsWith('/export/credential/')) {
    const c = cards.find((x) => x.id === path.split('/').pop())!
    return { '@context': ['MOCK'], type: ['VerifiableCredential', 'OpenBadgeCredential'], name: 'MOCK unsigned credential', credentialSubject: { achievement: c.role, hours: c.claimed_hours }, note: 'Unsigned. Not issued by any authority.' }
  }
  if (path === '/eval') return delay(mockEval, 600)
  throw new Error(`mock: unhandled ${method} ${path}`)
}
