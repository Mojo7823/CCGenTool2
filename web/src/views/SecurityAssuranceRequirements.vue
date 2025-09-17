<template>
  <div class="sar-container">
    <h2>Security Assurance Requirements</h2>
    <p>Manage Security Assurance Requirements (SARs) for your Common Criteria evaluation.</p>
    
    <!-- SAR Table Section -->
    <div class="sar-table-section">
      <div class="sar-table-header">
        <h3>Security Assurance Requirements</h3>
        <div class="table-actions">
          <button class="btn primary" @click="openAddModal">Add SAR</button>
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
              <td>{{ formatClassLabel(sar.className) }}</td>
              <td>{{ formatComponentLabel(sar) }}</td>
            </tr>
            <tr v-if="sarList.length === 0">
              <td colspan="2" class="no-data">No SARs available yet. Import SAR data or enable creation to get started.</td>
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
    <div class="sar-preview-section" ref="previewSection">
      <div class="sar-preview-header">
        <h3>Security Assurance Requirement Preview</h3>
        <div class="eal-selector">
          <label for="ealLevel">Evaluation Assurance Level (EAL)</label>
          <select id="ealLevel" v-model="selectedEalLevel" class="input eal-select">
            <option v-for="option in ealOptions" :key="option" :value="option">{{ option }}</option>
          </select>
        </div>
      </div>
      <div class="sar-preview-content" v-html="selectedSarPreview"></div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
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

interface SarClassGroup {
  key: string
  code: string
  description: string
  displayLabel: string
  entries: SarEntry[]
}

const DEFAULT_EAL_LEVEL = 'EAL 1'
const ealOptions = ['EAL 1', 'EAL 2', 'EAL 3', 'EAL 4', 'EAL 5', 'EAL 6', 'EAL 7']

// Modal state
const showAddModal = ref(false)
const showCustomModal = ref(false)
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

// Custom SAR inputs
const customClassInput = ref('')
const customComponentInput = ref('')

// Table data
const sarList = ref<SarEntry[]>([])
const selectedSarId = ref<number | null>(null)
const selectedSarPreview = ref('')
const selectedEalLevel = ref<string>(DEFAULT_EAL_LEVEL)
const previewSection = ref<HTMLDivElement | null>(null)
const isResizing = ref(false)
const nextSarId = ref(1)

// Session management
const userToken = ref(sessionService.getUserToken())
let isRestoringSession = false

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

const parseClassLabelForDisplay = (label: string, fallbackCode?: string) => {
  const safeLabel = (label || '').trim()
  const fallback = (fallbackCode || '').trim().toUpperCase()
  let code = fallback
  let description = ''

  if (safeLabel) {
    const colonIndex = safeLabel.indexOf(':')
    if (colonIndex !== -1) {
      const rawCode = safeLabel.slice(0, colonIndex).trim()
      const rawDescription = safeLabel.slice(colonIndex + 1).trim()
      if (rawCode) {
        code = rawCode.toUpperCase()
      }
      description = rawDescription
    } else {
      if (!code) {
        code = safeLabel.toUpperCase()
      }
      if (safeLabel.toUpperCase() !== code) {
        description = safeLabel
      }
    }
  }

  if (!code) {
    code = 'CLASS'
  }

  return { code, description }
}

const formatClassLabel = (label: string) => {
  const { code, description } = parseClassLabelForDisplay(label)
  return description ? `${code} - ${description}` : code
}

const formatComponentLabel = (entry: SarEntry) => {
  const componentId = entry.componentId || '—'
  return entry.componentName ? `${componentId} : ${entry.componentName}` : componentId
}

const formatComponentHeading = (entry: SarEntry) => {
  const componentId = entry.componentId || 'Component'
  return entry.componentName ? `${componentId} – ${entry.componentName}` : componentId
}

