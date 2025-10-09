import api from '../services/api'
import { sessionService, type CoverSessionData } from '../services/sessionService'
import { dataUrlToFile } from './dataUrl'

export interface CoverImageContext {
  form: CoverSessionData['form']
  uploadedImagePath: string | null
  uploadedImageData: string | null
}

export interface EnsureCoverImageOptions {
  force?: boolean
  filenamePrefix?: string
}

export async function ensureCoverImageUploaded(
  context: CoverImageContext,
  options: EnsureCoverImageOptions = {}
): Promise<string | null> {
  const { force = false, filenamePrefix = 'cover-image' } = options
  const userToken = sessionService.getUserToken()

  if (!userToken) {
    return context.uploadedImagePath
  }

  if (!context.uploadedImageData) {
    return context.uploadedImagePath
  }

  if (!force && context.uploadedImagePath) {
    return context.uploadedImagePath
  }

  const file = dataUrlToFile(context.uploadedImageData, filenamePrefix)
  if (!file) {
    return context.uploadedImagePath
  }

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/cover/upload', formData, {
      params: { user_id: userToken },
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const newPath: string | null = response.data?.path ?? null
    sessionService.saveCoverData(context.form, newPath, context.uploadedImageData)

    return newPath
  } catch (error) {
    console.error('Failed to restore cover image upload', error)
    return context.uploadedImagePath
  }
}
