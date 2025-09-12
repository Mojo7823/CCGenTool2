<template>
  <div class="card">
    <h2>XML Parser</h2>
    <p>Upload and parse Common Criteria XML files</p>
    
    <!-- File Upload Section -->
    <div class="upload-section">
      <h3>Upload XML File</h3>
      <div class="file-input-wrapper">
        <input
          type="file"
          ref="fileInput"
          @change="handleFileSelect"
          accept=".xml"
          class="file-input"
        />
        <button @click="triggerFileInput" class="btn btn-primary">
          Choose XML File
        </button>
        <span v-if="selectedFile" class="selected-file">
          {{ selectedFile.name }}
        </span>
      </div>
      
      <div class="action-buttons">
        <button
          @click="parseXml"
          :disabled="!selectedFile || isLoading"
          class="btn btn-success"
        >
          {{ isLoading ? 'Parsing...' : 'Parse XML' }}
        </button>
        <button
          @click="importToDatabase"
          :disabled="!selectedFile || isLoading"
          class="btn btn-info"
        >
          {{ isLoading ? 'Importing...' : 'Parse & Import to Database' }}
        </button>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessage" :class="['status-message', statusType]">
      {{ statusMessage }}
    </div>

    <!-- Modal for notifications -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="modalType === 'success'" class="modal-icon success">✓</div>
          <div v-else-if="modalType === 'error'" class="modal-icon error">✗</div>
          <div v-else class="modal-icon info">ℹ</div>
          <p>{{ modalMessage }}</p>
          <div v-if="modalDetails" class="modal-details">
            <details>
              <summary>Details</summary>
              <pre>{{ modalDetails }}</pre>
            </details>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModal" class="modal-btn">OK</button>
        </div>
      </div>
    </div>

    <!-- Parsed XML Tree View -->
    <div v-if="parsedData" class="parsed-data-section">
      <h3>Parsed XML Structure</h3>
      <div class="tree-container">
        <XMLTreeNode :node="parsedData" :level="0" />
      </div>
    </div>

    <!-- Components Preview -->
    <div v-if="extractedComponents && extractedComponents.length > 0" class="components-section">
      <h3>Extracted Components ({{ extractedComponents.length }})</h3>
      
      <!-- Simple table instead of DataTable for now -->
      <div class="simple-table-wrapper">
        <table class="simple-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Class</th>
              <th>Family</th>
              <th>Component</th>
              <th>Component Name</th>
              <th>Element</th>
              <th>Element Item</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(component, index) in extractedComponents" :key="index">
              <td>{{ component.id }}</td>
              <td>{{ component.class }}</td>
              <td>{{ component.family }}</td>
              <td>{{ component.component }}</td>
              <td>{{ component.component_name }}</td>
              <td>{{ component.element }}</td>
              <td class="element-item-cell">{{ component.element_item }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Import Summary -->
      <div v-if="importSummary" class="import-summary">
        <h4>Import Summary</h4>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">Components Imported:</span>
            <span class="value">{{ importSummary.components_imported }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Components Failed:</span>
            <span class="value">{{ importSummary.components_failed }}</span>
          </div>
          <div v-if="importSummary.tables_used" class="summary-item">
            <span class="label">Tables Used:</span>
            <span class="value">{{ importSummary.tables_used.join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'
import XMLTreeNode from '../components/XMLTreeNode.vue'
import type { Header } from 'vue3-easy-data-table'
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

// Reactive data
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const isLoading = ref(false)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info'>('info')
const parsedData = ref<any>(null)
const extractedComponents = ref<any[]>([])
const importSummary = ref<any>(null)

// Modal data
const showModal = ref(false)
const modalTitle = ref('')
const modalMessage = ref('')
const modalDetails = ref('')
const modalType = ref<'success' | 'error' | 'info'>('info')

// DataTable headers
const tableHeaders: Header[] = [
  { text: 'Class', value: 'class_name', sortable: true },
  { text: 'Family', value: 'family', sortable: true },
  { text: 'Component', value: 'component', sortable: true },
  { text: 'Component Name', value: 'component_name', sortable: true, width: 300 },
  { text: 'Element', value: 'element', sortable: true },
  { text: 'Element Item', value: 'element_item', sortable: false, width: 400 }
]

// Methods
function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    // Reset previous results
    parsedData.value = null
    extractedComponents.value = []
    statusMessage.value = ''
  }
}

function showModalNotification(title: string, message: string, type: 'success' | 'error' | 'info', details: string = '') {
  modalTitle.value = title
  modalMessage.value = message
  modalType.value = type
  modalDetails.value = details
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function parseXml() {
  if (!selectedFile.value) return

  isLoading.value = true
  statusMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await api.post('/xml/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      parsedData.value = response.data.data
      extractedComponents.value = response.data.components || []
      statusMessage.value = `Successfully parsed XML file. Found ${extractedComponents.value.length} components.`
      statusType.value = 'success'
      
      // Show success modal
      showModalNotification(
        'Parsing Complete',
        `Successfully parsed XML file. Found ${extractedComponents.value.length} components.`,
        'success'
      )
    } else {
      statusMessage.value = response.data.message || 'Failed to parse XML file'
      statusType.value = 'error'
      
      // Show error modal
      showModalNotification(
        'Parsing Failed',
        response.data.message || 'Failed to parse XML file',
        'error'
      )
    }
  } catch (error: any) {
    console.error('Error parsing XML:', error)
    const errorMessage = error.response?.data?.detail || 'Error parsing XML file'
    statusMessage.value = errorMessage
    statusType.value = 'error'
    
    // Show error modal
    showModalNotification(
      'Parsing Error',
      'An error occurred while parsing the XML file.',
      'error',
      JSON.stringify(error.response?.data || error.message, null, 2)
    )
  } finally {
    isLoading.value = false
  }
}

async function importToDatabase() {
  if (!selectedFile.value) return

  isLoading.value = true
  statusMessage.value = ''
  importSummary.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await api.post('/xml/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      importSummary.value = response.data
      statusMessage.value = `${response.data.message}. Imported: ${response.data.components_imported}, Failed: ${response.data.components_failed}`
      statusType.value = 'success'
      
      // Show success modal
      showModalNotification(
        'Import Complete',
        `Successfully imported XML data to database.`,
        'success',
        `Components imported: ${response.data.components_imported}\nComponents failed: ${response.data.components_failed}`
      )
      
      // Also parse to show the structure
      await parseXml()
    } else {
      statusMessage.value = response.data.message || 'Failed to import XML file'
      statusType.value = 'error'
      
      // Show error modal
      showModalNotification(
        'Import Failed',
        response.data.message || 'Failed to import XML file',
        'error'
      )
    }
  } catch (error: any) {
    console.error('Error importing XML:', error)
    const errorMessage = error.response?.data?.detail || 'Error importing XML file'
    statusMessage.value = errorMessage
    statusType.value = 'error'
    
    // Show error modal
    showModalNotification(
      'Import Error',
      'An error occurred while importing the XML file to database.',
      'error',
      JSON.stringify(error.response?.data || error.message, null, 2)
    )
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.upload-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid #374151;
  border-radius: 12px;
  background: var(--panel);
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.file-input {
  display: none;
}

.selected-file {
  color: var(--muted);
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #374151;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: #1f2937;
  color: var(--text);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  border-color: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-success {
  background: var(--success);
  border-color: #059669;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-info {
  background: #0891b2;
  border-color: #0e7490;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #0e7490;
}

.status-message {
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  font-weight: 500;
  border: 1px solid #374151;
}

.status-message.success {
  background: #064e3b;
  color: #34d399;
  border-color: #059669;
}

.status-message.error {
  background: #7f1d1d;
  color: #fca5a5;
  border-color: #991b1b;
}

.status-message.info {
  background: #0c4a6e;
  color: #7dd3fc;
  border-color: #0284c7;
}

.parsed-data-section {
  margin-top: 2rem;
}

.tree-container {
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 1rem;
  background: var(--panel);
}

.components-section {
  margin-top: 2rem;
}

.data-table-wrapper {
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--panel);
  overflow: hidden;
}

/* DataTable styling */
.customize-table {
  --easy-table-body-row-background-color: var(--panel);
  --easy-table-body-row-hover-background-color: rgba(55, 65, 81, 0.5);
  --easy-table-body-item-padding: 12px;
  --easy-table-header-background-color: var(--bg-soft);
  --easy-table-header-font-color: var(--text);
  --easy-table-header-item-padding: 12px;
  --easy-table-body-font-color: var(--text);
  --easy-table-border: 1px solid #374151;
  --easy-table-scrollbar-track-color: var(--bg-soft);
  --easy-table-scrollbar-color: #6b7280;
}

.element-item-cell {
  max-width: 400px;
  word-wrap: break-word;
  font-size: 0.9rem;
  line-height: 1.4;
}

.import-summary {
  margin-top: 2rem;
  padding: 1.5rem;
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--panel);
}

.import-summary h4 {
  margin: 0 0 1rem 0;
  color: var(--text);
  font-size: 1.1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-soft);
  border-radius: 6px;
  border: 1px solid #374151;
}

.summary-item .label {
  font-weight: 500;
  color: var(--muted);
}

.summary-item .value {
  font-weight: 600;
  color: var(--text);
}

/* Simple table styles */
.simple-table-wrapper {
  overflow-x: auto;
  border: 1px solid #374151;
  border-radius: 8px;
  margin-top: 1rem;
}

.simple-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-secondary);
}

