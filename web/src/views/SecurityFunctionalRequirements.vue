<template>
  <div class="sfr-container">
    <h2>Security Functional Requirements</h2>
    <p>Manage Security Functional Requirements (SFRs) for your Common Criteria evaluation.</p>
    
    <!-- SFR Table Section -->
    <div class="sfr-table-section">
      <div class="sfr-table-header">
        <h3>Security Functional Requirements</h3>
        <div class="table-actions">
          <button class="btn primary" @click="openAddModal">Add SFR</button>
          <button class="btn secondary" @click="openCustomSfrModal">Add Custom SFR</button>
          <button class="btn info" @click="editSelectedSfr" :disabled="!selectedSfrId">Edit Data</button>
          <button class="btn danger" @click="removeSFR" :disabled="!selectedSfrId">Remove SFR</button>
          <button
            class="btn warning"
            @click="clearSessionData"
            :disabled="sfrList.length === 0"
            title="Clear all SFR data"
          >
            Clear Data
          </button>
          <button
            class="btn"
            @click="openPreviewModal"
            :disabled="sfrList.length === 0"
            title="Preview Security Functional Requirements"
          >
            Preview
          </button>
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

    <!-- Add SFR Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ editingMode === 'database' ? 'Edit SFR' : 'Create New SFR' }}</h3>
        
        <!-- Search functionality -->
        <div class="form-group">
          <label for="sfrSearch">Search SFR:</label>
          <div class="search-combobox">
            <input
              id="sfrSearch"
              ref="searchInput"
              v-model="searchQuery"
              @input="onSearchInput"
              @focus="openSearchDropdown"
              @blur="handleSearchBlur"
              @keydown="handleSearchKeydown"
              type="text"
              class="input search-input"
              placeholder="Search by SFR Class or Components..."
              autocomplete="off"
            />
            <ul v-if="searchDropdownVisible" class="search-dropdown">
              <template v-if="filteredSfrClasses.length">
                <li
                  v-for="(cls, index) in filteredSfrClasses"
                  :key="cls.name"
                  :class="['search-dropdown-item', { active: index === highlightedClassIndex }]"
                  @mousedown.prevent="selectSfrClass(cls)"
                >
                  <span class="search-dropdown-code">{{ formatClassCode(cls.name) }}</span>
                  <span class="search-dropdown-label">{{ cleanClassDescription(cls.description) }}</span>
                </li>
              </template>
              <li v-else class="search-dropdown-empty">No classes found</li>
            </ul>
          </div>
        </div>

        <div class="form-group">
          <label for="sfrClassDisplay">SFR Class:</label>
          <div
            id="sfrClassDisplay"
            class="selected-class-display input"
            :class="{ placeholder: !selectedClassLabel }"
          >
            {{ selectedClassLabel || 'Please Select a Class' }}
          </div>
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
          <RichTextEditor
            v-model="previewContent"
            placeholder="Generated SFR details will appear here"
            min-height="260px"
            class="sfr-editor"
          />
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeSFR" :disabled="!selectedComponent">
            {{ editingMode === 'database' ? 'Finalize and Update SFR' : 'Finalize and Add SFR' }}
          </button>
          <button class="btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Add Custom SFR Modal -->
    <div v-if="showCustomModal" class="modal-overlay" @click="closeCustomModal">
      <div class="modal-content" @click.stop>
        <h3>{{ editingMode === 'custom' ? 'Edit Custom SFR' : 'Create Custom SFR' }}</h3>

        <div class="form-group">
          <label for="customSfrClass">SFR Class:</label>
          <input
            id="customSfrClass"
            v-model="customClassInput"
            type="text"
            class="input"
            placeholder="e.g. FAU: Security Audit"
          />
        </div>

        <div class="form-group">
          <label for="customSfrComponent">SFR Components:</label>
          <input
            id="customSfrComponent"
            v-model="customComponentInput"
            type="text"
            class="input"
            placeholder="e.g. FAU_SAR.1 - Audit Review"
          />
        </div>

        <div class="form-group">
          <label for="customSfrPreview">SFR Items and Description:</label>
          <RichTextEditor
            v-model="customPreviewContent"
            placeholder="Enter custom SFR details"
            min-height="260px"
            class="sfr-editor"
          />
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeCustomSFR" :disabled="!canFinalizeCustomSfr">
            Finalize and Add Custom SFR
          </button>
          <button class="btn" @click="closeCustomModal">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content docx-modal" @click.stop>
        <div class="modal-header">
          <h3>Security Functional Requirement Preview</h3>
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
import { ref, onMounted, nextTick, watch, computed, onBeforeUnmount } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../services/api'
import { sessionService } from '../services/sessionService'
import RichTextEditor from '../components/RichTextEditor.vue'

