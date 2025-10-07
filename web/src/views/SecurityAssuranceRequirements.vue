<template>
  <div class="sar-container">
    <h2>Security Assurance Requirements</h2>
    <p>Manage Security Assurance Requirements (SARs) for your Common Criteria evaluation.</p>
    
    <!-- SAR Table Section -->
    <div class="sar-table-section">
      <div class="sar-table-header">
        <h3>Security Assurance Requirements</h3>
        <div class="table-actions">
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
          <div class="eal-selector-inline">
            <label for="ealLevel">EAL:</label>
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
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'standard')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'standard')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'standard')"><u>U</u></button>
            <button type="button" class="btn color-btn" @click="toggleColorPicker('standard')">🎨</button>
            <div v-if="showColorPicker" class="color-picker">
              <button type="button" class="color-option" style="background-color: #000000" @click="applyColor('#000000', 'standard')" title="Black"></button>
              <button type="button" class="color-option" style="background-color: #FF0000" @click="applyColor('#FF0000', 'standard')" title="Red"></button>
              <button type="button" class="color-option" style="background-color: #00FF00" @click="applyColor('#00FF00', 'standard')" title="Green"></button>
              <button type="button" class="color-option" style="background-color: #0000FF" @click="applyColor('#0000FF', 'standard')" title="Blue"></button>
              <button type="button" class="color-option" style="background-color: #FFA500" @click="applyColor('#FFA500', 'standard')" title="Orange"></button>
              <button type="button" class="color-option" style="background-color: #800080" @click="applyColor('#800080', 'standard')" title="Purple"></button>
              <button type="button" class="color-option" style="background-color: #008080" @click="applyColor('#008080', 'standard')" title="Teal"></button>
              <button type="button" class="color-option" style="background-color: #FFD700" @click="applyColor('#FFD700', 'standard')" title="Gold"></button>
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
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'custom')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'custom')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'custom')"><u>U</u></button>
            <button type="button" class="btn color-btn" @click="toggleColorPicker('custom')">🎨</button>
            <div v-if="showCustomColorPicker" class="color-picker">
              <button type="button" class="color-option" style="background-color: #000000" @click="applyColor('#000000', 'custom')" title="Black"></button>
              <button type="button" class="color-option" style="background-color: #FF0000" @click="applyColor('#FF0000', 'custom')" title="Red"></button>
              <button type="button" class="color-option" style="background-color: #00FF00" @click="applyColor('#00FF00', 'custom')" title="Green"></button>
              <button type="button" class="color-option" style="background-color: #0000FF" @click="applyColor('#0000FF', 'custom')" title="Blue"></button>
              <button type="button" class="color-option" style="background-color: #FFA500" @click="applyColor('#FFA500', 'custom')" title="Orange"></button>
              <button type="button" class="color-option" style="background-color: #800080" @click="applyColor('#800080', 'custom')" title="Purple"></button>
              <button type="button" class="color-option" style="background-color: #008080" @click="applyColor('#008080', 'custom')" title="Teal"></button>
              <button type="button" class="color-option" style="background-color: #FFD700" @click="applyColor('#FFD700', 'custom')" title="Gold"></button>
            </div>
          </div>
          <div
            ref="customPreviewEditor"
            class="preview-editor"
            contenteditable="true"
            @input="onCustomPreviewInput"
          ></div>
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="finalizeCustomSAR" :disabled="!canFinalizeCustomSar">
            Finalize and Add Custom SAR
          </button>
          <button class="btn" @click="closeCustomModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreviewModal" class="modal-overlay" @click="closePreviewModal">
      <div class="modal-content preview-modal" @click.stop>
        <div class="modal-header">
          <h3>Security Assurance Requirement Preview</h3>
          <button class="modal-close" type="button" @click="closePreviewModal">&times;</button>
        </div>
        <div class="preview-modal-body docx-modal-body">
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

const escapeHtml = (value: string) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const formatAssuranceComponentLabel = (componentId: string, componentName?: string) => {
  const uppercaseId = componentId.toUpperCase()
  const trimmedName = componentName?.trim()
  return trimmedName ? `${uppercaseId} : ${trimmedName}` : uppercaseId
}

const formatComponentHeading = (componentId: string, componentName?: string) => {
  const uppercaseId = componentId.toUpperCase()
  const trimmedName = componentName?.trim()
  return trimmedName ? `${uppercaseId} – ${trimmedName}` : uppercaseId
}

