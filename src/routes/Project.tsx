import { useParams, useNavigate } from 'react-router-dom'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { RubricChecklist } from '../components/RubricChecklist'

export function Project() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { markProjectComplete } = useProgress()

  const topic = id ? getTopicById(id) : undefined

  if (!topic) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Topic not found.
      </div>
    )
  }

  const hasProject = topic.project.checklist.length > 0

  const handleSubmit = (score: number) => {
    markProjectComplete(topic.id, score)
    if (score >= 80) {
      navigate(`/result/${topic.id}`, { state: { passed: true, score: score / 100 } })
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 bg-slate-950/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate(`/topic/${id}`)} className="text-slate-400 hover:text-white text-sm">← Back</button>
        <div>
          <div className="text-xs text-indigo-400">Project</div>
          <div className="font-bold">{topic.title}</div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {hasProject ? (
          <RubricChecklist rubric={topic.project} onSubmit={handleSubmit} />
        ) : (
          <div className="bg-slate-800 rounded-2xl p-8 text-center text-slate-400">
            <p>Project coming soon for this topic.</p>
          </div>
        )}
      </div>
    </div>
  )
}

