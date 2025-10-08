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
  selectedEal?: string
  userToken: string
  timestamp: number
}

export interface CoverSessionData {
  form: {
    title: string
    version: string
    revision: string
    description: string
    manufacturer: string
    date: string
  }
  uploadedImagePath: string | null
  userToken: string
  timestamp: number
}

export interface STReferenceSessionData {
  stTitle: string
  stVersion: string
  stDate: string
  author: string
  userToken: string
  timestamp: number
}

export interface TOEReferenceSessionData {
  toeName: string
  toeVersion: string
  toeIdentification: string
  toeType: string
  userToken: string
  timestamp: number
}

export interface TOEOverviewSessionData {
  toeOverview: string
  toeType: string
  toeUsage: string
  toeMajorSecurityFeatures: string
  nonToeHardwareSoftwareFirmware: string
  userToken: string
  timestamp: number
}

export interface TOEDescriptionSessionData {
  toeDescription: string
  toePhysicalScope: string
  toeLogicalScope: string
  userToken: string
  timestamp: number
}

export interface ConformanceClaimsSessionData {
  ccConformance: string
  ppClaims: string
  additionalNotes: string
  userToken: string
  timestamp: number
}

class SessionService {
  private readonly STORAGE_KEY = 'ccgentool2_session'
  private readonly SAR_STORAGE_KEY = 'ccgentool2_sar_session'
  private readonly COVER_STORAGE_KEY = 'ccgentool2_cover_session'
  private readonly ST_REF_STORAGE_KEY = 'ccgentool2_stref_session'
  private readonly TOE_REF_STORAGE_KEY = 'ccgentool2_toeref_session'
  private readonly TOE_OVERVIEW_STORAGE_KEY = 'ccgentool2_toeoverview_session'
  private readonly TOE_DESC_STORAGE_KEY = 'ccgentool2_toedesc_session'
  private readonly CONFORMANCE_CLAIMS_STORAGE_KEY = 'ccgentool2_conformance_session'
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
  saveSarData(sarList: any[], selectedSarId: number | null, nextSarId: number, selectedEal: string): void {
    const sessionData: SarSessionData = {
      sarList,
      selectedSarId,
      nextSarId,
      selectedEal,
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

  /**
   * Save Cover data to session storage
   */
  saveCoverData(form: any, uploadedImagePath: string | null): void {
    const sessionData: CoverSessionData = {
      form,
      uploadedImagePath,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.COVER_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving Cover data to session:', error)
    }
  }

  /**
   * Load Cover data from session storage
   */
  loadCoverData(): CoverSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.COVER_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: CoverSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored Cover data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading Cover data from session:', error)
      return null
    }
  }

  /**
   * Clear Cover session data
   */
  clearCoverData(): void {
    try {
      const storageKey = this.getNamespacedKey(this.COVER_STORAGE_KEY)
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.error('Error clearing Cover data from session:', error)
    }
  }

  /**
   * Save ST Reference data to session storage
   */
  saveSTReferenceData(data: Omit<STReferenceSessionData, 'userToken' | 'timestamp'>): void {
    const sessionData: STReferenceSessionData = {
      ...data,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.ST_REF_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving ST Reference data to session:', error)
    }
  }

  /**
   * Load ST Reference data from session storage
   */
  loadSTReferenceData(): STReferenceSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.ST_REF_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: STReferenceSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored ST Reference data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading ST Reference data from session:', error)
      return null
    }
  }

  /**
   * Save TOE Reference data to session storage
   */
  saveTOEReferenceData(data: Omit<TOEReferenceSessionData, 'userToken' | 'timestamp'>): void {
    const sessionData: TOEReferenceSessionData = {
      ...data,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.TOE_REF_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving TOE Reference data to session:', error)
    }
  }

  /**
   * Load TOE Reference data from session storage
   */
  loadTOEReferenceData(): TOEReferenceSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.TOE_REF_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: TOEReferenceSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored TOE Reference data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading TOE Reference data from session:', error)
      return null
    }
  }

  /**
   * Save TOE Overview data to session storage
   */
  saveTOEOverviewData(data: Omit<TOEOverviewSessionData, 'userToken' | 'timestamp'>): void {
    const sessionData: TOEOverviewSessionData = {
      ...data,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.TOE_OVERVIEW_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving TOE Overview data to session:', error)
    }
  }

  /**
   * Load TOE Overview data from session storage
   */
  loadTOEOverviewData(): TOEOverviewSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.TOE_OVERVIEW_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: TOEOverviewSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored TOE Overview data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading TOE Overview data from session:', error)
      return null
    }
  }

  /**
   * Save TOE Description data to session storage
   */
  saveTOEDescriptionData(data: Omit<TOEDescriptionSessionData, 'userToken' | 'timestamp'>): void {
    const sessionData: TOEDescriptionSessionData = {
      ...data,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.TOE_DESC_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving TOE Description data to session:', error)
    }
  }

  /**
   * Load TOE Description data from session storage
   */
  loadTOEDescriptionData(): TOEDescriptionSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.TOE_DESC_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: TOEDescriptionSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored TOE Description data')
        return null
      }

      sessionData.toeDescription = sessionData.toeDescription || ''
      sessionData.toePhysicalScope = sessionData.toePhysicalScope || ''
      sessionData.toeLogicalScope = sessionData.toeLogicalScope || ''

      return sessionData
    } catch (error) {
      console.error('Error loading TOE Description data from session:', error)
      return null
    }
  }

  /**
   * Save Conformance Claims data to session storage
   */
  saveConformanceClaimsData(data: Omit<ConformanceClaimsSessionData, 'userToken' | 'timestamp'>): void {
    const sessionData: ConformanceClaimsSessionData = {
      ...data,
      userToken: this.userToken,
      timestamp: Date.now()
    }

    try {
      const storageKey = this.getNamespacedKey(this.CONFORMANCE_CLAIMS_STORAGE_KEY)
      localStorage.setItem(storageKey, JSON.stringify(sessionData))
    } catch (error) {
      console.error('Error saving Conformance Claims data to session:', error)
    }
  }

  /**
   * Load Conformance Claims data from session storage
   */
  loadConformanceClaimsData(): ConformanceClaimsSessionData | null {
    try {
      const storageKey = this.getNamespacedKey(this.CONFORMANCE_CLAIMS_STORAGE_KEY)
      const data = localStorage.getItem(storageKey)

      if (!data) {
        return null
      }

      const sessionData: ConformanceClaimsSessionData = JSON.parse(data)

      if (sessionData.userToken !== this.userToken) {
        console.warn('Session token mismatch, ignoring stored Conformance Claims data')
        return null
      }

      return sessionData
    } catch (error) {
      console.error('Error loading Conformance Claims data from session:', error)
      return null
    }
  }

  /**
   * Clear Conformance Claims session data
   */
  clearConformanceClaimsData(): void {
    try {
      const storageKey = this.getNamespacedKey(this.CONFORMANCE_CLAIMS_STORAGE_KEY)
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.error('Error clearing Conformance Claims data from session:', error)
    }
  }
}

// Export singleton instance
export const sessionService = new SessionService()
