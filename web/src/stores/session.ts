import { defineStore } from 'pinia'
import api from '../services/api'

const storageKey = 'ccgen-user-id'

type CoverFields = {
  title: string
  version: string
  revision: string
  description: string
  manufacturer: string
  date: string
}

type CoverSection = {
  fields: CoverFields
  image_path: string
  html: string
}

type StReferenceFields = {
  st_title: string
  st_version: string
  st_date: string
  author: string
}

type SectionWithFields<T> = {
  fields: T
  html: string
}

type ToeReferenceFields = {
  toe_name: string
  toe_version: string
  toe_identification: string
  toe_type: string
}

type ToeReferenceSection = {
  fields: ToeReferenceFields
  rich_text: ToeReferenceFields
  html: string
}

type ToeOverviewFields = {
  overview: string
  toe_type: string
  toe_usage: string
  toe_security_features: string
  non_toe_hw: string
}

type ToeDescriptionFields = {
  physical_scope: string
  logical_scope: string
}

type SessionResponse = {
  cover: CoverSection
  st_reference: SectionWithFields<StReferenceFields>
  toe_reference: ToeReferenceSection
  toe_overview: SectionWithFields<ToeOverviewFields>
  toe_description: SectionWithFields<ToeDescriptionFields>
}

export const useSessionStore = defineStore('session', {
  state: () => ({
    userId: '' as string,
    loaded: false,
    loading: false,
    loadPromise: null as Promise<void> | null,
    cover: {
      fields: {
        title: '',
        version: '',
        revision: '',
        description: '',
        manufacturer: '',
        date: ''
      },
      image_path: '',
      html: ''
    } as CoverSection,
    stReference: {
      fields: {
        st_title: '',
        st_version: '',
        st_date: '',
        author: ''
      },
      html: ''
    } as SectionWithFields<StReferenceFields>,
    toeReference: {
      fields: {
        toe_name: '',
        toe_version: '',
        toe_identification: '',
        toe_type: ''
      },
      rich_text: {
        toe_name: '',
        toe_version: '',
        toe_identification: '',
        toe_type: ''
      },
      html: ''
    } as ToeReferenceSection,
    toeOverview: {
      fields: {
        overview: '',
        toe_type: '',
        toe_usage: '',
        toe_security_features: '',
        non_toe_hw: ''
      },
      html: ''
    } as SectionWithFields<ToeOverviewFields>,
    toeDescription: {
      fields: {
        physical_scope: '',
        logical_scope: ''
      },
      html: ''
    } as SectionWithFields<ToeDescriptionFields>
  }),
  actions: {
    ensureUserId(): string {
      if (this.userId) return this.userId

      if (typeof window === 'undefined') return ''

      const existing = window.localStorage.getItem(storageKey)
      if (existing) {
        this.userId = existing
        return existing
      }

      const generated = typeof crypto !== 'undefined' && 'randomUUID' in crypto
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2)

      this.userId = generated
      window.localStorage.setItem(storageKey, generated)
      return generated
    },
    setUserId(id: string) {
      this.userId = id
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(storageKey, id)
      }
    },
    async loadSession(force = false): Promise<void> {
      if (!this.userId) {
        this.ensureUserId()
      }

      if (!this.userId) return

      if (this.loaded && !force) {
        return
      }

      if (this.loadPromise && !force) {
        return this.loadPromise
      }

      this.loading = true
      this.loadPromise = (async () => {
        try {
          const response = await api.get<SessionResponse>(`/st-introduction/${this.userId}`)
          const data = response.data
          if (data) {
            this.cover = data.cover
            this.stReference = data.st_reference
            this.toeReference = data.toe_reference
            this.toeOverview = data.toe_overview
            this.toeDescription = data.toe_description
          }
        } catch (error) {
          console.error('Failed to load ST introduction session data', error)
        } finally {
          this.loaded = true
          this.loading = false
          this.loadPromise = null
        }
      })()

      return this.loadPromise
    },
    updateCover(section: Partial<CoverSection>) {
      this.cover = {
        ...this.cover,
        ...section,
        fields: {
          ...this.cover.fields,
          ...(section.fields ?? {})
        }
      }
    },
    updateStReference(section: Partial<SectionWithFields<StReferenceFields>>) {
      this.stReference = {
        ...this.stReference,
        ...section,
        fields: {
          ...this.stReference.fields,
          ...(section?.fields ?? {})
        }
      }
    },
    updateToeReference(section: Partial<ToeReferenceSection>) {
      this.toeReference = {
        ...this.toeReference,
        ...section,
        fields: {
          ...this.toeReference.fields,
          ...(section?.fields ?? {})
        },
        rich_text: {
          ...this.toeReference.rich_text,
          ...(section?.rich_text ?? {})
        }
      }
    },
    updateToeOverview(section: Partial<SectionWithFields<ToeOverviewFields>>) {
      this.toeOverview = {
        ...this.toeOverview,
        ...section,
        fields: {
          ...this.toeOverview.fields,
          ...(section?.fields ?? {})
        }
      }
    },
    updateToeDescription(section: Partial<SectionWithFields<ToeDescriptionFields>>) {
      this.toeDescription = {
        ...this.toeDescription,
        ...section,
        fields: {
          ...this.toeDescription.fields,
          ...(section?.fields ?? {})
        }
      }
    }
  }
})
