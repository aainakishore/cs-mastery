import { useState, useEffect, useRef } from 'react'
import { get, set } from '../lib/storage'

interface Props {
  topicId: string
}

export function TopicNotes({ topicId }: Props) {
  const key = `notes:${topicId}`
  const [text, setText] = useState(() => get<string>(key) ?? '')
  const [saved, setSaved] = useState(true)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    setText(get<string>(key) ?? '')
  }, [key])

  const handleChange = (v: string) => {
    setText(v)
    setSaved(false)
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      set(key, v)
      setSaved(true)
    }, 800)
  }

  return (
    <div className="bg-slate-800 rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold text-slate-300"
      >
        <span>📝 My Notes</span>
        <span className="text-slate-500 text-xs flex items-center gap-2">
          {text.length > 0 && <span className="text-emerald-400">●</span>}
          {open ? '▲' : '▼'}
        </span>
      </button>
      {open && (
        <div className="px-4 pb-4">
          <textarea
            value={text}
            onChange={e => handleChange(e.target.value)}
            placeholder="Jot down key insights, your own analogies, things to remember…"
            className="w-full h-36 bg-slate-900 rounded-xl text-sm text-slate-200 p-3 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-slate-600"
          />
          <div className="flex justify-between text-xs text-slate-600 mt-1">
            <span>{text.length} chars</span>
            <span>{saved ? '✓ Saved' : 'Saving…'}</span>
          </div>
        </div>
      )}
    </div>
  )
}

