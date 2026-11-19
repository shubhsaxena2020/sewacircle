import type { RecruitRequest, RosterResult } from './types'
export const rosterReady = (roster: RosterResult) => roster.ready === true
export function recruitRequestText(request: RecruitRequest) {
  return `${request.needed} ${request.role}; ${request.skills.join(', ')}; ${request.slot}; ${request.area}; within ${request.max_travel_km} km. ${request.reason}`
}
