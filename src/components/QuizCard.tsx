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
        className={`rounded-2xl p-6 shadow-xl transition-all ${feedbackBorder}`}
        style={{ background: 'var(--bg-card)', border: submitted ? undefined : '1px solid var(--border)' }}
      >
        <div className="text-xs mb-3 font-medium" style={{ color: 'var(--text-subtle)' }}>
          Question {index + 1} / {total}
        </div>
        <p className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>{question.prompt}</p>

        {question.type === 'codeOutput' && (
          <pre className="rounded-lg p-3 text-sm mb-4 overflow-x-auto"
            style={{ background: '#0d1117', color: '#a5f3fc', border: '1px solid #1e293b' }}>
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
  choices, selected, onSelect, disabled, correctIndex,
}: {
  choices: string[]; selected: number | null; onSelect: (i: number) => void; disabled: boolean; correctIndex?: number
}) {
  return (
    <div className="space-y-2">
      {choices.map((c, i) => {
        let extraClass = 'quiz-choice'
        let inlineStyle: React.CSSProperties = {
          background: 'var(--bg-input)',
          border: '1.5px solid var(--border)',
          color: 'var(--text-primary)',
        }
        if (disabled && correctIndex !== undefined) {
          if (i === correctIndex) {
            extraClass += ' quiz-choice-correct'
            inlineStyle = { background: undefined, border: undefined, color: undefined }
          } else if (i === selected && i !== correctIndex) {
            extraClass += ' quiz-choice-wrong'
            inlineStyle = { background: undefined, border: undefined, color: undefined }
          } else {
            inlineStyle = { background: 'var(--bg-card)', border: '1.5px solid var(--border)', color: 'var(--text-subtle)', opacity: 0.5 }
          }
        } else if (selected === i) {
          inlineStyle = { background: '#6366f122', border: '1.5px solid #6366f1', color: '#6366f1' }
        }
        return (
          <button
            key={i}
            onClick={() => onSelect(i)}
            disabled={disabled}
            className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-all ${extraClass}`}
            style={inlineStyle}
          >
            <span className="font-mono mr-2 text-xs opacity-60">{String.fromCharCode(65 + i)}.</span>
            {c}
            {disabled && i === correctIndex && <span className="float-right text-emerald-500">✓</span>}
            {disabled && i === selected && i !== correctIndex && <span className="float-right text-red-500">✗</span>}
          </button>
        )
      })}
    </div>
  )
}

function MultiInput({
  choices, selected, onToggle, disabled,
}: {
  choices: string[]; selected: number[]; onToggle: (i: number) => void; disabled: boolean
}) {
  return (
    <div className="space-y-2">
      <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>Select all that apply</p>
      {choices.map((c, i) => (
        <button
          key={i}
          onClick={() => onToggle(i)}
          disabled={disabled}
          className="w-full text-left px-4 py-3 rounded-xl text-sm transition-all disabled:opacity-70"
          style={{
            background: selected.includes(i) ? '#6366f122' : 'var(--bg-input)',
            border: `1.5px solid ${selected.includes(i) ? '#6366f1' : 'var(--border)'}`,
            color: selected.includes(i) ? '#6366f1' : 'var(--text-primary)',
          }}
        >
          {selected.includes(i) ? '☑' : '☐'} {c}
        </button>
      ))}
    </div>
  )
}

function FillBlankInput({ value, onChange, disabled }: { value: string; onChange: (v: string) => void; disabled: boolean }) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder="Type your answer…"
      className="w-full rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-70"
      style={{ background: 'var(--bg-input)', border: '1.5px solid var(--border)', color: 'var(--text-primary)' }}
    />
  )
}

function OrderInput({
  items, order, onChange, disabled,
}: {
  items: string[]; order: number[]; onChange: (o: number[]) => void; disabled: boolean
}) {
  const move = (from: number, to: number) => {
    const next = [...order]; const [removed] = next.splice(from, 1); next.splice(to, 0, removed); onChange(next)
  }
  return (
    <div className="space-y-2">
      <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>Order these correctly (top = first)</p>
      {order.map((itemIdx, pos) => (
        <div key={itemIdx} className="flex items-center gap-2">
          <div className="flex-1 rounded-xl px-4 py-2 text-sm"
            style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
            {items[itemIdx]}
          </div>
          <div className="flex flex-col gap-1">
            <button onClick={() => !disabled && pos > 0 && move(pos, pos - 1)}
              disabled={disabled || pos === 0}
              className="disabled:opacity-30 text-xs px-1" style={{ color: 'var(--text-muted)' }}>▲</button>
            <button onClick={() => !disabled && pos < order.length - 1 && move(pos, pos + 1)}
              disabled={disabled || pos === order.length - 1}
              className="disabled:opacity-30 text-xs px-1" style={{ color: 'var(--text-muted)' }}>▼</button>
          </div>
        </div>
      ))}
    </div>
  )
}

function MatchInput({
  left, right, pairs, onChange, disabled,
}: {
  left: string[]; right: string[]; pairs: [number, number][]; onChange: (p: [number, number][]) => void; disabled: boolean
}) {
  const getPairFor = (leftIdx: number) => pairs.find(([l]) => l === leftIdx)?.[1] ?? -1
  const setMatch = (leftIdx: number, rightIdx: number) => {
    const withoutLeft = pairs.filter(([l]) => l !== leftIdx)
    const withoutRight = withoutLeft.filter(([, r]) => r !== rightIdx)
    onChange([...withoutRight, [leftIdx, rightIdx]])
  }
  return (
    <div className="space-y-3">
      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Match each item on the left to its definition</p>
      {left.map((l, li) => (
        <div key={li} className="flex items-center gap-3">
          <div className="flex-1 rounded-xl px-3 py-2 text-sm"
            style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
            {l}
          </div>
          <span style={{ color: 'var(--text-subtle)' }}>→</span>
          <select
            value={getPairFor(li)}
            onChange={(e) => setMatch(li, Number(e.target.value))}
            disabled={disabled}
            className="flex-1 rounded-xl px-3 py-2 text-sm disabled:opacity-70"
            style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}
          >
            <option value={-1}>— pick —</option>
            {right.map((r, ri) => <option key={ri} value={ri}>{r}</option>)}
          </select>
        </div>
      ))}
    </div>
  )
}
