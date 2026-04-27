export interface NudgeMessage {
  minHours: number
  title: string
  body: string
  emoji: string
}

export const NUDGE_TIERS: NudgeMessage[] = [
  {
    minHours: 2,
    title: "Hey, your neurons are getting rusty 🧠",
    body: "It's been a couple hours. Just one quick lesson — 5 minutes, promise!",
    emoji: "🧠",
  },
  {
    minHours: 4,
    title: "Still here? Let's go! 💪",
    body: "4 hours of procrastination. The topics are literally begging to be learned.",
    emoji: "💪",
  },
  {
    minHours: 6,
    title: "Your future self is disappointed 😤",
    body: "6 hours gone. That's 6 hours your future self will wish you'd spent studying.",
    emoji: "😤",
  },
  {
    minHours: 12,
    title: "HALF A DAY? SERIOUSLY?! 😱",
    body: "It's been 12 hours. The concepts are FADING from your memory as we speak. OPEN THE APP.",
    emoji: "😱",
  },
  {
    minHours: 24,
    title: "I'm calling your mom. 📵",
    body: "24 hours without studying. PUT DOWN YOUTUBE. CS Mastery is waiting. Your career is crying.",
    emoji: "📵",
  },
  {
    minHours: 36,
    title: "YOUR STREAK IS IN DANGER 🔥💀",
    body: "36 hours of laziness. The streak flame is flickering. DO SOMETHING ABOUT IT.",
    emoji: "💀",
  },
  {
    minHours: 48,
    title: "THE STREAK IS DEAD. ARE YOU HAPPY?! 💀",
    body: "48 hours. TWO WHOLE DAYS. Seriously, what are you even doing? Open the app. NOW.",
    emoji: "🤬",
  },
  {
    minHours: 72,
    title: "🚨 EMERGENCY ALERT 🚨",
    body: "3 DAYS. Your brain cells are staging a revolt. They WANT to learn. PLEASE. FOR THE LOVE OF ALGORITHMS.",
    emoji: "🚨",
  },
  {
    minHours: 96,
    title: "4 days. A whole long weekend wasted. 🛋️",
    body: "You could have finished 3 units by now. Instead you watched Netflix. The algorithms weep.",
    emoji: "🛋️",
  },
  {
    minHours: 120,
    title: "5 days gone. Your interviewer is laughing. 😂",
    body: "Someone else studied every one of those 5 days. They're getting your dream job. Wake up.",
    emoji: "😂",
  },
  {
    minHours: 144,
    title: "Six days. You're basically starting from zero. 🧊",
    body: "Memory decay is real. Everything you learned before is fading fast. One topic. Right now.",
    emoji: "🧊",
  },
  {
    minHours: 168,
    title: "ONE WEEK. A full week. 📅💀",
    body: "Seven days of zero progress. At this rate your resume will still say 'familiar with arrays' in 2027.",
    emoji: "📅",
  },
  {
    minHours: 216,
    title: "9 days. You've forgotten what a stack even is. 🤔",
    body: "Seriously — can you still reverse a linked list? No? That's on you. Open the app.",
    emoji: "🤔",
  },
  {
    minHours: 240,
    title: "10 days of silence. The app misses you. 💔",
    body: "Even your flashcards are collecting dust. They were rooting for you. Don't let them down.",
    emoji: "💔",
  },
  {
    minHours: 288,
    title: "12 days. Your future self is filing a complaint. 📋",
    body: "The version of you that lands a senior role studied consistently. Be that person. Start today.",
    emoji: "📋",
  },
  {
    minHours: 336,
    title: "TWO WEEKS. You've ghosted your own education. 👻",
    body: "14 days. That's 336 hours you could have spent mastering DSA, systems, AI. Just… open the app.",
    emoji: "👻",
  },
  {
    minHours: 504,
    title: "3 weeks. Are you even still a developer? 🧑‍💻❓",
    body: "21 days of nothing. Pick ONE topic. Spend 10 minutes. That's literally all it takes to restart.",
    emoji: "❓",
  },
  {
    minHours: 720,
    title: "A FULL MONTH. Respect for the commitment to not committing. 🏆",
    body: "30 days. We're not angry. We're just… deeply, profoundly, disappointed. The topics are still here. They forgive you.",
    emoji: "🏆",
  },
]

export function getCurrentNudge(hoursElapsed: number): NudgeMessage | null {
  const applicable = NUDGE_TIERS.filter((t) => hoursElapsed >= t.minHours)
  return applicable.length > 0 ? applicable[applicable.length - 1] : null
}

// ─── Daily 30-minute learning prompts ────────────────────────────────────────
// These fire every 30 mins throughout the day regardless of last study time.
// Used to keep the user in a "one more lesson" loop while the app is open.