interface SfrClass {
  name: string
  description: string
}

interface ComponentRecord {
  id: number
  component: string
  component_name: string
  element?: string
  element_item?: string
}

interface ComponentOption {
  id: number
  component: string
  component_name: string
}

type SfrSource = 'database' | 'custom'

interface SfrMetadata {
  classLabel?: string
  classDescription?: string
  customClassInput?: string
  customComponentInput?: string
  componentKey?: string
}

interface SfrEntry {
  id: number
  className: string
  classCode: string
  classDescription: string
  componentId: string
  componentKey: string
  componentName: string
  previewContent: string
  originalClass: string
  source: SfrSource
  metadata?: SfrMetadata
}

// Modal state
const showAddModal = ref(false)
const showCustomModal = ref(false)
const showPreviewModal = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)
const editingMode = ref<SfrSource | null>(null)
const editingSfrId = ref<number | null>(null)

// Selected SFR data
const selectedClass = ref('')
const selectedClassLabel = ref('')
const selectedComponent = ref('')
const previewContent = ref('')
const customPreviewContent = ref('')

// Reference data
const sfrClasses = ref<SfrClass[]>([])
const components = ref<ComponentRecord[]>([])
const uniqueComponents = ref<ComponentOption[]>([])

// Editors

// Search functionality
const searchQuery = ref('')
const filteredSfrClasses = ref<SfrClass[]>([])
const filteredUniqueComponents = ref<ComponentOption[]>([])
const searchInput = ref<HTMLInputElement | null>(null)
const searchDropdownVisible = ref(false)
const highlightedClassIndex = ref(0)
const shouldResetSearch = ref(false)

// Custom SFR inputs
const customClassInput = ref('')
const customComponentInput = ref('')

// Table data
const sfrList = ref<SfrEntry[]>([])
const selectedSfrId = ref<number | null>(null)
const selectedSfrPreview = ref('')
const nextSfrId = ref(1)

// Session management
const userToken = ref(sessionService.getUserToken())

const canFinalizeCustomSfr = computed(() => {
  return Boolean(
    customClassInput.value.trim() &&
    customComponentInput.value.trim() &&
    customPreviewContent.value.trim()
  )
})

const cleanClassDescription = (description: string) =>
  description.replace(/\(.*?\)/g, '').replace(/\s+/g, ' ').trim()

const formatClassCode = (name: string) => name.replace('_db', '').toUpperCase()

const uppercaseLeadingIdentifier = (value: string) =>
  value.replace(/^([a-z][a-z0-9_.-]*)/i, match => match.toUpperCase())

const normalizeComponentId = (value: string) => value.trim().toUpperCase()

const uppercaseIdentifiersInHtml = (html: string) => {
  const transform = (text: string) =>
    text.replace(/\b([a-z][a-z0-9_.-]*[_.][a-z0-9_.-]*)\b/gi, match => match.toUpperCase())

  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return transform(html)
  }

  const container = document.createElement('div')
  container.innerHTML = html
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT)

  while (walker.nextNode()) {
    const node = walker.currentNode as Text
    if (node.nodeValue) {
      node.nodeValue = transform(node.nodeValue)
    }
  }

  return container.innerHTML
}

const deriveClassDescriptionFromLabel = (label: string) => {
  const colonIndex = label.indexOf(':')
  if (colonIndex !== -1) {
    return label.slice(colonIndex + 1).trim()
  }
  return cleanClassDescription(label)
}

const getClassDescriptionForEntry = (entry: { classDescription?: string; className?: string; metadata?: SfrMetadata }) => {
  if (entry.classDescription) {
    return entry.classDescription
  }
  if (entry.metadata?.classDescription) {
    return entry.metadata.classDescription
  }
  if (entry.metadata?.classLabel) {
    return deriveClassDescriptionFromLabel(entry.metadata.classLabel)
  }
  if (entry.className) {
    return deriveClassDescriptionFromLabel(entry.className)
  }
  return ''
}

