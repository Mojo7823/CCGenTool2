<template>
  <div class="st-intro-page">
    <div class="card section-header">
      <h1>ST Introduction Preview</h1>
      <p class="section-subtitle">
        Combine the Cover, ST Reference, TOE Reference, TOE Overview, and TOE Description sections into a single document.
      </p>
    </div>

    <div class="card readiness-card">
      <h2>Section Status</h2>
      <ul>
        <li v-for="section in sectionStatus" :key="section.key">
          <span>{{ section.label }}</span>
          <span :class="['badge', section.ready ? 'ok' : 'degraded']">{{ section.ready ? 'Ready' : 'Missing' }}</span>
        </li>
      </ul>
    </div>

    <div class="card actions-card">
      <div class="actions">
        <button class="btn primary" type="button" @click="generatePreview" :disabled="previewLoading">
          {{ previewLoading ? 'Generating…' : 'Generate Preview' }}
        </button>
        <a
          v-if="downloadUrl"
          class="btn"
          :href="downloadUrl"
          download
        >Download DOCX</a>
      </div>
      <p class="hint">Ensure each section is filled before generating the preview.</p>
    </div>

    <div class="card preview-card">
      <h2>Preview</h2>
      <div class="preview-shell">
        <div v-if="previewLoading" class="preview-status">Generating preview…</div>
        <div v-else-if="previewError" class="preview-error">{{ previewError }}</div>
        <div
          v-else
          ref="previewContainer"
          class="docx-preview-container"
          :class="{ hidden: !docxPath }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { useSessionStore } from '../stores/session'

const sessionStore = useSessionStore()
const previewContainer = ref<HTMLDivElement | null>(null)
const previewLoading = ref(false)
const previewError = ref('')
const docxPath = ref('')
let beforeUnloadHandler: (() => void) | null = null

const sectionStatus = computed(() => [
  { key: 'cover', label: 'Cover', ready: !!sessionStore.cover.html },
  { key: 'stReference', label: 'ST Reference', ready: !!sessionStore.stReference.html },
  { key: 'toeReference', label: 'TOE Reference', ready: !!sessionStore.toeReference.html },
  { key: 'toeOverview', label: 'TOE Overview', ready: !!sessionStore.toeOverview.html },
  { key: 'toeDescription', label: 'TOE Description', ready: !!sessionStore.toeDescription.html },
])

const downloadUrl = computed(() => (docxPath.value ? api.getUri({ url: docxPath.value }) : ''))

function attachUnloadListeners() {
  if (typeof window === 'undefined' || beforeUnloadHandler) return
  beforeUnloadHandler = () => {
    cleanupDocx(true)
  }
  window.addEventListener('beforeunload', beforeUnloadHandler)
  window.addEventListener('pagehide', beforeUnloadHandler)
}

function detachUnloadListeners() {
  if (typeof window === 'undefined' || !beforeUnloadHandler) return
  window.removeEventListener('beforeunload', beforeUnloadHandler)
  window.removeEventListener('pagehide', beforeUnloadHandler)
  beforeUnloadHandler = null
}

async function renderDocx(path: string) {
  if (!previewContainer.value) return
  try {
    previewContainer.value.innerHTML = ''
    const response = await api.get(path, { responseType: 'arraybuffer' })
    const buffer = response.data as ArrayBuffer
    await renderAsync(buffer, previewContainer.value, undefined, {
      className: 'docx-rendered',
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      useBase64URL: true,
    })
  } catch (error: any) {
    previewError.value = error?.message || 'Unable to render preview.'
  }
}

async function deleteExistingPreview() {
  if (!sessionStore.userId || !docxPath.value) return
  try {
    await api.delete(`/st-introduction/preview/${sessionStore.userId}`)
  } catch (error) {
    console.warn('Failed to clean previous ST Introduction preview', error)
  }
  docxPath.value = ''
  sessionStore.clearStIntroductionDocxPath()
  if (previewContainer.value) {
    previewContainer.value.innerHTML = ''
  }
}

function cleanupDocx(keepalive = false) {
  if (!sessionStore.userId || !docxPath.value) return
  const url = api.getUri({ url: `/st-introduction/preview/${sessionStore.userId}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  docxPath.value = ''
  sessionStore.clearStIntroductionDocxPath()
}

async function generatePreview() {
  previewError.value = ''
  previewLoading.value = true
  await sessionStore.initialize()

  try {
    await deleteExistingPreview()
    if (!sessionStore.userId) {
      throw new Error('Unable to determine user session identifier.')
    }
    const response = await api.post('/st-introduction/preview', {
      user_id: sessionStore.userId,
    })
    const path: string | undefined = response.data?.path
    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }
    docxPath.value = path
    sessionStore.setStIntroductionDocxPath(path)
    await nextTick()
    await renderDocx(path)
    attachUnloadListeners()
  } catch (error: any) {
    previewError.value = error?.response?.data?.detail || error?.message || 'Unable to generate preview.'
  } finally {
    previewLoading.value = false
  }
}

onMounted(async () => {
  await sessionStore.initialize()
  const existingPath = sessionStore.stIntroductionDocxPath
  if (existingPath) {
    docxPath.value = existingPath
    await nextTick()
    await renderDocx(existingPath)
    attachUnloadListeners()
  }
})

onBeforeUnmount(() => {
  detachUnloadListeners()
})
</script>

<style scoped>
.st-intro-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-subtitle {
  color: var(--muted);
  margin: 0;
}

.readiness-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.readiness-card li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(15, 23, 42, 0.45);
  border-radius: 8px;
  padding: 8px 12px;
}

.actions-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hint {
  margin: 0;
  color: var(--muted);
}

.preview-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-shell {
  min-height: 240px;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 16px;
  background: rgba(15, 23, 42, 0.35);
  position: relative;
}

.preview-status {
  color: var(--muted);
}

.preview-error {
  color: #f87171;
}

.docx-preview-container {
  max-height: 480px;
  overflow: auto;
}

.docx-preview-container.hidden {
  display: none;
}
</style>
