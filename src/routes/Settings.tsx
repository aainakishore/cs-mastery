import { useRef } from 'react'
import { Download, Upload, Trash2 } from 'lucide-react'
import { exportProgress, importProgress, resetProgress } from '../lib/sync'
import { useProgress } from '../state/ProgressContext'
import { Layout } from '../components/Layout'

export function Settings() {
  const { xp, streak, topicProgress } = useProgress()
  const fileRef = useRef<HTMLInputElement>(null)
  const learnedCount = topicProgress.filter((p) => p.status === 'learned').length

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

        <div className="text-center text-slate-600 text-xs space-y-1">
          <p>CS Mastery v1.0 — No network. No accounts. 100% local.</p>
        </div>
      </div>
    </Layout>
  )
}
