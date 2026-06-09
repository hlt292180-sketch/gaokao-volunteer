import { useState } from 'react'
import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { generatePlan } from '../services/api'
import { track } from '../services/track'

// ===== 冲/稳/保 三档视觉配置 =====
const tierConfig = {
  '冲': {
    title: '冲刺院校',
    subtitle: '录取概率 20%-40%，值得一搏的理想选择',
    accent: '#dc2626',
    bg: '#fef2f2',
    border: '#fecaca',
    riskLabel: '高',
    riskColor: '#dc2626',
  },
  '稳': {
    title: '稳妥院校',
    subtitle: '录取概率 50%-70%，核心填报目标',
    accent: '#d97706',
    bg: '#fffbeb',
    border: '#fde68a',
    riskLabel: '中',
    riskColor: '#d97706',
  },
  '保': {
    title: '保底院校',
    subtitle: '录取概率 80%以上，确保有学可上',
    accent: '#16a34a',
    bg: '#f0fdf4',
    border: '#bbf7d0',
    riskLabel: '低',
    riskColor: '#16a34a',
  },
}

// ===== 根据数据生成志愿分析文案 =====
function generateAnalysis(score, rank, plans, strategy, subjectType) {
  const chongList = plans.filter((p) => p.type === '冲')
  const wenList = plans.filter((p) => p.type === '稳')
  const baoList = plans.filter((p) => p.type === '保')

  // 分析院校层次分布
  const has985 = plans.some((p) => p.is985)
  const has211 = plans.some((p) => p.is211)
  const hasDoubleFirst = plans.some((p) => p.isDoubleFirst)

  let levelText = '以省内重点高校为主'
  if (has985) levelText = '包含985层次院校，整体定位较高'
  else if (has211) levelText = '以省内211/双一流高校为主，兼顾重点本科'
  else if (hasDoubleFirst) levelText = '以双一流学科高校和省内重点本科为主'

  return `根据您的${score}分（全省第 ${rank.toLocaleString()} 名，${subjectType}）的成绩水平，${levelText}。冲刺档建议填报 ${chongList.length} 所院校，适当控制在合理风险区间；稳妥档 ${wenList.length} 所可作为核心填报目标，录取把握较大；保底档 ${baoList.length} 所确保兜底安全。整体采用「${strategy}」策略配比，建议将稳妥院校放在志愿表中间位置，冲刺在前、保底在后，避免倒挂。`
}

