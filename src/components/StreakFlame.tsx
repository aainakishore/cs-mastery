import { motion } from 'framer-motion'
import { Flame } from 'lucide-react'
import { useProgress } from '../state/ProgressContext'

export function StreakFlame() {
  const { streak } = useProgress()

  return (
    <motion.div
      className="flex items-center gap-1"
      animate={streak.count > 0 ? { scale: [1, 1.15, 1] } : {}}
      transition={{ duration: 0.5 }}
    >
      <Flame size={18} className={streak.count > 0 ? 'text-orange-400 fill-orange-400' : 'text-slate-600'} />
      <span className={`text-sm font-bold ${streak.count > 0 ? 'text-orange-300' : 'text-slate-500'}`}>
        {streak.count}
      </span>
    </motion.div>
  )
}

