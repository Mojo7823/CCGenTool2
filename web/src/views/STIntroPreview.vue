<template>
  <div class="st-intro-preview-page">
    <div class="card st-intro-preview-menubar">
      <div class="st-intro-preview-menubar-left">
        <h1>ST Introduction Preview</h1>
        <span class="menubar-subtitle">Preview and download the complete ST Introduction document</span>
      </div>
      <div class="menubar-actions">
        <button
          class="btn primary"
          type="button"
          @click="generatePreview"
          :disabled="previewLoading || !hasData"
        >
          Generate Preview
        </button>
        <a
          v-if="generatedDocxPath && !previewLoading && !previewError"
          :href="downloadUrl"
          download="ST_Introduction.docx"
          class="btn outline"
        >
          Download DOCX
        </a>
      </div>
    </div>

    <p class="page-description">Preview all the ST Introduction section</p>

    <div class="card section-status-card">
      <header class="status-header">
        <h2>Section status</h2>
        <p class="status-description">Complete each section before generating the preview.</p>
      </header>
      <ul class="status-list">
        <li v-for="section in sectionStatuses" :key="section.key" class="status-item">
          <div class="status-info">
            <span class="status-title">{{ section.title }}</span>
            <span class="status-label" :class="section.completed ? 'completed' : 'missing'">
              {{ section.completed ? 'Completed' : 'Missing' }}
            </span>
          </div>
          <RouterLink :to="section.route" class="status-link">Edit</RouterLink>
        </li>
      </ul>
      <div v-if="missingSections.length" class="status-warning">
        <strong>Reminder:</strong>
        <span>
          The following sections still need information:
          {{ missingSections.map(section => section.title).join(', ') }}.
        </span>
      </div>
      <div v-else class="status-success">All sections have information. You're ready to generate the preview.</div>
    </div>

    <div class="card st-intro-preview-panel">
      <header class="preview-header">
        <h2>ST Introduction Preview</h2>
        <span v-if="hasGeneratedDocx && !previewLoading && !previewError" class="preview-hint">
          Scroll to review the generated document.
        </span>
      </header>
      <div class="docx-preview-shell">
        <div v-if="previewLoading" class="modal-status overlay">Generating preview…</div>
        <div v-else-if="previewError" class="modal-error">{{ previewError }}</div>
        <div v-else-if="!generatedDocxPath" class="preview-placeholder">
          Click <strong>Generate Preview</strong> to render the combined ST Introduction document.
        </div>
        <div
          v-show="!!generatedDocxPath && !previewLoading && !previewError"
          ref="docxPreviewContainer"
          class="docx-preview-container"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { sessionService } from '../services/sessionService'
import type {
  CoverSessionData,
  STReferenceSessionData,
  TOEReferenceSessionData,
  TOEOverviewSessionData,
  TOEDescriptionSessionData
} from '../services/sessionService'

interface SectionStatus {
  key: string
  title: string
  completed: boolean
  route: string
}

const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const userToken = ref('')

const sections = reactive({
  cover: null as CoverSessionData | null,
  stReference: null as STReferenceSessionData | null,
  toeReference: null as TOEReferenceSessionData | null,
  toeOverview: null as TOEOverviewSessionData | null,
  toeDescription: null as TOEDescriptionSessionData | null,
})

const downloadUrl = computed(() => {
  if (!generatedDocxPath.value) return ''
  return api.getUri({ url: generatedDocxPath.value })
})

const sectionStatuses = computed<SectionStatus[]>(() => [
  {
    key: 'cover',
    title: 'Cover',
    completed: isCoverComplete(sections.cover),
    route: '/st-intro/cover',
  },
  {
    key: 'st-reference',
    title: 'ST Reference',
    completed: isSTReferenceComplete(sections.stReference),
    route: '/st-intro/reference',
  },
  {
    key: 'toe-reference',
    title: 'TOE Reference',
    completed: isTOEReferenceComplete(sections.toeReference),
    route: '/st-intro/toe-reference',
  },
  {
    key: 'toe-overview',
    title: 'TOE Overview',
    completed: isTOEOverviewComplete(sections.toeOverview),
    route: '/st-intro/toe-overview',
  },
  {
    key: 'toe-description',
    title: 'TOE Description',
    completed: isTOEDescriptionComplete(sections.toeDescription),
    route: '/st-intro/toe-description',
  },
])

const missingSections = computed(() => sectionStatuses.value.filter(section => !section.completed))
const hasData = computed(() => sectionStatuses.value.some(section => section.completed))

function isCoverComplete(data: CoverSessionData | null): boolean {
  if (!data) return false
  const { form, uploadedImagePath } = data
  return Boolean(
    uploadedImagePath ||
    form.title?.trim() ||
    form.version?.trim() ||
    form.revision?.trim() ||
    form.description?.trim() ||
    form.manufacturer?.trim() ||
    form.date?.trim()
  )
}

