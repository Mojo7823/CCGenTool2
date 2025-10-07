<template>
  <div class="rich-text-editor" :class="{ focused: isFocused }">
    <div class="editor-toolbar">
      <button type="button" class="btn" @click="applyFormat('bold')" title="Bold"><strong>B</strong></button>
      <button type="button" class="btn" @click="applyFormat('italic')" title="Italic"><em>I</em></button>
      <button type="button" class="btn" @click="applyFormat('underline')" title="Underline"><u>U</u></button>
      <button type="button" class="btn" @click="toggleList" title="Bullet list">• List</button>
      <button type="button" class="btn" @click="clearFormatting" title="Clear formatting">Clear</button>
    </div>
    <div
      ref="editor"
      class="editor-area"
      contenteditable="true"
      :data-placeholder="placeholder"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'blur'): void
}>()

const editor = ref<HTMLDivElement | null>(null)
const isFocused = ref(false)

function sanitizeHtml(value: string): string {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed) return ''
  return value
}

function syncContent(value: string) {
  if (!editor.value) return
  if (editor.value.innerHTML !== value) {
    editor.value.innerHTML = value || ''
  }
}

function onInput() {
  if (!editor.value) return
  const content = sanitizeHtml(editor.value.innerHTML)
  emit('update:modelValue', content)
}

function onFocus() {
  isFocused.value = true
}

function onBlur() {
  isFocused.value = false
  emit('blur')
  onInput()
}

function applyFormat(command: 'bold' | 'italic' | 'underline') {
  document.execCommand(command, false)
  onInput()
}

function toggleList() {
  document.execCommand('insertUnorderedList', false)
  onInput()
}

function clearFormatting() {
  if (!editor.value) return
  const text = editor.value.innerText
  editor.value.innerHTML = text
  onInput()
}

onMounted(() => {
  syncContent(props.modelValue || '')
})

watch(
  () => props.modelValue,
  value => {
    syncContent(value || '')
  }
)
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-toolbar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.editor-toolbar .btn {
  font-size: 0.875rem;
  padding: 6px 10px;
}

.editor-area {
  min-height: 140px;
  padding: 12px;
  border: 1px solid #374151;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.45);
  outline: none;
  overflow: auto;
}

.editor-area:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.4);
}

.editor-area:empty:before {
  content: attr(data-placeholder);
  color: var(--muted);
}
</style>
