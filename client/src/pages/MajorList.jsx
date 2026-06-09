import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMajors } from '../services/api'

const catColors = {
  '工学': { bg: '#dbeafe', text: 'var(--color-primary)' },
  '医学': { bg: '#fce7f3', text: '#9d174d' },
  '经济学': { bg: '#fef3c7', text: '#b45309' },
  '管理学': { bg: '#ccfbf1', text: '#115e59' },
  '法学': { bg: '#f3e8ff', text: '#6b21a8' },
  '文学': { bg: '#fce7f3', text: '#be185d' },
}

export default function MajorList() {
  const [list, setList] = useState([])
  const [keyword, setKeyword] = useState('')
  const [category, setCategory] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetch = async (p = 1) => {
    try {
      const res = await getMajors({ keyword, category, page: p, limit: 12 })
      setList(res.data); setTotalPages(res.pagination.totalPages)
    } catch (e) { console.error(e) }
  }

  useEffect(() => { fetch(page) }, [page])

  const inputStyle = { borderColor: 'var(--color-border)', background: 'var(--color-bg)' }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '24px', color: 'var(--color-primary)' }}>
        📚 专业查询
      </h1>
      <div className="flex gap-3 mb-6">
        <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)}
          placeholder="搜索专业..." className="flex-1 px-3 py-2 border rounded-lg focus:outline-none"
          style={inputStyle} />
        <select value={category} onChange={(e) => setCategory(e.target.value)}
          className="px-3 py-2 border rounded-lg" style={inputStyle}>
          <option value="">全部门类</option>
          {Object.keys(catColors).map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <button onClick={() => { setPage(1); fetch(1) }}
          className="px-4 py-2 rounded-lg"
          style={{ background: 'var(--color-primary)', color: 'white', fontWeight: 600 }}>
          搜索
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {list.map((m) => (
          <Link key={m.id} to={`/majors/${m.id}`}
            className="card block p-5" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="flex justify-between items-start mb-1">
              <h3 style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', fontSize: '1.05rem', color: 'var(--color-primary)' }}>
                {m.name}
              </h3>
              <span className="text-xs px-2 py-0.5 rounded" style={{
                background: (catColors[m.category] || { bg: 'var(--color-bg)', text: 'var(--color-muted)' }).bg,
                color: (catColors[m.category] || { bg: 'var(--color-bg)', text: 'var(--color-muted)' }).text,
              }}>
                {m.category}
              </span>
            </div>
            <p className="text-sm" style={{ color: 'var(--color-muted)' }}>{m.degree} · {m.duration}年</p>
            <p className="text-xs mt-2 line-clamp-2" style={{ color: 'var(--color-muted)', opacity: 0.7 }}>{m.intro}</p>
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
