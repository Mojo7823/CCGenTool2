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
          v-if="generatedDocxPath && !previewLoading && !previewError"
          class="btn primary"
          type="button"
          @click="handleDownloadClick"
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
          <span :class="['status-indicator', section.complete ? 'completed' : 'missing']">
            {{ section.complete ? 'Completed' : 'Missing' }}
          </span>
        </li>
      </ul>
      <div v-if="missingSections.length" class="status-warning">
        Please complete the following sections before generating the final document:
        <span>{{ missingSections.join(', ') }}</span>
      </div>
      <div v-else class="status-success">All sections are complete.</div>
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
} from '../services/sessionService'

type SectionKey = 
  | 'cover' 
  | 'st-reference' 
  | 'toe-reference' 
  | 'toe-overview' 
  | 'toe-description'
  | 'conformance-claims'
  | 'sfr'
  | 'sar'

interface SectionStatus {
  key: SectionKey
  label: string
  complete: boolean
}

interface SfrPreviewMetadata {
  classDescription?: string
  classLabel?: string
}

interface SfrPreviewEntry {
  classCode?: string
  classDescription?: string
  className?: string
  componentId?: string
  componentName?: string
  previewContent?: string
  metadata?: SfrPreviewMetadata
}

interface SarPreviewEntry {
  classCode?: string
  className?: string
  componentId?: string
  componentName?: string
  previewContent?: string
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
  { key: 'conformance-claims', label: 'Conformance Claims', complete: false },
  { key: 'sfr', label: 'Security Functional Requirements', complete: false },
  { key: 'sar', label: 'Security Assurance Requirements', complete: false },
])

const missingSections = computed(() => 
  sectionStatus.value.filter(section => !section.complete).map(section => section.label)
)

const hasData = computed(() => sectionStatus.value.some(section => section.complete))

const downloadUrl = computed(() => {
  if (!generatedDocxPath.value) return ''
  return api.getUri({ url: generatedDocxPath.value })
})

