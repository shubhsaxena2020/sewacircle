import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, ChevronRight, RotateCcw, ShieldCheck, Sparkles, UserRoundX } from 'lucide-react'
import { motion, AnimatePresence, useReducedMotion } from 'motion/react'
import { api, defaultOptions } from './api'
import { useUi } from './ui-context'
import { formatNumber, formatPercent, formatSlot, type Key } from './i18n'
import type { AttendanceRow, ContributionCard, Counterfactual, DropoutResult, EvalReport, ExtractionResult, LedgerEntry, LedgerVerification, RoleSpec, RosterBoth, RosterOptions, RosterResult, TaskSpec, Volunteer } from './types'
import { RecruitRequests, VerdictPanel } from './Verdict'

type Step = 'task' | 'roles' | 'crew' | 'evidence' | 'ledger' | 'evaluation'
const steps: Step[] = ['task', 'roles', 'crew', 'evidence', 'ledger', 'evaluation']
const methodKeys: { key: keyof RosterBoth; label: Key }[] = [{key:'cp_sat',label:'methodCp'},{key:'nearest_skill',label:'methodNear'},{key:'manual_greedy',label:'methodManual'},{key:'random_feasible',label:'methodRandom'}]
const englishSample = 'Saturday morning water and hygiene camp for the village. We need a team lead, a local-language liaison, first-aid support, a logistics volunteer for supplies, a hygiene educator and a documentation volunteer.'
const hinglishSample = 'Saturday subah gaon mein water aur hygiene camp hai. Team lead, local language se baat karne wala, first-aid support, supplies ke liye logistics, hygiene educator aur documentation volunteer chahiye.'
const safetySkills = new Set(['first_aid','disaster_response','driving_transport'])
const blankRole = (): RoleSpec => ({id:'manual-'+crypto.randomUUID().slice(0,8),role:'',count:1,required_skills:[],min_level:1,priority:'must',needs_experienced:false,evidence_span:'',confidence:'high',unresolved:false})
function errorText(err: unknown) { return err instanceof Error ? err.message : String(err) }

