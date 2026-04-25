import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  markdown: string
  failedTags?: string[]
}

export function GuideView({ markdown }: Props) {
  return (
    <div className="prose prose-invert prose-indigo max-w-none
      prose-headings:text-indigo-300 prose-a:text-indigo-400
      prose-code:bg-slate-800 prose-code:text-emerald-300 prose-code:px-1 prose-code:rounded
      prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
    </div>
  )
}

