import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import api from '../services/api'

export type SectionKey = 'cover' | 'stReference' | 'toeReference' | 'toeOverview' | 'toeDescription'

const SECTION_TO_SERVER: Record<SectionKey, string> = {
  cover: 'cover',
  stReference: 'st_reference',
  toeReference: 'toe_reference',
  toeOverview: 'toe_overview',
  toeDescription: 'toe_description',
}

export const useSessionStore = defineStore('session', () => {
  const storageKey = 'ccgen-user-id'
  const userId = ref('')
  const initializing = ref(false)
  const initialized = ref(false)

  const cover = reactive({
    fields: {
      title: '',
      version: '',
      revision: '',
      description: '',
      manufacturer: '',
      date: '',
    },
    imagePath: '',
    html: '',
  })

  const stReference = reactive({
    title: '',
    version: '',
    date: '',
    author: '',
    html: '',
  })

  const toeReference = reactive({
    toeName: '',
    toeVersion: '',
    toeIdentification: '',
    toeType: '',
    html: '',
  })

  const toeOverview = reactive({
    overview: '',
    toeType: '',
    toeUsage: '',
    securityFeatures: '',
    nonToe: '',
    html: '',
  })

  const toeDescription = reactive({
    physicalScope: '',
    logicalScope: '',
    html: '',
  })

  const stIntroductionDocxPath = ref('')

  function ensureUserId() {
    if (typeof window === 'undefined') return
    if (userId.value) return

    const existing = window.localStorage.getItem(storageKey)
    if (existing) {
      userId.value = existing
      return
    }

    const generated = typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2)
    userId.value = generated
    window.localStorage.setItem(storageKey, generated)
  }

  function applyCoverData(payload: any) {
    if (!payload) return
    const data = payload.data ?? payload.fields ?? {}
    if (data.fields && typeof data.fields === 'object') {
      Object.assign(cover.fields, data.fields)
    } else {
      Object.assign(cover.fields, data)
    }
    if (typeof data.image_path === 'string') {
      cover.imagePath = data.image_path
    } else if (typeof payload.image_path === 'string') {
      cover.imagePath = payload.image_path
    }
    if (typeof payload.html === 'string') {
      cover.html = payload.html
    }
  }

  function applySimpleSection(target: Record<string, any>, payload: any) {
    if (!payload) return
    const data = payload.data ?? {}
    if (data && typeof data === 'object') {
      Object.assign(target, data)
    }
    if (typeof payload.html === 'string') {
      target.html = payload.html
    }
  }

  async function initialize() {
    if (initialized.value || initializing.value) return

    ensureUserId()
    if (!userId.value) return

    initializing.value = true
    try {
      const response = await api.get(`/session/${userId.value}`)
      const sections = response.data?.sections ?? {}
      applyCoverData(sections.cover)
      applySimpleSection(stReference, sections.st_reference)
      applySimpleSection(toeReference, sections.toe_reference)
      applySimpleSection(toeOverview, sections.toe_overview)
      applySimpleSection(toeDescription, sections.toe_description)
    } catch (error) {
      console.error('Failed to load session data', error)
    } finally {
      initializing.value = false
      initialized.value = true
    }
  }

  async function saveSection(section: SectionKey, payload: { data?: Record<string, any>; html?: string }) {
    ensureUserId()
    if (!userId.value) throw new Error('Unable to determine user session identifier.')

    const request: Record<string, any> = {
      user_id: userId.value,
      section: SECTION_TO_SERVER[section],
    }

    if (payload.data !== undefined) {
      request.data = payload.data
    }

    if (payload.html !== undefined) {
      request.html_content = payload.html
    }

    await api.post('/session/section', request)
  }

  function setStIntroductionDocxPath(path: string) {
    stIntroductionDocxPath.value = path
  }

  function clearStIntroductionDocxPath() {
    stIntroductionDocxPath.value = ''
  }

  return {
    userId,
    cover,
    stReference,
    toeReference,
    toeOverview,
    toeDescription,
    stIntroductionDocxPath,
    initializing,
    initialized,
    ensureUserId,
    initialize,
    saveSection,
    setStIntroductionDocxPath,
    clearStIntroductionDocxPath,
  }
})
