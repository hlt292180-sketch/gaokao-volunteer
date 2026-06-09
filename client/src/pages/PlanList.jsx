import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getPlans, deletePlan, deletePlansBatch } from '../services/api'

// 科类标签
const SUBJECT_TABS = [
  { key: '', label: '全部' },
  { key: '物理类', label: '物理类' },
  { key: '历史类', label: '历史类' },
]

// 策略色彩
const strategyStyle = (s) => {
  if (s === '激进') return { bg: '#fef2f2', color: '#dc2626', text: '🔥 激进' }
  if (s === '均衡') return { bg: '#eff6ff', color: '#2563eb', text: '⚖ 均衡' }
  return { bg: '#f0fdf4', color: '#16a34a', text: '🛡 稳健' }
}

export default function PlanList() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // 科类筛选
  const [subjectTab, setSubjectTab] = useState('')

  // 批量选择
  const [selected, setSelected] = useState(new Set())
  const [deleting, setDeleting] = useState(false)

  // 加载
  const loadPlans = async (subjectType = '') => {
    setLoading(true); setError('')
    try {
      const params = subjectType ? { subjectType } : {}
      const r = await getPlans(params)
      setPlans(r.data || [])
      setSelected(new Set())  // 切换标签时清空选择
    } catch (e) { setError('加载失败') }
    setLoading(false)
  }

  useEffect(() => { loadPlans() }, [])

  // 切换科类标签
  const handleTab = (key) => {
    setSubjectTab(key)
    loadPlans(key)
  }

  // 全选/取消
  const toggleAll = () => {
    if (selected.size === plans.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(plans.map((p) => p.id)))
    }
  }

  // 单选
  const toggleOne = (id) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  // 单个删除
  const handleDeleteOne = async (id) => {
    try {
      await deletePlan(id)
      setPlans((prev) => prev.filter((p) => p.id !== id))
      setSelected((prev) => { const n = new Set(prev); n.delete(id); return n })
    } catch (e) { alert('删除失败') }
  }

  // 批量删除
  const handleBatchDelete = async () => {
    if (selected.size === 0) return
    if (!window.confirm(`确定要删除选中的 ${selected.size} 个方案吗？此操作不可恢复。`)) return
    setDeleting(true)
    try {
      await deletePlansBatch([...selected])
      setPlans((prev) => prev.filter((p) => !selected.has(p.id)))
      setSelected(new Set())
    } catch (e) { alert('批量删除失败') }
    setDeleting(false)
  }

  const hasSelection = selected.size > 0

  return (
    <div className="page-enter max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">

      {/* 头部 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(1.3rem, 3vw, 1.7rem)', fontWeight: 'bold', color: 'var(--color-primary)' }}>
          📋 我的方案
        </h1>
        <Link to="/plan/generate" style={{
          background: 'var(--color-accent)', color: 'var(--color-primary)',
          fontWeight: 700, fontSize: '0.9rem', padding: '10px 24px', borderRadius: '8px', textDecoration: 'none',
        }}>
          + 新建方案
        </Link>
      </div>

      {/* 科类标签 + 计数 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
        {SUBJECT_TABS.map((t) => (
          <button key={t.key} onClick={() => handleTab(t.key)}
            style={{
              padding: '5px 16px', fontSize: '0.82rem', fontWeight: 500, borderRadius: '16px',
              border: subjectTab === t.key ? '2px solid var(--color-accent)' : '1px solid var(--color-border)',
              background: subjectTab === t.key ? '#fef3c7' : 'white',
              color: subjectTab === t.key ? 'var(--color-primary)' : 'var(--color-muted)',
              cursor: 'pointer', transition: 'all 0.15s',
            }}>
            {t.label}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: '0.82rem', color: 'var(--color-muted)' }}>
          共 {plans.length} 个
        </span>
      </div>

      {/* 批量操作栏 */}
      {hasSelection && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '14px',
          padding: '10px 16px', marginBottom: '10px',
          background: '#fef3c7', border: '1px solid var(--color-accent)', borderRadius: '8px',
          fontSize: '0.85rem',
        }}>
          <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>
            已选 {selected.size} 个
          </span>
          <button onClick={handleBatchDelete} disabled={deleting}
            style={{
              padding: '5px 16px', fontSize: '0.82rem', fontWeight: 600, borderRadius: '5px',
              border: 'none', background: '#dc2626', color: 'white', cursor: 'pointer',
            }}>
            {deleting ? '删除中...' : '删除选中'}
          </button>
          <button onClick={() => setSelected(new Set())}
            style={{
              padding: '5px 12px', fontSize: '0.8rem', borderRadius: '5px',
              border: '1px solid var(--color-border)', background: 'white', cursor: 'pointer',
            }}>
            取消选择
          </button>
        </div>
      )}

      {/* 错误 */}
      {error && (
        <div style={{ padding: '10px 14px', background: '#fef2f2', color: '#dc2626', borderRadius: '8px', marginBottom: '14px', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      {/* 加载 */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--color-muted)' }}>加载中...</div>
      )}

      {/* 空状态 */}
      {!loading && plans.length === 0 && (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: 'white', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
          <p style={{ fontSize: '2rem', marginBottom: '12px' }}>📭</p>
          <p style={{ color: 'var(--color-muted)', marginBottom: '20px', fontSize: '0.95rem' }}>
            {subjectTab ? `没有${subjectTab}的方案` : '还没有志愿方案'}
          </p>
          <Link to="/plan/generate" style={{
            display: 'inline-block', background: 'var(--color-accent)', color: 'var(--color-primary)',
            fontWeight: 700, padding: '10px 32px', borderRadius: '8px', textDecoration: 'none',
          }}>生成第一份方案</Link>
        </div>
      )}

      {/* 全选行 */}
      {!loading && plans.length > 0 && (
        <label style={{
          display: 'flex', alignItems: 'center', gap: '8px', padding: '0 0 8px 4px',
          fontSize: '0.78rem', color: 'var(--color-muted)', cursor: 'pointer',
        }}>
          <input type="checkbox" checked={selected.size === plans.length} onChange={toggleAll}
            style={{ width: '16px', height: '16px', cursor: 'pointer' }} />
          全选
        </label>
      )}

      {/* 方案列表 */}
      {!loading && plans.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {plans.map((p) => {
            const strategy = p.strategy_type || '稳健'
            const st = strategyStyle(strategy)
            const isSel = selected.has(p.id)
            return (
              <div key={p.id} style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                padding: '12px 14px', background: isSel ? '#fef9e7' : 'white',
                border: isSel ? '2px solid var(--color-accent)' : '1px solid var(--color-border)',
                borderRadius: '10px', transition: 'all 0.1s',
              }}>
                {/* 复选框 */}
                <input type="checkbox" checked={isSel} onChange={() => toggleOne(p.id)}
                  style={{ width: '17px', height: '17px', cursor: 'pointer', flexShrink: 0 }} />

                {/* 方案信息 */}
                <Link to={`/plans/${p.id}`} style={{ flex: 1, textDecoration: 'none', color: 'inherit', minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '3px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-primary)' }}>
                      {p.plan_name || `方案 #${p.id}`}
                    </span>
                    <span style={{
                      fontSize: '0.68rem', padding: '1px 7px', borderRadius: '8px', fontWeight: 600,
                      background: st.bg, color: st.color,
                    }}>
                      {st.text}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>
                      {p.score}分 · 位次{p.rank?.toLocaleString()}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.73rem', color: 'var(--color-muted)', margin: 0 }}>
                    {p.subject_type} · {new Date(p.created_at).toLocaleDateString('zh-CN')}
                  </p>
                </Link>

                {/* 单个删除 */}
                <button onClick={(e) => { e.preventDefault(); handleDeleteOne(p.id) }}
                  title="删除此方案"
                  style={{
                    padding: '4px 8px', fontSize: '0.85rem', borderRadius: '5px', flexShrink: 0,
                    border: 'none', background: 'transparent', color: 'var(--color-muted)',
                    cursor: 'pointer', opacity: 0.5,
                  }}>
                  🗑
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
