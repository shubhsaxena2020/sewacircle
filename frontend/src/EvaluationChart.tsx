import { Bar, BarChart, Cell, ErrorBar, ResponsiveContainer, XAxis, YAxis } from 'recharts'
import { useUi } from './ui-context'
import type { EvalReport } from './types'
import { evaluationChartRows } from './evaluation-data'

export default function EvaluationChart({ report, metric }: { report: EvalReport; metric: string }) {
  const { t } = useUi()
  const data = evaluationChartRows(report, metric, t)
  return <div className="eval-chart"><ResponsiveContainer width="100%" height={190}>
    <BarChart data={data} layout="vertical" margin={{ top: 4, right: 20, bottom: 4, left: 0 }}>
      <XAxis type="number" domain={[0, 1]} hide/>
      <YAxis type="category" dataKey="name" width={118} tick={{ fill: '#4c5669', fontSize: 11 }} axisLine={false} tickLine={false}/>
      <Bar dataKey="value" barSize={21} radius={[0, 4, 4, 0]} isAnimationActive={false}>
        {data.map((row, index) => <Cell key={row.name} fill={index === 0 ? '#df8559' : '#77a99a'}/>)}
        <ErrorBar dataKey="error" direction="x" stroke="#202444" strokeWidth={1.5} width={7} isAnimationActive={false}/>
      </Bar>
    </BarChart>
  </ResponsiveContainer></div>
}
