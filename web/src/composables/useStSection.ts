import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import type { AxiosResponse } from 'axios'
import { getOrCreateUserId } from '../services/userSession'
import { loadSection, saveSection as saveLocalSection } from '../services/stIntroductionSessionService'
import type { SectionResponse } from '../types/st-introduction'

interface SectionOptions<T extends Record<string, any>> {
  sectionKey: string
  defaults: () => T
  fetchSection: (userId: string) => Promise<SectionResponse<T>>
  saveSection: (userId: string, data: T) => Promise<AxiosResponse<SectionResponse<T>>>
  transformBeforeSave?: (data: T) => T
}

export function useStSection<T extends Record<string, any>>(options: SectionOptions<T>) {
  const form = reactive(options.defaults())
  const userId = ref('')
  const isReady = ref(false)
  const saving = ref(false)
  const saveError = ref('')
  const lastSavedAt = ref<number | null>(null)
  const pendingSave = ref(false)
  const loadError = ref('')
  let autosaveHandle: number | undefined

  const saveStatus = computed(() => {
    if (saving.value) {
      return { text: 'Saving…', state: 'saving' as const }
    }
    if (saveError.value) {
      return { text: saveError.value, state: 'error' as const }
    }
    if (lastSavedAt.value) {
      const time = new Date(lastSavedAt.value)
      return { text: `Saved ${time.toLocaleTimeString()}`, state: 'saved' as const }
    }
    return { text: '', state: 'idle' as const }
  })

  function buildPayload(): T {
    const copy = { ...form } as T
    return options.transformBeforeSave ? options.transformBeforeSave(copy) : copy
  }

  function persistLocally() {
    if (!userId.value) return
    saveLocalSection(options.sectionKey, userId.value, buildPayload())
  }

  function cancelAutosave() {
    if (autosaveHandle !== undefined) {
      window.clearTimeout(autosaveHandle)
      autosaveHandle = undefined
    }
  }

  function scheduleSave(immediate = false) {
    if (!isReady.value || !userId.value) return

    if (autosaveHandle !== undefined) {
      window.clearTimeout(autosaveHandle)
      autosaveHandle = undefined
    }

    if (immediate) {
      void triggerSave()
      return
    }

    autosaveHandle = window.setTimeout(() => {
      autosaveHandle = undefined
      void triggerSave()
    }, 600)
  }

  async function triggerSave() {
    if (!userId.value || !isReady.value) return
    if (saving.value) {
      pendingSave.value = true
      return
    }

    saving.value = true
    saveError.value = ''
    const payload = buildPayload()

    try {
      const response = await options.saveSection(userId.value, payload)
      const updatedAt = response.data.updated_at
      if (updatedAt) {
        const parsed = Date.parse(updatedAt)
        if (!Number.isNaN(parsed)) {
          lastSavedAt.value = parsed
        }
      } else {
        lastSavedAt.value = Date.now()
      }
    } catch (error: any) {
      saveError.value = error?.response?.data?.detail || error?.message || 'Failed to save section.'
    } finally {
      saving.value = false
      if (pendingSave.value) {
        pendingSave.value = false
        scheduleSave(true)
      }
    }
  }

  async function initialise() {
    const id = getOrCreateUserId()
    if (!id) return
    userId.value = id

    const localData = loadSection(options.sectionKey, id, options.defaults())
    Object.assign(form, localData)

    try {
      const remote = await options.fetchSection(id)
      if (remote?.data) {
        Object.assign(form, remote.data)
      }
      if (remote?.updated_at) {
        const parsed = Date.parse(remote.updated_at)
        if (!Number.isNaN(parsed)) {
          lastSavedAt.value = parsed
        }
      }
    } catch (error: any) {
      console.error(`Failed to load ${options.sectionKey} section from server`, error)
      loadError.value = error?.message || 'Failed to load data.'
    }

    isReady.value = true
    persistLocally()
  }

  watch(
    form,
    () => {
      if (!isReady.value) return
      persistLocally()
      scheduleSave()
    },
    { deep: true }
  )

  onMounted(() => {
    void initialise()
  })

  onBeforeUnmount(() => {
    cancelAutosave()
  })

  return {
    form,
    userId,
    isReady,
    saving,
    saveError,
    lastSavedAt,
    saveStatus,
    loadError,
    scheduleImmediateSave: () => scheduleSave(true),
  }
}
