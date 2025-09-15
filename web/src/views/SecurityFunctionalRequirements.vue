<template>
  <div class="sfr-container">
    <h2>Security Functional Requirements</h2>
    <p>Manage Security Functional Requirements (SFRs) for your Common Criteria evaluation.</p>
    
    <!-- SFR Table Section -->
    <div class="sfr-table-section">
      <div class="sfr-table-header">
        <h3>Security Functional Requirements</h3>
        <div class="table-actions">
          <button class="btn primary" @click="showAddModal = true">Add SFR</button>
          <button class="btn danger" @click="removeSFR" :disabled="!selectedSfrId">Remove SFR</button>
          <button class="btn warning" @click="clearSessionData" :disabled="sfrList.length === 0" title="Clear all SFR data">Clear Data</button>
        </div>
      </div>
      
      <div class="sfr-table-container">
        <table class="sfr-table">
          <thead>
            <tr>
              <th>SFR Class</th>
              <th>SFR Components</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="sfr in sfrList" 
              :key="sfr.id"
              :class="{ selected: selectedSfrId === sfr.id }"
              @click="selectSfr(sfr.id)"
            >
              <td>{{ sfr.className }}</td>
              <td>{{ sfr.componentId }}</td>
            </tr>
            <tr v-if="sfrList.length === 0">
              <td colspan="2" class="no-data">No SFRs added yet. Click "Add SFR" to get started.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Resizable Separator -->
    <div class="separator-container">
      <div 
        class="resizable-separator"
        @mousedown="startResize"
        title="Drag to resize"
      >
        <div class="separator-line"></div>
        <div class="separator-handle">⋮⋮⋮</div>
      </div>
    </div>

    <!-- Preview Section -->
    <div class="sfr-preview-section" ref="previewSection">
      <div class="sfr-preview-header">
        <h3>Security Functional Requirement Preview</h3>
      </div>
      <div class="sfr-preview-content" v-html="selectedSfrPreview"></div>
    </div>

    <!-- Add SFR Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>Create New SFR</h3>
        
        <!-- Search functionality -->
        <div class="form-group">
          <label for="sfrSearch">Search SFR:</label>
          <input 
            id="sfrSearch" 
            v-model="searchQuery" 
            @input="onSearchInput"
            type="text" 
            class="input search-input" 
            placeholder="Search by SFR Class or Components..."
          />
        </div>

        <div class="form-group">
          <label for="sfrClass">SFR Class:</label>
          <select id="sfrClass" v-model="selectedClass" @change="onClassChange" class="input">
            <option value="">Please Select a Class</option>
            <option v-for="cls in filteredSfrClasses" :key="cls.name" :value="cls.name">
              {{ cls.name.replace('_db', '') }} - {{ cls.description.replace(/\(.*?\)/, '').trim() }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="sfrComponents">SFR Components:</label>
          <select id="sfrComponents" v-model="selectedComponent" @change="onComponentChange" class="input" :disabled="!selectedClass">
            <option value="">{{ selectedClass ? 'Please Choose SFR' : 'Please select SFR Class First' }}</option>
            <option v-for="component in filteredUniqueComponents" :key="component.id" :value="component.component">
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
            <button type="button" class="btn color-btn" @click="showColorPicker = !showColorPicker">🎨</button>
            <div v-if="showColorPicker" class="color-picker">
              <button type="button" class="color-option" style="background-color: #000000" @click="applyColor('#000000')" title="Black"></button>
              <button type="button" class="color-option" style="background-color: #FF0000" @click="applyColor('#FF0000')" title="Red"></button>
              <button type="button" class="color-option" style="background-color: #00FF00" @click="applyColor('#00FF00')" title="Green"></button>
              <button type="button" class="color-option" style="background-color: #0000FF" @click="applyColor('#0000FF')" title="Blue"></button>
              <button type="button" class="color-option" style="background-color: #FFA500" @click="applyColor('#FFA500')" title="Orange"></button>
              <button type="button" class="color-option" style="background-color: #800080" @click="applyColor('#800080')" title="Purple"></button>
              <button type="button" class="color-option" style="background-color: #008080" @click="applyColor('#008080')" title="Teal"></button>
              <button type="button" class="color-option" style="background-color: #FFD700" @click="applyColor('#FFD700')" title="Gold"></button>
            </div>
          </div>
          <div 
            ref="previewEditor"
            class="preview-editor" 
            contenteditable="true"
            @input="onPreviewInput"
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
import { ref, onMounted, nextTick, watch } from 'vue'
import api from '../services/api'
import { sessionService } from '../services/sessionService'

// Data
const showAddModal = ref(false)
const selectedClass = ref('')
const selectedComponent = ref('')
const previewContent = ref('')
const sfrClasses = ref([])
const components = ref([])
const uniqueComponents = ref([])
const previewEditor = ref(null)
const showColorPicker = ref(false)

// Search functionality
const searchQuery = ref('')
const filteredSfrClasses = ref([])
const filteredUniqueComponents = ref([])

// New data for SFR list and table functionality
const sfrList = ref([])
const selectedSfrId = ref(null)
const selectedSfrPreview = ref('')
const previewSection = ref(null)
const isResizing = ref(false)
const nextSfrId = ref(1)

// Session management
const userToken = ref(sessionService.getUserToken())

// Predefined template for SFR preview
const getSfrTemplate = () => {
  return `
<h4>5. SECURITY REQUIREMENTS</h4>
<p>This section defines the Security functional requirements (SFRs) and the Security assurance requirements (SARs) that fulfill the TOE. Assignment, selection, iteration and refinement operations have been made, adhering to the following conventions:</p>
<p><strong>Assignments.</strong> They appear between square brackets. The word "assignment" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>
<p><strong>Selections.</strong> They appear between square brackets. The word "selection" is maintained and the resolution is presented in <strong><em><span style="color: #0000FF;">boldface, italic and blue color</span></em></strong>.</p>
<p><strong>Iterations.</strong> It includes "/" and an "identifier" following requirement identifier that allows to distinguish the iterations of the requirement. Example: FCS_COP.1/XXX.</p>
<p><strong>Refinements:</strong> the text where the refinement has been done is shown <strong><em><span style="color: #FF6B6B;">bold, italic, and light red color</span></em></strong>. Where part of the content of a SFR component has been removed, the removed text is shown in <strong><em><span style="color: #FF6B6B;"><s>bold, italic, light red color and crossed out</s></span></em></strong>.</p>
<h4>5.1 Security Functional Requirements</h4>
`
}

// Methods
const closeModal = () => {
  showAddModal.value = false
  selectedClass.value = ''
  selectedComponent.value = ''
  previewContent.value = ''
  components.value = []
  uniqueComponents.value = []
  showColorPicker.value = false
  searchQuery.value = ''
  filteredSfrClasses.value = []
  filteredUniqueComponents.value = []
  
  // Clear the editor content
  if (previewEditor.value) {
    previewEditor.value.innerHTML = ''
  }
}

const onSearchInput = () => {
  filterSfrData()
}

const filterSfrData = () => {
  const query = searchQuery.value.toLowerCase().trim()
  
  if (!query) {
    // If search is empty, return all data
    filteredSfrClasses.value = [...sfrClasses.value]
    filteredUniqueComponents.value = [...uniqueComponents.value]
  } else {
    // Filter SFR Classes by name and description
    filteredSfrClasses.value = sfrClasses.value.filter(cls => {
      const className = cls.name.replace('_db', '').toLowerCase()
      const classDescription = cls.description.toLowerCase()
      return className.includes(query) || classDescription.includes(query)
    })
    
    // Filter SFR Components by component name and component_name
    filteredUniqueComponents.value = uniqueComponents.value.filter(comp => {
      const componentName = comp.component.toLowerCase()
      const componentDesc = comp.component_name.toLowerCase()
      return componentName.includes(query) || componentDesc.includes(query)
    })
  }
}

const onClassChange = async () => {
  selectedComponent.value = ''
  previewContent.value = ''
  components.value = []
  
  // Clear the editor content
  if (previewEditor.value) {
    previewEditor.value.innerHTML = ''
  }
  
  if (!selectedClass.value) return
  
  try {
    const response = await api.get(`/families/${selectedClass.value}`)
    
    // Group components by component name to remove duplicates
    const uniqueComponentsMap = new Map()
    response.data.forEach(item => {
      if (!uniqueComponentsMap.has(item.component)) {
        uniqueComponentsMap.set(item.component, {
          id: item.id,
          component: item.component,
          component_name: item.component_name
        })
      }
    })
    
    // Store the full response data for preview generation
    components.value = response.data
    
    // Store unique components for dropdown display
    uniqueComponents.value = Array.from(uniqueComponentsMap.values())
    
    // Apply current search filter to components
    filterSfrData()
  } catch (error) {
    console.warn('API failed for components, using mock data')
    
    // Mock components based on selected class
    let mockComponents = []
    if (selectedClass.value === 'fau_db') {
      mockComponents = [
        {
          id: 1,
          component: 'FAU_GEN.1',
          component_name: 'Audit data generation',
          element: 'FAU_GEN.1.1',
          element_item: 'The TSF shall be able to generate an audit record of the following auditable events: [assignment: list of auditable events].'
        },
        {
          id: 2,
          component: 'FAU_GEN.1',
          component_name: 'Audit data generation',
          element: 'FAU_GEN.1.2',
          element_item: 'The TSF shall record within each audit record at least the following information: [assignment: list of audit record information].'
        },
        {
          id: 3,
          component: 'FAU_GEN.2',
          component_name: 'User identity association',
          element: 'FAU_GEN.2.1',
          element_item: 'For audit events resulting from actions of identified users, the TSF shall be able to associate each auditable event with the identity of the user that caused the event.'
        }
      ]
    } else if (selectedClass.value === 'fia_db') {
      mockComponents = [
        {
          id: 4,
          component: 'FIA_AFL.1',
          component_name: 'Authentication failure handling',
          element: 'FIA_AFL.1.1',
          element_item: 'The TSF shall detect when [selection: positive integer number] unsuccessful authentication attempts occur related to [assignment: list of authentication events].'
        },
        {
          id: 5,
          component: 'FIA_ATD.1',
          component_name: 'User attribute definition',
          element: 'FIA_ATD.1.1',
          element_item: 'The TSF shall maintain the following list of security attributes belonging to individual users: [assignment: list of security attributes].'
        }
      ]
    } else if (selectedClass.value === 'fmt_db') {
      mockComponents = [
        {
          id: 6,
          component: 'FMT_MOF.1',
          component_name: 'Management of security functions behaviour',
          element: 'FMT_MOF.1.1',
          element_item: 'The TSF shall restrict the ability to [selection: change_default, query, modify, delete] the behaviour of the functions [assignment: list of functions] to [assignment: the authorised identified roles].'
        }
      ]
    } else {
      mockComponents = [
        {
          id: 7,
          component: 'MOCK_COMP.1',
          component_name: 'Mock component for testing',
          element: 'MOCK_COMP.1.1',
          element_item: 'This is a mock component for testing the search and selection functionality.'
        }
      ]
    }
    
    // Group components by component name to remove duplicates
    const uniqueComponentsMap = new Map()
    mockComponents.forEach(item => {
      if (!uniqueComponentsMap.has(item.component)) {
        uniqueComponentsMap.set(item.component, {
          id: item.id,
          component: item.component,
          component_name: item.component_name
        })
      }
    })
    
    components.value = mockComponents
    uniqueComponents.value = Array.from(uniqueComponentsMap.values())
    
    // Apply current search filter to components
    filterSfrData()
  }
}

const onComponentChange = async () => {
  if (!selectedComponent.value) {
    previewContent.value = ''
    if (previewEditor.value) {
      previewEditor.value.innerHTML = ''
    }
    return
  }
  
  try {
    // Find the component data that matches the selected component
    const componentData = components.value.filter(c => c.component === selectedComponent.value)
    
    // Build the preview content with elements and element items including sub-items
    let content = ''
    
    for (const item of componentData) {
      if (item.element && item.element_item) {
        content += `<p><strong>${item.element}</strong> ${item.element_item}</p>`
        
        // Check if this element has sub-items in element_list_db
        try {
          const elementResponse = await api.get(`/element-lists/formatted/${item.element}`)
          if (elementResponse.data && elementResponse.data.items && elementResponse.data.items.length > 0) {
            // Add the sub-items
            elementResponse.data.items.forEach(subItem => {
              content += `<p style="margin-left: 20px;">${subItem}</p>`
            })
          }
        } catch (elementError) {
          // Element might not have sub-items, which is fine
          console.log(`No sub-items found for element ${item.element}`)
        }
      }
    }
    
    previewContent.value = content
    
    // Update the editor content manually
    if (previewEditor.value) {
      previewEditor.value.innerHTML = content
    }
  } catch (error) {
    console.error('Error building preview:', error)
  }
}

const onPreviewInput = (event) => {
  // Simply update the content without trying to restore cursor position
  // The browser will handle cursor position naturally since we're not 
  // interfering with the contenteditable behavior
  previewContent.value = event.target.innerHTML
}

const formatText = (command) => {
  document.execCommand(command, false, null)
  previewEditor.value?.focus()
}

const applyColor = (color) => {
  document.execCommand('foreColor', false, color)
  showColorPicker.value = false
  previewEditor.value?.focus()
}

const finalizeSFR = async () => {
  try {
    // Get the family name for the class
    const selectedClassObj = sfrClasses.value.find(cls => cls.name === selectedClass.value)
    const classDisplayName = selectedClassObj ? selectedClassObj.description : selectedClass.value
    
    // Get the component name
    const selectedComponentObj = uniqueComponents.value.find(comp => comp.component === selectedComponent.value)
    const componentName = selectedComponentObj ? selectedComponentObj.component_name : ''
    
    // Create new SFR entry
    const newSfr = {
      id: nextSfrId.value++,
      className: classDisplayName,
      componentId: selectedComponent.value,
      componentName: componentName,
      previewContent: previewContent.value,
      originalClass: selectedClass.value
    }
    
    // Add to SFR list
    sfrList.value.push(newSfr)
    
    // Select the newly added SFR
    selectedSfrId.value = newSfr.id
    
    // Update preview to show all SFRs
    updatePreviewForAllSfrs()
    
    // Save to session
    saveSessionData()
    
    // Close modal
    closeModal()
    
    // Show success message
    console.log(`SFR created successfully!\nClass: ${selectedClass.value}\nComponent: ${selectedComponent.value}`)
  } catch (error) {
    console.error('Error finalizing SFR:', error)
    alert('Error creating SFR. Please try again.')
  }
}

const selectSfr = (sfrId) => {
  selectedSfrId.value = sfrId
  updatePreviewForAllSfrs()
  saveSessionData()
}

const updatePreviewForAllSfrs = () => {
  // Build the full preview with template and ALL SFR content
  const template = getSfrTemplate()
  
  if (sfrList.value.length === 0) {
    selectedSfrPreview.value = template
    return
  }
  
  // Group SFRs by their class for better organization
  const sfrsByClass = {}
  sfrList.value.forEach(sfr => {
    const classAbbr = sfr.originalClass ? sfr.originalClass.replace('_db', '').toUpperCase() : 'UNKNOWN'
    if (!sfrsByClass[classAbbr]) {
      sfrsByClass[classAbbr] = {
        className: sfr.className,
        sfrs: []
      }
    }
    sfrsByClass[classAbbr].sfrs.push(sfr)
  })
  
  // Build the SFR sections for all classes
  let allSfrSections = ''
  let classIndex = 1
  
  Object.keys(sfrsByClass).forEach(classAbbr => {
    const classData = sfrsByClass[classAbbr]
    
    allSfrSections += `
<h5>5.1.${classIndex} ${classAbbr}: ${classData.className}</h5>
`
    
    let componentIndex = 1
    classData.sfrs.forEach(sfr => {
      allSfrSections += `
<h6>5.1.${classIndex}.${componentIndex} ${sfr.componentId} : ${sfr.componentName}</h6>
<div style="margin-left: 20px;">
${sfr.previewContent}
</div>
`
      componentIndex++
    })
    
    classIndex++
  })
  
  selectedSfrPreview.value = template + allSfrSections
}

const removeSFR = () => {
  if (!selectedSfrId.value) return
  
  const index = sfrList.value.findIndex(sfr => sfr.id === selectedSfrId.value)
  if (index > -1) {
    sfrList.value.splice(index, 1)
    selectedSfrId.value = null
    updatePreviewForAllSfrs()
    saveSessionData()
  }
}

// Session management functions
const saveSessionData = () => {
  sessionService.saveSfrData(sfrList.value, selectedSfrId.value, nextSfrId.value)
}

const loadSessionData = () => {
  const sessionData = sessionService.loadSfrData()
  if (sessionData) {
    sfrList.value = sessionData.sfrList || []
    selectedSfrId.value = sessionData.selectedSfrId || null
    nextSfrId.value = sessionData.nextSfrId || 1
    updatePreviewForAllSfrs()
    console.log(`Loaded session data for user: ${sessionData.userToken}`)
  }
}

const clearSessionData = () => {
  if (confirm('Are you sure you want to clear all SFR data? This action cannot be undone.')) {
    sessionService.clearSfrData()
    sfrList.value = []
    selectedSfrId.value = null
    nextSfrId.value = 1
    updatePreviewForAllSfrs()
    console.log('Session data cleared')
  }
}

// Resizing functionality
const startResize = (event) => {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  event.preventDefault()
}

const handleResize = (event) => {
  if (!isResizing.value) return
  
  const container = document.querySelector('.sfr-container')
  const rect = container.getBoundingClientRect()
  const newHeight = event.clientY - rect.top - 100 // Adjust for header and margin
  
  if (newHeight > 150 && newHeight < window.innerHeight - 300) {
    const tableSection = document.querySelector('.sfr-table-section')
    if (tableSection) {
      tableSection.style.height = newHeight + 'px'
    }
  }
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// Load SFR classes on mount
onMounted(async () => {
  try {
    // Load session data first
    loadSessionData()
    
    // For testing, use mock data when API fails
    try {
      const response = await api.get('/families')
      sfrClasses.value = response.data.functional
    } catch (error) {
      console.warn('API failed, using mock data for testing')
      // Mock data for testing
      sfrClasses.value = [
        { name: 'fau_db', description: 'Security audit (FAU)' },
        { name: 'fia_db', description: 'Identification and authentication (FIA)' },
        { name: 'fmt_db', description: 'Security management (FMT)' },
        { name: 'fpt_db', description: 'Protection of the TSF (FPT)' }
      ]
    }
    
    // Initialize filtered arrays with all data
    filteredSfrClasses.value = [...sfrClasses.value]
    
    // Initialize with template (if no session data was loaded)
    if (sfrList.value.length === 0) {
      updatePreviewForAllSfrs()
    }
    
    console.log(`Session initialized for user: ${userToken.value}`)
  } catch (error) {
    console.error('Error in onMounted:', error)
    // Still load session data even if everything fails
    loadSessionData()
    updatePreviewForAllSfrs()
  }
})
</script>

<style scoped>
.sfr-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  gap: 0;
}

.sfr-table-section {
  min-height: 300px;
  height: 45vh;
  border: 1px solid #374151;
  border-radius: 8px 8px 0 0;
  background: var(--panel);
  display: flex;
  flex-direction: column;
}

.sfr-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #374151;
  background: var(--bg-soft);
  border-radius: 8px 8px 0 0;
}

