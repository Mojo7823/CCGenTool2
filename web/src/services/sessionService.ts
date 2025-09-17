// Session service for managing persistent user data with unique tokens

export interface SessionData {
  sfrList: any[]
  selectedSfrId: number | null
  nextSfrId: number
  userToken: string
  timestamp: number
}

export interface SarSessionData {
  sarList: any[]
  selectedSarId: number | null
  nextSarId: number
  userToken: string
  timestamp: number
}

class SessionService {
  private readonly STORAGE_KEY = 'ccgentool2_session'
  private readonly SAR_STORAGE_KEY = 'ccgentool2_sar_session'
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

  private getNamespacedKey(baseKey: string): string {
    return `${baseKey}_${this.userToken}`
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
      const storageKey = this.getNamespacedKey(this.STORAGE_KEY)
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
      const storageKey = this.getNamespacedKey(this.STORAGE_KEY)
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
   * Clear all SFR session data for the current user
   */
  clearSfrData(): void {
    try {
      const storageKey = this.getNamespacedKey(this.STORAGE_KEY)
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.error('Error clearing SFR data from session:', error)
    }
  }

  /**
   * Clear all SFR session data for all users (nuclear option)
   */
  clearAllSfrData(): void {
    this.clearAllByPrefix(this.STORAGE_KEY)
  }

  /**
   * Check if there's existing SFR session data
   */
  hasSessionData(): boolean {
    const storageKey = this.getNamespacedKey(this.STORAGE_KEY)
    return localStorage.getItem(storageKey) !== null
  }

  /**
   * Save SAR data to session storage
   */
  saveSarData(sarList: any[], selectedSarId: number | null, nextSarId: number): void {
    const sessionData: SarSessionData = {
      sarList,
      selectedSarId,
      nextSarId,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.SAR_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving SAR data to session:', error)
    }
  }

  /**
   * Load SAR data from session storage
   */
  loadSarData(): SarSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.SAR_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: SarSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored SAR data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading SAR data from session:', error)
      return null
    }
  }

  /**
   * Clear all SAR session data for the current user
   */
  clearSarData(): void {
    try {
      const storageKey = this.getNamespacedKey(this.SAR_STORAGE_KEY)
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.error('Error clearing SAR data from session:', error)
    }
  }

  /**
   * Clear all SAR session data for all users
   */
  clearAllSarData(): void {
    this.clearAllByPrefix(this.SAR_STORAGE_KEY)
  }

  /**
   * Check if there's existing SAR session data
   */
  hasSarSessionData(): boolean {
    const storageKey = this.getNamespacedKey(this.SAR_STORAGE_KEY)
    return localStorage.getItem(storageKey) !== null
  }

  /**
   * Get SFR session info for debugging
   */
  getSessionInfo(): { userToken: string; hasData: boolean; timestamp?: number } {
    const data = this.loadSfrData()
    return {
      userToken: this.userToken,
      hasData: this.hasSessionData(),
      timestamp: data?.timestamp
    }
  }

  /**
   * Get SAR session info for debugging
   */
  getSarSessionInfo(): { userToken: string; hasData: boolean; timestamp?: number } {
    const data = this.loadSarData()
    return {
      userToken: this.userToken,
      hasData: this.hasSarSessionData(),
      timestamp: data?.timestamp
    }
  }

  private clearAllByPrefix(baseKey: string): void {
    try {
      const keysToRemove: string[] = []
      const prefix = `${baseKey}_`
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && key.startsWith(prefix)) {
          keysToRemove.push(key)
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key))
    } catch (error) {
      console.error('Error clearing session data by prefix:', error)
    }
  }
}

// Export singleton instance
export const sessionService = new SessionService()
