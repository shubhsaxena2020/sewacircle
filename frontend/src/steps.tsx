import { useEffect, useMemo, useState } from 'react'
import { api, defaultOptions } from './api'
import { Bar, Btn, Chip, ErrorNote, StatusChip, flagLabel, pct, useT } from './ui'
import type {
  AttendanceRow, ContributionCard, Counterfactual, DropoutResult, EvalReport, ExtractionResult, LedgerEntry, LedgerVerification,
  RoleSpec, RosterBoth, RosterOptions, RosterResult, TaskSpec, Volunteer,
} from './types'

export const DEFAULT_BRIEF =
  'गाँव स्तर पर शनिवार सुबह 9 से 2 बजे तक स्वच्छ पेयजल और हाथ धोने की जागरूकता शिविर। लगभग 120 लोग आएँगे। एक टीम चाहिए जो पोस्टर, प्राथमिक उपचार, सामान और स्थानीय बोली में बात संभाल सके।'

/* ---------------- Step 1: brief ---------------- */
export function BriefStep(p: {
  tasks: TaskSpec[]; siteId: string; setSiteId: (s: string) => void; brief: string; setBrief: (s: string) => void
  onExtracted: (e: ExtractionResult) => void; tasksErr: unknown
}) {
  const t = useT()
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<unknown>(null)
  async function go() {
    setBusy(true); setErr(null)
    try { p.onExtracted(await api.extract(p.brief)) } catch (e) { setErr(e) } finally { setBusy(false) }
  }
  return (
    <div className="panel stack">
      <h2>{t('describeTask')}</h2>
      <div>
        <label className="label" htmlFor="site">{t('chooseSite')}</label>
        <select id="site" value={p.siteId} onChange={(e) => p.setSiteId(e.target.value)}>
          {p.tasks.map((x) => <option key={x.id} value={x.id}>{x.title} · {x.block}, {x.district}</option>)}
        </select>
      </div>
      <div>
        <label className="label" htmlFor="brief">{t('describeTask')}</label>
        <textarea id="brief" rows={6} value={p.brief} onChange={(e) => p.setBrief(e.target.value)} lang="hi" />
        <div className="muted" style={{ marginTop: 6 }}>{t('briefHelp')}</div>
      </div>
      <div className="row"><Btn onClick={go} disabled={busy || !p.brief.trim()}>{busy ? t('extracting') : t('extract')}</Btn></div>
      <ErrorNote err={err ?? p.tasksErr} />
    </div>
  )
}

/* ---------------- Step 2: roles ---------------- */
export function RolesStep(p: {
  extraction: ExtractionResult; roles: RoleSpec[]; setRoles: (r: RoleSpec[]) => void; onNext: () => void; busy: boolean; err: unknown
}) {
  const t = useT()
  const upd = (i: number, patch: Partial<RoleSpec>) => p.setRoles(p.roles.map((r, j) => (j === i ? { ...r, ...patch } : r)))
  return (
    <div className="panel stack">
      <h2>{t('rolesTitle')}</h2>
      <div className="row">
        {p.extraction.redactions > 0 && <Chip kind="info">{p.extraction.redactions} {t('redacted')}</Chip>}
        <Chip kind="draft">{t('draft')}</Chip>
        <span className="muted">model: {p.extraction.model}{p.extraction.cached ? ' (cached)' : ''}</span>
      </div>
      <table>
        <thead><tr><th>{t('role')}</th><th>{t('why')}</th><th>{t('need')}</th><th>{t('confidence')}</th><th /></tr></thead>
        <tbody>
          {p.roles.map((r, i) => (
            <tr key={r.id}>
              <td><input type="text" aria-label={t('role')} value={r.role} onChange={(e) => upd(i, { role: e.target.value })} /></td>
              <td className="muted" lang="hi">{r.evidence_span || r.required_skills.join(', ')}</td>
              <td style={{ width: 90 }}><input type="number" min={1} max={10} aria-label={t('need')} value={r.count} onChange={(e) => upd(i, { count: Math.max(1, Math.min(10, Number(e.target.value) || 1)) })} /></td>
              <td><Chip kind={r.confidence === 'high' ? 'ok' : r.confidence === 'medium' ? 'pending' : 'warn'}>{r.confidence}</Chip></td>
              <td><Btn small variant="secondary" aria-label="remove" onClick={() => p.setRoles(p.roles.filter((_, j) => j !== i))}>✕</Btn></td>
            </tr>
          ))}
        </tbody>
      </table>
      {p.extraction.needs_decision.length > 0 && (
        <div className="callout">
          <strong>{t('needsDecision')}</strong>
          <ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>{p.extraction.needs_decision.map((d, i) => <li key={i}>{d}</li>)}</ul>
        </div>
      )}
      <div className="row">
        <Btn variant="secondary" onClick={() => p.setRoles([...p.roles, { id: `r${Date.now() % 100000}`, role: '', count: 1, required_skills: [], min_level: 1, priority: 'must', needs_experienced: false, evidence_span: '', confidence: 'high' }])}>{t('addRole')}</Btn>
        <Btn onClick={p.onNext} disabled={p.busy || p.roles.length === 0}>{p.busy ? t('building') : t('buildRoster')}</Btn>
      </div>
      <ErrorNote err={p.err} />
    </div>
  )
}

