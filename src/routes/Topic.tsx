import { useParams, useNavigate } from 'react-router-dom'
import { BookOpen, Brain, Layers } from 'lucide-react'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { useHearts } from '../state/HeartsContext'
import { GuideView } from '../components/GuideView'
import { Layout } from '../components/Layout'

export function Topic() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()
  const { canAttemptQuiz, count: hearts } = useHearts()

  const topic = id ? getTopicById(id) : undefined

  if (!topic) {
    return <Layout title="Not found" back="/"><div className="p-8 text-center text-slate-400">Topic not found.</div></Layout>
  }

  const progress = getTopicProgress(topic.id)
  const hasGuide = !topic.guide.startsWith('<!--')

  return (
    <Layout title={topic.title} back="/">
      <div className="max-w-2xl mx-auto px-4 py-4 space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-xs bg-indigo-800 text-indigo-200 px-2 py-0.5 rounded-full font-semibold">Unit {topic.unit}</span>
          {progress.status === 'learned' && (
            <span className="text-emerald-400 text-xs font-bold bg-emerald-900/40 px-2 py-1 rounded-full">✓ Learned</span>
          )}
        </div>
        <p className="text-slate-400 text-sm">{topic.summary}</p>
        {hasGuide ? (
          <GuideView markdown={topic.guide} />
        ) : (
          <div className="bg-slate-800 rounded-2xl p-8 text-center text-slate-400">
            <BookOpen size={32} className="mx-auto mb-3 opacity-40" />
            <p>Guide coming soon for this topic.</p>
          </div>
        )}
      </div>

      {/* Sticky CTA bar */}
      <div className="sticky bottom-16 bg-slate-950/95 backdrop-blur border-t border-slate-800 px-4 py-4">
        <div className="max-w-2xl mx-auto flex gap-3">
          <button onClick={() => navigate(`/flashcards/${topic.id}`)} className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-3 rounded-xl text-sm font-semibold">
            <Layers size={16} /> Cards
          </button>
          <button onClick={() => navigate(`/project/${topic.id}`)} className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-3 rounded-xl text-sm font-semibold">
            <Brain size={16} /> Project
          </button>
          <button
            onClick={() => navigate(`/quiz/${topic.id}`)}
            disabled={!canAttemptQuiz()}
            className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-xl font-bold"
          >
            {canAttemptQuiz() ? 'Start Quiz →' : `No hearts (${hearts}/5)`}
          </button>
        </div>
      </div>
    </Layout>
  )
}
