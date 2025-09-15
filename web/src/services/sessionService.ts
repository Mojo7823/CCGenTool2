// Session service for managing persistent user data with unique tokens

export interface SessionData {
  sfrList: any[]
  selectedSfrId: number | null
  nextSfrId: number
  userToken: string
  timestamp: number
}

class SessionService {
  private readonly STORAGE_KEY = 'ccgentool2_session'
  private readonly TOKEN_KEY = 'ccgentool2_user_token'
  private userToken: string

  constructor() {
    this.userToken = this.getOrCreateUserToken()
  }

  /**
   * Generate or retrieve a unique user token
   */
  private getOrCreateUserToken(): string {
    let token = localStorage.getItem(this.TOKEN_KEY)
    
    if (!token) {
      // Generate a unique token using timestamp and random string
      token = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem(this.TOKEN_KEY, token)
    }
    
    return token
  }

  /**
   * Get the current user token
   */
  getUserToken(): string {
    return this.userToken
  }

  /**
   * Save SFR data to session storage
   */
  saveSfrData(sfrList: any[], selectedSfrId: number | null, nextSfrId: number): void {
    const sessionData: SessionData = {
      sfrList,
      selectedSfrId,
      nextSfrId,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = `${this.STORAGE_KEY}_${this.userToken}`
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving SFR data to session:', error)
    }
  }

  /**
   * Load SFR data from session storage
   */
  loadSfrData(): SessionData | null {
    try {
      const storageKey = `${this.STORAGE_KEY}_${this.userToken}`
      const data = localStorage.getItem(storageKey)
      
      if (!data) {
        return null
      }

      const sessionData: SessionData = JSON.parse(data)
      
      // Validate that the token matches
      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading SFR data from session:', error)
      return null
    }
  }

  /**
   * Clear all session data for the current user
   */
  clearSfrData(): void {
    try {
      const storageKey = `${this.STORAGE_KEY}_${this.userToken}`
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.error('Error clearing SFR data from session:', error)
    }
  }

  /**
   * Clear all session data for all users (nuclear option)
   */
  clearAllSfrData(): void {
    try {
      // Find all keys that match our storage pattern
      const keysToRemove: string[] = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && key.startsWith(this.STORAGE_KEY)) {
          keysToRemove.push(key)
        }
      }

      // Remove all matching keys
      keysToRemove.forEach(key => localStorage.removeItem(key))
    } catch (error) {
      console.error('Error clearing all SFR data from session:', error)
    }
  }

  /**
   * Check if there's existing session data
   */
  hasSessionData(): boolean {
    const storageKey = `${this.STORAGE_KEY}_${this.userToken}`
    return localStorage.getItem(storageKey) !== null
  }

  /**
   * Get session info for debugging
   */
  getSessionInfo(): { userToken: string; hasData: boolean; timestamp?: number } {
    const data = this.loadSfrData()
    return {
      userToken: this.userToken,
      hasData: this.hasSessionData(),
      timestamp: data?.timestamp
    }
  }
}

// Export singleton instance
export const sessionService = new SessionService()