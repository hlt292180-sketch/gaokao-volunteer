import { useState } from 'react'
import { Link } from 'react-router-dom'
import { checkVolunteer } from '../services/api'
import useAuthStore from '../store/authStore'

export default function VolunteerCheck() {
  const [content, setContent] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const user = useAuthStore((s) => s.user)
  const isPaid = user?.isPaid || user?.isAdmin
  const freeLeft = Math.max(0, 1 - (user?.free_check_count || 0))

  const handleCheck = async () => {
    if (!content.trim()) { setError('请粘贴你的志愿表'); return }
    if (!isPaid && freeLeft <= 0) { setError('免费体检次数已用完'); return }
    setLoading(true); setError('')
    try { const r = await checkVolunteer({ content }); setResult(r.data) } catch (e) { setError(e.message) }
    setLoading(false)
  }

  const icons = { pass: '✅', warn: '⚠️', fail: '❌' }
  const inputStyle = { borderColor: 'var(--color-border)', background: 'var(--color-bg)' }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '8px', color: 'var(--color-primary)' }}>
        🔍 志愿表安全体检
      </h1>
      <p className="mb-2" style={{ color: 'var(--color-muted)' }}>粘贴你的志愿表，检查是否有梯度倒挂、保底不足等问题</p>
      {!isPaid && <p className="text-sm mb-6" style={{ color: 'var(--color-accent)' }}>⚠️ 免费仅显示 1 个问题（剩余 {freeLeft} 次）</p>}
      {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">{error}</div>}
      <div className="card p-6 mb-6">
        <textarea value={content} onChange={(e) => setContent(e.target.value)}
          rows={6} placeholder="每行一个志愿，如：&#10;南京大学 计算机&#10;东南大学 软件工程"
          className="w-full px-3 py-2 border rounded-lg focus:outline-none resize-y"
          style={inputStyle} />
        <button onClick={handleCheck} disabled={loading}
          className="mt-4 w-full py-2 rounded-lg disabled:opacity-50"
          style={{ background: loading ? '#9ca3af' : 'var(--color-primary)', color: 'white', fontWeight: 600 }}>
          {loading ? '检测中...' : '开始体检'}
        </button>
      </div>
      {result && (
        <div className="card p-6">
          <h3 style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', marginBottom: '16px', color: 'var(--color-primary)' }}>
            体检报告
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {result.checks?.map((c, i) => (
              (!result.isPaid && i > 0) ? null : (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '12px', borderRadius: '8px', background: 'var(--color-bg)' }}>
                  <span style={{ fontSize: '1.2rem' }}>{icons[c.status]}</span>
                  <div>
                    <p className="text-sm font-medium">{c.name}</p>
                    <p className="text-xs" style={{ color: 'var(--color-muted)' }}>{c.detail}</p>
                    {c.suggestion && <p className="text-xs mt-1" style={{ color: 'var(--color-primary)' }}>💡 {c.suggestion}</p>}
                  </div>
                </div>
              )
            ))}
          </div>
          {!result.isPaid && result.hiddenCount > 0 && (
            <div className="mt-4 p-4 rounded-lg text-center" style={{ background: 'var(--color-primary)', color: 'white' }}>
              <p className="text-sm font-semibold">还有 {result.hiddenCount} 个问题未显示</p>
              <Link to="/upgrade" className="btn-cta text-sm" style={{ display: 'inline-block', marginTop: '8px' }}>
                升级查看完整报告
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
