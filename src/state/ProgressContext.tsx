import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react'
import type { TopicProgress, TopicStatus, QuizAttempt } from '../content/schema'
import type { ReviewRecord } from '../lib/scheduler'
import { createDefaultReview, updateSchedule } from '../lib/scheduler'
import {
  getProgress,
  setProgress,
  getXP,
  setXP,
  getStreak,
  setStreak,
  getReviewSchedules,
  setReviewSchedules,
  getFlashcardSchedules,
  setFlashcardSchedules,
  setLastStudied,
} from '../lib/storage'

function resetNudgeTierOnStudy() {
  try { sessionStorage.removeItem('csm:nudgeTierFired') } catch { /* ignore */ }
}
import { topics } from '../content'

interface ProgressState {
  topicProgress: TopicProgress[]
  xp: number
  streak: { count: number; lastDate: string }
  reviewSchedules: Record<string, ReviewRecord>
  flashcardSchedules: Record<string, ReviewRecord>
  streakBoosted: boolean
}

interface ProgressContextValue extends ProgressState {
  isUnlocked: (topicId: string) => boolean
  getTopicProgress: (topicId: string) => TopicProgress
  markLearned: (topicId: string) => void
  recordQuizResult: (topicId: string, score: number, failedTags: string[]) => void
  markProjectComplete: (topicId: string, score: number) => void
  updateReview: (topicId: string, score: number) => void
  updateFlashcard: (cardId: string, score: number) => void
  grantStreakBoost: () => void
}

const ProgressContext = createContext<ProgressContextValue | null>(null)

function defaultProgress(topicId: string): TopicProgress {
  return {
    topicId,
    status: 'locked',
    xpEarned: 0,
    projectComplete: false,
    quizHistory: [],
  }
}

