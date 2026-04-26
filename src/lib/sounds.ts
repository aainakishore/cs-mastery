/**
 * Sound effects using the Web Audio API — no external files needed.
 * All sounds are synthesised procedurally so the app stays offline.
 */

let ctx: AudioContext | null = null

function getCtx(): AudioContext | null {
  if (typeof window === 'undefined') return null
  if (!ctx) ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)()
  return ctx
}

function play(fn: (c: AudioContext) => void) {
  try {
    const c = getCtx()
    if (!c) return
    if (c.state === 'suspended') c.resume()
    fn(c)
  } catch { /* ignore */ }
}

/** Coin / XP earned — rising arpeggio */
export function playCoin() {
  play((c) => {
    const notes = [523, 659, 784, 1047] // C5 E5 G5 C6
    notes.forEach((freq, i) => {
      const osc = c.createOscillator()
      const gain = c.createGain()
      osc.connect(gain); gain.connect(c.destination)
      osc.type = 'sine'
      osc.frequency.value = freq
      const t = c.currentTime + i * 0.07
      gain.gain.setValueAtTime(0, t)
      gain.gain.linearRampToValueAtTime(0.25, t + 0.01)
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.18)
      osc.start(t); osc.stop(t + 0.2)
    })
  })
}

/** Correct answer — short pleasant chime */
export function playCorrect() {
  play((c) => {
    const osc = c.createOscillator()
    const gain = c.createGain()
    osc.connect(gain); gain.connect(c.destination)
    osc.type = 'sine'
    osc.frequency.setValueAtTime(880, c.currentTime)
    osc.frequency.linearRampToValueAtTime(1100, c.currentTime + 0.12)
    gain.gain.setValueAtTime(0.3, c.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.3)
    osc.start(); osc.stop(c.currentTime + 0.35)
  })
}

/** Wrong answer — descending sad tone */
export function playWrong() {
  play((c) => {
    const osc = c.createOscillator()
    const gain = c.createGain()
    osc.connect(gain); gain.connect(c.destination)
    osc.type = 'sawtooth'
    osc.frequency.setValueAtTime(300, c.currentTime)
    osc.frequency.linearRampToValueAtTime(180, c.currentTime + 0.3)
    gain.gain.setValueAtTime(0.15, c.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.4)
    osc.start(); osc.stop(c.currentTime + 0.45)
  })
}

/** Streak / achievement unlock — fanfare */
export function playFanfare() {
  play((c) => {
    const notes = [392, 494, 587, 784, 987]
    notes.forEach((freq, i) => {
      const osc = c.createOscillator()
      const gain = c.createGain()
      osc.connect(gain); gain.connect(c.destination)
      osc.type = 'square'
      osc.frequency.value = freq
      const t = c.currentTime + i * 0.09
      gain.gain.setValueAtTime(0, t)
      gain.gain.linearRampToValueAtTime(0.18, t + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22)
      osc.start(t); osc.stop(t + 0.25)
    })
  })
}

/** Tick — timer pressure */
export function playTick() {
  play((c) => {
    const buf = c.createBuffer(1, 512, c.sampleRate)
    const data = buf.getChannelData(0)
    for (let i = 0; i < 512; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / 512)
    const src = c.createBufferSource()
    const gain = c.createGain()
    src.buffer = buf; src.connect(gain); gain.connect(c.destination)
    gain.gain.value = 0.4
    src.start()
  })
}

