<template>
  <div class="rich-text-wrapper">
    <div
      ref="editor"
      class="rich-text-input"
      :class="{ 'is-empty': isEmpty, disabled }"
      :data-placeholder="placeholder"
      contenteditable="true"
      @input="handleInput"
      @blur="emit('blur')"
      @focus="emit('focus')"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string
  placeholder?: string
  disabled?: boolean
}>(), {
  modelValue: '',
  placeholder: '',
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}>()

const editor = ref<HTMLDivElement | null>(null)
const isEmpty = ref(true)

function sanitize(html: string): string {
  return html.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
}

function updatePlaceholderState() {
  if (!editor.value) return
  const textContent = editor.value.textContent?.trim() ?? ''
  const hasStructuredContent = editor.value.querySelector('img,table,ul,ol,li,br,p,div') !== null
  isEmpty.value = !textContent && !hasStructuredContent
}

function setContent(value: string) {
  if (!editor.value) return
  const sanitized = value || ''
  if (editor.value.innerHTML !== sanitized) {
    editor.value.innerHTML = sanitized
  }
  updatePlaceholderState()
}

function applyDisabledState() {
  if (!editor.value) return
  editor.value.setAttribute('contenteditable', props.disabled ? 'false' : 'true')
}

function handleInput() {
  if (!editor.value) return
  const sanitized = sanitize(editor.value.innerHTML)
  emit('update:modelValue', sanitized)
  updatePlaceholderState()
}

onMounted(() => {
  setContent(props.modelValue)
  applyDisabledState()
})

watch(() => props.modelValue, (value) => {
  setContent(value)
})

watch(() => props.disabled, () => {
  applyDisabledState()
})
</script>

<style scoped>
.rich-text-input {
  min-height: 140px;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.45);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.rich-text-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.35);
}

.rich-text-input.is-empty::before {
  content: attr(data-placeholder);
  color: var(--muted);
  pointer-events: none;
}

.rich-text-input.disabled {
  background: rgba(55, 65, 81, 0.35);
  cursor: not-allowed;
}
</style>
