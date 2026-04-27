import { useRef, useState } from 'react'
import { Download, Upload, Trash2, Bell, Volume2, VolumeX, Sun, Moon } from 'lucide-react'
import { exportProgress, importProgress, resetProgress } from '../lib/sync'
import { useProgress } from '../state/ProgressContext'
import { Layout } from '../components/Layout'
import { getLastStudied, getSettings, setSettings } from '../lib/storage'
import { getCurrentNudge } from '../lib/nudgeMessages'
import type { AppSettings } from '../content/schema'

export function Settings() {
  const { xp, streak, topicProgress } = useProgress()
  const fileRef = useRef<HTMLInputElement>(null)
  const learnedCount = topicProgress.filter((p) => p.status === 'learned').length

  const [settings, setLocalSettings] = useState<AppSettings>(() => getSettings())
  const [notifPermission, setNotifPermission] = useState<NotificationPermission>(() =>
    'Notification' in window ? Notification.permission : 'default',
  )

  const updateSetting = <K extends keyof AppSettings>(key: K, val: AppSettings[K]) => {
    const next = { ...settings, [key]: val }
    setLocalSettings(next)
    setSettings(next)
    // Apply theme immediately
    if (key === 'theme') {
      document.documentElement.classList.toggle('light-mode', val === 'light')
    }
  }

  const requestNotifications = async () => {
    if (!('Notification' in window)) return alert('Notifications not supported in this browser.')
    const result = await Notification.requestPermission()
    setNotifPermission(result)
    if (result === 'granted') {
      // Schedule a test notification
      setTimeout(() => {
        new Notification('CS Mastery 🎓', {
          body: 'Notifications enabled! You\'ll be reminded when topics are due for review.',
          icon: '/icon-192.png',
        })
      }, 500)
    }
  }

  const getHoursSinceLastStudy = () => {
    const lastStudied = getLastStudied()
    if (!lastStudied) return 48
    return Math.max(0, (Date.now() - new Date(lastStudied).getTime()) / (1000 * 60 * 60))
  }

  const testNudge = () => {
    if (!('Notification' in window) || Notification.permission !== 'granted') return
    const nudge = getCurrentNudge(Math.max(getHoursSinceLastStudy(), 2)) ?? {
      title: 'CS Mastery reminder 🧠',
      body: 'Time for a quick study session.',
    }
    new Notification(nudge.title, {
      body: nudge.body,
      icon: '/icon-192.png',
      tag: 'csm-nudge-test',
    })
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      await importProgress(file)
      window.dispatchEvent(new Event('csm-import'))
      alert('Progress imported successfully!')
    } catch (err) {
      alert('Import failed: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const handleReset = () => {
    if (confirm('Reset ALL progress? This cannot be undone unless you exported first.')) {
      resetProgress()
    }
  }

  return (
    <Layout title="Settings" back="/">
      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Stats */}
        <div className="bg-slate-800 rounded-2xl p-5 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-black text-indigo-300">{xp}</div>
            <div className="text-xs text-slate-400">Total XP</div>
          </div>
          <div>
            <div className="text-2xl font-black text-orange-300">{streak.count}</div>
            <div className="text-xs text-slate-400">Day streak</div>
          </div>
          <div>
            <div className="text-2xl font-black text-emerald-300">{learnedCount}</div>
            <div className="text-xs text-slate-400">Topics learned</div>
          </div>
        </div>

        {/* Preferences */}
        <div className="bg-slate-800 rounded-2xl p-5 space-y-4">
          <h3 className="font-bold text-slate-200">Preferences</h3>

          {/* Sound toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {settings.sound ? <Volume2 size={18} className="text-indigo-400" /> : <VolumeX size={18} className="text-slate-500" />}
              <div>
                <div className="text-sm text-slate-200 font-medium">Sound effects</div>
                <div className="text-xs text-slate-500">Coin, correct, wrong, fanfare</div>
              </div>
            </div>
            <button
              onClick={() => updateSetting('sound', !settings.sound)}
              className={`w-12 h-6 rounded-full transition-colors relative ${settings.sound ? 'bg-indigo-600' : 'bg-slate-700'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all ${settings.sound ? 'left-6' : 'left-0.5'}`} />
            </button>
          </div>

          {/* Animations toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-lg">✨</span>
              <div>
                <div className="text-sm text-slate-200 font-medium">Animations</div>
                <div className="text-xs text-slate-500">Confetti, celebrations</div>
              </div>
            </div>
            <button
              onClick={() => updateSetting('animations', !settings.animations)}
              className={`w-12 h-6 rounded-full transition-colors relative ${settings.animations ? 'bg-indigo-600' : 'bg-slate-700'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all ${settings.animations ? 'left-6' : 'left-0.5'}`} />
            </button>
          </div>

          {/* Theme toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {settings.theme === 'dark' ? <Moon size={18} className="text-indigo-400" /> : <Sun size={18} className="text-yellow-400" />}
              <div>
                <div className="text-sm text-slate-200 font-medium">Theme</div>
                <div className="text-xs text-slate-500">{settings.theme === 'dark' ? 'Dark mode' : 'Light mode'}</div>
              </div>
            </div>
            <button
              onClick={() => updateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark')}
              className={`w-12 h-6 rounded-full transition-colors relative ${settings.theme === 'light' ? 'bg-yellow-500' : 'bg-slate-700'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all ${settings.theme === 'light' ? 'left-6' : 'left-0.5'}`} />
            </button>
          </div>

          {/* Notifications */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell size={18} className={notifPermission === 'granted' ? 'text-emerald-400' : 'text-slate-500'} />
              <div>
                <div className="text-sm text-slate-200 font-medium">Angry study reminders 😤</div>
                <div className="text-xs text-slate-500">
                  {notifPermission === 'granted'
                    ? '✓ Active — reminders enabled'
                    : notifPermission === 'denied'
                    ? 'Blocked — enable in browser settings'
                    : 'Gets angrier the longer you ignore it'}
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              {notifPermission === 'granted' && (
                <button onClick={testNudge} className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-2 py-1 rounded-lg">
                  Test
                </button>
              )}
              {notifPermission !== 'granted' && notifPermission !== 'denied' && (
                <button onClick={requestNotifications} className="text-xs bg-indigo-700 hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg font-semibold">
                  Enable
                </button>
              )}
              {notifPermission === 'granted' && <span className="text-emerald-400 text-lg">✓</span>}
            </div>
          </div>
        </div>

        {/* Sync */}
        <div className="bg-slate-800 rounded-2xl p-5 space-y-4">
          <h3 className="font-bold text-slate-200">Cross-device sync</h3>
          <p className="text-slate-400 text-sm">Export → AirDrop to iPhone → Import on the other device.</p>
          <button onClick={exportProgress} className="w-full flex items-center justify-center gap-2 bg-indigo-700 hover:bg-indigo-600 text-white py-3 rounded-xl font-semibold">
            <Download size={16} /> Export progress
          </button>
          <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={handleImport} />
          <button onClick={() => fileRef.current?.click()} className="w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 py-3 rounded-xl font-semibold">
            <Upload size={16} /> Import progress
          </button>
        </div>

        {/* Danger zone */}
        <div className="bg-red-950/40 border border-red-800 rounded-2xl p-5 space-y-3">
          <h3 className="font-bold text-red-300">Danger zone</h3>
          <button onClick={handleReset} className="w-full flex items-center justify-center gap-2 bg-red-700 hover:bg-red-600 text-white py-3 rounded-xl font-semibold">
            <Trash2 size={16} /> Reset all progress
          </button>
        </div>

        <div className="text-center text-slate-600 text-xs">CS Mastery v1.0 — No network. No accounts. 100% local.</div>
      </div>
    </Layout>
  )
}
