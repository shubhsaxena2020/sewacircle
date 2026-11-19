import { describe, expect, it } from 'vitest'
import { evaluationChartRows } from './evaluation-data'
import type { EvalReport } from './types'

describe('evaluation confidence intervals', () => {
  it('uses asymmetric distances from the API bounds', () => {
    const report = {
      summary: { cp_sat: { ready: .7 } },
      ci95: { cp_sat: { ready: [.55, .8] } },
    } as unknown as EvalReport
    const [row] = evaluationChartRows(report, 'ready', key => key)
    expect(row.value).toBe(.7)
    expect(row.error[0]).toBeCloseTo(.15)
    expect(row.error[1]).toBeCloseTo(.1)
  })
})
