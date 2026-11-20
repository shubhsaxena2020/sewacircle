import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router'
import Lenis from 'lenis'
import { api, defaultOptions } from './api'
import { formatNumber, type Lang } from './i18n'
import type { EvalReport, ExtractionResult, LedgerVerification, RosterResult, TaskSpec, Volunteer } from './types'
import type { Seat, SceneData } from './RingScene'

const RingScene = lazy(() => import('./RingScene'))

const CHAPTERS = ['intro', 'interest', 'brief', 'crew', 'bench', 'verdict', 'gap', 'dropout', 'evidence', 'numbers', 'districts', 'try'] as const
type Chapter = typeof CHAPTERS[number]
const RING_LABEL_CHAPTERS: Chapter[] = ['crew', 'bench', 'gap', 'dropout']

const T = {
  en: {
    kicker: 'Willing volunteers are here', h1: 'Can this\ndrive run?', sub: 'SevaSetu answers READY or NOT READY for a volunteer drive, and names exactly who is still needed.', start: 'Plan a crew',
    interestK: '02 · Interest', interestH: 'Many said yes.', interestP: 'National platforms bring interest at scale: 2.22+ crore youth are registered on MY Bharat (PIB backgrounder, 05 July 2026). An organiser still has to turn a list of willing people into a crew that actually shows up.', optedIn: 'people opted in to this drive',
    briefK: '03 · The brief', briefH: 'A brief becomes roles.', briefP: 'The organiser writes the drive in Hindi, English or Hinglish. AI proposes roles and shows the phrase each came from. Tap a phrase.', aiProposed: 'AI proposed · you confirm', confidence: 'confidence',
    crewK: '04 · The crew', crewH: 'Fill the ring.', crewP: 'Only people who opted in. A solver weighs skills, availability, travel, guardian consent for 16–17 year olds, and fairness — so the same few are not picked every time.', plan: 'Plan the crew', planning: 'Planning…', planned: 'Planned live from the API',
    benchK: '05 · The bench', benchH: 'Every seat needs\na second plan.', benchP: 'A standby with the right skills is ready for the essential roles. Safety roles accept host-checked skills only.', standby: 'Standby', covers: 'can cover',
    verdictK: '06 · The verdict', ready: 'READY', notReady: 'NOT READY', verdictP: 'Every essential role is filled and has cover.', verdictNo: 'Some roles have no cover yet.', share: 'Copy public summary link', copied: 'Link copied',
    gapK: '07 · Honest gaps', gapH: 'Not every drive\ncan run.', gapP: 'The solver will not pretend: it says what is missing and writes the recruit request.', copyReq: 'Copy recruit request',
    dropK: '08 · Someone drops out', dropH: 'A real exit.\nA real re-plan.', dropP: 'Drop a seated volunteer. The plan re-runs live: the standby steps in — and if that leaves a single point of failure, it says so.', drop: 'Drop', dropping: 'Re-planning…',
    evidenceK: '09 · After the drive', evidenceH: 'Work leaves a trail.', evidenceP: 'Host notes become draft contribution cards. Rules check them against attendance — one card claims 8 hours where 5 were recorded, so it is flagged. A host confirms, corrects or sends it back; every step goes into a hash-chained log.', verify: 'Verify the log', verified: 'Chain intact', broken: 'Chain broken at entry', empty: 'The log is empty after the demo reset. Confirm a card in the console to start it.',
    numbersK: '10 · Measured', numbersH: 'On 10 synthetic drives', readyLbl: 'drives READY with SevaSetu', nearest: 'with nearest-skill matching', repeat: 'repeat picks', repeatVs: 'careful human organiser: 43%', speed: 'to plan a crew from 500 volunteers', recall: 'of roles found by a small open model on one free GPU',
    districtsK: '11 · Many places', districtsH: 'One plan.\nMany drives.', districtsP: 'Every drive keeps its own live status: ready, not ready, or not computed yet.', openDistricts: 'Open the district view',
    tryK: '12 · Try it', tryH: 'Bring a real brief.', tryP: 'AI drafts. The solver decides. A person confirms. Nothing is auto-verified.', youth: 'Find a project for me', console: 'Open the organiser console', volunteer: 'Volunteer view', method: 'How it works',
    open: 'open seat', recruit: 'Recruit', hostCheck: 'host-checked', left: 'left the crew', synthetic: 'Synthetic data · not affiliated with MY Bharat or any government body',
  },
  hi: {
    kicker: 'इच्छुक स्वयंसेवक मौजूद हैं', h1: 'क्या यह अभियान\nचल सकता है?', sub: 'सेवासेतु बताता है — अभियान तैयार है या नहीं, और अभी ठीक किसकी ज़रूरत है।', start: 'टीम बनाएँ',
    interestK: '02 · रुचि', interestH: 'बहुतों ने हाँ कहा।', interestP: 'राष्ट्रीय मंच बड़े स्तर पर रुचि लाते हैं: MY Bharat पर 2.22+ करोड़ युवा पंजीकृत हैं (PIB, 05 जुलाई 2026)। फिर भी आयोजक को इच्छुक लोगों की सूची से ऐसी टीम बनानी होती है जो सच में पहुँचे।', optedIn: 'लोगों ने इस अभियान में रुचि दिखाई',
    briefK: '03 · विवरण', briefH: 'विवरण से भूमिकाएँ।', briefP: 'आयोजक हिन्दी, अंग्रेज़ी या हिंग्लिश में अभियान लिखता है। AI भूमिकाएँ सुझाता है और बताता है कि हर भूमिका किस वाक्यांश से आई। किसी वाक्यांश पर टैप करें।', aiProposed: 'AI ने सुझाया · आप पुष्टि करें', confidence: 'विश्वास',
    crewK: '04 · टीम', crewH: 'घेरा भरें।', crewP: 'केवल वही लोग जिन्होंने रुचि दिखाई। सॉल्वर कौशल, उपलब्धता, दूरी, 16–17 वर्ष वालों के लिए अभिभावक अनुमति और निष्पक्षता देखता है।', plan: 'टीम बनाएँ', planning: 'योजना बन रही है…', planned: 'API से अभी बनी योजना',
    benchK: '05 · विकल्प', benchH: 'हर सीट का\nदूसरा विकल्प।', benchP: 'ज़रूरी भूमिकाओं के लिए सही कौशल वाला विकल्प तैयार है। सुरक्षा भूमिकाओं में केवल होस्ट द्वारा जाँचे गए कौशल मान्य हैं।', standby: 'विकल्प', covers: 'संभाल सकते हैं',
    verdictK: '06 · फैसला', ready: 'तैयार', notReady: 'तैयार नहीं', verdictP: 'हर ज़रूरी भूमिका भरी है और उसका विकल्प भी है।', verdictNo: 'कुछ भूमिकाओं का अभी विकल्प नहीं है।', share: 'सार्वजनिक सारांश लिंक कॉपी करें', copied: 'लिंक कॉपी हो गया',
    gapK: '07 · ईमानदार कमी', gapH: 'हर अभियान\nनहीं चल सकता।', gapP: 'सॉल्वर दिखावा नहीं करता: वह बताता है क्या कम है और भर्ती अनुरोध लिखता है।', copyReq: 'भर्ती अनुरोध कॉपी करें',
    dropK: '08 · कोई हट जाए', dropH: 'असली बदलाव।\nअसली नई योजना।', dropP: 'किसी स्वयंसेवक को हटाएँ। योजना फिर से चलती है: विकल्प आगे आता है — और अगर इससे कोई कमज़ोर कड़ी बनती है, तो वह साफ़ बताता है।', drop: 'हटाएँ', dropping: 'नई योजना…',
    evidenceK: '09 · अभियान के बाद', evidenceH: 'काम का रिकॉर्ड।', evidenceP: 'होस्ट के नोट्स से योगदान कार्ड का मसौदा बनता है। नियम उपस्थिति से मिलान करते हैं — एक कार्ड में 8 घंटे का दावा है पर 5 दर्ज हैं, इसलिए उसे चिह्नित किया गया। होस्ट पुष्टि करता है, सुधारता है या लौटाता है; हर कदम हैश-शृंखला लॉग में जाता है।', verify: 'लॉग जाँचें', verified: 'शृंखला सही है', broken: 'शृंखला टूटी है, प्रविष्टि', empty: 'डेमो रीसेट के बाद लॉग खाली है। शुरू करने के लिए कंसोल में कोई कार्ड पक्का करें।',
    numbersK: '10 · मापा गया', numbersH: '10 काल्पनिक अभियानों पर', readyLbl: 'अभियान सेवासेतु से तैयार', nearest: 'निकटतम-कौशल मिलान से', repeat: 'बार-बार चयन', repeatVs: 'सावधान मानव आयोजक: 43%', speed: '500 स्वयंसेवकों से टीम बनाने में', recall: 'भूमिकाएँ एक मुफ़्त GPU पर छोटे ओपन मॉडल ने पहचानीं',
    districtsK: '11 · कई जगह', districtsH: 'एक योजना।\nकई अभियान।', districtsP: 'हर अभियान की अपनी स्थिति: तैयार, तैयार नहीं, या अभी गणना नहीं हुई।', openDistricts: 'ज़िला दृश्य खोलें',
    tryK: '12 · आज़माएँ', tryH: 'असली विवरण लाएँ।', tryP: 'AI मसौदा बनाता है। सॉल्वर तय करता है। व्यक्ति पुष्टि करता है। कुछ भी अपने-आप सत्यापित नहीं।', youth: 'मेरे लिए परियोजना खोजें', console: 'आयोजक कंसोल खोलें', volunteer: 'स्वयंसेवक दृश्य', method: 'यह कैसे काम करता है',
    open: 'खाली सीट', recruit: 'भर्ती', hostCheck: 'होस्ट-जाँचा', left: 'टीम से हटे', synthetic: 'काल्पनिक डेटा · MY Bharat या किसी सरकारी संस्था से संबद्ध नहीं',
  },
} as const

