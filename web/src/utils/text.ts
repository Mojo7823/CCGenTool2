export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export function formatMultilineText(value: string): string {
  if (!value) return ''
  return escapeHtml(value).replace(/\r?\n/g, '<br />')
}

export function fallbackParagraph(content: string): string {
  return content && content.trim() ? content : '<p>&mdash;</p>'
}
