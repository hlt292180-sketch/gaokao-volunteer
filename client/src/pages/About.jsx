// 关于我们页面
export default function About() {
  return (
    <div className="page-enter" style={{ maxWidth: '680px', margin: '0 auto', padding: 'clamp(24px, 5vw, 48px) 16px' }}>
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(1.6rem, 4vw, 2rem)', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '32px' }}>
        关于我们
      </h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* 项目介绍 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            项目介绍
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            江苏高考志愿填报助手是一款专门面向江苏省高考考生的志愿填报辅助工具。
            系统基于历年录取数据和智能分析算法，帮助考生科学、高效地完成志愿填报决策，
            减少信息不对称带来的填报失误。
          </p>
        </section>

        {/* 功能介绍 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '16px' }}>
            功能介绍
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {[
              { icon: '🧭', title: '性格测评', desc: '霍兰德职业兴趣测评，发现适合的专业方向' },
              { icon: '📊', title: '分数换算', desc: '输入高考分数，一键查询全省位次和历年等效分' },
              { icon: '🔍', title: '志愿体检', desc: '智能检测志愿表中的梯度倒挂、保底不足等风险' },
              { icon: '🤖', title: '智能推荐', desc: '基于冲稳保策略，自动生成个性化志愿方案' },
              { icon: '📈', title: '专业分析', desc: '提供专业就业画像、薪资预测和趋势分析' },
            ].map((f) => (
              <div key={f.title} style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>{f.icon}</span>
                <div>
                  <p style={{ fontWeight: 600, color: 'var(--color-text)', fontSize: '0.92rem', marginBottom: '2px' }}>
                    {f.title}
                  </p>
                  <p style={{ color: 'var(--color-muted)', fontSize: '0.85rem', margin: 0 }}>
                    {f.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 服务理念 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            服务理念
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            我们相信，每一个考生都值得拥有充分的信息和科学的工具来做出人生中最重要的决策之一。
            我们的目标是帮助考生减少信息差，让志愿填报不再"拍脑袋"，
            用数据和方法让每一分都发挥最大的价值。
          </p>
        </section>

        {/* 更新计划 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            更新计划
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            我们将持续补充和更新江苏省院校与专业数据，优化推荐算法，
            并逐步增加更多实用功能，为用户提供更加完善的志愿填报辅助服务。
            如有任何建议或反馈，欢迎通过「联系我们」页面与我们沟通。
          </p>
        </section>
      </div>
    </div>
  )
}
