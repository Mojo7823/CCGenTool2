<template>
  <div class="cover-page">
    <div class="card cover-menubar">
      <div class="cover-menubar-left">
        <h1>Cover Image</h1>
        <span class="menubar-subtitle">Insert Cover Image Here</span>
      </div>
      <button class="btn primary" type="button" @click="openPreview" :disabled="!hasPreview">
        Preview Cover
      </button>
    </div>

    <div class="card cover-body">
      <div class="cover-grid">
        <section class="image-panel">
          <div class="drop-area"
               :class="{ active: dragActive }"
               @dragenter.prevent="dragActive = true"
               @dragover.prevent
               @dragleave.prevent="dragActive = false"
               @drop.prevent="handleDrop"
               @click="triggerFileDialog"
          >
            <input
              ref="fileInput"
              type="file"
              accept="image/jpeg,image/png,image/jpg,image/bmp"
              class="file-input"
              @change="handleFileSelection"
            />
            <div class="drop-content">
              <div class="drop-icon">📁</div>
              <p class="drop-text">Click or Drop Image Here (jpg, jpeg, png, bmp)</p>
              <p v-if="uploading" class="drop-status">Uploading...</p>
              <p v-if="uploadError" class="drop-error">{{ uploadError }}</p>
            </div>
          </div>
          <div class="image-preview" v-if="imageUrl">
            <img :src="imageUrl" alt="Uploaded cover preview" />
          </div>
        </section>

        <section class="info-panel">
          <div class="info-columns">
            <div>
              <h2>Cover Information</h2>
              <label>
                <span>Security Target Title</span>
                <input class="input" v-model="form.title" type="text" placeholder="Enter title" />
              </label>
              <label>
                <span>Security Target Version</span>
                <input class="input" v-model="form.version" type="text" placeholder="Enter version" />
              </label>
              <label>
                <span>Revision</span>
                <input class="input" v-model="form.revision" type="text" placeholder="Enter revision" />
              </label>
            </div>
            <div>
              <h2>Cover Description</h2>
              <label>
                <span>Additional Description</span>
                <textarea class="input textarea" v-model="form.description" placeholder="Provide additional description" />
              </label>
              <label>
                <span>Manufacturer/Laboratory Name</span>
                <input class="input" v-model="form.manufacturer" type="text" placeholder="Enter organisation" />
              </label>
              <label>
                <span>Date</span>
                <input class="input" v-model="form.date" type="date" />
              </label>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div v-if="showPreview" class="modal-overlay" @click.self="closePreview">
      <div class="modal-card docx-modal">
        <header class="modal-header">
          <h2>Cover Preview</h2>
          <button class="modal-close" type="button" @click="closePreview">&times;</button>
        </header>
        <section class="modal-body docx-modal-body">
          <div v-if="previewLoading" class="docx-status">Generating DOCX preview...</div>
          <div v-else-if="previewError" class="docx-status error">{{ previewError }}</div>
          <div v-else ref="docxPreviewContainer" class="docx-preview"></div>
        </section>
        <footer class="modal-footer">
          <button class="btn" type="button" @click="closePreview">Close</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import htmlToDocx from 'html-to-docx'
import { renderAsync } from 'docx-preview'
import api from '../services/api'

const fileInput = ref<HTMLInputElement | null>(null)
const dragActive = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const uploadedImagePath = ref<string | null>(null)
const showPreview = ref(false)
const hasUploaded = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)

const form = reactive({
  title: '',
  version: '',
  revision: '',
  description: '',
  manufacturer: '',
  date: ''
})

const storageKey = 'ccgen-user-id'
const userId = ref('')

const hasPreview = computed(() => !!uploadedImagePath.value || !!form.title || !!form.description)
const imageUrl = computed(() => {
  if (!uploadedImagePath.value) return ''
  return api.getUri({ url: uploadedImagePath.value })
})

const formattedDate = computed(() => {
  if (!form.date) return '—'
  try {
    return new Date(form.date).toLocaleDateString()
  } catch (error) {
    return form.date
  }
})

function ensureUserId() {
  if (typeof window === 'undefined') return
  const existing = window.localStorage.getItem(storageKey)
  if (existing) {
    userId.value = existing
    return
  }
  const generated = typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2)
  userId.value = generated
  window.localStorage.setItem(storageKey, generated)
}

function triggerFileDialog() {
  fileInput.value?.click()
}

