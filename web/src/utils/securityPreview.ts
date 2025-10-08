export interface SfrMetadata {
  classLabel?: string
  classDescription?: string
  customClassInput?: string
  customComponentInput?: string
  componentKey?: string
}

export interface SfrPreviewEntry {
  classCode?: string
  className?: string
  classDescription?: string
  componentId?: string
  componentName?: string
  previewContent?: string
  metadata?: SfrMetadata
  originalClass?: string
  source?: 'database' | 'custom'
}

export interface SarMetadata {
  classLabel?: string
  customClassInput?: string
  customComponentInput?: string
}

export interface SarPreviewEntry {
  classCode?: string
  className?: string
  componentId?: string
  componentName?: string
  previewContent?: string
  metadata?: SarMetadata
  originalClass?: string
  source?: 'database' | 'custom'
}

export interface SfrPreviewOptions {
  rootSectionNumber?: number
  includeRootHeading?: boolean
  includeFunctionalHeading?: boolean
}

export interface SarPreviewOptions {
  rootSectionNumber?: number
  selectedEal?: string
  includeRootHeading?: boolean
  includeAssuranceHeading?: boolean
}

export const normalizeComponentId = (value: string | undefined | null): string =>
  (value ?? '').trim().toUpperCase()

export const uppercaseIdentifiersInHtml = (html: string): string => {
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

const cleanWhitespace = (value: string | undefined | null): string =>
  (value ?? '').replace(/\s+/g, ' ').trim()

const deriveClassDescriptionFromLabel = (label: string): string => {
  const colonIndex = label.indexOf(':')
  if (colonIndex !== -1) {
    return cleanWhitespace(label.slice(colonIndex + 1))
  }
  return cleanWhitespace(label)
}

const resolveSfrClassDescription = (entry: SfrPreviewEntry): string => {
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

const resolveSarClassName = (entry: SarPreviewEntry): string => {
  if (entry.className) {
    return cleanWhitespace(entry.className)
  }
  if (entry.metadata?.classLabel) {
    return cleanWhitespace(entry.metadata.classLabel)
  }
  return entry.classCode ?? 'UNKNOWN'
}

const formatAssuranceComponentLabel = (componentId: string, componentName?: string) => {
  const normalizedId = normalizeComponentId(componentId)
  const trimmedName = cleanWhitespace(componentName)
  return trimmedName ? `${normalizedId} : ${trimmedName}` : normalizedId
}

const formatComponentHeading = (componentId: string, componentName?: string) => {
  const normalizedId = normalizeComponentId(componentId)
  const trimmedName = cleanWhitespace(componentName)
  return trimmedName ? `${normalizedId} – ${trimmedName}` : normalizedId
}

const escapeHtml = (value: string): string =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const buildSfrTemplate = ({
  rootSectionNumber,
  includeRootHeading,
  includeFunctionalHeading,
}: Required<Omit<SfrPreviewOptions, 'rootSectionNumber'>> & { rootSectionNumber: number }): string => {
  const sections: string[] = []
  if (includeRootHeading) {
    sections.push(`<h4>${rootSectionNumber}. SECURITY REQUIREMENTS</h4>`)
  }
  if (includeFunctionalHeading) {
    sections.push(`<h4>${rootSectionNumber}.1 Security Functional Requirements</h4>`)
  }
  sections.push(
    '<p>This section defines the Security functional requirements (SFRs) and the Security assurance requirements (SARs) that fulfill the TOE. Assignment, selection, iteration and refinement operations have been made, adhering to the following conventions:</p>',
    '<p><strong>Assignments.</strong> They appear between square brackets. The word "assignment" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>',
    '<p><strong>Selections.</strong> They appear between square brackets. The word "selection" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>',
    '<p><strong>Iterations.</strong> It includes "/" and an "identifier" following requirement identifier that allows to distinguish the iterations of the requirement. Example: FCS_COP.1/XXX.</p>',
    '<p><strong>Refinements:</strong> the text where the refinement has been done is shown <strong><em><span style="color: #FF6B6B;">bold, italic, and light red color</span></em></strong>. Where part of the content of a SFR component has been removed, the removed text is shown in <strong><em><span style="color: #FF6B6B;"><s>bold, italic, light red color and crossed out</s></span></em></strong>.</p>'
  )
  return sections.join('')
}

export const buildSfrPreviewHtml = (
  entries: SfrPreviewEntry[] | undefined,
  options: SfrPreviewOptions = {}
): string => {
  const rootSectionNumber = options.rootSectionNumber ?? 5
  const includeRootHeading = options.includeRootHeading ?? true
  const includeFunctionalHeading = options.includeFunctionalHeading ?? true

  const template = buildSfrTemplate({ rootSectionNumber, includeRootHeading, includeFunctionalHeading })

  if (!entries || entries.length === 0) {
    return uppercaseIdentifiersInHtml(template)
  }

  const sfrsByClass: Record<string, { classDescription: string; sfrs: SfrPreviewEntry[] }> = {}
  entries.forEach(entry => {
    const key = normalizeComponentId(entry.classCode ?? 'UNKNOWN') || 'UNKNOWN'
    if (!sfrsByClass[key]) {
      sfrsByClass[key] = {
        classDescription: resolveSfrClassDescription(entry),
        sfrs: [],
      }
    }
    sfrsByClass[key].sfrs.push(entry)
  })

  const sortedKeys = Object.keys(sfrsByClass)
  sortedKeys.sort()

  let allSections = ''
  let classIndex = 1
  const classPrefix = `${rootSectionNumber}.1`

  sortedKeys.forEach(classCode => {
    const classData = sfrsByClass[classCode]
    const classDescription = classData.classDescription || classCode

    allSections += `<h5>${classPrefix}.${classIndex} ${classCode}: ${escapeHtml(classDescription)}</h5>`

    let componentIndex = 1
    classData.sfrs.forEach(sfr => {
      const componentId = normalizeComponentId(sfr.componentId ?? '')
      const componentTitle = sfr.componentName
        ? `${componentId} : ${escapeHtml(sfr.componentName)}`
        : componentId
      const body = sfr.previewContent ?? ''
      allSections += `<h6>${classPrefix}.${classIndex}.${componentIndex} ${componentTitle}</h6>`
      allSections += `<div style="margin-left: 20px;">${body}</div>`
      componentIndex += 1
    })

    classIndex += 1
  })

  return uppercaseIdentifiersInHtml(template + allSections)
}

const buildSarTemplate = ({
  rootSectionNumber,
  includeRootHeading,
  includeAssuranceHeading,
  selectedEal,
}: Required<Omit<SarPreviewOptions, 'rootSectionNumber' | 'selectedEal'>> & {
  rootSectionNumber: number
  selectedEal: string
}): string => {
  const sections: string[] = []
  if (includeRootHeading) {
    sections.push(`<h4>${rootSectionNumber}. SECURITY REQUIREMENTS</h4>`)
  }
  const assuranceHeadingNumber = `${rootSectionNumber}.${includeAssuranceHeading ? '2' : '2'}`
  if (includeAssuranceHeading) {
    sections.push(`<h4>${assuranceHeadingNumber} SECURITY ASSURANCE REQUIREMENTS</h4>`)
  }
  const escapedEal = escapeHtml(selectedEal)
  sections.push(
    `<p>The development and the evaluation of the TOE shall be done in accordance to the following security assurance requirements: <code>${escapedEal}</code> as specified in Part 5 of the Common Criteria.</p>`,
    '<p>No operations are applied to the assurance components.</p>',
    '<p>The TOE shall meet the following security assurance requirements:</p>'
  )
  return sections.join('')
}

export const buildSarPreviewHtml = (
  entries: SarPreviewEntry[] | undefined,
  options: SarPreviewOptions = {}
): string => {
  const rootSectionNumber = options.rootSectionNumber ?? 5
  const includeRootHeading = options.includeRootHeading ?? true
  const includeAssuranceHeading = options.includeAssuranceHeading ?? true
  const selectedEal = options.selectedEal ?? 'EAL 1'

  const template = buildSarTemplate({
    rootSectionNumber,
    includeRootHeading,
    includeAssuranceHeading,
    selectedEal,
  })

  if (!entries || entries.length === 0) {
    const tableHtml = `
      <div class="sar-preview-table-wrapper">
        <table class="sar-preview-table">
          <thead>
            <tr>
              <th scope="col">SAR Class</th>
              <th scope="col">Assurance Components</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colspan="2" class="sar-preview-table__empty">No Security Assurance Requirements selected.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="sar-preview-table-caption">Table 7 Security Assurance Components</p>
    `
    return uppercaseIdentifiersInHtml(template + tableHtml)
  }

  const groups: Record<string, { className: string; sars: SarPreviewEntry[] }> = {}
  const classOrder: string[] = []

  entries.forEach(entry => {
    const key = normalizeComponentId(entry.classCode ?? 'UNKNOWN') || 'UNKNOWN'
    if (!groups[key]) {
      groups[key] = {
        className: resolveSarClassName(entry),
        sars: [],
      }
      classOrder.push(key)
    }
    groups[key].sars.push(entry)
  })

  let rowsHtml = ''
  classOrder.forEach(classCode => {
    const classData = groups[classCode]
    const sarEntries = classData?.sars ?? []

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
      const componentLabel = escapeHtml(formatAssuranceComponentLabel(sar.componentId ?? '', sar.componentName))
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

  const tableHtml = `
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

  let sectionsHtml = ''
  const classBaseNumber = `${rootSectionNumber}.${includeAssuranceHeading ? '3' : '2'}`
  classOrder.forEach((classCode, classIndex) => {
    const classData = groups[classCode]
    if (!classData) {
      return
    }

    const headingText = escapeHtml(`${classCode}: ${cleanWhitespace(classData.className)}`)
    sectionsHtml += `
      <section class="sar-preview-class">
        <h5 class="sar-preview-section-heading">${classBaseNumber}.${classIndex + 1} ${headingText}</h5>
    `

    const sarEntries = classData.sars ?? []
    if (sarEntries.length === 0) {
      sectionsHtml += '<p class="sar-preview-note">No assurance components documented for this class.</p>'
      sectionsHtml += '</section>'
      return
    }

    sarEntries.forEach(sar => {
      const componentHeading = escapeHtml(formatComponentHeading(sar.componentId ?? '', sar.componentName))
      const content =
        sar.previewContent && sar.previewContent.trim().length > 0
          ? sar.previewContent
          : '<p class="sar-preview-note">No component details provided.</p>'

      sectionsHtml += `
        <div class="sar-preview-component">
          <p class="sar-preview-component__title">${componentHeading}</p>
          <div class="sar-preview-component__body">${content}</div>
        </div>
      `
    })

    sectionsHtml += '</section>'
  })

  return uppercaseIdentifiersInHtml(template + tableHtml + sectionsHtml)
}
