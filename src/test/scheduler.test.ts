import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { updateSchedule, isDue, createDefaultReview } from '../lib/scheduler'

const BASE = createDefaultReview()

describe('updateSchedule', () => {
  it('score >= 0.8 increases interval and ease', () => {
    const result = updateSchedule({ ...BASE, intervalDays: 2, ease: 2.5, lapses: 0, dueAt: '' }, 0.9)
    expect(result.intervalDays).toBe(Math.round(2 * 2.5))
    expect(result.ease).toBeCloseTo(2.6)
    expect(result.lapses).toBe(0)
  })

  it('0.5 <= score < 0.8 reduces interval and ease', () => {
    const result = updateSchedule({ ...BASE, intervalDays: 4, ease: 2.5, lapses: 0, dueAt: '' }, 0.6)
    expect(result.intervalDays).toBe(Math.max(1, Math.round(4 * 0.6)))
    expect(result.ease).toBeCloseTo(2.35)
  })

  it('score < 0.5 resets interval and increments lapses', () => {
    const result = updateSchedule({ ...BASE, intervalDays: 10, ease: 2.5, lapses: 1, dueAt: '' }, 0.3)
    expect(result.intervalDays).toBe(1)
    expect(result.lapses).toBe(2)
    expect(result.ease).toBeCloseTo(2.2)
  })

  it('ease does not exceed 3.0', () => {
    const result = updateSchedule({ ...BASE, intervalDays: 1, ease: 2.95, lapses: 0, dueAt: '' }, 1.0)
    expect(result.ease).toBeLessThanOrEqual(3.0)
  })

  it('ease does not go below 1.3', () => {
    const result = updateSchedule({ ...BASE, intervalDays: 1, ease: 1.4, lapses: 0, dueAt: '' }, 0.1)
    expect(result.ease).toBeGreaterThanOrEqual(1.3)
  })
})

describe('isDue', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('past dueAt returns true', () => {
    vi.setSystemTime(new Date('2026-05-01'))
    expect(isDue({ ...BASE, dueAt: '2026-04-30T00:00:00.000Z' })).toBe(true)
  })

  it('future dueAt returns false', () => {
    vi.setSystemTime(new Date('2026-04-25'))
    expect(isDue({ ...BASE, dueAt: '2026-04-30T00:00:00.000Z' })).toBe(false)
  })
})

