<template>
  <div class="rich-text-editor">
    <label v-if="label" :for="id" class="editor-label">{{ label }}</label>
    <div class="toolbar" v-if="showToolbar">
      <button type="button" class="btn" @click="applyCommand('bold')" title="Bold"><strong>B</strong></button>
      <button type="button" class="btn" @click="applyCommand('italic')" title="Italic"><em>I</em></button>
      <button type="button" class="btn" @click="applyCommand('underline')" title="Underline"><u>U</u></button>
      <button type="button" class="btn" @click="applyCommand('insertUnorderedList')" title="Bullet list">• List</button>
      <button type="button" class="btn" @click="applyCommand('insertOrderedList')" title="Numbered list">1. List</button>
      <button type="button" class="btn" @click="applyCommand('undo')" title="Undo">↺</button>
      <button type="button" class="btn" @click="applyCommand('redo')" title="Redo">↻</button>
    </div>
    <div
      :id="id"
      ref="editor"
      class="editor"
      contenteditable="true"
      :data-placeholder="placeholder"
      @input="onInput"
      @blur="emitInput"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  id: { type: String, default: '' },
  showToolbar: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const editor = ref<HTMLDivElement | null>(null)
let isSettingContent = false

function emitInput() {
  if (!editor.value) return
  const value = editor.value.innerHTML
  emit('update:modelValue', value === '<br>' ? '' : value)
}

function onInput() {
  if (isSettingContent) return
  emitInput()
}

function applyCommand(command: string) {
  document.execCommand(command, false, undefined)
  emitInput()
}

onMounted(() => {
  if (editor.value && props.modelValue) {
    isSettingContent = true
    editor.value.innerHTML = props.modelValue
    isSettingContent = false
  }
})

watch(
  () => props.modelValue,
  value => {
    if (!editor.value) return
    if (editor.value.innerHTML === value || (editor.value.innerHTML === '<br>' && !value)) {
      return
    }
    isSettingContent = true
    editor.value.innerHTML = value || ''
    isSettingContent = false
  }
)
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-label {
  font-weight: 600;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.editor {
  min-height: 140px;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.35);
  transition: border-color 0.2s ease;
}

.editor:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25);
}

.editor:empty::before {
  content: attr(data-placeholder);
  color: var(--muted);
}
</style>