function resetUploadState(message = '') {
  uploading.value = false
  uploadError.value = message
}

function validateImage(file: File) {
  const allowed = ['image/jpeg', 'image/png', 'image/bmp', 'image/x-ms-bmp']
  if (!allowed.includes(file.type)) {
    throw new Error('Only jpg, jpeg, png, or bmp files are allowed.')
  }
}

async function uploadFile(file: File) {
  if (!userId.value) return
  uploading.value = true
  uploadError.value = ''
  try {
    validateImage(file)
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/cover/upload', formData, {
      params: { user_id: userId.value },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadedImagePath.value = response.data.path
    hasUploaded.value = true
  } catch (error: any) {
    console.error('Upload failed', error)
    resetUploadState(error?.response?.data?.detail || error?.message || 'Failed to upload image.')
    return
  }
  resetUploadState()
}

function handleFileSelection(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (!files || !files.length) return
  uploadFile(files[0])
}

function handleDrop(event: DragEvent) {
  dragActive.value = false
  const files = event.dataTransfer?.files
  if (!files || !files.length) return
  uploadFile(files[0])
}

function closePreview() {
  showPreview.value = false
  previewError.value = ''
  previewLoading.value = false
  if (docxPreviewContainer.value) {
    docxPreviewContainer.value.innerHTML = ''
  }
}

async function fetchAsDataUrl(url: string): Promise<string | null> {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error('Unable to load cover image for preview.')
    }
    const blob = await response.blob()
    return await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(typeof reader.result === 'string' ? reader.result : null)
      reader.onerror = () => reject(new Error('Failed to read image data.'))
      reader.readAsDataURL(blob)
    })
  } catch (error) {
    console.error(error)
    return null
  }
}

async function buildCoverHtml() {
  const sections: string[] = []
  const title = form.title || 'Security Target Title'
  const description = form.description || 'Additional description will appear here.'
  const version = form.version || '—'
  const revision = form.revision || '—'
  const manufacturer = form.manufacturer || '—'
  const dateText = formattedDate.value

  let imageBlock = ''
  if (imageUrl.value) {
    const dataUrl = await fetchAsDataUrl(imageUrl.value)
    if (dataUrl) {
      imageBlock = `
        <div class="cover-image">
          <img src="${dataUrl}" alt="Cover image" />
        </div>
      `
    }
  }

  sections.push(`
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #1f2937;
            padding: 40px;
          }
          .cover-container {
            display: flex;
            flex-direction: column;
            gap: 24px;
            align-items: center;
            text-align: center;
          }
          .cover-image img {
            max-width: 300px;
            height: auto;
            border-radius: 12px;
          }
          .cover-title {
            font-size: 28px;
            font-weight: 700;
            margin: 0;
          }
          .cover-description {
            font-size: 16px;
            margin: 12px 0 24px;
            max-width: 520px;
          }
          .cover-details {
            width: 100%;
            max-width: 520px;
            border-top: 1px solid #d1d5db;
          }
          .cover-details dl {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin: 0;
            padding: 24px 0;
          }
          .cover-details dt {
            font-weight: 600;
            text-align: left;
          }
          .cover-details dd {
            margin: 0;
            text-align: left;
          }
        </style>
      </head>
      <body>
        <div class="cover-container">
          ${imageBlock}
          <h1 class="cover-title">${title}</h1>
          <p class="cover-description">${description}</p>
          <div class="cover-details">
            <dl>
              <div>
                <dt>Version</dt>
                <dd>${version}</dd>
              </div>
              <div>
                <dt>Revision</dt>
                <dd>${revision}</dd>
              </div>
              <div>
                <dt>Manufacturer / Laboratory</dt>
                <dd>${manufacturer}</dd>
              </div>
              <div>
                <dt>Date</dt>
                <dd>${dateText}</dd>
              </div>
            </dl>
          </div>
        </div>
      </body>
    </html>
  `)

  return sections.join('')
}

