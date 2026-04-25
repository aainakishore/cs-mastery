import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Props {
  active: boolean
}

interface Particle {
  id: number
  x: number
  color: string
}

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ec4899', '#3b82f6', '#f97316']

export function Confetti({ active }: Props) {
  const [particles, setParticles] = useState<Particle[]>([])

  useEffect(() => {
    if (!active) return
    const items: Particle[] = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      color: COLORS[i % COLORS.length],
    }))
    setParticles(items)
    const t = setTimeout(() => setParticles([]), 3000)
    return () => clearTimeout(t)
  }, [active])

  return (
    <AnimatePresence>
      {particles.length > 0 && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {particles.map((p) => (
            <motion.div
              key={p.id}
              initial={{ y: -10, x: `${p.x}vw`, opacity: 1, rotate: 0, scale: 1 }}
              animate={{ y: '110vh', opacity: 0, rotate: 720, scale: 0.5 }}
              transition={{ duration: 2 + Math.random(), ease: 'easeIn', delay: Math.random() * 0.5 }}
              style={{ backgroundColor: p.color }}
              className="absolute w-3 h-3 rounded-sm"
            />
          ))}
        </div>
      )}
    </AnimatePresence>
  )
}

