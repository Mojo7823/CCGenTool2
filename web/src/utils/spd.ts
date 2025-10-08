import { type SpdEntry } from '../services/sessionService'

export type SpdSectionKey = 'assumptions' | 'threats' | 'osp'

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function ensurePrefixedTitle(title: string, prefix: string): string {
  const trimmed = title.trim()
  if (!trimmed) {
    return ''
  }

  const normalizedPrefix = prefix.toUpperCase()
  const upperValue = trimmed.toUpperCase()
  if (upperValue.startsWith(`${normalizedPrefix}.`)) {
    const remainder = trimmed.slice(trimmed.indexOf('.') + 1).trimStart()
    return `${normalizedPrefix}.${remainder}`
  }

  const withoutExistingPrefix = trimmed.replace(/^[A-Za-z]+\./, '').trim()
  return `${normalizedPrefix}.${withoutExistingPrefix}`
}

export function formatSpdEntryTitle(section: SpdSectionKey, title: string): string {
  if (section === 'assumptions') {
    return ensurePrefixedTitle(title, 'A')
  }

  if (section === 'threats') {
    return ensurePrefixedTitle(title, 'T')
  }

  return title.trim()
}

function buildTableHtml(section: SpdSectionKey, entries: SpdEntry[], label: string): string {
  if (entries.length === 0) {
    if (section === 'osp') {
      return '<p>There are no Organizational Security Policies identified for this TOE.</p>'
    }

    return ''
  }

  let html = '<table border="1" style="width: 100%; border-collapse: collapse;">'

  const headerLabel =
    section === 'assumptions' ? 'Assumptions' : section === 'threats' ? 'Threats' : 'Organisational Security Policies'

  html += `
    <tr>
      <th style="width: 30%; padding: 8px; text-align: left;">${escapeHtml(headerLabel)}</th>
      <th style="padding: 8px; text-align: left;">Description</th>
    </tr>
  `

  for (const entry of entries) {
    const formattedTitle = formatSpdEntryTitle(section, entry.title)
    const safeTitle = escapeHtml(formattedTitle)
    const description = entry.description || ''

    html += `
      <tr>
        <td style="width: 30%; padding: 8px; font-weight: bold; vertical-align: top;">${safeTitle}</td>
        <td style="padding: 8px;">${description}</td>
      </tr>
    `
  }

  html += '</table>'
  html += `<p style="text-align: center; margin-top: 8px;"><em>${label}</em></p>`

  return html
}

function buildIntroHtml(): string {
  return `
    <h2>3. Security Problem Definition</h2>
    <p>This chapter identifies the following:</p>
    <ul>
      <li>Significant assumptions about the TOE’s operational environment.</li>
      <li>Threats that must be countered by the TOE or its environment</li>
    </ul>
    <p>This document identifies assumptions as <strong>A.assumption</strong> with “assumption” specifying a unique name. Threats are identified as <strong>T.threat</strong> with “threat” specifying a unique name.</p>
  `
}

function buildAssumptionsContent(entries: SpdEntry[]): string {
  let html = `
    <h3>3.1 Assumptions</h3>
    <p>The specific conditions listed in the following subsections are assumed to exist in the TOE’s environment. These assumptions include both practical realities in the development of the TOE security requirements and the essential environmental conditions on the use of the TOE.</p>
  `

  if (entries.length === 0) {
    html += '<p>No assumptions have been documented at this time.</p>'
    return html
  }

  html += buildTableHtml('assumptions', entries, 'Table 3-1 Assumptions')
  return html
}

function buildThreatsContent(entries: SpdEntry[]): string {
  let html = `
    <h3>3.2 Threats</h3>
    <p>The following table defines the security threats for the TOE.</p>
  `

  if (entries.length === 0) {
    html += '<p>No threats have been documented at this time.</p>'
    return html
  }

  html += buildTableHtml('threats', entries, 'Table 3-2 Threats')
  return html
}

function buildOspContent(entries: SpdEntry[]): string {
  let html = `
    <h3>3.3 Organisational Security Policies</h3>
    <p>The following table defines the organizational security policies which are a set of rules, practices, and procedures imposed by an organization to address its security needs.</p>
  `

  if (entries.length === 0) {
    html += '<p>There are no Organizational Security Policies identified for this TOE.</p>'
    return html
  }

  html += buildTableHtml('osp', entries, 'Table 3-3 Organisational Security Policies')
  return html
}

export function buildSpdSectionHtml(section: SpdSectionKey, entries: SpdEntry[], options: { includeRootHeading?: boolean } = {}): string {
  const includeRootHeading = options.includeRootHeading ?? true
  const builders: Record<SpdSectionKey, (items: SpdEntry[]) => string> = {
    assumptions: buildAssumptionsContent,
    threats: buildThreatsContent,
    osp: buildOspContent,
  }

  const sectionHtml = builders[section](entries)
  if (!sectionHtml) {
    return includeRootHeading ? buildIntroHtml() : ''
  }

  if (!includeRootHeading) {
    return sectionHtml
  }

  return buildIntroHtml() + sectionHtml
}

export function buildSecurityProblemDefinitionHtml(
  data: { assumptions: SpdEntry[]; threats: SpdEntry[]; osp: SpdEntry[] },
  options: { includeRootHeading?: boolean } = {}
): string {
  const includeRootHeading = options.includeRootHeading ?? true

  const sections: string[] = []
  if (includeRootHeading) {
    sections.push(buildIntroHtml())
  }

  sections.push(buildAssumptionsContent(data.assumptions))
  sections.push(buildThreatsContent(data.threats))
  sections.push(buildOspContent(data.osp))

  return sections.join('')
}
