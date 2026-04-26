import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { topics } from '../content'
import { useProgress } from '../state/ProgressContext'

interface Node {
  id: string
  title: string
  unit: number
  x: number
  y: number
  status: 'locked' | 'available' | 'learned'
  prereqs: string[]
}

const UNIT_COLORS: Record<number, string> = {
  1: '#6366f1', // indigo - Foundations
  2: '#8b5cf6', // purple - AI Primer
  3: '#06b6d4', // cyan - Networking
  4: '#10b981', // emerald - Scaling
  5: '#f59e0b', // amber - Cloud
  6: '#ec4899', // pink - AI Advanced
  7: '#64748b', // slate - Tooling
}

const UNIT_LABELS: Record<number, string> = {
  1: 'Foundations', 2: 'AI Primer', 3: 'Networking',
  4: 'Scaling', 5: 'Cloud', 6: 'AI Advanced', 7: 'Tooling',
}

// Layout: arrange topics in a force-directed-style grid per unit
function computeLayout(): Node[] {
  const unitGroups: Record<number, typeof topics> = {}
  topics.forEach(t => {
    if (!unitGroups[t.unit]) unitGroups[t.unit] = []
    unitGroups[t.unit].push(t)
  })

  const nodes: Node[] = []
  const unitList = [1, 2, 3, 4, 5, 6, 7]
  const W = 900, H = 700
  const cx = W / 2, cy = H / 2

  // Place units in a circle, topics in a sub-circle around each unit center
  unitList.forEach((unit, ui) => {
    const angle = (ui / unitList.length) * 2 * Math.PI - Math.PI / 2
    const ux = cx + Math.cos(angle) * 280
    const uy = cy + Math.sin(angle) * 220
    const unitTopics = unitGroups[unit] || []
    unitTopics.forEach((t, ti) => {
      const tAngle = (ti / Math.max(unitTopics.length, 1)) * 2 * Math.PI
      const r = unitTopics.length <= 1 ? 0 : 55 + unitTopics.length * 4
      const tx = ux + Math.cos(tAngle) * r
      const ty = uy + Math.sin(tAngle) * r
      nodes.push({ id: t.id, title: t.title, unit: t.unit, x: tx, y: ty, status: 'available', prereqs: t.prereqs })
    })
  })
  return nodes
}

export function MindMap() {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()

  const nodes = useMemo(() => {
    const raw = computeLayout()
    return raw.map(n => ({
      ...n,
      status: getTopicProgress(n.id).status as 'locked' | 'available' | 'learned',
    }))
  }, [getTopicProgress])

  const W = 900, H = 700

  // Build edges from prereqs
  const edges: {x1:number,y1:number,x2:number,y2:number,key:string}[] = []
  nodes.forEach(n => {
    n.prereqs.forEach(preId => {
      const pre = nodes.find(p => p.id === preId)
      if (pre) edges.push({ x1: pre.x, y1: pre.y, x2: n.x, y2: n.y, key: `${preId}->${n.id}` })
    })
  })

  // Unit cluster circles
  const unitCenters: Record<number, {x:number,y:number}> = {}
  nodes.forEach(n => {
    if (!unitCenters[n.unit]) {
      const unitNodes = nodes.filter(nn => nn.unit === n.unit)
      const avgX = unitNodes.reduce((s, nn) => s + nn.x, 0) / unitNodes.length
      const avgY = unitNodes.reduce((s, nn) => s + nn.y, 0) / unitNodes.length
      unitCenters[n.unit] = { x: avgX, y: avgY }
    }
  })

  return (
    <div className="w-full overflow-auto">
      <div className="min-w-[600px]">
        {/* Legend */}
        <div className="flex flex-wrap gap-3 px-4 py-3 text-xs">
          {Object.entries(UNIT_LABELS).map(([unit, label]) => (
            <div key={unit} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ background: UNIT_COLORS[Number(unit)] }} />
              <span className="text-slate-400">{label}</span>
            </div>
          ))}
        </div>

        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full"
          style={{ maxHeight: '70vh' }}
        >
          {/* Unit background clusters */}
          {[1,2,3,4,5,6,7].map(unit => {
            const center = unitCenters[unit]
            if (!center) return null
            const color = UNIT_COLORS[unit]
            return (
              <g key={unit}>
                <circle
                  cx={center.x} cy={center.y} r={85}
                  fill={color} fillOpacity={0.07}
                  stroke={color} strokeOpacity={0.2} strokeWidth={1}
                />
                <text x={center.x} y={center.y - 70} textAnchor="middle"
                  fill={color} fontSize={11} fontWeight="bold" opacity={0.8}>
                  {UNIT_LABELS[unit]}
                </text>
              </g>
            )
          })}

          {/* Edges */}
          {edges.map(e => (
            <line key={e.key}
              x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
              stroke="#334155" strokeWidth={1} strokeOpacity={0.4}
              strokeDasharray="3 3"
            />
          ))}

          {/* Nodes */}
          {nodes.map(n => {
            const color = UNIT_COLORS[n.unit]
            const learned = n.status === 'learned'
            const r = 18
            return (
              <g key={n.id} style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/topic/${n.id}`)}>
                <circle
                  cx={n.x} cy={n.y} r={r}
                  fill={learned ? color : '#1e293b'}
                  stroke={color}
                  strokeWidth={learned ? 2 : 1.5}
                  opacity={n.status === 'locked' ? 0.35 : 1}
                />
                {learned && (
                  <text x={n.x} y={n.y + 5} textAnchor="middle"
                    fill="white" fontSize={14} fontWeight="bold">✓</text>
                )}
                <text x={n.x} y={n.y + r + 14} textAnchor="middle"
                  fill={color} fontSize={9} opacity={0.85}
                  style={{ pointerEvents: 'none' }}>
                  {n.title.length > 18 ? n.title.slice(0, 17) + '…' : n.title}
                </text>
              </g>
            )
          })}
        </svg>

        <p className="text-center text-slate-600 text-xs pb-3">
          Tap any node to open that topic · Dashed lines = prerequisite links
        </p>
      </div>
    </div>
  )
}

