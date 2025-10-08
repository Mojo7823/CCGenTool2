<template>
  <div class="spd-section-page">
    <div class="card spd-menubar">
      <div class="spd-menubar-left">
        <h1>{{ config.title }}</h1>
        <p class="menubar-subtitle">{{ config.subtitle }}</p>
      </div>
      <div class="menubar-actions">
        <button class="btn primary" type="button" @click="openAddModal">Add</button>
        <button class="btn" type="button" @click="openEditModal" :disabled="!selectedEntryId">Edit</button>
        <button class="btn danger" type="button" @click="removeEntry" :disabled="!selectedEntryId">Remove</button>
        <button class="btn" type="button" @click="openPreviewModal" :disabled="!canPreview">Preview</button>
      </div>
    </div>

    <div class="card spd-table-card">
      <table class="spd-table">
        <thead>
          <tr>
            <th>{{ config.tableLabel }}</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in entries"
            :key="entry.id"
            :class="{ selected: selectedEntryId === entry.id }"
            @click="selectEntry(entry.id)"
          >
            <td class="title-cell">{{ displayTitle(entry.title) }}</td>
            <td>
              <div class="description-cell" v-html="entry.description" />
            </td>
          </tr>
          <tr v-if="entries.length === 0">
            <td colspan="2" class="no-data">{{ config.emptyState }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showFormModal" class="modal-overlay" @click="closeFormModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="modal-close" type="button" @click="closeFormModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label :for="`${config.formId}-title`">{{ config.tableLabel }}</label>
            <input
              :id="`${config.formId}-title`"
              v-model="form.title"
              type="text"
              class="input"
              :placeholder="config.titlePlaceholder"
            />
          </div>
          <div class="form-group">
            <label :for="`${config.formId}-description`">Description</label>
            <RichTextEditor
              :id="`${config.formId}-description`"
              v-model="form.description"
              :placeholder="config.descriptionPlaceholder"
              min-height="220px"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn primary" type="button" @click="finalizeEntry" :disabled="!canSubmit">
            {{ finalizeButtonLabel }}
          </button>
          <button class="btn" type="button" @click="closeFormModal">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content docx-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ config.previewTitle }}</h3>
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
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { renderAsync } from 'docx-preview'
import api from '../../services/api'
import { sessionService, type SpdEntry } from '../../services/sessionService'
import RichTextEditor from '../../components/RichTextEditor.vue'
import { buildSpdSectionHtml, formatSpdEntryTitle, type SpdSectionKey } from '../../utils/spd'

interface SpdSectionConfig {
  title: string
  subtitle: string
  tableLabel: string
  emptyState: string
  addModalTitle: string
  editModalTitle: string
  finalizeLabel: string
  finalizeEditLabel: string
  previewTitle: string
  previewEndpoint: string
  cleanupEndpoint: (userId: string) => string
  optional: boolean
  formId: string
  titlePlaceholder: string
  descriptionPlaceholder: string
  load: () => SpdEntry[]
  save: (items: SpdEntry[]) => void
}

const props = defineProps<{ section: SpdSectionKey }>()

