import { Check, ClipboardCopy, Zap } from 'lucide-react'
import { motion } from 'motion/react'
import { useUi } from './ui-context'
import { formatNumber } from './i18n'
import type { RecruitRequest, RosterResult } from './types'

export function VerdictPanel({roster,title,block}:{roster:RosterResult;title:string;block:string}) {
  const {t,lang}=useUi();const ready=roster.ready===true
  return <motion.section key={ready?'yes':'no'} className={'verdict-panel '+(ready?'is-ready':'not-ready')} role="status" aria-live="polite" initial={{scale:.98,opacity:0}} animate={{scale:1,opacity:1}}><div className="verdict-icon">{ready?<Check size={32}/>:<Zap size={32}/>}</div><div><span className="kicker">{title} · {block}</span><h2>{ready?t('verdictReady'):t('verdictNo')}</h2><p>{ready?t('verdictReadyText'):t('verdictNoText')}</p></div><div className="verdict-ratio"><strong>{formatNumber(roster.metrics.slots_filled,lang)} / {formatNumber(roster.metrics.slots_required,lang)}</strong><span>{t('coverage')}</span></div></motion.section>
}
export function RecruitRequests({requests,onCopy,copied}:{requests:RecruitRequest[];onCopy:(request:RecruitRequest)=>void;copied:boolean}) {
  const {t,lang}=useUi()
  return <section className="work-panel recruit-panel"><h3>{t('recruitRequests')}</h3>{requests.length?requests.map((r,i)=><div className="recruit-row" key={i}><div><strong>{formatNumber(r.needed,lang)} × {r.role}</strong><p>{r.reason}</p><small>{r.area} · {r.slot} · {formatNumber(r.max_travel_km,lang)} km {r.checked_skill_required&&`· ${t('checkedRule')}`}</small></div><button className="button outline" onClick={()=>onCopy(r)}><ClipboardCopy size={16}/>{copied?t('copied'):t('copy')}</button></div>):<p>{t('noRequests')}</p>}</section>
}
