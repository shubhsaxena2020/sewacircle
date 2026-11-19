import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import { api, defaultOptions } from './api'
import { formatNumber } from './i18n'
import type { Lang } from './i18n'
import type { EvalReport, ExtractionResult, RosterResult, TaskSpec, Volunteer } from './types'
import TransitionFilm from './TransitionFilm'
import FilmLayers from './FilmLayers'

const VillageScene = lazy(() => import('./VillageScene'))
function supportsWebGL() {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}
const nav = [{ id: 'intro', name: 'Intro' }, { id: 'brief', name: 'Brief' }, { id: 'crew', name: 'Crew' }, { id: 'verdict', name: 'Verdict' }, { id: 'evidence', name: 'Evidence' }, { id: 'numbers', name: 'Numbers' }, { id: 'try', name: 'Try it' }]
const labels = { en: { overline: 'A crew is more than a list', title: 'Willing hands.<br/>A crew that can show up.', intro: 'Can this drive run?', brief: 'A brief becomes<br/>real roles.', crew: 'Make a circle<br/>that can hold.', verdict: 'Ready means<br/>every role has cover.', evidence: 'Work leaves<br/>a paper trail.', numbers: 'Measure what<br/>the plan can do.', try: 'One village.<br/>A hundred ways to help.', plan: 'Plan the crew', drop: 'Drop Heena P.', loading: 'A village is taking shape…', scroll: 'Scroll to continue', detail: 'AI proposed · you confirm', role: 'Role from the brief', synthetic: 'Synthetic data', share: 'Copy public summary link' }, hi: { overline: 'टीम केवल नामों की सूची नहीं', title: 'इच्छुक हाथ।<br/>एक तैयार टीम।', intro: 'क्या यह अभियान चल सकता है?', brief: 'विवरण से<br/>भूमिकाएँ बनती हैं।', crew: 'ऐसा घेरा<br/>जो साथ निभाए।', verdict: 'तैयार का अर्थ है<br/>हर भूमिका का सहारा।', evidence: 'काम का<br/>लिखित रिकॉर्ड।', numbers: 'योजना की<br/>क्षमता मापें।', try: 'एक गाँव।<br/>मदद के कई रास्ते।', plan: 'टीम बनाएँ', drop: 'हीना पी. को हटाएँ', loading: 'गाँव तैयार हो रहा है…', scroll: 'आगे पढ़ने के लिए स्क्रॉल करें', detail: 'AI का सुझाव · आपकी पुष्टि', role: 'विवरण से भूमिका', synthetic: 'सिंथेटिक डेटा', share: 'सार्वजनिक लिंक कॉपी करें' } }

