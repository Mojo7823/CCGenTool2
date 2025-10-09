<template>
  <div class="final-preview-page">
    <div class="card final-preview-menubar">
      <div class="final-preview-menubar-left">
        <h1>Final Document Preview</h1>
        <span class="menubar-subtitle">Here is all the Current Preview of all Security Target Document</span>
      </div>
      <div class="menubar-actions">
        <button
          class="btn"
          type="button"
          @click="saveProjectAsJSON"
          :disabled="!hasData"
        >
          Save Project
        </button>
        <button
          class="btn primary"
          type="button"
          @click="generatePreview"
          :disabled="previewLoading || !hasData"
        >
          {{ previewLoading ? 'Generating…' : 'Generate Preview' }}
        </button>
        <button
          class="btn primary"
          type="button"
          @click="handleDownload"
          :disabled="!canDownload"
        >
          Download DOCX
        </button>
      </div>
    </div>

    <div class="card status-card">
      <header class="status-header">
        <h2>Section status</h2>
        <p class="status-subtitle">Review the completion state for all Security Target sections</p>
      </header>
      <ul class="status-list">
        <li v-for="section in sectionStatus" :key="section.key">
          <span class="status-label">{{ section.label }}</span>
          <span :class="['status-indicator', statusClass(section)]">
            {{ statusLabel(section) }}
          </span>
        </li>
      </ul>
      <div v-if="missingSections.length" class="status-warning">
        Please complete the following required sections before generating the final document:
        <span>{{ missingSections.join(', ') }}</span>
      </div>
      <div v-else class="status-success">All required sections are complete.</div>
    </div>

    <div class="card preview-card">
      <header class="preview-header">
        <div>
          <h2>Security Target Document Preview</h2>
          <p class="preview-subtitle">A combined preview of the entire Security Target document with page breaks</p>
        </div>
      </header>

      <div class="preview-body">
        <div v-if="!hasData" class="info-message">
          <p>Please fill in at least one section to generate a preview.</p>
        </div>
        <div v-else class="docx-preview-shell">
          <div v-if="previewLoading" class="modal-status overlay">Generating preview…</div>
          <div v-else-if="previewError" class="modal-error">{{ previewError }}</div>
          <div
            ref="docxPreviewContainer"
            class="docx-preview-container"
            :class="{ hidden: previewLoading || !!previewError || !hasGeneratedDocx }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import {
  sessionService,
  type CoverSessionData,
  type STReferenceSessionData,
  type TOEReferenceSessionData,
  type TOEOverviewSessionData,
  type TOEDescriptionSessionData,
  type ConformanceClaimsSessionData,
  type SessionData,
  type SarSessionData,
  type AssumptionsSessionData,
  type ThreatsSessionData,
  type OspSessionData,
} from '../services/sessionService'
import {
  buildSarPreviewHtml,
  buildSfrPreviewHtml,
  type SarPreviewEntry,
  type SfrPreviewEntry,
} from '../utils/securityPreview'
import {
  buildSecurityProblemDefinitionHtml,
  hasAssumptions,
  hasOsp,
  hasThreats,
} from '../utils/spdPreview'

type SectionKey =
  | 'cover'
  | 'st-reference'
  | 'toe-reference'
  | 'toe-overview'
  | 'toe-description'
  | 'assumptions'
  | 'threats'
  | 'osp'
  | 'conformance-claims'
  | 'sfr'
  | 'sar'

interface SectionStatus {
  key: SectionKey
  label: string
  complete: boolean
  optional?: boolean
}

const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const userToken = ref('')
const sectionStatus = ref<SectionStatus[]>([
  { key: 'cover', label: 'Cover', complete: false },
  { key: 'st-reference', label: 'ST Reference', complete: false },
  { key: 'toe-reference', label: 'TOE Reference', complete: false },
  { key: 'toe-overview', label: 'TOE Overview', complete: false },
  { key: 'toe-description', label: 'TOE Description', complete: false },
  { key: 'assumptions', label: 'Assumptions', complete: false },
  { key: 'threats', label: 'Threats', complete: false },
  {
    key: 'osp',
    label: 'Organisational Security Policies (Optional)',
    complete: true,
    optional: true,
  },
  { key: 'conformance-claims', label: 'Conformance Claims', complete: false },
  { key: 'sfr', label: 'Security Functional Requirements', complete: false },
  { key: 'sar', label: 'Security Assurance Requirements', complete: false },
])

