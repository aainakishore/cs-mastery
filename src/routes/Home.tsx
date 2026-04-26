import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Settings } from 'lucide-react'
import { topics, UNIT_LABELS, UNITS, getTopicsByUnit } from '../content'
import { useProgress } from '../state/ProgressContext'
import { PathNode } from '../components/PathNode'
import { XPBar } from '../components/XPBar'
import { StreakFlame } from '../components/StreakFlame'
import { HeartsBar } from '../components/HeartsBar'
import { DueTodayCard } from '../components/DueTodayCard'
import type { Unit } from '../content/schema'

const ACTIVE_KEY = 'csm:activeMs'
const BREAK_INTERVAL_MS = 20 * 60 * 1000

function useActiveMinutes() {
  const [pct, setPct] = useState(0)
  const [minutes, setMinutes] = useState(0)

  useEffect(() => {
    const tick = () => {
      try {
        const stored = parseInt(localStorage.getItem(ACTIVE_KEY) ?? '0', 10) || 0
        const m = Math.floor(stored / 60000)
        setMinutes(m)
        setPct(Math.min(100, (stored / BREAK_INTERVAL_MS) * 100))
      } catch { /* ignore */ }
    }
    tick()
    const id = setInterval(tick, 5000)
    return () => clearInterval(id)
  }, [])

  return { pct, minutes }
}

export function Home() {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()
  const { pct, minutes } = useActiveMinutes()

  const learnedCount = topics.filter((t) => getTopicProgress(t.id).status === 'learned').length
  const totalCount = topics.length

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center justify-between gap-4">
        <div className="font-black text-indigo-400 text-lg tracking-tight">CS Mastery</div>
        <div className="flex items-center gap-3">
          <XPBar />
          <StreakFlame />
          <HeartsBar />
          <button
            onClick={() => navigate('/settings')}
            className="text-slate-400 hover:text-white transition-colors p-1"
            aria-label="Settings"
          >
            <Settings size={20} />
          </button>
        </div>
      </div>

      {/* Active-time bar */}
      <div className="px-4 pt-3">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>👁 Active study time</span>
          <span>{minutes}m / 20m — break reminder</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5">
          <div
            className="h-1.5 rounded-full transition-all duration-1000"
            style={{
              width: `${pct}%`,
              background: pct > 80 ? '#f97316' : '#6366f1',
            }}
          />
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Progress summary */}
        <div className="bg-slate-900 rounded-2xl p-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-400">Overall progress</span>
            <span className="text-slate-300 font-bold">{learnedCount} / {totalCount} topics</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(learnedCount / totalCount) * 100}%` }}
            />
          </div>
        </div>

        <DueTodayCard />

        {/* Unit sections */}
        {UNITS.map((unit) => {
          const unitTopics = getTopicsByUnit(unit as Unit)
          const unitLearned = unitTopics.filter(
            (t) => getTopicProgress(t.id).status === 'learned',
          ).length

          return (
            <div key={unit} className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="bg-indigo-700 text-indigo-200 text-xs font-bold px-3 py-1 rounded-full">
                  Unit {unit}
                </div>
                <span className="text-slate-300 font-semibold text-sm">
                  {UNIT_LABELS[unit as Unit]}
                </span>
                <span className="text-slate-500 text-xs ml-auto">
                  {unitLearned}/{unitTopics.length}
                </span>
              </div>

              {/* Nodes in vertical zigzag */}
              <div className="relative pl-6">
                <div className="absolute left-9 top-0 bottom-0 w-px bg-slate-700" />
                <div className="space-y-6">
                  {unitTopics.map((topic, i) => {
                    const progress = getTopicProgress(topic.id)
                    const isEven = i % 2 === 0
                    return (
                      <div
                        key={topic.id}
                        className={`flex ${isEven ? 'justify-start' : 'justify-end pr-8'}`}
                      >
                        <PathNode
                          topic={topic}
                          status={progress.status}
                          onClick={() => navigate(`/topic/${topic.id}`)}
                        />
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )
        })}

        <div className="h-24" /> {/* bottom padding for nav */}
      </div>

      {/* Bottom nav */}
      <div className="fixed bottom-0 left-0 right-0 z-20 bg-slate-900/95 backdrop-blur border-t border-slate-800 flex justify-around items-center py-2 safe-area-pb">
        <button onClick={() => navigate('/')} className="flex flex-col items-center gap-0.5 text-indigo-400 text-xs font-semibold px-4 py-1">
          <span className="text-xl">🏠</span> Home
        </button>
        <button onClick={() => navigate('/review')} className="flex flex-col items-center gap-0.5 text-slate-400 hover:text-white text-xs px-4 py-1">
          <span className="text-xl">🔁</span> Review
        </button>
        <button onClick={() => navigate('/settings')} className="flex flex-col items-center gap-0.5 text-slate-400 hover:text-white text-xs px-4 py-1">
          <span className="text-xl">⚙️</span> Settings
        </button>
      </div>
    </div>
  )
}

