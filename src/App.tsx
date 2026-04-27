import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect, useRef, useState, Component, type ReactNode } from 'react'
import { ProgressProvider, useProgress } from './state/ProgressContext'
import { HeartsProvider } from './state/HeartsContext'
import { BreakModal } from './components/BreakModal'
import { AchievementToast } from './components/AchievementToast'
import { Home } from './routes/Home'
import { Topic } from './routes/Topic'
import { Quiz } from './routes/Quiz'
import { Result } from './routes/Result'
import { Project } from './routes/Project'
import { Review } from './routes/Review'
import { Flashcards } from './routes/Flashcards'
import { Settings } from './routes/Settings'
import { MindMapRoute } from './routes/MindMapRoute'
import { Stats } from './routes/Stats'
import { getSettings } from './lib/storage'
import { getDueTopicIds } from './lib/scheduler'
import type { Achievement } from './lib/achievements'
import { requestPermission, scheduleNudges } from './lib/notificationService'

const BREAK_INTERVAL_MS = 20 * 60 * 1000 // 20 minutes of VISIBLE use

// ---- Active-time tracker ----
// Measures real wall-clock time the tab is visible.
// Persists to localStorage so it survives page reloads.
// Pauses automatically when tab is hidden or phone screen locks.
const ACTIVE_KEY = 'csm:activeMs'
const SESSION_START_KEY = 'csm:sessionStart'

function getStoredActiveMs(): number {
  try { return parseInt(localStorage.getItem(ACTIVE_KEY) ?? '0', 10) || 0 } catch { return 0 }
}
function saveActiveMs(ms: number) {
  try { localStorage.setItem(ACTIVE_KEY, String(ms)) } catch { /* ignore */ }
}

class ErrorBoundary extends Component<{ children: ReactNode }, { error: string | null }> {
  state = { error: null }
  static getDerivedStateFromError(e: Error) { return { error: e.message } }
  render() {
    if (this.state.error) {
      return (
        <div style={{ background: '#020617', color: '#f87171', padding: 32, fontFamily: 'monospace', minHeight: '100vh' }}>
          <h2>App crashed 💥</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}>{this.state.error}</pre>
          <button onClick={() => { localStorage.clear(); window.location.reload() }}
            style={{ marginTop: 16, background: '#4f46e5', color: '#fff', padding: '8px 16px', border: 'none', borderRadius: 8, cursor: 'pointer' }}>
            Clear storage &amp; reload
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

function AppShell() {
  const { grantStreakBoost, reviewSchedules, flashcardSchedules } = useProgress()
  const [showBreak, setShowBreak] = useState(false)
  const [pendingAchievement, setPendingAchievement] = useState<Achievement | null>(null)
  const sessionStartRef = useRef<number | null>(null)

  // Apply saved theme on mount
  useEffect(() => {
    const s = getSettings()
    document.documentElement.classList.toggle('light-mode', s.theme === 'light')
  }, [])

  // Nudge notifications — request permission after 10s, then check every 30 min
  useEffect(() => {
    const initTimer = setTimeout(async () => {
      await requestPermission()
      scheduleNudges()
    }, 10_000)
    const nudgeInterval = setInterval(scheduleNudges, 30 * 60 * 1000)
    return () => {
      clearTimeout(initTimer)
      clearInterval(nudgeInterval)
    }
  }, [])

  // Schedule review notifications once per session
  useEffect(() => {
    if (!('Notification' in window) || Notification.permission !== 'granted') return
    const dueCount = getDueTopicIds(reviewSchedules as never).length + getDueTopicIds(flashcardSchedules as never).length
    if (dueCount > 0 && !sessionStorage.getItem('csm:notified-today')) {
      sessionStorage.setItem('csm:notified-today', '1')
      setTimeout(() => {
        new Notification('CS Mastery — Time to review! 🔁', {
          body: `${dueCount} item${dueCount > 1 ? 's' : ''} due for review today.`,
          icon: '/icon-192.png',
        })
      }, 5000)
    }
  }, [reviewSchedules, flashcardSchedules])

  useEffect(() => {
    // Start counting when tab becomes visible, stop when hidden
    const startSession = () => {
      if (document.visibilityState === 'visible') {
        sessionStartRef.current = Date.now()
        try { localStorage.setItem(SESSION_START_KEY, String(sessionStartRef.current)) } catch { /* ignore */ }
      } else {
        // Tab hidden — flush elapsed time into storage
        if (sessionStartRef.current !== null) {
          const elapsed = Date.now() - sessionStartRef.current
          const prev = getStoredActiveMs()
          saveActiveMs(prev + elapsed)
          sessionStartRef.current = null
        }
      }
    }

    // Check every 30s if we've crossed 20 min of accumulated visible time
    const checkBreak = () => {
      if (document.visibilityState !== 'visible' || sessionStartRef.current === null) return
      const sessionElapsed = Date.now() - sessionStartRef.current
      const totalMs = getStoredActiveMs() + sessionElapsed
      if (totalMs >= BREAK_INTERVAL_MS && !showBreak) {
        setShowBreak(true)
        // Reset counter after triggering
        saveActiveMs(0)
        sessionStartRef.current = Date.now()
      }
    }

    // Kick off immediately if visible
    if (document.visibilityState === 'visible') {
      sessionStartRef.current = Date.now()
    }

    document.addEventListener('visibilitychange', startSession)
    const interval = setInterval(checkBreak, 30_000)

    return () => {
      document.removeEventListener('visibilitychange', startSession)
      clearInterval(interval)
      // Flush on unmount
      if (sessionStartRef.current !== null) {
        const elapsed = Date.now() - sessionStartRef.current
        saveActiveMs(getStoredActiveMs() + elapsed)
      }
    }
  }, [showBreak])

  return (
    <>
      {showBreak && (
        <BreakModal
          onBoost={() => { grantStreakBoost(); setShowBreak(false) }}
          onDismiss={() => setShowBreak(false)}
        />
      )}
      <AchievementToast achievement={pendingAchievement} onDone={() => setPendingAchievement(null)} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/topic/:id" element={<Topic />} />
        <Route path="/quiz/:id" element={<Quiz />} />
        <Route path="/result/:id" element={<Result />} />
        <Route path="/project/:id" element={<Project />} />
        <Route path="/review" element={<Review />} />
        <Route path="/flashcards/:id" element={<Flashcards />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/mindmap" element={<MindMapRoute />} />
        <Route path="/stats" element={<Stats />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <ProgressProvider>
        <HeartsProvider>
          <BrowserRouter basename="/cs-mastery">
            <AppShell />
          </BrowserRouter>
        </HeartsProvider>
      </ProgressProvider>
    </ErrorBoundary>
  )
}
