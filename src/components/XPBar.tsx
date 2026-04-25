import { useProgress } from '../state/ProgressContext'

export function XPBar() {
  const { xp } = useProgress()
  const level = Math.floor(xp / 100) + 1
  const progress = xp % 100

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-bold text-indigo-300">Lv{level}</span>
      <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-500 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <span className="text-xs text-slate-400">{xp} XP</span>
    </div>
  )
}