.sfr-table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.sfr-table-container {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.sfr-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
}

.sfr-table th {
  background: var(--bg-soft);
  border-bottom: 2px solid #374151;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--text-bright);
  position: sticky;
  top: 0;
  z-index: 1;
}

.sfr-table th:first-child {
  width: 50%;
}

.sfr-table th:last-child {
  width: 50%;
}

.sfr-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #374151;
  vertical-align: top;
}

.sfr-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.sfr-table tbody tr:hover {
  background: var(--bg-soft);
}

.sfr-table tbody tr.selected {
  background: var(--primary);
  color: white;
}

.sfr-table .no-data {
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
  padding: 40px;
}

.separator-container {
  height: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-left: 1px solid #374151;
  border-right: 1px solid #374151;
  position: relative;
}

.resizable-separator {
  width: 100%;
  height: 10px;
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-soft);
  position: relative;
}

.separator-line {
  width: 100%;
  height: 2px;
  background: #374151;
}

.separator-handle {
  position: absolute;
  color: #6B7280;
  font-size: 10px;
  letter-spacing: -1px;
  background: var(--bg-soft);
  padding: 0 8px;
}

.resizable-separator:hover {
  background: var(--primary);
}

.resizable-separator:hover .separator-handle {
  color: white;
}

.sfr-preview-section {
  flex: 1;
  min-height: 300px;
  border: 1px solid #374151;
  border-radius: 0 0 8px 8px;
  border-top: none;
  background: var(--panel);
  display: flex;
  flex-direction: column;
}