export interface DailyNudge {
  title: string
  body: string
  emoji: string
}

export const DAILY_NUDGES: DailyNudge[] = [
  {
    title: "30 minutes just passed ⏱️",
    body: "That's enough time for one quick topic. Pick the next one and knock it out.",
    emoji: "⏱️",
  },
  {
    title: "One more? You're on a roll. 🎯",
    body: "You've been at it a while — one more topic and you'll have earned that break.",
    emoji: "🎯",
  },
  {
    title: "Half an hour = one new concept 🧠",
    body: "Seriously. 30 minutes is all a topic takes. Load the next one up.",
    emoji: "🧠",
  },
  {
    title: "Compound learning is real 📈",
    body: "Every extra topic today means less review tomorrow. Keep the momentum.",
    emoji: "📈",
  },
  {
    title: "Your streak loves this energy 🔥",
    body: "Another 30 minutes in the books. One more topic and the flame burns brighter.",
    emoji: "🔥",
  },
  {
    title: "Tick tock. Next topic. ⚡",
    body: "You've proved you can focus. 30 more minutes = one more concept locked in long-term memory.",
    emoji: "⚡",
  },
  {
    title: "The interview doesn't wait. Neither should you. 💼",
    body: "Every topic you learn today is one fewer thing to cram before an interview. One more.",
    emoji: "💼",
  },
  {
    title: "You started. Don't stop now. 🏃",
    body: "The hardest part was opening the app. You did that. Just load the next topic.",
    emoji: "🏃",
  },
  {
    title: "30 min checkpoint 🚦",
    body: "Green light. Another topic is ready. Your brain is warmed up — best time to learn.",
    emoji: "🚦",
  },
  {
    title: "Deep work mode: activated 🎧",
    body: "You're in the zone. Don't break it. One more topic. Go.",
    emoji: "🎧",
  },
  {
    title: "Future you is watching right now 👀",
    body: "Every topic you do today is a gift to the version of you sitting in that interview. Keep going.",
    emoji: "👀",
  },
  {
    title: "Half an hour of consistency > 4 hours of cramming 📚",
    body: "This is how pros learn. Steady. Relentless. One more topic.",
    emoji: "📚",
  },
  {
    title: "Spaced repetition needs reps. 🔁",
    body: "The algorithm remembers what you do today. Give it one more data point.",
    emoji: "🔁",
  },
  {
    title: "30-minute mark. The app is proud of you. 🥹",
    body: "No really. You're doing the thing. Keep the thing going. Next topic is waiting.",
    emoji: "🥹",
  },
  {
    title: "You're not tired. You're just comfortable. 😌➡️💪",
    body: "Comfort is the enemy of growth. One more topic breaks the pattern.",
    emoji: "💪",
  },
  {
    title: "Another 30 mins. Another brick in the wall. 🧱",
    body: "That's how expertise is built — one small block at a time. Add yours.",
    emoji: "🧱",
  },
  {
    title: "Your competition didn't stop either. 🏆",
    body: "Somewhere right now someone else is doing another lesson. You in or out?",
    emoji: "🏆",
  },
  {
    title: "Time to level up again. ⬆️",
    body: "This study session is already a win. Make it a bigger win. Next topic.",
    emoji: "⬆️",
  },
  {
    title: "Flow state? Don't kill it. 🌊",
    body: "You're in it. Keep going. One more topic costs you 10 minutes. Do it.",
    emoji: "🌊",
  },
  {
    title: "Micro-sessions beat marathon sessions. ✅",
    body: "30 minutes at a time, all day. That's the cheat code. You already know this.",
    emoji: "✅",
  },
  {
    title: "The flashcards are getting lonely 🃏",
    body: "You haven't reviewed your cards in a bit. One topic + flashcard drill = perfect combo.",
    emoji: "🃏",
  },
  {
    title: "Another half hour, another chapter of your future. 📖",
    body: "Not a metaphor. The topics literally build a mental library you'll draw on for years.",
    emoji: "📖",
  },
  {
    title: "Consistent beats intense. Every time. ⏳",
    body: "You don't need 8 hours. You need this exact 30-minute block. Then the next one.",
    emoji: "⏳",
  },
  {
    title: "One more topic. Because why not? 🤷",
    body: "You're already here. The tab is open. The path is right there. Just click.",
    emoji: "🤷",
  },
]

/**
 * Returns a daily nudge message based on a rotating index.
 * Call with Math.floor(Date.now() / (30 * 60 * 1000)) % DAILY_NUDGES.length
 * to get a different message every 30 minutes.
 */
export function getDailyNudge(slotIndex: number): DailyNudge {
  return DAILY_NUDGES[slotIndex % DAILY_NUDGES.length]
}

