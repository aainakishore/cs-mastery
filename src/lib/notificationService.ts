import { getLastStudied } from './storage'
import { getCurrentNudge } from './nudgeMessages'

export async function requestPermission(): Promise<boolean> {
  if (!('Notification' in window)) return false
  if (Notification.permission === 'granted') return true
  if (Notification.permission === 'denied') return false
  const result = await Notification.requestPermission()
  return result === 'granted'
}

// ── Push notification via Service Worker (shows on iPhone home screen) ───────

export async function subscribeToPush(): Promise<PushSubscription | null> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return null
  try {
    const reg = await navigator.serviceWorker.ready
    // Use a static VAPID public key (example key — replace with real in production)
    // Generate with: npx web-push generate-vapid-keys
    const VAPID_PUBLIC_KEY = 'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBuyArmyGkBJjPZhIuLQ'
    const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
    const existing = await reg.pushManager.getSubscription()
    if (existing) return existing
    return await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: applicationServerKey as unknown as ArrayBuffer })
  } catch {
    return null
  }
}

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)))
}

// ── Schedule daily study reminder via SW (works when app is closed) ──────────

export async function scheduleWeeklyVideoReminder(): Promise<void> {
  if (!('serviceWorker' in navigator)) return
  const reg = await navigator.serviceWorker.ready
  const lastKey = 'csm:lastWeeklyVideoReminder'
  const last = localStorage.getItem(lastKey)
  const weekMs = 7 * 24 * 60 * 60 * 1000
  if (last && Date.now() - Number(last) < weekMs) return
  localStorage.setItem(lastKey, String(Date.now()))
  try {
    await reg.showNotification('📺 Weekly Learning Video', {
      body: "Time to watch one YouTube video from your study guide! 10 min = 10x retention.",
      icon: '/cs-mastery/icon-192.png',
      badge: '/cs-mastery/icon-192.png',
      tag: 'csm-weekly-video',
      requireInteraction: false,
      data: { url: '/cs-mastery/' },
    } as NotificationOptions)
  } catch { /* ignore */ }
}

export async function scheduleDailyStudyReminder(): Promise<void> {
  if (!('serviceWorker' in navigator)) return
  const reg = await navigator.serviceWorker.ready
  const lastKey = 'csm:lastDailyReminder'
  const last = localStorage.getItem(lastKey)
  const dayMs = 24 * 60 * 60 * 1000
  if (last && Date.now() - Number(last) < dayMs) return
  localStorage.setItem(lastKey, String(Date.now()))
  try {
    await reg.showNotification('🎯 CS Mastery Daily Goal', {
      body: "You have cards due for review! Keep your streak alive. 5 minutes is enough.",
      icon: '/cs-mastery/icon-192.png',
      badge: '/cs-mastery/icon-192.png',
      tag: 'csm-daily',
      requireInteraction: false,
      data: { url: '/cs-mastery/review' },
    } as NotificationOptions)
  } catch { /* ignore */ }
}

// ── Anti-boredom nudge notifications ─────────────────────────────────────────

const ANTI_BOREDOM_TIPS = [
  { title: "🔀 Context Switch Time!", body: "You've been in one section too long. Try a topic from a different track — your brain consolidates better with variety." },
  { title: "⚡ Flashcard Sprint!", body: "Do 10 flashcards from a topic you HAVEN'T studied today. Cross-track review = 2x retention." },
  { title: "🏗️ Build Something Small", body: "You've read the guide. Now build the smallest possible project that uses this concept. Learning by doing sticks." },
  { title: "📺 Watch Before Next Session", body: "Find the YouTube reference in today's topic guide. Watch it. Visual learning reinforces text 3x." },
  { title: "🧠 Teach It Back", body: "Close this app. Explain today's topic out loud as if teaching a friend. Can't explain it? You don't know it yet." },
]

export async function sendAntiBoredomeNudge(): Promise<void> {
  if (!('serviceWorker' in navigator)) return
  const reg = await navigator.serviceWorker.ready
  const tip = ANTI_BOREDOM_TIPS[Math.floor(Math.random() * ANTI_BOREDOM_TIPS.length)]
  try {
    await reg.showNotification(tip.title, {
      body: tip.body,
      icon: '/cs-mastery/icon-192.png',
      badge: '/cs-mastery/icon-192.png',
      tag: 'csm-antiboredom',
      requireInteraction: false,
      data: { url: '/cs-mastery/' },
    } as NotificationOptions)
  } catch { /* ignore */ }
}

// ── Original in-app nudge (for fallback when SW not available) ────────────────

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

  // Prefer SW notification (works when app is closed, shows on iPhone home screen)
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(reg => {
      reg.showNotification(nudge.title, {
        body: nudge.body,
        icon: '/cs-mastery/icon-192.png',
        badge: '/cs-mastery/icon-192.png',
        tag: 'csm-nudge',
        requireInteraction: false,
      } as NotificationOptions).catch(() => {
        // fallback to basic Notification API
        try { new Notification(nudge.title, { body: nudge.body, icon: '/cs-mastery/icon-192.png' }) } catch { /* ignore */ }
      })
    })
  } else {
    try {
      new Notification(nudge.title, {
        body: nudge.body,
        icon: '/cs-mastery/icon-192.png',
        badge: '/cs-mastery/icon-192.png',
        tag: 'csm-nudge',
      })
    } catch { /* ignore */ }
  }
}
