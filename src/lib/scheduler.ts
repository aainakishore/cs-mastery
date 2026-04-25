export interface ReviewRecord {
  ease: number
  intervalDays: number
  dueAt: string // ISO date string
  lapses: number
}

export function createDefaultReview(): ReviewRecord {
  return {
    ease: 2.5,
    intervalDays: 1,
    dueAt: new Date(Date.now() + 86400000).toISOString(),
    lapses: 0,
  }
}

export function updateSchedule(record: ReviewRecord, score: number): ReviewRecord {
  let { ease, intervalDays, lapses } = record

  if (score >= 0.8) {
    intervalDays = Math.round(intervalDays * ease)
    ease = Math.min(3.0, ease + 0.1)
  } else if (score >= 0.5) {
    intervalDays = Math.max(1, Math.round(intervalDays * 0.6))
    ease = ease - 0.15
  } else {
    intervalDays = 1
    ease = Math.max(1.3, ease - 0.3)
    lapses = lapses + 1
  }

  return {
    ease,
    intervalDays,
    dueAt: new Date(Date.now() + intervalDays * 86400000).toISOString(),
    lapses,
  }
}

export function isDue(record: ReviewRecord): boolean {
  return new Date(record.dueAt) <= new Date()
}

export function getDueTopicIds(schedules: Record<string, ReviewRecord>): string[] {
  return Object.entries(schedules)
    .filter(([, r]) => isDue(r))
    .map(([id]) => id)
}

