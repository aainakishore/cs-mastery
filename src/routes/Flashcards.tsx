import { useParams, useNavigate } from 'react-router-dom'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { FlashcardDeck } from '../components/FlashcardDeck'
import { Layout } from '../components/Layout'

export function Flashcards() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { updateFlashcard } = useProgress()

  const topic = id ? getTopicById(id) : undefined

  if (!topic) {
    return (
      <Layout title="Flashcards" back="/">
        <div className="p-8 text-center text-slate-400">Topic not found.</div>
      </Layout>
    )
  }

  return (
    <Layout title={`Flashcards: ${topic.title}`} back={`/topic/${id}`}>
      <div className="max-w-xl mx-auto px-4 py-6">
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
            <p>Flashcards coming soon for this topic.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
