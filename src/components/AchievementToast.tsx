import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Achievement } from '../lib/achievements'

interface Props {
  achievement: Achievement | null
  onDone: () => void
}

export function AchievementToast({ achievement, onDone }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!achievement) return
    setVisible(true)
    const t = setTimeout(() => { setVisible(false); setTimeout(onDone, 400) }, 3500)
    return () => clearTimeout(t)
  }, [achievement, onDone])

  return (
    <AnimatePresence>
      {visible && achievement && (
        <motion.div
          initial={{ y: -80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -80, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          className="fixed top-20 left-1/2 z-50 -translate-x-1/2 w-72"
        >
          <div className="bg-yellow-400 text-slate-900 rounded-2xl shadow-2xl px-5 py-4 flex items-center gap-4">
            <span className="text-4xl">{achievement.icon}</span>
            <div>
              <div className="text-xs font-bold uppercase tracking-widest text-yellow-800">Achievement!</div>
              <div className="font-black text-base">{achievement.title}</div>
              <div className="text-xs text-yellow-800">{achievement.desc}</div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

