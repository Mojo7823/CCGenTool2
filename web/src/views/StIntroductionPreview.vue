<template>
  <div class="preview-page">
    <div class="card intro-card">
      <h1>ST Introduction Preview</h1>
      <p>Generate a combined DOCX document containing the Cover, ST Reference, TOE Reference, TOE Overview, and TOE Description sections.</p>
      <div class="preview-actions">
        <button class="btn primary" type="button" @click="generatePreview" :disabled="previewLoading">Generate Preview</button>
        <a v-if="docxPath" class="btn" :href="downloadUrl" download="st-introduction.docx">Download DOCX</a>
      </div>
      <p v-if="previewError" class="status error">{{ previewError }}</p>
      <p v-else-if="previewLoading" class="status">Generating preview…</p>
      <p v-else-if="docxPath" class="status success">Preview generated. You can download the DOCX file or review it below.</p>
      <p v-else class="status">Changes are saved automatically. Generate a preview to see the combined output.</p>
    </div>

    <div class="card preview-card">
      <div class="docx-preview-shell">
        <div v-if="previewLoading" class="modal-status overlay">Generating preview…</div>
        <div v-else-if="previewError" class="modal-error">{{ previewError }}</div>
        <div
          ref="docxPreviewContainer"
          class="docx-preview-container"
          :class="{ hidden: previewLoading || !!previewError || !docxPath }"
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
import { cleanupStIntroductionPreview, generateStIntroductionPreview } from '../services/stIntroduction'

const session = useSessionStore()

const previewLoading = ref(false)
const previewError = ref('')
const docxPath = ref<string | null>(null)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)

const downloadUrl = computed(() => {
  if (!docxPath.value) return '#'
  return api.getUri({ url: docxPath.value })
})

async function generatePreview() {
  if (!session.userId) {
    session.ensureUserId()
  }
  if (!session.userId) {
    previewError.value = 'Unable to determine user session identifier.'
    return
  }

  await session.loadSession()

  await cleanupPreview()

  previewLoading.value = true
  previewError.value = ''

  try {
    const response = await generateStIntroductionPreview(session.userId)
    const path: string | undefined = response?.path
    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }
    docxPath.value = path
    await nextTick()
    await renderPreview(path)
  } catch (error: any) {
    previewError.value = error?.response?.data?.detail || error?.message || 'Unable to generate preview.'
    await cleanupPreview()
  } finally {
    previewLoading.value = false
  }
}

async function renderPreview(path: string) {
  if (!docxPreviewContainer.value) return
  try {
    docxPreviewContainer.value.innerHTML = ''
    const response = await api.get(path, { responseType: 'arraybuffer' })
    const buffer = response.data as ArrayBuffer
    await renderAsync(buffer, docxPreviewContainer.value, undefined, {
      className: 'docx-rendered',
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      useBase64URL: true,
    })
  } catch (error: any) {
    previewError.value = error?.message || 'Failed to render DOCX preview.'
  }
}

async function cleanupPreview(keepalive = false) {
  if (!session.userId || !docxPath.value) return
  try {
    if (keepalive) {
      const url = api.getUri({ url: `/st-introduction/docx/${session.userId}` })
      await fetch(url, { method: 'DELETE', keepalive: true }).catch(() => undefined)
    } else {
      await cleanupStIntroductionPreview(session.userId)
    }
  } catch {
    // Ignore cleanup errors
  } finally {
    docxPath.value = null
  }
}

function removeEventListeners() {
  if (typeof window === 'undefined') return
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
}

function handleBeforeUnload() {
  void cleanupPreview(true)
}

function handlePageHide() {
  void cleanupPreview(true)
}

onMounted(() => {
  session.ensureUserId()
  session.loadSession().catch(() => undefined)
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handlePageHide)
  }
})

onBeforeUnmount(() => {
  void cleanupPreview()
  removeEventListeners()
})
</script>

<style scoped>
.preview-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.status {
  margin-top: 12px;
  color: var(--muted);
}

.status.success {
  color: var(--success);
}

.status.error,
.modal-error {
  color: var(--danger);
}

.preview-card {
  padding: 0;
}

.docx-preview-shell {
  position: relative;
  min-height: 320px;
  padding: 24px;
}

.docx-preview-container {
  max-height: 640px;
  overflow: auto;
  background: rgba(15, 23, 42, 0.45);
  border-radius: 12px;
  padding: 16px;
}

.docx-preview-container.hidden {
  display: none;
}

.modal-status.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.85);
  border-radius: 12px;
  font-weight: 600;
}

.modal-error {
  padding: 16px;
  background: rgba(127, 29, 29, 0.3);
  border-radius: 12px;
}
</style>
