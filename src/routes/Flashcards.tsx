import { useParams, useNavigate } from 'react-router-dom'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { FlashcardDeck } from '../components/FlashcardDeck'

export function Flashcards() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { updateFlashcard } = useProgress()

  const topic = id ? getTopicById(id) : undefined

  if (!topic) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Topic not found.
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate(`/topic/${id}`)} className="text-slate-400 hover:text-white text-sm">← Back</button>
        <div>
          <div className="text-xs text-indigo-400">Flashcards</div>
          <div className="font-bold">{topic.title}</div>
        </div>
      </div>
      <div className="max-w-xl mx-auto px-4 py-8">
        {topic.flashcards.length > 0 ? (
          <FlashcardDeck
            cards={topic.flashcards}
            onComplete={(results) => {
              results.forEach(({ cardId, score }) => updateFlashcard(cardId, score))
              navigate(`/topic/${id}`)
            }}
          />
        ) : (
          <div className="bg-slate-800 rounded-2xl p-8 text-center text-slate-400">
            Flashcards coming soon for this topic.
          </div>
        )}
      </div>
    </div>
  )
}

