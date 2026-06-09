import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPlan } from '../services/api'

const typeColors = { '冲': { bg: '#fef2f2', text: '#dc2626', border: '#fecaca' }, '稳': { bg: '#fefce8', text: '#ca8a04', border: '#fef08a' }, '保': { bg: '#f0fdf4', text: '#16a34a', border: '#bbf7d0' } }

export default function PlanDetail() {
  const { id } = useParams()
  const [plan, setPlan] = useState(null)

  useEffect(() => {
    (async () => { try { const r = await getPlan(id); setPlan(r.data) } catch {} })()
  }, [id])

  if (!plan) return <div className="max-w-4xl mx-auto px-6 py-8 text-center" style={{ color: 'var(--color-muted)' }}>加载中...</div>

  const items = plan.plans_data || []

  return (
    <div className="page-enter max-w-4xl mx-auto px-6 py-8">
      <Link to="/plans" className="text-sm hover:underline" style={{ color: 'var(--color-muted)' }}>← 返回方案列表</Link>
      <div className="card p-6 my-4">
        <h1 className="text-2xl font-bold mb-2">方案 #{plan.id}</h1>
        <div className="flex gap-3 text-sm" style={{ color: 'var(--color-muted)' }}>
          <span>{plan.subject_type}</span> · <span className="font-semibold" style={{ color: 'var(--color-primary)' }}>{plan.score}分</span> · <span>位次{plan.rank?.toLocaleString()}</span> · <span>{plan.strategy_type}</span>
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item, i) => (
          <div key={i} className="card flex items-center gap-4 p-4" style={{ borderLeft: `4px solid ${typeColors[item.type]?.border || '#e5e7eb'}` }}>
            <span className="text-lg font-bold w-8 text-center" style={{ color: 'var(--color-muted)' }}>{i + 1}</span>
            <span className="text-xs px-2 py-1 rounded font-medium" style={{ background: typeColors[item.type]?.bg, color: typeColors[item.type]?.text }}>{item.type}</span>
            <div className="flex-1">
              <p className="font-semibold">{item.universityName}</p>
              <p className="text-xs" style={{ color: 'var(--color-muted)' }}>{item.city}{item.is985 === 1 ? ' · 985' : ''}{item.is211 === 1 ? ' · 211' : ''}{item.isDoubleFirst === 1 ? ' · 双一流' : ''}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold" style={{ color: 'var(--color-primary)' }}>{item.minScore}分</p>
              <p className="text-xs" style={{ color: 'var(--color-muted)' }}>位次{item.minRank?.toLocaleString()}</p>
            </div>
            <div className="text-right">
              <p className="text-xs" style={{ color: 'var(--color-muted)' }}>录取概率</p>
              <p className="text-sm font-semibold" style={{ color: typeColors[item.type]?.text }}>{item.probability}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
