<template>
  <div class="toe-description-page">
    <div class="card toe-description-menubar">
      <div class="toe-description-menubar-left">
        <h1>Target of Evaluation (TOE) Description</h1>
        <span class="menubar-subtitle">Please describe your Target of Evaluation (TOE) Physical boundary scope and Logical boundary scope</span>
      </div>
    </div>

    <div class="card toe-description-body">
      <form class="toe-description-form">
        <div class="form-section">
          <h3>TOE Physical Scope:</h3>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toePhysicalScope')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toePhysicalScope')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toePhysicalScope')"><u>U</u></button>
          </div>
          <div
            ref="toePhysicalScopeEditor"
            class="wysiwyg-editor large"
            contenteditable="true"
            @input="onToePhysicalScopeInput"
            placeholder="Enter TOE Physical Scope description"
          ></div>
        </div>

        <div class="form-section">
          <h3>TOE Logical Scope:</h3>
          <div class="wysiwyg-toolbar">
            <button type="button" class="btn" @click="formatText('bold', 'toeLogicalScope')"><strong>B</strong></button>
            <button type="button" class="btn" @click="formatText('italic', 'toeLogicalScope')"><em>I</em></button>
            <button type="button" class="btn" @click="formatText('underline', 'toeLogicalScope')"><u>U</u></button>
          </div>
          <div
            ref="toeLogicalScopeEditor"
            class="wysiwyg-editor large"
            contenteditable="true"
            @input="onToeLogicalScopeInput"
            placeholder="Enter TOE Logical Scope description"
          ></div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { sessionService } from '../services/sessionService'

const toePhysicalScopeEditor = ref<HTMLDivElement | null>(null)
const toeLogicalScopeEditor = ref<HTMLDivElement | null>(null)

const form = ref({
  toePhysicalScope: '',
  toeLogicalScope: ''
})

function formatText(command: string, editorName: string) {
  document.execCommand(command, false)
  
  // Trigger input event to save
  switch(editorName) {
    case 'toePhysicalScope':
      onToePhysicalScopeInput()
      break
    case 'toeLogicalScope':
      onToeLogicalScopeInput()
      break
  }
}

function onToePhysicalScopeInput() {
  if (toePhysicalScopeEditor.value) {
    form.value.toePhysicalScope = toePhysicalScopeEditor.value.innerHTML
    saveSessionData()
  }
}

function onToeLogicalScopeInput() {
  if (toeLogicalScopeEditor.value) {
    form.value.toeLogicalScope = toeLogicalScopeEditor.value.innerHTML
    saveSessionData()
  }
}

function saveSessionData() {
  sessionService.saveTOEDescriptionData({
    toePhysicalScope: form.value.toePhysicalScope,
    toeLogicalScope: form.value.toeLogicalScope
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEDescriptionData()
  if (data) {
    form.value.toePhysicalScope = data.toePhysicalScope
    form.value.toeLogicalScope = data.toeLogicalScope
    
    if (toePhysicalScopeEditor.value) toePhysicalScopeEditor.value.innerHTML = data.toePhysicalScope
    if (toeLogicalScopeEditor.value) toeLogicalScopeEditor.value.innerHTML = data.toeLogicalScope
  }
}

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.toe-description-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toe-description-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toe-description-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.toe-description-body {
  padding: 24px;
}

.toe-description-form {
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
  min-height: 150px;
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
  min-height: 200px;
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