.sfr-preview-header {
  padding: 16px 20px;
  border-bottom: 1px solid #374151;
  background: var(--bg-soft);
}

.sfr-preview-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sfr-preview-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: var(--bg);
  border-radius: 0 0 8px 8px;
  line-height: 1.6;
}

.sfr-preview-content h4 {
  color: var(--text-bright);
  margin-top: 0;
  margin-bottom: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 18px;
  font-weight: 600;
}

.sfr-preview-content h5 {
  color: var(--text-bright);
  margin-top: 24px;
  margin-bottom: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 16px;
  font-weight: 600;
}

.sfr-preview-content h6 {
  color: var(--text-bright);
  margin-top: 20px;
  margin-bottom: 10px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: 600;
}

.sfr-preview-content p {
  margin-bottom: 12px;
  color: var(--text);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  line-height: 1.6;
}

.sfr-preview-content strong {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-weight: 600;
  color: var(--text-bright);
}

.sfr-preview-content em {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-style: italic;
}

.btn.danger {
  background: #DC2626;
  color: white;
  border: 1px solid #B91C1C;
}

.btn.danger:hover:not(:disabled) {
  background: #B91C1C;
}

.btn.danger:disabled {
  background: #6B7280;
  border-color: #6B7280;
  cursor: not-allowed;
  opacity: 0.5;
}