const formatClassHeading = (className: string, classCode: string) => {
  const trimmed = className.trim()
  if (!trimmed) {
    return classCode
  }

  const colonIndex = trimmed.indexOf(':')
  if (colonIndex !== -1) {
    const descriptor = trimmed.slice(colonIndex + 1).trim()
    if (descriptor) {
      return `${descriptor} (${classCode})`
    }
  }

  return `${trimmed} (${classCode})`
}

const formatAssuranceComponent = (sar: SarEntry) =>
  formatAssuranceComponentLabel(sar.componentId, sar.componentName)

// Modal state
const showAddModal = ref(false)
const showCustomModal = ref(false)
const showPreviewModal = ref(false)
const editingMode = ref<SarSource | null>(null)
const editingSarId = ref<number | null>(null)

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

// Editors
const previewEditor = ref<HTMLDivElement | null>(null)
const customPreviewEditor = ref<HTMLDivElement | null>(null)
const showColorPicker = ref(false)
const showCustomColorPicker = ref(false)

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

// Preview modal state
const previewLoading = ref(false)
const previewError = ref('')
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const generatedDocxPath = ref('')

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

// Predefined template for SAR preview
const getSarTemplate = (ealLevel: string) => {
  const escapedEal = escapeHtml(ealLevel)
  return `
<h4>5. SECURITY REQUIREMENTS</h4>
<h4>5.2 SECURITY ASSURANCE REQUIREMENTS</h4>
<p>The development and the evaluation of the TOE shall be done in accordance to the following security assurance requirements: <code>${escapedEal}</code> as specified in Part 5 of the Common Criteria.</p>
<p>No operations are applied to the assurance components.</p>
<p>The TOE shall meet the following security assurance requirements:</p>
`
}

const buildSarTableHtml = (
  classOrder: string[],
  groups: Record<string, { className: string; sars: SarEntry[] }>
) => {
  let rowsHtml = ''

  if (classOrder.length === 0) {
    rowsHtml += `
      <tr>
        <td colspan="2" class="sar-preview-table__empty">No Security Assurance Requirements selected.</td>
      </tr>
    `
  } else {
    classOrder.forEach(classCode => {
      const classData = groups[classCode]
      if (!classData) {
        return
      }

      const sarEntries = classData.sars ?? []

      if (sarEntries.length === 0) {
        rowsHtml += `
          <tr>
            <td class="sar-preview-table__class-cell">${escapeHtml(classData.className)}</td>
            <td class="sar-preview-table__note">No assurance components recorded.</td>
          </tr>
        `
        return
      }

      sarEntries.forEach((sar, index) => {
        const componentLabel = escapeHtml(formatAssuranceComponentLabel(sar.componentId, sar.componentName))
        const classCell =
          index === 0
            ? `<td class="sar-preview-table__class-cell" rowspan="${sarEntries.length}">${escapeHtml(classData.className)}</td>`
            : ''

        rowsHtml += `
          <tr>
            ${classCell}
            <td class="sar-preview-table__component">${componentLabel}</td>
          </tr>
        `
      })
    })
  }

  return `
    <div class="sar-preview-table-wrapper">
      <table class="sar-preview-table">
        <thead>
          <tr>
            <th scope="col">SAR Class</th>
            <th scope="col">Assurance Components</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
    </div>
    <p class="sar-preview-table-caption">Table 7 Security Assurance Components</p>
  `
}

const buildSarSectionsHtml = (
  classOrder: string[],
  groups: Record<string, { className: string; sars: SarEntry[] }>
) => {
  if (classOrder.length === 0) {
    return '<p class="sar-preview-empty">No Security Assurance Requirements have been defined.</p>'
  }

  let html = ''
  let classIndex = 1

  classOrder.forEach(classCode => {
    const classData = groups[classCode]
    if (!classData) {
      return
    }

    const headingText = escapeHtml(formatClassHeading(classData.className, classCode))
    html += `
      <section class="sar-preview-class">
        <h5 class="sar-preview-section-heading">5.3.${classIndex} ${headingText}</h5>
    `

    if (!classData.sars.length) {
      html += '<p class="sar-preview-note">No assurance components documented for this class.</p>'
      html += '</section>'
      classIndex++
      return
    }

    classData.sars.forEach(sar => {
      const componentHeading = escapeHtml(formatComponentHeading(sar.componentId, sar.componentName))
      const content =
        sar.previewContent && sar.previewContent.trim().length > 0
          ? sar.previewContent
          : '<p class="sar-preview-note">No component details provided.</p>'

      html += `
        <div class="sar-preview-component">
          <p class="sar-preview-component__title">${componentHeading}</p>
          <div class="sar-preview-component__body">${content}</div>
        </div>
      `
    })

    html += '</section>'
    classIndex++
  })

  return html
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
  showColorPicker.value = false

  if (previewEditor.value) {
    previewEditor.value.innerHTML = ''
  }
}

