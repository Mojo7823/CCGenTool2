<template>
  <div class="cover-page">
    <div class="card cover-menubar">
      <div class="cover-menubar-left">
        <h1>Cover Image</h1>
        <span class="menubar-subtitle">Insert Cover Image Here</span>
      </div>
      <button
        class="btn primary"
        type="button"
        @click="openPreview"
        :disabled="!hasPreview || previewLoading"
      >
        Preview Cover
      </button>
    </div>

    <div class="card cover-body">
      <div class="save-status" :class="{ saving, error: !!saveError }">
        <span v-if="saveError">{{ saveError }}</span>
        <span v-else-if="saving">Saving…</span>
        <span v-else-if="lastSaved">Saved {{ lastSavedLabel }}</span>
        <span v-else>Changes are saved automatically.</span>
      </div>

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
          <div class="docx-preview-shell">
            <div v-if="previewLoading" class="modal-status overlay">Generating preview…</div>
            <div v-else-if="previewError" class="modal-error">{{ previewError }}</div>
            <div
              ref="docxPreviewContainer"
              class="docx-preview-container"
              :class="{ hidden: previewLoading || !!previewError }"
            ></div>
          </div>
        </section>
        <footer class="modal-footer">
          <button class="btn" type="button" @click="closePreview">Close</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { useSessionStore } from '../stores/session'
import { saveCoverSection } from '../services/stIntroduction'

const session = useSessionStore()

const fileInput = ref<HTMLInputElement | null>(null)
const dragActive = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const uploadedImagePath = ref<string | null>(null)
const showPreview = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const hasUploaded = ref(false)
const generatedDocxPath = ref<string | null>(null)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)

const form = reactive({
  title: '',
  version: '',
  revision: '',
  description: '',
  manufacturer: '',
  date: '',
})

const saving = ref(false)
const saveError = ref('')
const lastSaved = ref<Date | null>(null)
const ready = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

const userId = computed(() => session.userId)

const lastSavedLabel = computed(() => {
  if (!lastSaved.value) return ''
  return lastSaved.value.toLocaleTimeString()
})

const hasPreview = computed(() => !!uploadedImagePath.value || !!form.title || !!form.description)
const imageUrl = computed(() => {
  if (!uploadedImagePath.value) return ''
  return api.getUri({ url: uploadedImagePath.value })
})

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
  if (!userId.value) {
    session.ensureUserId()
  }

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
    await persistCover(true)
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

async function openPreview() {
  if (!hasPreview.value || previewLoading.value) return

  if (!userId.value) {
    session.ensureUserId()
  }

  if (!userId.value) {
    previewError.value = 'Unable to determine user session identifier.'
    showPreview.value = true
    return
  }

  // Remove any previously generated preview before creating a fresh one.
  cleanupDocx()

  const saved = await persistCover(true)
  if (!saved) {
    previewError.value = saveError.value || 'Unable to save cover information before generating preview.'
    showPreview.value = true
    previewLoading.value = false
    return
  }

  previewError.value = ''
  showPreview.value = true
  previewLoading.value = true

  try {
    const payload = {
      user_id: userId.value,
      title: form.title,
      version: form.version,
      revision: form.revision,
      description: form.description,
      manufacturer: form.manufacturer,
      date: form.date,
      image_path: uploadedImagePath.value,
    }

    const response = await api.post('/cover/preview', payload)
    const path: string | undefined = response.data?.path

    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }

    generatedDocxPath.value = path
    await nextTick()
    await renderDocxPreview(path)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || 'Unable to generate preview.'
    previewError.value = message
  } finally {
    previewLoading.value = false
  }
}

function closePreview() {
  showPreview.value = false
  if (!previewLoading.value) {
    previewError.value = ''
  }

  // Clean up the previously generated DOCX so repeat previews start fresh.
  cleanupDocx()
}

