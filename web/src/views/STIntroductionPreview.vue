<template>
  <div class="st-preview-page">
    <div class="card summary-card">
      <div class="summary-header">
        <div>
          <h1>ST Introduction Preview</h1>
          <p>Combine the Cover, ST Reference, TOE Reference, TOE Overview, and TOE Description into a single document.</p>
        </div>
        <div class="save-status" :class="[`state-${statusText.state}`, { empty: !statusText.text }]" role="status" aria-live="polite">
          {{ statusText.text || ' ' }}
        </div>
      </div>

      <ul class="section-status">
        <li
          v-for="section in sectionDefinitions"
          :key="section.key"
          :class="{ complete: sectionStatuses[section.key] }">
          <span class="indicator">{{ sectionStatuses[section.key] ? '✔' : '○' }}</span>
          <span>{{ section.label }}</span>
        </li>
      </ul>

      <div class="actions">
        <button class="btn primary" type="button" @click="generatePreview" :disabled="generating">
          {{ generating ? 'Generating…' : 'Generate ST Introduction Preview' }}
        </button>
        <a
          v-if="hasDocx"
          class="btn secondary"
          :href="downloadUrl"
          download
        >
          Download DOCX
        </a>
      </div>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="lastGeneratedLabel" class="hint">Last generated: {{ lastGeneratedLabel }}</p>
    </div>

    <div class="card preview-card">
      <h2>Preview</h2>
      <div class="preview-shell">
        <div v-if="generating" class="preview-status">Generating preview…</div>
        <div v-else-if="errorMessage" class="preview-error">{{ errorMessage }}</div>
        <div v-else-if="!hasDocx" class="preview-placeholder">
          Generate the preview to see the combined document.
        </div>
        <div ref="previewContainer" class="docx-preview" v-show="hasDocx"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { getOrCreateUserId } from '../services/userSession'
import {
  fetchCoverSection,
  fetchStReferenceSection,
  fetchToeReferenceSection,
  fetchToeOverviewSection,
  fetchToeDescriptionSection,
  generateStIntroductionPreview,
} from '../services/stIntroductionApi'
import type { StIntroductionPreviewResponse } from '../types/st-introduction'

const userId = ref('')
const generating = ref(false)
const errorMessage = ref('')
const docxPath = ref('')
const lastGeneratedAt = ref<number | null>(null)
const previewContainer = ref<HTMLDivElement | null>(null)
const sectionStatuses = reactive<Record<string, boolean>>({
  cover: false,
  st_reference: false,
  toe_reference: false,
  toe_overview: false,
  toe_description: false,
})

const sectionDefinitions = [
  { key: 'cover', label: 'Cover' },
  { key: 'st_reference', label: 'ST Reference' },
  { key: 'toe_reference', label: 'TOE Reference' },
  { key: 'toe_overview', label: 'TOE Overview' },
  { key: 'toe_description', label: 'TOE Description' },
] as const

const hasDocx = computed(() => !!docxPath.value)
const downloadUrl = computed(() => (docxPath.value ? api.getUri({ url: docxPath.value }) : ''))
const lastGeneratedLabel = computed(() => {
  if (!lastGeneratedAt.value) return ''
  const date = new Date(lastGeneratedAt.value)
  return date.toLocaleString()
})
const statusText = computed(() => {
  if (generating.value) {
    return { text: 'Generating preview…', state: 'saving' as const }
  }
  if (errorMessage.value) {
    return { text: errorMessage.value, state: 'error' as const }
  }
  if (lastGeneratedAt.value) {
    return { text: 'Preview is up to date', state: 'saved' as const }
  }
  return { text: '', state: 'idle' as const }
})

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
    errorMessage.value = error?.message || 'Failed to render preview document.'
  }
}

async function loadSectionStatuses() {
  if (!userId.value) return
  try {
    const [
      cover,
      stRef,
      toeRef,
      toeOverview,
      toeDescription,
    ] = await Promise.all([
      fetchCoverSection(userId.value).then(res => res.data),
      fetchStReferenceSection(userId.value).then(res => res.data),
      fetchToeReferenceSection(userId.value).then(res => res.data),
      fetchToeOverviewSection(userId.value).then(res => res.data),
      fetchToeDescriptionSection(userId.value).then(res => res.data),
    ])

    sectionStatuses.cover = !!cover?.html
    sectionStatuses.st_reference = !!stRef?.html
    sectionStatuses.toe_reference = !!toeRef?.html
    sectionStatuses.toe_overview = !!toeOverview?.html
    sectionStatuses.toe_description = !!toeDescription?.html
  } catch (error) {
    console.error('Failed to load ST introduction section statuses', error)
  }
}

async function generatePreview() {
  if (!userId.value) return
  generating.value = true
  errorMessage.value = ''
  try {
    const response = await generateStIntroductionPreview(userId.value)
    const data: StIntroductionPreviewResponse = response.data
    docxPath.value = data.path
    lastGeneratedAt.value = Date.now()
    if (data.sections) {
      for (const key of Object.keys(sectionStatuses)) {
        sectionStatuses[key] = !!data.sections[key as keyof typeof data.sections]
      }
    }
    await nextTick()
    await renderDocx(data.path)
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || error?.message || 'Failed to generate preview.'
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  userId.value = getOrCreateUserId()
  await loadSectionStatuses()
})
</script>

<style scoped>
.st-preview-page {
  display: grid;
  gap: 24px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.summary-header h1 {
  margin: 0 0 8px 0;
}

.summary-header p {
  margin: 0;
  color: var(--muted);
}

.save-status {
  min-width: 180px;
  text-align: right;
  font-size: 0.875rem;
  color: var(--muted);
  white-space: nowrap;
}

.save-status.empty {
  color: transparent;
}

.save-status.state-saving {
  color: var(--muted);
}

.save-status.state-error {
  color: var(--danger);
}

.save-status.state-saved {
  color: #34d399;
}

.section-status {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin: 0;
  padding: 0;
}

.section-status li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid #1f2937;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.35);
}

.section-status li.complete {
  border-color: #34d399;
}

.indicator {
  font-weight: 600;
  width: 24px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.error {
  color: var(--danger);
  margin: 0;
}

.hint {
  margin: 0;
  color: var(--muted);
}

.preview-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.preview-card h2 {
  margin: 0;
}

.preview-shell {
  min-height: 320px;
  background: #d1d5db;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  position: relative;
}

.preview-status,
.preview-error,
.preview-placeholder {
  text-align: center;
  font-weight: 500;
  color: var(--muted);
}

.preview-error {
  color: var(--danger);
}

.docx-preview {
  width: 100%;
  display: flex;
  justify-content: center;
}

.docx-preview .docx-wrapper {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}
</style>
