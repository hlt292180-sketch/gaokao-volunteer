import { Link, useNavigate, useLocation } from 'react-router-dom'
import useAuthStore from '../store/authStore'

// 主导航
const navItems = [
  { path: '/score-convert', label: '分数换算' },
  { path: '/universities', label: '院校' },
  { path: '/majors', label: '专业' },
  { path: '/assessment', label: '测评' },
]
// 底部导航（关于/免责/联系）
const footerNavItems = [
  { path: '/about', label: '关于' },
  { path: '/disclaimer', label: '免责' },
  { path: '/contact', label: '联系' },
]

export default function Navbar() {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const nav = useNavigate()
  const location = useLocation()
  const isLoggedIn = !!token
  const isPaid = user?.isPaid || user?.isAdmin
  const isAdmin = user?.isAdmin

  // 判断当前页是否匹配某个导航路径
  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b" style={{ borderColor: 'var(--color-border)' }}>
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold tracking-tight" style={{ color: 'var(--color-primary)', fontFamily: 'Georgia, serif' }}>
          志愿导航
        </Link>

        <div className="flex items-center gap-4 text-sm">
          {navItems.map((item) => {
            const active = isActive(item.path)
            return (
              <Link key={item.path} to={item.path}
                className="transition-colors relative pb-1"
                style={{
                  color: active ? 'var(--color-accent)' : 'var(--color-text)',
                  fontWeight: active ? 600 : 400,
                }}
              >
                {item.label}
                {/* 当前页下方小横线 */}
                {active && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded"
                    style={{ background: 'var(--color-accent)' }} />
                )}
              </Link>
            )
          })}

          {/* 底部导航：关于/免责/联系（小字体+分隔） */}
          <span style={{ color: 'var(--color-border)', margin: '0 4px' }}>|</span>
          {footerNavItems.map((item) => (
            <Link key={item.path} to={item.path}
              className="transition-colors"
              style={{
                color: isActive(item.path) ? 'var(--color-accent)' : 'var(--color-muted)',
                fontSize: '0.8rem',
                fontWeight: isActive(item.path) ? 500 : 400,
              }}>
              {item.label}
            </Link>
          ))}

          {isLoggedIn && (
            <Link to="/my-favorites" className="transition-colors relative pb-1"
              style={{
                color: isActive('/my-favorites') ? 'var(--color-accent)' : 'var(--color-text)',
                fontWeight: isActive('/my-favorites') ? 600 : 400,
              }}>
              ⭐
            </Link>
          )}

          {isLoggedIn && isPaid && (
            <>
              <Link to="/plan/generate" className="transition-colors relative pb-1"
                style={{
                  color: isActive('/plan/generate') ? 'var(--color-accent)' : 'var(--color-primary)',
                  fontWeight: isActive('/plan/generate') ? 600 : 500,
                }}>
                生成方案
                {isActive('/plan/generate') && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded"
                    style={{ background: 'var(--color-accent)' }} />
                )}
              </Link>
              <Link to="/plans" className="transition-colors relative pb-1"
                style={{
                  color: isActive('/plans') ? 'var(--color-accent)' : 'var(--color-text)',
                  fontWeight: isActive('/plans') ? 600 : 400,
                }}>
                我的方案
                {isActive('/plans') && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded"
                    style={{ background: 'var(--color-accent)' }} />
                )}
              </Link>
            </>
          )}

          {isLoggedIn ? (
            <div className="flex items-center gap-2 ml-2">
              {isAdmin && <Link to="/admin" className="text-xs px-2 py-0.5 rounded" style={{ background: 'var(--color-primary)', color: 'white' }}>管理</Link>}
              {isPaid && <span className="text-xs px-2 py-0.5 rounded" style={{ background: '#fef3c7', color: 'var(--color-accent)' }}>VIP</span>}
              <Link to="/profile" className="transition-colors" style={{
                  color: isActive('/profile') ? 'var(--color-accent)' : 'var(--color-text)',
                  fontWeight: isActive('/profile') ? 600 : 400,
                }}>{user?.nickname || '我的'}</Link>
              <button onClick={() => { logout(); nav('/') }} className="text-xs hover:opacity-70" style={{ color: 'var(--color-muted)' }}>退出</button>
            </div>
          ) : (
            <Link to="/login" className="btn-cta text-sm">登录</Link>
          )}
        </div>
      </div>
    </nav>
  )
}