/* ---------------- Step 3: roster ---------------- */
export function RosterStep(p: {
  task: TaskSpec; both: RosterBoth | null; roster: RosterResult | null; setRoster: (r: RosterResult) => void
  options: RosterOptions; setOptions: (o: RosterOptions) => void; rerun: () => void; busy: boolean; err: unknown
  volunteers: Volunteer[]; onApprove: () => void
}) {
  const t = useT()
  const [dropout, setDropout] = useState<DropoutResult | null>(null)
  const [why, setWhy] = useState(false)
  const [whyId, setWhyId] = useState('')
  const [cf, setCf] = useState<Counterfactual | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const roleName = useMemo(() => Object.fromEntries(p.task.roles.map((r) => [r.id, r.role])), [p.task.roles])
  const base = p.both?.nearest_skill
  const cp = p.roster
  if (!cp || !p.both) return <div className="panel"><ErrorNote err={p.err} />{p.busy && <p>{t('building')}</p>}</div>

  async function doDropout(vid: string) {
    setErr(null)
    try { const r = await api.dropout(p.task, cp!, vid, p.options); setDropout(r); p.setRoster(r.roster_after) } catch (e) { setErr(e) }
  }
  async function doWhy() {
    setErr(null); setCf(null)
    try { setCf(await api.whyNot(p.task, cp!, whyId, p.options)) } catch (e) { setErr(e) }
  }
  const m = cp.metrics, bm = base?.metrics
  const assignedIds = new Set(cp.assignments.map((a) => a.volunteer_id))
  const candidates = p.volunteers.filter((v) => !assignedIds.has(v.id))
  return (
    <div className="stack">
      <div className="panel">
        <div className="row between">
          <h2>{p.task.title}</h2>
          <div className="row">
            <span className="label">{t('options')}</span>
            {([['opted_in_only', 'optInOnly'], ['fairness', 'optFair'], ['resilience', 'optRes'], ['mentor_pairing', 'optMentor']] as const).map(([k, lab]) => (
              <label key={k} className="row" style={{ gap: 6 }}>
                <input type="checkbox" checked={p.options[k]} onChange={(e) => p.setOptions({ ...p.options, [k]: e.target.checked })} />{t(lab)}
              </label>
            ))}
            <Btn small variant="secondary" onClick={p.rerun} disabled={p.busy}>{p.busy ? t('building') : '↻'}</Btn>
          </div>
        </div>
      </div>
      <ReadyPanel roster={cp} />
      {dropout && (
        <div className={`callout ${dropout.uncovered_role_ids.length ? 'bad' : 'good'} heal`} role="status">
          <strong>{dropout.uncovered_role_ids.length ? t('notHealed') : t('healed')}.</strong>{' '}
          {dropout.healed_with_standby && dropout.replacement_volunteer_id && <>→ {p.volunteers.find((v) => v.id === dropout.replacement_volunteer_id)?.display_name ?? dropout.replacement_volunteer_id}</>}
          {dropout.uncovered_role_ids.length > 0 && <> {t('unfilled')}: {dropout.uncovered_role_ids.map((r) => roleName[r] ?? r).join(', ')}</>}
        </div>
      )}
      {cp.unfilled_role_ids.length > 0 && <div className="callout bad" role="alert"><strong>{t('unfilled')}:</strong> {cp.unfilled_role_ids.map((r) => roleName[r] ?? r).join(', ')}</div>}
      <div className="cols">
        <div className="panel">
          <table>
            <thead><tr><th>{t('role')}</th><th>{t('volunteer')}</th><th>{t('reason')}</th><th>{t('distance')}</th><th>{t('actions')}</th></tr></thead>
            <tbody>
              {cp.assignments.map((a, i) => (
                <tr key={`${a.role_id}-${a.slot_index}-${i}`}>
                  <td><strong>{roleName[a.role_id] ?? a.role_id}</strong></td>
                  <td>{a.volunteer_name}</td>
                  <td>
                    <ul style={{ margin: 0, paddingLeft: 16 }}>{a.reasons.map((r, j) => <li key={j}>{r}</li>)}</ul>
                    {a.flags.map((f) => <Chip key={f} kind={f === 'self_declared_skill' ? 'pending' : 'info'}>{flagLabel[f] ?? f}</Chip>)}
                  </td>
                  <td>{a.distance_km.toFixed(0)} km</td>
                  <td><Btn small variant="secondary" onClick={() => doDropout(a.volunteer_id)}>{t('dropOut')}</Btn></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="muted" style={{ marginTop: 8 }}>{t('flagsExplain')}</div>
          {cp.standby.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <span className="label">{t('standby')}</span>
              {cp.standby.map((s) => <div key={s.volunteer_id}><strong>{s.volunteer_name}</strong> <span className="muted">· {s.reason}</span></div>)}
            </div>
          )}
          <div className="row" style={{ marginTop: 16 }}>
            <Btn variant="secondary" onClick={() => setWhy(true)}>{t('whyNot')}</Btn>
            <Btn onClick={p.onApprove}>{t('approve')}</Btn>
          </div>
          <ErrorNote err={err ?? p.err} />
        </div>
        <div className="stack">
          <div className="panel">
            <h3>{t('vsBaseline')}</h3>
            <div style={{ marginTop: 12 }}>
              <div className="label">{t('coverage')}</div>
              <div className="muted">SewaCircle</div><Bar value={m.role_coverage} kind="good" />
              <div className="muted">{m.slots_filled} / {m.slots_required} {t('rolesCovered')}</div>
              {bm && <><div className="muted" style={{ marginTop: 8 }}>Nearest-skill</div><Bar value={bm.role_coverage} kind="base" /><div className="muted">{bm.slots_filled} / {bm.slots_required} {t('rolesCovered')}</div></>}
            </div>
            <div style={{ marginTop: 14 }}>
              <div className="label">{t('robustness')}</div>
              <div className="muted">SewaCircle</div><Bar value={m.robustness} kind="good" /><div className="muted">{pct(m.robustness)}</div>
              {bm && <><div className="muted" style={{ marginTop: 8 }}>Nearest-skill</div><Bar value={bm.robustness} kind="base" /><div className="muted">{pct(bm.robustness)}</div></>}
            </div>
            <div className="muted" style={{ marginTop: 10, fontSize: '0.85em' }}>solver: {m.solver_status} · {m.solve_ms} ms</div>
          </div>
          <div className="panel">
            <h3>{t('fairness')}</h3>
            {([
              ['repeatPick', pct(m.repeat_pick_share), bm ? pct(bm.repeat_pick_share) : ''],
              ['gini', m.exposure_gini.toFixed(2), bm ? bm.exposure_gini.toFixed(2) : ''],
              ['districts', String(m.district_spread), bm ? String(bm.district_spread) : ''],
              ['novices', String(m.novices), bm ? String(bm.novices) : ''],
              ['mentors', String(m.mentor_pairs), bm ? String(bm.mentor_pairs) : ''],
            ] as const).map(([k, a, b]) => (
              <div className="metric" key={k}><span>{t(k)}</span><span><strong>{a}</strong>{b && <span className="muted"> · {b}</span>}</span></div>
            ))}
            <div className="muted" style={{ marginTop: 6, fontSize: '0.85em' }}>SewaCircle · nearest-skill</div>
          </div>
        </div>
      </div>
      {why && (
        <aside className="drawer" aria-label={t('whyNot')}>
          <div className="row between"><h3>{t('whyNot')}</h3><Btn small variant="secondary" onClick={() => { setWhy(false); setCf(null) }}>{t('close')}</Btn></div>
          <div className="stack" style={{ marginTop: 16 }}>
            <label className="label" htmlFor="wn">{t('forceIn')}</label>
            <select id="wn" value={whyId} onChange={(e) => setWhyId(e.target.value)}>
              <option value="">—</option>
              {candidates.map((v) => <option key={v.id} value={v.id}>{v.display_name} · {v.block}</option>)}
            </select>
            <Btn onClick={doWhy} disabled={!whyId}>{t('ask')}</Btn>
            {cf && (
              <div className="callout">
                <p style={{ margin: 0 }}>{cf.narrative}</p>
                <p className="muted" style={{ margin: '8px 0 0' }}>Δ coverage {pct(cf.delta_role_coverage)} · Δ robustness {pct(cf.delta_robustness)}</p>
                {cf.blocking_reasons.length > 0 && <ul>{cf.blocking_reasons.map((b, i) => <li key={i}>{b}</li>)}</ul>}
              </div>
            )}
            <ErrorNote err={err} />
          </div>
        </aside>
      )}
    </div>
  )
}

/* ---------------- Ready Crew verdict ---------------- */
function ReadyPanel({ roster }: { roster: RosterResult }) {
  const t = useT()
  const reqs = roster.recruit_requests ?? []
  if (roster.ready == null) return null
  if (roster.ready) {
    return (
      <div className="callout good" role="status" style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
        <span style={{ fontSize: '1.6em', fontWeight: 600 }}>✓ {t('ready')}</span><span>{t('readyExplain')}</span>
      </div>
    )
  }
  const text = (r: NonNullable<RosterResult['recruit_requests']>[number]) =>
    `${t('recruit')} ${r.needed} × ${r.role}${r.skills.length ? ` (${r.skills.join(' / ')}${r.checked_skill_required ? `, ${t('checkedOnly')}` : ''})` : ''} · ${r.slot.replace('_', ' ')} · ${r.area} · ≤ ${r.max_travel_km.toFixed(0)} km`
  return (
    <div className="panel" role="alert" style={{ borderColor: 'var(--coral)', borderWidth: 2 }}>
      <div className="row" style={{ gap: 16 }}>
        <span style={{ fontSize: '1.6em', fontWeight: 600, color: 'var(--coral)' }}>! {t('notReadyV')}</span>
        <span className="muted">{t('notReadyExplain')}</span>
      </div>
      <ol style={{ margin: '12px 0 0', paddingLeft: 20 }}>
        {reqs.map((r, i) => (
          <li key={i} style={{ marginBottom: 10 }}>
            <strong>{text(r)}</strong>
            <div className="muted">{r.reason}</div>
            <Btn small variant="secondary" onClick={() => navigator.clipboard?.writeText(text(r) + ' — ' + r.reason)}>{t('copyRequest')}</Btn>
          </li>
        ))}
      </ol>
    </div>
  )
}

/* ---------------- Step 4: evidence ---------------- */
export function EvidenceStep(p: { task: TaskSpec; roster: RosterResult; roleName: Record<string, string>; onChanged: () => void }) {
  const t = useT()
  const demoClaimIdx = p.roster.assignments.length - 1
  const initNotes = p.roster.assignments.map((a, i) => `${a.volunteer_name} (${p.roleName[a.role_id] ?? a.role_id}) worked about ${i === demoClaimIdx ? 8 : 5} hours.`).join('\n')
  const [notes, setNotes] = useState(initNotes)
  const [hours, setHours] = useState<Record<string, number>>(Object.fromEntries(p.roster.assignments.map((a) => [a.volunteer_id, 5])))
  const [cards, setCards] = useState<ContributionCard[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<unknown>(null)
  const [fix, setFix] = useState<Record<string, number>>({})
  async function draft() {
    setBusy(true); setErr(null)
    try {
      const rows: AttendanceRow[] = p.roster.assignments.map((a) => ({ volunteer_id: a.volunteer_id, task_id: p.task.id, hours: hours[a.volunteer_id] ?? 0 }))
      setCards(await api.draft(p.task, notes, rows, p.roster.assignments)); p.onChanged()
    } catch (e) { setErr(e) } finally { setBusy(false) }
  }
  async function decide(id: string, action: 'confirm' | 'correct' | 'reject') {
    setErr(null)
    try {
      const card = cards.find((x) => x.id === id)
      const shown = fix[id] ?? card?.recorded_hours ?? card?.claimed_hours
      const c = await api.decide(id, action, action === 'correct' ? shown : undefined)
      setCards((cs) => cs.map((x) => (x.id === id ? c : x))); p.onChanged()
    } catch (e) { setErr(e) }
  }
  return (
    <div className="stack">
      <div className="panel stack">
        <h2>{t('hostNotes')}</h2>
        <div className="callout">{t('aiNever')} <span className="muted">(Demo scenario: the last claim is deliberately inflated to show the rule check.)</span></div>
        <textarea rows={5} value={notes} onChange={(e) => setNotes(e.target.value)} aria-label={t('hostNotes')} />
        <div className="label">{t('attendance')}</div>
        <div className="row">
          {p.roster.assignments.map((a) => (
            <label key={a.volunteer_id} style={{ width: 130 }}>
              <span className="muted">{a.volunteer_name}</span>
              <input type="number" min={0} max={24} step={0.5} value={hours[a.volunteer_id] ?? 0} onChange={(e) => setHours({ ...hours, [a.volunteer_id]: Number(e.target.value) })} />
            </label>
          ))}
        </div>
        <div className="row"><Btn onClick={draft} disabled={busy}>{busy ? t('extracting') : t('draftCards')}</Btn></div>
        <ErrorNote err={err} />
      </div>
      {cards.map((c) => (
        <div className="panel" key={c.id}>
          <div className="row between">
            <strong>{p.roster.assignments.find((a) => a.volunteer_id === c.volunteer_id)?.volunteer_name ?? c.volunteer_id} · {c.role}</strong>
            <StatusChip status={c.status} />
          </div>
          <p className="muted">{c.summary}</p>
          <div className="row">
            <span>{t('claimed')}: <strong>{c.claimed_hours} {t('hours')}</strong></span>
            <span>{t('recorded')}: <strong>{c.recorded_hours ?? '—'} {t('hours')}</strong></span>
          </div>
          {c.flags.map((f, i) => <div key={i} style={{ marginTop: 6 }}><Chip kind={f.severity === 'info' ? 'info' : 'warn'}>{f.code}</Chip> <span>{f.message}</span></div>)}
          {(c.status === 'draft' || c.status === 'flagged') && (
            <div className="row" style={{ marginTop: 12 }}>
              <Btn small onClick={() => decide(c.id, 'confirm')}>{t('confirm')}</Btn>
              <input type="number" style={{ width: 90 }} aria-label={t('correct')} min={0} max={24} step={0.5} value={fix[c.id] ?? c.recorded_hours ?? c.claimed_hours} onChange={(e) => setFix({ ...fix, [c.id]: Number(e.target.value) })} />
              <Btn small variant="secondary" onClick={() => decide(c.id, 'correct')}>{t('correct')}</Btn>
              <Btn small variant="secondary" onClick={() => decide(c.id, 'reject')}>{t('reject')}</Btn>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

/* ---------------- Step 5: ledger and export ---------------- */
export function LedgerStep({ refreshKey }: { refreshKey: number }) {
  const t = useT()
  const [entries, setEntries] = useState<LedgerEntry[]>([])
  const [ver, setVer] = useState<LedgerVerification | null>(null)
  const [cards, setCards] = useState<ContributionCard[]>([])
  const [cred, setCred] = useState<Record<string, unknown> | null>(null)
  const [err, setErr] = useState<unknown>(null)
  useEffect(() => {
    let live = true
    Promise.all([api.ledger(), api.cards()]).then(([l, c]) => { if (live) { setEntries(l); setCards(c) } }).catch((e) => live && setErr(e))
    return () => { live = false }
  }, [refreshKey])
  async function verify() { setErr(null); try { setVer(await api.verify()) } catch (e) { setErr(e) } }
  async function exportCred(id: string) { setErr(null); try { setCred(await api.credential(id)) } catch (e) { setErr(e) } }
  return (
    <div className="stack">
      <div className="panel stack">
        <div className="row between"><h2>{t('ledger')}</h2><Btn variant="secondary" onClick={verify}>{t('verify')}</Btn></div>
        <div className="muted">{t('ledgerNote')}</div>
        {ver && <div className={`callout ${ver.ok ? 'good' : 'bad'}`} role="status">{ver.ok ? '✓' : '!'} {ver.entries} entries{ver.ok ? '' : ` · first bad index ${ver.first_bad_index}`}</div>}
        <table>
          <thead><tr><th>#</th><th>action</th><th>card</th><th>actor</th><th>hash</th></tr></thead>
          <tbody>{entries.map((e) => <tr key={e.index}><td>{e.index}</td><td>{e.action}</td><td>{e.card_id}</td><td>{e.actor}</td><td className="muted">{e.entry_hash.slice(0, 10)}…</td></tr>)}</tbody>
        </table>
      </div>
      <div className="panel stack">
        <h3>{t('export')}</h3>
        <div className="row">
          {cards.filter((c) => c.status === 'confirmed' || c.status === 'corrected').map((c) => <Btn key={c.id} small variant="secondary" onClick={() => exportCred(c.id)}>{c.id} · {c.role}</Btn>)}
        </div>
        {cred && <><Chip kind="warn">{t('unsigned')}</Chip><pre className="mono">{JSON.stringify(cred, null, 2)}</pre></>}
        <ErrorNote err={err} />
      </div>
    </div>
  )
}

/* ---------------- Evaluation ---------------- */
export function EvalStep() {
  const t = useT()
  const [rep, setRep] = useState<EvalReport | null>(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<unknown>(null)
  async function run() { setBusy(true); setErr(null); try { setRep(await api.evalReport()) } catch (e) { setErr(e) } finally { setBusy(false) } }
  const metrics = ['ready', 'role_coverage', 'robustness', 'repeat_pick_share', 'exposure_gini'] as const
  return (
    <div className="panel stack">
      <div className="row between"><h2>{t('step6')}</h2><Btn onClick={run} disabled={busy}>{busy ? t('building') : t('runEval')}</Btn></div>
      <ErrorNote err={err} />
      {rep && (
        <>
          <div className="muted">{rep.n_tasks} tasks · {rep.n_volunteers} synthetic volunteers · {rep.generated_by}</div>
          <table>
            <thead><tr><th>method</th>{metrics.map((m) => <th key={m}>{m}</th>)}</tr></thead>
            <tbody>
              {Object.entries(rep.summary).map(([method, vals]) => (
                <tr key={method}><td><strong>{method}</strong></td>
                  {metrics.map((m) => {
                    const ci = rep.ci95?.[method]?.[m]
                    return <td key={m}>{vals[m]?.toFixed(2)}{ci ? <span className="muted"> [{ci[0].toFixed(2)}, {ci[1].toFixed(2)}]</span> : ''}</td>
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="callout"><strong>{t('misses')}</strong><ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>{rep.misses.length ? rep.misses.map((x, i) => <li key={i}>{x}</li>) : <li>none</li>}</ul></div>
          <div className="muted">Reproduce: <code>python -m eval.harness --out eval_report.json</code> (from backend/)</div>
        </>
      )}
    </div>
  )
}

export { defaultOptions }
