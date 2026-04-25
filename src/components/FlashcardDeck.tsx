import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Flashcard } from '../content/schema'

interface Props {
  cards: Flashcard[]
  onComplete: (results: { cardId: string; score: number }[]) => void
}

export function FlashcardDeck({ cards, onComplete }: Props) {
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [results, setResults] = useState<{ cardId: string; score: number }[]>([])

  if (cards.length === 0) {
    return (
      <div className="bg-slate-800 rounded-2xl p-8 text-center text-slate-400">
        No flashcards for this topic yet.
      </div>
    )
  }

  const card = cards[index]

  const rate = (score: number) => {
    const next = [...results, { cardId: card.id, score }]
    if (index + 1 >= cards.length) {
      onComplete(next)
    } else {
      setResults(next)
      setIndex(index + 1)
      setFlipped(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="text-xs text-slate-400 text-center">
        Card {index + 1} / {cards.length}
      </div>
      <div
        className="relative cursor-pointer select-none"
        style={{ perspective: 1000 }}
        onClick={() => setFlipped((f) => !f)}
      >
        <motion.div
          animate={{ rotateY: flipped ? 180 : 0 }}
          transition={{ duration: 0.4 }}
          style={{ transformStyle: 'preserve-3d' }}
          className="relative w-full h-48"
        >
          {/* Front */}
          <div
            style={{ backfaceVisibility: 'hidden' }}
            className="absolute inset-0 bg-slate-800 border border-slate-600 rounded-2xl p-6
              flex items-center justify-center"
          >
            <p className="text-slate-100 text-center font-semibold text-lg">{card.front}</p>
          </div>
          {/* Back */}
          <div
            style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
            className="absolute inset-0 bg-indigo-900 border border-indigo-500 rounded-2xl p-6
              flex items-center justify-center"
          >
            <p className="text-slate-100 text-center text-base">{card.back}</p>
          </div>
        </motion.div>
      </div>

      {!flipped ? (
        <p className="text-center text-slate-400 text-sm">Tap to reveal answer</p>
      ) : (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3"
          >
            <button
              onClick={() => rate(0.2)}
              className="flex-1 bg-red-700 hover:bg-red-600 text-white py-3 rounded-xl font-bold"
            >
              Again
            </button>
            <button
              onClick={() => rate(0.6)}
              className="flex-1 bg-amber-600 hover:bg-amber-500 text-white py-3 rounded-xl font-bold"
            >
              Hard
            </button>
            <button
              onClick={() => rate(1.0)}
              className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white py-3 rounded-xl font-bold"
            >
              Easy
            </button>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  )
}