const getClassMetadata = (cls: SfrClass) => {
  const code = formatClassCode(cls.name)
  const description = cleanClassDescription(cls.description)
  const display = description ? `${code}: ${description}` : code
  return { code, description, display }
}

const parseCustomClassInput = (input: string) => {
  const raw = input.trim()
  if (!raw) {
    return { code: 'CUSTOM', description: '', display: 'CUSTOM', raw: '' }
  }

  const colonIndex = raw.indexOf(':')
  let code = ''
  let description = ''

  if (colonIndex !== -1) {
    code = raw.slice(0, colonIndex).trim().toUpperCase()
    description = raw.slice(colonIndex + 1).trim()
  } else {
    const parts = raw.split(/\s+/)
    code = parts[0].toUpperCase()
    description = raw.slice(parts[0].length).trim()
  }

  const display = description ? `${code}: ${description}` : code

  return {
    code: code || 'CUSTOM',
    description,
    display,
    raw
  }
}

const parseCustomComponentInput = (input: string) => {
  const raw = input.trim()
  if (!raw) {
    return { id: '', name: '', display: '' }
  }

  const separators = [' - ', ' – ', ' — ', ':']
  let id = raw
  let name = ''

  for (const sep of separators) {
    const idx = raw.indexOf(sep)
    if (idx !== -1) {
      id = raw.slice(0, idx).trim()
      name = raw.slice(idx + sep.length).trim()
      break
    }
  }

  const display = name ? `${id} - ${name}` : id

  return {
    id,
    name,
    display
  }
}

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

const resetAddModalState = () => {
  selectedClass.value = ''
  selectedClassLabel.value = ''
  selectedComponent.value = ''
  previewContent.value = ''
  components.value = []
  uniqueComponents.value = []
  filteredUniqueComponents.value = []
  searchQuery.value = ''
  filteredSfrClasses.value = [...sfrClasses.value]
  highlightedClassIndex.value = 0
  searchDropdownVisible.value = false
  shouldResetSearch.value = false
}

const resetCustomModalState = () => {
  customClassInput.value = ''
  customComponentInput.value = ''
  customPreviewContent.value = ''
}

const openAddModal = async () => {
  editingMode.value = null
  editingSfrId.value = null
  resetAddModalState()
  showAddModal.value = true
  await nextTick()
  filterSfrData()
  searchDropdownVisible.value = true
  highlightedClassIndex.value = 0
  searchInput.value?.focus()
}

const openCustomSfrModal = async () => {
  editingMode.value = null
  editingSfrId.value = null
  resetCustomModalState()
  showCustomModal.value = true
  await nextTick()
  const input = document.getElementById('customSfrClass') as HTMLInputElement | null
  input?.focus()
}

const closeModal = () => {
  showAddModal.value = false
  resetAddModalState()
  editingMode.value = null
  editingSfrId.value = null
}

const closeCustomModal = () => {
  showCustomModal.value = false
  resetCustomModalState()
  editingMode.value = null
  editingSfrId.value = null
}

const onSearchInput = () => {
  shouldResetSearch.value = false
  filterSfrData()
  searchDropdownVisible.value = true
}

const openSearchDropdown = () => {
  if (shouldResetSearch.value) {
    searchQuery.value = ''
    shouldResetSearch.value = false
  }
  filterSfrData()
  searchDropdownVisible.value = true
}

const handleSearchBlur = () => {
  setTimeout(() => {
    searchDropdownVisible.value = false
  }, 120)
}

const filterSfrData = () => {
  const query = searchQuery.value.toLowerCase().trim()
  const normalizedQuery = query.replace(/[^a-z0-9]/g, '')

  if (!query) {
    filteredSfrClasses.value = [...sfrClasses.value]
    filteredUniqueComponents.value = [...uniqueComponents.value]
  } else {
    filteredSfrClasses.value = sfrClasses.value.filter(cls => {
      const classCode = formatClassCode(cls.name).toLowerCase()
      const classDescription = cleanClassDescription(cls.description).toLowerCase()
      const combined = `${classCode}: ${classDescription}`
      const normalizedCombined = combined.replace(/[^a-z0-9]/g, '')
      return (
        classCode.includes(query) ||
        classDescription.includes(query) ||
        combined.includes(query) ||
        (normalizedQuery.length > 0 && normalizedCombined.includes(normalizedQuery))
      )
    })

    const selectedLabel = selectedClassLabel.value.toLowerCase()
    const matchesSelectedClass =
      selectedLabel.length > 0 && (
        selectedLabel === query ||
        selectedLabel.replace(/[^a-z0-9]/g, '') === normalizedQuery
      )

    if (matchesSelectedClass) {
      filteredUniqueComponents.value = [...uniqueComponents.value]
    } else {
      filteredUniqueComponents.value = uniqueComponents.value.filter(comp => {
        const componentName = comp.component.toLowerCase()
        const componentDesc = comp.component_name.toLowerCase()
        return componentName.includes(query) || componentDesc.includes(query)
      })
    }
  }

  highlightedClassIndex.value = 0
}

