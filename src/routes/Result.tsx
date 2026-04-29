import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { getNextTopic, getTopicById } from '../content'
import { Confetti } from '../components/Confetti'
import { Layout } from '../components/Layout'

interface LocationState {
  passed: boolean
  score: number
  failedTags?: string[]
}

export function Result() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const state = (location.state ?? {}) as LocationState
  const { passed = false, score = 0, failedTags = [] } = state

  const topic = id ? getTopicById(id) : undefined
  const next = id ? getNextTopic(id) : undefined
  const pct = Math.round(score * 100)

  return (
    <Layout title={passed ? 'You passed! 🎉' : 'Result'} back={`/topic/${id}`}>
      <Confetti active={passed} />
      <div className="flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-sm w-full space-y-6 mt-4">
          <div className="text-6xl">{passed ? '🎉' : '😅'}</div>
          <div>
            <h1 className="text-3xl font-black mb-1" style={{ color: 'var(--text-primary)' }}>{passed ? 'You passed! 🎉' : 'Not quite'}</h1>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{topic?.title}</p>
          </div>
          <div className={`rounded-2xl p-4 ${passed ? 'bg-emerald-900/40 border border-emerald-600' : 'bg-red-900/30 border border-red-600'}`}>
            <div className="text-4xl font-black text-white">{pct}%</div>
            <div className={`text-sm font-semibold ${passed ? 'text-emerald-300' : 'text-red-300'}`}>
              {passed ? '+20 XP earned! 🌟' : 'Need ≥ 80% to pass'}
            </div>
          </div>
          {passed ? (
            <div className="space-y-3">
              {next && (
                <button onClick={() => navigate(`/topic/${next.id}`)} className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-bold">
                  Next: {next.title} →
                </button>
              )}
              <button onClick={() => navigate(`/project/${id}`)} className="w-full bg-slate-700 hover:bg-slate-600 text-slate-200 py-3 rounded-xl font-semibold">
                🧠 Try Project
              </button>
              <button onClick={() => navigate('/')} className="w-full text-slate-400 hover:text-slate-200 py-2 text-sm">
                Back to Home
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {failedTags.length > 0 && (
                <div className="bg-slate-800 rounded-xl p-3 text-left">
                  <p className="text-slate-400 text-xs mb-1">Concepts to revisit:</p>
                  <div className="flex flex-wrap gap-1">
                    {failedTags.map((tag) => (
                      <span key={tag} className="bg-red-900/50 text-red-300 text-xs px-2 py-0.5 rounded-full">{tag}</span>
                    ))}
                  </div>
                </div>
              )}
              <button onClick={() => navigate(`/topic/${id}`)} className="w-full bg-slate-700 hover:bg-slate-600 text-slate-200 py-3 rounded-xl font-semibold">📖 Back to Guide</button>
              <button onClick={() => navigate(`/quiz/${id}`)} className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-bold">Retry Quiz →</button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
