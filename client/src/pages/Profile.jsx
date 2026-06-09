import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

export default function Profile() {
  const user = useAuthStore((s) => s.user)
  const isPaid = user?.isPaid || user?.isAdmin
  const isAdmin = user?.isAdmin

  return (
    <div className="page-enter" style={{
      maxWidth: '480px',
      margin: '0 auto',
      padding: 'clamp(24px, 5vw, 48px) 16px',
    }}>
      <h1 style={{
        fontFamily: 'Georgia, serif',
        fontSize: 'clamp(1.5rem, 4vw, 1.8rem)',
        fontWeight: 'bold',
        color: 'var(--color-primary)',
        marginBottom: '28px',
      }}>
        个人中心
      </h1>

      {/* ===== 基本信息卡片 ===== */}
      <div className="card" style={{ padding: 'clamp(20px, 3vw, 28px)', marginBottom: '20px' }}>
        <h3 style={{
          fontFamily: 'Georgia, serif',
          fontSize: '1.05rem',
          fontWeight: 'bold',
          color: 'var(--color-primary)',
          marginBottom: '16px',
        }}>
          基本信息
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.9rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--color-muted)' }}>手机号</span>
            <span style={{ fontWeight: 500 }}>{user?.phone}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--color-muted)' }}>昵称</span>
            <span style={{ fontWeight: 500 }}>{user?.nickname}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--color-muted)' }}>会员状态</span>
            <span style={{
              fontWeight: 600,
              color: isAdmin ? 'var(--color-primary)' : isPaid ? '#16a34a' : 'var(--color-muted)',
            }}>
              {isAdmin ? '🛠 管理员' : isPaid ? '🟣 付费会员' : '🆓 免费用户'}
            </span>
          </div>
        </div>
      </div>

      {/* ===== 免费用户：升级引导 ===== */}
      {!isPaid && (
        <div style={{
          background: 'var(--color-primary)',
          borderRadius: '12px',
          padding: 'clamp(20px, 4vw, 28px)',
          marginBottom: '20px',
          textAlign: 'center',
          color: 'white',
        }}>
          <p style={{
            fontFamily: 'Georgia, serif',
            fontSize: 'clamp(1.1rem, 3vw, 1.25rem)',
            fontWeight: 'bold',
            marginBottom: '8px',
          }}>
            升级付费版
          </p>
          <p style={{
            fontSize: '0.85rem',
            color: 'rgba(255,255,255,0.7)',
            marginBottom: '16px',
          }}>
            解锁完整冲稳保方案、专业匹配等全部功能
          </p>
          <Link
            to="/upgrade"
            style={{
              display: 'inline-block',
              background: 'var(--color-accent)',
              color: 'var(--color-primary)',
              fontWeight: 700,
              fontSize: '0.95rem',
              padding: '12px 36px',
              borderRadius: '8px',
              textDecoration: 'none',
              transition: 'background 0.15s',
            }}
          >
            立即升级
          </Link>
        </div>
      )}

      {/* ===== 快捷入口 ===== */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginBottom: '20px',
      }}>
        <Link to="/plans" className="card" style={{
          padding: 'clamp(14px, 2vw, 18px)',
          textAlign: 'center',
          textDecoration: 'none',
          color: 'var(--color-text)',
        }}>
          <span style={{ fontSize: '1.3rem', display: 'block', marginBottom: '6px' }}>📋</span>
          <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>我的方案</span>
        </Link>
        <Link to="/assessment" className="card" style={{
          padding: 'clamp(14px, 2vw, 18px)',
          textAlign: 'center',
          textDecoration: 'none',
          color: 'var(--color-text)',
        }}>
          <span style={{ fontSize: '1.3rem', display: 'block', marginBottom: '6px' }}>🧭</span>
          <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>兴趣测评</span>
        </Link>
        <Link to="/volunteer-check" className="card" style={{
          padding: 'clamp(14px, 2vw, 18px)',
          textAlign: 'center',
          textDecoration: 'none',
          color: 'var(--color-text)',
        }}>
          <span style={{ fontSize: '1.3rem', display: 'block', marginBottom: '6px' }}>🔍</span>
          <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>志愿体检</span>
        </Link>
        {isAdmin && (
          <Link to="/admin" className="card" style={{
            padding: 'clamp(14px, 2vw, 18px)',
            textAlign: 'center',
            textDecoration: 'none',
            color: 'var(--color-text)',
          }}>
            <span style={{ fontSize: '1.3rem', display: 'block', marginBottom: '6px' }}>🛠</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>管理后台</span>
          </Link>
        )}
      </div>
    </div>
  )
}