const resetCustomModalState = () => {
  customClassInput.value = ''
  customComponentInput.value = ''
  customPreviewContent.value = ''
  showCustomColorPicker.value = false

  if (customPreviewEditor.value) {
    customPreviewEditor.value.innerHTML = ''
  }
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
    if (previewEditor.value) {
      previewEditor.value.innerHTML = ''
    }
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
    if (previewEditor.value) {
      previewEditor.value.innerHTML = ''
    }
    return
  }

  try {
    const componentData = components.value.filter(c => c.component === selectedComponent.value)
    let content = ''

    for (const item of componentData) {
      if (item.element && item.element_item) {
        content += `<p><strong>${item.element}</strong> ${item.element_item}</p>`

        try {
          const elementResponse = await api.get(`/element-lists/formatted/${item.element}`)
          if (elementResponse.data && elementResponse.data.items && elementResponse.data.items.length > 0) {
            elementResponse.data.items.forEach(subItem => {
              content += `<p style="margin-left: 20px;">${subItem}</p>`
            })
          }
        } catch (elementError) {
          console.log(`No sub-items found for element ${item.element}`)
        }
      }
    }

    previewContent.value = content

    if (previewEditor.value) {
      previewEditor.value.innerHTML = content
    }
  } catch (error) {
    console.error('Error building preview:', error)
  }
}

const onPreviewInput = (event: Event) => {
  const target = event.target as HTMLDivElement
  previewContent.value = target.innerHTML
}

const onCustomPreviewInput = (event: Event) => {
  const target = event.target as HTMLDivElement
  customPreviewContent.value = target.innerHTML
}

const formatText = (command: string, target: 'standard' | 'custom' = 'standard') => {
  const editor = target === 'standard' ? previewEditor.value : customPreviewEditor.value
  if (!editor) return
  editor.focus()
  document.execCommand(command, false, null)
}

const applyColor = (color: string, target: 'standard' | 'custom' = 'standard') => {
  const editor = target === 'standard' ? previewEditor.value : customPreviewEditor.value
  if (!editor) return
  editor.focus()
  document.execCommand('foreColor', false, color)
  if (target === 'standard') {
    showColorPicker.value = false
  } else {
    showCustomColorPicker.value = false
  }
}