/** Word-by-word reveal: each word rises and un-blurs with a stagger when its chapter becomes active. */
function Split({ text }: { text: string }) {
  const NL = String.fromCharCode(10), NBSP = String.fromCharCode(160)
  const lines = text.split(NL).map(l => l.split(' '))
  const offsets = lines.map((_, li) => lines.slice(0, li).reduce((n, w) => n + w.length, 0))
  return <>{lines.map((words, li) => <span key={li} className="line">{words.map((w, wi) => <span key={wi} className="w" style={{ '--i': offsets[li] + wi } as React.CSSProperties}>{w}{wi < words.length - 1 ? NBSP : ''}</span>)}</span>)}</>
}

function webgl() { try { const c = document.createElement('canvas'); return Boolean(c.getContext('webgl2') || c.getContext('webgl')) } catch { return false } }

/** One seat per required slot, in role order, filled from a roster's assignments. */
function seatsFor(task: TaskSpec | null, roster: RosterResult | null, dropped?: string): Array<Seat & { role: string; roleId: string; name?: string; reasons?: string[]; safety: boolean }> {
  if (!task) return []
  const seats: Array<Seat & { role: string; roleId: string; name?: string; reasons?: string[]; safety: boolean }> = []
  for (const r of task.roles) for (let k = 0; k < r.count; k++) {
    const a = roster?.assignments.find(x => x.role_id === r.id && x.slot_index === k)
    const unfilled = roster && !a
    seats.push({ state: a ? 'filled' : unfilled ? 'gap' : 'empty', volunteerId: a?.volunteer_id, role: r.role, roleId: r.id, name: a?.volunteer_name, reasons: a?.reasons, safety: Boolean(r.safety_critical) })
  }
  if (dropped) seats.forEach(s => { if (s.volunteerId === dropped) s.state = 'dropped' })
  return seats.slice(0, 12)
}

