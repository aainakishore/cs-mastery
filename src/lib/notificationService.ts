import { getLastStudied } from './storage'
import { getCurrentNudge } from './nudgeMessages'

export async function requestPermission(): Promise<boolean> {
  if (!('Notification' in window)) return false
  if (Notification.permission === 'granted') return true
  if (Notification.permission === 'denied') return false
  const result = await Notification.requestPermission()
  return result === 'granted'
}

export function scheduleNudges(): void {
  if (!('Notification' in window) || Notification.permission !== 'granted') return

  const lastStudied = getLastStudied()
  const now = Date.now()
  let hoursElapsed: number

  if (!lastStudied) {
    hoursElapsed = 48
  } else {
    hoursElapsed = (now - new Date(lastStudied).getTime()) / (1000 * 60 * 60)
  }

  const nudge = getCurrentNudge(hoursElapsed)
  if (!nudge) return

  const firedKey = 'csm:nudgeTierFired'
  const lastFiredTier = sessionStorage.getItem(firedKey)
  const thisTierKey = String(nudge.minHours)
  if (lastFiredTier === thisTierKey) return

  sessionStorage.setItem(firedKey, thisTierKey)

  try {
    new Notification(nudge.title, {
      body: nudge.body,
      icon: '/cs-mastery/icon-192.png',
      badge: '/cs-mastery/icon-192.png',
      tag: 'csm-nudge',
    })
  } catch {
    // ignore
  }
}
