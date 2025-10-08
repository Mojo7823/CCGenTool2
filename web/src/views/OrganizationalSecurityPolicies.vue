<template>
  <div class="osp-container">
    <h2>Organisational Security Policies</h2>
    <p>Write the set of security rules, procedures, or guidelines imposed by an organization on the operational environment of a Target of Evaluation (TOE), which is the product or system being evaluated.</p>
    
    <div class="osp-table-section">
      <div class="osp-table-header">
        <h3>Organisational Security Policies (Optional)</h3>
        <div class="table-actions">
          <button class="btn primary" @click="openAddModal">Add</button>
          <button class="btn info" @click="editSelected" :disabled="!selectedId">Edit</button>
          <button class="btn danger" @click="removeItem" :disabled="!selectedId">Remove</button>
          <button class="btn" @click="openPreviewModal">Preview</button>
        </div>
      </div>
      
      <div class="osp-table-container">
        <table class="osp-table">
          <thead>
            <tr>
              <th>OSP</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="item in ospList" 
              :key="item.id"
              :class="{ selected: selectedId === item.id }"
              @click="selectItem(item.id)"
            >
              <td>{{ item.osp }}</td>
              <td><div v-html="item.description" class="description-preview"></div></td>
            </tr>
            <tr v-if="ospList.length === 0">
              <td colspan="2" class="no-data">No OSP added yet. This section is optional.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ isEditing ? 'Edit OSP' : 'Insert OSP' }}</h3>
        
        <div class="form-group">
          <label for="ospInput">OSP</label>
          <input
            id="ospInput"
            v-model="currentOsp"
            type="text"
            class="input"
            placeholder="Insert OSP"
          />
        </div>

        <div class="form-group">
          <label for="descriptionInput">Description</label>
          <RichTextEditor v-model="currentDescription" placeholder="Enter description" min-height="240px" />
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeItem" :disabled="!canFinalize">
            {{ isEditing ? 'Finalize and Update OSP' : 'Finalize and Add OSP' }}
          </button>
          <button class="btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content docx-modal" @click.stop>
        <div class="modal-header">
          <h3>Organisational Security Policies Preview</h3>
          <button class="modal-close" type="button" @click="closePreviewModal">&times;</button>
        </div>
        <div class="docx-modal-body">
          <div class="docx-preview-shell">
            <div v-if="previewLoading" class="modal-status overlay">Generating preview…</div>
            <div v-else-if="previewError" class="modal-error">{{ previewError }}</div>
            <div
              ref="docxPreviewContainer"
              class="docx-preview-container"
              :class="{ hidden: previewLoading || !!previewError }"
            ></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" type="button" @click="closePreviewModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, onBeforeUnmount } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { sessionService, type OspEntry } from '../services/sessionService'
import RichTextEditor from '../components/RichTextEditor.vue'

const ospList = ref<OspEntry[]>([])
const selectedId = ref<number | null>(null)
const nextId = ref(1)
const userToken = ref('')

const showAddModal = ref(false)
const showPreviewModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const currentOsp = ref('')
const currentDescription = ref('')

const previewLoading = ref(false)
const previewError = ref('')
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)

const canFinalize = computed(() => {
  return currentOsp.value.trim() !== '' && currentDescription.value.trim() !== ''
})

const loadSessionData = () => {
  const data = sessionService.loadOspData()
  if (data) {
    ospList.value = data.ospList
    selectedId.value = data.selectedOspId
    nextId.value = data.nextOspId
  }
}

const saveSessionData = () => {
  sessionService.saveOspData(ospList.value, selectedId.value, nextId.value)
}

const selectItem = (id: number) => {
  selectedId.value = id
  saveSessionData()
}

const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  currentOsp.value = ''
  currentDescription.value = ''
  showAddModal.value = true
}

const editSelected = () => {
  if (!selectedId.value) return
  
  const item = ospList.value.find(a => a.id === selectedId.value)
  if (!item) return
  
  isEditing.value = true
  editingId.value = item.id
  currentOsp.value = item.osp
  currentDescription.value = item.description
  showAddModal.value = true
}

const closeModal = () => {
  showAddModal.value = false
  isEditing.value = false
  editingId.value = null
  currentOsp.value = ''
  currentDescription.value = ''
}

const finalizeItem = () => {
  if (!canFinalize.value) return
  
  if (isEditing.value && editingId.value !== null) {
    const index = ospList.value.findIndex(a => a.id === editingId.value)
    if (index !== -1) {
      ospList.value[index] = {
        id: editingId.value,
        osp: currentOsp.value.trim(),
        description: currentDescription.value
      }
    }
  } else {
    ospList.value.push({
      id: nextId.value,
      osp: currentOsp.value.trim(),
      description: currentDescription.value
    })
    nextId.value++
  }
  
  saveSessionData()
  closeModal()
}

const removeItem = () => {
  if (!selectedId.value) return
  
  if (confirm('Are you sure you want to remove this OSP?')) {
    ospList.value = ospList.value.filter(a => a.id !== selectedId.value)
    selectedId.value = null
    saveSessionData()
  }
}

