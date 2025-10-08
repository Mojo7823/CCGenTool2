<template>
  <div class="assumptions-container">
    <h2>Assumptions</h2>
    <p>Write the assumptions of the TOE. These assumptions include both practical realities in the development of the TOE security requirements and the essential environmental conditions on the use of the TOE.</p>
    
    <!-- Assumptions Table Section -->
    <div class="assumptions-table-section">
      <div class="assumptions-table-header">
        <div class="table-actions">
          <button class="btn primary" @click="openAddModal">Add</button>
          <button class="btn info" @click="editSelected" :disabled="!selectedId">Edit</button>
          <button class="btn danger" @click="removeItem" :disabled="!selectedId">Remove</button>
          <button
            class="btn"
            @click="openPreviewModal"
            :disabled="assumptionsList.length === 0"
            title="Preview Assumptions"
          >
            Preview
          </button>
        </div>
      </div>
      
      <div class="assumptions-table-container">
        <table class="assumptions-table">
          <thead>
            <tr>
              <th>Assumptions</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="item in assumptionsList" 
              :key="item.id"
              :class="{ selected: selectedId === item.id }"
              @click="selectItem(item.id)"
            >
              <td>{{ item.assumption }}</td>
              <td><div v-html="item.description"></div></td>
            </tr>
            <tr v-if="assumptionsList.length === 0">
              <td colspan="2" class="no-data">No assumptions added yet. Click "Add" to get started.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ isEditing ? 'Edit Assumptions' : 'Insert Assumptions' }}</h3>
        
        <div class="form-group">
          <label for="assumptionInput">Assumptions:</label>
          <input
            id="assumptionInput"
            v-model="currentAssumption"
            type="text"
            class="input"
            placeholder="Insert Assumptions"
          />
        </div>

        <div class="form-group">
          <label for="descriptionInput">Description:</label>
          <RichTextEditor
            v-model="currentDescription"
            placeholder="Enter description"
            min-height="240px"
          />
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeAssumption" :disabled="!canFinalize">
            {{ isEditing ? 'Update Assumptions' : 'Finalize and Add Assumptions' }}
          </button>
          <button class="btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content docx-modal" @click.stop>
        <div class="modal-header">
          <h3>Assumptions Preview</h3>
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
import { sessionService } from '../services/sessionService'
import RichTextEditor from '../components/RichTextEditor.vue'

interface AssumptionEntry {
  id: number
  assumption: string
  description: string
}

const assumptionsList = ref<AssumptionEntry[]>([])
const selectedId = ref<number | null>(null)
const nextId = ref(1)
const showAddModal = ref(false)
const showPreviewModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const currentAssumption = ref('')
const currentDescription = ref('')

const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const userToken = ref('')

const canFinalize = computed(() => {
  return currentAssumption.value.trim() !== '' && currentDescription.value.trim() !== ''
})

onMounted(() => {
  loadSessionData()
  userToken.value = sessionService.getUserToken()
  addPreviewListeners()
})

onBeforeUnmount(() => {
  removePreviewListeners()
  cleanupDocx()
})

const loadSessionData = () => {
  const data = sessionService.loadSPDAssumptionsData()
  if (data) {
    assumptionsList.value = data.assumptionsList
    selectedId.value = data.selectedAssumptionId
    nextId.value = data.nextAssumptionId
  }
}

const saveSessionData = () => {
  sessionService.saveSPDAssumptionsData(assumptionsList.value, selectedId.value, nextId.value)
}

const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  currentAssumption.value = ''
  currentDescription.value = ''
  showAddModal.value = true
}

const editSelected = () => {
  if (!selectedId.value) return
  
  const item = assumptionsList.value.find(a => a.id === selectedId.value)
  if (!item) return
  
  isEditing.value = true
  editingId.value = item.id
  currentAssumption.value = item.assumption
  currentDescription.value = item.description
  showAddModal.value = true
}

const closeModal = () => {
  showAddModal.value = false
  isEditing.value = false
  editingId.value = null
  currentAssumption.value = ''
  currentDescription.value = ''
}

const finalizeAssumption = () => {
  if (!canFinalize.value) return

  if (isEditing.value && editingId.value) {
    // Update existing
    const index = assumptionsList.value.findIndex(a => a.id === editingId.value)
    if (index !== -1) {
      assumptionsList.value[index] = {
        id: editingId.value,
        assumption: currentAssumption.value.trim(),
        description: currentDescription.value
      }
    }
  } else {
    // Add new
    assumptionsList.value.push({
      id: nextId.value,
      assumption: currentAssumption.value.trim(),
      description: currentDescription.value
    })
    selectedId.value = nextId.value
    nextId.value++
  }

  saveSessionData()
  closeModal()
}

const selectItem = (id: number) => {
  selectedId.value = id
  saveSessionData()
}

const removeItem = () => {
  if (!selectedId.value) return

  const index = assumptionsList.value.findIndex(a => a.id === selectedId.value)
  if (index > -1) {
    assumptionsList.value.splice(index, 1)
    selectedId.value = null
    saveSessionData()
  }
}

