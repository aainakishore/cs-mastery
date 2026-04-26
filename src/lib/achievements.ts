import { get, set } from './storage'

export interface Achievement {
  id: string
  title: string
  desc: string
  icon: string
  unlockedAt?: string
}

const DEFINITIONS: Achievement[] = [
  { id: 'first-quiz', title: 'First Blood', desc: 'Pass your first quiz', icon: '🎯' },
  { id: 'first-topic', title: 'Beginner', desc: 'Learn your first topic', icon: '🌱' },
  { id: 'unit-1', title: 'Foundations Laid', desc: 'Complete Unit 1 — Foundations', icon: '🏗️' },
  { id: 'unit-2', title: 'AI Primer', desc: 'Complete Unit 2 — AI Primer', icon: '🤖' },
  { id: 'unit-3', title: 'Networked', desc: 'Complete Unit 3 — Networking', icon: '🌐' },
  { id: 'unit-4', title: 'At Scale', desc: 'Complete Unit 4 — Scaling & Data', icon: '📈' },
  { id: 'unit-5', title: 'Cloud Native', desc: 'Complete Unit 5 — Cloud & DevOps', icon: '☁️' },
  { id: 'unit-6', title: 'AI Advanced', desc: 'Complete Unit 6 — AI Advanced', icon: '🧠' },
  { id: 'unit-7', title: 'Tool Master', desc: 'Complete Unit 7 — Tooling', icon: '🔧' },
  { id: 'streak-3', title: '3-Day Streak', desc: 'Study 3 days in a row', icon: '🔥' },
  { id: 'streak-7', title: 'Week Warrior', desc: 'Study 7 days in a row', icon: '⚡' },
  { id: 'streak-30', title: 'Unstoppable', desc: '30-day streak', icon: '💎' },
  { id: 'quiz-10', title: 'Quiz Machine', desc: 'Pass 10 quizzes', icon: '📝' },
  { id: 'quiz-50', title: 'Quiz Legend', desc: 'Pass 50 quizzes', icon: '🏆' },
  { id: 'perfect-quiz', title: 'Perfect Score', desc: 'Score 100% on a quiz', icon: '⭐' },
  { id: 'topic-10', title: 'Halfway There', desc: 'Learn 10 topics', icon: '🎓' },
  { id: 'topic-37', title: 'CS Master', desc: 'Learn all 37 topics', icon: '👑' },
  { id: 'project-1', title: 'Builder', desc: 'Complete your first project', icon: '🏛️' },
  { id: 'flashcard-50', title: 'Card Shark', desc: 'Review 50 flashcards', icon: '🃏' },
  { id: 'xp-500', title: '500 XP', desc: 'Earn 500 XP', icon: '💫' },
  { id: 'xp-2000', title: '2000 XP', desc: 'Earn 2000 XP', icon: '🌟' },
  { id: 'break-taken', title: 'Eye Care', desc: 'Take a 20-min break', icon: '👁️' },
]

type AchievementMap = Record<string, { unlockedAt: string }>

export function getAchievements(): Achievement[] {
  const unlocked = get<AchievementMap>('achievements') ?? {}
  return DEFINITIONS.map(a => ({
    ...a,
    unlockedAt: unlocked[a.id]?.unlockedAt,
  }))
}

export function unlockAchievement(id: string): Achievement | null {
  const unlocked = get<AchievementMap>('achievements') ?? {}
  if (unlocked[id]) return null // already unlocked
  unlocked[id] = { unlockedAt: new Date().toISOString() }
  set('achievements', unlocked)
  return DEFINITIONS.find(a => a.id === id) ?? null
}

export function checkAchievements(params: {
  learnedCount: number
  quizPassCount: number
  streakCount: number
  xp: number
  unitProgress: Record<number, { learned: number; total: number }>
  projectCount: number
  flashcardCount: number
  perfectQuiz?: boolean
  breakTaken?: boolean
}): Achievement[] {
  const newly: Achievement[] = []
  const unlock = (id: string) => {
    const a = unlockAchievement(id)
    if (a) newly.push(a)
  }

  if (params.learnedCount >= 1) unlock('first-topic')
  if (params.learnedCount >= 10) unlock('topic-10')
  if (params.learnedCount >= 37) unlock('topic-37')
  if (params.quizPassCount >= 1) unlock('first-quiz')
  if (params.quizPassCount >= 10) unlock('quiz-10')
  if (params.quizPassCount >= 50) unlock('quiz-50')
  if (params.perfectQuiz) unlock('perfect-quiz')
  if (params.streakCount >= 3) unlock('streak-3')
  if (params.streakCount >= 7) unlock('streak-7')
  if (params.streakCount >= 30) unlock('streak-30')
  if (params.xp >= 500) unlock('xp-500')
  if (params.xp >= 2000) unlock('xp-2000')
  if (params.projectCount >= 1) unlock('project-1')
  if (params.flashcardCount >= 50) unlock('flashcard-50')
  if (params.breakTaken) unlock('break-taken')

  // Unit completion
  Object.entries(params.unitProgress).forEach(([unit, p]) => {
    if (p.learned >= p.total && p.total > 0) unlock(`unit-${unit}`)
  })

  return newly
}

