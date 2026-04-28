import { useState, useMemo, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { useHearts } from '../state/HeartsContext'
import { scoreQuiz } from '../lib/scorer'
import { QuizCard } from '../components/QuizCard'
import { GuideView } from '../components/GuideView'
import { Layout } from '../components/Layout'
import { AchievementToast } from '../components/AchievementToast'
import { checkAchievements } from '../lib/achievements'
import { playCoin, playWrong, playFanfare } from '../lib/sounds'
import { haptic } from '../lib/haptics'
import { getSettings } from '../lib/storage'
import { topics } from '../content'
import type { Question } from '../content/schema'
import type { Achievement } from '../lib/achievements'

const TIMED_SECONDS = 30

function sampleQuestions(questions: Question[], count: number, failedTags: string[] = []): Question[] {
  if (questions.length === 0) return []
  const n = Math.min(count, questions.length)
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
  const { markLearned, recordQuizResult, getTopicProgress, topicProgress, xp, streak } = useProgress()
  const { loseHeart, canAttemptQuiz } = useHearts()

  const topic = id ? getTopicById(id) : undefined
  const settings = getSettings()

  const [retryTags, setRetryTags] = useState<string[]>([])
  const [answers, setAnswers] = useState<unknown[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [showRemediation, setShowRemediation] = useState(false)
  const [lastFailedTags, setLastFailedTags] = useState<string[]>([])
  const [timedMode, setTimedMode] = useState(false)
  const [timeLeft, setTimeLeft] = useState(TIMED_SECONDS)
  const [newAchievement, setNewAchievement] = useState<Achievement | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const questions = useMemo(
    () => sampleQuestions(topic?.questions ?? [], 5, retryTags),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [topic?.id, retryTags.join(',')],
  )

  // Timed mode countdown
  useEffect(() => {
    if (!timedMode) return
    setTimeLeft(TIMED_SECONDS)
    if (timerRef.current) clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          // Time's up — auto-submit wrong
          if (settings.sound) playWrong()
          haptic('error')
          handleAnswer(null)
          return TIMED_SECONDS
        }
        if (t <= 5 && settings.sound) { /* tick handled separately */ }
        return t - 1
      })
    }, 1000)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timedMode, currentIdx])

  if (!topic) return <Layout title="Quiz" back="/"><div className="p-8 text-center text-slate-400">Topic not found.</div></Layout>
  if (!canAttemptQuiz()) {
    return (
      <Layout title="No hearts" back={`/topic/${id}`}>
        <div className="flex flex-col items-center justify-center gap-6 p-10 text-center">
          <div className="text-5xl">💔</div>
          <h2 className="text-2xl font-black text-white">No hearts left!</h2>
          <p className="text-slate-400">Hearts regenerate 1 every 30 minutes.</p>
          <button onClick={() => navigate(`/topic/${id}`)} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold">Back to Guide</button>
        </div>
      </Layout>
    )
  }

  if (questions.length === 0 && !timedMode) {
    return (
      <Layout title="Quiz" back={`/topic/${id}`}>
        <div className="flex flex-col items-center justify-center gap-6 p-10 text-center">
          <div className="text-5xl">⏱</div>
          <h2 className="text-2xl font-black text-white">Choose mode</h2>
          <p className="text-slate-400">No questions available yet for this topic.</p>
          <button onClick={() => navigate(`/topic/${id}`)} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold">Back</button>
        </div>
      </Layout>
    )
  }

  // Mode select screen before first question
  if (answers.length === 0 && currentIdx === 0 && !showRemediation && questions.length > 0 && typeof timedMode === 'undefined') {
    // skip — fall through
  }

  if (showRemediation) {
    return (
      <Layout title={`Remediation — ${topic.title}`} back={`/topic/${id}`}>
        <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
          <div className="bg-red-900/30 border border-red-600 rounded-2xl p-4">
            <p className="text-red-300 font-semibold text-sm">Concepts to review: {lastFailedTags.join(', ')}</p>
          </div>
          <GuideView markdown={topic.guide} />
          <button
            onClick={() => { setRetryTags(lastFailedTags); setAnswers([]); setCurrentIdx(0); setShowRemediation(false) }}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-bold"
          >
            Retry Quiz →
          </button>
        </div>
      </Layout>
    )
  }

  const handleAnswer = (answer: unknown) => {
    if (timerRef.current) clearInterval(timerRef.current)

    const newAnswers = [...answers, answer]
    setAnswers(newAnswers)

    if (currentIdx + 1 < questions.length) {
      setCurrentIdx((i) => i + 1)
      if (timedMode) setTimeLeft(TIMED_SECONDS)
    } else {
      const result = scoreQuiz(questions, newAnswers)
      recordQuizResult(topic.id, result.score, result.failedTags)

      if (result.passed) {
        if (settings.sound) { playCoin(); setTimeout(playFanfare, 200) }
        haptic('heavy')
        const progress = getTopicProgress(topic.id)
        if (progress.status !== 'learned') markLearned(topic.id)

        // Check achievements
        const learnedCount = topicProgress.filter(p => p.status === 'learned').length + 1
        const passedCount = topicProgress.reduce((s, p) => s + p.quizHistory.filter(q => q.score >= 0.8).length, 0) + 1
        const unitProg: Record<number, {learned:number,total:number}> = {}
        ;[1,2,3,4,5,6,7].forEach(u => {
          const ut = topics.filter(t => t.unit === u)
          unitProg[u] = { learned: ut.filter(t => topicProgress.find(p => p.topicId === t.id)?.status === 'learned').length, total: ut.length }
        })
        const newAch = checkAchievements({
          learnedCount, quizPassCount: passedCount, streakCount: streak.count,
          xp: xp + 20, unitProgress: unitProg, projectCount: topicProgress.filter(p => p.projectComplete).length,
          flashcardCount: 0, perfectQuiz: result.score === 1.0,
        })
        if (newAch.length > 0) {
          setNewAchievement(newAch[0])
          if (settings.sound) playFanfare()
        }

        navigate(`/result/${topic.id}`, { state: { passed: true, score: result.score } })
      } else {
        if (settings.sound) playWrong()
        haptic('error')
        loseHeart()
        setLastFailedTags(result.failedTags)
        navigate(`/result/${topic.id}`, {
          state: { passed: false, score: result.score, failedTags: result.failedTags },
        })
      }
    }
  }

  const q = questions[currentIdx]
  const progressPct = (currentIdx / questions.length) * 100
  const timerColor = timeLeft <= 5 ? 'text-red-400' : timeLeft <= 10 ? 'text-orange-400' : 'text-slate-400'
  const timerBg = timeLeft <= 5 ? 'bg-red-500' : timeLeft <= 10 ? 'bg-orange-400' : 'bg-indigo-500'

  return (
    <Layout title={`Quiz: ${topic.title}`} back={`/topic/${id}`}>
      <AchievementToast achievement={newAchievement} onDone={() => setNewAchievement(null)} />

      {/* Quiz options bar */}
      <div className="px-4 pt-3 flex items-center justify-between gap-2">
        <div className="flex gap-2">
          <button
            onClick={() => setTimedMode(false)}
            className={`text-xs px-3 py-1 rounded-full font-semibold transition-colors ${!timedMode ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-400'}`}
          >Normal</button>
          <button
            onClick={() => setTimedMode(true)}
            className={`text-xs px-3 py-1 rounded-full font-semibold transition-colors ${timedMode ? 'bg-orange-600 text-white' : 'bg-slate-700 text-slate-400'}`}
          >⏱ Timed</button>
        </div>
        {timedMode && (
          <span className={`text-lg font-black tabular-nums ${timerColor}`}>{timeLeft}s</span>
        )}
        <span className="text-xs text-slate-500">Q {currentIdx + 1}/{questions.length}</span>
      </div>

      {/* Progress bar */}
      <div className="px-4 pt-2 pb-1">
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div className={`h-2 rounded-full transition-all duration-300 ${timerBg}`} style={{ width: `${progressPct}%` }} />
        </div>
        {timedMode && (
          <div className="w-full bg-slate-800 rounded-full h-1 mt-1">
            <div
              className={`h-1 rounded-full transition-all duration-1000 ${timerColor.replace('text-', 'bg-')}`}
              style={{ width: `${(timeLeft / TIMED_SECONDS) * 100}%` }}
            />
          </div>
        )}
      </div>

      <div className="max-w-xl mx-auto px-4 py-4">
        <QuizCard
          question={q}
          index={currentIdx}
          total={questions.length}
          onAnswer={(ans) => {
            haptic('light')
            handleAnswer(ans)
          }}
        />
      </div>
    </Layout>
  )
}

