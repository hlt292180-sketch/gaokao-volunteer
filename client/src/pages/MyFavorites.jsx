import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getFavUniversities, getFavMajors, unfavUniversity, unfavMajor } from '../services/api'

export default function MyFavorites() {
  const [unis, setUnis] = useState([])
  const [majors, setMajors] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      try {
        const [uRes, mRes] = await Promise.all([
          getFavUniversities().catch(() => ({ data: [] })),
          getFavMajors().catch(() => ({ data: [] })),
        ])
        setUnis(uRes.data || [])
        setMajors(mRes.data || [])
      } catch {}
      setLoading(false)
    })()
  }, [])

  const handleUnfavUni = async (id) => {
    try { await unfavUniversity(id); setUnis((p) => p.filter((u) => u.university_id !== id)) } catch {}
  }
  const handleUnfavMajor = async (id) => {
    try { await unfavMajor(id); setMajors((p) => p.filter((m) => m.major_id !== id)) } catch {}
  }

  if (loading) return <div className="max-w-3xl mx-auto px-6 py-8 text-center" style={{ color: 'var(--color-muted)' }}>加载中...</div>

  return (
    <div className="page-enter" style={{ maxWidth: '680px', margin: '0 auto', padding: 'clamp(20px, 4vw, 40px) 16px' }}>
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(1.5rem, 4vw, 1.8rem)', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '28px' }}>
        ⭐ 我的收藏
      </h1>

      {/* 收藏院校 */}
      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '14px' }}>
          🏫 收藏院校 ({unis.length})
        </h2>
        {unis.length === 0 ? (
          <div className="card" style={{ padding: '24px', textAlign: 'center', color: 'var(--color-muted)', fontSize: '0.9rem' }}>
            暂无收藏院校，去「院校查询」逛逛吧
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {unis.map((u) => (
              <div key={u.id} className="card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Link to={'/universities/' + u.university_id} style={{ textDecoration: 'none', color: 'inherit', flex: 1 }}>
                  <p style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '2px' }}>
                    {u.name}
                  </p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--color-muted)' }}>{u.city} · {u.type} · {u.level}</p>
                </Link>
                <button onClick={() => handleUnfavUni(u.university_id)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem', color: 'var(--color-muted)', padding: '4px 8px' }}>
                  ⭐
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* 收藏专业 */}
      <section>
        <h2 style={{ fontFamily: 'Georgia, serif', fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '14px' }}>
          📚 收藏专业 ({majors.length})
        </h2>
        {majors.length === 0 ? (
          <div className="card" style={{ padding: '24px', textAlign: 'center', color: 'var(--color-muted)', fontSize: '0.9rem' }}>
            暂无收藏专业，去「专业查询」逛逛吧
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {majors.map((m) => (
              <div key={m.id} className="card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Link to={'/majors/' + m.major_id} style={{ textDecoration: 'none', color: 'inherit', flex: 1 }}>
                  <p style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', color: 'var(--color-primary)', marginBottom: '2px' }}>
                    {m.name}
                  </p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--color-muted)' }}>{m.category} · {m.degree}</p>
                </Link>
                <button onClick={() => handleUnfavMajor(m.major_id)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem', color: 'var(--color-muted)', padding: '4px 8px' }}>
                  ⭐
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
