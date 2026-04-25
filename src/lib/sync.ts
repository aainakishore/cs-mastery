import { getAllEntries, set, clearAll } from './storage'

interface StoredValue {
  data: unknown
  updatedAt: string
}

export function exportProgress(): void {
  const entries = getAllEntries()
  const json = JSON.stringify(entries, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const date = new Date().toISOString().slice(0, 10)
  const a = document.createElement('a')
  a.href = url
  a.download = `cs-mastery-progress-${date}.json`
  a.click()
  URL.revokeObjectURL(url)
}

export async function importProgress(file: File): Promise<void> {
  const text = await file.text()
  let parsed: Record<string, StoredValue>
  try {
    parsed = JSON.parse(text) as Record<string, StoredValue>
  } catch {
    throw new Error('Invalid export file: could not parse JSON')
  }

  // Validate shape
  for (const [k, v] of Object.entries(parsed)) {
    if (typeof v !== 'object' || v === null || typeof v.updatedAt !== 'string') {
      throw new Error(`Invalid export file: key "${k}" has no updatedAt timestamp`)
    }
  }

  // Merge: keep newer updatedAt per key
  const existing = getAllEntries()
  for (const [k, incoming] of Object.entries(parsed)) {
    const current = existing[k]
    if (!current || new Date(incoming.updatedAt) > new Date(current.updatedAt)) {
      // Strip the 'csm:' prefix to use our set() helper (which adds it back)
      const shortKey = k.startsWith('csm:') ? k.slice(4) : k
      set(shortKey, incoming.data)
    }
  }
}

export function resetProgress(): void {
  clearAll()
  window.location.reload()
}