async function renderDocxPreview(path: string) {
  if (!docxPreviewContainer.value) return

  try {
    docxPreviewContainer.value.innerHTML = ''
    const response = await api.get(path, { responseType: 'arraybuffer' })
    const buffer = response.data as ArrayBuffer
    await renderAsync(buffer, docxPreviewContainer.value, undefined, {
      className: 'docx-rendered',
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      useBase64URL: true,
    })
  } catch (error: any) {
    const message = error?.message || 'Failed to render DOCX preview.'
    previewError.value = message
  }
}

function removeEventListeners() {
  if (typeof window === 'undefined') return
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
}

function cleanupUploads(keepalive = false) {
  if (!userId.value) return

  if (hasUploaded.value) {
    const url = api.getUri({ url: `/cover/upload/${userId.value}` })
    fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
    hasUploaded.value = false
    uploadedImagePath.value = null
  }

  cleanupDocx(keepalive)
}

function cleanupDocx(keepalive = false) {
  if (!userId.value || !generatedDocxPath.value) return
  const url = api.getUri({ url: `/cover/preview/${userId.value}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  generatedDocxPath.value = null
}

function handleBeforeUnload() {
  cleanupUploads(true)
}

function handlePageHide() {
  cleanupUploads(true)
}

onMounted(() => {
  session.ensureUserId()
  session.loadSession().then(() => {
    Object.assign(form, session.cover.fields)
    if (session.cover.image_path) {
      uploadedImagePath.value = session.cover.image_path
      hasUploaded.value = !!session.cover.image_path
    }
    ready.value = true
  })

  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handlePageHide)
  }
})

onBeforeUnmount(() => {
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
  cleanupDocx()
  removeEventListeners()
})

const schedulePersist = (immediate = false) => {
  if (!ready.value || !userId.value) return
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
  if (immediate) {
    void persistCover(true)
    return
  }
  saveTimer = setTimeout(() => {
    void persistCover()
  }, 400)
}

async function persistCover(immediate = false): Promise<boolean> {
  if (!ready.value || !userId.value) return false

  if (immediate && saveTimer) {
    clearTimeout(saveTimer)
    saveTimer = null
  }

  saving.value = true
  saveError.value = ''
  try {
    const payload = {
      user_id: userId.value,
      title: form.title,
      version: form.version,
      revision: form.revision,
      description: form.description,
      manufacturer: form.manufacturer,
      date: form.date,
      image_path: uploadedImagePath.value,
    }
    const result = await saveCoverSection(payload)
    session.updateCover(result)
    if (typeof result?.image_path === 'string') {
      uploadedImagePath.value = result.image_path || null
      hasUploaded.value = !!result.image_path
    }
    lastSaved.value = new Date()
    return true
  } catch (error: any) {
    console.error('Failed to save cover data', error)
    saveError.value = error?.response?.data?.detail || 'Unable to save cover data.'
    return false
  } finally {
    saving.value = false
  }
}

watch(form, () => {
  if (!ready.value) return
  schedulePersist()
}, { deep: true })
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
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cover-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
  gap: 24px;
}

.save-status {
  font-size: 14px;
  color: var(--muted);
}

.save-status.saving {
  color: var(--text);
}

.save-status.error {
  color: var(--danger);
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

.docx-modal {
  width: min(900px, 90vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.docx-modal-body {
  display: flex;
  flex-direction: column;
  background: var(--bg-soft);
  padding: 0;
  min-height: 60vh;
}

.modal-status,
.modal-error {
  padding: 24px;
  text-align: center;
  font-weight: 500;
}

.modal-status.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.75);
  color: #f9fafb;
  padding: 0;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.modal-error {
  color: var(--danger);
}

.docx-preview-shell {
  flex: 1;
  overflow: auto;
  padding: 24px;
  background: #d1d5db;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  position: relative;
}

.docx-preview-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.docx-preview-container.hidden {
  display: none;
}

.docx-preview-container .docx-wrapper {
  margin: 0 auto;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.docx-preview-container .docx-wrapper .docx {
  background: white;
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
