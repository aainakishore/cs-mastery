import { Heart } from 'lucide-react'
import { useHearts } from '../state/HeartsContext'

export function HeartsBar() {
  const { count } = useHearts()

  return (
    <div className="flex gap-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <Heart
          key={i}
          size={18}
          className={i < count ? 'text-red-500 fill-red-500' : 'text-slate-600'}
        />
      ))}
    </div>
  )
}

