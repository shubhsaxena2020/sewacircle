import { describe, expect, it } from 'vitest'
import { copy, formatNumber } from './i18n'
import { recruitRequestText, rosterReady } from './logic'
import type { RecruitRequest, RosterResult } from './types'

const roster = (ready: boolean | null): RosterResult => ({ task_id: 'task-01', method: 'cp_sat', assignments: [], standby: [], unfilled_role_ids: [], metrics: { role_coverage: 1, slots_filled: 1, slots_required: 1, robustness: 1, repeat_pick_share: 0, exposure_gini: 0, district_spread: 1, novices: 0, mentor_pairs: 0, solve_ms: 1, solver_status: 'OPTIMAL' }, explanations: [], ready, synthetic: true })
describe('verdict and recruit request copy', () => {
  it('only treats the API true verdict as ready', () => { expect(rosterReady(roster(true))).toBe(true); expect(rosterReady(roster(false))).toBe(false); expect(rosterReady(roster(null))).toBe(false) })
  it('renders a specific request with its actual area and limit', () => {
    const r: RecruitRequest = { role_id: 'r1', role: 'First-aid volunteer', needed: 1, skills: ['first_aid'], min_level: 2, checked_skill_required: true, slot: 'sat_morning', area: 'Sadar block', max_travel_km: 10, reason: 'No checked volunteer is available.' }
    expect(recruitRequestText(r)).toBe('1 First-aid volunteer; first_aid; sat_morning; Sadar block; within 10 km. No checked volunteer is available.')
  })
})
describe('language and number formatting', () => {
  it('has complete English and Hindi entries', () => { for (const [key, value] of Object.entries(copy)) { expect(value, key).toHaveLength(2); expect(value[0].trim(), `${key} English`).not.toBe(''); expect(value[1].trim(), `${key} Hindi`).not.toBe('') } })
  it('uses locale-aware grouping and Hindi digits', () => { expect(formatNumber(1234567, 'en')).toBe('12,34,567'); expect(formatNumber(1234567, 'hi')).toBe('१२,३४,५६७') })
})
