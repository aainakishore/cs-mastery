import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Question } from '../content/schema'

interface Props {
  question: Question
  index: number
  total: number
  onAnswer: (answer: unknown) => void
}

export function QuizCard({ question, index, total, onAnswer }: Props) {
  const [selected, setSelected] = useState<unknown>(null)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = () => {
    if (selected === null && question.type !== 'fillBlank') return
    setSubmitted(true)
    setTimeout(() => onAnswer(selected), 500)
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={question.id}
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -40 }}
        className="bg-slate-800 rounded-2xl p-6 shadow-xl"
      >
        <div className="text-xs text-slate-400 mb-3">
          Question {index + 1} / {total}
        </div>
        <p className="text-slate-100 text-lg font-semibold mb-4">{question.prompt}</p>

        {question.type === 'codeOutput' && (
          <pre className="bg-slate-900 text-emerald-300 rounded-lg p-3 text-sm mb-4 overflow-x-auto border border-slate-700">
            {question.code}
          </pre>
        )}

        {(question.type === 'mcq' || question.type === 'codeOutput') && (
          <MCQInput
            choices={question.choices}
            selected={selected as number | null}
            onSelect={(i) => !submitted && setSelected(i)}
            disabled={submitted}
          />
        )}

        {question.type === 'multi' && (
          <MultiInput
            choices={question.choices}
            selected={(selected as number[]) ?? []}
            onToggle={(i) => {
              if (submitted) return
              const arr = (selected as number[]) ?? []
              setSelected(arr.includes(i) ? arr.filter((x) => x !== i) : [...arr, i])
            }}
            disabled={submitted}
          />
        )}

        {question.type === 'fillBlank' && (
          <FillBlankInput
            value={(selected as string) ?? ''}
            onChange={(v) => !submitted && setSelected(v)}
            disabled={submitted}
          />
        )}

        {question.type === 'order' && (
          <OrderInput
            items={question.items}
            order={(selected as number[]) ?? question.items.map((_, i) => i)}
            onChange={(o) => !submitted && setSelected(o)}
            disabled={submitted}
          />
        )}

        {question.type === 'match' && (
          <MatchInput
            left={question.left}
            right={question.right}
            pairs={(selected as [number, number][]) ?? []}
            onChange={(p) => !submitted && setSelected(p)}
            disabled={submitted}
          />
        )}

        <button
          onClick={handleSubmit}
          disabled={submitted}
          className="mt-6 w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50
            text-white font-bold py-3 rounded-xl transition-all"
        >
          {submitted ? 'Next...' : 'Submit Answer'}
        </button>
      </motion.div>
    </AnimatePresence>
  )
}

function MCQInput({
  choices,
  selected,
  onSelect,
  disabled,
}: {
  choices: string[]
  selected: number | null
  onSelect: (i: number) => void
  disabled: boolean
}) {
  return (
    <div className="space-y-2">
      {choices.map((c, i) => (
        <button
          key={i}
          onClick={() => onSelect(i)}
          disabled={disabled}
          className={`w-full text-left px-4 py-3 rounded-xl border text-sm transition-all
            ${selected === i
              ? 'bg-indigo-700 border-indigo-400 text-white'
              : 'bg-slate-700 border-slate-600 text-slate-200 hover:bg-slate-600'
            } disabled:opacity-70`}
        >
          {c}
        </button>
      ))}
    </div>
  )
}

function MultiInput({
  choices,
  selected,
  onToggle,
  disabled,
}: {
  choices: string[]
  selected: number[]
  onToggle: (i: number) => void
  disabled: boolean
}) {
  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-400 mb-2">Select all that apply</p>
      {choices.map((c, i) => (
        <button
          key={i}
          onClick={() => onToggle(i)}
          disabled={disabled}
          className={`w-full text-left px-4 py-3 rounded-xl border text-sm transition-all
            ${selected.includes(i)
              ? 'bg-indigo-700 border-indigo-400 text-white'
              : 'bg-slate-700 border-slate-600 text-slate-200 hover:bg-slate-600'
            } disabled:opacity-70`}
        >
          {selected.includes(i) ? '☑' : '☐'} {c}
        </button>
      ))}
    </div>
  )
}

function FillBlankInput({
  value,
  onChange,
  disabled,
}: {
  value: string
  onChange: (v: string) => void
  disabled: boolean
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder="Type your answer..."
      className="w-full bg-slate-700 border border-slate-600 rounded-xl px-4 py-3
        text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500
        disabled:opacity-70"
    />
  )
}

function OrderInput({
  items,
  order,
  onChange,
  disabled,
}: {
  items: string[]
  order: number[]
  onChange: (o: number[]) => void
  disabled: boolean
}) {
  const move = (from: number, to: number) => {
    const next = [...order]
    const [removed] = next.splice(from, 1)
    next.splice(to, 0, removed)
    onChange(next)
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-400 mb-2">Order these correctly (top = first)</p>
      {order.map((itemIdx, pos) => (
        <div key={itemIdx} className="flex items-center gap-2">
          <div className="flex-1 bg-slate-700 border border-slate-600 rounded-xl px-4 py-2 text-sm text-slate-200">
            {items[itemIdx]}
          </div>
          <div className="flex flex-col gap-1">
            <button
              onClick={() => !disabled && pos > 0 && move(pos, pos - 1)}
              disabled={disabled || pos === 0}
              className="text-slate-400 hover:text-white disabled:opacity-30 text-xs px-1"
            >▲</button>
            <button
              onClick={() => !disabled && pos < order.length - 1 && move(pos, pos + 1)}
              disabled={disabled || pos === order.length - 1}
              className="text-slate-400 hover:text-white disabled:opacity-30 text-xs px-1"
            >▼</button>
          </div>
        </div>
      ))}
    </div>
  )
}

function MatchInput({
  left,
  right,
  pairs,
  onChange,
  disabled,
}: {
  left: string[]
  right: string[]
  pairs: [number, number][]
  onChange: (p: [number, number][]) => void
  disabled: boolean
}) {
  const getPairFor = (leftIdx: number) => pairs.find(([l]) => l === leftIdx)?.[1] ?? -1

  const setMatch = (leftIdx: number, rightIdx: number) => {
    const withoutLeft = pairs.filter(([l]) => l !== leftIdx)
    const withoutRight = withoutLeft.filter(([, r]) => r !== rightIdx)
    onChange([...withoutRight, [leftIdx, rightIdx]])
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-slate-400">Match each item on the left to its definition</p>
      {left.map((l, li) => (
        <div key={li} className="flex items-center gap-3">
          <div className="flex-1 bg-slate-700 border border-slate-600 rounded-xl px-3 py-2 text-sm text-slate-200">
            {l}
          </div>
          <span className="text-slate-400">→</span>
          <select
            value={getPairFor(li)}
            onChange={(e) => setMatch(li, Number(e.target.value))}
            disabled={disabled}
            className="flex-1 bg-slate-700 border border-slate-600 rounded-xl px-3 py-2 text-sm text-slate-200 disabled:opacity-70"
          >
            <option value={-1}>— pick —</option>
            {right.map((r, ri) => (
              <option key={ri} value={ri}>{r}</option>
            ))}
          </select>
        </div>
      ))}
    </div>
  )
}