const configMap: Record<SpdSectionKey, SpdSectionConfig> = {
  assumptions: {
    title: 'Assumptions',
    subtitle:
      'Write the assumptions of the TOE. These assumptions include both practical realities in the development of the TOE security requirements and the essential environmental conditions on the use of the TOE.',
    tableLabel: 'Assumptions',
    emptyState: 'No assumptions have been added yet.',
    addModalTitle: 'Insert Assumptions',
    editModalTitle: 'Edit Assumptions',
    finalizeLabel: 'Finalize and Add Assumptions',
    finalizeEditLabel: 'Finalize and Update Assumptions',
    previewTitle: 'Assumptions Preview',
    previewEndpoint: '/spd/assumptions/preview',
    cleanupEndpoint: userId => `/spd/assumptions/preview/${userId}`,
    optional: false,
    formId: 'spd-assumptions',
    titlePlaceholder: 'Insert Assumptions',
    descriptionPlaceholder: 'Describe the assumption details',
    load: () => sessionService.loadSpdAssumptions(),
    save: (items: SpdEntry[]) => sessionService.saveSpdAssumptions(items),
  },
  threats: {
    title: 'Threats',
    subtitle: 'Write the threats addressed by the TOE and its environment.',
    tableLabel: 'Threats',
    emptyState: 'No threats have been added yet.',
    addModalTitle: 'Insert Threats',
    editModalTitle: 'Edit Threats',
    finalizeLabel: 'Finalize and Add Threats',
    finalizeEditLabel: 'Finalize and Update Threats',
    previewTitle: 'Threats Preview',
    previewEndpoint: '/spd/threats/preview',
    cleanupEndpoint: userId => `/spd/threats/preview/${userId}`,
    optional: false,
    formId: 'spd-threats',
    titlePlaceholder: 'Insert Threat',
    descriptionPlaceholder: 'Describe the threat details',
    load: () => sessionService.loadSpdThreats(),
    save: (items: SpdEntry[]) => sessionService.saveSpdThreats(items),
  },
  osp: {
    title: 'Organisational Security Policies',
    subtitle:
      'Write the set of security rules, procedures, or guidelines imposed by an organization on the operational environment of a Target of Evaluation (TOE), which is the product or system being evaluated.',
    tableLabel: 'OSP',
    emptyState: 'No organizational security policies have been added yet.',
    addModalTitle: 'Insert Organizational Security Policy',
    editModalTitle: 'Edit Organizational Security Policy',
    finalizeLabel: 'Finalize and Add OSP',
    finalizeEditLabel: 'Finalize and Update OSP',
    previewTitle: 'Organisational Security Policies Preview',
    previewEndpoint: '/spd/osp/preview',
    cleanupEndpoint: userId => `/spd/osp/preview/${userId}`,
    optional: true,
    formId: 'spd-osp',
    titlePlaceholder: 'Insert Organizational Security Policy',
    descriptionPlaceholder: 'Describe the organizational security policy',
    load: () => sessionService.loadSpdOsp(),
    save: (items: SpdEntry[]) => sessionService.saveSpdOsp(items),
  },
}

const config = computed(() => configMap[props.section])

const entries = ref<SpdEntry[]>([])
const selectedEntryId = ref<string | null>(null)
const showFormModal = ref(false)
const isEditing = ref(false)
const form = reactive({
  title: '',
  description: '',
})

const showPreviewModal = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const generatedDocxPath = ref<string | null>(null)
const hasGeneratedDocx = ref(false)
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const userToken = ref(sessionService.getUserToken())

const modalTitle = computed(() => (isEditing.value ? config.value.editModalTitle : config.value.addModalTitle))
const finalizeButtonLabel = computed(() => (isEditing.value ? config.value.finalizeEditLabel : config.value.finalizeLabel))

const canPreview = computed(() => {
  if (config.value.optional) {
    return true
  }
  return entries.value.length > 0
})

const canSubmit = computed(() => {
  const titleFilled = form.title.trim().length > 0
  const descriptionFilled = hasRichTextContent(form.description)
  return titleFilled && descriptionFilled
})

function hasRichTextContent(value: string): boolean {
  if (!value) {
    return false
  }
  const text = value.replace(/<[^>]*>/g, ' ').replace(/&nbsp;/g, ' ').trim()
  return text.length > 0
}

function displayTitle(title: string): string {
  return formatSpdEntryTitle(props.section, title) || '—'
}

function resetForm() {
  form.title = ''
  form.description = ''
}

function openAddModal() {
  resetForm()
  isEditing.value = false
  showFormModal.value = true
}

function openEditModal() {
  if (!selectedEntryId.value) {
    return
  }
  const entry = entries.value.find(item => item.id === selectedEntryId.value)
  if (!entry) {
    return
  }
  form.title = entry.title
  form.description = entry.description
  isEditing.value = true
  showFormModal.value = true
}

function closeFormModal() {
  showFormModal.value = false
  resetForm()
}

function selectEntry(id: string) {
  selectedEntryId.value = id
}

function generateEntryId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function finalizeEntry() {
  if (!canSubmit.value) {
    return
  }

  if (isEditing.value && selectedEntryId.value) {
    const index = entries.value.findIndex(item => item.id === selectedEntryId.value)
    if (index !== -1) {
      entries.value.splice(index, 1, {
        id: selectedEntryId.value,
        title: form.title.trim(),
        description: form.description,
      })
    }
  } else {
    entries.value.push({
      id: generateEntryId(),
      title: form.title.trim(),
      description: form.description,
    })
  }

  closeFormModal()
}