.btn.warning {
  background: #F59E0B;
  color: white;
  border: 1px solid #D97706;
}

.btn.warning:hover:not(:disabled) {
  background: #D97706;
}

.btn.warning:disabled {
  background: #6B7280;
  border-color: #6B7280;
  cursor: not-allowed;
  opacity: 0.5;
}

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
  position: relative;
}

.wysiwyg-toolbar .btn {
  padding: 4px 8px;
  font-size: 12px;
}

.color-btn {
  position: relative;
}

.color-picker {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1000;
  background: var(--panel);
  border: 1px solid #374151;
  border-radius: 4px;
  padding: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  width: 120px;
}

.color-option {
  width: 20px;
  height: 20px;
  border: 1px solid #374151;
  border-radius: 3px;
  cursor: pointer;
  transition: transform 0.2s;
}

.color-option:hover {
  transform: scale(1.1);
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
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  line-height: 1.6;
}

.preview-editor:focus {
  border-color: var(--primary);
}

/* Ensure consistent typography in editor content */
.preview-editor h1, .preview-editor h2, .preview-editor h3, 
.preview-editor h4, .preview-editor h5, .preview-editor h6 {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-weight: 600;
  color: var(--text-bright);
}

.preview-editor p {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.preview-editor strong {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-weight: 600;
  color: var(--text-bright);
}

.preview-editor em {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-style: italic;
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 24px;
}

.search-input {
  border: 2px solid #374151;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>