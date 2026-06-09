import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { track } from '../services/track'

// ===== 模拟案例数据：冲稳保志愿方案示例 =====
const demoCases = [
  {
    id: 1,
    label: '案例一',
    profile: '物化生',
    score: 580,
    tiers: [
      { tag: '冲', uni: '南京邮电大学', detail: '通信工程 · 冲刺院校', color: '#dc2626' },
      { tag: '稳', uni: '江苏大学', detail: '计算机科学与技术 · 稳妥选择', color: 'var(--color-accent)' },
      { tag: '保', uni: '扬州大学', detail: '软件工程 · 保底志愿', color: '#16a34a' },
    ],
  },
  {
    id: 2,
    label: '案例二',
    profile: '历史类',
    score: 550,
    tiers: [
      { tag: '冲', uni: '南京师范大学', detail: '汉语言文学 · 冲刺院校', color: '#dc2626' },
      { tag: '稳', uni: '苏州大学', detail: '法学 · 稳妥选择', color: 'var(--color-accent)' },
      { tag: '保', uni: '江南大学', detail: '工商管理 · 保底志愿', color: '#16a34a' },
    ],
  },
  {
    id: 3,
    label: '案例三',
    profile: '物化生',
    score: 620,
    tiers: [
      { tag: '冲', uni: '东南大学', detail: '电子信息类 · 冲刺院校', color: '#dc2626' },
      { tag: '稳', uni: '南京航空航天大学', detail: '自动化 · 稳妥选择', color: 'var(--color-accent)' },
      { tag: '保', uni: '南京理工大学', detail: '机械工程 · 保底志愿', color: '#16a34a' },
    ],
  },
]

// ===== 为什么选择我们：四大价值点 =====
const features = [
  {
    icon: '📊',
    title: '分数换算位次',
    desc: '输入高考分数，一键查询全省位次排名。不只看分数，更看你在全省考生中的竞争位置。',
  },
  {
    icon: '🎯',
    title: '冲稳保智能推荐',
    desc: '基于近三年录取数据，科学计算冲刺、稳妥、保底三档志愿方案，有冲劲也有退路。',
  },
  {
    icon: '🔍',
    title: '院校专业查询',
    desc: '覆盖江苏省内本科院校，提供历年录取分数、专业详情、就业前景一站式查询。',
  },
  {
    icon: '🛡️',
    title: '志愿风险分析',
    desc: '智能检测志愿表梯度倒挂、保底不足等隐患，帮你避开滑档退档的坑。',
  },
]