async function uploadDocx(blob: Blob) {
  if (!userId.value) return null
  const formData = new FormData()
  formData.append('file', blob, 'cover-preview.docx')
  const response = await api.post('/cover/docx', formData, {
    params: { user_id: userId.value },
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  generatedDocxPath.value = response.data.path
  return api.getUri({ url: response.data.path })
}

async function renderDocxFromUrl(url: string) {
  const response = await fetch(url, { cache: 'no-store' })
  if (!response.ok) {
    throw new Error('Unable to load generated DOCX preview.')
  }
  const buffer = await response.arrayBuffer()
  if (docxPreviewContainer.value) {
    docxPreviewContainer.value.innerHTML = ''
    await renderAsync(buffer, docxPreviewContainer.value, undefined, {
      inWrapper: true,
      ignoreWidth: true,
      ignoreHeight: true,
      className: 'docx-rendered'
    })
  }
}

async function openPreview() {
  if (!hasPreview.value) return
  previewError.value = ''
  previewLoading.value = true
  showPreview.value = true

  await nextTick()

  try {
    const html = await buildCoverHtml()
    const buffer = await htmlToDocx(html)
    const blob = new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    const docxUrl = await uploadDocx(blob)
    if (!docxUrl) {
      throw new Error('Unable to store generated DOCX preview.')
    }
    await renderDocxFromUrl(docxUrl)
  } catch (error: any) {
    console.error('DOCX preview failed', error)
    previewError.value = error?.message || 'Failed to build DOCX preview.'
  } finally {
    previewLoading.value = false
  }
}

function removeEventListeners() {
  if (typeof window === 'undefined') return
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
}

function cleanupUploads(keepalive = false) {
  if (!userId.value) return
  if (!hasUploaded.value && !generatedDocxPath.value) return
  const url = api.getUri({ url: `/cover/upload/${userId.value}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  hasUploaded.value = false
  uploadedImagePath.value = null
  generatedDocxPath.value = null
}

function handleBeforeUnload() {
  cleanupUploads(true)
}

function handlePageHide() {
  cleanupUploads(true)
}

onMounted(() => {
  ensureUserId()
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handlePageHide)
  }
})

onBeforeUnmount(() => {
  cleanupUploads()
  removeEventListeners()
})
</script>

<style scoped>
.cover-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.cover-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.cover-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.cover-body {
  padding: 24px;
}

.cover-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
  gap: 24px;
}

@media (max-width: 1024px) {
  .cover-grid {
    grid-template-columns: 1fr;
  }
}

.image-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.drop-area {
  border: 2px dashed #374151;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  background: rgba(15, 23, 42, 0.45);
  position: relative;
  transition: border-color 0.2s, background 0.2s;
}

.drop-area.active {
  border-color: var(--primary);
  background: rgba(37, 99, 235, 0.15);
}

.file-input {
  display: none;
}

.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.drop-icon {
  font-size: 2rem;
}

.drop-text {
  margin: 0;
  font-weight: 500;
}

.drop-status {
  color: var(--muted);
}

.drop-error {
  color: var(--danger);
  margin: 0;
}

.image-preview {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #1f2937;
  background: rgba(15, 23, 42, 0.45);
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.info-panel {
  display: flex;
  flex-direction: column;
}

.info-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.info-panel h2 {
  margin: 0 0 12px 0;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 500;
}

.textarea {
  min-height: 120px;
  resize: vertical;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 1000;
}

.modal-card {
  background: var(--panel);
  border-radius: 16px;
  border: 1px solid #1f2937;
  max-width: 720px;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #1f2937;
}

.modal-header h2 {
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.docx-modal {
  max-width: 1000px;
  width: min(1000px, 95vw);
}

.docx-modal-body {
  min-height: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.35);
  border: 1px dashed rgba(148, 163, 184, 0.35);
}

.docx-preview {
  width: 100%;
  height: 100%;
  overflow: auto;
  padding: 12px;
  background: rgba(15, 23, 42, 0.55);
  border-radius: 8px;
}

.docx-status {
  width: 100%;
  text-align: center;
  font-weight: 600;
  color: var(--text);
}

.docx-status.error {
  color: var(--danger);
}

.docx-rendered {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.35);
}

.modal-image img {
  width: 100%;
  border-radius: 12px;
}

.modal-placeholder {
  padding: 48px 24px;
  text-align: center;
  border: 1px dashed #374151;
  border-radius: 12px;
}

.modal-details h3 {
  margin: 0 0 8px 0;
}

.modal-description {
  margin: 0 0 16px 0;
  color: var(--muted);
}

dl {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px 24px;
  margin: 0;
}

dl div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

dt {
  font-weight: 600;
  color: var(--muted);
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #1f2937;
  display: flex;
  justify-content: flex-end;
}
</style>