function isSTReferenceComplete(data: STReferenceSessionData | null): boolean {
  if (!data) return false
  return Boolean(
    data.stTitle?.trim() ||
    data.stVersion?.trim() ||
    data.stDate?.trim() ||
    data.author?.trim()
  )
}

function isTOEReferenceComplete(data: TOEReferenceSessionData | null): boolean {
  if (!data) return false
  return Boolean(
    data.toeName?.trim() ||
    data.toeVersion?.trim() ||
    data.toeIdentification?.trim() ||
    data.toeType?.trim()
  )
}

function isTOEOverviewComplete(data: TOEOverviewSessionData | null): boolean {
  if (!data) return false
  return Boolean(
    data.toeOverview?.trim() ||
    data.toeType?.trim() ||
    data.toeUsage?.trim() ||
    data.toeMajorSecurityFeatures?.trim() ||
    data.nonToeHardwareSoftwareFirmware?.trim()
  )
}

function isTOEDescriptionComplete(data: TOEDescriptionSessionData | null): boolean {
  if (!data) return false
  return Boolean(data.toePhysicalScope?.trim() || data.toeLogicalScope?.trim())
}

function refreshSectionData() {
  sections.cover = sessionService.loadCoverData()
  sections.stReference = sessionService.loadSTReferenceData()
  sections.toeReference = sessionService.loadTOEReferenceData()
  sections.toeOverview = sessionService.loadTOEOverviewData()
  sections.toeDescription = sessionService.loadTOEDescriptionData()
}

function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function buildSTReferenceHTML(data: STReferenceSessionData | null): string {
  if (!data || !isSTReferenceComplete(data)) {
    return ''
  }

  let html = '<table border="1" style="width: 100%; border-collapse: collapse;">'

  if (data.stTitle?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Title</td><td style="padding: 8px;">${escapeHtml(data.stTitle)}</td></tr>`
  }
  if (data.stVersion?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Version</td><td style="padding: 8px;">${escapeHtml(data.stVersion)}</td></tr>`
  }
  if (data.stDate?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Date</td><td style="padding: 8px;">${escapeHtml(data.stDate)}</td></tr>`
  }
  if (data.author?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">Author</td><td style="padding: 8px;">${escapeHtml(data.author).replace(/\n/g, '<br>')}</td></tr>`
  }

  html += '</table>'
  html += '<p style="text-align: center; margin-top: 8px;"><em>Table 1 Security Target reference</em></p>'

  return html
}

function buildTOEReferenceHTML(data: TOEReferenceSessionData | null): string {
  if (!data || !isTOEReferenceComplete(data)) {
    return ''
  }

  let html = '<table border="1" style="width: 100%; border-collapse: collapse;">'

  if (data.toeName?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Name</td><td style="padding: 8px;">${escapeHtml(data.toeName)}</td></tr>`
  }
  if (data.toeVersion?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Version</td><td style="padding: 8px;">${escapeHtml(data.toeVersion)}</td></tr>`
  }
  if (data.toeIdentification?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Identification</td><td style="padding: 8px;">${escapeHtml(data.toeIdentification)}</td></tr>`
  }
  if (data.toeType?.trim()) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Type</td><td style="padding: 8px;">${escapeHtml(data.toeType)}</td></tr>`
  }

  html += '</table>'
  html += '<p style="text-align: center; margin-top: 8px;"><em>Table 2 TOE reference</em></p>'

  return html
}

function buildTOEOverviewHTML(data: TOEOverviewSessionData | null): string {
  if (!data || !isTOEOverviewComplete(data)) {
    return ''
  }

  let html = ''

  if (data.toeOverview?.trim()) {
    html += `<div>${data.toeOverview}</div>`
  }

  if (data.toeType?.trim()) {
    html += '<h4>1.3.1 TOE Type</h4>'
    html += `<div>${data.toeType}</div>`
  }

  if (data.toeUsage?.trim()) {
    html += '<h4>1.3.2 TOE Usage</h4>'
    html += `<div>${data.toeUsage}</div>`
  }

  if (data.toeMajorSecurityFeatures?.trim()) {
    html += '<h4>1.3.3 TOE Major Security Features</h4>'
    html += `<div>${data.toeMajorSecurityFeatures}</div>`
  }

  if (data.nonToeHardwareSoftwareFirmware?.trim()) {
    html += '<h4>1.3.4 Non-TOE Hardware/Software/Firmware</h4>'
    html += `<div>${data.nonToeHardwareSoftwareFirmware}</div>`
  }

  return html
}