function hasCoverContent(data: CoverSessionData | null): boolean {
  if (!data) return false
  const form = data.form || {}
  return Boolean(
    data.uploadedImageBase64 ||
    data.uploadedImagePath ||
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

  sectionStatus.value = [
    { key: 'cover', label: 'Cover', complete: hasCoverContent(coverData) },
    { key: 'st-reference', label: 'ST Reference', complete: hasSTReferenceContent(stReferenceData) },
    { key: 'toe-reference', label: 'TOE Reference', complete: hasTOEReferenceContent(toeReferenceData) },
    { key: 'toe-overview', label: 'TOE Overview', complete: hasTOEOverviewContent(toeOverviewData) },
    { key: 'toe-description', label: 'TOE Description', complete: hasTOEDescriptionContent(toeDescriptionData) },
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

const cleanClassDescription = (description: string) =>
  description.replace(/\(.*?\)/g, '').replace(/\s+/g, ' ').trim()

const deriveClassDescriptionFromLabel = (label: string) => {
  const colonIndex = label.indexOf(':')
  if (colonIndex !== -1) {
    return label.slice(colonIndex + 1).trim()
  }
  return cleanClassDescription(label)
}

const getClassDescriptionForEntry = (entry: SfrPreviewEntry) => {
  if (entry.classDescription) {
    return entry.classDescription
  }
  if (entry.metadata?.classDescription) {
    return entry.metadata.classDescription
  }
  if (entry.metadata?.classLabel) {
    return deriveClassDescriptionFromLabel(entry.metadata.classLabel)
  }
  if (entry.className) {
    return deriveClassDescriptionFromLabel(entry.className)
  }
  return entry.classCode ?? 'UNKNOWN'
}

const normalizeComponentId = (value: string | undefined) => (value ?? '').trim().toUpperCase()

const uppercaseIdentifiersInHtml = (html: string) => {
  const transform = (text: string) =>
    text.replace(/\b([a-z][a-z0-9_.-]*[_.][a-z0-9_.-]*)\b/gi, match => match.toUpperCase())

  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return transform(html)
  }

  const container = document.createElement('div')
  container.innerHTML = html
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT)

  while (walker.nextNode()) {
    const node = walker.currentNode as Text
    if (node.nodeValue) {
      node.nodeValue = transform(node.nodeValue)
    }
  }

  return container.innerHTML
}

const getSfrTemplate = () => `
<h4>5. SECURITY REQUIREMENTS</h4>
<p>This section defines the Security functional requirements (SFRs) and the Security assurance requirements (SARs) that fulfill the TOE. Assignment, selection, iteration and refinement operations have been made, adhering to the following conventions:</p>
<p><strong>Assignments.</strong> They appear between square brackets. The word "assignment" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>
<p><strong>Selections.</strong> They appear between square brackets. The word "selection" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>
<p><strong>Iterations.</strong> It includes "/" and an "identifier" following requirement identifier that allows to distinguish the iterations of the requirement. Example: FCS_COP.1/XXX.</p>
<p><strong>Refinements:</strong> the text where the refinement has been done is shown <strong><em><span style="color: #FF6B6B;">bold, italic, and light red color</span></em></strong>. Where part of the content of a SFR component has been removed, the removed text is shown in <strong><em><span style="color: #FF6B6B;"><s>bold, italic, light red color and crossed out</s></span></em></strong>.</p>
<h4>5.1 Security Functional Requirements</h4>
`

function buildSfrPreviewHtml(entries: SfrPreviewEntry[]): string {
  const template = getSfrTemplate()

  if (!entries.length) {
    return template
  }

  const grouped: Record<string, { description: string; items: SfrPreviewEntry[] }> = {}

  entries.forEach(entry => {
    const classCode = entry.classCode || 'UNKNOWN'
    if (!grouped[classCode]) {
      grouped[classCode] = {
        description: getClassDescriptionForEntry(entry),
        items: [],
      }
    }
    grouped[classCode].items.push(entry)
  })

  let sectionsHtml = ''
  let classIndex = 1

  Object.keys(grouped).forEach(classCode => {
    const data = grouped[classCode]
    const classDescription = data.description || classCode
    sectionsHtml += `
<h5>5.1.${classIndex} ${classCode}: ${classDescription}</h5>
`

    let componentIndex = 1
    data.items.forEach(item => {
      const componentId = normalizeComponentId(item.componentId)
      const componentTitle = item.componentName
        ? `${componentId} : ${item.componentName}`
        : componentId
      sectionsHtml += `
<h6>5.1.${classIndex}.${componentIndex} ${componentTitle}</h6>
<div style="margin-left: 20px;">
${item.previewContent ?? ''}
</div>
`
      componentIndex += 1
    })

    classIndex += 1
  })

  return uppercaseIdentifiersInHtml(template + sectionsHtml)
}

const formatAssuranceComponentLabel = (componentId: string | undefined, componentName?: string) => {
  const normalizedId = normalizeComponentId(componentId)
  const trimmedName = componentName?.trim()
  return trimmedName ? `${normalizedId} : ${trimmedName}` : normalizedId
}

const formatComponentHeading = (componentId: string | undefined, componentName?: string) => {
  const normalizedId = normalizeComponentId(componentId)
  const trimmedName = componentName?.trim()
  return trimmedName ? `${normalizedId} – ${trimmedName}` : normalizedId
}

const formatClassHeading = (className: string | undefined, classCode: string) => {
  const trimmed = className?.trim() ?? ''
  if (!trimmed) {
    return classCode
  }

  const colonIndex = trimmed.indexOf(':')
  if (colonIndex !== -1) {
    const descriptor = trimmed.slice(colonIndex + 1).trim()
    if (descriptor) {
      return `${descriptor} (${classCode})`
    }
  }

  return `${trimmed} (${classCode})`
}

const getSarTemplate = (ealLevel: string) => `
<h4>5. SECURITY REQUIREMENTS</h4>
<h4>5.2 SECURITY ASSURANCE REQUIREMENTS</h4>
<p>The development and the evaluation of the TOE shall be done in accordance to the following security assurance requirements: <code>${escapeHtml(ealLevel)}</code> as specified in Part 5 of the Common Criteria.</p>
<p>No operations are applied to the assurance components.</p>
<p>The TOE shall meet the following security assurance requirements:</p>
`

const buildSarTableHtml = (classOrder: string[], groups: Record<string, { className: string; sars: SarPreviewEntry[] }>) => {
  let rowsHtml = ''

  if (classOrder.length === 0) {
    rowsHtml += `
      <tr>
        <td colspan="2" class="sar-preview-table__empty">No Security Assurance Requirements selected.</td>
      </tr>
    `
  } else {
    classOrder.forEach(classCode => {
      const classData = groups[classCode]
      if (!classData) {
        return
      }

      const sarEntries = classData.sars ?? []

      if (sarEntries.length === 0) {
        rowsHtml += `
          <tr>
            <td class="sar-preview-table__class-cell">${escapeHtml(classData.className)}</td>
            <td class="sar-preview-table__note">No assurance components recorded.</td>
          </tr>
        `
        return
      }

      sarEntries.forEach((sar, index) => {
        const componentLabel = escapeHtml(formatAssuranceComponentLabel(sar.componentId, sar.componentName))
        const classCell =
          index === 0
            ? `<td class="sar-preview-table__class-cell" rowspan="${sarEntries.length}">${escapeHtml(classData.className)}</td>`
            : ''

        rowsHtml += `
          <tr>
            ${classCell}
            <td class="sar-preview-table__component">${componentLabel}</td>
          </tr>
        `
      })
    })
  }

  return `
    <div class="sar-preview-table-wrapper">
      <table class="sar-preview-table">
        <thead>
          <tr>
            <th scope="col">SAR Class</th>
            <th scope="col">Assurance Components</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
    </div>
    <p class="sar-preview-table-caption">Table 7 Security Assurance Components</p>
  `
}

const buildSarSectionsHtml = (classOrder: string[], groups: Record<string, { className: string; sars: SarPreviewEntry[] }>) => {
  if (classOrder.length === 0) {
    return '<p class="sar-preview-empty">No Security Assurance Requirements have been defined.</p>'
  }

  let html = ''
  let classIndex = 1

  classOrder.forEach(classCode => {
    const classData = groups[classCode]
    if (!classData) {
      return
    }

    const headingText = escapeHtml(formatClassHeading(classData.className, classCode))
    html += `
      <section class="sar-preview-class">
        <h5 class="sar-preview-section-heading">5.3.${classIndex} ${headingText}</h5>
    `

    if (!classData.sars.length) {
      html += '<p class="sar-preview-note">No assurance components documented for this class.</p>'
      html += '</section>'
      classIndex += 1
      return
    }

    classData.sars.forEach(sar => {
      const componentHeading = escapeHtml(formatComponentHeading(sar.componentId, sar.componentName))
      const content =
        sar.previewContent && sar.previewContent.trim().length > 0
          ? sar.previewContent
          : '<p class="sar-preview-note">No component details provided.</p>'

      html += `
        <div class="sar-preview-component">
          <p class="sar-preview-component__title">${componentHeading}</p>
          <div class="sar-preview-component__body">${content}</div>
        </div>
      `
    })

    html += '</section>'
    classIndex += 1
  })

  return html
}

function buildSarPreviewHtml(entries: SarPreviewEntry[], selectedEal: string | undefined): string {
  const template = getSarTemplate(selectedEal || 'EAL 1')

  const groups: Record<string, { className: string; sars: SarPreviewEntry[] }> = {}
  const classOrder: string[] = []

  entries.forEach(entry => {
    const key = entry.classCode || 'UNKNOWN'
    if (!groups[key]) {
      groups[key] = {
        className: entry.className || key,
        sars: [],
      }
      classOrder.push(key)
    }
    groups[key].sars.push(entry)
  })

  const tableHtml = buildSarTableHtml(classOrder, groups)
  const sectionsHtml = buildSarSectionsHtml(classOrder, groups)

  return uppercaseIdentifiersInHtml(template + tableHtml + sectionsHtml)
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

    const sfrList = (sfrData?.sfrList as SfrPreviewEntry[] | undefined) ?? []
    const sarList = (sarData?.sarList as SarPreviewEntry[] | undefined) ?? []
    const sfrHtml = sfrList.length ? buildSfrPreviewHtml(sfrList) : ''
    const sarHtml = sarList.length ? buildSarPreviewHtml(sarList, sarData?.selectedEal) : ''

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
            image_base64: coverData.uploadedImageBase64,
          }
        : null,
      st_reference_html: stReferenceHTML || null,
      toe_reference_html: toeReferenceHTML || null,
      toe_overview_html: toeOverviewHTML || null,
      toe_description_html: toeDescriptionHTML || null,
      conformance_claims_html: conformanceClaimsHTML || null,
      sfr_list: sfrData?.sfrList || [],
      sfr_html: sfrHtml || null,
      sar_list: sarData?.sarList || [],
      sar_html: sarHtml || null,
      selected_eal: sarData?.selectedEal || null,
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

function handleDownloadClick() {
  if (!downloadUrl.value) {
    return
  }

  const anchor = document.createElement('a')
  anchor.href = downloadUrl.value
  anchor.download = 'Security_Target_Document.docx'
  anchor.target = '_blank'
  anchor.rel = 'noopener'
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
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
