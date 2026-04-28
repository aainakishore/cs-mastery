import { useMemo, useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { topics } from '../content'
import { useProgress } from '../state/ProgressContext'

const UNIT_COLORS: Record<number, string> = {
  1: '#6366f1', 2: '#8b5cf6', 3: '#06b6d4',
  4: '#10b981', 5: '#f59e0b', 6: '#ec4899', 7: '#64748b',
  8: '#f97316', 9: '#14b8a6', 10: '#a855f7',
}
const UNIT_LABELS: Record<number, string> = {
  1: 'Foundations', 2: 'AI Primer', 3: 'Networking',
  4: 'Scaling', 5: 'Cloud & DevOps', 6: 'AI Advanced', 7: 'Tooling',
  8: 'DSA (Java)', 9: 'Finance', 10: 'Frontend',
}

interface LayoutNode {
  id: string; title: string; unit: number; x: number; y: number
  status: 'locked' | 'available' | 'learned'; prereqs: string[]
  summary: string; tags: string[]
}

function buildLayout(): Omit<LayoutNode, 'status'>[] {
  const groups: Record<number, typeof topics> = {}
  topics.forEach(t => { if (!groups[t.unit]) groups[t.unit] = []; groups[t.unit].push(t) })
  const unitList = [...new Set(topics.map(t => t.unit))].sort()
  const nodes: Omit<LayoutNode, 'status'>[] = []
  const W = 1600, H = 1200, cx = W / 2, cy = H / 2

  unitList.forEach((unit, ui) => {
    const angle = (ui / unitList.length) * 2 * Math.PI - Math.PI / 2
    const ux = cx + Math.cos(angle) * 460
    const uy = cy + Math.sin(angle) * 360
    const group = groups[unit] || []
    group.forEach((t, ti) => {
      const tAngle = (ti / Math.max(group.length, 1)) * 2 * Math.PI
      const r = group.length <= 1 ? 0 : 70 + group.length * 6
      nodes.push({
        id: t.id, title: t.title, unit: t.unit,
        x: ux + Math.cos(tAngle) * r,
        y: uy + Math.sin(tAngle) * r,
        prereqs: t.prereqs,
        summary: t.summary,
        tags: (t as any).questions?.slice(0, 5).flatMap((q: any) => q.tags ?? []).filter((v: string, i: number, a: string[]) => a.indexOf(v) === i).slice(0, 4) ?? [],
      })
    })
  })
  return nodes
}

export function MindMap() {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()

  // Zoom/pan state
  const [scale, setScale] = useState(0.55)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [dragging, setDragging] = useState(false)
  const dragStart = useRef({ mx: 0, my: 0, px: 0, py: 0 })
  const svgRef = useRef<SVGSVGElement>(null)

  // UI state
  const [search, setSearch] = useState('')
  const [filterUnit, setFilterUnit] = useState<number | null>(null)
  const [hovered, setHovered] = useState<string | null>(null)
  const [selected, setSelected] = useState<string | null>(null)

  const rawNodes = useMemo(() => buildLayout(), [])

  const nodes: LayoutNode[] = useMemo(() => rawNodes.map(n => ({
    ...n,
    status: getTopicProgress(n.id).status as 'locked' | 'available' | 'learned',
  })), [rawNodes, getTopicProgress])

  const filteredNodes = useMemo(() => {
    const q = search.toLowerCase()
    return nodes.filter(n => {
      if (filterUnit !== null && n.unit !== filterUnit) return false
      if (q && !n.title.toLowerCase().includes(q) && !n.summary.toLowerCase().includes(q)) return false
      return true
    })
  }, [nodes, search, filterUnit])

  const filteredIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes])

  const edges = useMemo(() => {
    const result: { x1: number; y1: number; x2: number; y2: number; key: string; active: boolean }[] = []
    nodes.forEach(n => {
      n.prereqs.forEach(preId => {
        const pre = nodes.find(p => p.id === preId)
        if (pre) result.push({
          x1: pre.x, y1: pre.y, x2: n.x, y2: n.y,
          key: `${preId}->${n.id}`,
          active: filteredIds.has(preId) && filteredIds.has(n.id),
        })
      })
    })
    return result
  }, [nodes, filteredIds])

  const unitCenters = useMemo(() => {
    const map: Record<number, { x: number; y: number }> = {}
    nodes.forEach(n => {
      if (!map[n.unit]) {
        const group = nodes.filter(nn => nn.unit === n.unit)
        map[n.unit] = {
          x: group.reduce((s, nn) => s + nn.x, 0) / group.length,
          y: group.reduce((s, nn) => s + nn.y, 0) / group.length,
        }
      }
    })
    return map
  }, [nodes])

  // Selected node detail
  const selectedNode = selected ? nodes.find(n => n.id === selected) : null
  const hoveredNode = hovered ? nodes.find(n => n.id === hovered) : null
  const previewNode = selectedNode || hoveredNode

  // Mouse events for pan
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as Element).closest('.no-pan')) return
    setDragging(true)
    dragStart.current = { mx: e.clientX, my: e.clientY, px: pan.x, py: pan.y }
  }, [pan])

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging) return
    setPan({
      x: dragStart.current.px + e.clientX - dragStart.current.mx,
      y: dragStart.current.py + e.clientY - dragStart.current.my,
    })
  }, [dragging])

  const onMouseUp = useCallback(() => setDragging(false), [])

  const onWheel = useCallback((e: WheelEvent) => {
    e.preventDefault()
    setScale(s => Math.min(3, Math.max(0.2, s - e.deltaY * 0.001)))
  }, [])

  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return
    svg.addEventListener('wheel', onWheel, { passive: false })
    return () => svg.removeEventListener('wheel', onWheel)
  }, [onWheel])


  const unitList = [...new Set(topics.map(t => t.unit))].sort()

  return (
    <div className="flex flex-col gap-3 pb-4">
      {/* Toolbar */}
      <div className="flex flex-wrap gap-2 px-4 pt-3 items-center">
        <input
          className="bg-slate-800 border border-slate-600 rounded-xl px-3 py-1.5 text-sm text-slate-200
            placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-44"
          placeholder="🔍 Search topics…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setFilterUnit(null)}
            className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors
              ${filterUnit === null ? 'bg-slate-200 text-slate-900' : 'bg-slate-700 text-slate-400 hover:bg-slate-600'}`}
          >All</button>
          {unitList.map(u => (
            <button key={u}
              onClick={() => setFilterUnit(filterUnit === u ? null : u)}
              className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors`}
              style={{
                background: filterUnit === u ? UNIT_COLORS[u] : '#1e293b',
                color: filterUnit === u ? 'white' : UNIT_COLORS[u] ?? '#94a3b8',
                border: `1px solid ${UNIT_COLORS[u] ?? '#94a3b8'}40`,
              }}
            >{UNIT_LABELS[u] ?? `Unit ${u}`}</button>
          ))}
        </div>
        <div className="ml-auto flex gap-2 items-center">
          <button onClick={() => setScale(s => Math.min(3, s + 0.15))}
            className="bg-slate-700 text-slate-300 rounded-lg px-2.5 py-1 text-sm hover:bg-slate-600">+</button>
          <span className="text-xs text-slate-500 tabular-nums">{Math.round(scale * 100)}%</span>
          <button onClick={() => setScale(s => Math.max(0.2, s - 0.15))}
            className="bg-slate-700 text-slate-300 rounded-lg px-2.5 py-1 text-sm hover:bg-slate-600">−</button>
          <button onClick={() => { setScale(0.55); setPan({ x: 0, y: 0 }) }}
            className="bg-slate-700 text-slate-300 rounded-lg px-2.5 py-1 text-xs hover:bg-slate-600">Reset</button>
        </div>
      </div>

      <div className="flex gap-3 px-4">
        {/* SVG Canvas */}
        <div className="flex-1 min-w-0 border border-slate-700 rounded-2xl overflow-hidden bg-slate-950 relative"
          style={{ height: '68vh' }}>
          <svg
            ref={svgRef}
            width="100%" height="100%"
            onMouseDown={onMouseDown}
            onMouseMove={onMouseMove}
            onMouseUp={onMouseUp}
            onMouseLeave={onMouseUp}
            style={{ cursor: dragging ? 'grabbing' : 'grab', userSelect: 'none' }}
          >
            {/* Dot grid background */}
            <defs>
              <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="0.8" fill="#1e293b" />
              </pattern>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            <g transform={`translate(${pan.x}, ${pan.y}) scale(${scale})`}>
              {/* Unit cluster halos */}
              {unitList.map(unit => {
                const center = unitCenters[unit]
                if (!center) return null
                const color = UNIT_COLORS[unit] ?? '#6366f1'
                const isFiltered = filterUnit !== null && filterUnit !== unit
                const group = nodes.filter(n => n.unit === unit)
                const radius = 80 + group.length * 8
                return (
                  <g key={unit} opacity={isFiltered ? 0.1 : 1} style={{ transition: 'opacity 0.3s' }}>
                    <circle cx={center.x} cy={center.y} r={radius}
                      fill={color} fillOpacity={0.04}
                      stroke={color} strokeOpacity={0.15} strokeWidth={1.5}
                      strokeDasharray="6 4"
                    />
                    <text x={center.x} y={center.y - radius - 10}
                      textAnchor="middle" fill={color} fontSize={13}
                      fontWeight="700" opacity={0.7} letterSpacing="0.5">
                      {UNIT_LABELS[unit] ?? `Unit ${unit}`}
                    </text>
                    <text x={center.x} y={center.y - radius + 4}
                      textAnchor="middle" fill={color} fontSize={9} opacity={0.45}>
                      {group.filter(n => n.status === 'learned').length}/{group.length} learned
                    </text>
                  </g>
                )
              })}

              {/* Edges */}
              {edges.map(e => (
                <line key={e.key}
                  x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
                  stroke={e.active ? '#475569' : '#1e293b'}
                  strokeWidth={e.active ? 1.2 : 0.5}
                  strokeOpacity={e.active ? 0.5 : 0.15}
                  strokeDasharray="4 4"
                  markerEnd={e.active ? 'url(#arrow)' : undefined}
                />
              ))}
              <defs>
                <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L6,3 z" fill="#475569" opacity="0.5" />
                </marker>
              </defs>

              {/* Nodes */}
              {nodes.map(n => {
                const color = UNIT_COLORS[n.unit] ?? '#6366f1'
                const learned = n.status === 'learned'
                const isHovered = hovered === n.id
                const isSelected = selected === n.id
                const dimmed = filteredIds.size < nodes.length && !filteredIds.has(n.id)
                const r = isSelected ? 26 : isHovered ? 24 : learned ? 20 : 16

                return (
                  <g key={n.id}
                    style={{ cursor: 'pointer', transition: 'opacity 0.25s' }}
                    opacity={dimmed ? 0.15 : 1}
                    onClick={() => { if (!dragging) { setSelected(s => s === n.id ? null : n.id) } }}
                    onMouseEnter={() => setHovered(n.id)}
                    onMouseLeave={() => setHovered(null)}
                    className="no-pan"
                  >
                    {/* Glow ring for selected/hovered */}
                    {(isSelected || isHovered) && (
                      <circle cx={n.x} cy={n.y} r={r + 10}
                        fill={color} fillOpacity={0.12}
                        stroke={color} strokeOpacity={0.25} strokeWidth={1}
                      />
                    )}
                    {/* Main circle */}
                    <circle cx={n.x} cy={n.y} r={r}
                      fill={learned ? color : '#0f172a'}
                      stroke={color}
                      strokeWidth={isSelected ? 3 : learned ? 2.5 : 1.5}
                      filter={learned ? 'url(#glow)' : undefined}
                    />
                    {/* Icon */}
                    {learned ? (
                      <text x={n.x} y={n.y + 5} textAnchor="middle"
                        fill="white" fontSize={r * 0.8} fontWeight="bold">✓</text>
                    ) : (
                      <text x={n.x} y={n.y + 4} textAnchor="middle"
                        fill={color} fontSize={r * 0.75} opacity={0.85}>●</text>
                    )}
                    {/* Label */}
                    <text x={n.x} y={n.y + r + 16} textAnchor="middle"
                      fill={isSelected ? 'white' : color}
                      fontSize={10} fontWeight={isSelected ? '700' : '500'}
                      opacity={isSelected ? 1 : 0.9}
                      style={{ pointerEvents: 'none' }}>
                      {n.title.length > 20 ? n.title.slice(0, 19) + '…' : n.title}
                    </text>
                    {/* Tags as small chips */}
                    {(isHovered || isSelected) && n.tags.slice(0, 3).map((tag, ti) => (
                      <text key={tag}
                        x={n.x} y={n.y + r + 30 + ti * 13} textAnchor="middle"
                        fill={color} fontSize={8} opacity={0.65}
                        style={{ pointerEvents: 'none' }}>
                        #{tag}
                      </text>
                    ))}
                  </g>
                )
              })}
            </g>
          </svg>

          {/* Floating mini stats */}
          <div className="absolute bottom-3 left-3 flex gap-3 text-xs text-slate-500">
            <span>📌 {nodes.filter(n => n.status === 'learned').length}/{nodes.length} learned</span>
            <span>🔗 {edges.length} connections</span>
            <span className="text-slate-600">Scroll to zoom · Drag to pan · Click to select</span>
          </div>
        </div>

        {/* Node detail panel */}
        {previewNode && (
          <div className="w-64 shrink-0 bg-slate-900 border border-slate-700 rounded-2xl p-4 flex flex-col gap-3 text-sm overflow-y-auto"
            style={{ maxHeight: '68vh' }}>
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="text-xs font-medium mb-1"
                  style={{ color: UNIT_COLORS[previewNode.unit] }}>
                  {UNIT_LABELS[previewNode.unit] ?? `Unit ${previewNode.unit}`}
                </div>
                <h3 className="text-white font-bold text-base leading-tight">{previewNode.title}</h3>
              </div>
              <div className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                previewNode.status === 'learned' ? 'bg-emerald-800 text-emerald-300' :
                previewNode.status === 'locked' ? 'bg-slate-800 text-slate-500' :
                'bg-indigo-800 text-indigo-300'
              }`}>
                {previewNode.status}
              </div>
            </div>

            <p className="text-slate-400 text-xs leading-relaxed">{previewNode.summary}</p>

            {previewNode.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {previewNode.tags.map(tag => (
                  <span key={tag} className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full">
                    #{tag}
                  </span>
                ))}
              </div>
            )}

            {/* Prereqs */}
            {previewNode.prereqs.length > 0 && (
              <div>
                <div className="text-xs text-slate-500 mb-1.5 font-medium">Prerequisites</div>
                <div className="flex flex-col gap-1">
                  {previewNode.prereqs.map(pid => {
                    const pn = nodes.find(n => n.id === pid)
                    if (!pn) return null
                    return (
                      <div key={pid}
                        className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1.5 rounded-lg cursor-pointer
                          hover:bg-slate-700 flex items-center gap-1.5"
                        onClick={() => setSelected(pid)}
                      >
                        <span style={{ color: UNIT_COLORS[pn.unit] }}>●</span>
                        {pn.title}
                        {pn.status === 'learned' && <span className="ml-auto text-emerald-400">✓</span>}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Unlocks */}
            {(() => {
              const unlocks = nodes.filter(n => n.prereqs.includes(previewNode.id))
              if (unlocks.length === 0) return null
              return (
                <div>
                  <div className="text-xs text-slate-500 mb-1.5 font-medium">Unlocks</div>
                  <div className="flex flex-col gap-1">
                    {unlocks.map(un => (
                      <div key={un.id}
                        className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1.5 rounded-lg cursor-pointer
                          hover:bg-slate-700 flex items-center gap-1.5"
                        onClick={() => setSelected(un.id)}
                      >
                        <span style={{ color: UNIT_COLORS[un.unit] }}>→</span>
                        {un.title}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })()}

            <button
              onClick={() => navigate(`/topic/${previewNode.id}`)}
              className="mt-auto w-full py-2.5 rounded-xl font-bold text-sm text-white transition-colors"
              style={{ background: UNIT_COLORS[previewNode.unit] }}
            >
              Open Topic →
            </button>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1.5 px-4 text-xs text-slate-500">
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" />Learned</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-slate-700 border border-indigo-500 inline-block" />Available</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-slate-900 border border-slate-600 inline-block opacity-40" />Locked</span>
        <span className="text-slate-600">Dashed lines = prerequisite chains · Click node to see detail panel</span>
      </div>
    </div>
  )
}