function removeEntry() {
  if (!selectedEntryId.value) {
    return
  }

  entries.value = entries.value.filter(item => item.id !== selectedEntryId.value)
  selectedEntryId.value = null
}

function saveEntries() {
  const snapshot = entries.value.map(entry => ({ ...entry }))
  config.value.save(snapshot)
}

function loadEntries() {
  const stored = config.value.load()
  entries.value = stored.map(entry => ({ ...entry }))
  selectedEntryId.value = null
}

function buildPreviewHtml(): string {
  return buildSpdSectionHtml(props.section, entries.value, { includeRootHeading: true })
}

async function renderDocxPreview(path: string) {
  if (!docxPreviewContainer.value) {
    return
  }

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
    hasGeneratedDocx.value = false
  }
}

const cleanupDocx = (keepalive = false) => {
  if (!userToken.value || !generatedDocxPath.value) {
    return
  }

  const url = api.getUri({ url: config.value.cleanupEndpoint(userToken.value) })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  generatedDocxPath.value = null
  hasGeneratedDocx.value = false
}

const handleBeforeUnload = () => cleanupDocx(true)
const handlePageHide = () => cleanupDocx(true)

function addPreviewListeners() {
  if (typeof window === 'undefined') {
    return
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('pagehide', handlePageHide)
}

function removePreviewListeners() {
  if (typeof window === 'undefined') {
    return
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('pagehide', handlePageHide)
}

async function openPreviewModal() {
  if (!canPreview.value) {
    return
  }

  const htmlContent = buildPreviewHtml()
  previewError.value = ''
  previewLoading.value = true
  showPreviewModal.value = true
  await nextTick()
  cleanupDocx()

  try {
    const payload = {
      user_id: userToken.value,
      html_content: htmlContent,
    }

    const response = await api.post(config.value.previewEndpoint, payload)
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

function closePreviewModal() {
  showPreviewModal.value = false
  cleanupDocx()
  if (!previewLoading.value) {
    previewError.value = ''
  }
}

watch(entries, saveEntries, { deep: true })

watch(
  () => props.section,
  () => {
    closeFormModal()
    closePreviewModal()
    loadEntries()
  }
)

onMounted(() => {
  userToken.value = sessionService.getUserToken()
  loadEntries()
  addPreviewListeners()
})

onBeforeUnmount(() => {
  cleanupDocx()
  removePreviewListeners()
})
</script>

<style scoped>
.spd-section-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.spd-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.spd-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
  margin-top: 4px;
}

.menubar-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.spd-table-card {
  padding: 0;
}

.spd-table {
  width: 100%;
  border-collapse: collapse;
}

.spd-table th,
.spd-table td {
  padding: 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  text-align: left;
  vertical-align: top;
}

.spd-table thead th {
  background-color: rgba(148, 163, 184, 0.08);
  font-weight: 600;
}

.spd-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.spd-table tbody tr:hover {
  background-color: rgba(148, 163, 184, 0.08);
}

.spd-table tbody tr.selected {
  background-color: rgba(59, 130, 246, 0.12);
}

.no-data {
  text-align: center;
  color: var(--muted);
  padding: 24px;
}

.title-cell {
  font-weight: 600;
  width: 32%;
}

.description-cell :deep(p) {
  margin: 0;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 1000;
}

.modal-content {
  background: var(--surface);
  border-radius: 12px;
  width: min(720px, 100%);
  max-height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.35);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.docx-modal {
  width: min(860px, 100%);
}

.docx-modal-body {
  padding: 0 24px 24px;
}

.docx-preview-shell {
  position: relative;
  min-height: 320px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.35);
}

.docx-preview-container {
  height: 480px;
  overflow: auto;
  background: rgba(15, 23, 42, 0.25);
}

.docx-preview-container.hidden {
  display: none;
}

.modal-status {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text);
}

.modal-status.overlay {
  background: rgba(15, 23, 42, 0.6);
}

.modal-error {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
  color: #f87171;
  background: rgba(15, 23, 42, 0.75);
  font-weight: 600;
}
</style>
