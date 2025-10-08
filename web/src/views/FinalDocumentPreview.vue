<template>
  <div class="final-preview-page">
    <div class="card final-preview-menubar">
      <div class="menubar-left">
        <h1>Final Document Preview</h1>
        <span class="subtitle">Here is all the Current Preview of all Security Target Document</span>
      </div>
      <div class="menubar-actions">
        <button
          class="btn"
          type="button"
          @click="generatePreview"
          :disabled="previewLoading || !hasAnySectionData"
        >
          {{ previewLoading ? 'Generating…' : 'Generate Preview' }}
        </button>
        <button class="btn" type="button" @click="saveProjectSnapshot">Save Project</button>
        <a
          class="btn primary"
          :class="{ disabled: !hasGeneratedDocx || previewLoading }"
          :href="downloadUrl"
          :aria-disabled="!hasGeneratedDocx || previewLoading"
          @click="handleDownloadClick"
        >
          Download DOCX File
        </a>
      </div>
    </div>

    <div class="card status-card">
      <header class="status-header">
        <h2>Section status</h2>
        <p class="status-subtitle">Review the completion state for each section</p>
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
        Please complete or review the following sections before generating the final document:
        <span>{{ missingSections.join(', ') }}</span>
      </div>
      <div v-else class="status-success">All tracked sections have been completed.</div>
    </div>

    <div class="card preview-card">
      <header class="preview-header">
        <div>
          <h2>Preview Window</h2>
          <p class="preview-subtitle">
            Combined preview for the Security Target document, with automatic page breaks per section.
          </p>
        </div>
      </header>
      <div class="preview-body">
        <div v-if="!hasAnySectionData" class="info-message">
          <p>
            Please fill in at least one section (Cover, ST Introduction details, Conformance Claims, SFR, or SAR) to generate the
            final preview.
          </p>
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
  type SessionData,
  type SarSessionData,
} from '../services/sessionService'
import { downloadProjectSnapshot } from '../services/projectPersistence'

interface SectionStatus {
  key: string
  label: string
  complete: boolean
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
  { key: 'cc-claims', label: 'CC Conformance Claims', complete: false },
  { key: 'pp-claims', label: 'Protection Profile Claims', complete: false },
  { key: 'notes', label: 'Additional Notes', complete: false },
  { key: 'sfr', label: 'Security Functional Requirements', complete: false },
  { key: 'sar', label: 'Security Assurance Requirements', complete: false },
])

const missingSections = computed(() => sectionStatus.value.filter(section => !section.complete).map(section => section.label))
const hasAnySectionData = computed(() => sectionStatus.value.some(section => section.complete))

const downloadUrl = computed(() => {
  if (!generatedDocxPath.value) return ''
  return api.getUri({ url: generatedDocxPath.value })
})

const saveProjectSnapshot = () => {
  downloadProjectSnapshot()
}

const handleDownloadClick = (event: MouseEvent) => {
  if (!hasGeneratedDocx.value || previewLoading.value) {
    event.preventDefault()
  }
}

const hasCoverContent = (data: CoverSessionData | null): boolean => {
  if (!data) return false
  const form = data.form || {}
  return Boolean(
    data.uploadedImagePath ||
    form.title ||
    form.version ||
    form.revision ||
    form.description ||
    form.manufacturer ||
    form.date
  )
}

const hasStReferenceContent = (data: STReferenceSessionData | null): boolean => {
  if (!data) return false
  return Boolean(data.stTitle || data.stVersion || data.stDate || data.author)
}

const hasToeReferenceContent = (data: TOEReferenceSessionData | null): boolean => {
  if (!data) return false
  return Boolean(data.toeName || data.toeVersion || data.toeIdentification || data.toeType)
}

const hasToeOverviewContent = (data: TOEOverviewSessionData | null): boolean => {
  if (!data) return false
  return Boolean(
    data.toeOverview ||
    data.toeType ||
    data.toeUsage ||
    data.toeMajorSecurityFeatures ||
    data.nonToeHardwareSoftwareFirmware
  )
}

