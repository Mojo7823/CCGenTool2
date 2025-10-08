const STORAGE_KEY = 'ccgen-user-id'

export function getOrCreateUserId(): string {
  if (typeof window === 'undefined') {
    return ''
  }

  const existing = window.localStorage.getItem(STORAGE_KEY)
  if (existing) {
    return existing
  }

  const generated = typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2)
  window.localStorage.setItem(STORAGE_KEY, generated)
  return generated
}

export function clearUserId(): void {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(STORAGE_KEY)
}

export { STORAGE_KEY as USER_ID_STORAGE_KEY }
