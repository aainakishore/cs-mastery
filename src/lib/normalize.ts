// String normalization for fillBlank question scoring

export function normalizeAnswer(s: string): string {
  return s
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s]/g, '')
}

export function answersMatch(userInput: string, accepted: string[]): boolean {
  const normalized = normalizeAnswer(userInput)
  return accepted.some((a) => normalizeAnswer(a) === normalized)
}

