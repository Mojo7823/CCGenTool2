<template>
  <div class="toe-overview-page">
    <div class="card toe-overview-menubar">
      <div class="toe-overview-menubar-left">
        <h1>TOE Overview</h1>
        <span class="menubar-subtitle">Please describe your TOE and its features</span>
      </div>
    </div>

    <div class="card toe-overview-body">
      <form class="toe-overview-form">
        <div class="form-section">
          <h3>TOE Overview</h3>
          <p class="section-description">Please describe your TOE in short sentence (~100 words)</p>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeOverview')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeOverview')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeOverview')"><u>U</u></button>
          </div>
          <div
            ref="toeOverviewEditor"
            class="wysiwyg-editor"
            contenteditable="true"
            @input="onToeOverviewInput"
            placeholder="Enter TOE Overview (~100 words)"
          ></div>
        </div>

        <div class="form-section">
          <h3>TOE Type</h3>
          <p class="section-description">Please describe your TOE Type (What kind of device, its function, and its features), Short description (~200 Words)</p>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeType')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeType')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeType')"><u>U</u></button>
          </div>
          <div
            ref="toeTypeEditor"
            class="wysiwyg-editor large"
            contenteditable="true"
            @input="onToeTypeInput"
            placeholder="Enter TOE Type description (~200 words)"
          ></div>
        </div>

        <div class="form-section">
          <h3>TOE Usage</h3>
          <p class="section-description">Please describe how your TOE will be used and its intended environment</p>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeUsage')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeUsage')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeUsage')"><u>U</u></button>
          </div>
          <div
            ref="toeUsageEditor"
            class="wysiwyg-editor large"
            contenteditable="true"
            @input="onToeUsageInput"
            placeholder="Enter TOE Usage description"
          ></div>
        </div>

        <div class="form-section">
          <h3>TOE Major Security Features</h3>
          <p class="section-description">Please describe what security features that your TOE have (Firewall, Security Management, Encryption, etc)</p>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeMajorSecurityFeatures')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeMajorSecurityFeatures')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeMajorSecurityFeatures')"><u>U</u></button>
          </div>
          <div
            ref="toeMajorSecurityFeaturesEditor"
            class="wysiwyg-editor large"
            contenteditable="true"
            @input="onToeMajorSecurityFeaturesInput"
            placeholder="Enter TOE Major Security Features"
          ></div>
        </div>

        <div class="form-section">
          <h3>Non-TOE Hardware/Software/Firmware</h3>
          <p class="section-description">Please describe what Hardware/Software/Firmware that will be excluded as TOE (Excluded for evaluation)</p>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'nonToeHardwareSoftwareFirmware')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'nonToeHardwareSoftwareFirmware')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'nonToeHardwareSoftwareFirmware')"><u>U</u></button>
          </div>
          <div
            ref="nonToeHardwareSoftwareFirmwareEditor"
            class="wysiwyg-editor large"
            contenteditable="true"
            @input="onNonToeHardwareSoftwareFirmwareInput"
            placeholder="Enter Non-TOE Hardware/Software/Firmware"
          ></div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { sessionService } from '../services/sessionService'

const toeOverviewEditor = ref<HTMLDivElement | null>(null)
const toeTypeEditor = ref<HTMLDivElement | null>(null)
const toeUsageEditor = ref<HTMLDivElement | null>(null)
const toeMajorSecurityFeaturesEditor = ref<HTMLDivElement | null>(null)
const nonToeHardwareSoftwareFirmwareEditor = ref<HTMLDivElement | null>(null)

const form = ref({
  toeOverview: '',
  toeType: '',
  toeUsage: '',
  toeMajorSecurityFeatures: '',
  nonToeHardwareSoftwareFirmware: ''
})

function formatText(command: string, editorName: string) {
  document.execCommand(command, false)
  
  // Trigger input event to save
  switch(editorName) {
    case 'toeOverview':
      onToeOverviewInput()
      break
    case 'toeType':
      onToeTypeInput()
      break
    case 'toeUsage':
      onToeUsageInput()
      break
    case 'toeMajorSecurityFeatures':
      onToeMajorSecurityFeaturesInput()
      break
    case 'nonToeHardwareSoftwareFirmware':
      onNonToeHardwareSoftwareFirmwareInput()
      break
  }
}

function onToeOverviewInput() {
  if (toeOverviewEditor.value) {
    form.value.toeOverview = toeOverviewEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeTypeInput() {
  if (toeTypeEditor.value) {
    form.value.toeType = toeTypeEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeUsageInput() {
  if (toeUsageEditor.value) {
    form.value.toeUsage = toeUsageEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeMajorSecurityFeaturesInput() {
  if (toeMajorSecurityFeaturesEditor.value) {
    form.value.toeMajorSecurityFeatures = toeMajorSecurityFeaturesEditor.value.innerHTML
    saveSessionData()
  }
}

function onNonToeHardwareSoftwareFirmwareInput() {
  if (nonToeHardwareSoftwareFirmwareEditor.value) {
    form.value.nonToeHardwareSoftwareFirmware = nonToeHardwareSoftwareFirmwareEditor.value.innerHTML
    saveSessionData()
  }
}

function saveSessionData() {
  sessionService.saveTOEOverviewData({
    toeOverview: form.value.toeOverview,
    toeType: form.value.toeType,
    toeUsage: form.value.toeUsage,
    toeMajorSecurityFeatures: form.value.toeMajorSecurityFeatures,
    nonToeHardwareSoftwareFirmware: form.value.nonToeHardwareSoftwareFirmware
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEOverviewData()
  if (data) {
    form.value.toeOverview = data.toeOverview
    form.value.toeType = data.toeType
    form.value.toeUsage = data.toeUsage
    form.value.toeMajorSecurityFeatures = data.toeMajorSecurityFeatures
    form.value.nonToeHardwareSoftwareFirmware = data.nonToeHardwareSoftwareFirmware
    
    if (toeOverviewEditor.value) toeOverviewEditor.value.innerHTML = data.toeOverview
    if (toeTypeEditor.value) toeTypeEditor.value.innerHTML = data.toeType
    if (toeUsageEditor.value) toeUsageEditor.value.innerHTML = data.toeUsage
    if (toeMajorSecurityFeaturesEditor.value) toeMajorSecurityFeaturesEditor.value.innerHTML = data.toeMajorSecurityFeatures
    if (nonToeHardwareSoftwareFirmwareEditor.value) nonToeHardwareSoftwareFirmwareEditor.value.innerHTML = data.nonToeHardwareSoftwareFirmware
  }
}

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.toe-overview-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toe-overview-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toe-overview-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.toe-overview-body {
  padding: 24px;
}

.toe-overview-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 1000px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-section h3 {
  margin: 0;
  color: var(--text);
  font-size: 18px;
}

.section-description {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.wysiwyg-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 8px 8px 0 0;
  flex-wrap: wrap;
}

.wysiwyg-toolbar .btn {
  padding: 6px 12px;
  min-width: auto;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.wysiwyg-toolbar .btn:hover {
  background: #4b5563;
}

.wysiwyg-editor {
  min-height: 100px;
  padding: 12px;
  border: 1px solid #374151;
  border-radius: 0 0 8px 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
  overflow-y: auto;
}

.wysiwyg-editor.large {
  min-height: 150px;
}

.wysiwyg-editor:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.wysiwyg-editor[contenteditable]:empty:before {
  content: attr(placeholder);
  color: #6b7280;
}
</style>
