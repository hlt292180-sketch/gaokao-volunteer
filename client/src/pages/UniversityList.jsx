import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getUniversities } from '../services/api'

export default function UniversityList() {
  const [list, setList] = useState([])
  const [keyword, setKeyword] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)

  const fetch = async (p = 1) => {
    try {
      const res = await getUniversities({ keyword, page: p, limit: 12 })
      setList(res.data); setTotal(res.pagination.total); setTotalPages(res.pagination.totalPages)
    } catch (e) { console.error(e) }
  }

  useEffect(() => { fetch(page) }, [page])

  const inputStyle = { borderColor: 'var(--color-border)', background: 'var(--color-bg)' }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '24px', color: 'var(--color-primary)' }}>
        🏫 院校查询
      </h1>
      <div className="flex gap-3 mb-6">
        <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)}
          placeholder="搜索院校名称..." className="flex-1 px-3 py-2 border rounded-lg focus:outline-none"
          style={inputStyle} />
        <button onClick={() => { setPage(1); fetch(1) }}
          className="px-4 py-2 rounded-lg"
          style={{ background: 'var(--color-primary)', color: 'white', fontWeight: 600 }}>
          搜索
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {list.map((u) => (
          <Link key={u.id} to={`/universities/${u.id}`}
            className="card block p-5" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="flex justify-between items-start mb-1">
              <h3 style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', fontSize: '1.05rem', color: 'var(--color-primary)' }}>
                {u.name}
              </h3>
              <div className="flex gap-1">
                {u.is_985 === 1 && <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#fef3c7', color: '#b45309' }}>985</span>}
                {u.is_211 === 1 && <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#dbeafe', color: 'var(--color-primary)' }}>211</span>}
                {u.is_double_first_class === 1 && <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#dcfce7', color: '#166534' }}>双一流</span>}
              </div>
            </div>
            <p className="text-sm" style={{ color: 'var(--color-muted)' }}>{u.city} · {u.type} · {u.level}</p>
            <p className="text-xs mt-2 line-clamp-2" style={{ color: 'var(--color-muted)', opacity: 0.7 }}>{u.intro}</p>
          </Link>
        ))}
      </div>
      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          {Array.from({ length: totalPages }, (_, i) => (
            <button key={i} onClick={() => setPage(i + 1)}
              className="px-3 py-1 rounded text-sm"
              style={{
                background: page === i + 1 ? 'var(--color-primary)' : 'white',
                color: page === i + 1 ? 'white' : 'var(--color-text)',
                border: page === i + 1 ? 'none' : '1px solid var(--color-border)',
              }}>
              {i + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