function buildTOEDescriptionHTML(data: TOEDescriptionSessionData | null): string {
  if (!data || !isTOEDescriptionComplete(data)) {
    return ''
  }

  let html = ''

  if (data.toePhysicalScope?.trim()) {
    html += '<h4>1.4.1 TOE Physical Scope</h4>'
    html += `<div>${data.toePhysicalScope}</div>`
  }

  if (data.toeLogicalScope?.trim()) {
    html += '<h4>1.4.2 TOE Logical Scope</h4>'
    html += `<div>${data.toeLogicalScope}</div>`
  }

  return html
}

async function generatePreview() {
  if (!hasData.value || previewLoading.value) return

  refreshSectionData()
  previewError.value = ''
  previewLoading.value = true

  if (generatedDocxPath.value) {
    cleanupDocx()
  }

  await nextTick()
  if (docxPreviewContainer.value) {
    docxPreviewContainer.value.innerHTML = ''
  }

  try {
    const coverData = sections.cover
    const stReferenceHTML = buildSTReferenceHTML(sections.stReference)
    const toeReferenceHTML = buildTOEReferenceHTML(sections.toeReference)
    const toeOverviewHTML = buildTOEOverviewHTML(sections.toeOverview)
    const toeDescriptionHTML = buildTOEDescriptionHTML(sections.toeDescription)

    const payload = {
      user_id: userToken.value,
      cover_data: coverData
        ? {
            title: coverData.form.title,
            version: coverData.form.version,
            revision: coverData.form.revision,
            description: coverData.form.description,
            manufacturer: coverData.form.manufacturer,
            date: coverData.form.date,
            image_path: coverData.uploadedImagePath,
          }
        : null,
      st_reference_html: stReferenceHTML || null,
      toe_reference_html: toeReferenceHTML || null,
      toe_overview_html: toeOverviewHTML || null,
      toe_description_html: toeDescriptionHTML || null,
    }

    const response = await api.post('/st-intro/preview', payload)
    const path: string | undefined = response.data?.path

    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }

    generatedDocxPath.value = path
    hasGeneratedDocx.value = true
    await nextTick()
    await renderDocxPreview(path)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || 'Unable to generate preview.'
    previewError.value = message
  } finally {
    previewLoading.value = false
  }
}

async function renderDocxPreview(path: string) {
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
    const message = error?.message || 'Failed to render DOCX preview.'
    previewError.value = message
  }
}

const cleanupDocx = (keepalive = false) => {
  if (!userToken.value || !hasGeneratedDocx.value) {
    return
  }

  const url = api.getUri({ url: `/st-intro/preview/${userToken.value}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  generatedDocxPath.value = null
  hasGeneratedDocx.value = false
}

const handleBeforeUnload = () => cleanupDocx(true)
const handlePageHide = () => cleanupDocx(true)

const addPreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('pagehide', handlePageHide)
  window.addEventListener('focus', refreshSectionData)
}

const removePreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
  window.removeEventListener('focus', refreshSectionData)
}

onMounted(() => {
  userToken.value = sessionService.getUserToken()
  refreshSectionData()
  addPreviewListeners()
})

onBeforeUnmount(() => {
  cleanupDocx()
  removePreviewListeners()
})
</script>

<style scoped>
.st-intro-preview-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.st-intro-preview-menubar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.st-intro-preview-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.menubar-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.page-description {
  margin: 0;
  color: var(--muted);
}

.section-status-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-header h2 {
  margin: 0 0 4px 0;
}

.status-description {
  margin: 0;
  color: var(--muted);
}

.status-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.4);
}

.status-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-title {
  font-weight: 600;
}

.status-label {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-label.completed {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.status-label.missing {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.status-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.status-link:hover {
  text-decoration: underline;
}

.status-warning {
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(248, 113, 113, 0.12);
  color: #fca5a5;
}

.status-success {
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
}

.st-intro-preview-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.preview-header h2 {
  margin: 0;
}

.preview-hint {
  color: var(--muted);
  font-size: 0.9rem;
}

.docx-preview-shell {
  position: relative;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.6);
  min-height: 360px;
  max-height: 720px;
  overflow: hidden;
  padding: 0;
}

.preview-placeholder {
  padding: 32px;
  color: var(--muted);
  text-align: center;
}

.modal-status {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text);
  background: rgba(15, 23, 42, 0.85);
  font-weight: 500;
  z-index: 10;
}

.modal-error {
  padding: 24px;
  color: #fca5a5;
  text-align: center;
}

.docx-preview-container {
  height: 100%;
  overflow: auto;
  padding: 16px;
}

.docx-rendered {
  background: #fff;
  color: #111;
}

.btn.outline {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: transparent;
  color: var(--text);
}

.btn.outline:hover {
  background: rgba(148, 163, 184, 0.1);
}
</style>