const toggleColorPicker = (target: 'standard' | 'custom') => {
  if (target === 'standard') {
    showColorPicker.value = !showColorPicker.value
    if (showColorPicker.value) {
      showCustomColorPicker.value = false
    }
  } else {
    showCustomColorPicker.value = !showCustomColorPicker.value
    if (showCustomColorPicker.value) {
      showColorPicker.value = false
    }
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

  const entry: SarEntry = {
    id: editingMode.value === 'database' && editingSarId.value !== null ? editingSarId.value : nextSarId.value++,
    className: classMeta.display,
    classCode: classMeta.code,
    componentId: selectedComponent.value,
    componentName: selectedComponentObj.component_name,
    previewContent: previewContent.value,
    originalClass: selectedClass.value,
    source: 'database',
    metadata: {
      classLabel: classMeta.display
    }
  }

  // Check for duplicate component (not just class)
  const duplicateComponent = sarList.value.some(
    existing => 
      existing.classCode === entry.classCode && 
      existing.componentId.toUpperCase() === entry.componentId.toUpperCase() && 
      existing.id !== entry.id
  )

  if (duplicateComponent) {
    alert('This SAR component has already been added. Multiple components from the same class are allowed, but each component must be unique.')
    return
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

  const entry: SarEntry = {
    id: editingMode.value === 'custom' && editingSarId.value !== null ? editingSarId.value : nextSarId.value++,
    className: classMeta.display,
    classCode: classMeta.code,
    componentId: componentMeta.id,
    componentName: componentMeta.name,
    previewContent: customPreviewContent.value,
    originalClass: classMeta.raw,
    source: 'custom',
    metadata: {
      classLabel: classMeta.display,
      customClassInput: classMeta.raw,
      customComponentInput: componentMeta.display
    }
  }

  // Check for duplicate component (not just class)
  const duplicateComponent = sarList.value.some(
    existing => 
      existing.classCode === entry.classCode && 
      existing.componentId.toUpperCase() === entry.componentId.toUpperCase() && 
      existing.id !== entry.id
  )

  if (duplicateComponent) {
    alert('This SAR component has already been added. Multiple components from the same class are allowed, but each component must be unique.')
    return
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

const updatePreviewForAllSars = () => {
  const template = getSarTemplate(selectedEal.value)

  const groups: Record<string, { className: string; sars: SarEntry[] }> = {}
  const classOrder: string[] = []

  sarList.value.forEach(sar => {
    const key = sar.classCode || 'UNKNOWN'
    if (!groups[key]) {
      groups[key] = {
        className: sar.className || key,
        sars: []
      }
      classOrder.push(key)
    }
    groups[key].sars.push(sar)
  })

  const tableHtml = buildSarTableHtml(classOrder, groups)
  const sectionsHtml = buildSarSectionsHtml(classOrder, groups)

  selectedSarPreview.value = template + tableHtml + sectionsHtml
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

const openPreviewModal = async () => {
  updatePreviewForAllSars()
  
  // Clean up any previous preview
  cleanupDocx()
  
  previewError.value = ''
  showPreviewModal.value = true
  previewLoading.value = true

  try {
    const payload = {
      user_id: userToken.value,
      sar_html: selectedSarPreview.value,
      eal_level: selectedEal.value,
    }

    const response = await api.post('/sar/preview', payload)
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

const closePreviewModal = () => {
  showPreviewModal.value = false
  if (!previewLoading.value) {
    previewError.value = ''
  }
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

function cleanupDocx() {
  if (!generatedDocxPath.value || !userToken.value) return
  api.delete(`/sar/preview/${userToken.value}`).catch(() => {
    // Silently ignore cleanup errors
  })
  generatedDocxPath.value = ''
}

function handleBeforeUnload() {
  cleanupDocx()
}

function handlePageHide() {
  cleanupDocx()
}

onBeforeUnmount(() => {
  cleanupDocx()
  removeEventListeners()
})

function removeEventListeners() {
  if (typeof window === 'undefined') return
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
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
        return {
          ...item,
          source,
          classCode: deriveClassCodeForEntry({ ...item, source }),
          metadata
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

    selectedComponent.value = sar.componentId
    filteredUniqueComponents.value = [...uniqueComponents.value]
    previewContent.value = sar.previewContent
    await nextTick()
    if (previewEditor.value) {
      previewEditor.value.innerHTML = sar.previewContent
      previewEditor.value.focus()
    }
    searchDropdownVisible.value = false
  } else {
    resetCustomModalState()
    customClassInput.value = sar.metadata?.customClassInput ?? sar.className
    customComponentInput.value =
      sar.metadata?.customComponentInput ??
      (sar.componentName ? `${sar.componentId} - ${sar.componentName}` : sar.componentId)
    customPreviewContent.value = sar.previewContent

    showCustomModal.value = true
    await nextTick()
    if (customPreviewEditor.value) {
      customPreviewEditor.value.innerHTML = sar.previewContent
      customPreviewEditor.value.focus()
    }
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
    showColorPicker.value = false
    searchDropdownVisible.value = false
  }
})

watch(showCustomModal, value => {
  if (!value) {
    showCustomColorPicker.value = false
  }
})

onMounted(async () => {
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handlePageHide)
  }

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
</script>

<style scoped>
.sar-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  gap: 0;
}

.sar-table-section {
  min-height: 300px;
  flex: 1;
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--panel);
  display: flex;
  flex-direction: column;
}

.sar-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #374151;
  background: var(--bg-soft);
  border-radius: 8px 8px 0 0;
}

.sar-table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.eal-selector-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px;
  padding-left: 8px;
  border-left: 1px solid #374151;
}

.eal-selector-inline label {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}

.eal-select {
  padding: 6px 10px;
  background: var(--bg);
  border: 1px solid #374151;
  border-radius: 4px;
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.eal-select:hover {
  border-color: var(--primary);
}

.eal-select:focus {
  border-color: var(--primary);
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

.sar-preview-section {
  flex: 1;
  min-height: 300px;
  border: 1px solid #374151;
  border-radius: 0 0 8px 8px;
  border-top: none;
  background: var(--panel);
  display: flex;
  flex-direction: column;
}

.sar-preview-header {
  padding: 16px 20px;
  border-bottom: 1px solid #374151;
  background: var(--bg-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.sar-preview-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  flex: 1;
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

.sar-preview-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: var(--bg);
  border-radius: 0 0 8px 8px;
  line-height: 1.6;
}

.sar-preview-content :deep(h4) {
  color: var(--text-bright);
  margin-top: 0;
  margin-bottom: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 18px;
  font-weight: 600;
}

.sar-preview-content :deep(h5) {
  color: var(--text-bright);
  margin-top: 24px;
  margin-bottom: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 16px;
  font-weight: 600;
}

.sar-preview-content :deep(h6) {
  color: var(--text-bright);
  margin-top: 20px;
  margin-bottom: 10px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: 600;
}

.sar-preview-content :deep(p) {
  margin-bottom: 12px;
  color: var(--text);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  line-height: 1.6;
}

.sar-preview-content :deep(strong) {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-weight: 600;
  color: var(--text-bright);
}

.sar-preview-content :deep(em) {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-style: italic;
}

.sar-preview-content :deep(.sar-preview-table-wrapper) {
  margin-top: 16px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  overflow: hidden;
}

.sar-preview-content :deep(.sar-preview-table) {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  color: #1F2937;
}

.sar-preview-content :deep(.sar-preview-table thead th) {
  background: #1F2937;
  color: #F9FAFB;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.sar-preview-content :deep(.sar-preview-table tbody td) {
  padding: 12px 16px;
  border-top: 1px solid #E5E7EB;
  background: transparent;
  color: #1F2937;
  vertical-align: top;
}

.sar-preview-content :deep(.sar-preview-table tbody tr:nth-child(even) td) {
  background: #F3F4F6;
}

.sar-preview-content :deep(.sar-preview-table__class-cell) {
  font-weight: 600;
  width: 36%;
}

.sar-preview-content :deep(.sar-preview-table__component) {
  width: 64%;
}

.sar-preview-content :deep(.sar-preview-table__empty) {
  padding: 20px 16px;
  text-align: center;
  font-style: italic;
  color: #4B5563;
  background: #F9FAFB;
}

.sar-preview-content :deep(.sar-preview-table__note) {
  font-style: italic;
  color: #4B5563;
}

.sar-preview-content :deep(.sar-preview-table-caption) {
  text-align: center;
  font-size: 12px;
  font-style: italic;
  color: var(--text-muted);
  margin-top: 8px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.sar-preview-content :deep(.sar-preview-class) {
  margin-top: 24px;
}

.sar-preview-content :deep(.sar-preview-section-heading) {
  margin: 0 0 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-bright);
}

.sar-preview-content :deep(.sar-preview-note),
.sar-preview-content :deep(.sar-preview-empty) {
  font-style: italic;
  color: #9CA3AF;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
}

.sar-preview-content :deep(.sar-preview-note) {
  margin-left: 16px;
}

.sar-preview-content :deep(.sar-preview-component) {
  margin-bottom: 16px;
}

.sar-preview-content :deep(.sar-preview-component__title) {
  margin: 12px 0 4px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-bright);
}

.sar-preview-content :deep(.sar-preview-component__body) {
  margin-left: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
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

/* Preview Modal Styles */
.preview-modal {
  padding: 0;
  display: flex;
  flex-direction: column;
  max-width: 960px;
  width: 95vw;
  max-height: 90vh;
  overflow: hidden;
}

.preview-modal .modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #374151;
  background: var(--bg-soft);
}

.preview-modal-body {
  flex: 1;
  overflow: auto;
  background: var(--bg);
}

.docx-modal-body {
  padding: 20px;
  background: #525659;
  overflow: auto;
}

.docx-preview-shell {
  position: relative;
  min-height: 400px;
  max-width: 900px;
  margin: 0 auto;
}

.docx-preview-container {
  background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.docx-preview-container.hidden {
  display: none;
}

.modal-status {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--text);
  font-size: 16px;
}

.modal-status.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 10;
  color: white;
}

.modal-error {
  padding: 20px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c00;
  text-align: center;
}
</style>