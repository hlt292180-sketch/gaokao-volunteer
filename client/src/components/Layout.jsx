import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'

// 全局布局：导航 + 内容 + 页脚
export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--color-bg)' }}>
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
