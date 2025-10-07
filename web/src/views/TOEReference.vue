<template>
  <div class="toe-reference-page">
    <div class="card toe-reference-menubar">
      <div class="toe-reference-menubar-left">
        <h1>Target of Evaluation (TOE) Reference</h1>
        <span class="menubar-subtitle">Please describe the Target of Evaluation references</span>
      </div>
    </div>

    <div class="card toe-reference-body">
      <form class="toe-reference-form">
        <div class="form-group">
          <label for="toeName">TOE Name:</label>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeName')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeName')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeName')"><u>U</u></button>
          </div>
          <div
            ref="toeNameEditor"
            class="wysiwyg-editor"
            contenteditable="true"
            @input="onToeNameInput"
            placeholder="Enter TOE Name"
          ></div>
        </div>

        <div class="form-group">
          <label for="toeVersion">TOE Version:</label>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeVersion')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeVersion')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeVersion')"><u>U</u></button>
          </div>
          <div
            ref="toeVersionEditor"
            class="wysiwyg-editor"
            contenteditable="true"
            @input="onToeVersionInput"
            placeholder="Enter TOE Version"
          ></div>
        </div>

        <div class="form-group">
          <label for="toeIdentification">TOE Identification:</label>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeIdentification')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeIdentification')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeIdentification')"><u>U</u></button>
          </div>
          <div
            ref="toeIdentificationEditor"
            class="wysiwyg-editor"
            contenteditable="true"
            @input="onToeIdentificationInput"
            placeholder="Enter TOE Identification"
          ></div>
        </div>

        <div class="form-group">
          <label for="toeType">TOE Type:</label>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeType')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeType')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeType')"><u>U</u></button>
          </div>
          <div
            ref="toeTypeEditor"
            class="wysiwyg-editor"
            contenteditable="true"
            @input="onToeTypeInput"
            placeholder="Enter TOE Type"
          ></div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { sessionService } from '../services/sessionService'

const toeNameEditor = ref<HTMLDivElement | null>(null)
const toeVersionEditor = ref<HTMLDivElement | null>(null)
const toeIdentificationEditor = ref<HTMLDivElement | null>(null)
const toeTypeEditor = ref<HTMLDivElement | null>(null)

const form = ref({
  toeName: '',
  toeVersion: '',
  toeIdentification: '',
  toeType: ''
})

function formatText(command: string, editorName: string) {
  document.execCommand(command, false)
  
  // Trigger input event to save
  switch(editorName) {
    case 'toeName':
      onToeNameInput()
      break
    case 'toeVersion':
      onToeVersionInput()
      break
    case 'toeIdentification':
      onToeIdentificationInput()
      break
    case 'toeType':
      onToeTypeInput()
      break
  }
}

function onToeNameInput() {
  if (toeNameEditor.value) {
    form.value.toeName = toeNameEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeVersionInput() {
  if (toeVersionEditor.value) {
    form.value.toeVersion = toeVersionEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeIdentificationInput() {
  if (toeIdentificationEditor.value) {
    form.value.toeIdentification = toeIdentificationEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeTypeInput() {
  if (toeTypeEditor.value) {
    form.value.toeType = toeTypeEditor.value.innerHTML
    saveSessionData()
  }
}

function saveSessionData() {
  sessionService.saveTOEReferenceData({
    toeName: form.value.toeName,
    toeVersion: form.value.toeVersion,
    toeIdentification: form.value.toeIdentification,
    toeType: form.value.toeType
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEReferenceData()
  if (data) {
    form.value.toeName = data.toeName
    form.value.toeVersion = data.toeVersion
    form.value.toeIdentification = data.toeIdentification
    form.value.toeType = data.toeType
    
    if (toeNameEditor.value) toeNameEditor.value.innerHTML = data.toeName
    if (toeVersionEditor.value) toeVersionEditor.value.innerHTML = data.toeVersion
    if (toeIdentificationEditor.value) toeIdentificationEditor.value.innerHTML = data.toeIdentification
    if (toeTypeEditor.value) toeTypeEditor.value.innerHTML = data.toeType
  }
}

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.toe-reference-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toe-reference-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toe-reference-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.toe-reference-body {
  padding: 24px;
}

.toe-reference-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 900px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text);
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
  min-height: 80px;
  padding: 12px;
  border: 1px solid #374151;
  border-radius: 0 0 8px 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
  overflow-y: auto;
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
