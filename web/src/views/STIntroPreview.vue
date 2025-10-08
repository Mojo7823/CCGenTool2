<template>
  <div class="st-intro-preview-page">
    <div class="card st-intro-preview-menubar">
      <div class="st-intro-preview-menubar-left">
        <h1>ST Introduction Preview</h1>
        <span class="menubar-subtitle">Preview all the ST Introduction section</span>
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

    <div v-if="!hasData" class="card info-message">
      <p>Please fill in at least one section (Cover, ST Reference, TOE Reference, TOE Overview, or TOE Description) to generate a preview.</p>
    </div>

    <!-- Section Status Card -->
    <div v-if="hasData" class="card section-status-card">
      <h2>Section Status</h2>
      <div class="status-list">
        <div class="status-item">
          <span class="status-label">Cover</span>
          <span :class="['status-badge', sectionStatus.cover ? 'completed' : 'missing']">
            {{ sectionStatus.cover ? 'Completed' : 'Missing' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">ST Reference</span>
          <span :class="['status-badge', sectionStatus.stReference ? 'completed' : 'missing']">
            {{ sectionStatus.stReference ? 'Completed' : 'Missing' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">TOE Reference</span>
          <span :class="['status-badge', sectionStatus.toeReference ? 'completed' : 'missing']">
            {{ sectionStatus.toeReference ? 'Completed' : 'Missing' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">TOE Overview</span>
          <span :class="['status-badge', sectionStatus.toeOverview ? 'completed' : 'missing']">
            {{ sectionStatus.toeOverview ? 'Completed' : 'Missing' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">TOE Description</span>
          <span :class="['status-badge', sectionStatus.toeDescription ? 'completed' : 'missing']">
            {{ sectionStatus.toeDescription ? 'Completed' : 'Missing' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Inline Preview Section -->
    <div v-if="showPreview" class="card preview-card">
      <h2>ST Introduction Preview</h2>
      <div class="preview-content">
        <div v-if="previewLoading" class="preview-loading">Generating preview…</div>
        <div v-else-if="previewError" class="preview-error">{{ previewError }}</div>
        <div
          v-else
          ref="docxPreviewContainer"
          class="docx-preview-container"
        ></div>
      </div>
      <div v-if="generatedDocxPath && !previewLoading && !previewError" class="preview-footer">
        <a
          :href="downloadUrl"
          download="ST_Introduction.docx"
          class="btn primary"
        >
          Download DOCX
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { sessionService } from '../services/sessionService'

const showPreview = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const userToken = ref('')

const sectionStatus = computed(() => {
  const coverData = sessionService.loadCoverData()
  const stRefData = sessionService.loadSTReferenceData()
  const toeRefData = sessionService.loadTOEReferenceData()
  const toeOverviewData = sessionService.loadTOEOverviewData()
  const toeDescData = sessionService.loadTOEDescriptionData()
  
  return {
    cover: !!(coverData && (coverData.uploadedImagePath || coverData.form.title || coverData.form.description)),
    stReference: !!(stRefData && (stRefData.stTitle || stRefData.stVersion || stRefData.stDate || stRefData.author)),
    toeReference: !!(toeRefData && (toeRefData.toeName || toeRefData.toeVersion || toeRefData.toeIdentification || toeRefData.toeType)),
    toeOverview: !!(toeOverviewData && (toeOverviewData.toeOverview || toeOverviewData.toeType || toeOverviewData.toeUsage || toeOverviewData.toeMajorSecurityFeatures || toeOverviewData.nonToeHardwareSoftwareFirmware)),
    toeDescription: !!(toeDescData && (toeDescData.toePhysicalScope || toeDescData.toeLogicalScope))
  }
})

const hasData = computed(() => {
  const status = sectionStatus.value
  return status.cover || status.stReference || status.toeReference || status.toeOverview || status.toeDescription
})

const downloadUrl = computed(() => {
  if (!generatedDocxPath.value) return ''
  return api.getUri({ url: generatedDocxPath.value })
})

function buildSTReferenceHTML(): string {
  const data = sessionService.loadSTReferenceData()
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

function buildTOEReferenceHTML(): string {
  const data = sessionService.loadTOEReferenceData()
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

function buildTOEOverviewHTML(): string {
  const data = sessionService.loadTOEOverviewData()
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

function buildTOEDescriptionHTML(): string {
  const data = sessionService.loadTOEDescriptionData()
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
  showPreview.value = true
  previewLoading.value = true

  await nextTick()
  cleanupDocx()

  try {
    // Gather all data
    const coverData = sessionService.loadCoverData()
    const stReferenceHTML = buildSTReferenceHTML()
    const toeReferenceHTML = buildTOEReferenceHTML()
    const toeOverviewHTML = buildTOEOverviewHTML()
    const toeDescriptionHTML = buildTOEDescriptionHTML()

    const payload = {
      user_id: userToken.value,
      cover_data: coverData ? {
        title: coverData.form.title,
        version: coverData.form.version,
        revision: coverData.form.revision,
        description: coverData.form.description,
        manufacturer: coverData.form.manufacturer,
        date: coverData.form.date,
        image_path: coverData.uploadedImagePath
      } : null,
      st_reference_html: stReferenceHTML || null,
      toe_reference_html: toeReferenceHTML || null,
      toe_overview_html: toeOverviewHTML || null,
      toe_description_html: toeDescriptionHTML || null
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

function closePreview() {
  showPreview.value = false
  if (!previewLoading.value) {
    previewError.value = ''
  }
  cleanupDocx()
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
}

const removePreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
}

onMounted(() => {
  userToken.value = sessionService.getUserToken()
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

.info-message {
  padding: 24px;
  text-align: center;
  color: var(--muted);
}

/* Section Status Card */
.section-status-card {
  padding: 24px;
}

.section-status-card h2 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-soft);
  border-radius: 8px;
}

.status-label {
  font-weight: 500;
  color: var(--text);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.status-badge.completed {
  background: #10b981;
  color: white;
}

.status-badge.missing {
  background: #ef4444;
  color: white;
}

/* Preview Card */
.preview-card {
  padding: 24px;
}

.preview-card h2 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.preview-content {
  background: #1a1a1a;
  border-radius: 8px;
  min-height: 500px;
  position: relative;
}

.preview-loading,
.preview-error {
  padding: 48px 24px;
  text-align: center;
  color: var(--muted);
}

.preview-error {
  color: #ef4444;
}

.docx-preview-container {
  padding: 24px;
  overflow-y: auto;
  max-height: 70vh;
}

.preview-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
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