const handleSearchKeydown = async (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    searchDropdownVisible.value = false
    return
  }

  if (!filteredSfrClasses.value.length) {
    return
  }

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    highlightedClassIndex.value = (highlightedClassIndex.value + 1) % filteredSfrClasses.value.length
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    highlightedClassIndex.value =
      (highlightedClassIndex.value - 1 + filteredSfrClasses.value.length) % filteredSfrClasses.value.length
  } else if (event.key === 'Enter') {
    event.preventDefault()
    const cls = filteredSfrClasses.value[highlightedClassIndex.value]
    if (cls) {
      await selectSfrClass(cls)
    }
  }
}

const selectSfrClass = async (cls: SfrClass, options: { preservePreview?: boolean } = {}) => {
  const { preservePreview = false } = options
  selectedClass.value = cls.name
  const classMeta = getClassMetadata(cls)
  selectedClassLabel.value = classMeta.display
  searchQuery.value = classMeta.display
  shouldResetSearch.value = true
  filterSfrData()
  searchDropdownVisible.value = false
  highlightedClassIndex.value = 0
  await onClassChange({ preservePreview })
}

const onClassChange = async (options: { preservePreview?: boolean } = {}) => {
  const { preservePreview = false } = options

  if (!selectedClass.value) {
    components.value = []
    uniqueComponents.value = []
    filteredUniqueComponents.value = []
    return
  }

  if (!preservePreview) {
    selectedComponent.value = ''
    previewContent.value = ''
  }

  try {
    const response = await api.get(`/families/${selectedClass.value}`)
    const data = response.data as ComponentRecord[]
    components.value = data

    const uniqueMap = new Map<string, ComponentOption>()
    data.forEach(item => {
      if (item.component && !uniqueMap.has(item.component)) {
        uniqueMap.set(item.component, {
          id: item.id,
          component: item.component,
          component_name: item.component_name
        })
      }
    })

    uniqueComponents.value = Array.from(uniqueMap.values())
    filterSfrData()
  } catch (error) {
    console.error('Error loading SFR components:', error)
    components.value = []
    uniqueComponents.value = []
    filteredUniqueComponents.value = []
  }
}

const onComponentChange = async () => {
  if (!selectedComponent.value) {
    previewContent.value = ''
    return
  }

  try {
    const componentData = components.value.filter(c => c.component === selectedComponent.value)
    let content = ''

    for (const item of componentData) {
      if (item.element && item.element_item) {
        const heading = uppercaseLeadingIdentifier(item.element)
        const detail = item.element_item
        content += `<p><strong>${heading}</strong> ${detail}</p>`

        try {
          const elementResponse = await api.get(`/element-lists/formatted/${item.element}`)
          if (elementResponse.data && elementResponse.data.items && elementResponse.data.items.length > 0) {
            elementResponse.data.items.forEach(subItem => {
              const normalized = uppercaseLeadingIdentifier(String(subItem))
              content += `<p style="margin-left: 20px;">${normalized}</p>`
            })
          }
        } catch (elementError) {
          console.log(`No sub-items found for element ${item.element}`)
        }
      }
    }

    const sanitizedContent = uppercaseIdentifiersInHtml(content)
    previewContent.value = sanitizedContent
  } catch (error) {
    console.error('Error building preview:', error)
  }
}

const isDuplicateSfr = (classCode: string, componentId: string, excludeId: number | null = null) => {
  const normalizedClassCode = classCode.trim().toUpperCase()
  const normalizedComponentId = componentId.trim().toUpperCase()

  return sfrList.value.some(sfr => {
    const sameClass = sfr.classCode.trim().toUpperCase() === normalizedClassCode
    const sameComponent = sfr.componentId.trim().toUpperCase() === normalizedComponentId
    const differentEntry = excludeId === null || sfr.id !== excludeId
    return sameClass && sameComponent && differentEntry
  })
}

