import { useState } from 'react'
import { Link } from 'react-router-dom'
import { convertScore } from '../services/api'
import { track } from '../services/track'

export default function ScoreConvert() {
  const [year, setYear] = useState('2025')
  const [score, setScore] = useState('')
  const [targetYear, setTargetYear] = useState('2024')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleConvert = async (e) => {
    e.preventDefault(); setError(''); setResult(null)
    if (!score) { setError('请输入高考分数'); return }
    setLoading(true)
    try {
      const res = await convertScore({ provinceId: 1, year, score, subjectType: '物理类', targetYear })
      setResult(res.data)
      track('score_input', { score: Number(score) })
    } catch (err) { setError(err.message) }
    setLoading(false)
  }

  const inputStyle = { borderColor: 'var(--color-border)', background: 'var(--color-bg)' }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '8px', color: 'var(--color-primary)' }}>
        📊 分数位次换算
      </h1>
      <p className="mb-6" style={{ color: 'var(--color-muted)' }}>
        高考录取的核心是<strong style={{ color: 'var(--color-primary)' }}>位次</strong>而非分数。输入今年分数，换算历年等效分。
      </p>
      <form onSubmit={handleConvert} className="card p-6 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-muted)' }}>当前年份</label>
            <select value={year} onChange={(e) => setYear(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none" style={inputStyle}>
              <option value="2025">2025年</option><option value="2024">2024年</option><option value="2023">2023年</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-muted)' }}>你的分数</label>
            <input type="number" value={score} onChange={(e) => setScore(e.target.value)}
              placeholder="如 620" min="0" max="750"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none" style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-muted)' }}>目标年份</label>
            <select value={targetYear} onChange={(e) => setTargetYear(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none" style={inputStyle}>
              <option value="2024">2024年</option><option value="2023">2023年</option><option value="2025">2025年</option>
            </select>
          </div>
          <div className="flex items-end">
            <button type="submit" disabled={loading}
              className="w-full py-2 rounded-lg disabled:opacity-50"
              style={{ background: loading ? '#9ca3af' : 'var(--color-primary)', color: 'white', fontWeight: 600 }}>
              {loading ? '换算中...' : '开始换算'}
            </button>
          </div>
        </div>
        {error && <p className="mt-2 text-red-500 text-sm">{error}</p>}
      </form>

      {result && (
        <div className="card p-6">
          <h3 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '16px', color: 'var(--color-primary)' }}>
            换算结果
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-lg text-center" style={{ background: 'var(--color-bg)' }}>
              <p className="text-sm" style={{ color: 'var(--color-muted)' }}>{result.currentYear}年 高考分数</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--color-primary)', fontFamily: 'Georgia, serif' }}>{result.currentScore} 分</p>
            </div>
            <div className="p-4 rounded-lg text-center" style={{ background: '#f0fdf4' }}>
              <p className="text-sm" style={{ color: 'var(--color-muted)' }}>全省位次</p>
              <p className="text-3xl font-bold" style={{ color: '#16a34a', fontFamily: 'Georgia, serif' }}>
                第 {result.rank?.toLocaleString()} 名
              </p>
            </div>
            <div className="p-4 rounded-lg text-center col-span-2" style={{ background: '#f5f3ff' }}>
              <p className="text-sm" style={{ color: 'var(--color-muted)' }}>{result.targetYear}年 等效分数</p>
              <p className="text-3xl font-bold" style={{ color: '#7c3aed', fontFamily: 'Georgia, serif' }}>
                {result.equivalentScore ? `${result.equivalentScore} 分` : '暂无数据'}
              </p>
            </div>
          </div>
          <div className="mt-4 p-4 rounded-lg text-sm" style={{ background: 'var(--color-bg)', color: 'var(--color-text)' }}>
            💡 <strong>下一步：</strong>记住位次（第 {result.rank?.toLocaleString()} 名），去「院校查询」对比近3年录取位次。
            <Link to="/universities" style={{ color: 'var(--color-primary)', fontWeight: 500, marginLeft: '8px' }}>去查院校 →</Link>
          </div>
        </div>
      )}
    </div>
  )
}
