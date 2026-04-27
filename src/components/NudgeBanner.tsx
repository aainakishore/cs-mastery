import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { getLastStudied } from '../lib/storage'
import { getCurrentNudge } from '../lib/nudgeMessages'

const BANNER_DISMISSED_KEY = 'csm:bannerDismissed'
const MIN_HOURS_TO_SHOW = 4

function getHoursElapsed(): number {
  const lastStudied = getLastStudied()
  if (!lastStudied) return 72
  return (Date.now() - new Date(lastStudied).getTime()) / (1000 * 60 * 60)
}

export function NudgeBanner() {
  const [nudge, setNudge] = useState<{ title: string; body: string; emoji: string } | null>(null)

  useEffect(() => {
    const check = () => {
      const dismissed = sessionStorage.getItem(BANNER_DISMISSED_KEY)
      if (dismissed) { setNudge(null); return }
      const hours = getHoursElapsed()
      if (hours < MIN_HOURS_TO_SHOW) { setNudge(null); return }
      const n = getCurrentNudge(hours)
      setNudge(n)
    }
    check()
    const id = setInterval(check, 60_000)
    return () => clearInterval(id)
  }, [])

  const dismiss = () => {
    sessionStorage.setItem(BANNER_DISMISSED_KEY, '1')
    setNudge(null)
  }

  return (
    <AnimatePresence>
      {nudge && (
        <motion.div
          key="nudge-banner"
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="mx-4 mt-3 rounded-xl bg-orange-500/20 border border-orange-500/40 px-4 py-3 flex items-start gap-3 z-10"
        >
          <span className="text-2xl mt-0.5">{nudge.emoji}</span>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-orange-300 text-sm">{nudge.title}</p>
            <p className="text-orange-200/80 text-xs mt-0.5">{nudge.body}</p>
          </div>
          <button
            onClick={dismiss}
            className="text-orange-400 hover:text-white text-lg leading-none shrink-0 mt-0.5"
            aria-label="Dismiss"
          >
            ×
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
