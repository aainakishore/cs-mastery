import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye } from 'lucide-react'
import { Confetti } from './Confetti'

interface Props {
  onBoost: () => void
  onDismiss: () => void
}

export function BreakModal({ onBoost, onDismiss }: Props) {
  const [secondsLeft, setSecondsLeft] = useState(120)
  const [completed, setCompleted] = useState(false)

  useEffect(() => {
    if (secondsLeft <= 0) {
      setCompleted(true)
      onBoost()
      return
    }
    const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000)
    return () => clearTimeout(t)
  }, [secondsLeft, onBoost])

  const mins = Math.floor(secondsLeft / 60)
  const secs = secondsLeft % 60

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
      >
        <Confetti active={completed} />
        <motion.div
          initial={{ scale: 0.85, y: 30 }}
          animate={{ scale: 1, y: 0 }}
          className="bg-slate-800 border border-indigo-500 rounded-3xl p-8 max-w-sm w-full text-center shadow-2xl"
        >
          <div className="text-5xl mb-4">👁️</div>
          <h2 className="text-2xl font-black text-white mb-2">Take a Break!</h2>
          <p className="text-slate-300 text-sm mb-6">
            Look at something <strong>20 feet away</strong> for 2 minutes.
            Your eyes will thank you — and you'll get a <span className="text-amber-400 font-bold">streak boost</span>!
          </p>

          {!completed ? (
            <div className="mb-6">
              <div className="text-4xl font-black text-indigo-300 tabular-nums">
                {mins}:{String(secs).padStart(2, '0')}
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2 mt-3">
                <div
                  className="bg-indigo-500 h-2 rounded-full transition-all"
                  style={{ width: `${((120 - secondsLeft) / 120) * 100}%` }}
                />
              </div>
            </div>
          ) : (
            <div className="mb-6 text-emerald-400 font-bold text-lg">🎉 Streak boost earned!</div>
          )}

          <div className="flex gap-3">
            {!completed && (
              <button
                onClick={onDismiss}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-300 py-2 rounded-xl text-sm"
              >
                Dismiss
              </button>
            )}
            <button
              onClick={onDismiss}
              className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-xl font-bold flex items-center justify-center gap-2"
            >
              <Eye size={16} /> {completed ? 'Continue' : 'Skip break'}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

