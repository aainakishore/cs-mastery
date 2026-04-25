import { describe, it, expect } from 'vitest'
import { scoreQuestion, scoreQuiz } from '../lib/scorer'
import type { Question } from '../content/schema'

const mcq: Question = {
  id: 'test-mcq',
  type: 'mcq',
  prompt: 'Test?',
  choices: ['A', 'B', 'C'],
  answerIndex: 1,
  explanation: '',
  tags: ['tag-a'],
}

const multi: Question = {
  id: 'test-multi',
  type: 'multi',
  prompt: 'Test?',
  choices: ['A', 'B', 'C'],
  answerIndexes: [0, 2],
  explanation: '',
  tags: ['tag-b'],
}

const order: Question = {
  id: 'test-order',
  type: 'order',
  prompt: 'Order?',
  items: ['X', 'Y', 'Z'],
  correctOrder: [2, 0, 1],
  explanation: '',
  tags: ['tag-c'],
}

const match: Question = {
  id: 'test-match',
  type: 'match',
  prompt: 'Match?',
  left: ['A', 'B'],
  right: ['X', 'Y'],
  pairs: [[0, 1], [1, 0]],
  explanation: '',
  tags: ['tag-d'],
}

const fillBlank: Question = {
  id: 'test-fill',
  type: 'fillBlank',
  prompt: 'Fill?',
  accepted: ['correct', 'right answer'],
  explanation: '',
  tags: ['tag-e'],
}

const codeOutput: Question = {
  id: 'test-code',
  type: 'codeOutput',
  prompt: 'Output?',
  code: 'print(1+1)',
  choices: ['1', '2', '3'],
  answerIndex: 1,
  explanation: '',
  tags: ['tag-f'],
}

describe('scoreQuestion', () => {
  it('mcq correct', () => expect(scoreQuestion(mcq, 1).correct).toBe(true))
  it('mcq wrong', () => {
    const r = scoreQuestion(mcq, 0)
    expect(r.correct).toBe(false)
    expect(r.failedTags).toContain('tag-a')
  })

  it('multi correct', () => expect(scoreQuestion(multi, [0, 2]).correct).toBe(true))
  it('multi wrong order still correct', () => expect(scoreQuestion(multi, [2, 0]).correct).toBe(true))
  it('multi wrong', () => expect(scoreQuestion(multi, [0]).correct).toBe(false))

  it('order correct', () => expect(scoreQuestion(order, [2, 0, 1]).correct).toBe(true))
  it('order wrong', () => expect(scoreQuestion(order, [0, 1, 2]).correct).toBe(false))

  it('match correct', () => expect(scoreQuestion(match, [[0, 1], [1, 0]]).correct).toBe(true))
  it('match wrong', () => expect(scoreQuestion(match, [[0, 0], [1, 1]]).correct).toBe(false))

  it('fillBlank correct exact', () => expect(scoreQuestion(fillBlank, 'correct').correct).toBe(true))
  it('fillBlank correct case-insensitive', () => expect(scoreQuestion(fillBlank, 'CORRECT').correct).toBe(true))
  it('fillBlank synonym', () => expect(scoreQuestion(fillBlank, 'right answer').correct).toBe(true))
  it('fillBlank wrong', () => expect(scoreQuestion(fillBlank, 'wrong').correct).toBe(false))

  it('codeOutput correct', () => expect(scoreQuestion(codeOutput, 1).correct).toBe(true))
  it('codeOutput wrong', () => expect(scoreQuestion(codeOutput, 0).correct).toBe(false))
})

describe('scoreQuiz', () => {
  it('passes at 80%', () => {
    const questions = [mcq, mcq, mcq, mcq, mcq]
    const answers = [1, 1, 1, 1, 0] // 4/5 = 80%
    const result = scoreQuiz(questions, answers)
    expect(result.score).toBe(0.8)
    expect(result.passed).toBe(true)
  })

  it('fails below 80%', () => {
    const questions = [mcq, mcq, mcq, mcq, mcq]
    const answers = [1, 1, 1, 0, 0] // 3/5 = 60%
    const result = scoreQuiz(questions, answers)
    expect(result.passed).toBe(false)
    expect(result.failedTags).toContain('tag-a')
  })
})

