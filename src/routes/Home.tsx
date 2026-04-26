import { useNavigate } from 'react-router-dom'
import { topics, UNIT_LABELS, UNITS, getTopicsByUnit } from '../content'
import { useProgress } from '../state/ProgressContext'
import { PathNode } from '../components/PathNode'
import { DueTodayCard } from '../components/DueTodayCard'
import { Layout } from '../components/Layout'
import type { Unit } from '../content/schema'

export function Home() {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()
  const learnedCount = topics.filter((t) => getTopicProgress(t.id).status === 'learned').length
  const totalCount = topics.length

  return (
    <Layout title="CS Mastery">
      <div className="max-w-lg mx-auto px-4 py-4 space-y-6">
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
          const unitLearned = unitTopics.filter((t) => getTopicProgress(t.id).status === 'learned').length

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

        <div className="h-4" />
      </div>
    </Layout>
  )
}

