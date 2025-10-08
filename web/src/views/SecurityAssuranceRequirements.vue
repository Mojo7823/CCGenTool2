<template>
  <div class="sar-container">
    <h2>Security Assurance Requirements</h2>
    <p>Manage Security Assurance Requirements (SARs) for your Common Criteria evaluation.</p>
    
    <!-- SAR Table Section -->
    <div class="sar-table-section">
      <div class="sar-table-header">
        <h3>Security Assurance Requirements</h3>
        <div class="table-actions">
          <div class="action-buttons">
            <button class="btn primary" @click="openAddModal" title="Create a new Security Assurance Requirement">Add SAR</button>
            <button class="btn secondary" @click="openCustomSarModal">Add Custom SAR</button>
            <button class="btn info" @click="editSelectedSar" :disabled="!selectedSarId">Edit Data</button>
            <button class="btn danger" @click="removeSAR" :disabled="!selectedSarId">Remove SAR</button>
            <button
              class="btn warning"
              @click="clearSessionData"
              :disabled="sarList.length === 0"
              title="Clear all SAR data"
            >
              Clear Data
            </button>
            <button
              class="btn"
              @click="openPreviewModal"
              :disabled="sarList.length === 0"
              title="Preview Security Assurance Requirements"
            >
              Preview
            </button>
          </div>
          <div class="eal-selector compact">
            <label for="ealLevel">Evaluation Assurance Level:</label>
            <select id="ealLevel" v-model="selectedEal" class="eal-select">
              <option v-for="option in ealOptions" :key="option" :value="option">{{ option }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="sar-table-container">
        <table class="sar-table">
          <thead>
            <tr>
              <th>SAR Class</th>
              <th>Assurance Components</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="sar in sarList" 
              :key="sar.id"
              :class="{ selected: selectedSarId === sar.id }"
              @click="selectSar(sar.id)"
            >
              <td>{{ sar.className }}</td>
              <td>{{ formatAssuranceComponent(sar) }}</td>
            </tr>
            <tr v-if="sarList.length === 0">
              <td colspan="2" class="no-data">No SARs available yet. Click "Add SAR" or import data to get started.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add SAR Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ editingMode === 'database' ? 'Edit SAR' : 'Create New SAR' }}</h3>
        
        <!-- Search functionality -->
        <div class="form-group">
          <label for="sarSearch">Search SAR:</label>
          <div class="search-combobox">
            <input
              id="sarSearch"
              ref="searchInput"
              v-model="searchQuery"
              @input="onSearchInput"
              @focus="openSearchDropdown"
              @blur="handleSearchBlur"
              @keydown="handleSearchKeydown"
              type="text"
              class="input search-input"
              placeholder="Search by SAR Class or Components..."
              autocomplete="off"
            />
            <ul v-if="searchDropdownVisible" class="search-dropdown">
              <template v-if="filteredSarClasses.length">
                <li
                  v-for="(cls, index) in filteredSarClasses"
                  :key="cls.name"
                  :class="['search-dropdown-item', { active: index === highlightedClassIndex }]"
                  @mousedown.prevent="selectSarClass(cls)"
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
          <label for="sarClassDisplay">SAR Class:</label>
          <div
            id="sarClassDisplay"
            class="selected-class-display input"
            :class="{ placeholder: !selectedClassLabel }"
          >
            {{ selectedClassLabel || 'Please Select a Class' }}
          </div>
        </div>

        <div class="form-group">
          <label for="sarComponents">SAR Components:</label>
          <select id="sarComponents" v-model="selectedComponent" @change="onComponentChange" class="input" :disabled="!selectedClass">
            <option value="">{{ selectedClass ? 'Please Choose SAR' : 'Please select SAR Class First' }}</option>
            <option v-for="component in filteredUniqueComponents" :key="component.id" :value="component.component">
              {{ component.component }} - {{ component.component_name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="sarPreview">SAR Preview:</label>
          <RichTextEditor v-model="previewContent" placeholder="Compose the SAR details" min-height="240px" />
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeSAR" :disabled="!selectedComponent">
            {{ editingMode === 'database' ? 'Finalize and Update SAR' : 'Finalize and Add SAR' }}
          </button>
          <button class="btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Add Custom SAR Modal -->
    <div v-if="showCustomModal" class="modal-overlay" @click="closeCustomModal">
      <div class="modal-content" @click.stop>
        <h3>{{ editingMode === 'custom' ? 'Edit Custom SAR' : 'Create Custom SAR' }}</h3>

        <div class="form-group">
          <label for="customSarClass">SAR Class:</label>
          <input
            id="customSarClass"
            v-model="customClassInput"
            type="text"
            class="input"
            placeholder="e.g. ACO: Composition"
          />
        </div>

        <div class="form-group">
          <label for="customSarComponent">SAR Components:</label>
          <input
            id="customSarComponent"
            v-model="customComponentInput"
            type="text"
            class="input"
            placeholder="e.g. ACO_DEV.1 - Design documentation"
          />
        </div>

        <div class="form-group">
          <label for="customSarPreview">SAR Items and Description:</label>
          <RichTextEditor
            v-model="customPreviewContent"
            placeholder="Describe the custom SAR details"
            min-height="240px"
          />
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeCustomSAR" :disabled="!canFinalizeCustomSar">
            Finalize and Add Custom SAR
          </button>
          <button class="btn" @click="closeCustomModal">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content docx-modal" @click.stop>
        <div class="modal-header">
          <h3>Security Assurance Requirement Preview</h3>
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
import {
  buildSarPreviewHtml,
  normalizeComponentId,
  uppercaseIdentifiersInHtml,
  type SarPreviewEntry,
} from '../utils/securityPreview'

interface SarClass {
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

type SarSource = 'database' | 'custom'

interface SarMetadata {
  classLabel?: string
  customClassInput?: string
  customComponentInput?: string
}

interface SarEntry {
  id: number
  className: string
  classCode: string
  componentId: string
  componentKey: string
  componentName: string
  previewContent: string
  originalClass: string
  source: SarSource
  metadata?: SarMetadata
}

const ealOptions = ['EAL 1', 'EAL 2', 'EAL 3', 'EAL 4', 'EAL 5', 'EAL 6', 'EAL 7']
const defaultEalLevel = ealOptions[0]
const selectedEal = ref<string>(defaultEalLevel)
let isRestoringSession = false

const uppercaseLeadingIdentifier = (value: string) =>
  value.replace(/^([a-z][a-z0-9_.-]*)/i, match => match.toUpperCase())

const formatAssuranceComponentLabel = (componentId: string, componentName?: string) => {
  const normalizedId = normalizeComponentId(componentId || '')
  const trimmedName = componentName?.trim()
  return trimmedName ? `${normalizedId} : ${trimmedName}` : normalizedId
}

const formatAssuranceComponent = (sar: SarEntry) =>
  formatAssuranceComponentLabel(sar.componentId, sar.componentName)

// Modal state
const showAddModal = ref(false)
const showCustomModal = ref(false)
const showPreviewModal = ref(false)
const editingMode = ref<SarSource | null>(null)
const editingSarId = ref<number | null>(null)
const previewLoading = ref(false)
const previewError = ref('')
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)

// Selected SAR data
const selectedClass = ref('')
const selectedClassLabel = ref('')
const selectedComponent = ref('')
const previewContent = ref('')
const customPreviewContent = ref('')

// Reference data
const sarClasses = ref<SarClass[]>([])
const components = ref<ComponentRecord[]>([])
const uniqueComponents = ref<ComponentOption[]>([])

// Search functionality
const searchQuery = ref('')
const filteredSarClasses = ref<SarClass[]>([])
const filteredUniqueComponents = ref<ComponentOption[]>([])
const searchInput = ref<HTMLInputElement | null>(null)
const searchDropdownVisible = ref(false)
const highlightedClassIndex = ref(0)
const shouldResetSearch = ref(false)

// Custom SAR inputs
const customClassInput = ref('')
const customComponentInput = ref('')

// Table data
const sarList = ref<SarEntry[]>([])
const selectedSarId = ref<number | null>(null)
const selectedSarPreview = ref('')
const nextSarId = ref(1)

// Session management
const userToken = ref(sessionService.getUserToken())

const canFinalizeCustomSar = computed(() => {
  return Boolean(
    customClassInput.value.trim() &&
    customComponentInput.value.trim() &&
    customPreviewContent.value.trim()
  )
})

const cleanClassDescription = (description: string) =>
  description.replace(/\(.*?\)/g, '').replace(/\s+/g, ' ').trim()

const formatClassCode = (name: string) => name.replace('_db', '').toUpperCase()

const getClassMetadata = (cls: SarClass) => {
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

const isDuplicateSar = (classCode: string, componentId: string, excludeId: number | null = null) => {
  const normalizedClass = classCode.trim().toUpperCase()
  const normalizedComponent = componentId.trim().toUpperCase()

  return sarList.value.some(sar => {
    const sameClass = sar.classCode.trim().toUpperCase() === normalizedClass
    const sameComponent = sar.componentId.trim().toUpperCase() === normalizedComponent
    const differentEntry = excludeId === null || sar.id !== excludeId
    return sameClass && sameComponent && differentEntry
  })
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
  filteredSarClasses.value = [...sarClasses.value]
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
  editingSarId.value = null
  resetAddModalState()
  showAddModal.value = true
  await nextTick()
  filterSarData()
  searchDropdownVisible.value = true
  highlightedClassIndex.value = 0
  searchInput.value?.focus()
}

const openCustomSarModal = async () => {
  editingMode.value = null
  editingSarId.value = null
  resetCustomModalState()
  showCustomModal.value = true
  await nextTick()
  const input = document.getElementById('customSarClass') as HTMLInputElement | null
  input?.focus()
}

const closeModal = () => {
  showAddModal.value = false
  resetAddModalState()
  editingMode.value = null
  editingSarId.value = null
}

const closeCustomModal = () => {
  showCustomModal.value = false
  resetCustomModalState()
  editingMode.value = null
  editingSarId.value = null
}

const onSearchInput = () => {
  shouldResetSearch.value = false
  filterSarData()
  searchDropdownVisible.value = true
}

const openSearchDropdown = () => {
  if (shouldResetSearch.value) {
    searchQuery.value = ''
    shouldResetSearch.value = false
  }
  filterSarData()
  searchDropdownVisible.value = true
}

const handleSearchBlur = () => {
  setTimeout(() => {
    searchDropdownVisible.value = false
  }, 120)
}

const filterSarData = () => {
  const query = searchQuery.value.toLowerCase().trim()
  const normalizedQuery = query.replace(/[^a-z0-9]/g, '')

  if (!query) {
    filteredSarClasses.value = [...sarClasses.value]
    filteredUniqueComponents.value = [...uniqueComponents.value]
  } else {
    filteredSarClasses.value = sarClasses.value.filter(cls => {
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

  if (!filteredSarClasses.value.length) {
    return
  }

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    highlightedClassIndex.value = (highlightedClassIndex.value + 1) % filteredSarClasses.value.length
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    highlightedClassIndex.value =
      (highlightedClassIndex.value - 1 + filteredSarClasses.value.length) % filteredSarClasses.value.length
  } else if (event.key === 'Enter') {
    event.preventDefault()
    const cls = filteredSarClasses.value[highlightedClassIndex.value]
    if (cls) {
      await selectSarClass(cls)
    }
  }
}

const selectSarClass = async (cls: SarClass, options: { preservePreview?: boolean } = {}) => {
  const { preservePreview = false } = options
  selectedClass.value = cls.name
  const classMeta = getClassMetadata(cls)
  selectedClassLabel.value = classMeta.display
  searchQuery.value = classMeta.display
  shouldResetSearch.value = true
  filterSarData()
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
    filterSarData()
  } catch (error) {
    console.error('Error loading SAR components:', error)
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
        content += `<p><strong>${heading}</strong> ${item.element_item}</p>`

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

const finalizeSAR = async () => {
  if (!selectedClass.value || !selectedComponent.value) {
    alert('Please select an SAR class and component before finalizing.')
    return
  }

  const selectedClassObj = sarClasses.value.find(cls => cls.name === selectedClass.value)
  if (!selectedClassObj) {
    alert('Unable to find the selected SAR class. Please try again.')
    return
  }

  const classMeta = getClassMetadata(selectedClassObj)
  const selectedComponentObj = uniqueComponents.value.find(comp => comp.component === selectedComponent.value)

  if (!selectedComponentObj) {
    alert('Unable to find the selected SAR component. Please try again.')
    return
  }

  const componentKey = selectedComponent.value
  const componentId = normalizeComponentId(componentKey)

  if (isDuplicateSar(classMeta.code, componentId, editingMode.value === 'database' ? editingSarId.value : null)) {
    alert("This SAR component has already been added for the selected class.")
    return
  }

  const sanitizedPreview = uppercaseIdentifiersInHtml(previewContent.value)
  if (sanitizedPreview !== previewContent.value) {
    previewContent.value = sanitizedPreview
  }

  const entry: SarEntry = {
    id: editingMode.value === 'database' && editingSarId.value !== null ? editingSarId.value : nextSarId.value++,
    className: classMeta.display,
    classCode: classMeta.code,
    componentId,
    componentKey,
    componentName: selectedComponentObj.component_name,
    previewContent: sanitizedPreview,
    originalClass: selectedClass.value,
    source: 'database',
    metadata: {
      classLabel: classMeta.display,
      componentKey,
    }
  }

  if (editingMode.value === 'database' && editingSarId.value !== null) {
    const index = sarList.value.findIndex(item => item.id === editingSarId.value)
    if (index !== -1) {
      sarList.value[index] = { ...entry }
      selectedSarId.value = editingSarId.value
    }
  } else {
    sarList.value.push(entry)
    selectedSarId.value = entry.id
  }

  updatePreviewForAllSars()
  saveSessionData()
  closeModal()
}

const finalizeCustomSAR = () => {
  if (!canFinalizeCustomSar.value) {
    alert('Please provide the class, component, and description for the custom SAR.')
    return
  }

  const classMeta = parseCustomClassInput(customClassInput.value)
  const componentMeta = parseCustomComponentInput(customComponentInput.value)

  const componentKey = componentMeta.id.trim()
  const componentId = normalizeComponentId(componentKey || componentMeta.id)

  if (!componentId) {
    alert('Please provide a valid component identifier for the custom SAR.')
    return
  }

  if (isDuplicateSar(classMeta.code, componentId, editingMode.value === 'custom' ? editingSarId.value : null)) {
    alert("This SAR component has already been added for the selected class.")
    return
  }

  const sanitizedPreview = uppercaseIdentifiersInHtml(customPreviewContent.value)
  if (sanitizedPreview !== customPreviewContent.value) {
    customPreviewContent.value = sanitizedPreview
  }

  const entry: SarEntry = {
    id: editingMode.value === 'custom' && editingSarId.value !== null ? editingSarId.value : nextSarId.value++,
    className: classMeta.display,
    classCode: classMeta.code,
    componentId,
    componentKey: componentKey || componentId,
    componentName: componentMeta.name,
    previewContent: sanitizedPreview,
    originalClass: classMeta.raw,
    source: 'custom',
    metadata: {
      classLabel: classMeta.display,
      customClassInput: classMeta.raw,
      customComponentInput: componentMeta.display,
      componentKey: componentKey || componentId,
    }
  }

  if (editingMode.value === 'custom' && editingSarId.value !== null) {
    const index = sarList.value.findIndex(item => item.id === editingSarId.value)
    if (index !== -1) {
      sarList.value[index] = { ...entry }
      selectedSarId.value = editingSarId.value
    }
  } else {
    sarList.value.push(entry)
    selectedSarId.value = entry.id
  }

  updatePreviewForAllSars()
  saveSessionData()
  closeCustomModal()
}

const selectSar = (sarId: number) => {
  selectedSarId.value = sarId
  updatePreviewForAllSars()
  saveSessionData()
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

  const url = api.getUri({ url: `/security/sar/preview/${userToken.value}` })
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
  if (sarList.value.length === 0) {
    return
  }

  updatePreviewForAllSars()
  previewError.value = ''
  previewLoading.value = true
  showPreviewModal.value = true
  await nextTick()
  cleanupDocx()

  try {
    const payload = {
      user_id: userToken.value,
      html_content: selectedSarPreview.value,
    }

    const response = await api.post('/security/sar/preview', payload)
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

const updatePreviewForAllSars = () => {
  selectedSarPreview.value = buildSarPreviewHtml(sarList.value as unknown as SarPreviewEntry[], {
    selectedEal: selectedEal.value,
  })
}

const removeSAR = () => {
  if (!selectedSarId.value) return

  const index = sarList.value.findIndex(sar => sar.id === selectedSarId.value)
  if (index > -1) {
    sarList.value.splice(index, 1)
    selectedSarId.value = null
    updatePreviewForAllSars()
    saveSessionData()
  }
}

const saveSessionData = () => {
  if (isRestoringSession) {
    return
  }
  sessionService.saveSarData(sarList.value, selectedSarId.value, nextSarId.value, selectedEal.value)
}

const deriveClassCodeForEntry = (entry: Partial<SarEntry> & { source?: SarSource }) => {
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
  const sessionData = sessionService.loadSarData()
  if (sessionData) {
    isRestoringSession = true
    try {
      sarList.value = (sessionData.sarList || []).map((item: any) => {
        const source: SarSource = item.source === 'custom' ? 'custom' : 'database'
        const metadata: SarMetadata = item.metadata || {}
        const classCode = deriveClassCodeForEntry({ ...item, source })

        const storedComponentKey = item.componentKey || metadata.componentKey || item.componentId || ''
        const normalizedComponentId = storedComponentKey
          ? normalizeComponentId(storedComponentKey)
          : typeof item.componentId === 'string'
            ? normalizeComponentId(item.componentId)
            : ''

        const mergedMetadata: SarMetadata = {
          ...metadata,
          componentKey: storedComponentKey || metadata.componentKey,
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
          componentId: normalizedComponentId,
          componentKey: storedComponentKey || normalizedComponentId,
          previewContent: normalizedPreview,
          metadata: mergedMetadata,
        } as SarEntry
      })

      selectedSarId.value = sessionData.selectedSarId ?? null
      nextSarId.value = sessionData.nextSarId ?? 1
      selectedEal.value = sessionData.selectedEal || defaultEalLevel
    } finally {
      isRestoringSession = false
    }

    updatePreviewForAllSars()
    console.log(`Loaded session data for user: ${sessionData.userToken}`)
  }
}

const clearSessionData = () => {
  if (confirm('Are you sure you want to clear all SAR data? This action cannot be undone.')) {
    isRestoringSession = true
    try {
      sessionService.clearSarData()
      sarList.value = []
      selectedSarId.value = null
      nextSarId.value = 1
      selectedEal.value = defaultEalLevel
    } finally {
      isRestoringSession = false
    }

    updatePreviewForAllSars()
    showPreviewModal.value = false
    cleanupDocx()
    previewError.value = ''
    console.log('Session data cleared')
  }
}

const editSelectedSar = async () => {
  if (selectedSarId.value === null) {
    return
  }

  const sar = sarList.value.find(item => item.id === selectedSarId.value)
  if (!sar) {
    return
  }

  editingMode.value = sar.source
  editingSarId.value = sar.id

  if (sar.source === 'database') {
    resetAddModalState()
    selectedClass.value = sar.originalClass
    selectedClassLabel.value = sar.metadata?.classLabel ?? sar.className
    searchQuery.value = sar.metadata?.classLabel ?? sar.className
    filterSarData()

    showAddModal.value = true
    await nextTick()

    const classObj = sarClasses.value.find(cls => cls.name === sar.originalClass)
    if (classObj) {
      await onClassChange({ preservePreview: true })
    } else {
      await onClassChange({ preservePreview: true })
    }

    selectedComponent.value = sar.componentKey || sar.componentId
    filteredUniqueComponents.value = [...uniqueComponents.value]
    previewContent.value = sar.previewContent
    searchDropdownVisible.value = false
  } else {
    resetCustomModalState()
    customClassInput.value = sar.metadata?.customClassInput ?? sar.className
    customComponentInput.value =
      sar.metadata?.customComponentInput ??
      (sar.componentName ? `${sar.componentId} - ${sar.componentName}` : sar.componentKey || sar.componentId)
    customPreviewContent.value = sar.previewContent

    showCustomModal.value = true
  }
}

watch(selectedEal, () => {
  if (isRestoringSession) {
    return
  }
  updatePreviewForAllSars()
  saveSessionData()
})

watch(showAddModal, value => {
  if (!value) {
    searchDropdownVisible.value = false
  }
})

onMounted(async () => {
  addPreviewListeners()
  loadSessionData()

  try {
    const response = await api.get('/families')
    sarClasses.value = response.data.assurance as SarClass[]
  } catch (error) {
    console.error('Error loading SAR classes:', error)
    sarClasses.value = []
  }

  filteredSarClasses.value = [...sarClasses.value]
  filterSarData()

  if (sarList.value.length === 0) {
    updatePreviewForAllSars()
  }

  console.log(`Session initialized for user: ${userToken.value}`)
})

onBeforeUnmount(() => {
  cleanupDocx()
  removePreviewListeners()
})
</script>

<style scoped>

.sar-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: calc(100vh - 150px);
}

.sar-table-section {
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--panel);
  display: flex;
  flex-direction: column;
  min-height: 360px;
}

.sar-table-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #374151;
  background: var(--bg-soft);
  border-radius: 8px 8px 0 0;
  flex-wrap: wrap;
}

.sar-table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sar-table-container {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.sar-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
}

.sar-table th {
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

.sar-table th:first-child {
  width: 50%;
}

.sar-table th:last-child {
  width: 50%;
}

.sar-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #374151;
  vertical-align: top;
}

.sar-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.sar-table tbody tr:hover {
  background: var(--bg-soft);
}

.sar-table tbody tr.selected {
  background: var(--primary);
  color: white;
}

.sar-table .no-data {
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
  padding: 40px;
}

.eal-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
}

.eal-selector label {
  font-weight: 600;
  color: var(--text-bright);
}

.eal-selector.compact label {
  white-space: nowrap;
}

.eal-select {
  background: var(--bg);
  border: 1px solid #4B5563;
  border-radius: 6px;
  padding: 6px 10px;
  color: var(--text-bright);
}

.eal-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.35);
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