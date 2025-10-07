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

export function ensureParagraph(html: string, fallback = '—'): string {
  if (!html || !html.trim()) {
    return `<p>${escapeHtml(fallback)}</p>`
  }
  return html
}

export function safeText(value: string, fallback = '—'): string {
  if (!value || !value.trim()) {
    return escapeHtml(fallback)
  }
  return escapeHtml(value)
}
