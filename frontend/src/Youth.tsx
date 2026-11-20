import { useEffect, useMemo, useState } from 'react'
import { api, type ProjectMatch, type YouthResult } from './api'
import { useUi } from './ui-context'

type District = { name: string; lat: number; lon: number }

const SLOTS = ['sat_morning', 'sun_morning', 'sat_afternoon', 'sun_afternoon', 'sat_evening', 'wed_evening'] as const
const INTERESTS = ['health', 'environment', 'education', 'disaster_relief', 'sports', 'food', 'elderly_care'] as const
const PART_ORDER = ['skills', 'availability', 'distance', 'interests'] as const

const L = {
  en: {
    kicker: 'For young people', title: 'Find a project that fits you.', sub: 'Tell us what you can do and when you are free. SevaSetu checks eligibility first, then ranks community projects with a clear % match and the reasons behind it.',
    profile: 'Your profile', age: 'Age', district: 'District', skills: 'Skills you have', interests: 'What you care about', slots: 'When you are free', find: 'Show my top projects', finding: 'Matching…', sample: 'Fill a sample profile',
    results: 'Your top projects', role: 'Best-fit role', improve: 'To raise this match', interested: "I'm interested", sent: 'Interest sent (demo)', excluded: 'Not open to you', synthetic: 'Synthetic projects · not affiliated with MY Bharat or any government body', none: 'Fill your profile and press the button to see matches.', check: 'host check needed',
    parts: { skills: 'skills', availability: 'time', distance: 'distance', interests: 'interest' },
    slot: { sat_morning: 'Sat morning', sun_morning: 'Sun morning', sat_afternoon: 'Sat afternoon', sun_afternoon: 'Sun afternoon', sat_evening: 'Sat evening', wed_evening: 'Wed evening' },
    interest: { health: 'Health', environment: 'Environment', education: 'Education', disaster_relief: 'Disaster relief', sports: 'Sports', food: 'Food', elderly_care: 'Elderly care' },
  },
  hi: {
    kicker: 'युवाओं के लिए', title: 'अपने लिए सही परियोजना खोजें।', sub: 'बताइए आप क्या कर सकते हैं और कब खाली हैं। सेवासेतु पहले पात्रता जाँचता है, फिर स्पष्ट % मेल और कारणों के साथ परियोजनाएँ सुझाता है।',
    profile: 'आपकी प्रोफ़ाइल', age: 'आयु', district: 'ज़िला', skills: 'आपके कौशल', interests: 'आपकी रुचि', slots: 'आप कब खाली हैं', find: 'मेरी शीर्ष परियोजनाएँ दिखाएँ', finding: 'मिलान हो रहा है…', sample: 'नमूना प्रोफ़ाइल भरें',
    results: 'आपकी शीर्ष परियोजनाएँ', role: 'सबसे उपयुक्त भूमिका', improve: 'मेल बढ़ाने के लिए', interested: 'मुझे रुचि है', sent: 'रुचि भेजी गई (डेमो)', excluded: 'आपके लिए खुली नहीं', synthetic: 'काल्पनिक परियोजनाएँ · MY Bharat या किसी सरकारी संस्था से संबद्ध नहीं', none: 'प्रोफ़ाइल भरें और बटन दबाएँ।', check: 'होस्ट जाँच ज़रूरी',
    parts: { skills: 'कौशल', availability: 'समय', distance: 'दूरी', interests: 'रुचि' },
    slot: { sat_morning: 'शनि सुबह', sun_morning: 'रवि सुबह', sat_afternoon: 'शनि दोपहर', sun_afternoon: 'रवि दोपहर', sat_evening: 'शनि शाम', wed_evening: 'बुध शाम' },
    interest: { health: 'स्वास्थ्य', environment: 'पर्यावरण', education: 'शिक्षा', disaster_relief: 'आपदा राहत', sports: 'खेल', food: 'भोजन', elderly_care: 'बुज़ुर्ग देखभाल' },
  },
}

function Ring({ value }: { value: number }) {
  return <div className="match-ring" style={{ '--p': value } as React.CSSProperties} role="img" aria-label={`${value}% match`}><span>{value}<small>%</small></span></div>
}

