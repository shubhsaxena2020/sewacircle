// Mirrors backend/app/schemas.py. Keep in sync by hand (the head owns both).
export type Language = 'hi' | 'en' | 'hinglish'
export type Method = 'cp_sat' | 'nearest_skill' | 'random_feasible' | 'manual_greedy'
export type CardStatus = 'draft' | 'flagged' | 'confirmed' | 'corrected' | 'rejected'

export interface Volunteer {
  id: string; display_name: string; age: number; gender: string
  district: string; block: string; lat: number; lon: number
  skills: Record<string, number>; self_declared_skills: string[]; languages: string[]
  available_slots: string[]; has_vehicle: boolean; past_drives: number
  times_picked_last_90d: number; guardian_consent: boolean | null; opted_in_task_ids?: string[]; synthetic: boolean
}
export interface RoleSpec {
  id: string; role: string; count: number; required_skills: string[]; min_level: number
  priority: 'must' | 'should'; needs_experienced: boolean; evidence_span: string
  confidence: 'high' | 'medium' | 'low'; safety_critical?: boolean; unresolved?: boolean
}
export interface TaskSpec {
  id: string; title: string; brief_text: string; language: Language; slot: string
  district: string; block: string; lat: number; lon: number; team_size: number | null
  max_travel_km: number; allow_minors: boolean; roles: RoleSpec[]; synthetic: boolean
}
export interface ExtractedRole {
  role: string; count: number; required_skills: string[]; evidence_span: string
  confidence: 'high' | 'medium' | 'low'; reason: string; unresolved?: boolean
}
export interface ExtractionResult {
  roles: ExtractedRole[]; needs_decision: string[]; language_detected: Language
  model: string; cached: boolean; redactions: number; notes: string[]
}
export interface RosterOptions {
  fairness: boolean; resilience: boolean; mentor_pairing: boolean
  forced_in: string[]; forced_out: string[]; opted_in_only: boolean; time_limit_s: number; seed: number
}
export interface RecruitRequest {
  role_id: string; role: string; needed: number; skills: string[]; min_level: number
  checked_skill_required: boolean; slot: string; area: string; max_travel_km: number; reason: string
}
export interface Assignment {
  role_id: string; slot_index: number; volunteer_id: string; volunteer_name: string
  score: number; distance_km: number; reasons: string[]; flags: string[]
}
export interface StandbyPick { volunteer_id: string; volunteer_name: string; covers_role_ids: string[]; reason: string }
export interface RosterMetrics {
  role_coverage: number; slots_filled: number; slots_required: number; robustness: number
  repeat_pick_share: number; exposure_gini: number; district_spread: number
  novices: number; mentor_pairs: number; solve_ms: number; solver_status: string
}
export interface RosterResult {
  task_id: string; method: Method; assignments: Assignment[]; standby: StandbyPick[]
  unfilled_role_ids: string[]; metrics: RosterMetrics; explanations: string[]
  recruit_requests?: RecruitRequest[]; ready?: boolean | null; synthetic: boolean
}
export interface RosterBoth { cp_sat: RosterResult; nearest_skill: RosterResult }
export interface Counterfactual {
  volunteer_id: string; volunteer_name: string; feasible: boolean; narrative: string
  delta_role_coverage: number; delta_robustness: number
  displaced_volunteer_ids: string[]; blocking_reasons: string[]
}
export interface DropoutResult {
  task_id: string; dropped_volunteer_id: string; healed_with_standby: boolean
  replacement_volunteer_id: string | null; uncovered_role_ids: string[]; roster_after: RosterResult
}
export interface Flag { code: string; severity: 'info' | 'warn' | 'block'; message: string }
export interface ContributionCard {
  id: string; task_id: string; volunteer_id: string; role: string; claimed_hours: number
  recorded_hours: number | null; summary: string; evidence_refs: string[]; status: CardStatus
  flags: Flag[]; drafted_by: 'ai' | 'human'; confirmed_by: string | null; created_at: string; synthetic: boolean
}
export interface LedgerEntry {
  index: number; ts: string; action: string; card_id: string; actor: string
  payload_hash: string; prev_hash: string; entry_hash: string
}
export interface LedgerVerification { ok: boolean; entries: number; first_bad_index: number | null; note: string }
export interface EvalRow {
  task_id: string; method: Method; role_coverage: number; robustness: number
  repeat_pick_share: number; exposure_gini: number; solve_ms: number; ready?: number
}
export interface EvalReport {
  n_tasks: number; n_volunteers: number; rows: EvalRow[]
  summary: Record<string, Record<string, number>>
  ci95: Record<string, Record<string, [number, number]>>
  misses: string[]; generated_by: string; synthetic: boolean
}
export interface AttendanceRow { volunteer_id: string; task_id: string; hours: number; check_in?: string; check_out?: string }
