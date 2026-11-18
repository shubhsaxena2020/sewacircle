import { lazy, Suspense, useEffect, useState } from 'react'
import { Link } from 'react-router'
import { ArrowRight, ArrowUpRight, ClipboardList, HeartHandshake, ShieldCheck, Sparkles } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import { api } from './api'
import { useUi } from './ui-context'
import { formatPercent } from './i18n'
import type { EvalReport } from './types'
import crewImage from './assets/gen/crew.webp'
import evidenceImage from './assets/gen/evidence.webp'

const CrewScene = lazy(() => import('./CrewScene'))
const manual = 'https://mswebdocstorage.blob.core.windows.net/ismailyusufcollegedocuments/Manual_-_MY_Bharat.pdf'
const pib = 'https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc202675911701.pdf'
const stages = [
  ['stageBrief', 'stageBriefText', ClipboardList], ['stageCrew', 'stageCrewText', HeartHandshake], ['stageVerdict', 'stageVerdictText', ShieldCheck], ['stageEvidence', 'stageEvidenceText', Sparkles],
] as const
export default function Landing() {
  const { t, lang } = useUi()
  const reducedMotion = useReducedMotion()
  const [showScene, setShowScene] = useState(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false
    const canvas = document.createElement('canvas')
    return !!(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  })
  const [report, setReport] = useState<EvalReport | null>(null)
  const [evalState, setEvalState] = useState<'loading'|'ready'|'error'>('loading')
  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setShowScene(!media.matches && !!(document.createElement('canvas').getContext('webgl2') || document.createElement('canvas').getContext('webgl')))
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [])
  useEffect(() => { api.evalReport().then(r=>{setReport(r);setEvalState('ready')}).catch(() => setEvalState('error')) }, [])
  return <div className="landing">
    <section className="hero"><div className="hero-copy">
      <div className="eyebrow"><span className="eyebrow-line"/>{t('heroEyebrow')}</div>
      <h1>{t('heroTitle')}</h1><p>{t('heroText')}</p>
      <div className="hero-actions"><Link className="button primary" to="/console">{t('openConsole')}<ArrowRight size={18}/></Link><Link className="text-link" to="/volunteer">{t('seeVolunteer')}<ArrowUpRight size={18}/></Link></div>
      <div className="hero-foot"><span className="pulse"/>{t('synthetic')} <span className="sep"/> {t('unaffiliated')}</div>
    </div><div className="hero-art">{showScene ? <Suspense fallback={<img src={crewImage} alt="" className="hero-fallback"/>}><CrewScene/></Suspense> : <img src={crewImage} alt={t('heroText')} className="hero-fallback"/>}</div></section>

    <section className="story-section gap-section"><div className="section-lead"><span className="kicker">01 / {t('sectionContext')}</span><h2>{t('afterInterested')}</h2><p>{t('gapText')}</p><div className="source-links"><a href={manual} target="_blank" rel="noreferrer">{t('sourceManual')} <ArrowUpRight size={15}/></a><a href={pib} target="_blank" rel="noreferrer">{t('sourceBackground')} <ArrowUpRight size={15}/></a></div></div><div className="gap-diagram" aria-label={t('afterInterested')}><div className="gap-card left"><span className="small-label">MY BHARAT</span><h3>{t('interested')}</h3><div className="mini-rows"><i/><i/><i/><i/></div></div><div className="gap-arrow"><ArrowRight size={27}/></div><div className="gap-card right"><span className="small-label">SEWACIRCLE</span><h3>{t('crewDecision')}</h3><div className="mini-grid"><i/><i/><i/><i/><i/><i/></div><strong>{t('verdictReady')}</strong></div></div></section>

    <section className="story-section process-section"><div className="section-heading"><span className="kicker">02 / {t('sectionProcess')}</span><h2>{t('how')}</h2></div><div className="stage-grid">{stages.map(([title, body, Icon], i) => <motion.article className="stage-card" key={title} whileHover={reducedMotion?undefined:{y:-4}} transition={{duration:reducedMotion?0:.2}}><span className="stage-index">{String(i + 1).padStart(2, '0')}</span><Icon size={28} strokeWidth={1.6}/><h3>{t(title)}</h3><p>{t(body)}</p></motion.article>)}</div></section>

    <section className="story-section safety-section"><div className="safety-copy"><span className="kicker">03 / {t('sectionSafety')}</span><h2>{t('safety')}</h2><p>{t('safetyText')}</p><Link to="/method" className="text-link">{t('method')}<ArrowUpRight size={18}/></Link></div><div className="safety-visual"><div className="safety-orbit"><ShieldCheck size={86} strokeWidth={1}/></div><div className="safety-tag">{t('checkedRule')}</div></div></section>

    <section className="story-section results-section"><div className="section-heading"><span className="kicker">04 / {t('sectionMeasured')}</span><h2>{t('results')}</h2><p>{t('resultsNote')}</p></div>{report ? <div className="result-cards">{(['cp_sat', 'nearest_skill', 'manual_greedy', 'random_feasible'] as const).map((method) => <article key={method}><span className="small-label">{t(method === 'cp_sat' ? 'methodCp' : method === 'nearest_skill' ? 'methodNear' : method === 'manual_greedy' ? 'methodManual' : 'methodRandom')}</span><strong>{formatPercent(report.summary[method]?.ready ?? 0, lang)}</strong><span>{t('readyMetric')}</span><div className="result-track"><i style={{ width: `${(report.summary[method]?.ready ?? 0) * 100}%` }}/></div></article>)}</div> : <p className="muted" role="status">{evalState==='loading'?t('loading'):t('evalUnavailable')}</p>}<Link className="button dark" to="/console?step=evaluation">{t('viewEval')}<ArrowRight size={18}/></Link></section>

    <section className="story-section evidence-story"><div className="evidence-image"><img src={evidenceImage} alt={t('evidenceArt')}/></div><div className="evidence-copy"><span className="kicker">05 / {t('sectionReview')}</span><h2>{t('principles')}</h2><div className="principle-list"><p>{t('principleOne')}</p><p>{t('principleTwo')}</p><p>{t('principleThree')}</p></div></div></section>

    <section className="story-section limit-section"><div><span className="kicker">06 / {t('sectionLimits')}</span><h2>{t('limits')}</h2></div><p>{t('limitsText')}</p></section>
    <section className="story-section faq-section"><div className="section-heading"><span className="kicker">07 / FAQ</span><h2>{t('faq')}</h2></div><div className="faq-list">{([['faqOne','faqOneA'],['faqTwo','faqTwoA'],['faqThree','faqThreeA']] as const).map(([q,a]) => <details key={q}><summary>{t(q)}</summary><p>{t(a)}</p></details>)}</div></section>
    <section className="end-cta"><span className="kicker">{t('heroEyebrow')}</span><h2>{t('heroTitle')}</h2><Link className="button primary" to="/console">{t('openConsole')}<ArrowRight size={18}/></Link></section>
  </div>
}
