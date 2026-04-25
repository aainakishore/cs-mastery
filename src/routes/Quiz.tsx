import { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { useHearts } from '../state/HeartsContext'
import { scoreQuiz } from '../lib/scorer'
import { QuizCard } from '../components/QuizCard'
import { GuideView } from '../components/GuideView'
import type { Question } from '../content/schema'

function sampleQuestions(questions: Question[], count: number, failedTags: string[] = []): Question[] {
  if (questions.length === 0) return []
  const n = Math.min(count, questions.length)
  // Bias toward failed-tag questions
  const failed = failedTags.length > 0
    ? questions.filter((q) => q.tags.some((t) => failedTags.includes(t)))
    : []
  const rest = questions.filter((q) => !failed.includes(q))
  const shuffleFailed = [...failed].sort(() => Math.random() - 0.5)
  const shuffleRest = [...rest].sort(() => Math.random() - 0.5)
  return [...shuffleFailed, ...shuffleRest].slice(0, n)
}

export function Quiz() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { markLearned, recordQuizResult, getTopicProgress } = useProgress()
  const { loseHeart, canAttemptQuiz } = useHearts()

  const topic = id ? getTopicById(id) : undefined

  const [retryTags, setRetryTags] = useState<string[]>([])
  const [answers, setAnswers] = useState<unknown[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [showRemediation, setShowRemediation] = useState(false)
  const [lastFailedTags, setLastFailedTags] = useState<string[]>([])

  const questions = useMemo(
    () => sampleQuestions(topic?.questions ?? [], 5, retryTags),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [topic?.id, retryTags.join(',')],
  )

  if (!topic) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Topic not found.
      </div>
    )
  }

  if (!canAttemptQuiz()) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-6 p-6 text-center">
        <div className="text-5xl">💔</div>
        <h2 className="text-2xl font-black text-white">No hearts left!</h2>
        <p className="text-slate-400">Hearts regenerate 1 every 30 minutes.</p>
        <button onClick={() => navigate(`/topic/${id}`)} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold">
          Back to Guide
        </button>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-4 p-6 text-center">
        <h2 className="text-xl font-bold text-white">No questions yet for this topic.</h2>
        <button onClick={() => navigate(`/topic/${id}`)} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold">
          Back
        </button>
      </div>
    )
  }

  if (showRemediation) {
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <div className="sticky top-0 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center gap-3">
          <button onClick={() => navigate(`/topic/${id}`)} className="text-slate-400 hover:text-white text-sm">← Guide</button>
          <span className="font-bold">Remediation — {topic.title}</span>
        </div>
        <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
          <div className="bg-red-900/30 border border-red-600 rounded-2xl p-4">
            <p className="text-red-300 font-semibold text-sm">
              Concepts to review: {lastFailedTags.join(', ')}
            </p>
          </div>
          <GuideView markdown={topic.guide} />
          <button
            onClick={() => {
              setRetryTags(lastFailedTags)
              setAnswers([])
              setCurrentIdx(0)
              setShowRemediation(false)
            }}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-bold"
          >
            Retry Quiz →
          </button>
        </div>
      </div>
    )
  }

  const handleAnswer = (answer: unknown) => {
    const newAnswers = [...answers, answer]
    setAnswers(newAnswers)

    if (currentIdx + 1 < questions.length) {
      setCurrentIdx((i) => i + 1)
    } else {
      // Grade
      const result = scoreQuiz(questions, newAnswers)
      recordQuizResult(topic.id, result.score, result.failedTags)

      if (result.passed) {
        const progress = getTopicProgress(topic.id)
        if (progress.status !== 'learned') markLearned(topic.id)
        navigate(`/result/${topic.id}`, { state: { passed: true, score: result.score } })
      } else {
        loseHeart()
        setLastFailedTags(result.failedTags)
        navigate(`/result/${topic.id}`, {
          state: { passed: false, score: result.score, failedTags: result.failedTags },
        })
      }
    }
  }

  const q = questions[currentIdx]
  const progressPct = ((currentIdx) / questions.length) * 100

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={() => navigate(`/topic/${id}`)} className="text-slate-400 hover:text-white text-sm">✕</button>
          <span className="text-slate-300 text-sm font-semibold flex-1">{topic.title}</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1.5">
          <div
            className="bg-indigo-500 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <div className="max-w-xl mx-auto px-4 py-8">
        <QuizCard
          question={q}
          index={currentIdx}
          total={questions.length}
          onAnswer={handleAnswer}
        />
      </div>
    </div>
  )
}

