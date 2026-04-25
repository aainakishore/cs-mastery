import type { Question } from '../content/schema'
import { answersMatch } from './normalize'

export interface ScoreResult {
  correct: boolean
  partialCredit?: number
  failedTags: string[]
}

export interface QuizScoreResult {
  score: number
  passed: boolean
  failedTags: string[]
  results: ScoreResult[]
}

export function scoreQuestion(question: Question, answer: unknown): ScoreResult {
  const fail = (partial?: number): ScoreResult => ({
    correct: false,
    partialCredit: partial,
    failedTags: question.tags,
  })
  const pass: ScoreResult = { correct: true, failedTags: [] }

  switch (question.type) {
    case 'mcq':
    case 'codeOutput':
      return (answer as number) === question.answerIndex ? pass : fail()

    case 'multi': {
      const selected = [...(answer as number[])].sort()
      const expected = [...question.answerIndexes].sort()
      return JSON.stringify(selected) === JSON.stringify(expected) ? pass : fail()
    }

    case 'order':
      return JSON.stringify(answer) === JSON.stringify(question.correctOrder) ? pass : fail()

    case 'match': {
      const userPairs = (answer as [number, number][]).map(([a, b]) => `${a}:${b}`).sort()
      const correctPairs = question.pairs.map(([a, b]) => `${a}:${b}`).sort()
      return JSON.stringify(userPairs) === JSON.stringify(correctPairs) ? pass : fail()
    }

    case 'fillBlank':
      return answersMatch(answer as string, question.accepted) ? pass : fail()

    default:
      return fail()
  }
}

export function scoreQuiz(questions: Question[], answers: unknown[]): QuizScoreResult {
  const results = questions.map((q, i) => scoreQuestion(q, answers[i]))
  const correctCount = results.filter((r) => r.correct).length
  const score = questions.length > 0 ? correctCount / questions.length : 0
  const failedTagsSet = new Set<string>()
  results.forEach((r) => r.failedTags.forEach((t) => failedTagsSet.add(t)))
  return {
    score,
    passed: score >= 0.8,
    failedTags: [...failedTagsSet],
    results,
  }
}

