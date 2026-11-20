import { lazy, Suspense, useEffect, useState } from 'react'
import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router'
import { Context, type UiContext } from './ui-context'
import { api, MOCK, setDemoRole } from './api'
import { tr, type Lang } from './i18n'

const Story = lazy(() => import('./Story'))
const Console = lazy(() => import('./Console'))
const Volunteer = lazy(() => import('./Volunteer'))
const District = lazy(() => import('./District'))
const Method = lazy(() => import('./Method'))
const Youth = lazy(() => import('./Youth'))

function Frame() {
  const [lang, setLang] = useState<Lang>(() => localStorage.getItem('sewa-lang') === 'hi' ? 'hi' : 'en')
  const [projector, setProjector] = useState(() => localStorage.getItem('sewa-projector') === 'true')
  const [role, setRole] = useState(() => localStorage.getItem('sewa-role') || 'organiser')
  const [actions, setActions] = useState<string[]>([])
  const [backendDown, setBackendDown] = useState(false)
  const location = useLocation()
  useEffect(() => { localStorage.setItem('sewa-lang', lang); document.documentElement.lang = lang }, [lang])
  useEffect(() => { localStorage.setItem('sewa-projector', String(projector)); document.documentElement.classList.toggle('projector', projector) }, [projector])
  useEffect(() => { localStorage.setItem('sewa-role', role); setDemoRole(role) }, [role])
  useEffect(() => { let active = true; api.capabilities(role).then(data => { if (active) setActions(data.actions) }).catch(() => { if (active) setActions([]) }); return () => { active = false } }, [role])
  useEffect(() => { window.scrollTo(0, 0) }, [location.pathname])
  // A missing backend used to show up only as an empty drive list. Say it plainly and offer the built-in demo data.
  useEffect(() => {
    if (MOCK) return
    let active = true
    const check = () => api.health().then(() => { if (active) setBackendDown(false) }).catch(() => { if (active) setBackendDown(true) })
    check(); const id = setInterval(check, 15000)
    return () => { active = false; clearInterval(id) }
  }, [])
  const ctx: UiContext = { lang, role, actions, t: key => tr(lang, key), toggleLang: () => setLang(v => v === 'en' ? 'hi' : 'en') }
  return <Context.Provider value={ctx}>
    <a className="skip" href="#main">Skip to content</a>
    <div className="notice"><span className="notice-dot" />{ctx.t('synthetic')}{MOCK && <b className="mock-notice">MOCK · not live</b>}<span className="notice-right">Not affiliated with MY Bharat or any government body.</span></div>
    {backendDown && <div className="backend-down" role="alert"><b>The SevaSetu backend is not running or not reachable</b>, so drives, crews and numbers cannot load. Start it in a second terminal (see <code>TEAM-HANDOFF.md</code> or run <code>start.ps1</code> / <code>start.sh</code>), or <a href={`${location.pathname}?mock=1`}>open the site with built-in demo data</a>.</div>}
    <header className="site-header">
      <Link to="/" className="logo"><span className="logo-mark">◉</span><span>Seva<span className="logo-accent">Setu</span><small>VOLUNTEER MATCHING</small></span></Link>
      <nav aria-label="Main navigation"><Link to="/">Story</Link><Link to="/youth">Find projects</Link><Link to="/console">Console</Link><Link to="/volunteer">Volunteer</Link><Link to="/districts">Districts</Link><Link to="/method">Method</Link></nav>
      <div className="header-actions"><label className="role-switch"><span>Role simulation<br/><small>not authentication · {actions.length} API actions</small></span><select aria-label="Demo role (simulation, not authentication)" value={role} onChange={e => setRole(e.target.value)}><option value="organiser">Organiser</option><option value="host">Host</option><option value="volunteer">Volunteer</option><option value="viewer">Viewer</option></select></label><button className="text-button" aria-pressed={projector} onClick={() => setProjector(v => !v)}>{projector ? 'Standard' : 'Projector'}</button><button className="lang-button" onClick={ctx.toggleLang}>{lang === 'en' ? 'हिन्दी' : 'English'}</button></div>
    </header>
    <main id="main"><Suspense fallback={<div className="loading-page">SevaSetu · Loading…</div>}><Routes><Route path="/" element={<Story lang={lang} />} /><Route path="/youth" element={<Youth />} /><Route path="/console" element={<Console />} /><Route path="/volunteer" element={<Volunteer />} /><Route path="/districts" element={<District />} /><Route path="/method" element={<Method />} /><Route path="/drive/:key" element={<SharePage />} /></Routes></Suspense></main>
    <footer className="site-footer"><Link to="/">SevaSetu</Link><span>Synthetic data · Not affiliated with MY Bharat or any government body.</span></footer>
  </Context.Provider>
}

function SharePage() {
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { api.drive(location.pathname.split('/').pop() ?? '').then(setSummary).catch(e => setError(e.message)) }, [])
  const roles = Array.isArray(summary?.roles) ? summary.roles as Array<{ role?: string; count?: number; required_skills?: string[]; safety_critical?: boolean }> : []
  return <div className="page-shell share-page"><section className="page-intro"><span className="kicker">Public drive summary · synthetic</span><h1>{summary ? String(summary.title) : 'One drive, one snapshot.'}</h1>{error ? <p role="alert">{error}</p> : summary ? <><p>{String(summary.district)} · {String(summary.block)}</p><div className={`share-verdict ${summary.ready ? 'ready' : 'not-ready'}`}>{summary.ready ? 'READY' : summary.ready === false ? 'NOT READY' : 'Not computed'}<span>{summary.stale ? 'Stale plan · recompute before sharing' : 'Snapshot is current'}</span></div><p>{String(summary.notice ?? 'This summary contains no volunteer identities.')}</p><h2>Roles in this drive</h2><ul className="share-roles">{roles.map((r,i)=><li key={`${r.role}-${i}`}><strong>{r.count ?? '—'} × {r.role}</strong><small>{r.required_skills?.join(', ')}{r.safety_critical ? ' · host-checked skill required' : ''}</small></li>)}</ul><p className="small-caveat">Last computed: {String(summary.computed_at ?? 'Not computed')} · Synthetic data · Not affiliated with MY Bharat or any government body.</p></> : <p>Loading share…</p>}</section></div>
}

export default function App() { return <BrowserRouter><Frame /></BrowserRouter> }
