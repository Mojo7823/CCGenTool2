<template>
  <div class="st-intro-preview-page">
    <div class="card st-intro-preview-menubar">
      <div class="st-intro-preview-menubar-left">
        <h1>ST Introduction Preview</h1>
        <span class="menubar-subtitle">Preview and download the complete ST Introduction document</span>
      </div>
      <button
        class="btn primary"
        type="button"
        @click="generatePreview"
        :disabled="previewLoading || !hasData"
      >
        Generate Preview
      </button>
    </div>

    <div class="card st-intro-preview-body">
      <aside class="status-column">
        <header class="status-header">
          <h2>Section status</h2>
          <p>Preview all the ST Introduction section</p>
        </header>

        <div v-if="!hasData" class="status-alert info">
          Please fill in at least one ST Introduction section to enable the preview.
        </div>

        <div v-else-if="missingSections.length" class="status-alert warning">
          Some sections still have required information missing: {{ missingSections.join(', ') }}.
        </div>

        <ul class="status-list">
          <li
            v-for="status in sectionStatuses"
            :key="status.name"
            class="status-item"
            :class="status.complete ? 'complete' : 'missing'"
          >
            <div class="status-row">
              <span class="status-name">{{ status.name }}</span>
              <span class="status-pill" :class="status.complete ? 'complete' : 'missing'">
                {{ status.complete ? 'Completed' : 'Missing' }}
              </span>
            </div>
            <ul v-if="!status.complete && status.missing.length" class="missing-list">
              <li v-for="field in status.missing" :key="field">{{ field }}</li>
            </ul>
          </li>
        </ul>
      </aside>

      <section class="preview-column">
        <header class="preview-header">
          <h2>ST Introduction Preview</h2>
          <p>Preview all the ST Introduction section</p>
        </header>

        <div class="preview-window">
          <div v-if="previewLoading" class="preview-overlay">Generating preview…</div>
          <div v-else-if="previewError" class="preview-message error">{{ previewError }}</div>
          <div v-else-if="!hasGeneratedDocx" class="preview-message muted">
            Generate a preview to inspect your ST Introduction document.
          </div>
          <div
            v-show="hasGeneratedDocx && !previewLoading && !previewError"
            ref="docxPreviewContainer"
            class="docx-preview-container"
          ></div>
        </div>

        <div class="preview-actions">
          <a
            v-if="generatedDocxPath && !previewLoading && !previewError"
            :href="downloadUrl"
            download="ST_Introduction.docx"
            class="btn primary"
          >
            Download DOCX
          </a>
        </div>
      </section>
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

const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const userToken = ref('')

interface SectionStatus {
  name: string
  complete: boolean
  missing: string[]
  filled: boolean
}

const sectionData = reactive({
  cover: null as CoverSessionData | null,
  stReference: null as STReferenceSessionData | null,
  toeReference: null as TOEReferenceSessionData | null,
  toeOverview: null as TOEOverviewSessionData | null,
  toeDescription: null as TOEDescriptionSessionData | null,
})

const hasData = computed(() => {
  return sectionStatuses.value.some(status => status.filled)
})

const downloadUrl = computed(() => {
  if (!generatedDocxPath.value) return ''
  return api.getUri({ url: generatedDocxPath.value })
})

function hasText(value: string | null | undefined): boolean {
  return Boolean(value && value.toString().trim().length > 0)
}

function hasRichText(value: string | null | undefined): boolean {
  if (!value) return false
  const stripped = value.replace(/<[^>]*>/g, ' ').replace(/&nbsp;/gi, ' ').replace(/\s+/g, ' ').trim()
  return stripped.length > 0
}

const missingSections = computed(() =>
  sectionStatuses.value.filter(status => !status.complete).map(status => status.name)
)