export default function PlanGenerate() {
  const user = useAuthStore((s) => s.user)
  const isPaid = user?.isPaid || user?.isAdmin

  // 表单状态
  const [score, setScore] = useState('')
  const [rank, setRank] = useState('')
  const [subjectType, setSubjectType] = useState('物理类')
  const [strategy, setStrategy] = useState('稳健')

  // 结果状态
  const [result, setResult] = useState(null)       // API 返回的 data
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(true)    // 是否显示输入表单
  const [freeExhausted, setFreeExhausted] = useState(false)  // 免费次数用完

  // ===== 提交生成 =====
  const handleSubmit = async (e) => {
    e.preventDefault()
    const sn = Number(score), rn = Number(rank)
    if (!sn || !rn || isNaN(sn) || isNaN(rn)) {
      setError('请填写有效的分数和位次')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await generatePlan({
        provinceId: 1,
        score: sn,
        rank: rn,
        subjectType,
        strategyType: strategy,
      })
      setResult(res.data)
      setShowForm(false)
      // 📊 生成方案埋点
      track('plan_generate', { score: sn, rank: rn })
    } catch (err) {
      // 免费次数用完 → 展示付费引导而非纯文字错误
      if (err.message && err.message.includes('免费方案已用完')) {
        setFreeExhausted(true)
        setShowForm(false)
      } else {
        setError(err.message)
      }
    }
    setLoading(false)
  }

  // ===== 重新生成：回到表单 =====
  const handleRetry = () => {
    setShowForm(true)
    setError('')
    setFreeExhausted(false)
  }

  // ===== 当前用户是否应该看到打码（免费用户）=====
  const shouldBlur = result && !result.isPaid

  // ===== 辅助：获取院校列表的分组 =====
  const plans = result?.plans || []
  const chongPlans = plans.filter((p) => p.type === '冲')
  const wenPlans = plans.filter((p) => p.type === '稳')
  const baoPlans = plans.filter((p) => p.type === '保')
  const tierGroups = [
    { key: '冲', list: chongPlans },
    { key: '稳', list: wenPlans },
    { key: '保', list: baoPlans },
  ]

  // ===== 渲染一张院校卡片 =====
  const renderSchoolCard = (item, idx, tierKey, isBlurred) => {
    const cfg = tierConfig[tierKey]
    return (
      <div key={idx} style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'clamp(8px, 2vw, 16px)',
        padding: 'clamp(12px, 2vw, 16px)',
        background: 'white',
        borderRadius: '8px',
        border: `1px solid var(--color-border)`,
        position: 'relative',
        filter: isBlurred ? 'blur(4px)' : 'none',
        opacity: isBlurred ? 0.45 : 1,
        pointerEvents: isBlurred ? 'none' : 'auto',
        userSelect: isBlurred ? 'none' : 'auto',
      }}>
        {/* 序号 */}
        <span style={{
          fontFamily: 'Georgia, serif',
          fontSize: 'clamp(1rem, 2.5vw, 1.3rem)',
          fontWeight: 'bold',
          color: 'var(--color-muted)',
          minWidth: '24px',
          textAlign: 'center',
        }}>
          {idx + 1}
        </span>

        {/* 院校信息 */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(0.92rem, 2.5vw, 1.05rem)',
            fontWeight: 'bold',
            color: 'var(--color-primary)',
            marginBottom: '4px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {item.universityName}
            {/* 数据来源标识 */}
            {item.dataSource && (
              <span style={{
                display: 'inline-block',
                fontSize: '0.65rem',
                fontWeight: 500,
                padding: '1px 6px',
                borderRadius: '3px',
                marginLeft: '6px',
                verticalAlign: 'middle',
                background: item.dataSource === 'OFFICIAL' ? '#d1fae5' :
                           item.dataSource === 'MANUAL' ? '#dbeafe' : '#fef3c7',
                color: item.dataSource === 'OFFICIAL' ? '#065f46' :
                       item.dataSource === 'MANUAL' ? '#1e40af' : '#92400e',
              }}>
                {item.dataSource === 'OFFICIAL' ? '官方数据' :
                 item.dataSource === 'MANUAL' ? '第三方数据' : '模拟预测'}
              </span>
            )}
          </p>
          <p style={{
            fontSize: '0.78rem',
            color: 'var(--color-muted)',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {[item.city, item.is985 ? '985' : '', item.is211 ? '211' : '', item.isDoubleFirst ? '双一流' : '']
              .filter(Boolean).join(' · ')}
            {/* 专业组/选科信息（仅真实数据展示） */}
            {item.majorGroup && (
              <span style={{ color: 'var(--color-accent)', fontWeight: 500 }}>
                {' · '}{item.majorGroup}
                {item.subjectRequirement ? `(${item.subjectRequirement})` : ''}
              </span>
            )}
          </p>
        </div>

        {/* 往年最低位次 */}
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '2px' }}>最低位次</p>
          <p style={{
            fontSize: 'clamp(0.82rem, 2vw, 0.9rem)',
            fontWeight: 600,
            color: 'var(--color-text)',
          }}>
            {item.minRank?.toLocaleString() || '--'}
          </p>
        </div>

        {/* 录取概率 */}
        <div style={{ textAlign: 'center', flexShrink: 0, minWidth: '52px' }}>
          <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '2px' }}>概率</p>
          <p style={{
            fontSize: 'clamp(0.82rem, 2vw, 0.92rem)',
            fontWeight: 700,
            color: cfg.accent,
          }}>
            {item.probability}
          </p>
        </div>

        {/* 风险等级 */}
        <div style={{ flexShrink: 0 }}>
          <span style={{
            display: 'inline-block',
            fontSize: '0.7rem',
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: '4px',
            background: cfg.bg,
            color: cfg.riskColor,
            border: `1px solid ${cfg.border}`,
          }}>
            {cfg.riskLabel}风险
          </span>
        </div>
      </div>
    )
  }

  // ================================================================
  // 状态 A：免费次数用完 → 付费引导页
  // ================================================================
  if (freeExhausted) {
    return (
      <div className="page-enter" style={{
        maxWidth: '480px',
        margin: '0 auto',
        padding: 'clamp(40px, 8vw, 80px) 16px',
        textAlign: 'center',
      }}>
        {/* 图标 */}
        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🔒</div>

        <h1 style={{
          fontFamily: 'Georgia, serif',
          fontSize: 'clamp(1.4rem, 4vw, 1.8rem)',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '12px',
        }}>
          免费方案已用完
        </h1>

        <p style={{
          color: 'var(--color-muted)',
          fontSize: '0.9rem',
          lineHeight: 1.7,
          marginBottom: '8px',
        }}>
          每位用户可免费生成 <strong style={{ color: 'var(--color-text)' }}>1 次</strong>完整方案，
          您已使用过免费额度。
        </p>

        {/* 付费权益清单 */}
        <div style={{
          background: 'white',
          border: '1px solid var(--color-border)',
          borderRadius: '10px',
          padding: 'clamp(16px, 3vw, 24px)',
          marginBottom: '24px',
          textAlign: 'left',
        }}>
          <p style={{
            fontSize: '0.85rem',
            fontWeight: 600,
            color: 'var(--color-primary)',
            marginBottom: '12px',
          }}>
            升级后解锁：
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              '无限次生成冲稳保方案',
              '查看全部院校推荐（不再打码）',
              '完整志愿分析报告',
              '专业趋势预测 + 匹配度评分',
            ].map((item) => (
              <div key={item} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--color-text)' }}>
                <span style={{ color: '#16a34a', fontWeight: 'bold', flexShrink: 0 }}>✓</span>
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* CTA 按钮 */}
        <Link to="/upgrade" style={{
          display: 'inline-block',
          background: 'var(--color-accent)',
          color: 'var(--color-primary)',
          fontWeight: 700,
          fontSize: '1.05rem',
          padding: '14px 48px',
          borderRadius: '8px',
          textDecoration: 'none',
          boxShadow: '0 2px 8px rgba(0,0,0,0.12)',
          transition: 'background 0.15s',
        }}>
          解锁完整方案 ￥39
        </Link>

        <p style={{
          fontSize: '0.78rem',
          color: 'var(--color-muted)',
          marginTop: '14px',
        }}>
          首批体验价，原价 ￥168
        </p>

        {/* 返回修改参数 */}
        <button
          onClick={handleRetry}
          style={{
            display: 'inline-block',
            marginTop: '20px',
            fontSize: '0.82rem',
            color: 'var(--color-muted)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            textDecoration: 'underline',
          }}
        >
          ← 返回修改参数
        </button>
      </div>
    )
  }

  // ================================================================
  // 状态 B：未生成 → 显示输入表单
  // ================================================================
  if (showForm) {
    return (
      <div className="page-enter" style={{
        maxWidth: '480px',
        margin: '0 auto',
        padding: 'clamp(24px, 5vw, 48px) 16px',
      }}>
        <h1 style={{
          fontFamily: 'Georgia, serif',
          fontSize: 'clamp(1.6rem, 4vw, 2rem)',
          fontWeight: 'bold',
          textAlign: 'center',
          marginBottom: '8px',
          color: 'var(--color-primary)',
        }}>
          志愿方案生成
        </h1>
        <p style={{
          textAlign: 'center',
          color: 'var(--color-muted)',
          fontSize: '0.9rem',
          marginBottom: '32px',
        }}>
          输入分数和位次，智能生成冲稳保方案
        </p>

        <form onSubmit={handleSubmit} style={{
          background: 'white',
          border: '1px solid var(--color-border)',
          borderRadius: '12px',
          padding: 'clamp(20px, 4vw, 28px)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}>
          {error && (
            <div style={{
              background: '#fef2f2',
              color: '#dc2626',
              fontSize: '0.85rem',
              padding: '10px 14px',
              borderRadius: '8px',
              marginBottom: '16px',
            }}>
              {error}
            </div>
          )}

          {/* 选科 */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '0.85rem',
              fontWeight: 600,
              color: 'var(--color-text)',
              marginBottom: '6px',
            }}>
              选科类别
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['物理类', '历史类'].map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setSubjectType(t)}
                  style={{
                    flex: 1,
                    padding: '10px 0',
                    fontSize: '0.9rem',
                    fontWeight: subjectType === t ? 600 : 400,
                    borderRadius: '8px',
                    border: subjectType === t ? '2px solid var(--color-primary)' : '1px solid var(--color-border)',
                    background: subjectType === t ? 'var(--color-primary)' : 'white',
                    color: subjectType === t ? 'white' : 'var(--color-text)',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* 分数 + 位次 */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-text)',
                marginBottom: '6px',
              }}>
                高考分数
              </label>
              <input
                type="number"
                value={score}
                onChange={(e) => setScore(e.target.value)}
                placeholder="如 620"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  fontSize: '0.95rem',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-bg)',
                  color: 'var(--color-text)',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-text)',
                marginBottom: '6px',
              }}>
                全省位次
              </label>
              <input
                type="number"
                value={rank}
                onChange={(e) => setRank(e.target.value)}
                placeholder="如 8680"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  fontSize: '0.95rem',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-bg)',
                  color: 'var(--color-text)',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          {/* 策略 */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '0.85rem',
              fontWeight: 600,
              color: 'var(--color-text)',
              marginBottom: '6px',
            }}>
              策略偏好
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {[
                { key: '稳健', icon: '🛡', desc: '保底优先' },
                { key: '均衡', icon: '⚖', desc: '冲稳兼顾' },
                { key: '激进', icon: '🚀', desc: '冲刺为主' },
              ].map((s) => (
                <button
                  key={s.key}
                  type="button"
                  onClick={() => setStrategy(s.key)}
                  style={{
                    flex: 1,
                    padding: '10px 6px',
                    textAlign: 'center',
                    fontSize: '0.82rem',
                    fontWeight: strategy === s.key ? 600 : 400,
                    borderRadius: '8px',
                    border: strategy === s.key ? '2px solid var(--color-primary)' : '1px solid var(--color-border)',
                    background: strategy === s.key ? 'var(--color-primary)' : 'white',
                    color: strategy === s.key ? 'white' : 'var(--color-text)',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                    lineHeight: 1.3,
                  }}
                >
                  <span style={{ display: 'block', fontSize: '1.1rem', marginBottom: '2px' }}>{s.icon}</span>
                  {s.key}
                </button>
              ))}
            </div>
          </div>

          {/* 提交按钮 */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px 0',
              fontSize: '1rem',
              fontWeight: 700,
              borderRadius: '8px',
              border: 'none',
              background: loading ? '#c4b5a5' : 'var(--color-accent)',
              color: 'var(--color-primary)',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {loading ? '生成中...' : '生成志愿方案'}
          </button>

          {/* 免费用户提示 */}
          {!isPaid && (
            <p style={{
              textAlign: 'center',
              fontSize: '0.78rem',
              color: 'var(--color-muted)',
              marginTop: '14px',
            }}>
              免费用户可生成 1 次完整方案，升级付费版不限次数
            </p>
          )}
        </form>
      </div>
    )
  }

  // ================================================================
  // 状态 C：已生成 → 展示结果（四段式）
  // ================================================================
  return (
    <div className="page-enter" style={{
      maxWidth: '640px',
      margin: '0 auto',
      padding: 'clamp(20px, 4vw, 40px) 16px',
    }}>

      {/* ========== 第一部分：用户信息卡片 ========== */}
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
          gap: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px', flexWrap: 'wrap' }}>
            {/* 分数 */}
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>分数</span>
              <p style={{
                fontFamily: 'Georgia, serif',
                fontSize: 'clamp(1.5rem, 4vw, 1.8rem)',
                fontWeight: 'bold',
                color: 'var(--color-primary)',
                lineHeight: 1.2,
              }}>
                {score}
              </p>
            </div>
            {/* 分隔 */}
            <span style={{ color: 'var(--color-border)', fontSize: '1.2rem' }}>|</span>
            {/* 位次 */}
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>全省位次</span>
              <p style={{
                fontFamily: 'Georgia, serif',
                fontSize: 'clamp(1.5rem, 4vw, 1.8rem)',
                fontWeight: 'bold',
                color: 'var(--color-primary)',
                lineHeight: 1.2,
              }}>
                {Number(rank).toLocaleString()}
              </p>
            </div>
            {/* 分隔 */}
            <span style={{ color: 'var(--color-border)', fontSize: '1.2rem' }}>|</span>
            {/* 选科 */}
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>选科</span>
              <p style={{
                fontSize: '1rem',
                fontWeight: 600,
                color: 'var(--color-text)',
                lineHeight: 1.2,
              }}>
                {subjectType}
              </p>
            </div>
          </div>

          {/* 重新生成按钮 */}
          <button
            onClick={handleRetry}
            style={{
              padding: '8px 16px',
              fontSize: '0.82rem',
              fontWeight: 500,
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              background: 'white',
              color: 'var(--color-muted)',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {isPaid ? '重新生成' : '修改参数'}
          </button>
        </div>
      </div>

      {/* ========== 第二部分：冲/稳/保 三区结果 ========== */}
      {tierGroups.map(({ key, list }) => {
        const cfg = tierConfig[key]
        // 免费用户每个档只显示第1所，其余打码
        const visibleCount = shouldBlur ? 1 : list.length

        return (
          <div key={key} style={{ marginBottom: '24px' }}>
            {/* 分区标题 */}
            <div style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: '8px',
              marginBottom: '12px',
              padding: '0 4px',
            }}>
              <span style={{
                display: 'inline-block',
                width: '4px',
                height: '18px',
                borderRadius: '2px',
                background: cfg.accent,
                flexShrink: 0,
              }} />
              <h2 style={{
                fontFamily: 'Georgia, serif',
                fontSize: 'clamp(1.1rem, 3vw, 1.25rem)',
                fontWeight: 'bold',
                color: cfg.accent,
                margin: 0,
              }}>
                {cfg.title}
              </h2>
              <span style={{
                fontSize: '0.75rem',
                color: 'var(--color-muted)',
              }}>
                {cfg.subtitle}
              </span>
              {shouldBlur && list.length > 1 && (
                <span style={{
                  fontSize: '0.7rem',
                  background: 'var(--color-accent)',
                  color: 'var(--color-primary)',
                  fontWeight: 600,
                  padding: '1px 8px',
                  borderRadius: '10px',
                  marginLeft: 'auto',
                }}>
                  剩余 {list.length - 1} 所需解锁
                </span>
              )}
            </div>

            {/* 院校列表 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {list.map((item, idx) => {
                const isBlurred = idx >= visibleCount
                return renderSchoolCard(item, idx, key, isBlurred)
              })}
            </div>
          </div>
        )
      })}

      {/* ========== 数据来源合规提示 ========== */}
      {result?.dataQuality && (
        <div style={{
          background: '#f0fdf4',
          border: '1px solid #bbf7d0',
          borderRadius: '8px',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flexWrap: 'wrap',
          fontSize: '0.82rem',
          color: '#065f46',
        }}>
          <span style={{ fontWeight: 700 }}>📊 数据质量</span>
          <span>官方数据占比 <b>{result.dataQuality.realDataRate}%</b></span>
          <span style={{ color: '#6b7280' }}>|</span>
          <span>官方 {result.dataQuality.officialCount} 条</span>
          <span style={{ color: '#6b7280' }}>|</span>
          <span>模拟 {result.dataQuality.simulatedCount} 条</span>
          {result.dataQuality.realDataRate < 95 && (
            <span style={{
              fontSize: '0.75rem',
              color: '#92400e',
              background: '#fef3c7',
              padding: '2px 8px',
              borderRadius: '3px',
              fontWeight: 600,
            }}>
              ⚠️ 部分数据为模拟预测，仅供参考
            </span>
          )}
        </div>
      )}

      {/* ========== 第三部分：志愿分析文案 ========== */}
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
          fontSize: 'clamp(1rem, 2.5vw, 1.1rem)',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '12px',
        }}>
          📋 志愿分析
        </h3>
        {shouldBlur ? (
          // 免费用户：分析文打码
          <div style={{ position: 'relative' }}>
            <p style={{
              color: 'var(--color-text)',
              fontSize: '0.9rem',
              lineHeight: 1.85,
              filter: 'blur(4px)',
              opacity: 0.45,
              userSelect: 'none',
              margin: 0,
            }}>
              {generateAnalysis(Number(score), Number(rank), plans, strategy, subjectType)}
            </p>
            {/* 遮罩 */}
            <div style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}>
              <span style={{ fontSize: '1.5rem' }}>🔒</span>
              <span style={{
                fontSize: '0.82rem',
                fontWeight: 600,
                color: 'var(--color-primary)',
              }}>
                解锁完整分析报告
              </span>
            </div>
          </div>
        ) : (
          <p style={{
            color: 'var(--color-text)',
            fontSize: '0.9rem',
            lineHeight: 1.85,
            margin: 0,
          }}>
            {generateAnalysis(Number(score), Number(rank), plans, strategy, subjectType)}
          </p>
        )}
      </div>

      {/* ========== 第四部分：免费用户付费引导（仅免费用户显示）========== */}
      {shouldBlur && (
        <div style={{
          textAlign: 'center',
          padding: 'clamp(24px, 4vw, 36px) 20px',
          background: 'var(--color-primary)',
          borderRadius: '12px',
          color: 'white',
        }}>
          <p style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1.1rem, 3vw, 1.3rem)',
            fontWeight: 'bold',
            marginBottom: '12px',
          }}>
            解锁完整方案
          </p>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            marginBottom: '20px',
            fontSize: '0.88rem',
            color: 'rgba(255,255,255,0.75)',
          }}>
            <span>✓ 查看全部 {plans.length} 所院校推荐</span>
            <span>✓ 查看专业推荐与匹配度</span>
            <span>✓ 查看志愿分析报告</span>
            <span>✓ 无限次生成方案 + 多方案对比</span>
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link
              to="/upgrade"
              style={{
                display: 'inline-block',
                background: 'var(--color-accent)',
                color: 'var(--color-primary)',
                fontWeight: 700,
                fontSize: '1rem',
                padding: '12px 40px',
                borderRadius: '8px',
                textDecoration: 'none',
                transition: 'background 0.15s',
              }}
            >
              立即解锁 ￥168
            </Link>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              fontSize: '0.8rem',
              color: 'rgba(255,255,255,0.6)',
            }}>
              或 3人拼团 ￥128/人
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
