import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getQuestions, submitAssessment, getLatestResult } from '../services/api'
import useAuthStore from '../store/authStore'

const dimNames = { R: '现实型', I: '研究型', A: '艺术型', S: '社会型', E: '企业型', C: '常规型' }
const dimColors = { R: 'bg-red-500', I: 'bg-blue-500', A: 'bg-purple-500', S: 'bg-green-500', E: 'bg-yellow-500', C: 'bg-teal-500' }

export default function Assessment() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [lastResult, setLastResult] = useState(null)     // 上次测评结果
  const [showRetest, setShowRetest] = useState(false)     // 是否显示重新测试的题目
  const user = useAuthStore((s) => s.user)
  const refreshUser = useAuthStore((s) => s.refreshUser)
  const isPaid = user?.isPaid || user?.isAdmin
  const freeLeft = Math.max(0, 1 - (user?.free_assessment_count || 0))

  useEffect(() => {
    (async () => {
      try {
        // 先查是否有历史结果
        const latestRes = await getLatestResult().catch(() => null)
        if (latestRes?.data) {
          setLastResult(latestRes.data)
        }
        // 同时加载题目备用
        const qRes = await getQuestions()
        setQuestions(qRes.data)
      } catch (e) { setError(e.message) }
      setLoading(false)
    })()
  }, [])

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) { setError('请回答所有题目'); return }
    if (!isPaid && freeLeft <= 0) { setError('免费测评次数已用完，请升级付费版'); return }
    setSubmitting(true); setError('')
    try {
      const dimScores = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 }
      const dimCounts = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 }
      questions.forEach((q) => {
        const score = answers[q.id] || 0
        dimScores[q.dimension] += score; dimCounts[q.dimension]++
      })
      Object.keys(dimScores).forEach((d) => { dimScores[d] = Math.round((dimScores[d] / (dimCounts[d] * 4)) * 100) })
      const r = await submitAssessment({ scores: dimScores })
      await refreshUser()
      // 把刚提交的结果作为最新结果展示
      const newRes = await getLatestResult()
      if (newRes?.data) setLastResult(newRes.data)
      setShowRetest(false)
    } catch (e) { setError(e.message) }
    setSubmitting(false)
  }

  if (loading) return <div className="max-w-2xl mx-auto px-6 py-8 text-center" style={{ color: 'var(--color-muted)' }}>加载中...</div>

  // ========== 有历史结果，且不是重新测试模式 → 展示结果 ==========
  if (lastResult && !showRetest) {
    const scores = JSON.parse(lastResult.result_scores)
    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1])

    return (
      <div className="page-enter max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-2">🧭 我的测评结果</h1>
        <p className="mb-6" style={{ color: 'var(--color-muted)' }}>霍兰德职业兴趣类型：<strong style={{ color: 'var(--color-primary)' }}>{lastResult.primary_type}</strong></p>

        <div className="card p-6 mb-6">
          <h3 className="font-bold mb-4">各维度得分</h3>
          <div className="space-y-3">
            {sorted.map(([dim, score]) => (
              <div key={dim}>
                <div className="flex justify-between text-sm mb-1"><span>{dimNames[dim]}（{dim}）</span><span className="font-semibold">{score} 分</span></div>
                <div className="w-full bg-gray-200 rounded-full h-2"><div className={`h-2 rounded-full ${dimColors[dim]}`} style={{ width: `${score}%` }}></div></div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-4">
          <button onClick={() => { setShowRetest(true); setAnswers({}); setError('') }}
            className="btn-cta">{isPaid || freeLeft > 0 ? '🔄 重新测试' : '🔄 重新测试（升级后不限次）'}</button>
          <Link to="/majors" className="px-6 py-3 rounded-lg border transition-colors hover:opacity-70" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)' }}>
            查看专业匹配 →
          </Link>
        </div>
      </div>
    )
  }

  // ========== 答题模式（首次或重新测试）==========
  return (
    <div className="page-enter max-w-2xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">🧭 霍兰德职业兴趣测评</h1>
      <p className="mb-2" style={{ color: 'var(--color-muted)' }}>共 {questions.length} 题，帮你发现职业兴趣倾向</p>
      {!isPaid && <p className="text-sm mb-6" style={{ color: 'var(--color-accent)' }}>⚠️ 免费用户仅可测评 1 次（剩余 {freeLeft} 次），付费不限</p>}
      {isPaid && <p className="text-sm mb-6" style={{ color: 'var(--color-muted)' }}>付费用户可无限次测评</p>}
      {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">{error}</div>}
      <div className="space-y-4">
        {questions.map((q, idx) => {
          const opts = JSON.parse(q.options)
          return (
            <div key={q.id} className="card p-4">
              <p className="text-sm font-medium mb-3">{idx + 1}. {q.question_text} <span className="text-xs" style={{ color: 'var(--color-muted)' }}>[{dimNames[q.dimension]}]</span></p>
              <div className="flex flex-wrap gap-2">
                {opts.map((opt, oi) => (
                  <button key={oi} onClick={() => setAnswers({ ...answers, [q.id]: 4 - oi })}
                    className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                      answers[q.id] === 4 - oi
                        ? 'text-white'
                        : 'bg-white hover:border-current'
                    }`}
                    style={answers[q.id] === 4 - oi
                      ? { background: 'var(--color-primary)', borderColor: 'var(--color-primary)' }
                      : { borderColor: 'var(--color-border)', color: 'var(--color-text)' }}
                  >{opt}</button>
                ))}
              </div>
            </div>
          )
        })}
      </div>
      <div className="flex gap-4 mt-6">
        <button onClick={handleSubmit} disabled={submitting}
          className="btn-cta flex-1">
          {submitting ? '提交中...' : '提交测评'}
        </button>
        {lastResult && (
          <button onClick={() => { setShowRetest(false); setError('') }}
            className="px-6 py-3 rounded-lg border transition-colors" style={{ borderColor: 'var(--color-border)', color: 'var(--color-muted)' }}>
            取消，返回结果
          </button>
        )}
      </div>
    </div>
  )
}
