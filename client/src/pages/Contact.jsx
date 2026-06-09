// 联系我们页面 — 联系方式通过环境变量配置
export default function Contact() {
  const contactInfo = [
    { label: '微信', value: import.meta.env.VITE_CONTACT_WECHAT || '待设置', placeholder: true },
    { label: 'QQ', value: import.meta.env.VITE_CONTACT_QQ || '待设置', placeholder: true },
    { label: '邮箱', value: import.meta.env.VITE_CONTACT_EMAIL || '待设置', placeholder: true },
  ]

  return (
    <div className="page-enter" style={{ maxWidth: '680px', margin: '0 auto', padding: 'clamp(24px, 5vw, 48px) 16px' }}>
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(1.6rem, 4vw, 2rem)', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '32px' }}>
        联系我们
      </h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* 用户反馈 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            用户反馈
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85, marginBottom: '16px' }}>
            我们非常重视每一位用户的反馈和建议。无论您在使用过程中遇到问题，
            还是有功能改进的想法，欢迎随时与我们联系。
          </p>
          <div style={{ background: 'var(--color-bg)', borderRadius: '8px', padding: '16px' }}>
            <p style={{ color: 'var(--color-muted)', fontSize: '0.85rem', margin: 0 }}>
              💡 建议反馈方式：通过下方任一联系方式发送消息，注明"志愿填报助手反馈"，
              我们会在 24 小时内回复。
            </p>
          </div>
        </section>

        {/* 联系方式 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '16px' }}>
            联系方式
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {contactInfo.map((item) => (
              <div key={item.label} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '14px 16px', borderRadius: '8px',
                background: 'var(--color-bg)',
              }}>
                <span style={{ fontWeight: 600, color: 'var(--color-text)', fontSize: '0.92rem' }}>
                  {item.label}
                </span>
                <span style={{
                  color: item.placeholder ? 'var(--color-muted)' : 'var(--color-primary)',
                  fontSize: '0.9rem', fontStyle: item.placeholder ? 'italic' : 'normal',
                }}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* 工作时间 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            工作时间
          </h2>
          <p style={{ color: 'var(--color-muted)', fontSize: '0.9rem', lineHeight: 1.8, margin: 0 }}>
            高考出分期间（6月24日-7月2日）：每日 8:00 - 22:00<br />
            其他时间：工作日 9:00 - 18:00
          </p>
        </section>
      </div>
    </div>
  )
}
