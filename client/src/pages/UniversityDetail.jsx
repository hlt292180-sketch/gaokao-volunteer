import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getUniversity } from '../services/api'

export default function UniversityDetail() {
  const { id } = useParams()
  const [uni, setUni] = useState(null)

  useEffect(() => {
    (async () => { try { const r = await getUniversity(id); setUni(r.data) } catch {} })()
  }, [id])

  if (!uni) return <div className="max-w-4xl mx-auto px-4 py-8 text-center" style={{ color: 'var(--color-muted)' }}>加载中...</div>

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to="/universities" className="text-sm mb-4 inline-block" style={{ color: 'var(--color-primary)', fontWeight: 500 }}>
        ← 返回院校列表
      </Link>
      <div className="card p-6 mb-6">
        <div className="flex justify-between flex-wrap gap-2">
          <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--color-primary)' }}>
            {uni.name}
          </h1>
          <div className="flex gap-1">
            {uni.is_985 === 1 && <span className="text-xs px-2 py-0.5 rounded" style={{ background: '#fef3c7', color: '#b45309' }}>985</span>}
            {uni.is_211 === 1 && <span className="text-xs px-2 py-0.5 rounded" style={{ background: '#dbeafe', color: 'var(--color-primary)' }}>211</span>}
            {uni.is_double_first_class === 1 && <span className="text-xs px-2 py-0.5 rounded" style={{ background: '#dcfce7', color: '#166534' }}>双一流</span>}
          </div>
        </div>
        <p className="mt-2 text-sm" style={{ color: 'var(--color-muted)' }}>{uni.city} · {uni.type} · {uni.level}</p>
        <p className="mt-4" style={{ color: 'var(--color-text)' }}>{uni.intro}</p>
      </div>
      <div className="card p-6">
        <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '16px', color: 'var(--color-primary)' }}>
          📈 历年录取分数线（江苏 物理类 本科批）
        </h2>
        {uni.admissionScores?.length > 0 ? (
          <table className="w-full text-sm">
            <thead><tr style={{ borderBottom: '1px solid var(--color-border)' }}><th className="text-left py-2">年份</th><th className="text-right py-2">最低分</th><th className="text-right py-2">最低位次</th><th className="text-right py-2">招生人数</th></tr></thead>
            <tbody>
              {uni.admissionScores.map((s, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td className="py-2">{s.year}</td>
                  <td className="py-2 text-right font-semibold" style={{ color: 'var(--color-primary)' }}>{s.min_score}</td>
                  <td className="py-2 text-right">{s.min_rank?.toLocaleString()}</td>
                  <td className="py-2 text-right">{s.plan_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p style={{ color: 'var(--color-muted)' }}>暂无数据</p>}
      </div>
    </div>
  )
}