const missingSections = computed(() =>
  sectionStatus.value
    .filter(section => !section.complete && !section.optional)
    .map(section => section.label)
)

const hasData = computed(() =>
  sectionStatus.value.some(section => section.complete && !section.optional)
)

function statusLabel(section: SectionStatus): string {
  if (section.optional && !section.complete) {
    return 'Optional'
  }
  return section.complete ? 'Completed' : 'Missing'
}

function statusClass(section: SectionStatus): string {
  if (section.optional && !section.complete) {
    return 'optional'
  }
  return section.complete ? 'completed' : 'missing'
}

const downloadUrl = computed(() => {
  if (!generatedDocxPath.value || !userToken.value) return ''
  const segments = generatedDocxPath.value.split('/')
  const filename = segments[segments.length - 1]
  if (!filename) return ''
  return api.getUri({ url: `/final-preview/download/${userToken.value}/${filename}` })
})

const canDownload = computed(() => !!downloadUrl.value)

function hasCoverContent(data: CoverSessionData | null): boolean {
  if (!data) return false
  const form = data.form || {}
  return Boolean(
    data.uploadedImagePath ||
    data.uploadedImageData ||
    form.title ||
    form.version ||
    form.revision ||
    form.description ||
    form.manufacturer ||
    form.date
  )
}

function hasSTReferenceContent(data: STReferenceSessionData | null): boolean {
  if (!data) return false
  return Boolean(data.stTitle || data.stVersion || data.stDate || data.author)
}

function hasTOEReferenceContent(data: TOEReferenceSessionData | null): boolean {
  if (!data) return false
  return Boolean(data.toeName || data.toeVersion || data.toeIdentification || data.toeType)
}

function hasTOEOverviewContent(data: TOEOverviewSessionData | null): boolean {
  if (!data) return false
  return Boolean(
    data.toeOverview ||
    data.toeType ||
    data.toeUsage ||
    data.toeMajorSecurityFeatures ||
    data.nonToeHardwareSoftwareFirmware
  )
}

function hasTOEDescriptionContent(data: TOEDescriptionSessionData | null): boolean {
  if (!data) return false
  return Boolean(data.toeDescription || data.toePhysicalScope || data.toeLogicalScope)
}

function hasConformanceClaimsContent(data: ConformanceClaimsSessionData | null): boolean {
  if (!data) return false
  return Boolean(data.ccConformance || data.ppClaims || data.additionalNotes)
}

function hasAssumptionsContent(data: AssumptionsSessionData | null): boolean {
  return hasAssumptions(data?.items)
}

function hasThreatsContent(data: ThreatsSessionData | null): boolean {
  return hasThreats(data?.items)
}

function hasOspContent(data: OspSessionData | null): boolean {
  return hasOsp(data?.items)
}

function hasSFRContent(data: SessionData | null): boolean {
  if (!data) return false
  return Boolean(data.sfrList && data.sfrList.length > 0)
}

function hasSARContent(data: SarSessionData | null): boolean {
  if (!data) return false
  return Boolean(data.sarList && data.sarList.length > 0)
}

function updateSectionStatus() {
  const coverData = sessionService.loadCoverData()
  const stReferenceData = sessionService.loadSTReferenceData()
  const toeReferenceData = sessionService.loadTOEReferenceData()
  const toeOverviewData = sessionService.loadTOEOverviewData()
  const toeDescriptionData = sessionService.loadTOEDescriptionData()
  const conformanceClaimsData = sessionService.loadConformanceClaimsData()
  const sfrData = sessionService.loadSfrData()
  const sarData = sessionService.loadSarData()
  const assumptionsData = sessionService.loadAssumptionsData()
  const threatsData = sessionService.loadThreatsData()
  const ospData = sessionService.loadOspData()

  sectionStatus.value = [
    { key: 'cover', label: 'Cover', complete: hasCoverContent(coverData) },
    { key: 'st-reference', label: 'ST Reference', complete: hasSTReferenceContent(stReferenceData) },
    { key: 'toe-reference', label: 'TOE Reference', complete: hasTOEReferenceContent(toeReferenceData) },
    { key: 'toe-overview', label: 'TOE Overview', complete: hasTOEOverviewContent(toeOverviewData) },
    { key: 'toe-description', label: 'TOE Description', complete: hasTOEDescriptionContent(toeDescriptionData) },
    { key: 'assumptions', label: 'Assumptions', complete: hasAssumptionsContent(assumptionsData) },
    { key: 'threats', label: 'Threats', complete: hasThreatsContent(threatsData) },
    {
      key: 'osp',
      label: 'Organisational Security Policies (Optional)',
      complete: hasOspContent(ospData),
      optional: true,
    },
    { key: 'conformance-claims', label: 'Conformance Claims', complete: hasConformanceClaimsContent(conformanceClaimsData) },
    { key: 'sfr', label: 'Security Functional Requirements', complete: hasSFRContent(sfrData) },
    { key: 'sar', label: 'Security Assurance Requirements', complete: hasSARContent(sarData) },
  ]
}

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
  if (!data || (!data.toeDescription && !data.toePhysicalScope && !data.toeLogicalScope)) {
    return ''
  }

  let html = ''

  if (data.toeDescription) {
    html += `<div>${data.toeDescription}</div>`
  }

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

