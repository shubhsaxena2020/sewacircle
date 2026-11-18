import { useCallback, useEffect, useMemo, useState } from 'react'
import { MOCK, api, defaultOptions } from './api'
import { LangCtx, Btn } from './ui'
import { tr, type Lang } from './i18n'
import { BriefStep, DEFAULT_BRIEF, EvalStep, EvidenceStep, LedgerStep, RolesStep, RosterStep } from './steps'
import type { ExtractionResult, RoleSpec, RosterBoth, RosterOptions, RosterResult, TaskSpec, Volunteer } from './types'

type Step = 1 | 2 | 3 | 4 | 5 | 6

export default function App() {
  const params = new URLSearchParams(location.search)
  const [lang, setLang] = useState<Lang>(params.get('lang') === 'hi' ? 'hi' : 'en')
  const [demo, setDemo] = useState(params.has('demo'))
  const [step, setStep] = useState<Step>(1)
  const [tasks, setTasks] = useState<TaskSpec[]>([])
  const [tasksErr, setTasksErr] = useState<unknown>(null)
  const [volunteers, setVolunteers] = useState<Volunteer[]>([])
  const [siteId, setSiteId] = useState('')
  const [brief, setBrief] = useState(DEFAULT_BRIEF)
  const [extraction, setExtraction] = useState<ExtractionResult | null>(null)
  const [roles, setRoles] = useState<RoleSpec[]>([])
  const [options, setOptions] = useState<RosterOptions>(defaultOptions)
  const [both, setBoth] = useState<RosterBoth | null>(null)
  const [roster, setRoster] = useState<RosterResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<unknown>(null)
  const [ledgerKey, setLedgerKey] = useState(0)

  useEffect(() => { document.documentElement.classList.toggle('demo', demo) }, [demo])
  useEffect(() => { document.documentElement.lang = lang }, [lang])
  useEffect(() => {
    api.tasks().then((t) => { setTasks(t); if (t[0]) setSiteId(t[0].id) }).catch(setTasksErr)
    api.volunteers().then(setVolunteers).catch(() => undefined)
  }, [])

  const site = tasks.find((t) => t.id === siteId)
  const task: TaskSpec | null = useMemo(() => (site ? { ...site, brief_text: brief, roles } : null), [site, brief, roles])
  const roleName = useMemo(() => Object.fromEntries(roles.map((r) => [r.id, r.role])), [roles])

  function onExtracted(e: ExtractionResult) {
    setExtraction(e)
    setRoles(e.roles.map((r, i) => ({
      id: `role-${String(i + 1).padStart(2, '0')}`, role: r.role, count: r.count, required_skills: r.required_skills, min_level: 1,
      priority: 'must', needs_experienced: false, evidence_span: r.evidence_span, confidence: r.confidence,
    })))
    setBoth(null); setRoster(null); setStep(2)
  }

  const runRoster = useCallback(async (opts: RosterOptions) => {
    if (!task) return
    setBusy(true); setErr(null)
    try {
      const r = await api.roster(task, opts)
      setBoth(r); setRoster(r.cp_sat)
    } catch (e) { setErr(e) } finally { setBusy(false) }
  }, [task])

  async function toRoster() { setStep(3); await runRoster(options) }

  const t = (k: Parameters<typeof tr>[1]) => tr(lang, k)
  const reach = { 1: true, 2: !!extraction, 3: !!roster, 4: !!roster, 5: !!roster, 6: true } as const
  const labels: [Step, Parameters<typeof tr>[1]][] = [[1, 'step1'], [2, 'step2'], [3, 'step3'], [4, 'step4'], [5, 'step5'], [6, 'step6']]

  return (
    <LangCtx.Provider value={lang}>
      <header className="top">
        <span className="brand">{t('appName')}</span>
        <span className="muted">{t('tagline')}</span>
        <span className="grow" />
        {MOCK ? <span className="banner mock" role="status">{t('mock')}</span> : null}
        <span className="banner" role="status">{t('synthetic')}</span>
        <Btn small variant="secondary" onClick={() => setLang(lang === 'en' ? 'hi' : 'en')} aria-label="language">{lang === 'en' ? 'हिन्दी' : 'English'}</Btn>
        <label className="row" style={{ gap: 6 }}><input type="checkbox" checked={demo} onChange={(e) => setDemo(e.target.checked)} />{t('demoMode')}</label>
      </header>
      <div className="shell">
        <nav className="steps" aria-label="steps">
          {labels.map(([n, k]) => (
            <button key={n} className={`step ${step === n ? 'active' : ''}`} disabled={!reach[n]} onClick={() => setStep(n)} aria-current={step === n ? 'step' : undefined}>{t(k)}</button>
          ))}
        </nav>
        <main>
          {step === 1 && <BriefStep tasks={tasks} siteId={siteId} setSiteId={setSiteId} brief={brief} setBrief={setBrief} onExtracted={onExtracted} tasksErr={tasksErr} />}
          {step === 2 && extraction && <RolesStep extraction={extraction} roles={roles} setRoles={setRoles} onNext={toRoster} busy={busy} err={err} />}
          {step === 3 && task && <RosterStep task={task} both={both} roster={roster} setRoster={setRoster} options={options} setOptions={setOptions} rerun={() => runRoster(options)} busy={busy} err={err} volunteers={volunteers} onApprove={() => setStep(4)} />}
          {step === 4 && task && roster && <EvidenceStep task={task} roster={roster} roleName={roleName} onChanged={() => setLedgerKey((k) => k + 1)} />}
          {step === 5 && <LedgerStep refreshKey={ledgerKey} />}
          {step === 6 && <EvalStep />}
        </main>
      </div>
    </LangCtx.Provider>
  )
}
