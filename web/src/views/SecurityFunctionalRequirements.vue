<template>
  <div>
    <h2>Security Functional Requirements</h2>
    <p>Manage Security Functional Requirements (SFRs) for your Common Criteria evaluation.</p>
    
    <div class="actions">
      <button class="btn primary" @click="showAddModal = true">Add SFR</button>
    </div>

    <!-- Add SFR Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>Create New SFR</h3>
        
        <div class="form-group">
          <label for="sfrClass">SFR Class:</label>
          <select id="sfrClass" v-model="selectedClass" @change="onClassChange" class="input">
            <option value="">Please Select a Class</option>
            <option v-for="cls in sfrClasses" :key="cls.name" :value="cls.name">
              {{ cls.name.replace('_db', '') }} - {{ cls.description.replace(/\(.*?\)/, '').trim() }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="sfrComponents">SFR Components:</label>
          <select id="sfrComponents" v-model="selectedComponent" @change="onComponentChange" class="input" :disabled="!selectedClass">
            <option value="">{{ selectedClass ? 'Loading components...' : 'Please select SFR Class First' }}</option>
            <option v-for="component in components" :key="component.id" :value="component.component">
              {{ component.component }} - {{ component.component_name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="sfrPreview">SFR Preview:</label>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline')"><u>U</u></button>
          </div>
          <div 
            ref="previewEditor"
            class="preview-editor" 
            contenteditable="true"
            @input="onPreviewInput"
            v-html="previewContent"
          ></div>
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeSFR" :disabled="!selectedComponent">Finalize and Add SFR</button>
          <button class="btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'

// Data
const showAddModal = ref(false)
const selectedClass = ref('')
const selectedComponent = ref('')
const previewContent = ref('')
const sfrClasses = ref([])
const components = ref([])
const previewEditor = ref(null)

// Methods
const closeModal = () => {
  showAddModal.value = false
  selectedClass.value = ''
  selectedComponent.value = ''
  previewContent.value = ''
  components.value = []
}

const onClassChange = async () => {
  selectedComponent.value = ''
  previewContent.value = ''
  components.value = []
  
  if (!selectedClass.value) return
  
  try {
    const response = await api.get(`/families/${selectedClass.value}`)
    components.value = response.data
  } catch (error) {
    console.error('Error fetching components:', error)
  }
}

const onComponentChange = async () => {
  if (!selectedComponent.value) {
    previewContent.value = ''
    return
  }
  
  try {
    // Find the component data that matches the selected component
    const componentData = components.value.filter(c => c.component === selectedComponent.value)
    
    // Build the preview content with elements and element items
    let content = ''
    componentData.forEach(item => {
      if (item.element && item.element_item) {
        content += `<p><strong>${item.element}</strong> ${item.element_item}</p>`
      }
    })
    
    previewContent.value = content
  } catch (error) {
    console.error('Error building preview:', error)
  }
}

const onPreviewInput = (event) => {
  previewContent.value = event.target.innerHTML
}

const formatText = (command) => {
  document.execCommand(command, false, null)
  previewEditor.value?.focus()
}

const finalizeSFR = () => {
  // In a real implementation, this would save the SFR to the database
  alert(`SFR created successfully!\nClass: ${selectedClass.value}\nComponent: ${selectedComponent.value}`)
  closeModal()
}

// Load SFR classes on mount
onMounted(async () => {
  try {
    const response = await api.get('/families')
    sfrClasses.value = response.data.functional
  } catch (error) {
    console.error('Error fetching SFR classes:', error)
  }
})
</script>

<style scoped>
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
  background: var(--panel);
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}

.form-group select,
.form-group input {
  width: 100%;
}

.wysiwyg-toolbar {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
  padding: 8px;
  background: var(--bg-soft);
  border: 1px solid #374151;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
}

.wysiwyg-toolbar .btn {
  padding: 4px 8px;
  font-size: 12px;
}

.preview-editor {
  width: 100%;
  min-height: 200px;
  padding: 12px;
  background: var(--bg);
  border: 1px solid #374151;
  border-radius: 0 0 8px 8px;
  color: var(--text);
  outline: none;
}

.preview-editor:focus {
  border-color: var(--primary);
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>