const buildPreviewHtml = (): string => {
  if (assumptionsList.value.length === 0) {
    return '<p>No assumptions have been defined.</p>'
  }

  let html = '<h4>3. Security Problem Definition</h4>'
  html += '<p>This chapter identifies the following:</p>'
  html += '<ul>'
  html += '<li>Significant assumptions about the TOE\'s operational environment.</li>'
  html += '<li>Threats that must be countered by the TOE or its environment</li>'
  html += '</ul>'
  html += '<p>This document identifies assumptions as A.assumption with "assumption" specifying a unique name.</p>'
  html += '<p>Threats are identified as T.threat with "threat" specifying a unique name</p>'
  html += '<h4>3.1 Assumptions</h4>'
  html += '<p>The specific conditions listed in the following subsections are assumed to exist in the TOE\'s environment. '
  html += 'These assumptions include both practical realities in the development of the TOE security requirements '
  html += 'and the essential environmental conditions on the use of the TOE.</p>'
  
  html += '<table border="1" style="width: 100%; border-collapse: collapse;">'
  html += '<thead><tr>'
  html += '<th style="padding: 8px; background-color: #f0f0f0;">Assumptions</th>'
  html += '<th style="padding: 8px; background-color: #f0f0f0;">Description</th>'
  html += '</tr></thead>'
  html += '<tbody>'
  
  assumptionsList.value.forEach(item => {
    html += '<tr>'
    html += `<td style="padding: 8px; border: 1px solid #ccc;">${escapeHtml(item.assumption)}</td>`
    html += `<td style="padding: 8px; border: 1px solid #ccc;">${item.description}</td>`
    html += '</tr>'
  })
  
  html += '</tbody></table>'
  
  return html
}

const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const openPreviewModal = async () => {
  if (assumptionsList.value.length === 0) {
    return
  }

  previewError.value = ''
  previewLoading.value = true
  showPreviewModal.value = true
  await nextTick()
  cleanupDocx()

  try {
    const htmlContent = buildPreviewHtml()
    const payload = {
      user_id: userToken.value,
      html_content: htmlContent,
    }

    const response = await api.post('/spd/assumptions/preview', payload)
    const path: string | undefined = response.data?.path

    if (!path) {
      throw new Error('No preview path returned from server')
    }

    generatedDocxPath.value = path
    await renderDocxPreview(path)
  } catch (error: any) {
    console.error('Error generating preview:', error)
    previewError.value = error.response?.data?.detail || error.message || 'Failed to generate preview'
  } finally {
    previewLoading.value = false
  }
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  cleanupDocx()
}

const renderDocxPreview = async (path: string) => {
  if (!docxPreviewContainer.value) return

  try {
    const segments = path.split('/')
    const filename = segments[segments.length - 1]
    if (!filename) {
      throw new Error('Invalid preview path')
    }

    const downloadUrl = api.getUri({ url: `/spd/assumptions/download/${userToken.value}/${filename}` })
    const response = await fetch(downloadUrl)

    if (!response.ok) {
      throw new Error(`Failed to fetch DOCX: ${response.statusText}`)
    }

    const blob = await response.blob()
    await renderAsync(blob, docxPreviewContainer.value)
  } catch (error: any) {
    console.error('Error rendering DOCX preview:', error)
    previewError.value = error.message || 'Failed to render preview'
  }
}

const cleanupDocx = async (onlyIfExists = false) => {
  if (!generatedDocxPath.value) {
    return
  }

  if (onlyIfExists && !generatedDocxPath.value) {
    return
  }

  try {
    const segments = generatedDocxPath.value.split('/')
    const filename = segments[segments.length - 1]
    if (filename && userToken.value) {
      await api.delete(`/spd/assumptions/cleanup/${userToken.value}/${filename}`)
    }
  } catch (error) {
    console.error('Cleanup error:', error)
  } finally {
    generatedDocxPath.value = null
  }
}

const handleBeforeUnload = () => cleanupDocx(true)
const handlePageHide = () => cleanupDocx(true)

const addPreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('pagehide', handlePageHide)
}

const removePreviewListeners = () => {
  if (typeof window === 'undefined') {
    return
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
}
</script>

<style scoped>
.assumptions-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.assumptions-table-section {
  margin-top: 24px;
}

.assumptions-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.assumptions-table-container {
  overflow-x: auto;
}

.assumptions-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 4px;
  overflow: hidden;
}

.assumptions-table thead {
  background-color: #f5f5f5;
}

.assumptions-table th,
.assumptions-table td {
  padding: 12px;
  text-align: left;
  border: 1px solid #ddd;
}

.assumptions-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.assumptions-table tbody tr:hover {
  background-color: #f9f9f9;
}

.assumptions-table tbody tr.selected {
  background-color: #e3f2fd;
}

.assumptions-table .no-data {
  text-align: center;
  color: #999;
  font-style: italic;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
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
  margin-bottom: 8px;
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
  gap: 8px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background-color: #1976d2;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background-color: #1565c0;
}

.btn.info {
  background-color: #0288d1;
  color: white;
}

.btn.info:hover:not(:disabled) {
  background-color: #0277bd;
}

.btn.danger {
  background-color: #d32f2f;
  color: white;
}

.btn.danger:hover:not(:disabled) {
  background-color: #c62828;
}

.docx-modal {
  max-width: 1000px;
  width: 95%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-close:hover {
  color: #000;
}

.docx-modal-body {
  margin-bottom: 16px;
}

.docx-preview-shell {
  position: relative;
  min-height: 500px;
  background: #f5f5f5;
  border-radius: 4px;
}

.docx-preview-container {
  max-height: 600px;
  overflow-y: auto;
}

.docx-preview-container.hidden {
  display: none;
}

.modal-status {
  padding: 20px;
  text-align: center;
  color: #666;
}

.modal-error {
  padding: 20px;
  text-align: center;
  color: #d32f2f;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
