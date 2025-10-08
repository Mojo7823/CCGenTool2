import { defineStore } from 'pinia'
import { reactive, ref, watch } from 'vue'

export type StIntroductionSection =
  | 'cover'
  | 'st-reference'
  | 'toe-reference'
  | 'toe-overview'
  | 'toe-description'

interface CoverFormState {
  title: string
  version: string
  revision: string
  description: string
  manufacturer: string
  date: string
}

interface StReferenceState {
  stTitle: string
  stVersion: string
  stDate: string
  author: string
}

interface ToeReferenceState {
  toeName: string
  toeVersion: string
  toeIdentification: string
  toeType: string
}

interface ToeOverviewState {
  overview: string
  toeType: string
  usage: string
  securityFeatures: string
  nonToe: string
}

interface ToeDescriptionState {
  physicalScope: string
  logicalScope: string
}

interface PersistedState {
  coverForm: CoverFormState
  coverImagePath: string | null
  stReference: StReferenceState
  toeReference: ToeReferenceState
  toeOverview: ToeOverviewState
  toeDescription: ToeDescriptionState
}

const STORAGE_KEY = 'ccgentool2_st_introduction'

function createDefaultState(): PersistedState {
  return {
    coverForm: {
      title: '',
      version: '',
      revision: '',
      description: '',
      manufacturer: '',
      date: ''
    },
    coverImagePath: null,
    stReference: {
      stTitle: '',
      stVersion: '',
      stDate: '',
      author: ''
    },
    toeReference: {
      toeName: '',
      toeVersion: '',
      toeIdentification: '',
      toeType: ''
    },
    toeOverview: {
      overview: '',
      toeType: '',
      usage: '',
      securityFeatures: '',
      nonToe: ''
    },
    toeDescription: {
      physicalScope: '',
      logicalScope: ''
    }
  }
}

export const useStIntroductionStore = defineStore('stIntroduction', () => {
  const coverForm = reactive<CoverFormState>({ ...createDefaultState().coverForm })
  const coverImagePath = ref<string | null>(null)
  const stReference = reactive<StReferenceState>({ ...createDefaultState().stReference })
  const toeReference = reactive<ToeReferenceState>({ ...createDefaultState().toeReference })
  const toeOverview = reactive<ToeOverviewState>({ ...createDefaultState().toeOverview })
  const toeDescription = reactive<ToeDescriptionState>({ ...createDefaultState().toeDescription })

  function persist() {
    if (typeof window === 'undefined') return
    const payload: PersistedState = {
      coverForm: { ...coverForm },
      coverImagePath: coverImagePath.value,
      stReference: { ...stReference },
      toeReference: { ...toeReference },
      toeOverview: { ...toeOverview },
      toeDescription: { ...toeDescription }
    }
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    } catch (error) {
      console.error('Failed to persist ST Introduction state:', error)
    }
  }

  function load() {
    if (typeof window === 'undefined') return
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return

    try {
      const parsed = JSON.parse(raw) as Partial<PersistedState>
      if (parsed.coverForm) {
        Object.assign(coverForm, parsed.coverForm)
      }
      if (Object.prototype.hasOwnProperty.call(parsed, 'coverImagePath')) {
        coverImagePath.value = parsed.coverImagePath ?? null
      }
      if (parsed.stReference) {
        Object.assign(stReference, parsed.stReference)
      }
      if (parsed.toeReference) {
        Object.assign(toeReference, parsed.toeReference)
      }
      if (parsed.toeOverview) {
        Object.assign(toeOverview, parsed.toeOverview)
      }
      if (parsed.toeDescription) {
        Object.assign(toeDescription, parsed.toeDescription)
      }
    } catch (error) {
      console.error('Failed to load ST Introduction state:', error)
    }
  }

  if (typeof window !== 'undefined') {
    load()
    watch(
      () => ({
        coverForm: { ...coverForm },
        coverImagePath: coverImagePath.value,
        stReference: { ...stReference },
        toeReference: { ...toeReference },
        toeOverview: { ...toeOverview },
        toeDescription: { ...toeDescription }
      }),
      persist,
      { deep: false }
    )
  }

  function reset() {
    const defaults = createDefaultState()
    Object.assign(coverForm, defaults.coverForm)
    coverImagePath.value = defaults.coverImagePath
    Object.assign(stReference, defaults.stReference)
    Object.assign(toeReference, defaults.toeReference)
    Object.assign(toeOverview, defaults.toeOverview)
    Object.assign(toeDescription, defaults.toeDescription)
    persist()
  }

  return {
    coverForm,
    coverImagePath,
    stReference,
    toeReference,
    toeOverview,
    toeDescription,
    reset,
    persist,
    load
  }
})
