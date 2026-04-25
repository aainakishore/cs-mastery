import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react'
import { getHearts, setHearts } from '../lib/storage'

const MAX_HEARTS = 5
const REGEN_MS = 30 * 60 * 1000 // 30 minutes

interface HeartsState {
  count: number
  lastRegen: string
  nextRegenMs: number // ms until next heart
}

interface HeartsContextValue extends HeartsState {
  loseHeart: () => void
  canAttemptQuiz: () => boolean
}

const HeartsContext = createContext<HeartsContextValue | null>(null)

function computeHearts(stored: { count: number; lastRegen: string }) {
  const elapsed = Date.now() - new Date(stored.lastRegen).getTime()
  const regenCount = Math.floor(elapsed / REGEN_MS)
  const newCount = Math.min(MAX_HEARTS, stored.count + regenCount)
  const remainder = elapsed % REGEN_MS
  const nextRegenMs = newCount < MAX_HEARTS ? REGEN_MS - remainder : Infinity
  const newLastRegen = new Date(
    new Date(stored.lastRegen).getTime() + regenCount * REGEN_MS,
  ).toISOString()
  return { count: newCount, lastRegen: newLastRegen, nextRegenMs }
}

export function HeartsProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<HeartsState>(() => {
    const stored = getHearts()
    return computeHearts(stored)
  })

  const saveAndCompute = useCallback((count: number, lastRegen: string) => {
    setHearts({ count, lastRegen })
    const computed = computeHearts({ count, lastRegen })
    setState(computed)
  }, [])

  // Regen tick
  useEffect(() => {
    const recalc = () => {
      setState((prev) => {
        const recomputed = computeHearts({ count: prev.count, lastRegen: prev.lastRegen })
        if (recomputed.count !== prev.count) {
          setHearts({ count: recomputed.count, lastRegen: recomputed.lastRegen })
        }
        return recomputed
      })
    }
    const interval = setInterval(recalc, 60000)
    document.addEventListener('visibilitychange', recalc)
    return () => {
      clearInterval(interval)
      document.removeEventListener('visibilitychange', recalc)
    }
  }, [])

  const loseHeart = useCallback(() => {
    setState((prev) => {
      const newCount = Math.max(0, prev.count - 1)
      const lastRegen = prev.count === MAX_HEARTS ? new Date().toISOString() : prev.lastRegen
      saveAndCompute(newCount, lastRegen)
      return { ...prev, count: newCount, lastRegen }
    })
  }, [saveAndCompute])

  const canAttemptQuiz = useCallback(() => state.count > 0, [state.count])

  return (
    <HeartsContext.Provider value={{ ...state, loseHeart, canAttemptQuiz }}>
      {children}
    </HeartsContext.Provider>
  )
}

export function useHearts(): HeartsContextValue {
  const ctx = useContext(HeartsContext)
  if (!ctx) throw new Error('useHearts must be used inside HeartsProvider')
  return ctx
}

