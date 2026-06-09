import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import api, { getAnalyticsStats, getPendingPayments, approvePayment, getFunnel } from '../services/api'

// ===== 指标卡片配置 =====
const metricDefs = [
  { key: 'visitors', label: '访问人数', icon: '👁', desc: '最近7天打开首页的用户' },
  { key: 'scoreInputUsers', label: '输入分数', icon: '📊', desc: '使用分数换算功能' },
  { key: 'planUsers', label: '生成方案', icon: '🤖', desc: '成功生成志愿方案' },
  { key: 'payClickUsers', label: '点击付款', icon: '💰', desc: '点击了"我已付款"' },
  { key: 'payConfirmUsers', label: '确认付款', icon: '✅', desc: '付款确认提交成功' },
]

export default function Admin() {
  const user = useAuthStore((s) => s.user)
  const isAdmin = user?.isAdmin

  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dbMsg, setDbMsg] = useState('')

  // 💰 支付订单管理
  const [payments, setPayments] = useState([])
  const [payLoading, setPayLoading] = useState(true)
  const [approving, setApproving] = useState(null)

  // 📊 转化漏斗
  const [funnel, setFunnel] = useState(null)

  // 📊 数据质量仪表盘
  const [dataQuality, setDataQuality] = useState(null)
  const [dqLoading, setDqLoading] = useState(true)

  // 📊 加载统计数据 + 支付订单 + 漏斗
  useEffect(() => {
    if (!isAdmin) return
    ;(async () => {
      try {
        const [statsRes, payRes, funnelRes, dqRes] = await Promise.all([
          getAnalyticsStats({ days: 7 }),
          getPendingPayments().catch(() => ({ data: [] })),
          getFunnel({ days: 30 }).catch(() => ({ data: null })),
          api.get('/analytics/data-quality').catch(() => ({ data: null })),
        ])
        setStats(statsRes.data)
        setPayments(payRes.data || [])
        if (funnelRes.data) setFunnel(funnelRes.data.funnel)
        if (dqRes.data?.success) setDataQuality(dqRes.data.data)
      } catch (err) {
        setError('数据加载失败：' + err.message)
      }
      setLoading(false)
      setPayLoading(false)
      setDqLoading(false)
    })()
  }, [isAdmin])

  // 💰 审核通过一笔支付
  const handleApprove = async (orderNo) => {
    setApproving(orderNo)
    try {
      await approvePayment(orderNo)
      // 从列表中移除已审核的订单
      setPayments((prev) => prev.filter((p) => p.order_no !== orderNo))
    } catch (err) {
      alert('审核失败：' + err.message)
    }
    setApproving(null)
  }

  if (!isAdmin) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20 text-center">
        <h1 className="text-3xl font-bold mb-4">🚫 无权访问</h1>
        <p style={{ color: 'var(--color-muted)' }}>此页面仅限管理员</p>
      </div>
    )
  }

  const handleCheckDb = async () => {
    try {
      const r = await api.get('/provinces/')
      setDbMsg(`✅ 数据库连接正常。省份：${r.data[0]?.name || '无数据'}`)
    } catch (e) {
      setDbMsg(`❌ 连接失败：${e.message}`)
    }
  }

  const metrics = stats?.metrics || {}
  const conversion = stats?.conversion || {}
  const daily = stats?.daily || {}

  return (
    <div className="page-enter" style={{
      maxWidth: '720px',
      margin: '0 auto',
      padding: 'clamp(20px, 4vw, 40px) 16px',
    }}>
      <h1 style={{
        fontFamily: 'Georgia, serif',
        fontSize: 'clamp(1.5rem, 4vw, 1.8rem)',
        fontWeight: 'bold',
        color: 'var(--color-primary)',
        marginBottom: '4px',
      }}>
        📊 数据统计
      </h1>
      <p style={{ color: 'var(--color-muted)', fontSize: '0.85rem', marginBottom: '28px' }}>
        {stats?.period || '最近 7 天'} · 管理员 {user?.phone}
      </p>

      {/* ===== 核心指标卡片 ===== */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
        gap: '12px',
        marginBottom: '24px',
      }}>
        {metricDefs.map((m) => (
          <div key={m.key} style={{
            background: 'white',
            border: '1px solid var(--color-border)',
            borderRadius: '10px',
            padding: 'clamp(14px, 2vw, 20px)',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
          }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '6px' }}>{m.icon}</div>
            <p style={{
              fontFamily: 'Georgia, serif',
              fontSize: 'clamp(1.3rem, 3vw, 1.6rem)',
              fontWeight: 'bold',
              color: 'var(--color-primary)',
              marginBottom: '2px',
            }}>
              {loading ? '--' : (metrics[m.key] ?? 0)}
            </p>
            <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '2px' }}>
              {m.label}
            </p>
            <p style={{ fontSize: '0.65rem', color: 'var(--color-muted)', opacity: 0.7 }}>
              {m.desc}
            </p>
          </div>
        ))}
      </div>

      {/* ===== 转化率漏斗 ===== */}
      <div style={{
        background: 'white',
        border: '1px solid var(--color-border)',
        borderRadius: '12px',
        padding: 'clamp(16px, 3vw, 24px)',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <h3 style={{
          fontFamily: 'Georgia, serif',
          fontSize: '1.05rem',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '16px',
        }}>
          转化漏斗
        </h3>

        {/* 漏斗条 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[
            { label: '访问 → 输入分数', value: conversion.visitToScore, width: '100%' },
            { label: '输入分数 → 生成方案', value: conversion.scoreToPlan, width: '75%' },
            { label: '生成方案 → 点击付款', value: conversion.planToPayClick, width: '50%' },
            { label: '点击付款 → 确认付款', value: conversion.payClickToConfirm, width: '35%' },
          ].map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{
                fontSize: '0.78rem',
                color: 'var(--color-muted)',
                minWidth: '140px',
                textAlign: 'right',
                flexShrink: 0,
              }}>
                {item.label}
              </span>
              <div style={{
                flex: 1,
                height: '24px',
                background: 'var(--color-bg)',
                borderRadius: '4px',
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: item.value || '0%',
                  background: `hsl(${220 - i * 30}, 60%, ${45 + i * 8}%)`,
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  paddingRight: '8px',
                  transition: 'width 0.5s ease',
                }}>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    color: 'white',
                  }}>
                    {item.value || '0%'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 总转化率 */}
        <div style={{
          marginTop: '16px',
          paddingTop: '14px',
          borderTop: '1px solid var(--color-border)',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.85rem',
        }}>
          <span style={{ color: 'var(--color-muted)' }}>访问 → 付款（总转化率）</span>
          <span style={{
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
            color: 'var(--color-primary)',
            fontSize: '1.05rem',
          }}>
            {loading ? '--' : (conversion.visitToPay || '0%')}
          </span>
        </div>
      </div>

      {/* ===== 每日趋势 ===== */}
      {Object.keys(daily).length > 0 && (
        <div style={{
          background: 'white',
          border: '1px solid var(--color-border)',
          borderRadius: '12px',
          padding: 'clamp(16px, 3vw, 24px)',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}>
          <h3 style={{
            fontFamily: 'Georgia, serif',
            fontSize: '1.05rem',
            fontWeight: 'bold',
            color: 'var(--color-primary)',
            marginBottom: '16px',
          }}>
            每日事件数
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <th style={{ textAlign: 'left', padding: '6px 8px', color: 'var(--color-muted)', fontWeight: 500 }}>日期</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: 'var(--color-muted)', fontWeight: 500 }}>访问</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: 'var(--color-muted)', fontWeight: 500 }}>输入分数</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: 'var(--color-muted)', fontWeight: 500 }}>生成方案</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: 'var(--color-muted)', fontWeight: 500 }}>付款</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(daily).map(([dt, events]) => (
                  <tr key={dt} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '6px 8px', fontWeight: 500 }}>{dt}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{events.page_view || 0}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{events.score_input || 0}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{events.plan_generate || 0}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px', fontWeight: 600, color: 'var(--color-primary)' }}>
                      {(events.pay_click || 0) + (events.pay_confirm || 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ===== 加载 / 错误状态 ===== */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-muted)', fontSize: '0.9rem' }}>
          加载统计数据中...
        </div>
      )}
      {error && !loading && (
        <div style={{
          background: '#fef2f2',
          color: '#dc2626',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '0.85rem',
          marginBottom: '24px',
        }}>
          {error}
        </div>
      )}

      {/* ===== 转化漏斗 ===== */}
      {funnel && funnel.length > 0 && (
        <div style={{
          background: 'white', border: '1px solid var(--color-border)',
          borderRadius: '12px', padding: 'clamp(16px, 3vw, 24px)',
          marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}>
          <h3 style={{ fontFamily: 'Georgia, serif', fontSize: '1.05rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '16px' }}>
            📊 转化漏斗
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {funnel.map((step, i) => {
              const maxCount = funnel[0]?.count || 1
              const width = Math.max(2, (step.count / maxCount) * 100)
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--color-muted)', minWidth: '80px', textAlign: 'right', flexShrink: 0 }}>
                    {step.step}
                  </span>
                  <div style={{ flex: 1, height: '28px', background: 'var(--color-bg)', borderRadius: '4px', overflow: 'hidden', position: 'relative' }}>
                    <div style={{
                      height: '100%', width: width + '%',
                      background: 'hsl(' + (240 - i * 30) + ', 55%, ' + (40 + i * 8) + '%)',
                      borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
                      paddingRight: '8px', transition: 'width 0.5s',
                    }}>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'white' }}>
                        {step.count}人
                      </span>
                    </div>
                  </div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-primary)', minWidth: '40px', flexShrink: 0 }}>
                    {step.rate}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* ===== 支付订单管理 ===== */}
      <div style={{
        background: 'white',
        border: '1px solid var(--color-border)',
        borderRadius: '12px',
        padding: 'clamp(16px, 3vw, 24px)',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '8px',
          marginBottom: '16px',
        }}>
          <h3 style={{
            fontFamily: 'Georgia, serif',
            fontSize: '1.05rem',
            fontWeight: 'bold',
            color: 'var(--color-primary)',
            margin: 0,
          }}>
            💰 待审核付款
          </h3>
          {payments.length > 0 && (
            <span style={{
              fontSize: '0.72rem',
              fontWeight: 600,
              padding: '2px 10px',
              borderRadius: '10px',
              background: '#fef2f2',
              color: '#dc2626',
            }}>
              {payments.length} 笔待处理
            </span>
          )}
        </div>

        {/* 加载中 */}
        {payLoading && (
          <div style={{ textAlign: 'center', padding: '16px', color: 'var(--color-muted)', fontSize: '0.85rem' }}>
            加载中...
          </div>
        )}

        {/* 无待审核订单 */}
        {!payLoading && payments.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '24px',
            color: 'var(--color-muted)',
            fontSize: '0.85rem',
            background: 'var(--color-bg)',
            borderRadius: '8px',
          }}>
            ✅ 暂无待审核的付款订单
          </div>
        )}

        {/* 订单列表 */}
        {!payLoading && payments.length > 0 && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              fontSize: '0.82rem',
              borderCollapse: 'collapse',
            }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--color-muted)', fontWeight: 500, whiteSpace: 'nowrap' }}>订单号</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--color-muted)', fontWeight: 500, whiteSpace: 'nowrap' }}>用户</th>
                  <th style={{ textAlign: 'center', padding: '8px 6px', color: 'var(--color-muted)', fontWeight: 500, whiteSpace: 'nowrap' }}>金额</th>
                  <th style={{ textAlign: 'center', padding: '8px 6px', color: 'var(--color-muted)', fontWeight: 500, whiteSpace: 'nowrap' }}>时间</th>
                  <th style={{ textAlign: 'center', padding: '8px 6px', color: 'var(--color-muted)', fontWeight: 500, whiteSpace: 'nowrap' }}>操作</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.order_no} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    {/* 订单号 */}
                    <td style={{ padding: '10px 6px', fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--color-muted)' }}>
                      {p.order_no}
                    </td>
                    {/* 用户信息 */}
                    <td style={{ padding: '10px 6px' }}>
                      <p style={{ fontWeight: 500, margin: 0, fontSize: '0.85rem' }}>{p.nickname || '未设置'}</p>
                      <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--color-muted)' }}>{p.phone}</p>
                    </td>
                    {/* 金额 */}
                    <td style={{ padding: '10px 6px', textAlign: 'center' }}>
                      <span style={{
                        fontWeight: 700,
                        color: 'var(--color-primary)',
                        fontFamily: 'Georgia, serif',
                      }}>
                        ¥{p.amount}
                      </span>
                    </td>
                    {/* 提交时间 */}
                    <td style={{ padding: '10px 6px', textAlign: 'center', fontSize: '0.78rem', color: 'var(--color-muted)', whiteSpace: 'nowrap' }}>
                      {p.created_at ? new Date(p.created_at).toLocaleString('zh-CN', {
                        month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
                      }) : '--'}
                    </td>
                    {/* 确认按钮 */}
                    <td style={{ padding: '10px 6px', textAlign: 'center' }}>
                      <button
                        onClick={() => handleApprove(p.order_no)}
                        disabled={approving === p.order_no}
                        style={{
                          padding: '6px 14px',
                          fontSize: '0.78rem',
                          fontWeight: 600,
                          borderRadius: '6px',
                          border: 'none',
                          background: approving === p.order_no ? '#c4b5a5' : '#16a34a',
                          color: 'white',
                          cursor: approving === p.order_no ? 'not-allowed' : 'pointer',
                          whiteSpace: 'nowrap',
                          transition: 'background 0.15s',
                        }}
                      >
                        {approving === p.order_no ? '审核中...' : '确认支付'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ===== 数据质量仪表盘 ===== */}
      <div style={{ background: 'white', border: '1px solid var(--color-border)', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
        <h3 style={{ fontFamily: 'Georgia, serif', fontSize: '1.05rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '16px' }}>
          📊 数据质量仪表盘
        </h3>
        {dqLoading ? (
          <p style={{ color: 'var(--color-muted)', fontSize: '0.85rem' }}>加载中...</p>
        ) : dataQuality ? (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px', marginBottom: '16px' }}>
              <div style={{ background: dataQuality.overall.realDataRate >= 95 ? '#f0fdf4' : '#fffbeb', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: dataQuality.overall.realDataRate >= 95 ? '#16a34a' : '#d97706' }}>{dataQuality.overall.realDataRate}%</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>真实数据率</div>
              </div>
              <div style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#16a34a' }}>{dataQuality.overall.officialRecords}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>官方数据</div>
              </div>
              <div style={{ background: '#fef3c7', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#d97706' }}>{dataQuality.overall.simulatedRecords}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>模拟数据</div>
              </div>
              <div style={{ background: dataQuality.overall.allowPayment ? '#f0fdf4' : '#fef2f2', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: dataQuality.overall.allowPayment ? '#16a34a' : '#dc2626' }}>
                  {dataQuality.overall.allowPayment ? '✅ 允许' : '🚫 禁止'}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>收费状态</div>
              </div>
            </div>
            <div style={{ marginBottom: '12px' }}>
              <p style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '8px', color: 'var(--color-text)' }}>数据来源分布</p>
              <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', fontSize: '0.8rem' }}>
                {dataQuality.sourceDistribution.map((s, i) => (
                  <span key={i} style={{ padding: '3px 10px', borderRadius: '12px', fontSize: '0.75rem',
                    background: s.source === 'OFFICIAL' ? '#d1fae5' : s.source === 'MANUAL' ? '#dbeafe' : '#fef3c7',
                    color: s.source === 'OFFICIAL' ? '#065f46' : s.source === 'MANUAL' ? '#1e40af' : '#92400e',
                  }}>{s.source} Lv.{s.verifiedLevel}: {s.count}条</span>
                ))}
              </div>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-muted)', marginBottom: '8px' }}>
              📋 一分一段表: {dataQuality.segments.totalRecords}条 · {dataQuality.segments.yearsCovered}年 · {dataQuality.segments.subjectsCovered}科类 · <span style={{ color: '#16a34a', fontWeight: 600 }}>100%真实</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-muted)' }}>
              📚 专业数据: 画像{dataQuality.profilesCoverage.majorProfiles}/趋势{dataQuality.profilesCoverage.majorTrends}/总数{dataQuality.profilesCoverage.majorsTotal}个 · 覆盖率{dataQuality.profilesCoverage.coverageRate}%
            </div>
          </div>
        ) : <p style={{ color: 'var(--color-muted)', fontSize: '0.85rem' }}>数据质量接口暂不可用</p>}
      </div>

      {/* ===== 快捷入口 ===== */}
      <div style={{
        background: 'white',
        border: '1px solid var(--color-border)',
        borderRadius: '12px',
        padding: 'clamp(16px, 3vw, 24px)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <h3 style={{
          fontFamily: 'Georgia, serif',
          fontSize: '1.05rem',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '12px',
        }}>
          快捷操作
        </h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={handleCheckDb} style={{
            padding: '8px 16px',
            fontSize: '0.82rem',
            borderRadius: '6px',
            border: '1px solid var(--color-border)',
            background: 'white',
            color: 'var(--color-text)',
            cursor: 'pointer',
          }}>
            测试数据库
          </button>
          <Link to="/plan/generate" style={{
            padding: '8px 16px',
            fontSize: '0.82rem',
            borderRadius: '6px',
            border: '1px solid var(--color-border)',
            background: 'white',
            color: 'var(--color-text)',
            textDecoration: 'none',
          }}>
            生成方案
          </Link>
          <Link to="/score-convert" style={{
            padding: '8px 16px',
            fontSize: '0.82rem',
            borderRadius: '6px',
            border: '1px solid var(--color-border)',
            background: 'white',
            color: 'var(--color-text)',
            textDecoration: 'none',
          }}>
            分数换算
          </Link>
        </div>
        {dbMsg && <p style={{ marginTop: '10px', fontSize: '0.82rem', color: 'var(--color-muted)' }}>{dbMsg}</p>}
      </div>
    </div>
  )
}