const hasToeDescriptionContent = (data: TOEDescriptionSessionData | null): boolean => {
  if (!data) return false
  return Boolean(data.toeDescription || data.toePhysicalScope || data.toeLogicalScope)
}

const hasConformanceField = (value: string | undefined | null): boolean => Boolean(value && value.trim().length)

const hasSfrContent = (data: SessionData | null): boolean => Boolean(data && Array.isArray(data.sfrList) && data.sfrList.length)
const hasSarContent = (data: SarSessionData | null): boolean => Boolean(data && Array.isArray(data.sarList) && data.sarList.length)

const updateSectionStatus = () => {
  const coverData = sessionService.loadCoverData()
  const stReferenceData = sessionService.loadSTReferenceData()
  const toeReferenceData = sessionService.loadTOEReferenceData()
  const toeOverviewData = sessionService.loadTOEOverviewData()
  const toeDescriptionData = sessionService.loadTOEDescriptionData()
  const conformanceData = sessionService.loadConformanceClaimsData()
  const sfrData = sessionService.loadSfrData()
  const sarData = sessionService.loadSarData()

  sectionStatus.value = [
    { key: 'cover', label: 'Cover', complete: hasCoverContent(coverData) },
    { key: 'st-reference', label: 'ST Reference', complete: hasStReferenceContent(stReferenceData) },
    { key: 'toe-reference', label: 'TOE Reference', complete: hasToeReferenceContent(toeReferenceData) },
    { key: 'toe-overview', label: 'TOE Overview', complete: hasToeOverviewContent(toeOverviewData) },
    { key: 'toe-description', label: 'TOE Description', complete: hasToeDescriptionContent(toeDescriptionData) },
    { key: 'cc-claims', label: 'CC Conformance Claims', complete: hasConformanceField(conformanceData?.ccConformance) },
    { key: 'pp-claims', label: 'Protection Profile Claims', complete: hasConformanceField(conformanceData?.ppClaims) },
    { key: 'notes', label: 'Additional Notes', complete: hasConformanceField(conformanceData?.additionalNotes) },
    { key: 'sfr', label: 'Security Functional Requirements', complete: hasSfrContent(sfrData) },
    { key: 'sar', label: 'Security Assurance Requirements', complete: hasSarContent(sarData) },
  ]
}

const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const buildStReferenceHtml = (): string => {
  const data = sessionService.loadSTReferenceData()
  if (!hasStReferenceContent(data)) {
    return ''
  }

  let html = '<h2>Security Target (ST) Reference</h2>'
  html += '<table border="1" style="width: 100%; border-collapse: collapse;">'

  if (data?.stTitle) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Title</td><td style="padding: 8px;">${escapeHtml(data.stTitle)}</td></tr>`
  }
  if (data?.stVersion) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Version</td><td style="padding: 8px;">${escapeHtml(data.stVersion)}</td></tr>`
  }
  if (data?.stDate) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">ST Date</td><td style="padding: 8px;">${escapeHtml(data.stDate)}</td></tr>`
  }
  if (data?.author) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">Author</td><td style="padding: 8px;">${escapeHtml(data.author).replace(/\n/g, '<br>')}</td></tr>`
  }

  html += '</table>'
  html += '<p style="text-align: center; margin-top: 8px;"><em>Security Target reference</em></p>'
  return html
}

