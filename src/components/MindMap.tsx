import { useMemo, useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { topics, UNIT_LABELS } from '../content'
import { useProgress } from '../state/ProgressContext'

const UNIT_COLORS: Record<number, string> = {
  1:'#6366f1', 2:'#f7c948', 3:'#3178c6', 4:'#61dafb', 5:'#dd0031',
  6:'#06b6d4', 7:'#8b5cf6', 8:'#14b8a6', 9:'#10b981', 10:'#f59e0b',
  11:'#ec4899', 12:'#ef4444', 13:'#0ea5e9', 14:'#a855f7',
  15:'#f97316', 16:'#64748b', 17:'#84cc16', 18:'#FF9900',
}

interface LayoutNode {
  id: string; title: string; unit: number; x: number; y: number
  status: 'locked'|'available'|'learned'; prereqs: string[]; summary: string
  w: number; h: number
}

function wrapTitle(title: string, maxLen = 16): string[] {
  if (title.length <= maxLen) return [title]
  const words = title.split(' ')
  const lines: string[] = []
  let cur = ''
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > maxLen) {
      if (cur) lines.push(cur.trim())
      cur = w
    } else {
      cur = (cur + ' ' + w).trim()
    }
  }
  if (cur) lines.push(cur.trim())
  return lines.slice(0, 2)
}

function buildLayout(): Omit<LayoutNode, 'status'>[] {
  const groups: Record<number, typeof topics> = {}
  topics.forEach(t => { if (!groups[t.unit]) groups[t.unit] = []; groups[t.unit].push(t) })
  const unitList = [...new Set(topics.map(t => t.unit))].sort()
  const nodes: Omit<LayoutNode, 'status'>[] = []
  const W = 3200, H = 2400, cx = W / 2, cy = H / 2

  unitList.forEach((unit, ui) => {
    // Spread units more — larger ring radius and more spacing
    const angle = (ui / unitList.length) * 2 * Math.PI - Math.PI / 2
    const ux = cx + Math.cos(angle) * 980
    const uy = cy + Math.sin(angle) * 800
    const group = groups[unit] || []
    group.forEach((t, ti) => {
      const tAngle = (ti / Math.max(group.length, 1)) * 2 * Math.PI
      // Spread topics: larger radius per group size so nodes don't overlap
      const r = group.length <= 1 ? 0 : 130 + group.length * 10
      const lines = wrapTitle(t.title)
      const nodeW = Math.max(96, lines[0].length * 8 + 20)
      const nodeH = lines.length > 1 ? 48 : 34
      nodes.push({
        id: t.id, title: t.title, unit: t.unit,
        x: ux + Math.cos(tAngle) * r,
        y: uy + Math.sin(tAngle) * r,
        prereqs: t.prereqs, summary: t.summary,
        w: nodeW, h: nodeH,
      })
    })
  })
  return nodes
}

function bezierPath(x1: number, y1: number, x2: number, y2: number): string {
  const dx = Math.abs(x2 - x1) * 0.45
  const dy = (y2 - y1) * 0.2
  return `M ${x1} ${y1} C ${x1 + dx} ${y1 + dy}, ${x2 - dx} ${y2 - dy}, ${x2} ${y2}`
}

