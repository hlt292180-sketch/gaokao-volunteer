import { useState, useEffect } from 'react'
import useAuthStore from '../store/authStore'
import { createPayment } from '../services/api'
import { track } from '../services/track'
import axios from 'axios'

// ===== 已包含功能列表 =====
const includedFeatures = [
  '完整冲稳保志愿方案',
  '推荐专业匹配分析',
  '志愿表风险体检',
  '多所院校智能推荐',
  '专业趋势预测（4年后就业前景）',
  '无限次方案生成与对比',
]

// ===== 付款流程四步骤 =====
const steps = [
  {
    num: 1,
    title: '扫码付款',
    desc: '使用微信或支付宝扫描二维码，支付首批体验价 ￥39',
  },
  {
    num: 2,
    title: '点击确认',
    desc: '付款完成后，点击下方「我已付款」按钮提交确认',
  },
  {
    num: 3,
    title: '系统审核',
    desc: '系统将核对您的付款信息，通常在 1 小时内完成',
  },
  {
    num: 4,
    title: '开通服务',
    desc: '审核通过后自动为您开通全部付费功能',
  },
]

export default function Upgrade() {
  const user = useAuthStore((s) => s.user)
  const refreshUser = useAuthStore((s) => s.refreshUser)
  const isPaid = user?.isPaid || user?.isAdmin

  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [orderNo, setOrderNo] = useState('')
  const [error, setError] = useState('')
  const [paymentAllowed, setPaymentAllowed] = useState(true)  // 收费保护
  const [realDataRate, setRealDataRate] = useState(0)         // 真实数据率

  // 检查收费保护状态
  useEffect(() => {
    axios.get('/api/analytics/data-quality').then(res => {
      if (res.data?.success) {
        const dq = res.data.data.overall
        setRealDataRate(dq.realDataRate)
        setPaymentAllowed(dq.allowPayment)
      }
    }).catch(() => {
      // 接口不可用时默认允许（避免阻塞正常支付流程）
      setPaymentAllowed(true)
    })
  }, [])

  // ===== 点击"我已付款" =====
  const handleConfirm = async () => {
    // 📊 点击付款埋点
    track('pay_click')
    setSubmitting(true)
    setError('')
    try {
      const res = await createPayment({ amount: 39, plan: 'standard' })
      setOrderNo(res.data.orderNo)
      setSubmitted(true)
      await refreshUser()
      // 📊 确认付款埋点
      track('pay_confirm')
    } catch (err) {
      setError(err.message)
    }
    setSubmitting(false)
  }

  // ===== 已付费用户：展示已开通状态 =====
  if (isPaid) {
    return (
      <div className="page-enter" style={{
        maxWidth: '480px',
        margin: '0 auto',
        padding: 'clamp(40px, 8vw, 80px) 16px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>✅</div>
        <h1 style={{
          fontFamily: 'Georgia, serif',
          fontSize: 'clamp(1.4rem, 3.5vw, 1.8rem)',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '12px',
        }}>
          您已开通付费版
        </h1>
        <p style={{ color: 'var(--color-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          全部付费功能已解锁，可无限次使用
        </p>
        <a
          href="/plan/generate"
          style={{
            display: 'inline-block',
            background: 'var(--color-accent)',
            color: 'var(--color-primary)',
            fontWeight: 700,
            fontSize: '1rem',
            padding: '12px 32px',
            borderRadius: '8px',
            textDecoration: 'none',
          }}
        >
          去生成方案 →
        </a>
      </div>
    )
  }

  return (
    <div className="page-enter" style={{
      maxWidth: '520px',
      margin: '0 auto',
      padding: 'clamp(20px, 4vw, 40px) 16px',
    }}>

      {/* =============================================
          标题区
          ============================================= */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{
          fontFamily: 'Georgia, serif',
          fontSize: 'clamp(1.6rem, 4vw, 2rem)',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '8px',
        }}>
          解锁完整志愿方案
        </h1>
        <p style={{
          color: 'var(--color-muted)',
          fontSize: '0.9rem',
        }}>
          一次付费，高考出分期间无限使用
        </p>
      </div>

      {/* =============================================
          功能清单
          ============================================= */}
      <div style={{
        background: 'white',
        border: '1px solid var(--color-border)',
        borderRadius: '12px',
        padding: 'clamp(20px, 4vw, 28px)',
        marginBottom: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <h3 style={{
          fontFamily: 'Georgia, serif',
          fontSize: '1.05rem',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '16px',
        }}>
          已包含
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {includedFeatures.map((f) => (
            <div key={f} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.9rem',
              color: 'var(--color-text)',
            }}>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: '#dcfce7',
                color: '#16a34a',
                fontSize: '0.7rem',
                fontWeight: 'bold',
                flexShrink: 0,
              }}>
                ✓
              </span>
              {f}
            </div>
          ))}
        </div>
      </div>

      {/* =============================================
          价格区域
          ============================================= */}
      <div style={{
        background: 'var(--color-primary)',
        borderRadius: '12px',
        padding: 'clamp(20px, 4vw, 28px)',
        marginBottom: '20px',
        color: 'white',
        textAlign: 'center',
      }}>
        {/* 原价划线 */}
        <p style={{
          fontSize: '0.9rem',
          color: 'rgba(255,255,255,0.5)',
          textDecoration: 'line-through',
          marginBottom: '4px',
        }}>
          原价：168 元
        </p>

        {/* 现价 */}
        <div style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'center',
          gap: '6px',
          marginBottom: '8px',
        }}>
          <span style={{
            fontSize: '0.9rem',
            color: 'rgba(255,255,255,0.7)',
          }}>
            首批体验价
          </span>
          <span style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(2.2rem, 6vw, 2.8rem)',
            fontWeight: 'bold',
            color: 'var(--color-accent)',
            lineHeight: 1,
          }}>
            39
          </span>
          <span style={{
            fontSize: '1rem',
            color: 'rgba(255,255,255,0.7)',
          }}>
            元
          </span>
        </div>

        {/* 限时标签 */}
        <span style={{
          display: 'inline-block',
          fontSize: '0.72rem',
          fontWeight: 600,
          padding: '3px 10px',
          borderRadius: '10px',
          background: 'rgba(255,255,255,0.12)',
          color: 'rgba(255,255,255,0.8)',
          letterSpacing: '1px',
        }}>
          限时开放
        </span>
      </div>

      {/* =============================================
          付款流程
          ============================================= */}
      <div style={{
        background: 'white',
        border: '1px solid var(--color-border)',
        borderRadius: '12px',
        padding: 'clamp(20px, 4vw, 28px)',
        marginBottom: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <h3 style={{
          fontFamily: 'Georgia, serif',
          fontSize: '1.05rem',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '20px',
        }}>
          付款流程
        </h3>

        {/* 四步骤 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {steps.map((step, i) => (
            <div key={step.num} style={{ display: 'flex', gap: '14px' }}>
              {/* 左侧：序号 + 连接线 */}
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                flexShrink: 0,
                width: '32px',
              }}>
                {/* 圆形序号 */}
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'var(--color-primary)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  flexShrink: 0,
                }}>
                  {step.num}
                </div>
                {/* 连接线（最后一步不画） */}
                {i < steps.length - 1 && (
                  <div style={{
                    width: '1px',
                    flex: 1,
                    minHeight: '24px',
                    background: 'var(--color-border)',
                    margin: '4px 0',
                  }} />
                )}
              </div>

              {/* 右侧：标题 + 描述 */}
              <div style={{
                paddingBottom: i < steps.length - 1 ? '24px' : '0',
                paddingTop: '4px',
              }}>
                <p style={{
                  fontSize: '0.92rem',
                  fontWeight: 600,
                  color: 'var(--color-text)',
                  marginBottom: '2px',
                }}>
                  {step.title}
                </p>
                <p style={{
                  fontSize: '0.8rem',
                  color: 'var(--color-muted)',
                  lineHeight: 1.5,
                  margin: 0,
                }}>
                  {step.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* 付款二维码区域 */}
        <div style={{
          marginTop: '24px',
          padding: '24px',
          background: 'var(--color-bg)',
          borderRadius: '8px',
          textAlign: 'center',
          border: '1px dashed var(--color-border)',
        }}>
          {/* 二维码占位 —— 替换为真实收款码图片 */}
          <div style={{
            width: '160px',
            height: '160px',
            margin: '0 auto 12px',
            background: 'white',
            border: '1px solid var(--color-border)',
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-muted)',
          }}>
            <span style={{ fontSize: '2rem', marginBottom: '4px' }}>📱</span>
            <span style={{ fontSize: '0.72rem' }}>收款二维码</span>
            <span style={{ fontSize: '0.65rem', opacity: 0.6 }}>部署后替换</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--color-muted)', margin: 0 }}>
            请使用 <strong>微信</strong> 或 <strong>支付宝</strong> 扫描二维码付款
          </p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div style={{
            marginTop: '16px',
            padding: '10px 14px',
            background: '#fef2f2',
            color: '#dc2626',
            fontSize: '0.85rem',
            borderRadius: '8px',
          }}>
            {error}
          </div>
        )}

        {/* 提交成功 */}
        {submitted && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            fontSize: '0.85rem',
            color: '#16a34a',
          }}>
            <p style={{ fontWeight: 600, marginBottom: '4px' }}>✅ 付款确认已提交</p>
            <p style={{ margin: 0, fontSize: '0.8rem' }}>
              订单号：{orderNo}，请耐心等待管理员审核开通，通常 1 小时内完成。
            </p>
          </div>
        )}

        {/* 收费保护提示 */}
        {!paymentAllowed && (
          <div style={{
            marginTop: '16px',
            padding: '14px 16px',
            background: '#fffbeb',
            border: '2px solid #f59e0b',
            borderRadius: '8px',
          }}>
            <p style={{ fontWeight: 700, color: '#92400e', marginBottom: '6px', fontSize: '0.9rem' }}>
              ⚠️ 收费功能暂未开放
            </p>
            <p style={{ color: '#92400e', fontSize: '0.82rem', margin: 0, lineHeight: 1.6 }}>
              当前系统真实数据覆盖率 <b>{realDataRate}%</b>，
              未达到 95% 收费门槛。部分院校数据仍使用模拟预测，
              根据平台运营规范，暂不开启收费功能。请关注后续数据更新。
            </p>
          </div>
        )}

        {/* 我已付款按钮 */}
        {!submitted && paymentAllowed && (
          <button
            onClick={handleConfirm}
            disabled={submitting}
            style={{
              width: '100%',
              marginTop: '20px',
              padding: '14px 0',
              fontSize: '1rem',
              fontWeight: 700,
              borderRadius: '8px',
              border: 'none',
              background: submitting ? '#c4b5a5' : 'var(--color-accent)',
              color: 'var(--color-primary)',
              cursor: submitting ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {submitting ? '提交中...' : '我已付款，确认开通'}
          </button>
        )}

        {/* 数据来源声明 */}
        <p style={{
          color: 'var(--color-muted)',
          fontSize: '0.72rem',
          textAlign: 'center',
          marginTop: '16px',
          lineHeight: 1.5,
        }}>
          数据来源：江苏省教育考试院 | 中国教育在线 | 各高校招生网。
          部分院校数据暂未公开，系统使用历史趋势模型进行预测，
          预测结果仅供参考，最终以官方录取结果为准。
        </p>
      </div>

      {/* =============================================
          信任模块：为什么收费？
          ============================================= */}
      <div style={{
        background: 'white',
        border: '1px solid var(--color-border)',
        borderRadius: '12px',
        padding: 'clamp(20px, 4vw, 28px)',
        marginBottom: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <h3 style={{
          fontFamily: 'Georgia, serif',
          fontSize: '1.05rem',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '12px',
        }}>
          为什么收费？
        </h3>
        <div style={{
          fontSize: '0.88rem',
          color: 'var(--color-muted)',
          lineHeight: 1.8,
        }}>
          <p style={{ margin: '0 0 10px' }}>
            本系统需要持续<strong style={{ color: 'var(--color-text)' }}>维护服务器</strong>、
            更新<strong style={{ color: 'var(--color-text)' }}>历年录取数据</strong>，
            并不断优化算法以保证推荐的准确性。
          </p>
          <p style={{ margin: 0 }}>
            39 元是首批用户的<strong style={{ color: 'var(--color-text)' }}>体验价格</strong>，
            远低于线下咨询（3000-8000 元）和其他在线平台（200-400 元），
            希望让更多考生用得起数据驱动的志愿决策工具。
          </p>
        </div>
      </div>

      {/* =============================================
          免责声明
          ============================================= */}
      <div style={{
        borderLeft: '3px solid var(--color-border)',
        padding: '12px 16px',
        borderRadius: '0 6px 6px 0',
      }}>
        <p style={{
          fontSize: '0.78rem',
          color: 'var(--color-muted)',
          lineHeight: 1.6,
          margin: 0,
        }}>
          ⚠️ 本服务仅供志愿填报参考，不构成最终填报建议。最终填报结果请以江苏省教育考试院公布信息为准。
        </p>
      </div>

    </div>
  )
}
