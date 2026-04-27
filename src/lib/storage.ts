import type {
  TopicProgress,
  AppSettings,
} from '../content/schema'
import type { ReviewRecord } from './scheduler'

const NS = 'csm:'

interface StoredValue<T> {
  data: T
  updatedAt: string
}

function key(k: string): string {
  return NS + k
}

export function get<T>(k: string): T | null {
  try {
    const raw = localStorage.getItem(key(k))
    if (!raw) return null
    const parsed = JSON.parse(raw) as StoredValue<T>
    return parsed.data
  } catch {
    return null
  }
}

export function set<T>(k: string, value: T): void {
  const stored: StoredValue<T> = { data: value, updatedAt: new Date().toISOString() }
  localStorage.setItem(key(k), JSON.stringify(stored))
}

export function remove(k: string): void {
  localStorage.removeItem(key(k))
}

export function clearAll(): void {
  const keysToRemove: string[] = []
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i)
    if (k && k.startsWith(NS)) keysToRemove.push(k)
  }
  keysToRemove.forEach((k) => localStorage.removeItem(k))
}

export function getAllEntries(): Record<string, StoredValue<unknown>> {
  const result: Record<string, StoredValue<unknown>> = {}
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i)
    if (k && k.startsWith(NS)) {
      try {
        result[k] = JSON.parse(localStorage.getItem(k)!) as StoredValue<unknown>
      } catch {
        // skip corrupt entry
      }
    }
  }
  return result
}

// ---- Typed helpers ----

export function getProgress(): TopicProgress[] {
  return get<TopicProgress[]>('progress') ?? []
}
export function setProgress(p: TopicProgress[]): void {
  set('progress', p)
}

export function getReviewSchedules(): Record<string, ReviewRecord> {
  return get<Record<string, ReviewRecord>>('reviewSchedules') ?? {}
}
export function setReviewSchedules(r: Record<string, ReviewRecord>): void {
  set('reviewSchedules', r)
}

export function getFlashcardSchedules(): Record<string, ReviewRecord> {
  return get<Record<string, ReviewRecord>>('flashcardSchedules') ?? {}
}
export function setFlashcardSchedules(r: Record<string, ReviewRecord>): void {
  set('flashcardSchedules', r)
}

export function getXP(): number {
  return get<number>('xp') ?? 0
}
export function setXP(n: number): void {
  set('xp', n)
}

export function getStreak(): { count: number; lastDate: string } {
  return get<{ count: number; lastDate: string }>('streak') ?? { count: 0, lastDate: '' }
}
export function setStreak(s: { count: number; lastDate: string }): void {
  set('streak', s)
}

export function getHearts(): { count: number; lastRegen: string } {
  return get<{ count: number; lastRegen: string }>('hearts') ?? {
    count: 5,
    lastRegen: new Date().toISOString(),
  }
}
export function setHearts(h: { count: number; lastRegen: string }): void {
  set('hearts', h)
}

export function getSettings(): AppSettings {
  return get<AppSettings>('settings') ?? { sound: true, animations: true, theme: 'dark' }
}
export function setSettings(s: AppSettings): void {
  set('settings', s)
}

export function getLastStudied(): string | null {
  return get<string>('lastStudied') ?? null
}
export function setLastStudied(iso: string): void {
  set('lastStudied', iso)
}

export function getActiveMinutes(): number {
  return get<number>('activeMinutes') ?? 0
}
export function setActiveMinutes(n: number): void {
  set('activeMinutes', n)
}

