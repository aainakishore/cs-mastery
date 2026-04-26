import { useParams, useNavigate } from 'react-router-dom'
import { getTopicById } from '../content'
import { useProgress } from '../state/ProgressContext'
import { RubricChecklist } from '../components/RubricChecklist'
import { Layout } from '../components/Layout'

export function Project() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { markProjectComplete } = useProgress()

  const topic = id ? getTopicById(id) : undefined

  if (!topic) {
    return (
      <Layout title="Project" back="/">
        <div className="p-8 text-center text-slate-400">Topic not found.</div>
      </Layout>
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
    <Layout title={`Project: ${topic.title}`} back={`/topic/${id}`}>
      <div className="max-w-2xl mx-auto px-4 py-6">
        {hasProject ? (
          <RubricChecklist rubric={topic.project} onSubmit={handleSubmit} />
        ) : (
          <div className="bg-slate-800 rounded-2xl p-8 text-center text-slate-400">
            <p>Project coming soon for this topic.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