export default function Console() {
  const { t, lang } = useUi()
  const reducedMotion = useReducedMotion()
  const initial = new URLSearchParams(location.search).get('step') as Step | null
  const [step, setStep] = useState<Step>(initial && steps.includes(initial) ? initial : 'task')
  const [tasks, setTasks] = useState<TaskSpec[]>([])
  const [volunteers, setVolunteers] = useState<Volunteer[]>([])
  const [taskId, setTaskId] = useState('')
  const [brief, setBrief] = useState('')
  const [extraction, setExtraction] = useState<ExtractionResult | null>(null)
  const [roles, setRoles] = useState<RoleSpec[]>([])
  const [options, setOptions] = useState<RosterOptions>(defaultOptions)
  const [all, setAll] = useState<RosterBoth | null>(null)
  const [roster, setRoster] = useState<RosterResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notes, setNotes] = useState('')
  const [hours, setHours] = useState<Record<string, number>>({})
  const [cards, setCards] = useState<ContributionCard[]>([])
  const [ledger, setLedger] = useState<LedgerEntry[]>([])
  const [verification, setVerification] = useState<LedgerVerification | null>(null)
  const [report, setReport] = useState<EvalReport | null>(null)
  const [dropout, setDropout] = useState<DropoutResult | null>(null)
  const [whyId, setWhyId] = useState('')
  const [counter, setCounter] = useState<Counterfactual | null>(null)
  const [copied, setCopied] = useState(false)
  const [fix, setFix] = useState<Record<string, number>>({})

  useEffect(() => {
    api.tasks().then(data => { setTasks(data); if (data[0]) { setTaskId(data[0].id); setBrief(data[0].brief_text) } }).catch(e => setError(errorText(e)))
    api.volunteers().then(setVolunteers).catch(e => setError(errorText(e)))
    api.cards().then(setCards).catch(() => undefined)
  }, [])
  useEffect(() => { if (step === 'ledger') refreshLedger(); if (step === 'evaluation' && !report) loadEval() }, [step, report])
  const site = tasks.find(x => x.id === taskId)
  const task = useMemo(() => site ? {...site,brief_text:brief,roles} : null, [site,brief,roles])
  const candidates = volunteers.filter(v => !roster?.assignments.some(a => a.volunteer_id === v.id))
  function chooseTask(id: string) { const next = tasks.find(x => x.id === id); setTaskId(id); setBrief(next?.brief_text ?? ''); setExtraction(null); setRoles([]); setAll(null); setRoster(null); setCards([]); setNotes(''); setHours({}); setDropout(null) }
  async function extract() {
    if (!brief.trim()) return
    setBusy(true); setError('')
    try {
      const result = await api.extract(brief)
      setExtraction(result)
      setRoles(result.roles.map((r,i) => ({id:`role-${String(i+1).padStart(2,'0')}`,role:r.role,count:r.count,required_skills:r.required_skills,min_level:1,priority:'must',needs_experienced:false,evidence_span:r.evidence_span,confidence:r.confidence,unresolved:!!r.unresolved,safety_critical:r.required_skills.some(s=>safetySkills.has(s))})))
      setStep('roles')
    } catch (e) { setError(errorText(e)); setRoles(site?.roles ?? []); setStep('roles') } finally { setBusy(false) }
  }
  async function build() {
    if (!task) return
    setBusy(true); setError(''); setDropout(null); setCounter(null)
    try { const data = await api.roster(task, options); setAll(data); setRoster(data.cp_sat); setStep('crew') }
    catch (e) { setError(errorText(e)) } finally { setBusy(false) }
  }
  async function doDrop(id: string) {
    if (!task || !roster) return
    setBusy(true); setError('')
    try { const result=await api.dropout(task,roster,id,options); setDropout(result); setRoster(result.roster_after) }
    catch(e){setError(errorText(e))}finally{setBusy(false)}
  }
  async function askWhy() {
    if (!task || !roster || !whyId) return
    setBusy(true); setError('')
    try {setCounter(await api.whyNot(task,roster,whyId,options))} catch(e){setError(errorText(e))} finally{setBusy(false)}
  }
  async function draft() {
    if (!task || !roster) return
    const rows: AttendanceRow[] = roster.assignments.filter(a=>hours[a.volunteer_id]!==undefined).map(a=>({volunteer_id:a.volunteer_id,task_id:task.id,hours:hours[a.volunteer_id]}))
    setBusy(true);setError('')
    try { const result=await api.draft(task,notes,rows,roster.assignments);setCards(result) }catch(e){setError(errorText(e))}finally{setBusy(false)}
  }
  async function decide(card: ContributionCard, action:'confirm'|'correct'|'reject') {
    setBusy(true);setError('')
    try { const updated=await api.decide(card.id,action,action==='correct' ? (fix[card.id] ?? card.recorded_hours ?? card.claimed_hours) : undefined);setCards(cs=>cs.map(c=>c.id===card.id?updated:c));await refreshLedger() }
    catch(e){setError(errorText(e))}finally{setBusy(false)}
  }
  async function refreshLedger() { try { setLedger(await api.ledger()) } catch(e){setError(errorText(e))} }
  async function verify() { try { setVerification(await api.verify());await refreshLedger() } catch(e){setError(errorText(e))} }
  async function exportCard(card: ContributionCard) {
    try { const credential=await api.credential(card.id); const blob=new Blob([JSON.stringify(credential,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download=`${card.id}-unsigned.json`;anchor.click();URL.revokeObjectURL(url);await refreshLedger() } catch(e){setError(errorText(e))}
  }
  async function loadEval() { setBusy(true);setError('');try{setReport(await api.evalReport())}catch(e){setError(errorText(e))}finally{setBusy(false)} }
  function goEvidence() {
    setStep('evidence')
  }
  function updateRole(index:number, patch:Partial<RoleSpec>) {setRoles(rs=>rs.map((r,i)=>i===index?{...r,...patch}:r))}
  const canGo = (s:Step) => s==='task' || s==='evaluation' || s==='roles' && roles.length>0 || ['crew','evidence','ledger'].includes(s) && !!roster
  return <div className="console-page page-shell">
    <div className="page-intro"><span className="kicker">{t('heroEyebrow')}</span><h1>{t('consoleTitle')}</h1><p>{t('consoleSub')}</p></div>
    <div className="console-layout"><aside className="console-sidebar"><nav aria-label={t('console')}>{steps.map((s,i)=><button key={s} disabled={!canGo(s)} className={'console-nav-item '+(step===s?'selected':'')} onClick={()=>setStep(s)}><span className="nav-index">{String(i+1).padStart(2,'0')}</span>{t(s)}<ChevronRight size={15}/></button>)}</nav><div className="sidebar-note"><ShieldCheck size={22}/><p>{t('checkedRule')}</p></div></aside>
      <div className="console-content">
        <AnimatePresence mode="wait"><motion.div key={step} initial={reducedMotion?false:{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={reducedMotion?undefined:{opacity:0,y:-6}} transition={{duration:reducedMotion?0:.2}}>
          {step==='task' && <section className="work-panel"><div className="panel-title"><span className="kicker">{t('task')}</span><h2>{t('chooseDrive')}</h2></div><label className="field"><span>{t('chooseDrive')}</span><select value={taskId} onChange={e=>chooseTask(e.target.value)}>{tasks.map(x=><option key={x.id} value={x.id}>{x.title} · {x.block}, {x.district}</option>)}</select></label><div className="task-meta">{site && <><span>{site.district} / {site.block}</span><span>{formatSlot(site.slot,lang)}</span><span>{formatNumber(site.max_travel_km,lang)} {t('km')}</span></>}</div><label className="field"><span>{t('brief')}</span><textarea rows={7} value={brief} onChange={e=>setBrief(e.target.value)}/><small>{t('briefHelp')}</small></label><div className="sample-row"><button onClick={()=>setBrief(site?.brief_text??'')}>{t('sampleHi')}</button><button onClick={()=>setBrief(englishSample)}>{t('sampleEn')}</button><button onClick={()=>setBrief(hinglishSample)}>{t('sampleHinglish')}</button></div><div className="panel-actions"><button className="button primary" onClick={extract} disabled={busy||!brief.trim()}>{busy?t('extracting'):t('extract')}<ArrowRight size={17}/></button><button className="text-button" onClick={()=>{setRoles(site?.roles??[blankRole()]);setStep('roles')}}>{t('manualRoles')}</button></div></section>}
          {step==='roles' && <section className="work-panel"><div className="panel-title"><span className="kicker">{t('roles')}</span><h2>{t('rolesTitle')}</h2><p>{t('rolesSub')}</p></div>{extraction && <div className="info-strip"><span className="tag draft-tag">{t('draft')}</span><span>{extraction.model} {extraction.cached&&`· ${t('cached')}`}</span>{extraction.redactions>0&&<span>{formatNumber(extraction.redactions,lang)} {t('redactions')}</span>}</div>}{extraction?.needs_decision.length ? <div className="decision-box"><strong>{t('needsDecision')}</strong><ul>{extraction.needs_decision.map((x,i)=><li key={i}>{x}</li>)}</ul></div>:null}<div className="role-list">{roles.map((r,i)=><article key={r.id} className={'role-editor '+(r.unresolved?'unresolved':'')}><div className="role-editor-head"><span className="role-number">{String(i+1).padStart(2,'0')}</span><span className={'tag '+(r.unresolved?'warn-tag':'draft-tag')}>{r.unresolved?t('unresolved'):t('draft')}</span><button aria-label={t('removeRole')} title={t('removeRole')} className="small-icon" onClick={()=>setRoles(roles.filter((_,j)=>j!==i))}>×</button></div><div className="role-fields"><label className="field"><span>{t('roles')}</span><input value={r.role} onChange={e=>updateRole(i,{role:e.target.value})}/></label><label className="field small-field"><span>{t('count')}</span><input type="number" min="1" max="20" value={r.count} onChange={e=>updateRole(i,{count:Math.max(1,Number(e.target.value)||1)})}/></label><label className="field"><span>{t('requiredSkills')}</span><input value={r.required_skills.join(', ')} onChange={e=>updateRole(i,{required_skills:e.target.value.split(',').map(x=>x.trim()).filter(Boolean)})}/></label><label className="field small-field"><span>{t('priority')}</span><select value={r.priority} onChange={e=>updateRole(i,{priority:e.target.value as 'must'|'should'})}><option value="must">{t('must')}</option><option value="should">{t('should')}</option></select></label></div><div className="role-source"><span>{t('sourcePhrase')}</span><q>{r.evidence_span||'—'}</q><span className="confidence">{t('confidence')}: {t(r.confidence==='high'?'confidenceHigh':r.confidence==='medium'?'confidenceMedium':'confidenceLow')}</span></div><label className="check-row"><input type="checkbox" checked={!!r.unresolved} onChange={e=>updateRole(i,{unresolved:e.target.checked})}/>{t('unresolved')}</label></article>)}</div><div className="panel-actions"><button className="button outline" onClick={()=>setRoles([...roles,blankRole()])}>{t('addRole')}</button><button className="button primary" onClick={build} disabled={busy||roles.length===0||roles.some(r=>!r.role.trim())}>{busy?t('building'):t('buildCrew')}<ArrowRight size={17}/></button></div></section>}
          {step==='crew' && roster && <CrewView task={task!} roster={roster} all={all} options={options} setOptions={setOptions} build={build} busy={busy} dropout={dropout} doDrop={doDrop} candidates={candidates} whyId={whyId} setWhyId={setWhyId} askWhy={askWhy} counter={counter} copied={copied} setCopied={setCopied} next={goEvidence}/>}
          {step==='evidence' && roster && <section className="work-panel"><div className="panel-title"><span className="kicker">{t('evidence')}</span><h2>{t('hostNotes')}</h2><p>{t('principleThree')}</p></div><label className="field"><span>{t('hostNotes')}</span><textarea rows={6} value={notes} onChange={e=>setNotes(e.target.value)}/><small>{t('notesHelp')}</small></label><div className="attendance-head"><h3>{t('attendance')}</h3><span>{t('synthetic')}</span></div><div className="attendance-list">{roster.assignments.map(a=><label key={a.volunteer_id} className="attendance-row"><span>{a.volunteer_name}</span><span>{t('hours')}</span><input aria-label={`${a.volunteer_name} ${t('hours')}`} type="number" min="0" max="24" step=".5" value={hours[a.volunteer_id]??''} onChange={e=>setHours(current=>{const next={...current};if(e.target.value==='') delete next[a.volunteer_id];else next[a.volunteer_id]=Number(e.target.value);return next})}/></label>)}</div><button className="button primary" disabled={busy||!notes.trim()} onClick={draft}>{busy?t('drafting'):t('draftCards')}<Sparkles size={17}/></button><div className="cards-grid">{cards.filter(c=>c.task_id===task?.id).map(card=><article key={card.id} className="contribution-card"><div className="card-top"><span className="tag">{t('card')}</span><span className={'tag '+(card.status==='flagged'?'warn-tag':card.status==='confirmed'||card.status==='corrected'?'ready-tag':'draft-tag')}>{t(card.status==='flagged'?'statusFlagged':card.status==='confirmed'?'statusConfirmed':card.status==='corrected'?'statusCorrected':card.status==='rejected'?'statusRejected':'statusDraft')}</span></div><h3>{volunteers.find(v=>v.id===card.volunteer_id)?.display_name??card.volunteer_id}</h3><p>{card.role}</p><p>{card.summary}</p><div className="card-hours"><span>{t('claimed')} <b>{formatNumber(card.claimed_hours,lang,1)}</b></span><span>{t('recorded')} <b>{card.recorded_hours==null?'—':formatNumber(card.recorded_hours,lang,1)}</b></span></div>{card.flags.length>0&&<div className="flag-list"><strong>{t('flags')}</strong>{card.flags.map((f,i)=><p key={i}>{f.message}</p>)}</div>}{['draft','flagged'].includes(card.status)&&<div className="card-actions"><button onClick={()=>decide(card,'confirm')} disabled={busy}>{t('confirm')}</button><label><span>{t('correct')}</span><input aria-label={`${t('correct')} ${card.id}`} type="number" min="0" max="24" step=".5" value={fix[card.id]??card.recorded_hours??card.claimed_hours} onChange={e=>setFix({...fix,[card.id]:Number(e.target.value)})}/></label><button onClick={()=>decide(card,'correct')} disabled={busy}>{t('correct')}</button><button onClick={()=>decide(card,'reject')} disabled={busy}>{t('reject')}</button></div>}{['confirmed','corrected'].includes(card.status)&&<button className="text-button" onClick={()=>exportCard(card)}>{t('export')}</button>}</article>)}</div>{cards.length>0&&<button className="button outline" onClick={()=>setStep('ledger')}>{t('ledger')}<ArrowRight size={17}/></button>}</section>}
          {step==='ledger' && <section className="work-panel"><div className="panel-title"><span className="kicker">{t('ledger')}</span><h2>{t('ledgerTitle')}</h2><p>{t('ledgerNote')}</p></div><div className="ledger-toolbar"><button className="button primary" onClick={verify}>{t('verify')}<ShieldCheck size={17}/></button>{verification&&<strong role="status" className={verification.ok?'success-text':'error-text'}>{verification.ok?t('verified'):t('failed')} · {formatNumber(verification.entries,lang)}</strong>}</div>{ledger.length===0?<p className="empty-state">{t('emptyLedger')}</p>:<div className="ledger-chain">{ledger.map((entry,i)=><article className="ledger-block" key={i}><span className="ledger-index">{formatNumber(entry.index,lang)}</span><div><strong>{entry.action}</strong><span>{entry.card_id}</span><code>{entry.entry_hash.slice(0,18)}…</code></div><ChevronRight size={19}/></article>)}</div>}<p className="muted">{t('unsigned')}</p></section>}
          {step==='evaluation' && <section className="work-panel"><div className="panel-title"><span className="kicker">{t('evaluation')}</span><h2>{t('evalTitle')}</h2><p>{t('evalSub')}</p></div>{!report?<button className="button primary" onClick={loadEval} disabled={busy}>{busy?t('loading'):t('retry')}</button>:<EvalView report={report}/>}</section>}
        </motion.div></AnimatePresence>
        {error&&<div className="error-box" role="alert"><strong>{t('error')}</strong><p>{error}</p><button className="small-icon" onClick={()=>setError('')}>{t('close')}</button></div>}
      </div></div>
  </div>
}

function CrewView(p:{task:TaskSpec;roster:RosterResult;all:RosterBoth|null;options:RosterOptions;setOptions:(o:RosterOptions)=>void;build:()=>void;busy:boolean;dropout:DropoutResult|null;doDrop:(id:string)=>void;candidates:Volunteer[];whyId:string;setWhyId:(id:string)=>void;askWhy:()=>void;counter:Counterfactual|null;copied:boolean;setCopied:(b:boolean)=>void;next:()=>void}) {
  const {t,lang}=useUi();const ready=p.roster.ready===true
  const reducedMotion=useReducedMotion()
  const requests=p.roster.recruit_requests??[]
  const roleNames=Object.fromEntries(p.task.roles.map(r=>[r.id,r.role]))
  async function copyRequest(r:typeof requests[number]){const text=`${r.needed} ${r.role}; ${r.skills.join(', ')}; ${r.slot}; ${r.area}; ${r.max_travel_km} km. ${r.reason}`;await navigator.clipboard.writeText(text);p.setCopied(true);setTimeout(()=>p.setCopied(false),1800)}
  return <div className="crew-view">
    <VerdictPanel roster={p.roster} title={p.task.title} block={p.task.block}/>
    {!ready&&<RecruitRequests requests={requests} onCopy={copyRequest} copied={p.copied}/>}
    <AnimatePresence>{p.dropout&&<motion.div className={'dropout-result '+(p.dropout.healed_with_standby?'good':'bad')} role="status" initial={reducedMotion?false:{opacity:0,y:12}} animate={{opacity:1,y:0}} exit={reducedMotion?undefined:{opacity:0,y:-8}} transition={{duration:reducedMotion?0:.25}}><UserRoundX size={23}/><div><strong>{p.dropout.healed_with_standby?t('healed'):t('notHealed')}</strong><p>{p.dropout.replacement_volunteer_id??p.dropout.uncovered_role_ids.map(id=>roleNames[id]??id).join(', ')}</p></div></motion.div>}</AnimatePresence>
    <section className="work-panel"><div className="panel-title compact"><span className="kicker">{t('crew')}</span><h2>{t('crewBoard')}</h2></div><div className="crew-board">{p.task.roles.map(r=>{const assigned=p.roster.assignments.filter(a=>a.role_id===r.id);const standbys=p.roster.standby.filter(s=>s.covers_role_ids.includes(r.id));return <article className="crew-role" key={r.id}><div className="crew-role-head"><span>{r.role}</span><span className={'tag '+(r.priority==='must'?'must-tag':'')}>{t(r.priority)}</span></div>{assigned.length?assigned.map(a=><div className="crew-person" key={a.volunteer_id}><span className="avatar">{a.volunteer_name.slice(0,1)}</span><div><strong>{a.volunteer_name}</strong><small>{a.reasons.join(' · ')}</small></div><button disabled={p.busy} title={t('drop')} aria-label={`${t('drop')} ${a.volunteer_name}`} onClick={()=>p.doDrop(a.volunteer_id)}><UserRoundX size={18}/></button></div>):<p className="empty-role">{t('noAssignment')}</p>}{standbys.map(s=><div className="standby-person" key={s.volunteer_id}><span>↳ {t('standby')}</span><strong>{s.volunteer_name}</strong><small>{s.reason}</small></div>)}</article>})}</div></section>
    <section className="work-panel"><div className="panel-title compact"><span className="kicker">{t('compare')}</span><h2>{t('compare')}</h2></div><div className="comparison-grid">{methodKeys.map(({key,label})=>{const m=p.all?.[key]?.metrics;return <article key={key} className={key==='cp_sat'?'featured':''}><span className="small-label">{t(label)}</span><strong>{p.all?.[key]?.ready?t('verdictReady'):t('verdictNo')}</strong><div><span>{t('coverage')}</span><b>{m?formatPercent(m.role_coverage,lang):'—'}</b></div><div><span>{t('robustness')}</span><b>{m?formatPercent(m.robustness,lang):'—'}</b></div><div><span>{t('repeat')}</span><b>{m?formatPercent(m.repeat_pick_share,lang):'—'}</b></div><div><span>{t('gini')}</span><b>{m?formatNumber(m.exposure_gini,lang,2):'—'}</b></div></article>})}</div></section>
    <section className="work-panel"><div className="panel-title compact"><h2>{t('plannerOptions')}</h2></div><div className="option-grid">{([['opted_in_only','optIn'],['fairness','fairRotation'],['resilience','standbyOpt'],['mentor_pairing','mentorOpt']] as const).map(([key,label])=><label className="toggle-row" key={key}><span>{t(label)}</span><input type="checkbox" checked={p.options[key]} onChange={e=>p.setOptions({...p.options,[key]:e.target.checked})}/></label>)}</div><button className="button outline" onClick={p.build} disabled={p.busy}><RotateCcw size={17}/>{p.busy?t('building'):t('rerun')}</button><div className="safety-info"><ShieldCheck size={20}/><span>{t('checkedRule')}</span><span>{t('novice')}: {formatNumber(p.roster.metrics.novices,lang)} · {t('mentor')}: {formatNumber(p.roster.metrics.mentor_pairs,lang)}</span></div></section>
    <section className="work-panel why-panel"><div className="panel-title compact"><h2>{t('whyNot')}</h2></div><div className="why-controls"><select aria-label={t('selectVolunteer')} value={p.whyId} onChange={e=>p.setWhyId(e.target.value)}><option value="">{t('selectVolunteer')}</option>{p.candidates.map(v=><option key={v.id} value={v.id}>{v.display_name} · {v.block}</option>)}</select><button className="button outline" disabled={!p.whyId||p.busy} onClick={p.askWhy}>{t('askWhy')}</button></div>{p.counter&&<div className="counter-result" role="status"><strong>{p.counter.volunteer_name}</strong><p>{p.counter.narrative}</p>{p.counter.blocking_reasons.map((x,i)=><p key={i}>{x}</p>)}</div>}</section>
    <div className="panel-actions"><button className="button primary" onClick={p.next}>{t('evidence')}<ArrowRight size={17}/></button></div>
  </div>
}
function EvalView({report}:{report:EvalReport}){
  const {t,lang}=useUi()
  const metrics:[keyof EvalReport['summary'][string],Key][]=[['ready','readyMetric'],['role_coverage','coverage'],['robustness','robustness'],['repeat_pick_share','repeat'],['exposure_gini','gini']]
  return <div className="eval-view"><div className="eval-head"><span>{t('synthetic')}</span><strong>{formatNumber(report.n_tasks,lang)} {t('drives')} · {formatNumber(report.n_volunteers,lang)} {t('volunteers')}</strong></div>{metrics.map(([metric,label])=><section className="eval-metric" key={metric}><h3>{t(label)}</h3>{methodKeys.map(({key,label:ml})=>{const value=report.summary[key]?.[metric]??0;const ci=report.ci95[key]?.[metric];return <div className="eval-bar-row" key={key}><span>{t(ml)}</span><div className="eval-track"><i style={{width:`${Math.max(1,value*100)}%`}}/></div><strong>{metric==='exposure_gini'?formatNumber(value,lang,2):formatPercent(value,lang)}</strong>{ci&&<small>[{formatNumber(ci[0],lang,2)}, {formatNumber(ci[1],lang,2)}]</small>}</div>})}</section>)}<div className="misses"><h3>{t('misses')}</h3>{report.misses.length?<ul>{report.misses.map((x,i)=><li key={i}>{x}</li>)}</ul>:<p>{t('noMisses')}</p>}</div></div>
}
