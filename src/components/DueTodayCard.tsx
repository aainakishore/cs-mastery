import { Link } from 'react-router-dom'
import { CalendarClock } from 'lucide-react'
import { useProgress } from '../state/ProgressContext'
import { getDueTopicIds } from '../lib/scheduler'

export function DueTodayCard() {
  const { reviewSchedules, flashcardSchedules } = useProgress()
  const dueTopics = getDueTopicIds(reviewSchedules).length
  const dueCards = getDueTopicIds(flashcardSchedules).length
  const total = dueTopics + dueCards

  if (total === 0) return null

  return (
    <Link
      to="/review"
      className="flex items-center gap-3 bg-amber-900/40 border border-amber-600 rounded-2xl
        px-4 py-3 hover:bg-amber-900/60 transition-all"
    >
      <CalendarClock size={20} className="text-amber-400 flex-shrink-0" />
      <div>
        <div className="text-amber-200 font-semibold text-sm">Due for review: {total}</div>
        <div className="text-amber-400/70 text-xs">
          {dueTopics > 0 && `${dueTopics} topic${dueTopics > 1 ? 's' : ''}`}
          {dueTopics > 0 && dueCards > 0 && ' · '}
          {dueCards > 0 && `${dueCards} flashcard${dueCards > 1 ? 's' : ''}`}
        </div>
      </div>
    </Link>
  )
}

