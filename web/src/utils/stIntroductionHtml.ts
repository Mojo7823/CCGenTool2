import { escapeHtml, formatMultilineText, fallbackParagraph } from './text'

export interface CoverFormLike {
  title: string
  version: string
  revision: string
  description: string
  manufacturer: string
  date: string
}

export function buildCoverHtml(form: CoverFormLike, imagePath: string | null): string {
  const title = escapeHtml(form.title || '')
  const version = escapeHtml(form.version || '')
  const revision = escapeHtml(form.revision || '')
  const manufacturer = escapeHtml(form.manufacturer || '')
  const date = escapeHtml(form.date || '')
  const description = escapeHtml(form.description || '')

  return `
    <section>
      <h2>Security Target Cover</h2>
      <table>
        <tbody>
          <tr><th scope="row">Security Target Title</th><td>${title || '&mdash;'}</td></tr>
          <tr><th scope="row">Security Target Version</th><td>${version || '&mdash;'}</td></tr>
          <tr><th scope="row">Revision</th><td>${revision || '&mdash;'}</td></tr>
          <tr><th scope="row">Manufacturer/Laboratory</th><td>${manufacturer || '&mdash;'}</td></tr>
          <tr><th scope="row">Date</th><td>${date || '&mdash;'}</td></tr>
          <tr><th scope="row">Cover Image</th><td>${imagePath ? 'Uploaded' : 'Not Provided'}</td></tr>
        </tbody>
      </table>
      <p>${description || '&nbsp;'}</p>
    </section>
  `.trim()
}

export interface StReferenceLike {
  stTitle: string
  stVersion: string
  stDate: string
  author: string
}

export function buildStReferenceHtml(data: StReferenceLike): string {
  const title = escapeHtml(data.stTitle || '')
  const version = escapeHtml(data.stVersion || '')
  const date = escapeHtml(data.stDate || '')
  const author = formatMultilineText(data.author || '') || '&mdash;'

  return `
    <section>
      <h2>1. Security Target Introduction</h2>
      <p>This section presents the following information required for a Common Criteria (CC) evaluation:</p>
      <ul>
        <li>Identifies the Security Target (ST) and the Target of Evaluation (TOE)</li>
        <li>Specifies the security target conventions</li>
        <li>Describes the organization of the security target</li>
      </ul>
      <h3>1.1 ST Reference</h3>
      <table>
        <tbody>
          <tr><th scope="row">ST Title</th><td>${title || '&mdash;'}</td></tr>
          <tr><th scope="row">ST Version</th><td>${version || '&mdash;'}</td></tr>
          <tr><th scope="row">ST Date</th><td>${date || '&mdash;'}</td></tr>
          <tr><th scope="row">Author</th><td>${author}</td></tr>
        </tbody>
      </table>
      <p><em>Table 1 Security Target reference</em></p>
    </section>
  `.trim()
}

export interface ToeReferenceLike {
  toeName: string
  toeVersion: string
  toeIdentification: string
  toeType: string
}

export function buildToeReferenceHtml(data: ToeReferenceLike): string {
  return `
    <section>
      <h3>1.2 TOE Reference</h3>
      <table>
        <tbody>
          <tr><th scope="row">TOE Name</th><td>${fallbackParagraph(data.toeName || '')}</td></tr>
          <tr><th scope="row">TOE Version</th><td>${fallbackParagraph(data.toeVersion || '')}</td></tr>
          <tr><th scope="row">TOE Identification</th><td>${fallbackParagraph(data.toeIdentification || '')}</td></tr>
          <tr><th scope="row">TOE Type</th><td>${fallbackParagraph(data.toeType || '')}</td></tr>
        </tbody>
      </table>
      <p><em>Table 2 TOE reference</em></p>
    </section>
  `.trim()
}

export interface ToeOverviewLike {
  overview: string
  toeType: string
  usage: string
  securityFeatures: string
  nonToe: string
}

export function buildToeOverviewHtml(data: ToeOverviewLike): string {
  return `
    <section>
      <h3>1.3 TOE Overview</h3>
      ${fallbackParagraph(data.overview || '')}
      <h4>1.3.1 TOE Type</h4>
      ${fallbackParagraph(data.toeType || '')}
      <h4>1.3.2 TOE Usage</h4>
      ${fallbackParagraph(data.usage || '')}
      <h4>1.3.3 TOE Major Security Features</h4>
      ${fallbackParagraph(data.securityFeatures || '')}
      <h4>1.3.4 Non-TOE Hardware/Software/Firmware</h4>
      ${fallbackParagraph(data.nonToe || '')}
    </section>
  `.trim()
}

export interface ToeDescriptionLike {
  physicalScope: string
  logicalScope: string
}

export function buildToeDescriptionHtml(data: ToeDescriptionLike): string {
  return `
    <section>
      <h3>1.4 TOE Description</h3>
      <h4>1.4.1 TOE Physical Scope</h4>
      ${fallbackParagraph(data.physicalScope || '')}
      <h4>1.4.2 TOE Logical Scope</h4>
      ${fallbackParagraph(data.logicalScope || '')}
    </section>
  `.trim()
}
