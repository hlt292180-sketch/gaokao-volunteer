import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { track } from '../services/track'

export default function Register() {
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const [error, setError] = useState('')
  const registerAction = useAuthStore((s) => s.registerAction)
  const loading = useAuthStore((s) => s.loading)
  const nav = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    if (password.length < 6) { setError('密码至少6位'); return }
    const r = await registerAction(phone, password, nickname)
    if (r.success) { track('register'); nav('/') }
    else setError(r.message)
  }

  return (
    <div className="min-h-[calc(100vh-12rem)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 'bold', textAlign: 'center', marginBottom: '24px', color: 'var(--color-primary)' }}>
          注册志愿导航
        </h1>
        <form onSubmit={handleSubmit} className="card p-6" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg">{error}</div>}
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-muted)' }}>手机号</label>
            <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)}
              placeholder="请输入11位手机号" className="w-full px-3 py-2 border rounded-lg focus:outline-none"
              style={{ borderColor: 'var(--color-border)', background: 'var(--color-bg)' }}
              required />
          </div>
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-muted)' }}>昵称（选填）</label>
            <input type="text" value={nickname} onChange={(e) => setNickname(e.target.value)}
              placeholder="给自己取个名字" className="w-full px-3 py-2 border rounded-lg focus:outline-none"
              style={{ borderColor: 'var(--color-border)', background: 'var(--color-bg)' }} />
          </div>
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-muted)' }}>密码</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="至少6位" className="w-full px-3 py-2 border rounded-lg focus:outline-none"
              style={{ borderColor: 'var(--color-border)', background: 'var(--color-bg)' }}
              required />
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-2 rounded-lg disabled:opacity-50"
            style={{ background: loading ? '#9ca3af' : 'var(--color-primary)', color: 'white', fontWeight: 600 }}>
            {loading ? '注册中...' : '注册'}
          </button>
          <p className="text-center text-sm" style={{ color: 'var(--color-muted)' }}>
            已有账号？<Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 500 }}>立即登录</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