function buildConformanceClaimsHTML(): string {
  const data = sessionService.loadConformanceClaimsData()
  if (!data || (!data.ccConformance && !data.ppClaims && !data.additionalNotes)) {
    return ''
  }

  let html = ''

  if (data.ccConformance) {
    html += '<h4>Common Criteria (CC) Conformance Claims</h4>'
    html += `<div>${data.ccConformance}</div>`
  }

  if (data.ppClaims) {
    html += '<h4>Protection Profile (PP) Claims</h4>'
    html += `<div>${data.ppClaims}</div>`
  }

  if (data.additionalNotes) {
    html += '<h4>Additional Notes</h4>'
    html += `<div>${data.additionalNotes}</div>`
  }

  return html
}

function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

async function generatePreview() {
  updateSectionStatus()

  if (!hasData.value || previewLoading.value) return

  if (!userToken.value) {
    userToken.value = sessionService.getUserToken()
  }

  previewError.value = ''
  previewLoading.value = true

  await nextTick()
  cleanupDocx()
  hasGeneratedDocx.value = false

  try {
    const coverData = sessionService.loadCoverData()
    const stReferenceHTML = buildSTReferenceHTML()
    const toeReferenceHTML = buildTOEReferenceHTML()
    const toeOverviewHTML = buildTOEOverviewHTML()
    const toeDescriptionHTML = buildTOEDescriptionHTML()
    const conformanceClaimsHTML = buildConformanceClaimsHTML()
    const sfrData = sessionService.loadSfrData()
    const sarData = sessionService.loadSarData()
    const assumptionsData = sessionService.loadAssumptionsData()
    const threatsData = sessionService.loadThreatsData()
    const ospData = sessionService.loadOspData()

    const sfrEntries = (sfrData?.sfrList || []) as unknown as SfrPreviewEntry[]
    const sarEntries = (sarData?.sarList || []) as unknown as SarPreviewEntry[]

    const spdHtml = buildSecurityProblemDefinitionHtml({
      assumptions: assumptionsData?.items ?? [],
      threats: threatsData?.items ?? [],
      osp: ospData?.items ?? [],
    })

    const sfrPreviewHtml = sfrEntries.length
      ? buildSfrPreviewHtml(sfrEntries, {
          rootSectionNumber: 5,
          includeRootHeading: false,
          includeFunctionalHeading: false,
        })
      : ''

    const sarPreviewHtml = sarEntries.length
      ? buildSarPreviewHtml(sarEntries, {
          rootSectionNumber: 5,
          selectedEal: sarData?.selectedEal || 'EAL 1',
          includeRootHeading: false,
          includeAssuranceHeading: false,
        })
      : ''

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
      conformance_claims_html: conformanceClaimsHTML || null,
      spd_html: spdHtml || null,
      sfr_list: sfrData?.sfrList || [],
      sar_list: sarData?.sarList || [],
      selected_eal: sarData?.selectedEal || null,
      sfr_preview_html: sfrPreviewHtml || null,
      sar_preview_html: sarPreviewHtml || null,
    }

    const response = await api.post('/final-preview', payload)
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
    hasGeneratedDocx.value = false
  }
}