const buildToeReferenceHtml = (): string => {
  const data = sessionService.loadTOEReferenceData()
  if (!hasToeReferenceContent(data)) {
    return ''
  }

  let html = '<h2>TOE Reference</h2>'
  html += '<table border="1" style="width: 100%; border-collapse: collapse;">'

  if (data?.toeName) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Name</td><td style="padding: 8px;">${escapeHtml(data.toeName)}</td></tr>`
  }
  if (data?.toeVersion) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Version</td><td style="padding: 8px;">${escapeHtml(data.toeVersion)}</td></tr>`
  }
  if (data?.toeIdentification) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Identification</td><td style="padding: 8px;">${escapeHtml(data.toeIdentification)}</td></tr>`
  }
  if (data?.toeType) {
    html += `<tr><td style="padding: 8px; font-weight: bold;">TOE Type</td><td style="padding: 8px;">${escapeHtml(data.toeType)}</td></tr>`
  }

  html += '</table>'
  html += '<p style="text-align: center; margin-top: 8px;"><em>TOE reference</em></p>'
  return html
}

const buildToeOverviewHtml = (): string => {
  const data = sessionService.loadTOEOverviewData()
  if (!hasToeOverviewContent(data)) {
    return ''
  }

  let html = '<h2>TOE Overview</h2>'

  if (data?.toeOverview) {
    html += `<div>${data.toeOverview}</div>`
  }
  if (data?.toeType) {
    html += '<h3>TOE Type</h3>'
    html += `<div>${data.toeType}</div>`
  }
  if (data?.toeUsage) {
    html += '<h3>TOE Usage</h3>'
    html += `<div>${data.toeUsage}</div>`
  }
  if (data?.toeMajorSecurityFeatures) {
    html += '<h3>TOE Major Security Features</h3>'
    html += `<div>${data.toeMajorSecurityFeatures}</div>`
  }
  if (data?.nonToeHardwareSoftwareFirmware) {
    html += '<h3>Non-TOE Hardware/Software/Firmware</h3>'
    html += `<div>${data.nonToeHardwareSoftwareFirmware}</div>`
  }

  return html
}

const buildToeDescriptionHtml = (): string => {
  const data = sessionService.loadTOEDescriptionData()
  if (!hasToeDescriptionContent(data)) {
    return ''
  }

  let html = '<h2>TOE Description</h2>'

  if (data?.toeDescription) {
    html += `<div>${data.toeDescription}</div>`
  }
  if (data?.toePhysicalScope) {
    html += '<h3>TOE Physical Scope</h3>'
    html += `<div>${data.toePhysicalScope}</div>`
  }
  if (data?.toeLogicalScope) {
    html += '<h3>TOE Logical Scope</h3>'
    html += `<div>${data.toeLogicalScope}</div>`
  }

  return html
}

const buildConformanceHtmlSegments = (): { cc: string; pp: string; notes: string } => {
  const data = sessionService.loadConformanceClaimsData()
  const cc = data?.ccConformance?.trim().length
    ? `<h2>Common Criteria (CC) Conformance Claims</h2><div>${data.ccConformance}</div>`
    : ''
  const pp = data?.ppClaims?.trim().length
    ? `<h2>Protection Profile (PP) Claims</h2><div>${data.ppClaims}</div>`
    : ''
  const notes = data?.additionalNotes?.trim().length
    ? `<h2>Additional Notes</h2><div>${data.additionalNotes}</div>`
    : ''
  return { cc, pp, notes }
}

const normalizeComponentId = (value: string): string => value.trim().toUpperCase()

const getSfrTemplate = (): string => `
  <h2>Security Functional Requirements</h2>
  <p>This section defines the Security functional requirements (SFRs) and the Security assurance requirements (SARs) that fulfill the TOE. Assignment, selection, iteration and refinement operations have been made, adhering to the following conventions:</p>
  <p><strong>Assignments.</strong> They appear between square brackets. The word "assignment" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>
  <p><strong>Selections.</strong> They appear between square brackets. The word "selection" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>
  <p><strong>Iterations.</strong> It includes "/" and an "identifier" following requirement identifier that allows to distinguish the iterations of the requirement. Example: FCS_COP.1/XXX.</p>
  <p><strong>Refinements:</strong> the text where the refinement has been done is shown <strong><em><span style="color: #FF6B6B;">bold, italic, and light red color</span></em></strong>. Where part of the content of a SFR component has been removed, the removed text is shown in <strong><em><span style="color: #FF6B6B;"><s>bold, italic, light red color and crossed out</s></span></em></strong>.</p>
  <h3>Security Functional Requirements</h3>
