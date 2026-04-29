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
  1:  'Foundations',
  2:  'Python',
  3:  'TypeScript',
  4:  'React',
  5:  'Angular',
  6:  'Networking',
  7:  'AI Primer',
  8:  'DSA in Java',
  9:  'Scaling & Data',
  10: 'Cloud & DevOps',
  11: 'AI Advanced',
  12: 'Security',
  13: 'System Design',
  14: 'Java Advanced',
  15: 'Financial Literacy',
  16: 'Advanced Engineering',
  17: 'Tooling',
  18: 'AWS',
}

export const UNIT_DIFFICULTY: Record<Unit, string> = {
  1: 'beginner', 2: 'beginner',
  3: 'intermediate', 4: 'intermediate', 5: 'intermediate',
  6: 'intermediate', 7: 'intermediate',
  8: 'advanced', 9: 'advanced', 10: 'advanced',
  11: 'advanced', 12: 'advanced', 18: 'advanced',
  13: 'expert', 14: 'expert',
  15: 'optional', 16: 'optional', 17: 'optional',
}

export function getTopicsByUnit(unit: Unit): Topic[] {
  return topics.filter((t) => t.unit === unit)
}

export const UNITS: Unit[] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
