// Content schema — all types used by topic JSON files and state layer

export type TopicId = string
export type Unit = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10

export type QuestionType = 'mcq' | 'multi' | 'order' | 'match' | 'fillBlank' | 'codeOutput'

export type Question =
  | { id: string; type: 'mcq'; prompt: string; choices: string[]; answerIndex: number; explanation: string; tags: string[] }
  | { id: string; type: 'multi'; prompt: string; choices: string[]; answerIndexes: number[]; explanation: string; tags: string[] }
  | { id: string; type: 'order'; prompt: string; items: string[]; correctOrder: number[]; explanation: string; tags: string[] }
  | { id: string; type: 'match'; prompt: string; left: string[]; right: string[]; pairs: [number, number][]; explanation: string; tags: string[] }
  | { id: string; type: 'fillBlank'; prompt: string; accepted: string[]; explanation: string; tags: string[] }
  | { id: string; type: 'codeOutput'; prompt: string; code: string; choices: string[]; answerIndex: number; explanation: string; tags: string[] }

export interface Flashcard {
  id: string
  front: string
  back: string
  tags: string[]
}

export interface ChecklistItem {
  id: string
  text: string
  weight: number
}

export interface ProjectRubric {
  brief: string
  checklist: ChecklistItem[]
  hints: string[]
}

export interface Topic {
  id: TopicId
  unit: Unit
  order: number
  title: string
  summary: string
  prereqs: TopicId[]
  guide: string
  questions: Question[]
  flashcards: Flashcard[]
  project: ProjectRubric
}

// ---- State / progress types ----

export type TopicStatus = 'locked' | 'available' | 'learned'

export interface QuizAttempt {
  date: string
  score: number
  failedTags: string[]
}

export interface TopicProgress {
  topicId: TopicId
  status: TopicStatus
  xpEarned: number
  projectComplete: boolean
  quizHistory: QuizAttempt[]
}

export interface ReviewRecord {
  ease: number
  intervalDays: number
  dueAt: string // ISO date
  lapses: number
}

export interface FlashcardRecord {
  cardId: string
  ease: number
  intervalDays: number
  dueAt: string
  lapses: number
}

export interface AppSettings {
  sound: boolean
  animations: boolean
  theme: 'dark' | 'light'
}

