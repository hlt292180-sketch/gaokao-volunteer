// 免责声明页面
export default function Disclaimer() {
  return (
    <div className="page-enter" style={{ maxWidth: '680px', margin: '0 auto', padding: 'clamp(24px, 5vw, 48px) 16px' }}>
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(1.6rem, 4vw, 2rem)', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '32px' }}>
        免责声明
      </h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* 服务性质 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            一、服务性质
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            本系统（江苏高考志愿填报助手）仅提供高考志愿填报辅助参考服务，不构成任何形式的填报建议或录取承诺。
            系统生成的冲稳保方案、专业匹配度评分、趋势预测等内容均为基于历史数据的统计分析结果，
            不代表对当年录取结果的预测或保证。
          </p>
        </section>

        {/* 数据说明 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            二、数据说明
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            本系统中的院校信息、录取数据、专业分析、就业画像、趋势预测等内容，
            来源于公开资料整理、历史数据分析及系统模型计算，仅供用户参考。
            系统不保证数据的完整性、准确性或时效性。实际录取数据请以
            <strong>江苏省教育考试院</strong>（http://www.jseea.cn/）官方公布信息为准。
          </p>
        </section>

        {/* 风险提示 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            三、风险提示
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            高考志愿填报结果受当年招生计划、报考人数、政策变化、院校录取规则等多重因素影响，
            存在较大不确定性。系统生成的推荐方案不保证用户被任何院校录取，
            用户应充分了解并接受志愿填报本身存在的风险。
          </p>
        </section>

        {/* 用户责任 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            四、用户责任
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            最终的高考志愿填报决策应由用户本人及其监护人独立完成。
            用户应结合自身兴趣特长、家庭情况、院校官方招生章程、江苏省教育考试院公布的官方数据
            等多方面信息综合判断。因使用本系统而产生的任何填报决策及其后果，由用户自行承担。
          </p>
        </section>

        {/* 法律声明 */}
        <section className="card" style={{ padding: 'clamp(20px, 3vw, 28px)' }}>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '12px' }}>
            五、法律声明
          </h2>
          <p style={{ color: 'var(--color-text)', fontSize: '0.92rem', lineHeight: 1.85 }}>
            使用本系统即视为您已阅读、理解并同意本免责声明的全部内容。
            如不同意本声明中的任何条款，请立即停止使用本系统。
            本免责声明的最终解释权归系统运营方所有。
          </p>
        </section>

        {/* 更新时间 */}
        <p style={{ textAlign: 'center', color: 'var(--color-muted)', fontSize: '0.8rem', marginTop: '8px' }}>
          更新日期：2026年6月
        </p>
      </div>
    </div>
  )
}
