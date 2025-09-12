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
      <div class="components-table-wrapper">
        <table class="components-table">
          <thead>
            <tr>
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
              <td>{{ component.class_name }}</td>
              <td>{{ component.family }}</td>
              <td>{{ component.component }}</td>
              <td>{{ component.component_name }}</td>
              <td>{{ component.element }}</td>
              <td class="element-item">{{ component.element_item }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'
import XMLTreeNode from '../components/XMLTreeNode.vue'

// Reactive data
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const isLoading = ref(false)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info'>('info')
const parsedData = ref<any>(null)
const extractedComponents = ref<any[]>([])

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
    } else {
      statusMessage.value = response.data.message || 'Failed to parse XML file'
      statusType.value = 'error'
    }
  } catch (error: any) {
    console.error('Error parsing XML:', error)
    statusMessage.value = error.response?.data?.detail || 'Error parsing XML file'
    statusType.value = 'error'
  } finally {
    isLoading.value = false
  }
}

async function importToDatabase() {
  if (!selectedFile.value) return

  isLoading.value = true
  statusMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await api.post('/xml/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      statusMessage.value = `${response.data.message}. Imported: ${response.data.components_imported}, Failed: ${response.data.components_failed}`
      statusType.value = 'success'
      
      // Also parse to show the structure
      await parseXml()
    } else {
      statusMessage.value = response.data.message || 'Failed to import XML file'
      statusType.value = 'error'
    }
  } catch (error: any) {
    console.error('Error importing XML:', error)
    statusMessage.value = error.response?.data?.detail || 'Error importing XML file'
    statusType.value = 'error'
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

.components-table-wrapper {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--panel);
}

.components-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  color: var(--text);
}

.components-table th,
.components-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #374151;
}

.components-table th {
  background: var(--bg-soft);
  font-weight: 600;
  position: sticky;
  top: 0;
  color: var(--text);
}

.components-table tr:hover {
  background: rgba(55, 65, 81, 0.5);
}

.element-item {
  max-width: 300px;
  word-wrap: break-word;
  font-size: 0.8rem;
}
</style>