import type { EvalReport } from './types'
import type { Key } from './i18n'

const methods = [
  ['cp_sat', 'methodCp'], ['nearest_skill', 'methodNear'],
  ['manual_greedy', 'methodManual'], ['random_feasible', 'methodRandom'],
] as const

export function evaluationChartRows(report: EvalReport, metric: string, t: (key: Key) => string) {
  return methods.map(([key, label]) => {
    const value = report.summary[key]?.[metric] ?? 0
    const [low, high] = report.ci95[key]?.[metric] ?? [value, value]
    return { name: t(label), value, error: [Math.max(0, value - low), Math.max(0, high - value)] }
  })
}
