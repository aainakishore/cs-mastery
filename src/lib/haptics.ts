/** Haptic feedback via Vibration API (Android) and CSS Haptics hint for iOS PWA */
export function haptic(pattern: 'light' | 'medium' | 'heavy' | 'error' = 'light') {
  try {
    if (!navigator.vibrate) return
    const patterns = {
      light: [10],
      medium: [20],
      heavy: [40],
      error: [30, 50, 30],
    }
    navigator.vibrate(patterns[pattern])
  } catch { /* ignore */ }
}