function computeStatuses(progress: TopicProgress[]): TopicProgress[] {
  const learnedSet = new Set(
    progress.filter((p) => p.status === 'learned').map((p) => p.topicId),
  )

  // Sort all topics globally by order
  const sorted = [...topics].sort((a, b) => a.order - b.order)

  // Build per-unit sorted arrays
  const unitGroups: Record<number, typeof topics> = {}
  sorted.forEach((t) => {
    if (!unitGroups[t.unit]) unitGroups[t.unit] = []
    unitGroups[t.unit].push(t)
  })
  const units = Object.keys(unitGroups).map(Number).sort((a, b) => a - b)

  // Last topic id per unit (must be learned to unlock next unit's first topic)
  const lastOfUnit: Record<number, string> = {}
  units.forEach((u) => {
    const grp = unitGroups[u]
    lastOfUnit[u] = grp[grp.length - 1].id
  })

  return sorted.map((topic) => {
    const existing = progress.find((p) => p.topicId === topic.id) ?? defaultProgress(topic.id)
    if (existing.status === 'learned') return existing

    const unitTopics = unitGroups[topic.unit] ?? []
    const posInUnit = unitTopics.findIndex((t) => t.id === topic.id)
    units.indexOf(topic.unit);
    let available = false

    if (posInUnit === 0) {
      // First topic of EVERY unit is always available immediately
      available = true
    } else {
      // Strictly sequential: previous topic in unit must be learned
      const prevTopic = unitTopics[posInUnit - 1]
      available = learnedSet.has(prevTopic.id)
    }

    return { ...existing, status: available ? 'available' : ('locked' as TopicStatus) }
  })
}

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ProgressState>(() => {
    const raw = getProgress()
    const computed = computeStatuses(raw)
    return {
      topicProgress: computed,
      xp: getXP(),
      streak: getStreak(),
      reviewSchedules: getReviewSchedules(),
      flashcardSchedules: getFlashcardSchedules(),
      streakBoosted: false,
    }
  })

  const save = useCallback((next: ProgressState) => {
    setProgress(next.topicProgress)
    setXP(next.xp)
    setStreak(next.streak)
    setReviewSchedules(next.reviewSchedules)
    setFlashcardSchedules(next.flashcardSchedules)
  }, [])

  const isUnlocked = useCallback(
    (topicId: string) => {
      const p = state.topicProgress.find((x) => x.topicId === topicId)
      return p ? p.status !== 'locked' : false
    },
    [state.topicProgress],
  )

  const getTopicProgress = useCallback(
    (topicId: string) =>
      state.topicProgress.find((p) => p.topicId === topicId) ?? defaultProgress(topicId),
    [state.topicProgress],
  )

  const tryIncrementStreak = (streak: { count: number; lastDate: string }) => {
    const today = new Date().toDateString()
    if (streak.lastDate === today) return streak
    return { count: streak.count + 1, lastDate: today }
  }

  const markLearned = useCallback(
    (topicId: string) => {
      setState((prev) => {
        const updated = prev.topicProgress.map((p) =>
          p.topicId === topicId
            ? { ...p, status: 'learned' as TopicStatus, xpEarned: p.xpEarned + 20 }
            : p,
        )
        const recomputed = computeStatuses(updated)
        const newReview = { ...prev.reviewSchedules, [topicId]: createDefaultReview() }
        const newStreak = tryIncrementStreak(prev.streak)
        const next: ProgressState = {
          ...prev,
          topicProgress: recomputed,
          xp: prev.xp + 20,
          streak: newStreak,
          reviewSchedules: newReview,
        }
        save(next)
        setLastStudied(new Date().toISOString())
        resetNudgeTierOnStudy()
        return next
      })
    },
    [save],
  )

  const recordQuizResult = useCallback(
    (topicId: string, score: number, failedTags: string[]) => {
      setState((prev) => {
        const attempt: QuizAttempt = {
          date: new Date().toISOString(),
          score,
          failedTags,
        }
        const updated = prev.topicProgress.map((p) =>
          p.topicId === topicId
            ? { ...p, quizHistory: [...p.quizHistory, attempt] }
            : p,
        )
        const next = { ...prev, topicProgress: updated }
        save(next)
        return next
      })
    },
    [save],
  )

  const markProjectComplete = useCallback(
    (topicId: string, score: number) => {
      const xpGain = Math.round(score * 0.3) // up to 30 XP for project
      setState((prev) => {
        const updated = prev.topicProgress.map((p) =>
          p.topicId === topicId
            ? { ...p, projectComplete: true, xpEarned: p.xpEarned + xpGain }
            : p,
        )
        const next = { ...prev, topicProgress: updated, xp: prev.xp + xpGain }
        save(next)
        return next
      })
    },
    [save],
  )

  const updateReview = useCallback(
    (topicId: string, score: number) => {
      setState((prev) => {
        const existing =
          prev.reviewSchedules[topicId] ?? createDefaultReview()
        const updated = updateSchedule(existing, score)
        const newSchedules = { ...prev.reviewSchedules, [topicId]: updated }
        const newStreak =
          score >= 0.8 ? tryIncrementStreak(prev.streak) : prev.streak
        const next = { ...prev, reviewSchedules: newSchedules, streak: newStreak }
        save(next)
        return next
      })
    },
    [save],
  )

  const updateFlashcard = useCallback(
    (cardId: string, score: number) => {
      setState((prev) => {
        const existing = prev.flashcardSchedules[cardId] ?? createDefaultReview()
        const updated = updateSchedule(existing, score)
        const newSchedules = { ...prev.flashcardSchedules, [cardId]: updated }
        const next = { ...prev, flashcardSchedules: newSchedules }
        save(next)
        return next
      })
    },
    [save],
  )

  const grantStreakBoost = useCallback(() => {
    setState((prev) => {
      const next = { ...prev, streakBoosted: true }
      return next
    })
  }, [])

  // Sync from external import
  useEffect(() => {
    const handler = () => {
      const raw = getProgress()
      const computed = computeStatuses(raw)
      setState((prev) => ({
        ...prev,
        topicProgress: computed,
        xp: getXP(),
        streak: getStreak(),
        reviewSchedules: getReviewSchedules(),
        flashcardSchedules: getFlashcardSchedules(),
      }))
    }
    window.addEventListener('csm-import', handler)
    return () => window.removeEventListener('csm-import', handler)
  }, [])

  const value: ProgressContextValue = {
    ...state,
    isUnlocked,
    getTopicProgress,
    markLearned,
    recordQuizResult,
    markProjectComplete,
    updateReview,
    updateFlashcard,
    grantStreakBoost,
  }

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>
}

export function useProgress(): ProgressContextValue {
  const ctx = useContext(ProgressContext)
  if (!ctx) throw new Error('useProgress must be used inside ProgressProvider')
  return ctx
}

