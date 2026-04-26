import { Layout } from '../components/Layout'
import { MindMap } from '../components/MindMap'

export function MindMapRoute() {
  return (
    <Layout title="Mind Map" back="/">
      <div className="max-w-4xl mx-auto px-2 py-4">
        <p className="text-slate-400 text-sm px-4 pb-2">
          Visual map of all 37 topics and their connections. ✓ = learned. Tap any node to study.
        </p>
        <MindMap />
      </div>
    </Layout>
  )
}

