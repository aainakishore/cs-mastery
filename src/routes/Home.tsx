import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { topics, UNIT_LABELS, UNIT_DIFFICULTY, getTopicsByUnit } from '../content'
import { useProgress } from '../state/ProgressContext'
import { PathNode } from '../components/PathNode'
import { DueTodayCard } from '../components/DueTodayCard'
import { Layout } from '../components/Layout'
import { ChevronDown, ChevronUp } from 'lucide-react'
import type { Unit } from '../content/schema'

// ── Colours ───────────────────────────────────────────────────────────────────
const UNIT_COLORS: Record<number, string> = {
  1:'#6366f1', 2:'#f7c948', 3:'#3178c6', 4:'#61dafb', 5:'#dd0031',
  6:'#06b6d4', 7:'#8b5cf6', 8:'#14b8a6', 9:'#10b981', 10:'#f59e0b',
  11:'#ec4899', 12:'#ef4444', 13:'#0ea5e9', 14:'#a855f7',
  15:'#f97316', 16:'#64748b', 17:'#84cc16', 18:'#FF9900',
}
const DIFF_COLORS: Record<string, string> = {
  beginner:'#10b981', intermediate:'#f59e0b',
  advanced:'#ef4444', expert:'#a855f7', optional:'#64748b',
}

// Difficulty background tints for cards — removed; use CSS var instead
const DIFF_BG: Record<string, string> = {
  beginner:     'var(--bg-card)',
  intermediate: 'var(--bg-card)',
  advanced:     'var(--bg-card)',
  expert:       'var(--bg-card)',
  optional:     'var(--bg-card)',
}
// PathNode: w-20 outer (80px), w-14 button (56px), label ~28px => ~90px tall total
const NODE_H  = 90   // px — height of one PathNode including label
const CONN_H  = 56   // px — height of SVG connector
const SLOT_H  = NODE_H + CONN_H  // 146px per topic step

// ── Layout constants ──────────────────────────────────────────────────────────
const COLUMNS = [
  { label:'Beginner',     emoji:'🌱', diff:'beginner',     units:[1, 2] },
  { label:'Intermediate', emoji:'⚡', diff:'intermediate',  units:[3, 4, 5, 6, 7] },
  { label:'Advanced',     emoji:'🔥', diff:'advanced',      units:[8, 9, 10, 11, 12, 18] },
  { label:'Expert',       emoji:'💎', diff:'expert',        units:[13, 14] },
]
const OPTIONAL_UNITS = [15, 16, 17]

// ── Difficulty column layout ──────────────────────────────────────────────────
// Uses absolute positioning so x=25/x=75 in viewBox ALWAYS aligns with node centres
// (nodes are positioned at calc(25%-40px) and calc(75%-40px))
function CurvedArrow({ fromLeft, color }: { fromLeft: boolean; color: string }) {
  const sx = fromLeft ? 25 : 75
  const ex = fromLeft ? 75 : 25
  // Symmetric S-curve — looks good at any container width
  const d = `M ${sx} 0 C ${sx} ${CONN_H * 0.55}, ${ex} ${CONN_H * 0.45}, ${ex} ${CONN_H}`
  const ah = 7   // arrowhead size
  const spread = fromLeft ? 3.5 : -3.5
  return (
    <svg
      viewBox={`0 0 100 ${CONN_H}`}
      style={{ position:'absolute', left:0, width:'100%', height:CONN_H }}
      preserveAspectRatio="none"
    >
      <path d={d} fill="none" stroke={color} strokeWidth="2"
        strokeDasharray="5 4" strokeLinecap="round" opacity="0.6" />
      <polygon
        points={`${ex - spread} ${CONN_H - ah}, ${ex + spread} ${CONN_H - ah}, ${ex} ${CONN_H}`}
        fill={color} opacity="0.7"
      />
    </svg>
  )
}