function MatchCard({ m, t, weights, rank }: { m: ProjectMatch; t: typeof L.en; weights: Record<string, number>; rank: number }) {
  const [sent, setSent] = useState(false)
  return <article className="match-card">
    <div className="match-head">
      <span className="match-rank">{String(rank).padStart(2, '0')}</span>
      <div className="match-title"><h3>{m.title}</h3><p>{m.block}, {m.district} · {t.slot[m.slot as keyof typeof t.slot] ?? m.slot} · {m.distance_km} km</p></div>
      <Ring value={m.percent} />
    </div>
    <div className="match-bar" aria-hidden="true">{PART_ORDER.map(k => <span key={k} className={`seg seg-${k}`} style={{ flexGrow: m.parts[k] || 0.0001 }} title={`${t.parts[k]} ${m.parts[k]}/${weights[k]}`} />)}</div>
    <ul className="match-parts">{PART_ORDER.map(k => <li key={k}><i className={`dot seg-${k}`} />{t.parts[k]} <b>{m.parts[k]}</b>/{weights[k]}</li>)}</ul>
    {m.best_role && <p className="match-role"><span>{t.role}</span> {m.best_role}{m.host_check_needed && <em> · {t.check}</em>}</p>}
    <ul className="match-reasons">{m.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
    {m.improve && <p className="match-improve"><span>{t.improve}:</span> {m.improve}</p>}
    <button className={`btn ${sent ? 'ghost' : ''}`} onClick={() => setSent(true)} disabled={sent}>{sent ? t.sent : t.interested}</button>
  </article>
}

export default function Youth() {
  const { lang } = useUi()
  const t = L[lang]
  const [skills, setSkills] = useState<Record<string, string>>({})
  const [districts, setDistricts] = useState<District[]>([])
  const [age, setAge] = useState(19)
  const [district, setDistrict] = useState('Kanpur Nagar')
  const [mySkills, setMySkills] = useState<string[]>([])
  const [interests, setInterests] = useState<string[]>([])
  const [slots, setSlots] = useState<string[]>([])
  const [result, setResult] = useState<YouthResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.meta().then(m => setSkills(m.skills)).catch(e => setError(e.message))
    api.geo().then(g => setDistricts(((g.districts as District[]) ?? []).slice().sort((a, b) => a.name.localeCompare(b.name)))).catch(() => undefined)
  }, [])
  const here = useMemo(() => districts.find(d => d.name === district), [districts, district])
  const toggle = (list: string[], set: (v: string[]) => void, v: string) => set(list.includes(v) ? list.filter(x => x !== v) : [...list, v])

  const find = async () => {
    if (!here) return
    setBusy(true); setError('')
    try { setResult(await api.youthRecommend({ age, lat: here.lat, lon: here.lon, district, skills: mySkills, interests, available_slots: slots }, lang)) } catch (e) { setError((e as Error).message) } finally { setBusy(false) }
  }
  const sample = () => { setAge(19); setDistrict('Kanpur Dehat'); setMySkills(['teaching_literacy', 'documentation_reporting', 'hygiene_promotion', 'first_aid', 'hindi_fluent']); setInterests(['health', 'education']); setSlots(['sat_morning', 'sun_morning', 'sat_afternoon']) }

  return <div className="page-shell youth-page">
    <div className="page-intro"><span className="kicker">{t.kicker}</span><h1>{t.title}</h1><p>{t.sub}</p>{error && <div className="callout bad" role="alert">{error}</div>}</div>
    <div className="youth-layout">
      <section className="work-panel youth-form" aria-labelledby="yp">
        <div className="youth-form-head"><h2 id="yp">{t.profile}</h2><button className="text-button" onClick={sample}>{t.sample}</button></div>
        <div className="youth-row">
          <label className="field"><span>{t.age}</span><input type="number" min={14} max={35} value={age} onChange={e => setAge(Number(e.target.value) || 0)} /></label>
          <label className="field"><span>{t.district}</span><select value={district} onChange={e => setDistrict(e.target.value)}>{districts.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}</select></label>
        </div>
        <fieldset className="chips"><legend>{t.skills}</legend>{Object.entries(skills).map(([id, label]) => <button type="button" key={id} className={`pick ${mySkills.includes(id) ? 'on' : ''}`} aria-pressed={mySkills.includes(id)} onClick={() => toggle(mySkills, setMySkills, id)}>{label}</button>)}</fieldset>
        <fieldset className="chips"><legend>{t.interests}</legend>{INTERESTS.map(k => <button type="button" key={k} className={`pick ${interests.includes(k) ? 'on' : ''}`} aria-pressed={interests.includes(k)} onClick={() => toggle(interests, setInterests, k)}>{t.interest[k]}</button>)}</fieldset>
        <fieldset className="chips"><legend>{t.slots}</legend>{SLOTS.map(s => <button type="button" key={s} className={`pick ${slots.includes(s) ? 'on' : ''}`} aria-pressed={slots.includes(s)} onClick={() => toggle(slots, setSlots, s)}>{t.slot[s]}</button>)}</fieldset>
        <button className="btn youth-go" onClick={find} disabled={busy || !here}>{busy ? t.finding : t.find}</button>
        <p className="small-caveat">{t.synthetic}</p>
      </section>
      <section className="youth-results" aria-live="polite" aria-labelledby="yr">
        <h2 id="yr">{t.results}</h2>
        {!result ? <p className="empty-state">{t.none}</p> : <>
          <div className="match-list">{result.matches.map((m, i) => <MatchCard key={m.task_id} m={m} t={t} weights={result.weights} rank={i + 1} />)}</div>
          {result.excluded.length > 0 && <div className="excluded"><h3>{t.excluded}</h3><ul>{result.excluded.map(x => <li key={x.task_id}><b>{x.title}</b> · {x.reason}</li>)}</ul></div>}
        </>}
      </section>
    </div>
  </div>
}
