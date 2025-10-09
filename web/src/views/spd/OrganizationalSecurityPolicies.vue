<template>
  <div class="spd-page">
    <div class="card spd-menubar">
      <div class="spd-menubar-left">
        <h1>Organisational Security Policies</h1>
        <span class="menubar-subtitle">
          Write the set of security rules, procedures, or guidelines imposed by an organization on the operational environment of a Target of Evaluation (TOE), which is the product or system being evaluated.
        </span>
      </div>
      <div class="spd-actions">
        <button class="btn primary" type="button" @click="openAddModal">Add</button>
        <button class="btn" type="button" @click="openEditModal" :disabled="!selectedIdExists">Edit</button>
        <button class="btn danger" type="button" @click="removeSelected" :disabled="!selectedIdExists">Remove</button>
        <button class="btn info" type="button" @click="openPreviewModal">
          Preview
        </button>
      </div>
    </div>

    <div class="card spd-table-card">
      <div class="spd-table-header">
        <h2>Organisational Security Policies</h2>
      </div>
      <div class="spd-table-container">
        <table class="spd-table">
          <thead>
            <tr>
              <th>OSP</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in items" :key="entry.id" :class="{ selected: entry.id === selectedId }" @click="selectEntry(entry.id)">
              <td>{{ entry.title }}</td>
              <td>
                <div class="rich-text-preview" v-html="entry.description"></div>
              </td>
            </tr>
            <tr v-if="!items.length">
              <td class="no-data" colspan="2">No organizational security policies have been added yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="modal-close" type="button" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <label class="modal-label" for="policy-name">Organisational Security Policy</label>
          <input
            id="policy-name"
            v-model="form.title"
            class="modal-input"
            type="text"
            placeholder="Insert Organisational Security Policy"
          />

          <label class="modal-label" for="policy-description">Description</label>
          <RichTextEditor
            id="policy-description"
            v-model="form.description"
            placeholder="Describe the policy"
            min-height="240px"
          />

          <p v-if="validationError" class="validation-error">{{ validationError }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn" type="button" @click="closeModal">Cancel</button>
          <button class="btn primary" type="button" @click="finalizeEntry">
            {{ primaryButtonLabel }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content docx-modal" @click.stop>
        <div class="modal-header">
          <h3>Security Problem Definition Preview</h3>
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
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { renderAsync } from 'docx-preview'
import RichTextEditor from '../../components/RichTextEditor.vue'
import api from '../../services/api'
import {
  sessionService,
  type AssumptionsSessionData,
  type OspSessionData,
  type SpdEntry,
  type ThreatsSessionData,
} from '../../services/sessionService'
import { buildSecurityProblemDefinitionHtml } from '../../utils/spdPreview'

const items = ref<SpdEntry[]>([])
const selectedId = ref<number | null>(null)
const nextId = ref(1)
const showModal = ref(false)
const validationError = ref('')
const form = reactive({
  title: '',
  description: '',
})
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const showPreviewModal = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const docxPreviewContainer = ref<HTMLDivElement | null>(null)
const generatedDocxPath = ref<string | null>(null)
const userToken = sessionService.getUserToken()

const modalTitle = computed(() =>
  isEditing.value ? 'Edit Organisational Security Policy' : 'Insert Organisational Security Policy'
)
const primaryButtonLabel = computed(() =>
  isEditing.value ? 'Save Changes' : 'Finalize and Add Policy'
)
const selectedIdExists = computed(() => selectedId.value !== null)

function loadSessionData() {
  const data: OspSessionData | null = sessionService.loadOspData()
  if (data) {
    items.value = Array.isArray(data.items) ? data.items : []
    nextId.value = typeof data.nextId === 'number' ? data.nextId : items.value.length + 1
  }
}

function persistSession() {
  sessionService.saveOspData([...items.value], nextId.value)
}

function resetForm() {
  form.title = ''
  form.description = ''
  validationError.value = ''
}

function openAddModal() {
  isEditing.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

function openEditModal() {
  if (selectedId.value === null) return
  const entry = items.value.find(item => item.id === selectedId.value)
  if (!entry) return
  isEditing.value = true
  editingId.value = entry.id
  form.title = entry.title
  form.description = entry.description
  validationError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  validationError.value = ''
}

function finalizeEntry() {
  if (!form.title.trim()) {
    validationError.value = 'Policy name is required.'
    return
  }

  if (isEditing.value && editingId.value !== null) {
    const index = items.value.findIndex(item => item.id === editingId.value)
    if (index !== -1) {
      items.value[index] = {
        ...items.value[index],
        title: form.title.trim(),
        description: form.description,
      }
      selectedId.value = editingId.value
    }
  } else {
    const newEntry: SpdEntry = {
      id: nextId.value++,
      title: form.title.trim(),
      description: form.description,
    }
    items.value.push(newEntry)
    selectedId.value = newEntry.id
  }

  persistSession()
  closeModal()
}

function selectEntry(id: number) {
  selectedId.value = id
}

function removeSelected() {
  if (selectedId.value === null) return
  const entry = items.value.find(item => item.id === selectedId.value)
  if (!entry) return
  const confirmed = window.confirm(`Remove policy "${entry.title}"?`)
  if (!confirmed) return

  items.value = items.value.filter(item => item.id !== entry.id)
  selectedId.value = items.value.length ? items.value[0].id : null
  persistSession()
}

function closePreviewModal() {
  showPreviewModal.value = false
  previewError.value = ''
  cleanupDocx()
}

async function openPreviewModal() {
  previewError.value = ''
  previewLoading.value = true
  showPreviewModal.value = true

  await nextTick()

  cleanupDocx()

  const assumptionsData: AssumptionsSessionData | null = sessionService.loadAssumptionsData()
  const threatsData: ThreatsSessionData | null = sessionService.loadThreatsData()

  const html = buildSecurityProblemDefinitionHtml({
    assumptions: assumptionsData?.items ?? [],
    threats: threatsData?.items ?? [],
    osp: items.value,
  })

  try {
    const response = await api.post('/spd/preview', {
      user_id: userToken,
      html_content: html,
    })
    const path: string | undefined = response.data?.path
    if (!path) {
      throw new Error('Preview generation did not return a document path.')
    }
    generatedDocxPath.value = path
    await nextTick()
    await renderDocxPreview(path)
  } catch (error: any) {
    previewError.value = error?.response?.data?.detail || error?.message || 'Unable to generate preview.'
  } finally {
    previewLoading.value = false
  }
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
    previewError.value = error?.message || 'Failed to render DOCX preview.'
  }
}

function cleanupDocx(keepalive = false) {
  if (!generatedDocxPath.value) return
  const url = api.getUri({ url: `/spd/preview/${userToken}` })
  fetch(url, { method: 'DELETE', keepalive }).catch(() => undefined)
  generatedDocxPath.value = null
}

onMounted(() => {
  loadSessionData()
})

onBeforeUnmount(() => {
  cleanupDocx(true)
})
</script>

<style scoped>
.spd-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.spd-menubar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.spd-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  max-width: 720px;
  line-height: 1.5;
}

.spd-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 18px;
  border-radius: 8px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn:hover:not(:disabled) {
  background: #374151;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: var(--primary);
  border-color: #2563eb;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn.danger {
  background: #7f1d1d;
  border-color: #b91c1c;
  color: #fecaca;
}

.btn.danger:hover:not(:disabled) {
  background: #991b1b;
}

.btn.info {
  background: #0f172a;
  border-color: #2563eb;
  color: #bfdbfe;
}

.btn.info:hover:not(:disabled) {
  background: #1e293b;
}

.card {
  padding: 24px;
}

.spd-table-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.spd-table-header h2 {
  margin: 0;
}

.spd-table-container {
  overflow-x: auto;
}

.spd-table {
  width: 100%;
  border-collapse: collapse;
}

.spd-table th,
.spd-table td {
  border: 1px solid #374151;
  padding: 12px 16px;
  text-align: left;
  vertical-align: top;
}

.spd-table tbody tr {
  cursor: pointer;
  transition: background 0.2s;
}

.spd-table tbody tr:hover {
  background: var(--bg-soft);
}

.spd-table tbody tr.selected {
  background: rgba(37, 99, 235, 0.25);
}

.no-data {
  text-align: center;
  color: var(--muted);
}

.rich-text-preview :deep(p) {
  margin: 0 0 8px;
}

.rich-text-preview :deep(ul),
.rich-text-preview :deep(ol) {
  margin: 0 0 8px 20px;
  padding-left: 20px;
}

.rich-text-preview :deep(li) {
  margin-bottom: 4px;
}

.rich-text-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
}

.rich-text-preview :deep(th),
.rich-text-preview :deep(td) {
  border: 1px solid #4b5563;
  padding: 6px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.85);
  z-index: 50;
  padding: 16px;
}

.modal-content {
  background: var(--panel);
  border-radius: 12px;
  padding: 24px;
  width: min(720px, 95vw);
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
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
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-label {
  font-weight: 600;
  color: var(--text);
}

.modal-input {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
}

.validation-error {
  color: #fca5a5;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.docx-modal {
  width: min(900px, 95vw);
  max-height: 90vh;
  overflow: hidden;
}

.docx-modal-body {
  position: relative;
  min-height: 420px;
  border: 1px solid #374151;
  border-radius: 8px;
  background: #0f172a;
  padding: 0;
  overflow: hidden;
}

.docx-preview-shell {
  flex: 1;
  overflow: auto;
  padding: 24px;
  background: #d1d5db;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100%;
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

.modal-status {
  padding: 24px;
  text-align: center;
  color: var(--muted);
}

.modal-status.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.85);
  z-index: 10;
}

.modal-error {
  padding: 24px;
  text-align: center;
  color: #f87171;
}
</style>
