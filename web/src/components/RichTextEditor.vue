<template>
  <div class="rich-text-editor">
    <div class="toolbar">
      <button type="button" class="btn" @click="applyFormat('bold')" title="Bold"><strong>B</strong></button>
      <button type="button" class="btn" @click="applyFormat('italic')" title="Italic"><em>I</em></button>
      <button type="button" class="btn" @click="applyFormat('underline')" title="Underline"><u>U</u></button>
      <button type="button" class="btn" @click="applyFormat('unorderedList')" title="Bullet list">• List</button>
      <button type="button" class="btn" @click="applyFormat('orderedList')" title="Numbered list">1. List</button>
      <button type="button" class="btn" @click="clearFormatting" title="Clear formatting">Clear</button>
    </div>
    <div
      ref="editor"
      class="editor"
      contenteditable="true"
      :data-placeholder="placeholder"
      @input="handleInput"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

const props = defineProps<{ modelValue: string; placeholder?: string }>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}>()

const editor = ref<HTMLDivElement | null>(null)
let updating = false

function setContent(value: string) {
  if (!editor.value) return
  updating = true
  editor.value.innerHTML = value || ''
  updating = false
}

onMounted(() => {
  setContent(props.modelValue)
})

watch(
  () => props.modelValue,
  (value) => {
    if (updating) return
    if (!editor.value) return
    const current = editor.value.innerHTML
    if ((value || '') === current) return
    setContent(value || '')
  }
)

function cleanHtml(html: string): string {
  const trimmed = html.trim()
  if (!trimmed || trimmed === '<br>' || trimmed === '<div><br></div>') {
    return ''
  }
  return html
}

function handleInput() {
  if (!editor.value) return
  if (updating) return
  const html = cleanHtml(editor.value.innerHTML)
  updating = true
  if (editor.value.innerHTML !== html) {
    editor.value.innerHTML = html
  }
  emit('update:modelValue', html)
  updating = false
}

function focusEditor() {
  editor.value?.focus()
}

function applyFormat(format: 'bold' | 'italic' | 'underline' | 'unorderedList' | 'orderedList') {
  if (typeof document === 'undefined') return
  focusEditor()
  const commandMap: Record<typeof format, string> = {
    bold: 'bold',
    italic: 'italic',
    underline: 'underline',
    unorderedList: 'insertUnorderedList',
    orderedList: 'insertOrderedList',
  }
  document.execCommand(commandMap[format], false)
  handleInput()
}

function clearFormatting() {
  if (typeof document === 'undefined') return
  focusEditor()
  document.execCommand('removeFormat', false)
  handleInput()
}
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar .btn {
  padding: 6px 10px;
  font-size: 14px;
}

.editor {
  min-height: 140px;
  padding: 12px;
  border: 1px solid #374151;
  border-radius: 8px;
  background: #0b1220;
  color: var(--text);
  outline: none;
  white-space: pre-wrap;
}

.editor:empty::before {
  content: attr(data-placeholder);
  color: var(--muted);
}
</style>
