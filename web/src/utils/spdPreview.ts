import type { SpdEntry } from '../services/sessionService'

export interface SpdPreviewData {
  assumptions?: SpdEntry[]
  threats?: SpdEntry[]
  osp?: SpdEntry[]
}

export interface SpdPreviewOptions {
  /**
   * Chapter number used for the Security Problem Definition section.
   * Defaults to 3 to preserve historical output when options are not supplied.
   */
  rootSectionNumber?: number
  /**
   * Controls whether the top-level heading (e.g. “3. Security Problem Definition”)
   * is included in the generated HTML fragment.
   */
  includeRootHeading?: boolean
}

function escapeHtml(value: string): string {
  const div = document.createElement('div')
  div.textContent = value
  return div.innerHTML
}

function buildEntriesTable(entries: SpdEntry[], nameLabel: string): string {
  if (!entries.length) {
    return ''
  }

  const rows = entries
    .map(entry => {
      const safeTitle = escapeHtml(entry.title || '')
      const description = entry.description || ''
      return `
        <tr>
          <td style="padding: 8px; vertical-align: top;">${safeTitle}</td>
          <td style="padding: 8px; vertical-align: top;">${description}</td>
        </tr>
      `
    })
    .join('')

  return `
    <table border="1" style="width: 100%; border-collapse: collapse;">
      <thead>
        <tr>
          <th style="padding: 8px; text-align: left;">${nameLabel}</th>
          <th style="padding: 8px; text-align: left;">Description</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `
}

function resolveSectionNumber(value: number | undefined, fallback: number): string {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return `${fallback}`
  }
  return `${Math.trunc(value)}`
}

export function buildSecurityProblemDefinitionHtml(
  data: SpdPreviewData,
  options: SpdPreviewOptions = {},
): string {
  const assumptions = data.assumptions ?? []
  const threats = data.threats ?? []
  const osp = data.osp ?? []
  const rootSectionNumber = resolveSectionNumber(options.rootSectionNumber, 3)
  const includeRootHeading = options.includeRootHeading ?? true

  const assumptionsHeadingNumber = `${rootSectionNumber}.1`
  const threatsHeadingNumber = `${rootSectionNumber}.2`
  const ospHeadingNumber = `${rootSectionNumber}.3`

  const sections: string[] = []

  if (includeRootHeading) {
    sections.push(`<h2>${rootSectionNumber}. Security Problem Definition</h2>`)
  }

  sections.push(
    '<p>This chapter identifies the following:</p>' +
      '<ul>' +
      '<li>Significant assumptions about the TOE’s operational environment.</li>' +
      '<li>Threats that must be countered by the TOE or its environment.</li>' +
      '</ul>' +
      '<p>This document identifies assumptions as A.assumption with “assumption” specifying a unique name. Threats are identified as T.threat with “threat” specifying a unique name.</p>',
  )

  sections.push(
    `<h3>${assumptionsHeadingNumber} Assumptions</h3>` +
      '<p>The specific conditions listed in the following subsections are assumed to exist in the TOE’s environment. These assumptions include both practical realities in the development of the TOE security requirements and the essential environmental conditions on the use of the TOE.</p>',
  )

  if (assumptions.length) {
    sections.push(buildEntriesTable(assumptions, 'Assumptions'))
  } else {
    sections.push('<p>There are no assumptions identified for this TOE.</p>')
  }

  sections.push(
    `<h3>${threatsHeadingNumber} Threats</h3>` +
      '<p>The following table defines the security threats for the TOE.</p>',
  )

  if (threats.length) {
    sections.push(buildEntriesTable(threats, 'Threats'))
  } else {
    sections.push('<p>There are no threats identified for this TOE.</p>')
  }

  sections.push(`<h3>${ospHeadingNumber} Organisational Security Policies</h3>`)
  if (osp.length) {
    sections.push(
      '<p>The following table defines the organizational security policies which are a set of rules, practices, and procedures imposed by an organization to address its security needs.</p>' +
        buildEntriesTable(osp, 'Organisational Security Policies'),
    )
  } else {
    sections.push('<p>There are no Organizational Security Policies identified for this TOE.</p>')
  }

  return sections.join('')
}

export function hasAssumptions(entries: SpdEntry[] | undefined | null): boolean {
  return Array.isArray(entries) && entries.length > 0
}

export function hasThreats(entries: SpdEntry[] | undefined | null): boolean {
  return Array.isArray(entries) && entries.length > 0
}

export function hasOsp(entries: SpdEntry[] | undefined | null): boolean {
  return Array.isArray(entries) && entries.length > 0
}
