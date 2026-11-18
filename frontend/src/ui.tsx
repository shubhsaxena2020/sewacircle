import { createContext, useContext, type ReactNode } from 'react'
import { tr, type Key, type Lang } from './i18n'
import type { CardStatus } from './types'

export const LangCtx = createContext<Lang>('en')
export const useT = () => {
  const lang = useContext(LangCtx)
  return (k: Key) => tr(lang, k)
}

export function Chip({ kind, children }: { kind: 'ok' | 'draft' | 'warn' | 'pending' | 'info'; children: ReactNode }) {
  const icon = { ok: '✓', draft: '✎', warn: '!', pending: '…', info: 'i' }[kind]
  return <span className={`chip ${kind}`}><span aria-hidden="true">{icon}</span>{children}</span>
}

export function StatusChip({ status }: { status: CardStatus }) {
  const t = useT()
  const map: Record<CardStatus, ['ok' | 'draft' | 'warn' | 'pending' | 'info', 'confirmed' | 'draft' | 'flagged' | 'corrected' | 'rejected']> = {
    draft: ['draft', 'draft'], flagged: ['warn', 'flagged'], confirmed: ['ok', 'confirmed'], corrected: ['ok', 'corrected'], rejected: ['warn', 'rejected'],
  }
  const [kind, key] = map[status]
  return <Chip kind={kind}>{t(key)}</Chip>
}

export function Bar({ value, kind }: { value: number; kind: 'good' | 'base' }) {
  const pct = Math.max(0, Math.min(1, value)) * 100
  return <div className="bar" role="img" aria-label={`${Math.round(pct)}%`}><i className={kind} style={{ width: `${pct}%` }} /></div>
}

export function Btn(props: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary'; small?: boolean }) {
  const { variant = 'primary', small, className, ...rest } = props
  return <button {...rest} className={`btn ${variant === 'secondary' ? 'secondary' : ''} ${small ? 'small' : ''} ${className ?? ''}`} />
}

export function ErrorNote({ err }: { err: unknown }) {
  const t = useT()
  if (!err) return null
  const status = (err as { status?: number }).status
  const text = status === 501 ? t('notReady') : status === 502 ? t('aiFail') : String((err as Error).message ?? err)
  return <div className="callout bad" role="alert" style={{ marginTop: 12 }}>{text}</div>
}

export const pct = (x: number) => `${Math.round(x * 100)}%`
export const flagLabel: Record<string, string> = {
  self_declared_skill: 'self-declared skill', novice: 'newcomer', minor_guardian_consent: 'minor with guardian consent',
}