const escapeHtml = (value: string) =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const buildSarClassGroups = (): SarClassGroup[] => {
  const groupMap = new Map<string, SarClassGroup>()
  const groups: SarClassGroup[] = []

  sarList.value.forEach(entry => {
    const classLabel = entry.metadata?.classLabel ?? entry.className ?? ''
    const { code, description } = parseClassLabelForDisplay(classLabel, entry.classCode)
    const key = code || entry.classCode || classLabel || `CLASS_${groups.length + 1}`

    if (!groupMap.has(key)) {
      const displayLabel = formatClassLabel(classLabel || code)
      const group: SarClassGroup = {
        key,
        code,
        description,
        displayLabel,
        entries: []
      }
      groupMap.set(key, group)
      groups.push(group)
    }

    const group = groupMap.get(key)
    if (group) {
      group.entries.push(entry)
    }
  })

  return groups
}

const buildPreviewTableHtml = (groups: SarClassGroup[]) => {
  if (!groups.length) {
    return ''
  }

  let tableHtml = '<div class="sar-preview-table-wrapper">'
  tableHtml += '<table class="sar-preview-table">'
  tableHtml += '<thead><tr><th>Requirement Class</th><th>Assurance Components</th></tr></thead>'
  tableHtml += '<tbody>'

  groups.forEach(group => {
    if (!group.entries.length) {
      return
    }

    const groupLabel = escapeHtml(group.displayLabel)

    group.entries.forEach((entry, index) => {
      const componentLabel = escapeHtml(formatComponentLabel(entry))
      tableHtml += '<tr>'
      if (index === 0) {
        tableHtml += `<td rowspan="${group.entries.length}">${groupLabel}</td>`
      }
      tableHtml += `<td>${componentLabel}</td>`
      tableHtml += '</tr>'
    })
  })

  tableHtml += '</tbody></table></div>'
  return tableHtml
}

const buildDetailedSectionHtml = (groups: SarClassGroup[], selectedId: number | null) => {
  if (!groups.length) {
    return ''
  }

  let detailHtml = '<h4>5.3 DETAILED SECURITY ASSURANCE REQUIREMENTS</h4>'

  groups.forEach((group, index) => {
    const headingTitle = group.description
      ? `${group.description} (${group.code})`
      : group.code
    detailHtml += `<h5>5.3.${index + 1} ${escapeHtml(headingTitle)}</h5>`

    group.entries.forEach(entry => {
      const heading = escapeHtml(formatComponentHeading(entry))
      const highlightClass = selectedId === entry.id ? ' selected' : ''
      const content = entry.previewContent && entry.previewContent.trim().length > 0
        ? entry.previewContent
        : '<p>No description provided.</p>'

      detailHtml += '<div class="sar-component-section">'
      detailHtml += `<p class="sar-component-heading${highlightClass}">[${heading}]</p>`
      detailHtml += `<div class="sar-component-content">${content}</div>`
      detailHtml += '</div>'
    })
  })

  return detailHtml
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
  filterSarData()
  searchDropdownVisible.value = true
}

const openSearchDropdown = () => {
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
  const ealLabel = selectedEalLevel.value || DEFAULT_EAL_LEVEL
  const groups = buildSarClassGroups()

  let previewHtml = '<h4>5.2 SECURITY ASSURANCE REQUIREMENTS</h4>'
  previewHtml += `
<p class="sar-intro-text">The development and the evaluation of the TOE shall be done in accordance to the following security assurance requirements: <span class="sar-eal-level">${escapeHtml(ealLabel)}</span> as specified in Part 5 of the Common Criteria. No operations are applied to the assurance components.</p>
`
  previewHtml += '<p class="sar-intro-text">The TOE shall meet the following security assurance requirements:</p>'

  if (!groups.length) {
    previewHtml += '<p class="sar-empty-note">No security assurance requirements have been added yet.</p>'
    selectedSarPreview.value = previewHtml
    return
  }

  previewHtml += buildPreviewTableHtml(groups)
  previewHtml += '<p class="sar-table-caption">Table 7 Security Assurance Components</p>'
  previewHtml += buildDetailedSectionHtml(groups, selectedSarId.value)

  selectedSarPreview.value = previewHtml
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
  sessionService.saveSarData(sarList.value, selectedSarId.value, nextSarId.value, selectedEalLevel.value)
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
    try {
      isRestoringSession = true
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
      selectedEalLevel.value = sessionData.ealLevel || DEFAULT_EAL_LEVEL
    } finally {
      isRestoringSession = false
    }

    console.log(`Loaded session data for user: ${sessionData.userToken}`)
  }
}