.simple-table th,
.simple-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #374151;
  color: var(--text);
}

.simple-table th {
  background: var(--bg-tertiary);
  font-weight: 600;
  color: var(--text-secondary);
}

.simple-table tbody tr:hover {
  background: var(--bg-tertiary);
}

.simple-table .element-item-cell {
  max-width: 300px;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg);
  border: 1px solid #374151;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  padding: 1.5rem 1.5rem 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #374151;
  margin-bottom: 1rem;
}

.modal-header h3 {
  margin: 0;
  color: var(--text);
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: background 0.2s;
}

.modal-close:hover {
  background: var(--bg-soft);
}

.modal-body {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.modal-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.modal-icon.success {
  background: #064e3b;
  color: #34d399;
  border: 2px solid #059669;
}

.modal-icon.error {
  background: #7f1d1d;
  color: #fca5a5;
  border: 2px solid #991b1b;
}

.modal-icon.info {
  background: #0c4a6e;
  color: #7dd3fc;
  border: 2px solid #0284c7;
}

.modal-body p {
  margin: 0 0 1rem 0;
  color: var(--text);
  font-size: 1rem;
  line-height: 1.5;
}

.modal-details {
  width: 100%;
  margin-top: 1rem;
  text-align: left;
}

.modal-details details {
  border: 1px solid #374151;
  border-radius: 6px;
  padding: 0.5rem;
  background: var(--bg-soft);
}

.modal-details summary {
  cursor: pointer;
  font-weight: 500;
  color: var(--text);
  padding: 0.5rem;
}

.modal-details pre {
  margin: 0.5rem 0 0 0;
  padding: 1rem;
  background: var(--bg);
  border: 1px solid #374151;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.875rem;
  color: var(--text);
  white-space: pre-wrap;
}

.modal-footer {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  justify-content: center;
}

.modal-btn {
  padding: 0.75rem 2rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.modal-btn:hover {
  background: #2563eb;
}
</style>