function saveProjectAsJSON() {
  // Export all session data as JSON
  const projectData = {
    coverData: sessionService.loadCoverData(),
    stReferenceData: sessionService.loadSTReferenceData(),
    toeReferenceData: sessionService.loadTOEReferenceData(),
    toeOverviewData: sessionService.loadTOEOverviewData(),
    toeDescriptionData: sessionService.loadTOEDescriptionData(),
    conformanceClaimsData: sessionService.loadConformanceClaimsData(),
    sfrData: sessionService.loadSfrData(),
    sarData: sessionService.loadSarData(),
    assumptionsData: sessionService.loadAssumptionsData(),
    threatsData: sessionService.loadThreatsData(),
    ospData: sessionService.loadOspData(),
    exportedAt: new Date().toISOString(),
  }

  const jsonStr = JSON.stringify(projectData, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `CCGenTool_Project_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const cleanupDocx = (keepalive = false) => {
  if (!userToken.value || !generatedDocxPath.value) {
    return
  }

  const url = api.getUri({ url: `/final-preview/${userToken.value}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  generatedDocxPath.value = null
  hasGeneratedDocx.value = false
}

function handleDownload() {
  if (!canDownload.value || typeof window === 'undefined') {
    return
  }

  const url = downloadUrl.value
  if (!url) {
    return
  }

  const opened = window.open(url, '_blank')
  if (!opened) {
    const link = document.createElement('a')
    link.href = url
    link.target = '_blank'
    link.rel = 'noopener'
    link.download = 'Security_Target_Document.docx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    opened.opener = null
  }
}

const handleBeforeUnload = () => cleanupDocx(true)
const handlePageHide = () => cleanupDocx(true)

const handleWindowFocus = () => updateSectionStatus()

const addPreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('pagehide', handlePageHide)
  window.addEventListener('focus', handleWindowFocus)
}

const removePreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
  window.removeEventListener('focus', handleWindowFocus)
}

onMounted(() => {
  userToken.value = sessionService.getUserToken()
  updateSectionStatus()
  addPreviewListeners()
})

onBeforeUnmount(() => {
  cleanupDocx()
  removePreviewListeners()
})
</script>

<style scoped>
.final-preview-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.final-preview-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.final-preview-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.menubar-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.status-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.status-header h2 {
  margin: 0;
}

.status-subtitle {
  margin: 4px 0 0;
  color: var(--muted);
}

.status-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #374151;
  background: rgba(55, 65, 81, 0.18);
}

.status-label {
  font-weight: 500;
}

.status-indicator {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border: 1px solid transparent;
}

.status-indicator.completed {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border-color: rgba(34, 197, 94, 0.45);
}

.status-indicator.missing {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.4);
}

.status-indicator.optional {
  background: rgba(250, 204, 21, 0.15);
  color: #fde68a;
  border-color: rgba(250, 204, 21, 0.4);
}

.status-warning {
  border-left: 3px solid #f97316;
  padding: 12px 16px;
  background: rgba(249, 115, 22, 0.12);
  border-radius: 8px;
  color: #fb923c;
}

.status-success {
  border-left: 3px solid #22c55e;
  padding: 12px 16px;
  background: rgba(34, 197, 94, 0.12);
  border-radius: 8px;
  color: #4ade80;
}

.preview-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.preview-header h2 {
  margin: 0;
}

.preview-subtitle {
  margin: 4px 0 0;
  color: var(--muted);
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-message {
  padding: 24px;
  text-align: center;
  color: var(--muted);
  border: 1px dashed #4b5563;
  border-radius: 12px;
}

.docx-preview-shell {
  position: relative;
  min-height: 520px;
  width: 100%;
  border: 1px solid #374151;
  border-radius: 12px;
  background: #0f172a;
  overflow: hidden;
}

.modal-status {
  padding: 24px;
  text-align: center;
  color: var(--muted);
}

.modal-status.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.85);
  z-index: 10;
}

.modal-error {
  padding: 24px;
  text-align: center;
  color: #ef4444;
}

.docx-preview-container {
  padding: 24px;
  overflow-y: auto;
  max-height: 520px;
  background: #1a1f2e;
  height: 100%;
}

.docx-preview-container.hidden {
  display: none;
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

@media (max-width: 768px) {
  .status-list li {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .preview-header {
    align-items: flex-start;
  }
}

:global(.docx-rendered) {
  background: white;
  padding: 40px;
  margin: 0 auto;
  max-width: 210mm;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