`

const uppercaseIdentifiersInHtml = (html: string): string => {
  const transform = (text: string) => text.replace(/\b([a-z][a-z0-9_.-]*[_.][a-z0-9_.-]*)\b/gi, match => match.toUpperCase())
  const container = document.createElement('div')
  container.innerHTML = html

  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null)
  const nodes: Text[] = []
  while (walker.nextNode()) {
    const current = walker.currentNode as Text
    if (current.nodeValue && current.nodeValue.trim().length) {
      nodes.push(current)
    }
  }

  nodes.forEach(node => {
    if (node.nodeValue) {
      node.nodeValue = transform(node.nodeValue)
    }
  })

  return container.innerHTML
}

const buildSfrHtml = (): string => {
  const data = sessionService.loadSfrData()
  if (!hasSfrContent(data)) {
    return ''
  }

  const template = getSfrTemplate()
  const sfrList = Array.isArray(data?.sfrList) ? data!.sfrList : []
  const sfrsByClass: Record<string, { label: string; sfrs: any[] }> = {}

  sfrList.forEach((sfr: any) => {
    const classCode = typeof sfr.classCode === 'string' && sfr.classCode.trim() ? sfr.classCode.trim().toUpperCase() : 'UNKNOWN'
    if (!sfrsByClass[classCode]) {
      sfrsByClass[classCode] = {
        label: sfr.classDescription || sfr.metadata?.classDescription || sfr.className || classCode,
        sfrs: [],
      }
    }
    sfrsByClass[classCode].sfrs.push(sfr)
  })

  let classIndex = 1
  let html = ''

  Object.keys(sfrsByClass).forEach(classCode => {
    const classData = sfrsByClass[classCode]
    const classDescription = classData.label || classCode

    html += `<h4>5.1.${classIndex} ${classCode}: ${escapeHtml(classDescription)}</h4>`

    let componentIndex = 1
    classData.sfrs.forEach((sfr: any) => {
      const componentId = normalizeComponentId(typeof sfr.componentId === 'string' ? sfr.componentId : sfr.componentKey || '')
      const componentName = typeof sfr.componentName === 'string' && sfr.componentName.trim().length
        ? ` : ${escapeHtml(sfr.componentName)}`
        : ''
      html += `<h5>5.1.${classIndex}.${componentIndex} ${componentId}${componentName}</h5>`
      html += `<div style="margin-left: 20px;">${sfr.previewContent || ''}</div>`
      componentIndex++
    })

    classIndex++
  })

  return uppercaseIdentifiersInHtml(template + html)
}

const getSarTemplate = (ealLevel: string): string => {
  const escapedEal = escapeHtml(ealLevel)
  return `
    <h2>Security Assurance Requirements</h2>
    <h3>Security Assurance Overview</h3>
    <p>The development and the evaluation of the TOE shall be done in accordance to the following security assurance requirements: <code>${escapedEal}</code> as specified in Part 5 of the Common Criteria.</p>
    <p>No operations are applied to the assurance components.</p>
    <p>The TOE shall meet the following security assurance requirements:</p>
  `
}

const formatAssuranceComponentLabel = (componentId: string, componentName?: string): string => {
  const normalizedId = normalizeComponentId(componentId || '')
  const trimmedName = componentName?.trim()
  return trimmedName ? `${normalizedId} - ${trimmedName}` : normalizedId
}

const formatComponentHeading = (componentId: string, componentName?: string): string => {
  const normalizedId = normalizeComponentId(componentId || '')
  const trimmedName = componentName?.trim()
  return trimmedName ? `${normalizedId} – ${trimmedName}` : normalizedId
}

const formatClassHeading = (className: string, classCode: string): string => {
  const trimmed = className.trim()
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

const buildSarTableHtml = (
  classOrder: string[],
  groups: Record<string, { className: string; sars: any[] }>
): string => {
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

      sarEntries.forEach((sar: any, index: number) => {
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
    <p class="sar-preview-table-caption">Security Assurance Components</p>
  `
}

