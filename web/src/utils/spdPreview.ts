import type { SpdEntry } from '../services/sessionService'

export interface SpdPreviewData {
  assumptions?: SpdEntry[]
  threats?: SpdEntry[]
  osp?: SpdEntry[]
}

export interface SpdPreviewOptions {
  /**
   * Root chapter number used when generating heading text (e.g. 2 for "2. Security Problem Definition").
   * Defaults to 3 so that standalone SPD previews keep the previous numbering.
   */
  rootSectionNumber?: number
  /**
   * Whether to include the root heading ("X. Security Problem Definition").
   * The final preview already adds its own heading so it disables this flag to avoid duplication.
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

export function buildSecurityProblemDefinitionHtml(
  data: SpdPreviewData,
  options: SpdPreviewOptions = {}
): string {
  const assumptions = data.assumptions ?? []
  const threats = data.threats ?? []
  const osp = data.osp ?? []

  const rootSectionNumber = options.rootSectionNumber ?? 3
  const includeRootHeading = options.includeRootHeading ?? true

  let html = ''

  if (includeRootHeading) {
    html += `<h2>${rootSectionNumber}. Security Problem Definition</h2>`
  }
  html +=
    '<p>This chapter identifies the following:</p>' +
    '<ul>' +
    '<li>Significant assumptions about the TOE’s operational environment.</li>' +
    '<li>Threats that must be countered by the TOE or its environment.</li>' +
    '</ul>'
  html +=
    '<p>This document identifies assumptions as A.assumption with “assumption” specifying a unique name. Threats are identified as T.threat with “threat” specifying a unique name.</p>'

  html += `<h3>${rootSectionNumber}.1 Assumptions</h3>`
  html +=
    '<p>The specific conditions listed in the following subsections are assumed to exist in the TOE’s environment. These assumptions include both practical realities in the development of the TOE security requirements and the essential environmental conditions on the use of the TOE.</p>'

  if (assumptions.length) {
    html += buildEntriesTable(assumptions, 'Assumptions')
  } else {
    html += '<p>There are no assumptions identified for this TOE.</p>'
  }

  html += `<h3>${rootSectionNumber}.2 Threats</h3>`
  html += '<p>The following table defines the security threats for the TOE.</p>'

  if (threats.length) {
    html += buildEntriesTable(threats, 'Threats')
  } else {
    html += '<p>There are no threats identified for this TOE.</p>'
  }

  html += `<h3>${rootSectionNumber}.3 Organisational Security Policies</h3>`
  if (osp.length) {
    html +=
      '<p>The following table defines the organizational security policies which are a set of rules, practices, and procedures imposed by an organization to address its security needs.</p>'
    html += buildEntriesTable(osp, 'Organisational Security Policies')
  } else {
    html += '<p>There are no Organizational Security Policies identified for this TOE.</p>'
  }

  return html
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