const clearSessionData = () => {
  if (confirm('Are you sure you want to clear all SAR data? This action cannot be undone.')) {
    sessionService.clearSarData()
    try {
      isRestoringSession = true
      sarList.value = []
      selectedSarId.value = null
      nextSarId.value = 1
      selectedEalLevel.value = DEFAULT_EAL_LEVEL
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

const startResize = (event: MouseEvent) => {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  event.preventDefault()
}

const handleResize = (event: MouseEvent) => {
  if (!isResizing.value) return

  const container = document.querySelector('.sar-container') as HTMLElement | null
  if (!container) return

  const rect = container.getBoundingClientRect()
  const newHeight = event.clientY - rect.top - 100

  if (newHeight > 150 && newHeight < window.innerHeight - 300) {
    const tableSection = document.querySelector('.sar-table-section') as HTMLElement | null
    if (tableSection) {
      tableSection.style.height = `${newHeight}px`
    }
  }
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

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

watch(selectedEalLevel, () => {
  updatePreviewForAllSars()
  saveSessionData()
})

onMounted(async () => {
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

  updatePreviewForAllSars()

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
  height: 45vh;
  border: 1px solid #374151;
  border-radius: 8px 8px 0 0;
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
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
}

.sar-preview-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  flex: 1 1 auto;
}

.eal-selector {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 200px;
}

.eal-selector label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.eal-select {
  min-width: 180px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 8px;
}

.sar-preview-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: var(--bg);
  border-radius: 0 0 8px 8px;
  line-height: 1.75;
}

.sar-preview-content h4 {
  color: var(--text-bright);
  margin-top: 0;
  margin-bottom: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 15pt;
  font-weight: 600;
}

.sar-preview-content h5 {
  color: var(--text-bright);
  margin-top: 24px;
  margin-bottom: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14pt;
  font-weight: 600;
}

.sar-preview-content h6 {
  color: var(--text-bright);
  margin-top: 20px;
  margin-bottom: 10px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13pt;
  font-weight: 600;
}

.sar-preview-content p {
  margin-bottom: 12px;
  color: var(--text);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 12pt;
  line-height: 1.75;
}

.sar-preview-content strong {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-weight: 600;
  color: var(--text-bright);
  font-size: 12pt;
}

.sar-preview-content em {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-style: italic;
}

.sar-intro-text {
  font-size: 12pt;
}

.sar-eal-level {
  color: var(--primary);
  font-weight: 700;
}

.sar-empty-note {
  font-style: italic;
  color: var(--text-muted);
  margin-top: 12px;
}

.sar-preview-table-wrapper {
  margin: 16px 0;
  border: 1px solid #374151;
  border-radius: 8px;
  overflow: hidden;
}

.sar-preview-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg);
}

.sar-preview-table th,
.sar-preview-table td {
  border: 1px solid #374151;
  padding: 10px 14px;
  vertical-align: top;
  font-size: 12pt;
  line-height: 1.7;
}

.sar-preview-table th {
  background: var(--bg-soft);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 11pt;
}

.sar-preview-table td:first-child {
  font-weight: 600;
  width: 45%;
}

.sar-table-caption {
  margin-top: 8px;
  font-style: italic;
  color: var(--text-muted);
  font-size: 11pt;
}

.sar-component-section {
  margin-top: 20px;
}

.sar-component-heading {
  font-size: 13pt;
  font-weight: 600;
  display: inline-block;
  padding: 6px 12px;
  background: rgba(59, 130, 246, 0.18);
  border-left: 4px solid var(--primary);
  border-radius: 4px;
  color: var(--text-bright);
}

.sar-component-heading.selected {
  background: var(--primary);
  color: #FFFFFF;
}

.sar-component-content {
  margin-top: 10px;
  padding-left: 14px;
  border-left: 3px solid rgba(59, 130, 246, 0.35);
}

.sar-component-content p {
  font-size: 12pt;
  line-height: 1.75;
}

.sar-component-content strong {
  font-size: 12pt;
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
  font-size: 12pt;
  line-height: 1.75;
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
  font-size: 12pt;
  line-height: 1.75;
  margin-bottom: 12px;
}

.preview-editor strong {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-weight: 600;
  color: var(--text-bright);
  font-size: 12pt;
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
</style>