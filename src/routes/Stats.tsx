import { useMemo } from 'react'
import { Layout } from '../components/Layout'
import { useProgress } from '../state/ProgressContext'
import { topics } from '../content'
import { getAchievements } from '../lib/achievements'

function getDailyActivity(): Record<string, number> {
  // Read quiz history across all topics
  return JSON.parse(localStorage.getItem('csm:dailyActivity') ?? '{}') as Record<string, number>
}

export function Stats() {
  const { topicProgress, xp, streak } = useProgress()

  const achievements = useMemo(() => getAchievements().filter(a => a.unlockedAt), [])
  const lockedAchievements = useMemo(() => getAchievements().filter(a => !a.unlockedAt), [])

  const learnedCount = topicProgress.filter(p => p.status === 'learned').length
  const passedQuizzes = topicProgress.reduce((s, p) => s + p.quizHistory.filter(q => q.score >= 0.8).length, 0)
  const projectsDone = topicProgress.filter(p => p.projectComplete).length

  // Per-unit progress
  const unitStats = [1,2,3,4,5,6,7].map(unit => {
    const unitTopics = topics.filter(t => t.unit === unit)
    const learned = unitTopics.filter(t => topicProgress.find(p => p.topicId === t.id)?.status === 'learned').length
    return { unit, learned, total: unitTopics.length }
  })

  // Per-topic accuracy (last quiz attempt)
  const topicAccuracy = topicProgress
    .filter(p => p.quizHistory.length > 0)
    .map(p => {
      const last5 = p.quizHistory.slice(-5)
      const avg = last5.reduce((s, q) => s + q.score, 0) / last5.length
      const topic = topics.find(t => t.id === p.topicId)
      return { topicId: p.topicId, title: topic?.title ?? p.topicId, avg, attempts: p.quizHistory.length }
    })
    .sort((a, b) => b.avg - a.avg)

  const daily = getDailyActivity()
  // Build last 14 days heatmap
  const heatmap = Array.from({ length: 14 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (13 - i))
    const key = d.toDateString()
    return { key, count: daily[key] ?? 0, label: d.toLocaleDateString('en', { weekday: 'short' }) }
  })
  const maxCount = Math.max(1, ...heatmap.map(h => h.count))

  return (
    <Layout title="Stats & Achievements" back="/">
      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">

        {/* Summary cards */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: 'Total XP', value: xp, icon: '⚡', color: 'text-indigo-300' },
            { label: 'Day Streak', value: streak.count, icon: '🔥', color: 'text-orange-300' },
            { label: 'Topics Learned', value: `${learnedCount}/37`, icon: '🎓', color: 'text-emerald-300' },
            { label: 'Quizzes Passed', value: passedQuizzes, icon: '📝', color: 'text-cyan-300' },
            { label: 'Projects Done', value: projectsDone, icon: '🏛️', color: 'text-pink-300' },
            { label: 'Achievements', value: achievements.length, icon: '🏆', color: 'text-yellow-300' },
          ].map(s => (
            <div key={s.label} className="bg-slate-800 rounded-2xl p-4 flex items-center gap-3">
              <span className="text-2xl">{s.icon}</span>
              <div>
                <div className={`text-xl font-black ${s.color}`}>{s.value}</div>
                <div className="text-xs text-slate-500">{s.label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* 14-day activity heatmap */}
        <div className="bg-slate-800 rounded-2xl p-4">
          <h3 className="font-bold text-slate-200 mb-3 text-sm">14-Day Activity</h3>
          <div className="flex gap-1.5 items-end">
            {heatmap.map(h => (
              <div key={h.key} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full rounded-sm transition-all"
                  style={{
                    height: `${Math.max(4, (h.count / maxCount) * 40)}px`,
                    background: h.count === 0 ? '#1e293b' : `rgba(99, 102, 241, ${0.3 + (h.count / maxCount) * 0.7})`,
                  }}
                />
                {heatmap.indexOf(h) % 3 === 0 && (
                  <span className="text-slate-600" style={{ fontSize: 8 }}>{h.label}</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Unit progress */}
        <div className="bg-slate-800 rounded-2xl p-4 space-y-3">
          <h3 className="font-bold text-slate-200 text-sm">Unit Progress</h3>
          {unitStats.map(({ unit, learned, total }) => (
            <div key={unit}>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Unit {unit}</span>
                <span>{learned}/{total}</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-1.5">
                <div
                  className="h-1.5 rounded-full bg-indigo-500 transition-all"
                  style={{ width: `${total ? (learned / total) * 100 : 0}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Per-topic accuracy */}
        {topicAccuracy.length > 0 && (
          <div className="bg-slate-800 rounded-2xl p-4 space-y-2">
            <h3 className="font-bold text-slate-200 text-sm">Per-Topic Quiz Accuracy (last 5)</h3>
            {topicAccuracy.slice(0, 10).map(t => (
              <div key={t.topicId} className="flex items-center gap-2">
                <span className="text-xs text-slate-400 truncate flex-1">{t.title}</span>
                <div className="w-20 bg-slate-700 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full transition-all"
                    style={{
                      width: `${t.avg * 100}%`,
                      background: t.avg >= 0.8 ? '#10b981' : t.avg >= 0.5 ? '#f59e0b' : '#ef4444',
                    }}
                  />
                </div>
                <span className="text-xs text-slate-400 w-8 text-right">{Math.round(t.avg * 100)}%</span>
              </div>
            ))}
          </div>
        )}

        {/* Achievements — unlocked */}
        {achievements.length > 0 && (
          <div className="bg-slate-800 rounded-2xl p-4 space-y-3">
            <h3 className="font-bold text-slate-200 text-sm">🏆 Earned Achievements</h3>
            <div className="grid grid-cols-2 gap-2">
              {achievements.map(a => (
                <div key={a.id} className="flex items-center gap-2 bg-yellow-900/30 border border-yellow-700/40 rounded-xl p-2">
                  <span className="text-xl">{a.icon}</span>
                  <div>
                    <div className="text-xs font-bold text-yellow-200">{a.title}</div>
                    <div className="text-xs text-yellow-700">{a.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Locked achievements */}
        {lockedAchievements.length > 0 && (
          <div className="bg-slate-800 rounded-2xl p-4 space-y-3">
            <h3 className="font-bold text-slate-200 text-sm">🔒 Locked Achievements</h3>
            <div className="grid grid-cols-2 gap-2">
              {lockedAchievements.map(a => (
                <div key={a.id} className="flex items-center gap-2 bg-slate-900/50 border border-slate-700 rounded-xl p-2 opacity-50">
                  <span className="text-xl grayscale">{a.icon}</span>
                  <div>
                    <div className="text-xs font-bold text-slate-400">{a.title}</div>
                    <div className="text-xs text-slate-600">{a.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