function Counter({ to, suffix = '', decimals = 0, lang }: { to: number | null; suffix?: string; decimals?: number; lang: Lang }) {
  const el = useRef<HTMLSpanElement>(null)
  const [reduced] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches)
  const [anim, setV] = useState(0)
  const v = reduced && to !== null ? to : anim
  useEffect(() => {
    if (to === null || !el.current || reduced) return
    const io = new IntersectionObserver(es => {
      if (!es.some(e => e.isIntersecting)) return
      io.disconnect(); const t0 = performance.now()
      const tick = (now: number) => { const p = Math.min(1, (now - t0) / 1100); setV(p === 1 ? to : to * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(tick) }
      requestAnimationFrame(tick)
    }, { threshold: 0.5 })
    io.observe(el.current); return () => io.disconnect()
  }, [to, reduced])
  return <span ref={el} data-final={to !== null && v === to}>{to === null ? '—' : formatNumber(Number(v.toFixed(decimals)), lang)}{suffix}</span>
}

export default function Story({ lang }: { lang: Lang }) {
  const t = T[lang]
  const [motion] = useState(() => !matchMedia('(prefers-reduced-motion: reduce)').matches)
  const [gl] = useState(webgl)
  // The opening screen shows a still rendered from this same scene; the live WebGL ring takes over on the
  // first interaction (or after 6 s), so the headline paints and responds without waiting for shader compilation.
  const [stageOn, setStageOn] = useState(false)
  const [stageLive, setStageLive] = useState(false)
  useEffect(() => {
    const start = () => setStageOn(true)
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { start(); return }
    const evs = ['pointermove', 'wheel', 'touchstart', 'keydown', 'scroll'] as const
    evs.forEach(e => window.addEventListener(e, start, { once: true, passive: true }))
    const id = setTimeout(start, 6000)
    return () => { clearTimeout(id); evs.forEach(e => window.removeEventListener(e, start)) }
  }, [])
  const [chapter, setChapter] = useState<Chapter>('intro')
  const [task, setTask] = useState<TaskSpec | null>(null)
  const [gapTask, setGapTask] = useState<TaskSpec | null>(null)
  const [vols, setVols] = useState<Volunteer[]>([])
  const [extraction, setExtraction] = useState<ExtractionResult | null>(null)
  const [roster, setRoster] = useState<RosterResult | null>(null)
  const [gapRoster, setGapRoster] = useState<RosterResult | null>(null)
  const [dropRoster, setDropRoster] = useState<RosterResult | null>(null)
  const [dropped, setDropped] = useState<{ id: string; name: string; healed: boolean } | null>(null)
  const [evalReport, setEvalReport] = useState<EvalReport | null>(null)
  const [drives, setDrives] = useState<Array<{ ready: boolean | null }>>([])
  const [ledger, setLedger] = useState<LedgerVerification | null>(null)
  const [busy, setBusy] = useState('')
  const [phrase, setPhrase] = useState<number | null>(null)
  const [toast, setToast] = useState('')
  const [error, setError] = useState('')
  const labelEls = useRef<(HTMLElement | null)[]>([])
  const [hovered, setHovered] = useState<number | null>(null)
  const bar = useRef<HTMLDivElement>(null)
  const root = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api.tasksLang(lang).then(rows => { setTask(rows.find(x => x.id === 'task-01') ?? rows[0] ?? null); setGapTask(rows.find(x => x.id === 'task-05') ?? null) }).catch(e => setError(e.message))
    api.volunteers().then(setVols).catch(() => undefined)
    api.evalReport().then(setEvalReport).catch(() => undefined)
  }, [lang])
  useEffect(() => { if (task?.brief_text) api.extract(task.brief_text).then(setExtraction).catch(() => undefined) }, [task?.id, task?.brief_text])

  // smooth scroll + active chapter
  useEffect(() => {
    let lenis: Lenis | null = null
    if (motion) { lenis = new Lenis({ lerp: 0.11 }); const raf = (time: number) => { lenis?.raf(time); id = requestAnimationFrame(raf) }; let id = requestAnimationFrame(raf); const stop = () => cancelAnimationFrame(id); return () => { stop(); lenis?.destroy() } }
  }, [motion])
  useEffect(() => {
    const onScroll = () => { const h = document.documentElement; if (bar.current) bar.current.style.transform = `scaleX(${h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)})` }
    // magnetic buttons (pattern from Motion Primitives' Magnetic, written fresh): pull toward the pointer, spring back
    const onMove = (e: PointerEvent) => {
      const b = (e.target as HTMLElement).closest<HTMLElement>('.story .btn'); if (!b || !motion) return
      const r = b.getBoundingClientRect(); b.style.transform = `translate(${((e.clientX - r.left) / r.width - 0.5) * 10}px, ${((e.clientY - r.top) / r.height - 0.5) * 8}px)`
    }
    const onLeave = (e: PointerEvent) => { const b = (e.target as HTMLElement).closest<HTMLElement>('.story .btn'); if (b) b.style.transform = '' }
    window.addEventListener('scroll', onScroll, { passive: true }); root.current?.addEventListener('pointermove', onMove); root.current?.addEventListener('pointerout', onLeave)
    const node = root.current
    return () => { window.removeEventListener('scroll', onScroll); node?.removeEventListener('pointermove', onMove); node?.removeEventListener('pointerout', onLeave) }
  }, [motion])
  useEffect(() => {
    const els = root.current?.querySelectorAll<HTMLElement>('[data-chapter]') ?? []
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) setChapter((e.target as HTMLElement).dataset.chapter as Chapter) }), { rootMargin: '-48% 0px -48% 0px' })
    els.forEach(el => io.observe(el)); return () => io.disconnect()
  }, [])

  const plan = async () => {
    if (!task || busy) return
    setBusy('plan'); setError('')
    try { const r = await api.roster(task, defaultOptions, lang); setRoster(r.cp_sat); setDropRoster(null); setDropped(null) } catch (e) { setError((e as Error).message) } finally { setBusy('') }
  }
  // scrolling past the crew chapter without clicking still shows a live plan
  // eslint-disable-next-line react-hooks/exhaustive-deps, react/set-state-in-effect -- one-shot API call when the reader scrolls past the crew chapter without clicking
  useEffect(() => { if (['bench', 'verdict'].includes(chapter) && !roster && task && !busy) void plan() }, [chapter, roster, task])
  useEffect(() => {
    if (chapter === 'gap' && gapTask && !gapRoster) api.roster(gapTask, defaultOptions, lang).then(r => setGapRoster(r.cp_sat)).catch(e => setError(e.message))
    if (chapter === 'districts' && !drives.length) api.driveStatus().then(s => setDrives(((s.tasks as Array<{ ready: boolean | null }>) ?? []).map(x => ({ ready: x.ready })))).catch(() => undefined)
  }, [chapter, gapTask, gapRoster, drives.length, lang])

  const dropOne = async () => {
    const base = dropRoster ?? roster
    if (!task || !base || busy) return
    const target = base.assignments[3] ?? base.assignments[0]
    if (!target) return
    setBusy('drop'); setError('')
    try {
      const r = await api.dropout(task, base, target.volunteer_id, defaultOptions)
      setDropped({ id: target.volunteer_id, name: target.volunteer_name, healed: r.healed_with_standby })
      setDropRoster(r.roster_after)
    } catch (e) { setError((e as Error).message) } finally { setBusy('') }
  }
  const copy = async (text: string) => { try { await navigator.clipboard.writeText(text); setToast(t.copied) } catch { setToast(text) } setTimeout(() => setToast(''), 2400) }
  const share = async () => { if (!task) return; try { const r = await api.share(task.id); await copy(`${location.origin}/drive/${r.share_key}`) } catch (e) { setError((e as Error).message) } }

  const shownRoster = chapter === 'dropout' && dropRoster ? dropRoster : roster
  const seats = useMemo(() => chapter === 'gap' ? seatsFor(gapTask, gapRoster) : seatsFor(task, shownRoster, chapter === 'dropout' ? undefined : undefined), [chapter, task, gapTask, gapRoster, shownRoster])
  const poolTask = chapter === 'gap' ? gapTask : task
  const poolIds = useMemo(() => {
    const opted = vols.filter(v => poolTask && v.opted_in_task_ids?.includes(poolTask.id))
    return (opted.length ? opted : vols.slice(0, 40)).map(v => v.id)
  }, [vols, poolTask])
  const optedCount = useMemo(() => task ? vols.filter(v => v.opted_in_task_ids?.includes(task.id)).length : 0, [vols, task])
  const standby = chapter === 'gap' ? gapRoster?.standby[0] : shownRoster?.standby[0]
  const activeRoster = chapter === 'gap' ? gapRoster : shownRoster
  const sceneData: SceneData = { chapter, seats, poolIds, standbyId: standby?.volunteer_id, glow: chapter === 'verdict' && roster?.ready === true, drives: drives.length ? drives : Array.from({ length: 10 }, () => ({ ready: null })), hovered }
  const showLabels = RING_LABEL_CHAPTERS.includes(chapter) && Boolean(activeRoster)
  const spans = useMemo(() => extraction?.roles ?? [], [extraction])
  const briefHtml = useMemo(() => {
    const text = task?.brief_text ?? ''
    const parts: Array<{ s: string; i: number | null }> = []
    let rest = text
    const found = spans.map((r, i) => ({ i, span: r.evidence_span })).filter(x => x.span && text.includes(x.span))
    while (rest) {
      let best: { i: number; at: number; span: string } | null = null
      for (const f of found) { const at = rest.indexOf(f.span); if (at >= 0 && (!best || at < best.at)) best = { i: f.i, at, span: f.span } }
      if (!best) { parts.push({ s: rest, i: null }); break }
      if (best.at) parts.push({ s: rest.slice(0, best.at), i: null })
      parts.push({ s: best.span, i: best.i }); rest = rest.slice(best.at + best.span.length)
    }
    return parts
  }, [task?.brief_text, spans])
  const ev = evalReport?.summary
  const recruitText = (gapRoster?.recruit_requests ?? []).map(r => `${r.needed} × ${r.role} · ${r.slot.replaceAll('_', ' ')} · ${r.area} · within ${r.max_travel_km} km`).join('\n')

  return <div className={`story chapter-${chapter}`} ref={root}>
    <div className="stage" aria-hidden="true">
      {gl ? <>{!stageLive && <picture className="stage-still"><source media="(max-width: 820px)" srcSet="/media/ring-hero-m.webp" /><img src="/media/ring-hero.webp" alt="" fetchPriority="high" /></picture>}{stageOn && <Suspense fallback={null}><RingScene data={sceneData} labelEls={labelEls} motion={motion} onHover={setHovered} onReady={() => setStageLive(true)} /></Suspense>}</> : <svg className="stage-fallback" viewBox="0 0 800 500"><ellipse cx="520" cy="250" rx="240" ry="100" fill="none" stroke="#c98a2e" strokeWidth="26" /></svg>}
      <div className={`seat-labels ${showLabels ? 'on' : ''}`}>
        {seats.map((s, i) => <div key={`${chapter}-${i}`} ref={el => { labelEls.current[i] = el }} className={`seat-label s-${s.state} ${hovered === i ? 'hot' : ''}`} onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)}>
          <div className="seat-inner">
            <b>{s.state === 'filled' ? s.name : s.state === 'gap' ? `${t.recruit}: ${s.role}` : s.state === 'dropped' ? s.name : t.open}</b>
            <small>{s.state === 'dropped' ? t.left : s.role}{s.safety && s.state === 'filled' ? ` · ${t.hostCheck} ✓` : ''}</small>
            {s.state === 'filled' && s.reasons?.length ? <ul className="why">{s.reasons.slice(0, 4).map((r, k) => <li key={k}>{r}</li>)}</ul> : null}
          </div>
        </div>)}
      </div>
    </div>
    <ul className="sr-only" aria-live="polite" aria-label="Crew on the ring">{seats.map((s, i) => <li key={i}>{s.state === 'filled' ? `${s.name}, ${s.role}. ${s.reasons?.join('. ') ?? ''}` : s.state === 'gap' ? `${t.recruit}: ${s.role}` : `${t.open}: ${s.role}`}</li>)}</ul>
    <nav className="chapter-dots" aria-label="Story chapters">{CHAPTERS.map((c, i) => <a key={c} href={`#${c}`} aria-current={chapter === c ? 'step' : undefined} aria-label={`${String(i + 1).padStart(2, '0')} ${c}`}><span>{String(i + 1).padStart(2, '0')} · {c}</span></a>)}</nav>
    <div className="scroll-bar" ref={bar} aria-hidden="true" />
    {toast && <div className="toast" role="status">{toast}</div>}
    {error && <div className="toast toast-error" role="alert">{error}</div>}

    <section id="intro" data-chapter="intro" className={`ch ch-intro ${chapter === 'intro' ? 'on' : ''}`}>
      <p className="k">{t.kicker}</p>
      <h1 lang={lang}><Split text={t.h1} /></h1>
      <p className="lede">{t.sub}</p>
      <a className="btn" href="#crew">{t.start} ↓</a>
    </section>

    <section id="interest" data-chapter="interest" className={`ch ${chapter === 'interest' ? 'on' : ''}`}>
      <p className="k">{t.interestK}</p>
      <h2><Split text={t.interestH} /></h2>
      <p className="giant"><Counter to={optedCount || null} lang={lang} /></p>
      <p className="giant-label">{t.optedIn}</p>
      <p className="body">{t.interestP}</p>
    </section>

    <section id="brief" data-chapter="brief" className={`ch ${chapter === 'brief' ? 'on' : ''}`}>
      <p className="k">{t.briefK}</p>
      <h2><Split text={t.briefH} /></h2>
      <p className="body">{t.briefP}</p>
      <blockquote className="brief" lang={task?.language === 'hi' ? 'hi' : undefined}>{briefHtml.map((p, k) => p.i === null ? <span key={k}>{p.s}</span> : <button key={k} className={`phrase ${phrase === p.i ? 'on' : ''}`} onClick={() => setPhrase(p.i)} aria-pressed={phrase === p.i}>{p.s}</button>)}</blockquote>
      <div className="role-chips">{spans.map((r, i) => <button key={i} className={`chip ${phrase === i ? 'on' : ''}`} onClick={() => setPhrase(i)}><b>{r.role}</b><small>{phrase === i ? t.aiProposed : `${t.confidence}: ${r.confidence}`}</small></button>)}</div>
    </section>

    <section id="crew" data-chapter="crew" className={`ch ${chapter === 'crew' ? 'on' : ''}`}>
      <p className="k">{t.crewK}</p>
      <h2><Split text={t.crewH} /></h2>
      <p className="body">{t.crewP}</p>
      <button className="btn" onClick={plan} disabled={busy === 'plan' || !task}>{busy === 'plan' ? t.planning : t.plan}</button>
      {roster && <p className="meta">{t.planned} · {roster.metrics.slots_filled}/{roster.metrics.slots_required} · {formatNumber(Math.round(roster.metrics.solve_ms), lang)} ms</p>}
    </section>

    <section id="bench" data-chapter="bench" className={`ch ${chapter === 'bench' ? 'on' : ''}`}>
      <p className="k">{t.benchK}</p>
      <h2><Split text={t.benchH} /></h2>
      <p className="body">{t.benchP}</p>
      {roster?.standby.map(s => <p key={s.volunteer_id} className="standby-line"><b>{t.standby}: {s.volunteer_name}</b> — {t.covers} {s.covers_role_ids.map(id => task?.roles.find(r => r.id === id)?.role ?? id).join(', ')}</p>)}
    </section>

    <section id="verdict" data-chapter="verdict" className={`ch ch-center ${chapter === 'verdict' ? 'on' : ''}`}>
      <p className="k">{t.verdictK}</p>
      <p className={`verdict ${roster?.ready ? 'ok' : roster ? 'no' : ''}`}>{roster ? (roster.ready ? `${t.ready} · तैयार` : `${t.notReady}`) : '…'}</p>
      <p className="body">{roster?.ready ? t.verdictP : roster ? t.verdictNo : ''}</p>
      <button className="btn ghost" onClick={share} disabled={!roster}>{t.share}</button>
    </section>

    <section id="gap" data-chapter="gap" className={`ch ${chapter === 'gap' ? 'on' : ''}`}>
      <p className="k">{t.gapK}</p>
      <h2><Split text={t.gapH} /></h2>
      <p className="body">{gapTask ? `${gapTask.title}, ${gapTask.block}, ${gapTask.district}. ` : ''}{t.gapP}</p>
      {gapRoster && <><p className={`verdict small ${gapRoster.ready ? 'ok' : 'no'}`}>{gapRoster.ready ? t.ready : t.notReady}</p>
        <ul className="recruit">{gapRoster.recruit_requests?.map((r, i) => <li key={i}><b>{r.needed} × {r.role}</b><small>{r.slot.replaceAll('_', ' ')} · {r.area} · ≤ {r.max_travel_km} km{r.checked_skill_required ? ` · ${t.hostCheck}` : ''}</small><small>{r.reason}</small></li>)}</ul>
        {recruitText && <button className="btn ghost" onClick={() => copy(recruitText)}>{t.copyReq}</button>}</>}
    </section>

    <section id="dropout" data-chapter="dropout" className={`ch ${chapter === 'dropout' ? 'on' : ''}`}>
      <p className="k">{t.dropK}</p>
      <h2><Split text={t.dropH} /></h2>
      <p className="body">{t.dropP}</p>
      <button className="btn" onClick={dropOne} disabled={!roster || busy === 'drop'}>{busy === 'drop' ? t.dropping : `${t.drop} ${((dropRoster ?? roster)?.assignments[3] ?? (dropRoster ?? roster)?.assignments[0])?.volunteer_name ?? ''}`}</button>
      {dropped && dropRoster && <div className="drop-result" role="status"><p><b>{dropped.name}</b> {t.left}. {dropped.healed ? `${t.standby} ↑` : ''}</p><p className={`verdict small ${dropRoster.ready ? 'ok' : 'no'}`}>{dropRoster.ready ? t.ready : t.notReady}</p>{dropRoster.recruit_requests?.map((r, i) => <p key={i} className="meta">{r.needed} × {r.role} — {r.reason}</p>)}</div>}
    </section>

    <section id="evidence" data-chapter="evidence" className={`ch ${chapter === 'evidence' ? 'on' : ''}`}>
      <p className="k">{t.evidenceK}</p>
      <h2><Split text={t.evidenceH} /></h2>
      <p className="body">{t.evidenceP}</p>
      <div className="card-demo"><span className="flag">8 h claimed · 5 h recorded</span><span>Draft · AI</span></div>
      <button className="btn ghost" onClick={() => api.verify().then(setLedger).catch(e => setError(e.message))}>{t.verify}</button>
      {ledger && <p className="meta" role="status">{ledger.entries === 0 ? t.empty : ledger.ok ? `${t.verified} · ${ledger.entries}` : `${t.broken} ${ledger.first_bad_index}`}</p>}
    </section>

    <section id="numbers" data-chapter="numbers" className={`ch ch-numbers ${chapter === 'numbers' ? 'on' : ''}`}>
      <p className="k">{t.numbersK} · {t.numbersH}</p>
      <div className="nums">
        <div className="num big"><Counter to={ev ? Math.round(ev.cp_sat.ready * 100) : null} suffix="%" lang={lang} /><small>{t.readyLbl}</small><em>{ev ? `${Math.round(ev.nearest_skill.ready * 100)}%` : '—'} {t.nearest}</em></div>
        <div className="num"><Counter to={ev ? Math.round(ev.cp_sat.repeat_pick_share * 100) : null} suffix="%" lang={lang} /><small>{t.repeat}</small><em>{t.repeatVs}</em></div>
        <div className="num"><span>0.33 s</span><small>{t.speed}</small></div>
        <div className="num"><span>93%</span><small>{t.recall}</small></div>
      </div>
      <p className="source">{t.synthetic} · docs/EVAL_RESULTS.md · docs/LOCAL_MODEL_RESULTS.md</p>
    </section>

    <section id="districts" data-chapter="districts" className={`ch ${chapter === 'districts' ? 'on' : ''}`}>
      <p className="k">{t.districtsK}</p>
      <h2><Split text={t.districtsH} /></h2>
      <p className="body">{t.districtsP}</p>
      <Link className="btn ghost" to="/districts">{t.openDistricts} →</Link>
    </section>

    <section id="try" data-chapter="try" className={`ch ch-center ${chapter === 'try' ? 'on' : ''}`}>
      <p className="k">{t.tryK}</p>
      <h2><Split text={t.tryH} /></h2>
      <p className="body">{t.tryP}</p>
      <div className="row"><Link className="btn" to="/youth">{t.youth} →</Link><Link className="btn ghost" to="/console">{t.console} →</Link><Link className="btn ghost" to="/volunteer">{t.volunteer}</Link><Link className="btn ghost" to="/method">{t.method}</Link></div>
      <p className="source">{t.synthetic}</p>
    </section>
  </div>
}