const buildPreviewHtml = (): string => {
  let html = '<h4>3.3 Organisational Security Policies</h4>'
  
  if (ospList.value.length === 0) {
    html += '<p>There are no Organizational Security Policies identified for this TOE.</p>'
    return html
  }
  
  html += '<p>The following table defines the organizational security policies which are a set of rules, practices, and procedures imposed by an organization to address its security needs.</p>'
  
  html += '<table style="width: 100%; border-collapse: collapse; border: 1px solid black;">'
  html += '<thead><tr>'
  html += '<th style="border: 1px solid black; padding: 8px; background-color: #f2f2f2;">OSP</th>'
  html += '<th style="border: 1px solid black; padding: 8px; background-color: #f2f2f2;">Description</th>'
  html += '</tr></thead><tbody>'
  
  for (const item of ospList.value) {
    html += '<tr>'
    html += `<td style="border: 1px solid black; padding: 8px;">${escapeHtml(item.osp)}</td>`
    html += `<td style="border: 1px solid black; padding: 8px;">${item.description}</td>`
    html += '</tr>'
  }
  
  html += '</tbody></table>'
  return html
}

const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const cleanupDocx = (isPageUnload: boolean = false) => {
  if (generatedDocxPath.value && userToken.value) {
    const segments = generatedDocxPath.value.split('/')
    const filename = segments[segments.length - 1]
    if (filename) {
      const deleteUrl = `/spd/osp/preview/${userToken.value}/${filename}`
      if (isPageUnload) {
        navigator.sendBeacon(api.getUri({ url: deleteUrl }))
      } else {
        api.delete(deleteUrl).catch(() => {})
      }
    }
  }
  
  if (docxPreviewContainer.value) {
    docxPreviewContainer.value.innerHTML = ''
  }
  
  generatedDocxPath.value = null
  hasGeneratedDocx.value = false
}

const renderDocxPreview = async (path: string) => {
  if (!docxPreviewContainer.value) return
  
  try {
    const segments = path.split('/')
    const filename = segments[segments.length - 1]
    if (!filename) {
      throw new Error('Invalid document path')
    }
    
    const downloadUrl = api.getUri({ url: `/spd/osp/preview/${userToken.value}/${filename}` })
    const response = await fetch(downloadUrl)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch document: ${response.statusText}`)
    }
    
    const blob = await response.blob()
    await renderAsync(blob, docxPreviewContainer.value)
  } catch (error: any) {
    const message = error?.message || 'Unable to render preview'
    previewError.value = message
  }
}

const openPreviewModal = async () => {
  previewError.value = ''
  previewLoading.value = true
  showPreviewModal.value = true
  await nextTick()
  cleanupDocx()
  
  try {
    const payload = {
      user_id: userToken.value,
      html_content: buildPreviewHtml()
    }
    
    const response = await api.post('/spd/osp/preview', payload)
    const path: string | undefined = response.data?.path
    
    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }
    
    generatedDocxPath.value = path
    hasGeneratedDocx.value = true
    await nextTick()
    await renderDocxPreview(path)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || 'Unable to generate preview.'
    previewError.value = message
  } finally {
    previewLoading.value = false
  }
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  cleanupDocx()
  if (!previewLoading.value) {
    previewError.value = ''
  }
}

const handleBeforeUnload = () => cleanupDocx(true)
const handlePageHide = () => cleanupDocx(true)

onMounted(() => {
  userToken.value = sessionService.getUserToken()
  loadSessionData()
  
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handlePageHide)
  }
})

onBeforeUnmount(() => {
  cleanupDocx()
  
  if (typeof window !== 'undefined') {
    window.removeEventListener('beforeunload', handleBeforeUnload)
    window.removeEventListener('pagehide', handlePageHide)
  }
})
</script>

<style scoped>
.osp-container {
  padding: 20px;
}

.osp-table-section {
  margin-top: 24px;
}

.osp-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.osp-table-container {
  overflow-x: auto;
}

.osp-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border: 1px solid #ddd;
}

.osp-table th,
.osp-table td {
  padding: 12px;
  text-align: left;
  border: 1px solid #ddd;
}

.osp-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.osp-table tbody tr {
  cursor: pointer;
}

.osp-table tbody tr:hover {
  background-color: #f9f9f9;
}

.osp-table tbody tr.selected {
  background-color: #e3f2fd;
}

.no-data {
  text-align: center;
  color: #999;
  font-style: italic;
}

.description-preview {
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background-color: #1976d2;
  color: white;
  border-color: #1976d2;
}

.btn.primary:hover:not(:disabled) {
  background-color: #1565c0;
}

.btn.info {
  background-color: #0288d1;
  color: white;
  border-color: #0288d1;
}

.btn.danger {
  background-color: #d32f2f;
  color: white;
  border-color: #d32f2f;
}

.docx-modal {
  max-width: 1200px;
  width: 95%;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ddd;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.docx-modal-body {
  flex: 1;
  overflow: hidden;
}

.docx-preview-shell {
  height: 100%;
  position: relative;
}

.docx-preview-container {
  height: 100%;
  overflow-y: auto;
  border: 1px solid #ddd;
  background-color: #f5f5f5;
}

.docx-preview-container.hidden {
  display: none;
}

.modal-status {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  color: #666;
}

.modal-error {
  padding: 20px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  margin: 20px;
}

.modal-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #ddd;
  display: flex;
  justify-content: flex-end;
}
</style>
