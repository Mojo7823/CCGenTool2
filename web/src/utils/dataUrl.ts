export function dataUrlToFile(dataUrl: string, filenamePrefix = 'file'): File | null {
  if (typeof window === 'undefined') {
    return null
  }

  if (!dataUrl || !dataUrl.startsWith('data:')) {
    return null
  }

  const [metadata, base64Data] = dataUrl.split(',', 2)
  if (!metadata || !base64Data) {
    return null
  }

  const mimeMatch = metadata.match(/data:(.*?);base64/)
  const mime = mimeMatch?.[1] || 'application/octet-stream'

  try {
    const binaryString = window.atob(base64Data)
    const length = binaryString.length
    const bytes = new Uint8Array(length)

    for (let i = 0; i < length; i += 1) {
      bytes[i] = binaryString.charCodeAt(i)
    }

    const extension = mime.split('/')[1] || 'bin'
    const filename = `${filenamePrefix}.${extension}`

    return new File([bytes], filename, { type: mime })
  } catch (error) {
    console.error('Failed to convert data URL to file', error)
    return null
  }
}
