import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getMajor, getMajorTrend } from '../services/api'
import useAuthStore from '../store/authStore'

// ===== 趋势指标配色映射 =====
const demandColors = {
  '快速增长': { color: '#16a34a', bg: '#f0fdf4' },
  '增长': { color: '#16a34a', bg: '#f0fdf4' },
  '稳定': { color: '#d97706', bg: '#fffbeb' },
  '下降': { color: '#dc2626', bg: '#fef2f2' },
}

const saturationLabels = {
  '供不应求': { color: '#16a34a', text: '供不应求' },
  '平衡': { color: '#d97706', text: '供需平衡' },
  '供过于求': { color: '#dc2626', text: '供过于求' },
}

const confidenceColors = {
  '高': { color: '#16a34a' },
  '中': { color: '#d97706' },
  '低': { color: '#dc2626' },
}

export default function MajorDetail() {
  const { id } = useParams()
  const [major, setMajor] = useState(null)
  const [trend, setTrend] = useState(null)
  const [trendLoading, setTrendLoading] = useState(true)
  const isPaid = useAuthStore((s) => s.user?.isPaid || s.user?.isAdmin)

  useEffect(() => {
    (async () => {
      try {
        const r = await getMajor(id)
        setMajor(r.data)
      } catch {}
    })()
    // 同时加载趋势数据（无论是否付费都获取，前端做打码）
    ;(async () => {
      try {
        const r = await getMajorTrend(id)
        if (r.data) setTrend(r.data)
      } catch {}
      setTrendLoading(false)
    })()
  }, [id])

  if (!major) return (
    <div className="max-w-4xl mx-auto px-4 py-8 text-center" style={{ color: 'var(--color-muted)' }}>加载中...</div>
  )

  const p = major.profile

  return (
    <div className="page-enter" style={{
      maxWidth: '680px',
      margin: '0 auto',
      padding: 'clamp(16px, 3vw, 32px) 16px',
    }}>
      {/* 返回链接 */}
      <Link to="/majors" className="text-sm mb-4 inline-block hover:underline"
        style={{ color: 'var(--color-muted)' }}>
        ← 返回专业列表
      </Link>

      {/* ===== 专业基本信息 ===== */}
      <div className="card" style={{ padding: 'clamp(16px, 3vw, 24px)', marginBottom: '20px' }}>
        <h1 style={{
          fontFamily: 'Georgia, serif',
          fontSize: 'clamp(1.3rem, 3.5vw, 1.6rem)',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '10px',
        }}>
          {major.name}
        </h1>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
          <span style={{
            fontSize: '0.75rem', padding: '3px 10px', borderRadius: '6px',
            background: 'var(--color-bg)', color: 'var(--color-primary)', fontWeight: 500,
          }}>
            {major.category}
          </span>
          <span style={{
            fontSize: '0.75rem', padding: '3px 10px', borderRadius: '6px',
            background: 'var(--color-bg)', color: 'var(--color-muted)',
          }}>
            {major.degree} · {major.duration}年制
          </span>
        </div>
        <p style={{ color: 'var(--color-text)', fontSize: '0.9rem', lineHeight: 1.7 }}>
          {major.intro}
        </p>
      </div>

      {/* ===== 就业画像 ===== */}
      {p ? (
        <div className="card" style={{ padding: 'clamp(16px, 3vw, 24px)', marginBottom: '20px' }}>
          <h2 style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1rem, 2.5vw, 1.1rem)',
            fontWeight: 'bold',
            color: 'var(--color-primary)',
            marginBottom: '16px',
          }}>
            💼 就业画像（{p.data_year}年数据）
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '10px',
          }}>
            {[
              { label: '平均起薪', value: `¥${p.avg_starting_salary?.toLocaleString() || '--'}`, color: 'var(--color-primary)' },
              { label: '就业率', value: `${Number(p.employment_rate_3yr) || '--'}%`, color: '#16a34a' },
              { label: '读研比例', value: `${Number(p.postgrad_rate) || '--'}%`, color: '#7c3aed' },
              { label: '霍兰德代码', value: p.holland_code || '--', color: '#ea580c' },
            ].map((item) => (
              <div key={item.label} style={{
                textAlign: 'center',
                padding: 'clamp(10px, 2vw, 14px)',
                borderRadius: '8px',
                background: 'var(--color-bg)',
              }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '4px' }}>
                  {item.label}
                </p>
                <p style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
                  fontWeight: 'bold',
                  color: item.color,
                }}>
                  {item.value}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card text-center" style={{ padding: '24px', marginBottom: '20px', color: 'var(--color-muted)' }}>
          暂无就业数据
        </div>
      )}

      {/* ===== 趋势预测 —— 核心付费区域 ===== */}
      <div className="card" style={{
        padding: 'clamp(16px, 3vw, 24px)',
        marginBottom: '20px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* 标题行 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '8px',
          marginBottom: '16px',
        }}>
          <h2 style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1rem, 2.5vw, 1.1rem)',
            fontWeight: 'bold',
            color: 'var(--color-primary)',
            margin: 0,
          }}>
            📈 {trend?.yearForecast || '2030'}年趋势预测
          </h2>
          {!isPaid && trend && (
            <span style={{
              fontSize: '0.7rem',
              fontWeight: 600,
              padding: '2px 10px',
              borderRadius: '10px',
              background: 'var(--color-accent)',
              color: 'var(--color-primary)',
            }}>
              🔒 需付费查看
            </span>
          )}
        </div>

        {/* 趋势数据加载中 */}
        {trendLoading && (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-muted)', fontSize: '0.85rem' }}>
            趋势数据加载中...
          </div>
        )}

        {/* 无趋势数据 */}
        {!trendLoading && !trend && (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-muted)', fontSize: '0.85rem' }}>
            暂无该专业的趋势预测数据
          </div>
        )}

        {/* 有趋势数据 */}
        {!trendLoading && trend && (
          <div style={{
            filter: isPaid ? 'none' : 'blur(5px)',
            opacity: isPaid ? 1 : 0.4,
            pointerEvents: isPaid ? 'auto' : 'none',
            userSelect: isPaid ? 'auto' : 'none',
            transition: 'filter 0.2s',
          }}>
            {/* 四个指标卡片 */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: '10px',
              marginBottom: '16px',
            }}>
              {/* 需求趋势 */}
              <div style={{
                textAlign: 'center',
                padding: 'clamp(10px, 2vw, 14px)',
                borderRadius: '8px',
                background: (demandColors[trend.demandTrend] || demandColors['稳定']).bg,
              }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '4px' }}>
                  需求趋势
                </p>
                <p style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
                  fontWeight: 'bold',
                  color: (demandColors[trend.demandTrend] || demandColors['稳定']).color,
                }}>
                  {trend.demandTrend}
                </p>
              </div>

              {/* 人才饱和度 */}
              <div style={{
                textAlign: 'center',
                padding: 'clamp(10px, 2vw, 14px)',
                borderRadius: '8px',
                background: (saturationLabels[trend.saturationLevel] || saturationLabels['平衡']).color === '#16a34a'
                  ? '#f0fdf4' : (saturationLabels[trend.saturationLevel] || saturationLabels['平衡']).color === '#dc2626'
                    ? '#fef2f2' : '#fffbeb',
              }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '4px' }}>
                  人才饱和度
                </p>
                <p style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
                  fontWeight: 'bold',
                  color: (saturationLabels[trend.saturationLevel] || saturationLabels['平衡']).color,
                }}>
                  {(saturationLabels[trend.saturationLevel] || { text: trend.saturationLevel }).text}
                </p>
              </div>

              {/* 预测薪资 */}
              <div style={{
                textAlign: 'center',
                padding: 'clamp(10px, 2vw, 14px)',
                borderRadius: '8px',
                background: 'var(--color-bg)',
              }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '4px' }}>
                  {trend.yearForecast}年预测月薪
                </p>
                <p style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
                  fontWeight: 'bold',
                  color: 'var(--color-primary)',
                }}>
                  ¥{trend.avgSalaryForecast?.toLocaleString() || '--'}
                </p>
              </div>

              {/* 置信度 */}
              <div style={{
                textAlign: 'center',
                padding: 'clamp(10px, 2vw, 14px)',
                borderRadius: '8px',
                background: 'var(--color-bg)',
              }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginBottom: '4px' }}>
                  预测置信度
                </p>
                <p style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
                  fontWeight: 'bold',
                  color: (confidenceColors[trend.confidence] || confidenceColors['中']).color,
                }}>
                  {trend.confidence}
                </p>
              </div>
            </div>

            {/* 分析总结 */}
            <div style={{
              padding: 'clamp(12px, 2vw, 16px)',
              borderRadius: '8px',
              background: 'var(--color-bg)',
              marginBottom: '12px',
            }}>
              <p style={{
                fontSize: '0.85rem',
                color: 'var(--color-text)',
                lineHeight: 1.8,
                margin: 0,
              }}>
                {trend.summary}
              </p>
            </div>

            {/* 数据来源 */}
            <p style={{
              fontSize: '0.72rem',
              color: 'var(--color-muted)',
              margin: 0,
              textAlign: 'right',
            }}>
              数据来源：{trend.dataSource}
            </p>
          </div>
        )}

        {/* 付费遮罩层（覆盖在模糊内容上方） */}
        {!isPaid && trend && (
          <div style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'var(--color-primary)',
            color: 'white',
            textAlign: 'center',
            padding: 'clamp(16px, 3vw, 24px) 16px',
            borderRadius: '0 0 12px 12px',
          }}>
            <p style={{
              fontFamily: 'Georgia, serif',
              fontSize: 'clamp(0.95rem, 2.5vw, 1.05rem)',
              fontWeight: 'bold',
              marginBottom: '4px',
            }}>
              解锁完整方案需付费 ￥39
            </p>
            <p style={{
              fontSize: '0.78rem',
              color: 'rgba(255,255,255,0.7)',
              marginBottom: '14px',
            }}>
              查看趋势预测完整数据 + 更多付费权益
            </p>
            <Link to="/upgrade" style={{
              display: 'inline-block',
              background: 'var(--color-accent)',
              color: 'var(--color-primary)',
              fontWeight: 700,
              fontSize: '0.9rem',
              padding: '10px 32px',
              borderRadius: '8px',
              textDecoration: 'none',
              transition: 'background 0.15s',
            }}>
              立即解锁
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
