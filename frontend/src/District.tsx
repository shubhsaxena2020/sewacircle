import { useEffect, useMemo, useState } from 'react'
import { ArrowUpRight, MapPin } from 'lucide-react'
import { api, defaultOptions } from './api'
import { useUi } from './ui-context'
import { formatNumber } from './i18n'
import type { TaskSpec, Volunteer } from './types'
import source from '../../docs/research/up_districts.json'

type Verdicts = Record<string, boolean | null>
export default function District() {
  const { t, lang } = useUi()
  const [tasks, setTasks] = useState<TaskSpec[]>([])
  const [volunteers, setVolunteers] = useState<Volunteer[]>([])
  const [verdicts, setVerdicts] = useState<Verdicts>({})
  const [selected, setSelected] = useState('Lucknow')
  useEffect(() => {
    api.tasks().then(async data => {
      setTasks(data)
      const results=await Promise.allSettled(data.map(task=>api.roster(task,defaultOptions)))
      setVerdicts(Object.fromEntries(data.map((task,i)=>[task.id,results[i].status==='fulfilled'?(results[i] as PromiseFulfilledResult<Awaited<ReturnType<typeof api.roster>>>).value.cp_sat.ready??null:null])))
    }).catch(()=>undefined)
    api.volunteers().then(setVolunteers).catch(()=>undefined)
  }, [])
  const district = source.districts.find(d=>d.name===selected)
  const localTasks=tasks.filter(x=>x.district===selected)
  const localVolunteers=volunteers.filter(x=>x.district===selected)
  const markers=useMemo(()=>source.districts.map(d=>({name:d.name,x:10+(d.lon-77.3)/(84.1-77.3)*79,y:12+(29.95-d.lat)/(29.95-24.3)*75})),[])
  return <div className="page-shell district-page"><div className="page-intro"><span className="kicker">{t('district')}</span><h1>{t('districtTitle')}</h1><p>{t('districtSub')}</p></div><div className="district-layout"><div className="map-card"><div className="map-top"><span>UTTAR PRADESH / SYNTHETIC LAYER</span><span>{formatNumber(source.districts.length,lang)} {t('district')}</span></div><div className="map-art"><svg viewBox="0 0 900 570" preserveAspectRatio="none" aria-hidden="true"><defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#e6e2d8" strokeWidth="1"/></pattern></defs><rect width="900" height="570" fill="url(#grid)"/><path d="M65 90 L145 57 L218 83 L275 57 L354 109 L438 91 L495 147 L588 121 L690 172 L740 222 L804 242 L769 291 L824 339 L758 370 L720 443 L651 459 L606 513 L546 462 L455 484 L410 430 L329 453 L279 400 L186 415 L149 362 L76 354 L99 290 L48 243 L95 181 Z" fill="#e8ece7" stroke="#9db2a9" strokeWidth="2" strokeDasharray="7 6"/><path d="M177 332 C320 250 510 267 696 309" fill="none" stroke="#b5c5ba" strokeWidth="3" strokeDasharray="3 9"/></svg>{markers.map(m=><button key={m.name} className={'map-marker '+(m.name===selected?'selected':'')+(tasks.some(x=>x.district===m.name)?' has-drive':'')} style={{left:`${m.x}%`,top:`${m.y}%`}} onClick={()=>setSelected(m.name)} aria-label={m.name} aria-pressed={m.name===selected} title={m.name}><span/></button>)}</div><div className="map-legend"><span><i className="legend-dot drive"/> {t('drives')}</span><span><i className="legend-dot"/> {t('district')}</span><span><MapPin size={15}/> {t('districtSource')}</span></div></div><aside className="district-detail"><span className="kicker">DISTRICT POINT</span><h2>{district?.name}</h2><div className="district-stat-grid"><div><strong>{formatNumber(localTasks.length,lang)}</strong><span>{t('drives')}</span></div><div><strong>{formatNumber(localVolunteers.length,lang)}</strong><span>{t('volunteers')}</span></div></div><h3>{t('drives')}</h3>{localTasks.length?localTasks.map(task=><article className="district-drive" key={task.id}><strong>{task.title}</strong><span>{task.block}</span><b className={verdicts[task.id]===true?'success-text':'warn-text'}>{verdicts[task.id]==null?t('notComputed'):verdicts[task.id]?t('verdictReady'):t('verdictNo')}</b></article>):<p className="empty-state">{t('noDrive')}</p>}<a href={source.coordinate_source_repo_url} target="_blank" rel="noreferrer" className="text-link">{t('districtSource')} <ArrowUpRight size={17}/></a><p className="map-caveat">{source.coordinate_caveat}</p></aside></div></div>
}
