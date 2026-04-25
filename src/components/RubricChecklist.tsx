import { useState } from 'react'
import { motion } from 'framer-motion'
import { Lightbulb } from 'lucide-react'
import type { ProjectRubric } from '../content/schema'
import { GuideView } from './GuideView'

interface Props {
  rubric: ProjectRubric
  onSubmit: (score: number) => void
}

export function RubricChecklist({ rubric, onSubmit }: Props) {
  const [checked, setChecked] = useState<Set<string>>(new Set())
  const [hintsUsed, setHintsUsed] = useState(0)

  const toggle = (id: string) => {
    setChecked((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const maxScore =
    hintsUsed === 0 ? 100 : hintsUsed === 1 ? 90 : hintsUsed === 2 ? 80 : 70

  const rawScore = rubric.checklist.reduce(
    (sum, item) => sum + (checked.has(item.id) ? item.weight : 0),
    0,
  )
  const finalScore = Math.round((rawScore / 100) * maxScore)

  const handleHint = () => {
    if (hintsUsed < rubric.hints.length) setHintsUsed((h) => h + 1)
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 rounded-2xl p-6">
        <GuideView markdown={rubric.brief} />
      </div>

      {hintsUsed > 0 && (
        <div className="space-y-3">
          {rubric.hints.slice(0, hintsUsed).map((hint, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-amber-900/40 border border-amber-600 rounded-xl p-4 text-amber-200 text-sm"
            >
              <span className="font-semibold">Hint {i + 1}:</span> {hint}
            </motion.div>
          ))}
        </div>
      )}

      <div className="bg-slate-800 rounded-2xl p-6 space-y-3">
        <h3 className="text-slate-100 font-bold text-lg">Rubric Checklist</h3>
        {hintsUsed < rubric.hints.length && (
          <p className="text-xs text-amber-400">
            ⚠ Using a hint caps max score at {maxScore === 100 ? 90 : maxScore - 10}%
          </p>
        )}
        {rubric.checklist.map((item) => (
          <label
            key={item.id}
            className="flex items-start gap-3 cursor-pointer group"
          >
            <input
              type="checkbox"
              checked={checked.has(item.id)}
              onChange={() => toggle(item.id)}
              className="mt-1 accent-indigo-500 w-4 h-4 flex-shrink-0"
            />
            <span className="text-slate-200 text-sm group-hover:text-white transition">
              {item.text}
              <span className="ml-2 text-slate-500 text-xs">({item.weight} pts)</span>
            </span>
          </label>
        ))}
      </div>

      <div className="flex items-center justify-between bg-slate-900 rounded-2xl p-4">
        <div>
          <div className="text-2xl font-bold text-white">{finalScore}<span className="text-slate-400 text-base">/100</span></div>
          <div className="text-xs text-slate-400">{finalScore >= 80 ? '✅ Pass!' : 'Keep going...'}</div>
        </div>
        <div className="flex gap-3">
          {rubric.hints.length > 0 && hintsUsed < rubric.hints.length && (
            <button
              onClick={handleHint}
              className="flex items-center gap-2 bg-amber-700 hover:bg-amber-600 text-white px-4 py-2 rounded-xl text-sm font-semibold"
            >
              <Lightbulb size={16} /> Hint
            </button>
          )}
          <button
            onClick={() => onSubmit(finalScore)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-xl font-bold"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  )
}

