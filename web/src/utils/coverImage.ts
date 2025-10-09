import api from '../services/api'

function dataUrlToBlob(dataUrl: string): { blob: Blob; mime: string } {
  const parts = dataUrl.split(',')
  if (parts.length !== 2) {
    throw new Error('Invalid data URL format.')
  }

  const mimeMatch = parts[0].match(/data:(.*?);base64/)
  if (!mimeMatch) {
    throw new Error('Unable to determine MIME type from data URL.')
  }

  const mime = mimeMatch[1]
  const binary = atob(parts[1])
  const length = binary.length
  const buffer = new Uint8Array(length)

  for (let i = 0; i < length; i += 1) {
    buffer[i] = binary.charCodeAt(i)
  }

  return {
    blob: new Blob([buffer], { type: mime }),
    mime,
  }
}

function buildFileName(mime: string): string {
  const [, subtype = 'png'] = mime.split('/')
  const safeSubtype = subtype.replace(/[^a-z0-9]/gi, '-') || 'png'
  return `cover-${Date.now()}.${safeSubtype}`
}

export async function uploadCoverImageFromDataUrl(dataUrl: string, userToken: string): Promise<string> {
  const { blob, mime } = dataUrlToBlob(dataUrl)
  const formData = new FormData()
  formData.append('file', blob, buildFileName(mime))

  const response = await api.post('/cover/upload', formData, {
    params: { user_id: userToken },
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  const path: string | undefined = response.data?.path
  if (!path) {
    throw new Error('Upload did not return a document path.')
  }

  return path
}

export function coverPathMatchesUser(path: string | null | undefined, userToken: string): boolean {
  if (!path) {
    return false
  }
  return path.includes(`/${userToken}/`)
}
