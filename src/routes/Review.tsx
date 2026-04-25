import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProgress } from '../state/ProgressContext'
import { getDueTopicIds } from '../lib/scheduler'
import { getTopicById, topics } from '../content'
import { scoreQuiz } from '../lib/scorer'
import { QuizCard } from '../components/QuizCard'
import { FlashcardDeck } from '../components/FlashcardDeck'
import type { Question } from '../content/schema'

type QueueItem =
  | { kind: 'topic'; topicId: string }
  | { kind: 'flashcards'; topicId: string }

function buildQueue(
  reviewSchedules: Record<string, unknown>,
  flashcardSchedules: Record<string, unknown>,
): QueueItem[] {
  const dueTopics = getDueTopicIds(reviewSchedules as never)
  const dueCards = getDueTopicIds(flashcardSchedules as never)

  // Unique topic IDs that have due flashcards
  const dueFlashcardTopics = [...new Set(
    dueCards.map((cardId) => {
      // cardId format: topicId + '-fc*'
      const topic = topics.find((t) => t.flashcards.some((fc) => fc.id === cardId))
      return topic?.id
    }).filter(Boolean) as string[],
  )]

  const items: QueueItem[] = []
  dueTopics.forEach((id) => items.push({ kind: 'topic', topicId: id }))
  dueFlashcardTopics.forEach((id) => items.push({ kind: 'flashcards', topicId: id }))
  return items
}

export function Review() {
  const navigate = useNavigate()
  const { reviewSchedules, flashcardSchedules, updateReview, updateFlashcard } = useProgress()

  const [queue] = useState<QueueItem[]>(() => buildQueue(reviewSchedules, flashcardSchedules))
  const [queueIdx, setQueueIdx] = useState(0)
  const [answers, setAnswers] = useState<unknown[]>([])
  const [questionIdx, setQuestionIdx] = useState(0)

  if (queue.length === 0) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-4 p-6 text-center text-white">
        <div className="text-5xl">🎯</div>
        <h2 className="text-2xl font-black">All caught up!</h2>
        <p className="text-slate-400">Nothing due for review right now. Check back tomorrow.</p>
        <button onClick={() => navigate('/')} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold">
          Home
        </button>
      </div>
    )
  }

  if (queueIdx >= queue.length) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-4 p-6 text-center text-white">
        <div className="text-5xl">✅</div>
        <h2 className="text-2xl font-black">Review complete!</h2>
        <p className="text-slate-400">Great work. See you next time.</p>
        <button onClick={() => navigate('/')} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold">
          Home
        </button>
      </div>
    )
  }

  const item = queue[queueIdx]
  const topic = getTopicById(item.topicId)
  if (!topic) {
    setQueueIdx((i) => i + 1)
    return null
  }

  const advance = () => {
    setAnswers([])
    setQuestionIdx(0)
    setQueueIdx((i) => i + 1)
  }

  if (item.kind === 'flashcards') {
    const dueCards = topic.flashcards.filter((fc) => {
      const sched = flashcardSchedules[fc.id]
      return !sched || new Date(sched.dueAt) <= new Date()
    })
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <div className="sticky top-0 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center gap-3">
          <button onClick={() => navigate('/')} className="text-slate-400 hover:text-white text-sm">✕</button>
          <span className="font-bold">Flashcards — {topic.title}</span>
          <span className="ml-auto text-slate-400 text-xs">{queueIdx + 1}/{queue.length}</span>
        </div>
        <div className="max-w-xl mx-auto px-4 py-8">
          <FlashcardDeck
            cards={dueCards}
            onComplete={(results) => {
              results.forEach(({ cardId, score }) => updateFlashcard(cardId, score))
              advance()
            }}
          />
        </div>
      </div>
    )
  }

  // kind === 'topic' — 5-question review quiz
  const questions: Question[] = topic.questions.length > 0
    ? [...topic.questions].sort(() => Math.random() - 0.5).slice(0, 5)
    : []

  if (questions.length === 0) {
    advance()
    return null
  }

  const handleAnswer = (answer: unknown) => {
    const newAnswers = [...answers, answer]
    setAnswers(newAnswers)
    if (questionIdx + 1 < questions.length) {
      setQuestionIdx((i) => i + 1)
    } else {
      const result = scoreQuiz(questions, newAnswers)
      updateReview(topic.id, result.score)
      advance()
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={() => navigate('/')} className="text-slate-400 hover:text-white text-sm">✕</button>
          <span className="font-bold flex-1">Review — {topic.title}</span>
          <span className="text-slate-400 text-xs">{queueIdx + 1}/{queue.length}</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1.5">
          <div
            className="bg-indigo-500 h-1.5 rounded-full transition-all"
            style={{ width: `${(questionIdx / questions.length) * 100}%` }}
          />
        </div>
      </div>
      <div className="max-w-xl mx-auto px-4 py-8">
        <QuizCard
          question={questions[questionIdx]}
          index={questionIdx}
          total={questions.length}
          onAnswer={handleAnswer}
        />
      </div>
    </div>
  )
}

