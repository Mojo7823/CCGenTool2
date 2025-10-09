import api from '../services/api'

interface EnsureCoverImageParams {
  userToken: string
  imagePath?: string | null
  imageData?: string | null
  fileName?: string
}

export interface EnsureCoverImageResult {
  path: string | null
  uploaded: boolean
}

function dataUrlToFile(dataUrl: string, filename: string): File {
  const match = dataUrl.match(/^data:(.*?);base64,(.*)$/)
  if (!match) {
    throw new Error('Invalid data URL provided')
  }

  const mimeType = match[1] || 'application/octet-stream'
  const binary = atob(match[2])
  const length = binary.length
  const buffer = new Uint8Array(length)

  for (let i = 0; i < length; i += 1) {
    buffer[i] = binary.charCodeAt(i)
  }

  const extension = mimeType.split('/')[1] || 'bin'
  return new File([buffer], `${filename}.${extension}`, { type: mimeType })
}

async function pathAccessible(path: string): Promise<boolean> {
  try {
    await api.get(path, { responseType: 'blob' })
    return true
  } catch (error: any) {
    if (error?.response?.status === 404) {
      return false
    }
    console.warn('Unexpected error while verifying cover image path', error)
    return false
  }
}

export async function ensureCoverImagePath({
  userToken,
  imagePath,
  imageData,
  fileName = 'cover-image',
}: EnsureCoverImageParams): Promise<EnsureCoverImageResult> {
  if (!userToken) {
    return { path: imagePath ?? null, uploaded: false }
  }

  const expectedPrefix = `/cover/uploads/${userToken}/`
  let resolvedPath = imagePath ?? null

  if (resolvedPath && resolvedPath.startsWith(expectedPrefix)) {
    if (await pathAccessible(resolvedPath)) {
      return { path: resolvedPath, uploaded: false }
    }
  }

  if (!imageData) {
    return { path: null, uploaded: false }
  }

  const file = dataUrlToFile(imageData, fileName)
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/cover/upload', formData, {
    params: { user_id: userToken },
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  resolvedPath = response.data?.path ?? null
  return {
    path: resolvedPath,
    uploaded: Boolean(resolvedPath),
  }
}
