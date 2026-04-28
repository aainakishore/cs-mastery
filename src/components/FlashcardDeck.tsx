import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Flashcard } from '../content/schema'

interface Props {
  cards: Flashcard[]
  onComplete: (results: { cardId: string; score: number }[]) => void
}

const RATING_INFO = [
  { score: 0.2, label: 'Again', emoji: '🔁', sub: 'See again soon', color: 'bg-red-700 hover:bg-red-600' },
  { score: 0.6, label: 'Hard',  emoji: '😓', sub: 'Review in ~1 day', color: 'bg-amber-600 hover:bg-amber-500' },
  { score: 1.0, label: 'Easy',  emoji: '✅', sub: 'Review in ~3 days', color: 'bg-emerald-600 hover:bg-emerald-500' },
]

export function FlashcardDeck({ cards, onComplete }: Props) {
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [results, setResults] = useState<{ cardId: string; score: number }[]>([])
  const [direction, setDirection] = useState(1)

  if (cards.length === 0) {
    return (
      <div className="bg-slate-800 rounded-2xl p-8 text-center text-slate-400">
        No flashcards for this topic yet.
      </div>
    )
  }

  const card = cards[index]

  const rate = (score: number) => {
    setDirection(1)
    const next = [...results, { cardId: card.id, score }]
    if (index + 1 >= cards.length) {
      onComplete(next)
    } else {
      setResults(next)
      setFlipped(false)
      // Small delay so flip back animation plays before card changes
      setTimeout(() => setIndex(index + 1), 200)
    }
  }

  const progress = ((index) / cards.length) * 100

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="w-full bg-slate-700 rounded-full h-1.5">
        <div
          className="h-1.5 bg-indigo-500 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-500">
        <span>Card {index + 1} / {cards.length}</span>
        <span className="text-indigo-400">{results.filter(r => r.score >= 0.8).length} easy so far</span>
      </div>

      {/* Flip card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${card.id}-${index}`}
          initial={{ opacity: 0, x: direction * 40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: direction * -40 }}
          transition={{ duration: 0.2 }}
          className="relative cursor-pointer select-none"
          style={{ perspective: 1200 }}
          onClick={() => setFlipped(f => !f)}
        >
          <motion.div
            animate={{ rotateY: flipped ? 180 : 0 }}
            transition={{ duration: 0.45, type: 'spring', stiffness: 120, damping: 14 }}
            style={{ transformStyle: 'preserve-3d' }}
            className="relative w-full min-h-[180px]"
          >
            {/* Front */}
            <div
              style={{ backfaceVisibility: 'hidden' }}
              className="absolute inset-0 bg-slate-800 border border-slate-600 rounded-2xl p-6
                flex flex-col items-center justify-center gap-2"
            >
              <span className="text-xs text-slate-500 uppercase tracking-wide">Concept</span>
              <p className="text-slate-100 text-center font-semibold text-lg leading-snug">{card.front}</p>
              <div className="flex gap-1 mt-2">
                {card.tags.map(t => (
                  <span key={t} className="text-xs bg-slate-700 text-slate-400 px-2 py-0.5 rounded-full">{t}</span>
                ))}
              </div>
            </div>
            {/* Back */}
            <div
              style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
              className="absolute inset-0 bg-indigo-950 border border-indigo-600 rounded-2xl p-6
                flex flex-col items-center justify-center gap-2"
            >
              <span className="text-xs text-indigo-400 uppercase tracking-wide">Answer</span>
              <p className="text-slate-100 text-center text-base leading-relaxed">{card.back}</p>
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>

      {!flipped ? (
        <motion.p
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-center text-slate-400 text-sm"
        >
          👆 Tap to reveal answer
        </motion.p>
      ) : (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className="space-y-2"
          >
            <p className="text-center text-xs text-slate-500">How well did you know this?</p>
            <div className="flex gap-2">
              {RATING_INFO.map(r => (
                <button
                  key={r.label}
                  onClick={() => rate(r.score)}
                  className={`flex-1 ${r.color} text-white py-3 rounded-xl font-bold text-sm
                    transition-transform active:scale-95 flex flex-col items-center gap-0.5`}
                >
                  <span>{r.emoji} {r.label}</span>
                  <span className="text-xs font-normal opacity-75">{r.sub}</span>
                </button>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  )
}

interface Props {
  cards: Flashcard[]
  onComplete: (results: { cardId: string; score: number }[]) => void
}
