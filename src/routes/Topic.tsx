import { useParams, useNavigate } from 'react-router-dom'
import { BookOpen, Brain, Layers } from 'lucide-react'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { useHearts } from '../state/HeartsContext'
import { GuideView } from '../components/GuideView'

export function Topic() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()
  const { canAttemptQuiz, count: hearts } = useHearts()

  const topic = id ? getTopicById(id) : undefined

  if (!topic) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Topic not found.
      </div>
    )
  }

  const progress = getTopicProgress(topic.id)
  const hasGuide = !topic.guide.startsWith('<!--')

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate('/')} className="text-slate-400 hover:text-white text-sm">
          ← Back
        </button>
        <div className="flex-1">
          <div className="text-xs text-indigo-400 font-semibold">Unit {topic.unit}</div>
          <div className="font-bold text-white">{topic.title}</div>
        </div>
        {progress.status === 'learned' && (
          <span className="text-emerald-400 text-xs font-bold bg-emerald-900/40 px-2 py-1 rounded-full">
            ✓ Learned
          </span>
        )}
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Summary */}
        <p className="text-slate-400 text-sm">{topic.summary}</p>

        {/* Guide */}
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
      <div className="sticky bottom-0 bg-slate-950/95 backdrop-blur border-t border-slate-800 px-4 py-4">
        <div className="max-w-2xl mx-auto flex gap-3">
          <button
            onClick={() => navigate(`/flashcards/${topic.id}`)}
            className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-3 rounded-xl text-sm font-semibold transition-all"
          >
            <Layers size={16} /> Cards
          </button>
          <button
            onClick={() => navigate(`/project/${topic.id}`)}
            className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-3 rounded-xl text-sm font-semibold transition-all"
          >
            <Brain size={16} /> Project
          </button>
          <button
            onClick={() => navigate(`/quiz/${topic.id}`)}
            disabled={!canAttemptQuiz()}
            className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-xl font-bold transition-all"
          >
            {canAttemptQuiz() ? 'Start Quiz →' : `No hearts (${hearts}/5)`}
          </button>
        </div>
      </div>
    </div>
  )
}