const finalizeSFR = async () => {
  if (!selectedClass.value || !selectedComponent.value) {
    alert('Please select an SFR class and component before finalizing.')
    return
  }

  const selectedClassObj = sfrClasses.value.find(cls => cls.name === selectedClass.value)
  if (!selectedClassObj) {
    alert('Unable to find the selected SFR class. Please try again.')
    return
  }

  const classMeta = getClassMetadata(selectedClassObj)
  const selectedComponentObj = uniqueComponents.value.find(comp => comp.component === selectedComponent.value)

  if (!selectedComponentObj) {
    alert('Unable to find the selected SFR component. Please try again.')
    return
  }

  const componentKey = selectedComponent.value
  const componentId = normalizeComponentId(componentKey)

  if (isDuplicateSfr(classMeta.code, componentId, editingMode.value === 'database' ? editingSfrId.value : null)) {
    alert('This SFR component has already been added.')
    return
  }

  previewContent.value = uppercaseIdentifiersInHtml(previewContent.value)

  const entry: SfrEntry = {
    id: editingMode.value === 'database' && editingSfrId.value !== null ? editingSfrId.value : nextSfrId.value++,
    className: classMeta.display,
    classCode: classMeta.code,
    classDescription: classMeta.description,
    componentId,
    componentKey,
    componentName: selectedComponentObj.component_name,
    previewContent: previewContent.value,
    originalClass: selectedClass.value,
    source: 'database',
    metadata: {
      classLabel: classMeta.display,
      classDescription: classMeta.description,
      componentKey,
    }
  }

  if (editingMode.value === 'database' && editingSfrId.value !== null) {
    const index = sfrList.value.findIndex(item => item.id === editingSfrId.value)
    if (index !== -1) {
      sfrList.value[index] = { ...entry }
      selectedSfrId.value = editingSfrId.value
    }
  } else {
    sfrList.value.push(entry)
    selectedSfrId.value = entry.id
  }

  updatePreviewForAllSfrs()
  saveSessionData()
  closeModal()
}

const finalizeCustomSFR = () => {
  if (!canFinalizeCustomSfr.value) {
    alert('Please provide the class, component, and description for the custom SFR.')
    return
  }

  const classMeta = parseCustomClassInput(customClassInput.value)
  const componentMeta = parseCustomComponentInput(customComponentInput.value)

  const componentKey = componentMeta.id.trim()
  const componentId = normalizeComponentId(componentKey || componentMeta.id)

  if (!componentId) {
    alert('Please provide a valid component identifier for the custom SFR.')
    return
  }

  if (isDuplicateSfr(classMeta.code, componentId, editingMode.value === 'custom' ? editingSfrId.value : null)) {
    alert('This SFR component has already been added.')
    return
  }

  const entry: SfrEntry = {
    id: editingMode.value === 'custom' && editingSfrId.value !== null ? editingSfrId.value : nextSfrId.value++,
    className: classMeta.display,
    classCode: classMeta.code,
    classDescription: classMeta.description,
    componentId,
    componentKey: componentKey || componentId,
    componentName: componentMeta.name,
    previewContent: customPreviewContent.value,
    originalClass: classMeta.raw,
    source: 'custom',
    metadata: {
      classLabel: classMeta.display,
      classDescription: classMeta.description,
      customClassInput: classMeta.raw,
      customComponentInput: componentMeta.display,
      componentKey: componentKey || componentId,
    }
  }

  if (editingMode.value === 'custom' && editingSfrId.value !== null) {
    const index = sfrList.value.findIndex(item => item.id === editingSfrId.value)
    if (index !== -1) {
      sfrList.value[index] = { ...entry }
      selectedSfrId.value = editingSfrId.value
    }
  } else {
    sfrList.value.push(entry)
    selectedSfrId.value = entry.id
  }

  updatePreviewForAllSfrs()
  saveSessionData()
  closeCustomModal()
}

const selectSfr = (sfrId: number) => {
  selectedSfrId.value = sfrId
  updatePreviewForAllSfrs()
  saveSessionData()
}

