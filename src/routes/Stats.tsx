import { useMemo } from 'react'
import { Layout } from '../components/Layout'
import { useProgress } from '../state/ProgressContext'
import { topics } from '../content'
import { getAchievements } from '../lib/achievements'

function getDailyActivity(): Record<string, number> {
  return JSON.parse(localStorage.getItem('csm:dailyActivity') ?? '{}') as Record<string, number>
}

export function Stats() {
  const { topicProgress, xp, streak } = useProgress()

  const achievements = useMemo(() => getAchievements().filter(a => a.unlockedAt), [])
  const lockedAchievements = useMemo(() => getAchievements().filter(a => !a.unlockedAt), [])

  const learnedCount = topicProgress.filter(p => p.status === 'learned').length
  const passedQuizzes = topicProgress.reduce((s, p) => s + p.quizHistory.filter(q => q.score >= 0.8).length, 0)
  const projectsDone = topicProgress.filter(p => p.projectComplete).length

  const topicAccuracy = topicProgress
    .filter(p => p.quizHistory.length > 0)
    .map(p => {
      const last5 = p.quizHistory.slice(-5)
      const avg = last5.reduce((s, q) => s + q.score, 0) / last5.length
      const topic = topics.find(t => t.id === p.topicId)
      return { topicId: p.topicId, title: topic?.title ?? p.topicId, avg }
    })
    .sort((a, b) => b.avg - a.avg)

  const daily = getDailyActivity()
  const heatmap = Array.from({ length: 14 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (13 - i))
    const key = d.toDateString()
    return { key, count: daily[key] ?? 0, label: d.toLocaleDateString('en', { weekday: 'short' }) }
  })
  const maxCount = Math.max(1, ...heatmap.map(h => h.count))

  const CARD_STYLE = { background: 'var(--bg-card)', border: '1px solid var(--border)' }

  return (
    <Layout title="Stats & Achievements" back="/">
      <div className="w-full px-4 py-6 lg:px-8">
        <div className="max-w-5xl mx-auto space-y-6">

          {/* Summary cards */}
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { label: 'Total XP',       value: xp,                          icon: '⚡', color: '#6366f1' },
              { label: 'Day Streak',     value: streak.count,                icon: '🔥', color: '#f97316' },
              { label: 'Topics Learned', value: `${learnedCount}/${topics.length}`, icon: '🎓', color: '#10b981' },
              { label: 'Quizzes Passed', value: passedQuizzes,               icon: '📝', color: '#06b6d4' },
              { label: 'Projects Done',  value: projectsDone,                icon: '🏛️', color: '#ec4899' },
              { label: 'Achievements',   value: achievements.length,         icon: '🏆', color: '#f7c948' },
            ].map(s => (
              <div key={s.label} className="rounded-2xl p-4 flex items-center gap-3" style={CARD_STYLE}>
                <span className="text-2xl">{s.icon}</span>
                <div>
                  <div className="text-xl font-black" style={{ color: s.color }}>{s.value}</div>
                  <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
                </div>
              </div>
            ))}
          </div>

          {/* 14-day heatmap */}
          <div className="rounded-2xl p-4" style={CARD_STYLE}>
            <h3 className="font-bold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>14-Day Activity</h3>
            <div className="flex gap-1.5 items-end">
              {heatmap.map((h, idx) => (
                <div key={h.key} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full rounded-sm transition-all" style={{
                    height: `${Math.max(4, (h.count / maxCount) * 40)}px`,
                    background: h.count === 0 ? 'var(--border)' : `rgba(99,102,241,${0.3 + (h.count / maxCount) * 0.7})`,
                  }} />
                  {idx % 3 === 0 && (
                    <span style={{ fontSize: 8, color: 'var(--text-subtle)' }}>{h.label}</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Unit progress + quiz accuracy */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="rounded-2xl p-4 space-y-3" style={CARD_STYLE}>
              <h3 className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>Unit Progress</h3>
              {[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18].map(unit => {
                const ut = topics.filter(t => t.unit === unit)
                if (!ut.length) return null
                const learned = ut.filter(t => topicProgress.find(p => p.topicId === t.id)?.status === 'learned').length
                return (
                  <div key={unit}>
                    <div className="flex justify-between text-xs mb-1" style={{ color: 'var(--text-muted)' }}>
                      <span>Unit {unit}</span><span>{learned}/{ut.length}</span>
                    </div>
                    <div className="w-full rounded-full h-1.5" style={{ background: 'var(--border)' }}>
                      <div className="h-1.5 rounded-full bg-indigo-500 transition-all"
                        style={{ width: `${ut.length ? (learned / ut.length) * 100 : 0}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>

            {topicAccuracy.length > 0 && (
              <div className="rounded-2xl p-4 space-y-2" style={CARD_STYLE}>
                <h3 className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>Quiz Accuracy (last 5)</h3>
                {topicAccuracy.slice(0, 14).map(t => (
                  <div key={t.topicId} className="flex items-center gap-2">
                    <span className="text-xs truncate flex-1" style={{ color: 'var(--text-muted)' }}>{t.title}</span>
                    <div className="w-24 rounded-full h-1.5" style={{ background: 'var(--border)' }}>
                      <div className="h-1.5 rounded-full transition-all"
                        style={{ width: `${t.avg * 100}%`, background: t.avg >= 0.8 ? '#10b981' : t.avg >= 0.5 ? '#f59e0b' : '#ef4444' }} />
                    </div>
                    <span className="text-xs w-8 text-right" style={{ color: 'var(--text-muted)' }}>{Math.round(t.avg * 100)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Earned achievements */}
          {achievements.length > 0 && (
            <div className="rounded-2xl p-4 space-y-3" style={CARD_STYLE}>
              <h3 className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>🏆 Earned Achievements</h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
                {achievements.map(a => (
                  <div key={a.id} className="flex items-center gap-2 rounded-xl p-2"
                    style={{ background: '#f7c94818', border: '1px solid #f7c94840' }}>
                    <span className="text-xl">{a.icon}</span>
                    <div>
                      <div className="text-xs font-bold" style={{ color: '#f7c948' }}>{a.title}</div>
                      <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{a.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Locked achievements */}
          {lockedAchievements.length > 0 && (
            <div className="rounded-2xl p-4 space-y-3" style={CARD_STYLE}>
              <h3 className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>🔒 Locked Achievements</h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
                {lockedAchievements.map(a => (
                  <div key={a.id} className="flex items-center gap-2 rounded-xl p-2 opacity-50"
                    style={{ background: 'var(--border)', border: '1px solid var(--border)' }}>
                    <span className="text-xl grayscale">{a.icon}</span>
                    <div>
                      <div className="text-xs font-bold" style={{ color: 'var(--text-muted)' }}>{a.title}</div>
                      <div className="text-xs" style={{ color: 'var(--text-subtle)' }}>{a.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </Layout>
  )
}
