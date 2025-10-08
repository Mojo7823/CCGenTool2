<template>
  <div class="page">
    <div class="card">
      <header class="card-header">
        <div>
          <h1>ST Introduction Preview</h1>
          <p class="subtitle">Generate and download a consolidated ST Introduction document.</p>
        </div>
        <div class="actions">
          <button class="btn primary" type="button" @click="generatePreview" :disabled="previewLoading">
            {{ previewLoading ? 'Generating…' : 'Generate Preview' }}
          </button>
          <a
            v-if="docxPath"
            class="btn"
            :href="downloadHref"
            target="_blank"
            rel="noopener"
            download
          >Download DOCX</a>
        </div>
      </header>
      <section class="preview-grid">
        <div class="preview-pane">
          <h2>Combined HTML</h2>
          <div class="html-preview" v-if="combinedHtml" v-html="combinedHtml"></div>
          <p v-else class="placeholder">No ST Introduction content available yet.</p>
        </div>
        <div class="preview-pane">
          <h2>DOCX Preview</h2>
          <div class="docx-preview-shell">
            <div v-if="previewLoading" class="modal-status">Generating preview…</div>
            <div v-else-if="previewError" class="modal-error">{{ previewError }}</div>
            <div
              ref="docxPreviewContainer"
              class="docx-preview-container"
              :class="{ hidden: previewLoading || !!previewError }"
            ></div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import { getOrCreateUserId } from '../utils/user'
import {
  cleanupStIntroductionPreview,
  cleanupStIntroductionSession,
  generateStIntroductionPreview,
} from '../services/stIntroductionService'
import api from '../services/api'

const userId = ref('')
const combinedHtml = ref('')
const docxPath = ref('')
const previewLoading = ref(false)
const previewError = ref('')
const docxPreviewContainer = ref<HTMLDivElement | null>(null)

const downloadHref = computed(() => docxPath.value ? api.getUri({ url: docxPath.value }) : '#')

async function generatePreview() {
  if (!userId.value) {
    previewError.value = 'Unable to determine user session identifier.'
    return
  }
  previewLoading.value = true
  previewError.value = ''
  await cleanupExistingPreview()
  try {
    const response = await generateStIntroductionPreview(userId.value)
    combinedHtml.value = response.html_content
    docxPath.value = response.path
    await nextTick()
    await renderDocxPreview()
  } catch (error: any) {
    previewError.value = error?.response?.data?.detail || error?.message || 'Failed to generate preview.'
  } finally {
    previewLoading.value = false
  }
}

async function renderDocxPreview() {
  if (!docxPreviewContainer.value || !docxPath.value) return
  try {
    docxPreviewContainer.value.innerHTML = ''
    const response = await api.get(docxPath.value, { responseType: 'arraybuffer' })
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

async function cleanupExistingPreview() {
  if (!userId.value || !docxPath.value) return
  await cleanupStIntroductionPreview(userId.value)
  docxPath.value = ''
}

function handleBeforeUnload() {
  if (!userId.value) return
  cleanupStIntroductionSession(userId.value, true)
}

onMounted(() => {
  userId.value = getOrCreateUserId()
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handleBeforeUnload)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('beforeunload', handleBeforeUnload)
    window.removeEventListener('pagehide', handleBeforeUnload)
  }
  cleanupExistingPreview()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 24px;
}

.subtitle {
  margin: 4px 0 0;
  color: var(--muted);
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.preview-pane {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.html-preview {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  padding: 16px;
  background: rgba(15, 23, 42, 0.25);
  max-height: 420px;
  overflow: auto;
}

.placeholder {
  color: var(--muted);
}

.docx-preview-shell {
  position: relative;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  min-height: 360px;
  background: rgba(15, 23, 42, 0.25);
  padding: 16px;
}

.docx-preview-container.hidden {
  display: none;
}

.modal-status {
  text-align: center;
  padding: 32px 0;
  color: var(--muted);
}

.modal-error {
  color: #f87171;
  padding: 16px;
}
</style>
