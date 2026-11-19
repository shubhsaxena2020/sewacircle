import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context } from './ui-context'
import { tr } from './i18n'
import { RecruitRequests, VerdictPanel } from './Verdict'
import type { RecruitRequest, RosterResult } from './types'

const roster = {ready:true,metrics:{slots_filled:6,slots_required:6}} as RosterResult
const request:RecruitRequest={role_id:'first',role:'First-aid support',needed:1,skills:['first_aid'],min_level:1,checked_skill_required:true,slot:'sat_morning',area:'Akbarpur',max_travel_km:25,reason:'No checked first-aider is available.'}
const en = {lang:'en' as const,t:(key:Parameters<typeof tr>[1])=>tr('en',key),toggleLang:()=>{}}
const hi = {lang:'hi' as const,t:(key:Parameters<typeof tr>[1])=>tr('hi',key),toggleLang:()=>{}}
afterEach(cleanup)
describe('crew decision',()=>{
  it('announces the ready verdict and filled slots',()=>{
    render(<Context.Provider value={en}><VerdictPanel roster={roster} title="Water camp" block="Akbarpur"/></Context.Provider>)
    expect(screen.getByRole('status').textContent).toContain('READY')
    expect(screen.getByRole('status').textContent).toContain('6 / 6')
  })
  it('announces a not ready verdict in Hindi',()=>{
    render(<Context.Provider value={hi}><VerdictPanel roster={{...roster,ready:false}} title="Water camp" block="Akbarpur"/></Context.Provider>)
    expect(screen.getByRole('status').textContent).toContain('तैयार नहीं')
  })
  it('renders the exact recruit request and copy action',()=>{
    const copy=vi.fn()
    render(<Context.Provider value={en}><RecruitRequests requests={[request]} onCopy={copy} copied={false}/></Context.Provider>)
    expect(screen.getByText('1 × First-aid support')).toBeTruthy()
    expect(screen.getByText(/No checked first-aider/)).toBeTruthy()
    fireEvent.click(screen.getByRole('button',{name:/Copy request/}))
    expect(copy).toHaveBeenCalledWith(request)
  })
})
