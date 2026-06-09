import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="mt-auto py-8 text-center text-xs" style={{ background: 'var(--color-primary)', color: 'rgba(255,255,255,0.6)' }}>
      <p style={{ fontFamily: 'Georgia, serif', color: 'white', fontSize: '1rem' }}>志愿导航</p>
      <p className="mt-1">高考志愿填报辅助系统</p>
      <div className="mt-3" style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
        <Link to="/about" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>关于我们</Link>
        <Link to="/disclaimer" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>免责声明</Link>
        <Link to="/contact" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>联系我们</Link>
      </div>
      <p className="mt-3">⚠ 本系统数据仅供参考，不构成最终填报建议</p>
    </footer>
  )
}