export default function Story({ lang }: { lang: Lang }) {
  const text = labels[lang]; const root = useRef<HTMLDivElement>(null); const progressRef = useRef(0); const [webglAvailable] = useState(supportsWebGL); const [sceneReady, setSceneReady] = useState(() => !webglAvailable); const [task, setTask] = useState<TaskSpec | null>(null); const [volunteers, setVolunteers] = useState<Volunteer[]>([]); const [extraction, setExtraction] = useState<ExtractionResult | null>(null); const [evalReport, setEvalReport] = useState<EvalReport | null>(null); const [roster, setRoster] = useState<RosterResult | null>(null); const [dropResult, setDropResult] = useState<string>(''); const [selectedRole, setSelectedRole] = useState(''); const [error, setError] = useState(''); const [active, setActive] = useState('intro'); const [share, setShare] = useState('');
  useEffect(() => {
    if (!webglAvailable || matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const crew = root.current?.querySelector('#crew')
    if (!crew) return
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        setSceneReady(true)
        observer.disconnect()
      }
    }, { rootMargin: '120% 0px' })
    observer.observe(crew)
    return () => observer.disconnect()
  }, [webglAvailable])
  useEffect(() => { api.tasksLang(lang).then(rows => setTask(rows.find(x => x.id === 'task-01') ?? rows[0] ?? null)).catch(e => setError(e.message)); api.volunteers().then(setVolunteers).catch(() => undefined); api.evalReport().then(setEvalReport).catch(() => undefined) }, [lang])
  useEffect(() => { if (task?.brief_text) api.extract(task.brief_text).then(setExtraction).catch(() => undefined) }, [task?.id, task?.brief_text])
  useEffect(() => {
    if (!root.current || matchMedia('(prefers-reduced-motion: reduce)').matches) return
    gsap.registerPlugin(ScrollTrigger)
    const lenis = new Lenis({ lerp: .1, smoothWheel: true })
    const update = (time: number) => lenis.raf(time * 1000)
    gsap.ticker.add(update); gsap.ticker.lagSmoothing(0)
    lenis.on('scroll', ScrollTrigger.update)
    const ctx = gsap.context(() => {
      gsap.to(progressRef, { current: 1, ease: 'none', scrollTrigger: { trigger: root.current, start: 'top top', end: 'bottom bottom', scrub: 1 } })
      root.current?.querySelectorAll<HTMLElement>('.chapter').forEach(section => {
        ScrollTrigger.create({ trigger: section, start: 'top center', end: 'bottom center', onEnter: () => setActive(section.dataset.id ?? 'intro'), onEnterBack: () => setActive(section.dataset.id ?? 'intro') })
        gsap.fromTo(section.querySelector('.chapter-copy'), { y: 40 }, { y: 0, scrollTrigger: { trigger: section, start: 'top 78%', end: 'center center', scrub: true } })
      })
    }, root)
    return () => { ctx.revert(); gsap.ticker.remove(update); lenis.destroy() }
  }, [])
  async function plan() { if (!task) return; setError(''); setDropResult(''); try { const r = await api.roster(task, defaultOptions, lang); setRoster(r.cp_sat) } catch (e) { setError((e as Error).message) } }
  async function dropout() { if (!task || !roster) return; setError(''); try { const chosen = roster.assignments[3] ?? roster.assignments[0]; if (!chosen) throw new Error('No seated volunteer is available to drop.'); const r = await api.dropout(task, roster, chosen.volunteer_id, defaultOptions); setRoster(r.roster_after); setDropResult(`Dropout recorded. ${r.healed_with_standby ? 'Standby promoted.' : 'No standby could cover the gap.'} Current verdict: ${r.roster_after.ready === true ? 'READY' : 'NOT READY'}. ${r.roster_after.recruit_requests?.map(x => `${x.needed} ${x.role}`).join('; ') ?? ''}`) } catch (e) { setError((e as Error).message) } }
  async function sharePlan() { if (!task) return; try { const r = await api.share(task.id); const url = `${location.origin}/drive/${r.share_key}`; await navigator.clipboard.writeText(url); setShare(url) } catch (e) { setError((e as Error).message) } }
  const reduce = typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches
  const headline = (key: keyof typeof text) => text[key]
  const briefRoles = extraction ? extraction.roles.map((r, i) => ({ key: `extracted-${i}`, role: r.role, source: r.evidence_span || r.reason, confidence: r.confidence })) : (task?.roles ?? []).map(r => ({ key: r.id, role: r.role, source: r.evidence_span || r.required_skills.join(', '), confidence: r.confidence }))
  return <div className={`story ${reduce ? 'reduced' : ''}`} ref={root}>
    <div className="world-canvas" aria-hidden="true"><FilmLayers progress={progressRef}/>{reduce || !webglAvailable ? <img className="scene-still" src="/media/layers/dawn-board-base.webp" alt="Illustrative paper village"/> : sceneReady && <Suspense fallback={null}><VillageScene progress={progressRef}/></Suspense>}<span className="scene-illustrative">Illustrative · film layers</span></div>
    <aside className="progress-rail" aria-label="Story progress">{nav.map(n => <a key={n.id} href={`#${n.id}`} className={active === n.id ? 'active' : ''} aria-label={n.name} title={n.name}><span>{n.name}</span></a>)}</aside>
    <div className="story-scroll-hint">↓ {text.scroll}</div>
    <section className="chapter chapter-intro" id="intro" data-id="intro"><TransitionFilm start={0} end={10} poster="/media/film-poster-01.jpg" label="Dawn at the notice board" immediate/><div className="chapter-copy"><p className="eyebrow">{text.overline} <span>· 01 / 10</span></p><h1><span lang={lang} dangerouslySetInnerHTML={{ __html: headline('title') }} /></h1><p className="lead">{text.intro}</p><p className="story-note">An interactive paper village · <span>Illustrative</span></p><a className="jump-link" href="#interest">Explore the village ↓</a></div></section>
    <section className="chapter" id="interest" data-id="intro"><div className="chapter-copy"><p className="eyebrow">Interest · 02 / 10</p><h2>Many say yes.<br/><span>Then what?</span></h2><p>Interest is the beginning. A safe, role-complete team takes planning.</p><div className="source-figures"><strong>2.22+ crore <small>youth on MY Bharat</small></strong><strong>1.52+ lakh <small>opportunities</small></strong></div><small>Source: PIB backgrounder, 05 July 2026. Not affiliated with MY Bharat.</small><div className="paper-people">{volunteers.filter(v => v.opted_in_task_ids?.includes(task?.id ?? '')).slice(0, 5).map(v => <button key={v.id} title={`${v.age} · ${Object.keys(v.skills).join(', ') || v.self_declared_skills.join(', ')}`} onClick={() => setSelectedRole(`${v.display_name} · ${Object.keys(v.skills).join(', ') || v.self_declared_skills.join(', ')}`)}><i/><span>{v.display_name}</span></button>)}{selectedRole && <p role="status">{selectedRole}</p>}</div></div></section>
    <TransitionFilm start={10} end={20} poster="/media/film-poster-02.jpg" label="Young volunteers gather" />
    <section className="chapter" id="brief" data-id="brief"><div className="chapter-copy"><p className="eyebrow">The brief · 03 / 10</p><h2 dangerouslySetInnerHTML={{ __html: headline('brief') }} /><p className="quote-paper" lang={lang}>{task?.brief_text || 'गाँव स्तर पर स्वच्छ पेयजल और हाथ धोने की जागरूकता शिविर।'}</p><div className="evidence-phrases">{extraction?.roles.filter(r => r.evidence_span).map(r => <button key={r.role} onClick={() => setSelectedRole(r.role)}><mark>{r.evidence_span}</mark><span> → {r.role}</span>{selectedRole === r.role && <b>{text.detail}</b>}</button>)}</div><div className="role-chips">{briefRoles.map(r => <button key={r.key} className={selectedRole === r.key ? 'chosen' : ''} onClick={() => setSelectedRole(selectedRole === r.key ? '' : r.key)}><b>{r.role}</b><small>{r.source} · {r.confidence}</small>{selectedRole === r.key && <em>{text.detail}</em>}</button>)}</div><small>{text.role}: select any highlighted phrase to see its proposed role.</small></div></section>
    <TransitionFilm start={20} end={30} poster="/media/film-poster-03.jpg" label="The turmeric ring forms" />
    <section className="chapter" id="crew" data-id="crew"><div className="chapter-copy"><p className="eyebrow">The crew · 04 / 10</p><h2 dangerouslySetInnerHTML={{ __html: headline('crew') }} /><p>Only people who opted in. A solver weighs skills, travel, fairness and backup.</p><button className="action-button" onClick={plan} disabled={!task}>{text.plan}</button>{roster && <div className="crew-pill-list">{roster.assignments.map(a => <button key={a.volunteer_id} title={a.reasons.join(' · ')}>{a.volunteer_name}<small>{a.reasons.join(' · ')}</small></button>)}{roster.standby.map(s => <span key={s.volunteer_id}>↳ Standby · {s.volunteer_name}</span>)}</div>}{error && <p className="inline-error" role="alert">{error}</p>}</div></section>
    <TransitionFilm start={30} end={38.8} poster="/media/film-poster-04.jpg" label="Crew and backups settle into the ring" />
    <section className="chapter" id="bench" data-id="crew"><div className="chapter-copy"><p className="eyebrow">The bench · 05 / 10</p><h2>Every seat needs<br/><span>a second plan.</span></h2><p>Standby is only useful when the person has the right skills and is available. Safety-critical skills need host checks.</p>{roster?.standby.map(s => <p className="paper-slip" key={s.volunteer_id}>Standby · {s.volunteer_name}<small>{s.reason}</small></p>)}</div></section>
    <section className="chapter" id="verdict" data-id="verdict"><div className="chapter-copy"><p className="eyebrow">The verdict · 06 / 10</p><h2 dangerouslySetInnerHTML={{ __html: headline('verdict') }} /><div className={`verdict-stamp ${roster?.ready ? 'ready' : 'waiting'}`}>{roster ? (roster.ready ? 'READY · तैयार' : 'NOT READY · भर्ती चाहिए') : 'PLAN TO SEE'}</div>{roster?.recruit_requests?.map((r,i) => <p className="paper-slip" key={i}>{r.needed} more {r.role}<small>{r.slot.replaceAll('_',' ')} · {r.area} · within {r.max_travel_km} km · {r.reason}</small></p>)}<button className="quiet-button" onClick={sharePlan} disabled={!roster}>{text.share}</button>{share && <a className="share-result" href={share}>{share}</a>}</div></section>
    <TransitionFilm start={38.8} end={48.8} poster="/media/film-poster-05.jpg" label="The last gap closes and the seal lands" />
    <section className="chapter" id="dropout" data-id="verdict"><div className="chapter-copy"><p className="eyebrow">What if someone drops? · 07 / 10</p><h2>A real exit.<br/><span>A real re-plan.</span></h2><p>Heena P. is in the opted-in pool, but the default solver leaves her off the seated crew. This moment drops a real seated volunteer so the API can return an honest result.</p><button className="action-button" onClick={dropout} disabled={!roster}>{roster ? `Drop ${roster.assignments[3]?.volunteer_name ?? roster.assignments[0]?.volunteer_name ?? 'volunteer'}` : text.drop}</button>{dropResult && <p className="paper-slip" role="status">{dropResult}</p>}</div></section>
    <section className="chapter" id="evidence" data-id="evidence"><div className="chapter-copy"><p className="eyebrow">The drive and evidence · 08 / 10</p><h2 dangerouslySetInnerHTML={{ __html: headline('evidence') }} /><p>After the work, a host reviews contribution cards against attendance. The ledger records decisions; it does not prove the work happened.</p><p className="paper-slip">8 hours claimed · 5 hours recorded<small>Example flag · synthetic data</small></p><Link className="jump-link" to="/console">Review evidence in the console ↗</Link></div></section>
    <TransitionFilm start={48.8} end={58.8} poster="/media/film-poster-06.jpg" label="Drive, evidence and the village map" />
    <section className="chapter" id="districts" data-id="numbers"><div className="chapter-copy"><p className="eyebrow">Many villages · 09 / 10</p><h2>One small plan.<br/><span>Many places.</span></h2><p>District and block markers show only public geography and drive status. Map: illustrative.</p><Link className="jump-link" to="/districts">Explore the district view ↗</Link></div></section>
    <section className="chapter" id="numbers" data-id="numbers"><div className="chapter-copy"><p className="eyebrow">Synthetic evaluation · 10 / 10</p><h2 dangerouslySetInnerHTML={{ __html: headline('numbers') }} /><div className="story-metrics">{evalReport ? <><Metric target={evalReport.summary.cp_sat?.ready ?? 0} lang={lang} label="Ready · SewaCircle"/><Metric target={evalReport.summary.nearest_skill?.ready ?? 0} lang={lang} label="Ready · nearest skill"/><Metric target={evalReport.summary.cp_sat?.repeat_pick_share ?? 0} lang={lang} label="Repeat picks · SewaCircle"/><Metric target={evalReport.summary.nearest_skill?.repeat_pick_share ?? 0} lang={lang} label="Repeat picks · nearest skill"/><Metric value={`${formatNumber(evalReport.n_tasks,lang)} drives`} label="Evaluation set"/></> : <p>Loading live evaluation…</p>}</div><p className="small-caveat">Proxy results on synthetic data. No field impact claim.</p></div></section>
    <section className="chapter chapter-end" id="try" data-id="try"><div className="chapter-copy"><p className="eyebrow">Ready Crew · SewaCircle</p><h2 dangerouslySetInnerHTML={{ __html: headline('try') }} /><p>AI reads the brief. A deterministic solver proposes the team. A person approves.</p><div className="end-actions"><Link className="action-button" to="/console">Open organiser console ↗</Link><Link className="quiet-button" to="/volunteer">Volunteer view ↗</Link></div><p className="small-caveat">Synthetic data · Not affiliated with MY Bharat or any government body.</p></div></section>
  </div>
}
function Metric({ value, target, lang, label }: { value?: string; target?: number; lang?: Lang; label: string }) {
  const element = useRef<HTMLDivElement>(null); const [shown, setShown] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches ? target ?? 0 : 0)
  useEffect(() => { if (target === undefined || !element.current || matchMedia('(prefers-reduced-motion: reduce)').matches) return; const observer = new IntersectionObserver(entries => { if (!entries.some(e => e.isIntersecting)) return; observer.disconnect(); const start = performance.now(); const tick = (now: number) => { const p = Math.min(1, (now - start) / 800); setShown(p === 1 ? target : target * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(tick) }; requestAnimationFrame(tick) }, { threshold: .4 }); observer.observe(element.current); return () => observer.disconnect() }, [target])
  const ready = target === undefined || shown === target
  return <div className="story-metric" ref={element} data-counter-ready={ready}><strong>{target === undefined ? value : `${formatNumber(Math.round(shown * 100), lang ?? 'en')}%`}</strong><span>{label}</span></div>
}
