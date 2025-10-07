interface StoredSection<T> {
  data: T
  timestamp: number
}

const STORAGE_PREFIX = 'ccgentool2_st_intro_section'

function buildKey(section: string, userId: string): string {
  return `${STORAGE_PREFIX}_${section}_${userId}`
}

export function loadSection<T>(section: string, userId: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback

  try {
    const raw = window.localStorage.getItem(buildKey(section, userId))
    if (!raw) return fallback

    const parsed: StoredSection<T> = JSON.parse(raw)
    if (parsed && typeof parsed === 'object' && 'data' in parsed) {
      return parsed.data
    }
  } catch (error) {
    console.error(`Failed to load ${section} section from session`, error)
  }

  return fallback
}

export function saveSection<T>(section: string, userId: string, data: T): void {
  if (typeof window === 'undefined') return

  try {
    const payload: StoredSection<T> = {
      data,
      timestamp: Date.now(),
    }
    window.localStorage.setItem(buildKey(section, userId), JSON.stringify(payload))
  } catch (error) {
    console.error(`Failed to persist ${section} section to session`, error)
  }
}

export function clearSection(section: string, userId: string): void {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.removeItem(buildKey(section, userId))
  } catch (error) {
    console.error(`Failed to clear ${section} section from session`, error)
  }
}
