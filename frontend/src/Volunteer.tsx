import { useEffect, useState } from 'react'
import { ShieldCheck, UserRound } from 'lucide-react'
import { api } from './api'
import { useUi } from './ui-context'
import { formatNumber, formatSlot } from './i18n'
import type { ContributionCard, TaskSpec, Volunteer as VolunteerType } from './types'

export default function Volunteer() {
  const { t, lang, role } = useUi()
  const [volunteers, setVolunteers] = useState<VolunteerType[]>([])
  const [tasks, setTasks] = useState<TaskSpec[]>([])
  const [cards, setCards] = useState<ContributionCard[]>([])
  const [id, setId] = useState('')
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    api.tasks().then(rows => { if (active) setTasks(rows) }).catch(e => { if (active) setError(e.message) })
    if (role === 'organiser') {
      api.volunteers().then(rows => { if (active) { setVolunteers(rows); setId(rows[0]?.id ?? '') } }).catch(e => { if (active) setError(e.message) })
      api.cards().then(rows => { if (active) setCards(rows) }).catch(e => { if (active) setError(e.message) })
    }
    return () => { active = false }
  }, [role])
  const person = volunteers.find(v => v.id === id)
  const opted = tasks.filter(task => person?.opted_in_task_ids?.includes(task.id))
  const confirmed = cards.filter(card => card.volunteer_id === id && ['confirmed', 'corrected'].includes(card.status))
  return <div className="page-shell volunteer-page">
    <div className="page-intro"><span className="kicker">{t('volunteer')}</span><h1>{t('volunteerTitle')}</h1><p>{t('volunteerSub')}</p>{error && <div className="callout bad" role="alert">{error}</div>}</div>
    {role !== 'organiser' ? <section className="work-panel"><span className="kicker">Volunteer access</span><h2>This demo has no personal sign-in.</h2><p>The current role is a simulation, not authentication. The API does not expose a self-service volunteer profile endpoint, so personal roster data is hidden here.</p><p>Public synthetic drive details remain available in <a href="/districts">Districts</a>. Switch to organiser to inspect synthetic sample profiles.</p></section> : <div className="volunteer-layout">
      <aside className="profile-card"><div className="profile-symbol"><UserRound size={43} strokeWidth={1.5}/></div><label className="field"><span>{t('profile')}</span><select value={id} onChange={e => setId(e.target.value)}>{volunteers.map(v => <option key={v.id} value={v.id}>{v.display_name} · {v.block}</option>)}</select></label>{person && <div className="profile-meta"><h2>{person.display_name}</h2><p>{person.block}, {person.district}</p><div><span>{formatNumber(person.age, lang)}</span><span>{person.languages.join(' · ')}</span></div></div>}<div className="profile-notice">{t('synthetic')} · {t('unaffiliated')}</div></aside>
      <div className="volunteer-main"><section className="work-panel"><span className="kicker">{t('optedDrives')}</span><h2>{t('optedDrives')}</h2><div className="opted-list">{opted.length ? opted.map(task => <article key={task.id}><span className="opted-icon">↗</span><div><strong>{task.title}</strong><p>{task.block}, {task.district} · {formatSlot(task.slot, lang)}</p></div></article>) : <p className="empty-state">{t('noDrive')}</p>}</div></section>
        <div className="skill-columns"><section className="work-panel"><div className="skill-header checked"><ShieldCheck size={21}/><h2>{t('checkedSkills')}</h2></div>{person && Object.keys(person.skills).length ? <div className="skill-list">{Object.entries(person.skills).map(([name, level]) => <span key={name}>{name.replaceAll('_', ' ')} <b>{formatNumber(level, lang)}</b></span>)}</div> : <p>{t('noSkills')}</p>}</section><section className="work-panel"><div className="skill-header"><UserRound size={21}/><h2>{t('declaredSkills')}</h2></div>{person?.self_declared_skills.length ? <div className="skill-list">{person.self_declared_skills.map(name => <span key={name}>{name.replaceAll('_', ' ')}</span>)}</div> : <p>{t('noSkills')}</p>}</section></div>
        <section className="safety-note"><ShieldCheck size={29}/><div><h3>{t('safetyWhy')}</h3><p>{t('safetyWhyText')}</p></div></section><section className="work-panel"><span className="kicker">{t('contributions')}</span><h2>{t('contributions')}</h2>{confirmed.length ? confirmed.map(card => <article className="volunteer-contribution" key={card.id}><div><strong>{card.role}</strong><p>{card.summary}</p></div><span>{formatNumber(card.claimed_hours, lang, 1)} {t('hours')}</span></article>) : <p className="empty-state">{t('noContrib')}</p>}</section>
      </div>
    </div>}
  </div>
}