const sectionStatuses = computed<SectionStatus[]>(() => {
  const statuses: SectionStatus[] = []

  const cover = sectionData.cover
  const coverChecks: Array<[string, boolean]> = [
    ['Cover image', Boolean(cover?.uploadedImagePath)],
    ['Title', hasText(cover?.form.title)],
    ['Version', hasText(cover?.form.version)],
    ['Revision', hasText(cover?.form.revision)],
    ['Description', hasText(cover?.form.description)],
    ['Manufacturer/Laboratory', hasText(cover?.form.manufacturer)],
    ['Date', hasText(cover?.form.date)],
  ]
  const coverMissing = coverChecks.filter(([, ok]) => !ok).map(([label]) => label)
  const coverFilled = coverChecks.some(([, ok]) => ok)
  statuses.push({
    name: 'Cover',
    complete: coverMissing.length === 0 && coverFilled,
    missing: coverMissing,
    filled: coverFilled,
  })

  const stReference = sectionData.stReference
  const stReferenceChecks: Array<[string, boolean]> = [
    ['ST Title', hasText(stReference?.stTitle)],
    ['ST Version', hasText(stReference?.stVersion)],
    ['ST Date', hasText(stReference?.stDate)],
    ['Author', hasText(stReference?.author)],
  ]
  const stReferenceMissing = stReferenceChecks.filter(([, ok]) => !ok).map(([label]) => label)
  const stReferenceFilled = stReferenceChecks.some(([, ok]) => ok)
  statuses.push({
    name: 'ST Reference',
    complete: stReferenceMissing.length === 0 && stReferenceFilled,
    missing: stReferenceMissing,
    filled: stReferenceFilled,
  })

  const toeReference = sectionData.toeReference
  const toeReferenceChecks: Array<[string, boolean]> = [
    ['TOE Name', hasText(toeReference?.toeName)],
    ['TOE Version', hasText(toeReference?.toeVersion)],
    ['TOE Identification', hasText(toeReference?.toeIdentification)],
    ['TOE Type', hasText(toeReference?.toeType)],
  ]
  const toeReferenceMissing = toeReferenceChecks.filter(([, ok]) => !ok).map(([label]) => label)
  const toeReferenceFilled = toeReferenceChecks.some(([, ok]) => ok)
  statuses.push({
    name: 'TOE Reference',
    complete: toeReferenceMissing.length === 0 && toeReferenceFilled,
    missing: toeReferenceMissing,
    filled: toeReferenceFilled,
  })

  const toeOverview = sectionData.toeOverview
  const overviewChecks: Array<[string, boolean]> = [
    ['TOE Overview', hasRichText(toeOverview?.toeOverview)],
    ['TOE Type', hasRichText(toeOverview?.toeType)],
    ['TOE Usage', hasRichText(toeOverview?.toeUsage)],
    ['TOE Major Security Features', hasRichText(toeOverview?.toeMajorSecurityFeatures)],
    ['Non-TOE Hardware/Software/Firmware', hasRichText(toeOverview?.nonToeHardwareSoftwareFirmware)],
  ]
  const overviewMissing = overviewChecks.filter(([, ok]) => !ok).map(([label]) => label)
  const overviewFilled = overviewChecks.some(([, ok]) => ok)
  statuses.push({
    name: 'TOE Overview',
    complete: overviewMissing.length === 0 && overviewFilled,
    missing: overviewMissing,
    filled: overviewFilled,
  })

  const toeDescription = sectionData.toeDescription
  const descriptionChecks: Array<[string, boolean]> = [
    ['TOE Physical Scope', hasRichText(toeDescription?.toePhysicalScope)],
    ['TOE Logical Scope', hasRichText(toeDescription?.toeLogicalScope)],
  ]
  const descriptionMissing = descriptionChecks.filter(([, ok]) => !ok).map(([label]) => label)
  const descriptionFilled = descriptionChecks.some(([, ok]) => ok)
  statuses.push({
    name: 'TOE Description',
    complete: descriptionMissing.length === 0 && descriptionFilled,
    missing: descriptionMissing,
    filled: descriptionFilled,
  })

  return statuses
})

function refreshSectionData() {
  sectionData.cover = sessionService.loadCoverData()
  sectionData.stReference = sessionService.loadSTReferenceData()
  sectionData.toeReference = sessionService.loadTOEReferenceData()
  sectionData.toeOverview = sessionService.loadTOEOverviewData()
  sectionData.toeDescription = sessionService.loadTOEDescriptionData()
}

function buildSTReferenceHTML(data: STReferenceSessionData | null): string {
  if (!data || (!data.stTitle && !data.stVersion && !data.stDate && !data.author)) {
    return ''
  }

  let html = '<table border="1" style="width: 100%; border-collapse: collapse;">'
  
  if (data.stTitle) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Title</td><td style="padding: 8px;">${escapeHtml(data.stTitle)}</td></tr>`
  }
  if (data.stVersion) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Version</td><td style="padding: 8px;">${escapeHtml(data.stVersion)}</td></tr>`
  }
  if (data.stDate) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Date</td><td style="padding: 8px;">${escapeHtml(data.stDate)}</td></tr>`
  }
  if (data.author) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">Author</td><td style="padding: 8px;">${escapeHtml(data.author).replace(/\n/g, '<br>')}</td></tr>`
  }
  
  html += '</table>'
  html += '<p style="text-align: center; margin-top: 8px;"><em>Table 1 Security Target reference</em></p>'
  
  return html
}

function buildTOEReferenceHTML(data: TOEReferenceSessionData | null): string {
  if (!data || (!data.toeName && !data.toeVersion && !data.toeIdentification && !data.toeType)) {
    return ''
  }

  let html = '<table border="1" style="width: 100%; border-collapse: collapse;">'
  
  if (data.toeName) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Name</td><td style="padding: 8px;">${data.toeName}</td></tr>`
  }
  if (data.toeVersion) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Version</td><td style="padding: 8px;">${data.toeVersion}</td></tr>`
  }
  if (data.toeIdentification) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Identification</td><td style="padding: 8px;">${data.toeIdentification}</td></tr>`
  }
  if (data.toeType) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Type</td><td style="padding: 8px;">${data.toeType}</td></tr>`
  }
  
  html += '</table>'
  html += '<p style="text-align: center; margin-top: 8px;"><em>Table 2 TOE reference</em></p>'
  
  return html
}