const buildSarSectionsHtml = (
  classOrder: string[],
  groups: Record<string, { className: string; sars: any[] }>
): string => {
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
        <h4 class="sar-preview-section-heading">5.3.${classIndex} ${headingText}</h4>
    `

    if (!classData.sars.length) {
      html += '<p class="sar-preview-note">No assurance components documented for this class.</p>'
      html += '</section>'
      classIndex++
      return
    }

    classData.sars.forEach((sar: any) => {
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
    classIndex++
  })

  return html
}

const buildSarHtml = (): string => {
  const data = sessionService.loadSarData()
  if (!hasSarContent(data)) {
    return ''
  }

  const sarList = Array.isArray(data?.sarList) ? data!.sarList : []
  const ealLevel = data?.selectedEal || 'EAL 1'
  const groups: Record<string, { className: string; sars: any[] }> = {}
  const classOrder: string[] = []

  sarList.forEach((sar: any) => {
    const classCode = typeof sar.classCode === 'string' && sar.classCode.trim() ? sar.classCode.trim().toUpperCase() : 'UNKNOWN'
    if (!groups[classCode]) {
      groups[classCode] = {
        className: sar.className || classCode,
        sars: [],
      }
      classOrder.push(classCode)
    }

    groups[classCode].sars.push(sar)
  })

  const template = getSarTemplate(ealLevel)
  const tableHtml = buildSarTableHtml(classOrder, groups)
  const sectionsHtml = buildSarSectionsHtml(classOrder, groups)

  return uppercaseIdentifiersInHtml(template + tableHtml + sectionsHtml)
}

const buildCoverPayload = () => {
  const coverData = sessionService.loadCoverData()
  if (!coverData) {
    return null
  }

  const form = coverData.form || {}
  if (!hasCoverContent(coverData)) {
    return null
  }

  return {
    title: form.title || '',
    version: form.version || '',
    revision: form.revision || '',
    description: form.description || '',
    manufacturer: form.manufacturer || '',
    date: form.date || '',
    image_path: coverData.uploadedImagePath,
  }
}

const generatePreview = async () => {
  updateSectionStatus()

  if (!hasAnySectionData.value || previewLoading.value) {
    return
  }

  if (!userToken.value) {
    userToken.value = sessionService.getUserToken()
  }

  previewError.value = ''
  previewLoading.value = true

  await nextTick()
  cleanupDocx()
  hasGeneratedDocx.value = false

  try {
    const coverPayload = buildCoverPayload()
    const stReferenceHtml = buildStReferenceHtml()
    const toeReferenceHtml = buildToeReferenceHtml()
    const toeOverviewHtml = buildToeOverviewHtml()
    const toeDescriptionHtml = buildToeDescriptionHtml()
    const { cc, pp, notes } = buildConformanceHtmlSegments()
    const sfrHtml = buildSfrHtml()
    const sarHtml = buildSarHtml()

    const payload = {
      user_id: userToken.value,
      cover_data: coverPayload,
      st_reference_html: stReferenceHtml || null,
      toe_reference_html: toeReferenceHtml || null,
      toe_overview_html: toeOverviewHtml || null,
      toe_description_html: toeDescriptionHtml || null,
      cc_conformance_html: cc || null,
      pp_claims_html: pp || null,
      additional_notes_html: notes || null,
      sfr_html: sfrHtml || null,
      sar_html: sarHtml || null,
    }

    const response = await api.post('/final-document/preview', payload)
    const path: string | undefined = response.data?.path

    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }

    generatedDocxPath.value = path
    hasGeneratedDocx.value = true
    await nextTick()
    await renderDocxPreview(path)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || 'Unable to generate the final document preview.'
    previewError.value = message
  } finally {
    previewLoading.value = false
  }
}

const renderDocxPreview = async (path: string) => {
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

const cleanupDocx = (keepalive = false) => {
  if (!userToken.value || !generatedDocxPath.value) {
    return
  }

  const url = api.getUri({ url: `/final-document/preview/${userToken.value}` })
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
}

.menubar-left h1 {
  margin: 0;
}

.subtitle {
  color: var(--muted);
}

.menubar-actions {
  display: flex;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:hover:not(.disabled):not(:disabled) {
  background: #374151;
  transform: translateY(-1px);
}

.btn:disabled,
.btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.btn.primary {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
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

@media (max-width: 768px) {
  .final-preview-menubar {
    flex-direction: column;
    align-items: flex-start;
  }

  .menubar-actions {
    width: 100%;
    flex-direction: column;
  }

  .menubar-actions .btn {
    width: 100%;
  }

  .status-list li {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
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