export default function Home() {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const isLoggedIn = !!token
  const isPaid = user?.isPaid || user?.isAdmin

  // 📊 首页访问埋点
  useEffect(() => { track('page_view') }, [])

  // 未登录 → 注册页；已登录 → 方案生成页（免费用户有1次额度）
  const ctaLink = isLoggedIn ? '/plan/generate' : '/register'

  return (
    <div className="page-enter">

      {/* =============================================
          第一屏：Hero —— 5秒内让用户明白网站是干什么的
          ============================================= */}
      <section style={{ background: 'var(--color-primary)', padding: 'clamp(60px, 10vw, 100px) 0' }}>
        <div className="max-w-4xl mx-auto px-6">

          {/* 主标题 */}
          <h1 style={{
            fontFamily: 'Georgia, serif',
            color: 'white',
            fontSize: 'clamp(1.8rem, 5vw, 3.2rem)',
            fontWeight: 'bold',
            lineHeight: 1.35,
            textAlign: 'center',
            marginBottom: '16px',
            letterSpacing: '0.02em',
          }}>
            江苏高考志愿填报助手
          </h1>

          {/* 副标题 */}
          <p style={{
            color: 'rgba(255,255,255,0.75)',
            fontSize: 'clamp(0.95rem, 2.5vw, 1.2rem)',
            textAlign: 'center',
            maxWidth: '540px',
            margin: '0 auto 40px',
            lineHeight: 1.6,
          }}>
            输入高考分数，快速生成冲、稳、保三档志愿方案
          </p>

          {/* 四个功能要点 —— 横向排列 */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: 'clamp(12px, 3vw, 28px)',
            maxWidth: '620px',
            margin: '0 auto 40px',
          }}>
            {['江苏省专属数据', '历年录取分数分析', '位次智能匹配', '志愿方案推荐'].map((item) => (
              <span key={item} style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                color: 'rgba(255,255,255,0.82)',
                fontSize: 'clamp(0.8rem, 2vw, 0.92rem)',
                whiteSpace: 'nowrap',
              }}>
                <span style={{
                  display: 'inline-block',
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: 'var(--color-accent)',
                  flexShrink: 0,
                }} />
                {item}
              </span>
            ))}
          </div>

          {/* 主按钮 */}
          <div style={{ textAlign: 'center' }}>
            <Link
              to={ctaLink}
              style={{
                display: 'inline-block',
                background: 'var(--color-accent)',
                color: 'var(--color-primary)',
                fontWeight: 700,
                fontSize: 'clamp(0.95rem, 2.5vw, 1.1rem)',
                padding: '14px 48px',
                borderRadius: '8px',
                textDecoration: 'none',
                transition: 'background 0.2s, transform 0.1s',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              }}
            >
              立即生成方案
            </Link>
            {/* 根据登录状态给出不同的辅助说明 */}
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem', marginTop: '14px' }}>
              {!isLoggedIn
                ? '新用户注册即可免费生成 1 次完整方案'
                : isPaid
                  ? '付费用户 · 无限次使用全部功能'
                  : '免费用户可生成 1 次方案，升级后不限次数'}
            </p>
          </div>

          {/* 数据来源声明（Hero区域） */}
          <p style={{
            color: 'rgba(255,255,255,0.45)',
            fontSize: '0.72rem',
            textAlign: 'center',
            marginTop: '24px',
            lineHeight: 1.6,
          }}>
            数据来源：江苏省教育考试院官方一分一段表 + 院校专业组投档线。
            部分院校数据暂未公开，系统使用历史趋势模型进行预测，
            预测结果仅供参考，最终以官方录取结果为准。
          </p>
        </div>
      </section>

      {/* =============================================
          第二屏：为什么选择我们 —— 四卡片布局
          ============================================= */}
      <section style={{ padding: 'clamp(50px, 8vw, 80px) 0', background: 'white' }}>
        <div className="max-w-5xl mx-auto px-6">
          <h2 style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1.4rem, 3.5vw, 1.8rem)',
            fontWeight: 'bold',
            textAlign: 'center',
            marginBottom: '48px',
            color: 'var(--color-primary)',
          }}>
            为什么选择我们
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 'clamp(16px, 3vw, 24px)',
          }}>
            {features.map((f, i) => (
              <div key={i} className="card" style={{
                padding: 'clamp(24px, 4vw, 36px) clamp(20px, 3vw, 28px)',
                textAlign: 'center',
                cursor: 'default',
              }}>
                {/* 图标 */}
                <div style={{ fontSize: 'clamp(2rem, 4vw, 2.5rem)', marginBottom: '16px' }}>
                  {f.icon}
                </div>
                {/* 标题 */}
                <h3 style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: 'clamp(1rem, 2.5vw, 1.15rem)',
                  fontWeight: 'bold',
                  marginBottom: '12px',
                  color: 'var(--color-primary)',
                }}>
                  {f.title}
                </h3>
                {/* 描述 */}
                <p style={{
                  color: 'var(--color-muted)',
                  fontSize: 'clamp(0.85rem, 2vw, 0.92rem)',
                  lineHeight: 1.75,
                  maxWidth: '280px',
                  margin: '0 auto',
                }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* =============================================
          第三屏：真实案例展示 —— 杂志风卡片
          ============================================= */}
      <section style={{ padding: 'clamp(50px, 8vw, 80px) 0', background: 'var(--color-bg)' }}>
        <div className="max-w-5xl mx-auto px-6">
          <h2 style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1.4rem, 3.5vw, 1.8rem)',
            fontWeight: 'bold',
            textAlign: 'center',
            marginBottom: '10px',
            color: 'var(--color-primary)',
          }}>
            真实案例展示
          </h2>
          <p style={{
            textAlign: 'center',
            color: 'var(--color-muted)',
            fontSize: '0.88rem',
            marginBottom: '48px',
          }}>
            以下为基于历年录取数据的模拟志愿方案，仅供参考
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 'clamp(16px, 3vw, 24px)',
          }}>
            {demoCases.map((c) => (
              <div key={c.id} className="card" style={{ padding: '0', overflow: 'hidden' }}>

                {/* 案例顶部：选科 + 分数 */}
                <div style={{
                  background: 'var(--color-primary)',
                  color: 'white',
                  padding: '24px 24px 20px',
                }}>
                  <span style={{
                    fontSize: '0.7rem',
                    textTransform: 'uppercase',
                    letterSpacing: '3px',
                    opacity: 0.6,
                    fontFamily: 'Georgia, serif',
                  }}>
                    {c.label}
                  </span>
                  <div style={{
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: '10px',
                    marginTop: '6px',
                  }}>
                    <span style={{ fontSize: '0.85rem', opacity: 0.75 }}>{c.profile}</span>
                    <span style={{
                      fontFamily: 'Georgia, serif',
                      fontSize: '2.8rem',
                      fontWeight: 'bold',
                      lineHeight: 1,
                    }}>
                      {c.score}
                    </span>
                    <span style={{ fontSize: '0.8rem', opacity: 0.65 }}>分</span>
                  </div>
                </div>

                {/* 冲稳保三行 */}
                <div style={{ padding: '24px' }}>
                  {c.tiers.map((tier, j) => (
                    <div key={j} style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '14px',
                      paddingTop: j > 0 ? '18px' : '0',
                      marginTop: j > 0 ? '18px' : '0',
                      borderTop: j > 0 ? '1px solid var(--color-border)' : 'none',
                    }}>
                      {/* 冲/稳/保 标签 */}
                      <span style={{
                        display: 'inline-block',
                        background: tier.color,
                        color: 'white',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        padding: '3px 10px',
                        borderRadius: '4px',
                        flexShrink: 0,
                        marginTop: '2px',
                        minWidth: '32px',
                        textAlign: 'center',
                      }}>
                        {tier.tag}
                      </span>
                      {/* 院校名 + 说明 */}
                      <div>
                        <p style={{
                          fontFamily: 'Georgia, serif',
                          fontSize: '1.02rem',
                          fontWeight: 'bold',
                          color: 'var(--color-primary)',
                          marginBottom: '3px',
                        }}>
                          {tier.uni}
                        </p>
                        <p style={{
                          color: 'var(--color-muted)',
                          fontSize: '0.78rem',
                          lineHeight: 1.5,
                        }}>
                          {tier.detail}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* =============================================
          第四屏：数据来源说明 —— 增强信任感
          ============================================= */}
      <section style={{ padding: 'clamp(50px, 8vw, 80px) 0', background: 'white' }}>
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1.4rem, 3.5vw, 1.8rem)',
            fontWeight: 'bold',
            marginBottom: '28px',
            color: 'var(--color-primary)',
          }}>
            数据来源
          </h2>

          {/* 内容框 —— 居中、温暖的设计 */}
          <div style={{
            maxWidth: '540px',
            margin: '0 auto',
            padding: 'clamp(24px, 4vw, 36px)',
            border: '1px solid var(--color-border)',
            borderRadius: '12px',
            background: 'var(--color-bg)',
          }}>
            {/* 顶部图标 */}
            <div style={{ fontSize: '2rem', marginBottom: '16px', opacity: 0.4 }}>📋</div>

            <p style={{
              color: 'var(--color-text)',
              lineHeight: 1.85,
              fontSize: 'clamp(0.9rem, 2vw, 0.98rem)',
              margin: 0,
            }}>
              系统根据<strong style={{ color: 'var(--color-primary)' }}>江苏省历年录取数据</strong>、
              <strong style={{ color: 'var(--color-primary)' }}>位次信息</strong>及
              <strong style={{ color: 'var(--color-primary)' }}>院校招生情况</strong>进行分析，仅供志愿填报参考。
            </p>

            {/* 底部安全标识 */}
            <div style={{
              marginTop: '24px',
              paddingTop: '20px',
              borderTop: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              color: 'var(--color-muted)',
              fontSize: '0.83rem',
            }}>
              <span>🔒</span>
              <span>数据参考：江苏省教育考试院公开发布数据</span>
            </div>
          </div>
        </div>
      </section>

      {/* =============================================
          第五屏：免责声明 —— 合法合规，降低法律风险
          ============================================= */}
      <section style={{ padding: '0 0 clamp(40px, 6vw, 60px)', background: 'var(--color-bg)' }}>
        <div className="max-w-3xl mx-auto px-6">
          <div style={{
            borderLeft: '3px solid var(--color-accent)',
            padding: 'clamp(14px, 2vw, 20px) clamp(16px, 2vw, 24px)',
            background: 'white',
            borderRadius: '0 8px 8px 0',
          }}>
            <p style={{
              color: 'var(--color-muted)',
              fontSize: 'clamp(0.8rem, 2vw, 0.87rem)',
              lineHeight: 1.75,
              margin: 0,
            }}>
              <strong style={{ color: 'var(--color-text)' }}>⚠️ 数据来源与免责声明：</strong>
              本系统一分一段表数据来源于<strong style={{ color: 'var(--color-text)' }}>江苏省教育考试院</strong>官方发布，
              院校专业组投档线来源于<strong style={{ color: 'var(--color-text)' }}>中国教育在线</strong>和高校招生网。
              部分院校数据暂未公开，系统使用历史趋势模型进行预测，<strong style={{ color: '#dc2626' }}>预测结果仅供参考</strong>。
              最终录取结果以<strong style={{ color: 'var(--color-text)' }}>江苏省教育考试院</strong>官方公布为准。
              志愿填报关系个人前途，建议结合自身兴趣特长、家庭情况、院校官方招生章程等多方面信息综合判断。
            </p>
          </div>
        </div>
      </section>

    </div>
  )
}