export function MindMap() {
  const navigate = useNavigate()
  const { getTopicProgress } = useProgress()

  const [scale, setScale] = useState(0.38)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [dragging, setDragging] = useState(false)
  const dragStart = useRef({ mx: 0, my: 0, px: 0, py: 0 })
  const pinchStart = useRef({ dist: 0, scale: 0.38 })
  const containerRef = useRef<HTMLDivElement>(null)
  const [search, setSearch] = useState('')
  const [filterUnit, setFilterUnit] = useState<number | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)
  const dragged = useRef(false)

  const rawNodes = useMemo(() => buildLayout(), [])
  const nodes: LayoutNode[] = useMemo(() => rawNodes.map(n => ({
    ...n, status: getTopicProgress(n.id).status as 'locked'|'available'|'learned',
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
    const result: { path: string; key: string; active: boolean; color: string }[] = []
    nodes.forEach(n => {
      n.prereqs.forEach(preId => {
        const pre = nodes.find(p => p.id === preId)
        if (pre) result.push({
          path: bezierPath(pre.x + pre.w / 2, pre.y + pre.h / 2, n.x - n.w / 2, n.y + n.h / 2),
          key: `${preId}->${n.id}`,
          active: filteredIds.has(preId) && filteredIds.has(n.id),
          color: UNIT_COLORS[n.unit] ?? '#6366f1',
        })
      })
    })
    return result
  }, [nodes, filteredIds])

  const unitCenters = useMemo(() => {
    const map: Record<number, { x: number; y: number }> = {}
    nodes.forEach(n => {
      if (!map[n.unit]) {
        const g = nodes.filter(nn => nn.unit === n.unit)
        map[n.unit] = { x: g.reduce((s, nn) => s + nn.x, 0) / g.length, y: g.reduce((s, nn) => s + nn.y, 0) / g.length }
      }
    })
    return map
  }, [nodes])

  const selectedNode = selected ? nodes.find(n => n.id === selected) : null
  const unitList = [...new Set(topics.map(t => t.unit))].sort()

  // ── Pan/zoom handlers ──────────────────────────────────────────────────────
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as Element).closest('.no-pan')) return
    dragged.current = false; setDragging(true)
    dragStart.current = { mx: e.clientX, my: e.clientY, px: pan.x, py: pan.y }
  }, [pan])

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging) return
    const dx = e.clientX - dragStart.current.mx
    const dy = e.clientY - dragStart.current.my
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragged.current = true
    setPan({ x: dragStart.current.px + dx, y: dragStart.current.py + dy })
  }, [dragging])

  const onMouseUp = useCallback(() => setDragging(false), [])

  const onWheel = useCallback((e: WheelEvent) => {
    e.preventDefault()
    const delta = e.ctrlKey ? e.deltaY * 0.01 : e.deltaY * 0.001
    setScale(s => Math.min(3, Math.max(0.12, s - delta)))
  }, [])

  const onTouchStart = useCallback((e: TouchEvent) => {
    if (e.touches.length === 1) {
      dragged.current = false
      dragStart.current = { mx: e.touches[0].clientX, my: e.touches[0].clientY, px: pan.x, py: pan.y }
      setDragging(true)
    } else if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX
      const dy = e.touches[0].clientY - e.touches[1].clientY
      pinchStart.current = { dist: Math.hypot(dx, dy), scale }; setDragging(false)
    }
  }, [pan, scale])

  const onTouchMove = useCallback((e: TouchEvent) => {
    e.preventDefault()
    if (e.touches.length === 1 && dragging) {
      const dx = e.touches[0].clientX - dragStart.current.mx
      const dy = e.touches[0].clientY - dragStart.current.my
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragged.current = true
      setPan({ x: dragStart.current.px + dx, y: dragStart.current.py + dy })
    } else if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX
      const dy = e.touches[0].clientY - e.touches[1].clientY
      setScale(Math.min(3, Math.max(0.12, pinchStart.current.scale * (Math.hypot(dx, dy) / pinchStart.current.dist))))
    }
  }, [dragging])

  const onTouchEnd = useCallback(() => setDragging(false), [])

  useEffect(() => {
    const el = containerRef.current; if (!el) return
    el.addEventListener('wheel', onWheel, { passive: false })
    el.addEventListener('touchstart', onTouchStart, { passive: false })
    el.addEventListener('touchmove', onTouchMove, { passive: false })
    el.addEventListener('touchend', onTouchEnd)
    return () => {
      el.removeEventListener('wheel', onWheel)
      el.removeEventListener('touchstart', onTouchStart)
      el.removeEventListener('touchmove', onTouchMove)
      el.removeEventListener('touchend', onTouchEnd)
    }
  }, [onWheel, onTouchStart, onTouchMove, onTouchEnd])

  const handleNodeClick = useCallback((id: string) => {
    if (dragged.current) return
    setSelected(s => s === id ? null : id); setSheetOpen(true)
  }, [])

  const resetView = () => { setScale(0.38); setPan({ x: 0, y: 0 }) }

  return (
    <div className="flex flex-col gap-2 pb-4">
      {/* Toolbar */}
      <div className="flex flex-wrap gap-2 px-3 pt-2 items-center">
        <input
          className="rounded-xl px-3 py-1.5 text-sm flex-1 min-w-0 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}
          placeholder="🔍 Search topics…"
          value={search} onChange={e => setSearch(e.target.value)}
        />
        <div className="flex gap-1 items-center shrink-0">
          <button onClick={() => setScale(s => Math.min(3, s + 0.12))}
            className="rounded-lg w-8 h-8 font-bold"
            style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>+</button>
          <span className="text-xs w-10 text-center tabular-nums" style={{ color: 'var(--text-subtle)' }}>{Math.round(scale*100)}%</span>
          <button onClick={() => setScale(s => Math.max(0.12, s - 0.12))}
            className="rounded-lg w-8 h-8 font-bold"
            style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>−</button>
          <button onClick={resetView}
            className="rounded-lg px-2 py-1 text-xs"
            style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>Reset</button>
        </div>
      </div>

      {/* Unit filter chips */}
      <div className="flex flex-wrap gap-1 px-3 pb-1">
        <button onClick={() => setFilterUnit(null)}
          className="text-xs px-2.5 py-0.5 rounded-full font-medium transition-colors"
          style={{
            background: filterUnit === null ? '#6366f1' : 'var(--bg-card)',
            color: filterUnit === null ? 'white' : 'var(--text-muted)',
            border: '1px solid var(--border)',
          }}>
          All
        </button>
        {unitList.map(u => (
          <button key={u} onClick={() => setFilterUnit(filterUnit === u ? null : u)}
            className="text-xs px-2 py-0.5 rounded-full font-medium transition-all"
            style={{
              background: filterUnit === u ? UNIT_COLORS[u] : 'var(--bg-card)',
              color: filterUnit === u ? 'white' : UNIT_COLORS[u] ?? '#94a3b8',
              border: `1px solid ${(UNIT_COLORS[u]??'#94a3b8')+'55'}`,
            }}>{(UNIT_LABELS as Record<number,string>)[u]?.split(' ')[0] ?? `U${u}`}</button>
        ))}
      </div>

      {/* ── Canvas ─────────────────────────────────────────────────────────── */}
      <div
        ref={containerRef}
        className="relative rounded-2xl overflow-hidden mx-3 touch-none mm-canvas"
        style={{
          height: 'calc(100svh - 210px)', minHeight: 380,
          background: 'var(--mm-bg, #0d1117)',
          border: '1px solid var(--border)',
          cursor: dragging ? 'grabbing' : 'grab',
        }}
        onMouseDown={onMouseDown} onMouseMove={onMouseMove}
        onMouseUp={onMouseUp} onMouseLeave={onMouseUp}
      >
        <svg width="100%" height="100%" style={{ userSelect: 'none' }}>
          <defs>
            <pattern id="mmgrid" width="28" height="28" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" className="mm-dot" fill="var(--mm-dot, #1a2235)" />
            </pattern>
            <marker id="arr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
              <path d="M 0 0 L 7 3.5 L 0 7 Z" fill="#6366f1" fillOpacity="0.6" />
            </marker>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="b" />
              <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="softglow">
              <feGaussianBlur stdDeviation="2" result="b" />
              <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>
          <rect width="100%" height="100%" fill="url(#mmgrid)" />

          <g transform={`translate(${pan.x},${pan.y}) scale(${scale})`}>
            {/* Unit halo bubbles */}
            {unitList.map(unit => {
              const center = unitCenters[unit]; if (!center) return null
              const color = UNIT_COLORS[unit] ?? '#6366f1'
              const isFiltered = filterUnit !== null && filterUnit !== unit
              const group = nodes.filter(n => n.unit === unit)
              const radius = 110 + group.length * 9
              return (
                <g key={unit} opacity={isFiltered ? 0.05 : 1} style={{ transition: 'opacity 0.3s' }}>
                  <circle cx={center.x} cy={center.y} r={radius}
                    fill={color} fillOpacity={0.04}
                    stroke={color} strokeOpacity={0.15} strokeWidth={1.5} strokeDasharray="10 6" />
                  <text x={center.x} y={center.y - radius - 10}
                    textAnchor="middle" fill={color} fontSize={14} fontWeight="700" opacity={0.8}>
                    {(UNIT_LABELS as Record<number,string>)[unit] ?? `Unit ${unit}`}
                  </text>
                </g>
              )
            })}

            {/* Edges */}
            {edges.map(e => (
              <path key={e.key} d={e.path} fill="none"
                stroke={e.active ? e.color : '#1e293b'}
                strokeWidth={e.active ? 1.8 : 0.6}
                strokeOpacity={e.active ? 0.45 : 0.08}
                markerEnd={e.active ? 'url(#arr)' : undefined}
              />
            ))}

            {/* Nodes — rounded rectangles like Obsidian */}
            {nodes.map(n => {
              const color = UNIT_COLORS[n.unit] ?? '#6366f1'
              const learned = n.status === 'learned'
              const available = n.status === 'available'
              const sel = selected === n.id
              const dimmed = filteredIds.size < nodes.length && !filteredIds.has(n.id)
              const lines = wrapTitle(n.title)
              const rx = n.x - n.w / 2, ry = n.y - n.h / 2

              return (
                <g key={n.id}
                  className="no-pan"
                  style={{ cursor:'pointer', transition:'opacity 0.2s' }}
                  opacity={dimmed ? 0.07 : 1}
                  onClick={() => handleNodeClick(n.id)}
                >
                  {/* Selection halo */}
                  {sel && (
                    <rect x={rx - 8} y={ry - 8} width={n.w + 16} height={n.h + 16} rx={12}
                      fill="none" stroke={color} strokeWidth={2} strokeOpacity={0.5}
                      strokeDasharray="5 3" />
                  )}
                  {/* Available pulse ring */}
                  {available && !sel && (
                    <rect x={rx - 5} y={ry - 5} width={n.w + 10} height={n.h + 10} rx={10}
                      fill="none" stroke={color} strokeWidth="1" strokeOpacity="0.25"
                      strokeDasharray="4 4" />
                  )}
                  {/* Main rect */}
                  <rect
                    x={rx} y={ry} width={n.w} height={n.h} rx={8}
                    fill={learned ? color + 'ee' : available ? color + '22' : 'var(--bg-card, #131a27)'}
                    stroke={color}
                    strokeWidth={sel ? 2.5 : learned ? 2 : available ? 1.5 : 0.8}
                    strokeOpacity={n.status === 'locked' ? 0.3 : 0.85}
                    filter={learned ? 'url(#glow)' : sel ? 'url(#softglow)' : undefined}
                  />
                  {/* Status dot */}
                  <circle cx={rx + n.w - 8} cy={ry + 8} r={4}
                    fill={learned ? '#ffffff' : available ? color : '#334155'}
                    opacity={n.status === 'locked' ? 0.3 : 0.85}
                  />
                  {/* Title text — max 2 lines */}
                  {lines.map((line, li) => (
                    <text key={li}
                      x={n.x} y={n.y + (lines.length === 1 ? 5 : li === 0 ? -4 : 11)}
                      textAnchor="middle"
                      fill={learned ? '#ffffff' : available ? 'var(--text-primary, #e2e8f0)' : 'var(--text-subtle, #64748b)'}
                      fontSize={11} fontWeight={learned || sel ? '700' : '500'}
                      style={{ pointerEvents: 'none' }}
                    >{line}</text>
                  ))}
                </g>
              )
            })}
          </g>
        </svg>

        {/* Zoom hint overlay */}
        <div className="absolute bottom-3 right-3 text-xs pointer-events-none" style={{ color: 'var(--text-subtle)' }}>
          Scroll/pinch to zoom · Drag to pan · Tap node
        </div>
        <div className="absolute bottom-3 left-3 text-xs pointer-events-none" style={{ color: 'var(--text-muted)' }}>
          ✓ {nodes.filter(n=>n.status==='learned').length} / {nodes.length} learned
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 px-3 text-xs" style={{ color: 'var(--text-muted)' }}>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded inline-block bg-emerald-500" />Learned</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded border border-indigo-500 inline-block" style={{ background: 'var(--bg-card)' }} />Available</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded inline-block opacity-30" style={{ border: '1px solid var(--text-subtle)', background: 'var(--bg-card)' }} />Locked</span>
        <span style={{ color: 'var(--text-subtle)' }}>→ arrows = prerequisites</span>
      </div>

      {/* Bottom sheet */}
      {selectedNode && (
        <div className="fixed inset-x-0 bottom-0 z-50 rounded-t-3xl shadow-2xl"
          style={{
            background: 'var(--bg-card)', borderTop: '1px solid var(--border)',
            maxHeight:'60svh', overflowY:'auto', transition:'transform 0.25s',
            transform: sheetOpen ? 'translateY(0)' : 'translateY(100%)',
          }}>
          <div className="flex justify-center pt-3 pb-1">
            <div className="w-10 h-1 rounded-full" style={{ background: 'var(--border)' }} />
          </div>
          <div className="px-5 pb-6 flex flex-col gap-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-xs font-semibold mb-0.5" style={{ color: UNIT_COLORS[selectedNode.unit] }}>
                  {(UNIT_LABELS as Record<number,string>)[selectedNode.unit]}
                </div>
                <h3 className="font-bold text-lg leading-tight" style={{ color: 'var(--text-primary)' }}>{selectedNode.title}</h3>
              </div>
              <div className="flex flex-col items-end gap-2 shrink-0">
                <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                  style={{
                    background: selectedNode.status==='learned' ? '#10b98122' : selectedNode.status==='locked' ? 'var(--border)' : '#6366f122',
                    color: selectedNode.status==='learned' ? '#10b981' : selectedNode.status==='locked' ? 'var(--text-subtle)' : '#6366f1',
                  }}>{selectedNode.status}</span>
                <button onClick={() => setSheetOpen(false)} className="text-xs" style={{ color: 'var(--text-muted)' }}>✕ close</button>
              </div>
            </div>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>{selectedNode.summary}</p>

            {selectedNode.prereqs.length > 0 && (
              <div>
                <div className="text-xs mb-1.5 font-medium" style={{ color: 'var(--text-subtle)' }}>Requires first</div>
                <div className="flex flex-wrap gap-2">
                  {selectedNode.prereqs.map(pid => {
                    const pn = nodes.find(n => n.id === pid); if (!pn) return null
                    return (
                      <button key={pid}
                        className="text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1.5"
                        style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}
                        onClick={() => setSelected(pid)}>
                        <span style={{ color: UNIT_COLORS[pn.unit] }}>●</span>{pn.title}
                        {pn.status==='learned' && <span style={{ color: '#10b981' }}>✓</span>}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {(() => {
              const unlocks = nodes.filter(n => n.prereqs.includes(selectedNode.id))
              if (!unlocks.length) return null
              return (
                <div>
                  <div className="text-xs mb-1.5 font-medium" style={{ color: 'var(--text-subtle)' }}>Unlocks these topics</div>
                  <div className="flex flex-wrap gap-2">
                    {unlocks.map(un => (
                      <button key={un.id}
                        className="text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1.5"
                        style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}
                        onClick={() => setSelected(un.id)}>
                        <span style={{ color: UNIT_COLORS[un.unit] }}>→</span>{un.title}
                      </button>
                    ))}
                  </div>
                </div>
              )
            })()}

            <button onClick={() => navigate(`/topic/${selectedNode.id}`)}
              className="w-full py-3 rounded-2xl font-bold text-white text-sm mt-1"
              style={{ background: UNIT_COLORS[selectedNode.unit] ?? '#6366f1' }}>
              Open Topic →
            </button>
          </div>
        </div>
      )}
      {selectedNode && sheetOpen && (
        <div className="fixed inset-0 z-40 bg-black/50" onClick={() => setSheetOpen(false)} />
      )}
    </div>
  )
}

