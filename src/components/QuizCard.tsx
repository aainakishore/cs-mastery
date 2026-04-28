import { useState, useEffect } from 'react'
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
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null)

  // Reset state whenever the question changes (index changes)
  useEffect(() => {
    setSelected(null)
    setSubmitted(false)
    setIsCorrect(null)
  }, [question.id, index])

  const checkCorrect = (ans: unknown): boolean => {
    if (question.type === 'mcq' || question.type === 'codeOutput') {
      return ans === question.answerIndex
    }
    if (question.type === 'multi') {
      const a = [...((ans as number[]) ?? [])].sort()
      const b = [...question.answerIndexes].sort()
      return a.length === b.length && a.every((v, i) => v === b[i])
    }
    if (question.type === 'fillBlank') {
      const norm = (s: string) => s.toLowerCase().trim().replace(/[^a-z0-9]/g, '')
      return question.accepted.some(acc => norm(acc) === norm((ans as string) ?? ''))
    }
    if (question.type === 'order') {
      const a = (ans as number[]) ?? []
      return a.length === question.correctOrder.length && a.every((v, i) => v === question.correctOrder[i])
    }
    if (question.type === 'match') {
      const a = (ans as [number, number][]) ?? []
      const b = question.pairs
      if (a.length !== b.length) return false
      return b.every(([l, r]) => a.some(([al, ar]) => al === l && ar === r))
    }
    return false
  }

  const handleSubmit = () => {
    if (selected === null && question.type !== 'fillBlank') return
    if (submitted) return
    const correct = checkCorrect(selected)
    setIsCorrect(correct)
    setSubmitted(true)
    // Show result briefly then advance
    setTimeout(() => onAnswer(selected), 1200)
  }

  const feedbackBorder = submitted
    ? isCorrect ? 'border-2 border-emerald-500' : 'border-2 border-red-500'
    : ''

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`${question.id}-${index}`}
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -40 }}
        className={`bg-slate-800 rounded-2xl p-6 shadow-xl transition-all ${feedbackBorder}`}
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
            correctIndex={submitted ? question.answerIndex : undefined}
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
          disabled={submitted || (selected === null && question.type !== 'fillBlank')}
          className={`mt-6 w-full font-bold py-3 rounded-xl transition-all
            ${submitted
              ? isCorrect
                ? 'bg-emerald-600 text-white'
                : 'bg-red-600 text-white'
              : 'bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white'
            }`}
        >
          {submitted ? (isCorrect ? '✓ Correct!' : '✗ Wrong') : 'Submit Answer'}
        </button>

        {/* Explanation shown after submit */}
        {submitted && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mt-4 rounded-xl p-4 text-sm ${
              isCorrect
                ? 'bg-emerald-900/40 border border-emerald-700 text-emerald-200'
                : 'bg-red-900/40 border border-red-700 text-red-200'
            }`}
          >
            <span className="font-bold">{isCorrect ? '💡 ' : '📖 '}</span>
            {question.explanation}
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

function MCQInput({
  choices,
  selected,
  onSelect,
  disabled,
  correctIndex,
}: {
  choices: string[]
  selected: number | null
  onSelect: (i: number) => void
  disabled: boolean
  correctIndex?: number
}) {
  return (
    <div className="space-y-2">
      {choices.map((c, i) => {
        let cls = 'bg-slate-700 border-slate-600 text-slate-200 hover:bg-slate-600'
        if (disabled && correctIndex !== undefined) {
          if (i === correctIndex) cls = 'bg-emerald-800 border-emerald-500 text-white'
          else if (i === selected && i !== correctIndex) cls = 'bg-red-800 border-red-500 text-white'
          else cls = 'bg-slate-800 border-slate-700 text-slate-400 opacity-60'
        } else if (selected === i) {
          cls = 'bg-indigo-700 border-indigo-400 text-white'
        }
        return (
          <button
            key={i}
            onClick={() => onSelect(i)}
            disabled={disabled}
            className={`w-full text-left px-4 py-3 rounded-xl border text-sm transition-all ${cls}`}
          >
            <span className="font-mono text-slate-500 mr-2">{String.fromCharCode(65 + i)}.</span>
            {c}
            {disabled && i === correctIndex && <span className="float-right">✓</span>}
            {disabled && i === selected && i !== correctIndex && <span className="float-right">✗</span>}
          </button>
        )
      })}
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