function buildTOEOverviewHTML(data: TOEOverviewSessionData | null): string {
  if (!data || (!data.toeOverview && !data.toeType && !data.toeUsage && !data.toeMajorSecurityFeatures && !data.nonToeHardwareSoftwareFirmware)) {
    return ''
  }

  let html = ''
  
  if (data.toeOverview) {
    html += `<div>${data.toeOverview}</div>`
  }
  
  if (data.toeType) {
    html += '<h4>1.3.1 TOE Type</h4>'
    html += `<div>${data.toeType}</div>`
  }
  
  if (data.toeUsage) {
    html += '<h4>1.3.2 TOE Usage</h4>'
    html += `<div>${data.toeUsage}</div>`
  }
  
  if (data.toeMajorSecurityFeatures) {
    html += '<h4>1.3.3 TOE Major Security Features</h4>'
    html += `<div>${data.toeMajorSecurityFeatures}</div>`
  }
  
  if (data.nonToeHardwareSoftwareFirmware) {
    html += '<h4>1.3.4 Non-TOE Hardware/Software/Firmware</h4>'
    html += `<div>${data.nonToeHardwareSoftwareFirmware}</div>`
  }
  
  return html
}

function buildTOEDescriptionHTML(data: TOEDescriptionSessionData | null): string {
  if (!data || (!data.toePhysicalScope && !data.toeLogicalScope)) {
    return ''
  }

  let html = ''
  
  if (data.toePhysicalScope) {
    html += '<h4>1.4.1 TOE Physical Scope</h4>'
    html += `<div>${data.toePhysicalScope}</div>`
  }
  
  if (data.toeLogicalScope) {
    html += '<h4>1.4.2 TOE Logical Scope</h4>'
    html += `<div>${data.toeLogicalScope}</div>`
  }
  
  return html
}

function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

async function generatePreview() {
  if (!hasData.value || previewLoading.value) return

  previewError.value = ''
  previewLoading.value = true

  refreshSectionData()
  cleanupDocx()

  try {
    const coverData = sectionData.cover
    const stReferenceHTML = buildSTReferenceHTML(sectionData.stReference)
    const toeReferenceHTML = buildTOEReferenceHTML(sectionData.toeReference)
    const toeOverviewHTML = buildTOEOverviewHTML(sectionData.toeOverview)
    const toeDescriptionHTML = buildTOEDescriptionHTML(sectionData.toeDescription)

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
const handleWindowFocus = () => refreshSectionData()
const handleStorageEvent = (_event: StorageEvent) => refreshSectionData()

const addPreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('pagehide', handlePageHide)
  window.addEventListener('focus', handleWindowFocus)
  window.addEventListener('storage', handleStorageEvent)
}

const removePreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
  window.removeEventListener('focus', handleWindowFocus)
  window.removeEventListener('storage', handleStorageEvent)
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
  align-items: center;
  gap: 16px;
}

.st-intro-preview-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.st-intro-preview-body {
  display: grid;
  gap: 24px;
  padding: 24px;
  grid-template-columns: minmax(0, 320px) minmax(0, 1fr);
}

@media (max-width: 1024px) {
  .st-intro-preview-body {
    grid-template-columns: 1fr;
  }
}

.status-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-header h2 {
  margin: 0;
}

.status-header p {
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
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 16px;
  background: #111827;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.status-name {
  font-weight: 600;
}

.status-pill {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pill.complete {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.status-pill.missing {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.missing-list {
  margin: 12px 0 0;
  padding-left: 18px;
  color: #fca5a5;
  font-size: 13px;
  line-height: 1.5;
}

.status-alert {
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.5;
}

.status-alert.info {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #93c5fd;
}

.status-alert.warning {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #fca5a5;
}

.preview-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-header h2 {
  margin: 0;
}

.preview-header p {
  margin: 0;
  color: var(--muted);
}

.preview-window {
  position: relative;
  border: 1px solid #374151;
  border-radius: 12px;
  background: var(--bg);
  min-height: 360px;
  max-height: 70vh;
  overflow: hidden;
}

@media (max-width: 1024px) {
  .preview-window {
    max-height: none;
  }
}

.preview-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.78);
  color: #f8fafc;
  font-weight: 600;
  z-index: 2;
}

.preview-message {
  padding: 24px;
  text-align: center;
}

.preview-message.muted {
  color: var(--muted);
}

.preview-message.error {
  color: #f87171;
}

.docx-preview-container {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  text-decoration: none;
  display: inline-block;
}

.btn:hover:not(:disabled) {
  background: #374151;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
}

.btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

:global(.docx-rendered) {
  background: white;
  padding: 40px;
  margin: 0 auto;
  max-width: 210mm;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