const updatePreviewForAllSfrs = () => {
  const template = getSfrTemplate()

  if (sfrList.value.length === 0) {
    selectedSfrPreview.value = template
    return
  }

  const sfrsByClass: Record<string, { classDescription: string; sfrs: SfrEntry[] }> = {}
  sfrList.value.forEach(sfr => {
    const key = sfr.classCode || 'UNKNOWN'
    if (!sfrsByClass[key]) {
      sfrsByClass[key] = {
        classDescription: getClassDescriptionForEntry(sfr),
        sfrs: []
      }
    }
    sfrsByClass[key].sfrs.push(sfr)
  })

  let allSfrSections = ''
  let classIndex = 1

  Object.keys(sfrsByClass).forEach(classCode => {
    const classData = sfrsByClass[classCode]
    const classDescription = classData.classDescription || classCode

    allSfrSections += `
<h5>5.1.${classIndex} ${classCode}: ${classDescription}</h5>
`

    let componentIndex = 1
    classData.sfrs.forEach(sfr => {
      const componentId = normalizeComponentId(sfr.componentId)
      const componentTitle = sfr.componentName
        ? `${componentId} : ${sfr.componentName}`
        : componentId
      allSfrSections += `
<h6>5.1.${classIndex}.${componentIndex} ${componentTitle}</h6>
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

const renderDocxPreview = async (path: string) => {
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

const cleanupDocx = (keepalive = false) => {
  if (!userToken.value || !hasGeneratedDocx.value) {
    return
  }

  const url = api.getUri({ url: `/security/sfr/preview/${userToken.value}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  generatedDocxPath.value = null
  hasGeneratedDocx.value = false
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

const openPreviewModal = async () => {
  if (sfrList.value.length === 0) {
    return
  }

  updatePreviewForAllSfrs()
  previewError.value = ''
  previewLoading.value = true
  showPreviewModal.value = true
  await nextTick()
  cleanupDocx()

  try {
    const payload = {
      user_id: userToken.value,
      html_content: selectedSfrPreview.value,
    }

    const response = await api.post('/security/sfr/preview', payload)
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

const saveSessionData = () => {
  sessionService.saveSfrData(sfrList.value, selectedSfrId.value, nextSfrId.value)
}

const deriveClassCodeForEntry = (entry: Partial<SfrEntry> & { source?: SfrSource }) => {
  if (entry.classCode) {
    return entry.classCode
  }

  if (entry.source === 'custom' && entry.originalClass) {
    return parseCustomClassInput(entry.originalClass).code
  }

  if (entry.originalClass) {
    return formatClassCode(entry.originalClass)
  }

  if (entry.className) {
    const colonIndex = entry.className.indexOf(':')
    if (colonIndex !== -1) {
      return entry.className.slice(0, colonIndex).trim().toUpperCase()
    }
  }

  return 'UNKNOWN'
}

const loadSessionData = () => {
  const sessionData = sessionService.loadSfrData()
  if (sessionData) {
    sfrList.value = (sessionData.sfrList || []).map((item: any) => {
      const source: SfrSource = item.source === 'custom' ? 'custom' : 'database'
      const metadata: SfrMetadata = item.metadata || {}
      const classCode = deriveClassCodeForEntry({ ...item, source })
      const classDescription = getClassDescriptionForEntry({ ...item, metadata })

      let componentKey = item.componentKey || metadata.componentKey || ''
      if (!componentKey && metadata.customComponentInput) {
        componentKey = parseCustomComponentInput(metadata.customComponentInput).id
      }
      if (!componentKey && typeof item.componentId === 'string') {
        componentKey = item.componentId
      }

      const normalizedComponentId = typeof item.componentId === 'string' && item.componentId
        ? normalizeComponentId(item.componentId)
        : componentKey
          ? normalizeComponentId(componentKey)
          : ''

      const mergedMetadata: SfrMetadata = {
        ...metadata,
        classDescription,
        componentKey: componentKey || metadata.componentKey,
      }

      if (!mergedMetadata.classLabel && item.className) {
        mergedMetadata.classLabel = item.className
      }

      const originalPreview = typeof item.previewContent === 'string' ? item.previewContent : ''
      const normalizedPreview = source === 'database'
        ? uppercaseIdentifiersInHtml(originalPreview)
        : originalPreview

      return {
        ...item,
        source,
        classCode,
        classDescription,
        componentKey: componentKey || normalizedComponentId,
        componentId: normalizedComponentId || '',
        metadata: mergedMetadata,
        previewContent: normalizedPreview,
      } as SfrEntry
    })

    selectedSfrId.value = sessionData.selectedSfrId ?? null
    nextSfrId.value = sessionData.nextSfrId ?? 1
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
    showPreviewModal.value = false
    cleanupDocx()
    previewError.value = ''
    console.log('Session data cleared')
  }
}

const editSelectedSfr = async () => {
  if (selectedSfrId.value === null) {
    return
  }

  const sfr = sfrList.value.find(item => item.id === selectedSfrId.value)
  if (!sfr) {
    return
  }

  editingMode.value = sfr.source
  editingSfrId.value = sfr.id

  if (sfr.source === 'database') {
    resetAddModalState()
    selectedClass.value = sfr.originalClass
    selectedClassLabel.value = sfr.metadata?.classLabel ?? sfr.className
    searchQuery.value = sfr.metadata?.classLabel ?? sfr.className
    shouldResetSearch.value = true
    filterSfrData()

    showAddModal.value = true
    await nextTick()

    const classObj = sfrClasses.value.find(cls => cls.name === sfr.originalClass)
    if (classObj) {
      await onClassChange({ preservePreview: true })
    } else {
      await onClassChange({ preservePreview: true })
    }

    const matchingComponent = uniqueComponents.value.find(
      comp => normalizeComponentId(comp.component) === sfr.componentId
    )
    selectedComponent.value = matchingComponent ? matchingComponent.component : sfr.componentKey
    filteredUniqueComponents.value = [...uniqueComponents.value]
    previewContent.value = sfr.previewContent
    searchDropdownVisible.value = false
  } else {
    resetCustomModalState()
    customClassInput.value = sfr.metadata?.customClassInput ?? sfr.className
    customComponentInput.value =
      sfr.metadata?.customComponentInput ??
      (sfr.componentName ? `${sfr.componentId} - ${sfr.componentName}` : sfr.componentId)
    customPreviewContent.value = sfr.previewContent
    showCustomModal.value = true
  }
}

onMounted(async () => {
  addPreviewListeners()
  loadSessionData()

  try {
    const response = await api.get('/families')
    sfrClasses.value = response.data.functional as SfrClass[]
  } catch (error) {
    console.error('Error loading SFR classes:', error)
    sfrClasses.value = []
  }

  filteredSfrClasses.value = [...sfrClasses.value]
  filterSfrData()

  if (sfrList.value.length === 0) {
    updatePreviewForAllSfrs()
  }

  console.log(`Session initialized for user: ${userToken.value}`)
})

onBeforeUnmount(() => {
  cleanupDocx()
  removePreviewListeners()
})
</script>

<style scoped>
.sfr-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: calc(100vh - 150px);
}

.sfr-table-section {
  flex: 1;
  min-height: 360px;
  border: 1px solid #374151;
  border-radius: 8px;
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}

.docx-modal {
  width: min(900px, 90vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.btn.secondary {
  background: #4B5563;
  color: white;
  border: 1px solid #374151;
}

.btn.secondary:hover:not(:disabled) {
  background: #374151;
}

.btn.info {
  background: #2563EB;
  color: white;
  border: 1px solid #1D4ED8;
}

.btn.info:hover:not(:disabled) {
  background: #1D4ED8;
}

.btn.secondary:disabled,
.btn.info:disabled {
  background: #6B7280;
  border-color: #6B7280;
  cursor: not-allowed;
  opacity: 0.6;
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

.sfr-editor {
  margin-top: 8px;
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

.search-combobox {
  position: relative;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--panel);
  border: 1px solid #374151;
  border-top: none;
  max-height: 240px;
  overflow-y: auto;
  z-index: 1000;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.35);
}

.search-dropdown-item {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-dropdown-item:hover,
.search-dropdown-item.active {
  background: var(--primary);
  color: white;
}

.search-dropdown-code {
  font-weight: 600;
  min-width: 52px;
}

.search-dropdown-label {
  flex: 1;
  color: var(--text);
}

.search-dropdown-item.active .search-dropdown-label,
.search-dropdown-item:hover .search-dropdown-label {
  color: white;
}

.search-dropdown-empty {
  padding: 10px 12px;
  color: var(--text-muted);
  font-style: italic;
}

.selected-class-display {
  min-height: 40px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  display: flex;
  align-items: center;
  pointer-events: none;
}

.selected-class-display.placeholder {
  color: var(--text-muted);
  font-style: italic;
}
</style>