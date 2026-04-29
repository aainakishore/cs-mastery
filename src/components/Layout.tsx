import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Settings } from 'lucide-react'
import { XPBar } from './XPBar'
import { StreakFlame } from './StreakFlame'
import { HeartsBar } from './HeartsBar'
import { NudgeBanner } from './NudgeBanner'
import * as React from "react";

const ACTIVE_KEY = 'csm:activeMs'
const BREAK_INTERVAL_MS = 20 * 60 * 1000

function useActiveMinutes() {
  const [pct, setPct] = useState(0)
  const [minutes, setMinutes] = useState(0)
  useEffect(() => {
    const tick = () => {
      try {
        const stored = parseInt(localStorage.getItem(ACTIVE_KEY) ?? '0', 10) || 0
        setMinutes(Math.floor(stored / 60000))
        setPct(Math.min(100, (stored / BREAK_INTERVAL_MS) * 100))
      } catch { /* ignore */ }
    }
    tick()
    const id = setInterval(tick, 5000)
    return () => clearInterval(id)
  }, [])
  return { pct, minutes }
}

interface LayoutProps {
  children: React.ReactNode
  title?: string
  back?: string   // route to go back to, e.g. '/'
  hideNav?: boolean
}

export function Layout({ children, title, back, hideNav }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { pct, minutes } = useActiveMinutes()

  const navItems = [
    { path: '/',         label: 'Home',    icon: '🏠' },
    { path: '/review',   label: 'Review',  icon: '🎴' },
    { path: '/mindmap',  label: 'Map',     icon: '🗺️' },
    { path: '/stats',    label: 'Stats',   icon: '📈' },
    { path: '/settings', label: 'Settings',icon: '⚙️' },
  ]

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-app)', color: 'var(--text-primary)' }}>
      {/* ── Top bar ── */}
      <div className="sticky top-0 z-20 backdrop-blur" style={{ background: 'var(--bg-nav)', borderBottom: '1px solid var(--border)' }}>
        <div className="w-full px-4 py-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            {back && (
              <button
                onClick={() => navigate(back)}
                className="text-sm shrink-0 font-medium hover:opacity-70"
                style={{ color: 'var(--text-muted)' }}
              >
                ←
              </button>
            )}
            <span className="font-black text-indigo-500 text-base tracking-tight truncate">
              {title ?? 'CS Mastery'}
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <XPBar />
            <StreakFlame />
            <HeartsBar />
            <button
              onClick={() => navigate('/settings')}
              className="p-1 hover:opacity-70"
              style={{ color: 'var(--text-muted)' }}
              aria-label="Settings"
            >
              <Settings size={18} />
            </button>
          </div>
        </div>

        {/* Active-time progress bar */}
        <div className="px-4 pb-2">
          <div className="flex items-center justify-between text-xs mb-1" style={{ color: 'var(--text-subtle)' }}>
            <span>👁 Active time</span>
            <span className={pct > 80 ? 'text-orange-400 font-semibold' : ''}>
              {minutes}m / 20m
            </span>
          </div>
          <div className="w-full rounded-full h-1" style={{ background: 'var(--border)' }}>
            <div
              className="h-1 rounded-full transition-all duration-1000"
              style={{ width: `${pct}%`, background: pct > 80 ? '#f97316' : '#6366f1' }}
            />
          </div>
        </div>
      </div>

      {/* ── Page content ── */}
      <NudgeBanner />
      <div className="flex-1 pb-20 w-full">
        {children}
      </div>

      {/* ── Bottom nav ── */}
      {!hideNav && (
        <div className="fixed bottom-0 left-0 right-0 z-20 backdrop-blur flex justify-around items-center py-2"
          style={{ background: 'var(--bg-nav)', borderTop: '1px solid var(--border)' }}>
          {navItems.map(({ path, label, icon }) => {
            const active = location.pathname === path
            return (
              <button
                key={path}
                onClick={() => navigate(path)}
                className="flex flex-col items-center gap-0.5 text-xs px-3 py-1 transition-all rounded-xl"
                style={{
                  color: active ? '#6366f1' : 'var(--text-muted)',
                  fontWeight: active ? 700 : 400,
                  background: active ? '#6366f120' : 'transparent',
                }}
              >
                <span className="text-xl">{icon}</span>
                {label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

