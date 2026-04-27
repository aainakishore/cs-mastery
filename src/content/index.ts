import type { Topic, Unit } from './schema'

// Vite import.meta.glob — loads all topic JSONs without per-file import statements
// This avoids TS2307 errors from verbatimModuleSyntax + bundler moduleResolution
const topicModules = import.meta.glob('./topics/**/*.json', { eager: true }) as Record<
  string,
  { default: Topic }
>

export const topics: Topic[] = Object.values(topicModules)
  .map((m) => m.default)
  .sort((a, b) => a.order - b.order)

export function getTopicById(id: string): Topic | undefined {
  return topics.find((t) => t.id === id)
}

export function getNextTopic(id: string): Topic | undefined {
  const idx = topics.findIndex((t) => t.id === id)
  return idx >= 0 ? topics[idx + 1] : undefined
}

export const UNIT_LABELS: Record<Unit, string> = {
  1: 'Foundations',
  2: 'AI Primer',
  3: 'Networking & Protocols',
  4: 'Scaling & Data',
  5: 'Cloud & DevOps',
  6: 'AI Advanced',
  7: 'Tooling',
  8: 'Financial Literacy',
  9: 'DSA in Java',
  10: 'Frontend Frameworks',
}

export function getTopicsByUnit(unit: Unit): Topic[] {
  return topics.filter((t) => t.unit === unit)
}

export const UNITS: Unit[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