// ── Zigzag path with absolute positioning ─────────────────────────────────────
function ZigzagPath({ unitTopics, color, onTopicClick }: {
  unitTopics: ReturnType<typeof getTopicsByUnit>
  color: string
  onTopicClick: (id: string) => void
}) {
  const { getTopicProgress } = useProgress()
  const n = unitTopics.length
  if (n === 0) return null
  // Total height: n nodes + (n-1) connectors
  const containerH = n * NODE_H + (n - 1) * CONN_H

  return (
    <div style={{ position:'relative', height: containerH, minHeight: containerH }}>
      {unitTopics.map((topic, idx) => {
        const progress = getTopicProgress(topic.id)
        const isLeft = idx % 2 === 0
        const nodeTop = idx * SLOT_H
        const connTop = nodeTop + NODE_H

        return (
          <div key={topic.id}>
            {/* Node — always at exactly 25% or 75% centre */}
            <div style={{
              position: 'absolute',
              top: nodeTop,
              left: isLeft ? 'calc(25% - 40px)' : 'calc(75% - 40px)',
              width: 80,
            }}>
              <PathNode
                topic={topic}
                status={progress.status}
                onClick={() => onTopicClick(topic.id)}
                color={color}
                progress={progress}
              />
            </div>

            {/* Connector to next node */}
            {idx < n - 1 && (
              <div style={{ position:'absolute', top: connTop, left:0, right:0 }}>
                <CurvedArrow fromLeft={isLeft} color={color} />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Single collapsible unit card ─────────────────────────────────────────────
function UnitCard({ unit, isOpen, onToggle }: {
  unit: number
  isOpen: boolean
  onToggle: () => void
}) {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()
  const color = UNIT_COLORS[unit] ?? '#6366f1'
  const diff = UNIT_DIFFICULTY[unit as Unit] ?? 'optional'
  const diffBg = DIFF_BG[diff] ?? '#0f172a'
  const unitTopics = getTopicsByUnit(unit as Unit).sort((a, b) => a.order - b.order)
  const learned = unitTopics.filter(t => getTopicProgress(t.id).status === 'learned').length
  const pct = unitTopics.length > 0 ? (learned / unitTopics.length) * 100 : 0

  return (
    <div
      className="rounded-2xl overflow-hidden mb-3"
      style={{ background: diffBg, border:`1.5px solid ${color}40` }}
    >
      {/* Header — always visible, acts as toggle */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-2 px-3 py-2.5 text-left rounded-none"
        style={{ background: isOpen ? color + '18' : 'transparent' }}
      >
        <span className="text-xs font-bold px-2 py-0.5 rounded-full shrink-0"
          style={{ background: color + '25', color }}>
          {unit}
        </span>
        <span className="font-semibold text-xs flex-1 leading-tight" style={{ color: 'var(--text-primary)' }}>
          {UNIT_LABELS[unit as Unit]}
        </span>
        <span className="text-xs shrink-0" style={{ color: 'var(--text-subtle)' }}>{learned}/{unitTopics.length}</span>
        {isOpen ? <ChevronUp size={14} style={{ color: 'var(--text-subtle)' }} /> : <ChevronDown size={14} style={{ color: 'var(--text-subtle)' }} />}
      </button>

      {/* Mini progress bar */}
      <div className="h-0.5 bg-slate-800">
        <div className="h-full transition-all duration-700" style={{ width:`${pct}%`, background: color }} />
      </div>

      {/* Collapsible zigzag body */}
      {isOpen && (
        <div className="px-3 pt-3 pb-4">
          <ZigzagPath
            unitTopics={unitTopics}
            color={color}
            onTopicClick={(id) => navigate(`/topic/${id}`)}
          />
        </div>
      )}
    </div>
  )
}

// ── Difficulty column header ──────────────────────────────────────────────────
function DiffHeader({ label, emoji, diff }: { label: string; emoji: string; diff: string }) {
  const col = DIFF_COLORS[diff] ?? '#64748b'
  return (
    <div className="flex items-center gap-1.5 mb-3 pb-2" style={{ borderBottom: '1px solid var(--border)' }}>
      <span className="text-base">{emoji}</span>
      <span className="text-xs font-bold uppercase tracking-widest" style={{ color: col }}>
        {label}
      </span>
    </div>
  )
}

// ── Suggestion banner ─────────────────────────────────────────────────────────
function SuggestionBanner({ recentUnit, onNavigate }: { recentUnit:number; onNavigate:(p:string)=>void }) {
  const { getTopicProgress } = useProgress()
  const diff = UNIT_DIFFICULTY[recentUnit as Unit] ?? 'intermediate'
  const isHard = ['advanced', 'expert'].includes(diff)
  const suggestion = topics.find(t => {
    if (getTopicProgress(t.id).status !== 'available') return false
    const d = UNIT_DIFFICULTY[t.unit as Unit] ?? 'intermediate'
    return isHard ? ['beginner','intermediate'].includes(d) : ['advanced','expert'].includes(d)
  })
  if (!suggestion) return null
  const color = UNIT_COLORS[suggestion.unit] ?? '#6366f1'
  return (
    <div className="rounded-2xl p-3 border flex items-center gap-3 cursor-pointer mb-4"
      style={{ background: color+'18', borderColor: color+'55' }}
      onClick={() => onNavigate(`/topic/${suggestion.id}`)}>
      <div className="text-xl">{isHard ? '😌' : '🔥'}</div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold mb-0.5" style={{ color }}>
          {isHard ? 'Balance it out — try something lighter' : 'Ready for a challenge?'}
        </p>
        <p className="text-slate-200 text-sm font-bold truncate">{suggestion.title}</p>
        <p className="text-slate-500 text-xs">{UNIT_LABELS[suggestion.unit as Unit]}</p>
      </div>
      <span className="text-slate-400">›</span>
    </div>
  )
}

// ── Main Home component ────────────────────────────────────────────────────────
export function Home() {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()

  // Default: first unit of each column open
  const [openUnits, setOpenUnits] = useState<Set<number>>(
    () => new Set([COLUMNS[0].units[0], COLUMNS[1].units[0], COLUMNS[2].units[0], COLUMNS[3].units[0]])
  )

  const toggle = useCallback((unit: number) => {
    setOpenUnits(prev => {
      const next = new Set(prev)
      next.has(unit) ? next.delete(unit) : next.add(unit)
      return next
    })
  }, [])

  const learnedCount = topics.filter(t => getTopicProgress(t.id).status === 'learned').length

  const lastLearnedTopic = [...topics]
    .filter(t => getTopicProgress(t.id).status === 'learned')
    .sort((a, b) => b.order - a.order)[0]

  return (
    <Layout title="CS Mastery">
      <div className="w-full px-3 py-4 lg:px-6">

        {/* Overall progress */}
        <div className="rounded-2xl p-4 mb-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          <div className="flex justify-between text-sm mb-2">
            <span style={{ color: 'var(--text-muted)' }}>Overall progress</span>
            <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{learnedCount} / {topics.length}</span>
          </div>
          <div className="w-full rounded-full h-2" style={{ background: 'var(--border)' }}>
            <div className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
              style={{ width:`${(learnedCount/topics.length)*100}%` }} />
          </div>
        </div>

        <DueTodayCard />

        {lastLearnedTopic && (
          <div className="mb-4">
            <SuggestionBanner recentUnit={lastLearnedTopic.unit} onNavigate={navigate} />
          </div>
        )}

        {/* ── DESKTOP: 4 difficulty columns ─────────────────────────────────── */}
        <div className="hidden lg:grid lg:grid-cols-4 gap-3 mb-4">
          {COLUMNS.map(col => (
            <div key={col.diff} className="min-w-0">
              <DiffHeader label={col.label} emoji={col.emoji} diff={col.diff} />
              {col.units.map(u => (
                <UnitCard key={u} unit={u} isOpen={openUnits.has(u)} onToggle={() => toggle(u)} />
              ))}
            </div>
          ))}
        </div>

        {/* ── DESKTOP: Optional row ─────────────────────────────────────────── */}
        <div className="hidden lg:block mb-6">
          <div className="flex items-center gap-2 mb-3 pb-2" style={{ borderBottom: '1px solid var(--border)' }}>
            <span className="text-base">📦</span>
            <span className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--text-subtle)' }}>Optional</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {OPTIONAL_UNITS.map(u => (
              <UnitCard key={u} unit={u} isOpen={openUnits.has(u)} onToggle={() => toggle(u)} />
            ))}
          </div>
        </div>

        {/* ── MOBILE: Single column ─────────────────────────────────────────── */}
        <div className="lg:hidden space-y-1">
          {[...COLUMNS, { label:'Optional', emoji:'📦', diff:'optional', units: OPTIONAL_UNITS }]
            .map(col => (
              <div key={col.diff} className="mb-4">
                <DiffHeader label={col.label} emoji={col.emoji} diff={col.diff} />
                {col.units.map(u => (
                  <UnitCard key={u} unit={u} isOpen={openUnits.has(u)} onToggle={() => toggle(u)} />
                ))}
              </div>
            ))
          }
        </div>

        <div className="h-8" />
      </div>
    </Layout>
  )
}
