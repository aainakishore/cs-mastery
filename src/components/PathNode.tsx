import { motion } from 'framer-motion'
import { Lock, Play, CheckCircle2 } from 'lucide-react'
import type { Topic, TopicStatus } from '../content/schema'

interface Props {
  topic: Topic
  status: TopicStatus
  onClick?: () => void
  isActive?: boolean
}

const statusConfig = {
  locked: {
    bg: 'bg-slate-700',
    border: 'border-slate-600',
    text: 'text-slate-400',
    icon: Lock,
  },
  available: {
    bg: 'bg-indigo-600',
    border: 'border-indigo-400',
    text: 'text-white',
    icon: Play,
  },
  learned: {
    bg: 'bg-emerald-600',
    border: 'border-emerald-400',
    text: 'text-white',
    icon: CheckCircle2,
  },
}

export function PathNode({ topic, status, onClick, isActive }: Props) {
  const cfg = statusConfig[status]
  const Icon = cfg.icon
  const clickable = status !== 'locked'

  return (
    <div className="flex flex-col items-center gap-2">
      <motion.button
        onClick={clickable ? onClick : undefined}
        disabled={!clickable}
        animate={
          status === 'available'
            ? { scale: [1, 1.06, 1], transition: { repeat: Infinity, duration: 2 } }
            : isActive
              ? { scale: 1.1 }
              : { scale: 1 }
        }
        whileTap={clickable ? { scale: 0.95 } : {}}
        className={`w-14 h-14 rounded-full border-2 flex items-center justify-center
          ${cfg.bg} ${cfg.border} ${cfg.text}
          ${clickable ? 'cursor-pointer shadow-lg hover:brightness-110' : 'cursor-not-allowed opacity-60'}
          transition-all duration-200`}
      >
        <Icon size={22} />
      </motion.button>
      <span
        className={`text-xs font-medium text-center max-w-[72px] leading-tight ${
          status === 'locked' ? 'text-slate-500' : 'text-slate-200'
        }`}
      >
        {topic.title}
      </span>
    </div>
  )
}

