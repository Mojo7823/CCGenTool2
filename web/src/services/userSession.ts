const USER_ID_STORAGE_KEY = 'ccgen-user-id'

function generateUserId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return Math.random().toString(36).slice(2)
}

export function getExistingUserId(): string | null {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage.getItem(USER_ID_STORAGE_KEY)
  } catch (error) {
    console.error('Unable to read user id from storage', error)
    return null
  }
}

export function getOrCreateUserId(): string {
  if (typeof window === 'undefined') {
    return ''
  }

  try {
    let userId = window.localStorage.getItem(USER_ID_STORAGE_KEY)
    if (!userId) {
      userId = generateUserId()
      window.localStorage.setItem(USER_ID_STORAGE_KEY, userId)
    }
    return userId
  } catch (error) {
    console.error('Unable to access user id storage', error)
    return generateUserId()
  }
}

export { USER_ID_STORAGE_KEY }
