import { lazy, Suspense, useEffect, useState } from 'react'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation } from 'react-router'
import { ArrowUpRight, CircleDot, Languages, MonitorUp } from 'lucide-react'
import { MOCK } from './api'
import { tr, type Lang } from './i18n'
import { Context, useUi } from './ui-context'

const Landing = lazy(() => import('./Landing'))
const Console = lazy(() => import('./Console'))
const Volunteer = lazy(() => import('./Volunteer'))
const District = lazy(() => import('./District'))
const Method = lazy(() => import('./Method'))

function Frame() {
  const { t } = useUi()
  const location = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [location.pathname])
  const nav = [
    ['/', 'story'], ['/console', 'console'], ['/volunteer', 'volunteer'], ['/districts', 'district'], ['/method', 'method'],
  ] as const
  return <>
    <a className="skip" href="#main">{t('skip')}</a>
    <div className="notice"><span className="notice-dot" />{t('synthetic')}{MOCK && <strong className="mock-notice">{t('mock')}</strong>}<span className="notice-right">{t('unaffiliated')}</span></div>
    <header className="site-header">
      <Link to="/" className="logo" aria-label={`SewaCircle · ${t('brand')}`}><span className="logo-mark"><CircleDot size={23} strokeWidth={2.5}/></span><span>Sewa<span className="logo-accent">Circle</span></span></Link>
      <nav aria-label={t('mainNav')} className="main-nav">{nav.map(([href, key]) => <NavLink key={href} end={href === '/'} to={href} className={({ isActive }) => isActive ? 'active' : ''}>{t(key)}</NavLink>)}</nav>
      <div className="header-actions"><LanguageToggle/><ProjectorToggle/></div>
    </header>
    <main id="main"><Suspense fallback={<div className="loading-page">{t('loading')}</div>}><Routes>
      <Route path="/" element={<Landing/>}/><Route path="/console" element={<Console/>}/><Route path="/volunteer" element={<Volunteer/>}/><Route path="/districts" element={<District/>}/><Route path="/method" element={<Method/>}/>
    </Routes></Suspense></main>
    <footer className="site-footer"><div><Link className="logo" to="/">Sewa<span className="logo-accent">Circle</span></Link><p>{t('unaffiliated')} {t('synthetic')}.</p></div><div className="footer-links"><Link to="/method">{t('method')} <ArrowUpRight size={16}/></Link><Link to="/console">{t('console')} <ArrowUpRight size={16}/></Link></div></footer>
  </>
}
function LanguageToggle() {
  const { lang, toggleLang } = useUi()
  return <button className="icon-button language-button" aria-label={lang === 'en' ? 'हिन्दी' : 'English'} onClick={toggleLang}><Languages size={17}/><span>{lang === 'en' ? 'हिन्दी' : 'English'}</span></button>
}
function ProjectorToggle() {
  const { t } = useUi()
  const [on, setOn] = useState(localStorage.getItem('sewa-projector') === 'true')
  useEffect(() => { document.documentElement.classList.toggle('projector', on); localStorage.setItem('sewa-projector', String(on)) }, [on])
  return <button className={'icon-button projector-button ' + (on ? 'active' : '')} aria-label={t('projector')} aria-pressed={on} title={t('projector')} onClick={() => setOn(!on)}><MonitorUp size={17}/><span>{t('projector')}</span></button>
}
export default function App() {
  const [lang, setLang] = useState<Lang>(() => localStorage.getItem('sewa-lang') === 'hi' ? 'hi' : 'en')
  useEffect(() => { localStorage.setItem('sewa-lang', lang); document.documentElement.lang = lang }, [lang])
  return <Context.Provider value={{ lang, t: key => tr(lang, key), toggleLang: () => setLang(v => v === 'en' ? 'hi' : 'en') }}><BrowserRouter><Frame/></BrowserRouter></Context.Provider>
}
