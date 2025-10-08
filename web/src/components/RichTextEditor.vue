<template>
  <div v-if="editor" class="rich-text-editor">
    <div class="toolbar">
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-button"
          :disabled="!editor.can().undo()"
          title="Undo"
          aria-label="Undo"
          @click="editor.chain().focus().undo().run()"
        >
          ⟲
        </button>
        <button
          type="button"
          class="toolbar-button"
          :disabled="!editor.can().redo()"
          title="Redo"
          aria-label="Redo"
          @click="editor.chain().focus().redo().run()"
        >
          ⟳
        </button>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="heading-select">Text Size</label>
        <select
          id="heading-select"
          class="toolbar-select"
          v-model="headingSelection"
          title="Change text size"
          aria-label="Change text size"
          @change="applyHeading"
        >
          <option value="paragraph">Paragraph</option>
          <option value="1">Heading 1</option>
          <option value="2">Heading 2</option>
          <option value="3">Heading 3</option>
          <option value="4">Heading 4</option>
        </select>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="list-select">Lists</label>
        <select
          id="list-select"
          class="toolbar-select"
          v-model="listSelection"
          title="Insert or remove list"
          aria-label="Insert or remove list"
          @change="applyList"
        >
          <option value="">Select</option>
          <option value="bullet">Bullet list</option>
          <option value="ordered">Ordered list</option>
          <option value="task">Task list</option>
          <option value="remove">Remove list</option>
        </select>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="color-select">Text Color</label>
        <select
          id="color-select"
          class="toolbar-select"
          v-model="colorSelection"
          title="Change text color"
          aria-label="Change text color"
          @change="applyColor"
        >
          <option value="default">Default</option>
          <option value="black">Black</option>
          <option value="red">Red</option>
          <option value="blue">Blue</option>
          <option value="green">Green</option>
        </select>
      </div>

      <div class="toolbar-group format-group">
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive('bold') }"
          title="Bold"
          aria-label="Bold"
          @click="toggleInline('bold')"
        >
          B
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive('italic') }"
          title="Italic"
          aria-label="Italic"
          @click="toggleInline('italic')"
        >
          I
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive('strike') }"
          title="Strikethrough"
          aria-label="Strikethrough"
          @click="toggleInline('strike')"
        >
          S
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive('underline') }"
          title="Underline"
          aria-label="Underline"
          @click="toggleInline('underline')"
        >
          U
        </button>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="highlight-select">Highlight</label>
        <select
          id="highlight-select"
          class="toolbar-select"
          v-model="highlightSelection"
          title="Highlight text"
          aria-label="Highlight text"
          @change="applyHighlight"
        >
          <option value="">Select</option>
          <option value="green">Green</option>
          <option value="yellow">Yellow</option>
          <option value="blue">Blue</option>
          <option value="red">Red</option>
          <option value="remove">Remove highlight</option>
        </select>
      </div>

      <div class="toolbar-group format-group">
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive('superscript') }"
          title="Superscript"
          aria-label="Superscript"
          @click="toggleSuperscript"
        >
          X<sup>2</sup>
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive('subscript') }"
          title="Subscript"
          aria-label="Subscript"
          @click="toggleSubscript"
        >
          X<sub>2</sub>
        </button>
      </div>

      <div class="toolbar-group format-group">
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive({ textAlign: 'left' }) }"
          title="Align left"
          aria-label="Align left"
          @click="setAlignment('left')"
        >
          ⬅
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive({ textAlign: 'center' }) }"
          title="Align center"
          aria-label="Align center"
          @click="setAlignment('center')"
        >
          ⬍
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive({ textAlign: 'right' }) }"
          title="Align right"
          aria-label="Align right"
          @click="setAlignment('right')"
        >
          ➡
        </button>
        <button
          type="button"
          class="toolbar-button"
          :class="{ active: editor.isActive({ textAlign: 'justify' }) }"
          title="Justify"
          aria-label="Justify"
          @click="setAlignment('justify')"
        >
          ☰
        </button>
      </div>

      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-button"
          title="Insert image"
          aria-label="Insert image"
          @click="triggerImageUpload"
        >
          🖼
        </button>
        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          class="sr-only"
          aria-hidden="true"
          @change="handleImageSelection"
        />
      </div>

      <div class="toolbar-group table-group">
        <label class="toolbar-label" for="table-rows">Insert Table</label>
        <div class="table-inputs">
          <input
            id="table-rows"
            type="number"
            min="1"
            v-model.number="tableRows"
            title="Number of rows"
            aria-label="Number of rows"
          />
          <span aria-hidden="true">×</span>
          <input
            id="table-columns"
            type="number"
            min="1"
            v-model.number="tableCols"
            title="Number of columns"
            aria-label="Number of columns"
          />
          <button
            type="button"
            class="toolbar-button"
            title="Insert table"
            aria-label="Insert table"
            @click="insertTable"
          >
            Insert
          </button>
        </div>
        <label class="toolbar-label" for="table-action-select">Delete</label>
        <select
          id="table-action-select"
          class="toolbar-select"
          v-model="tableAction"
          title="Delete table elements"
          aria-label="Delete table elements"
          @change="handleTableAction"
        >
          <option value="">Select</option>
          <option value="delete-row">Delete row</option>
          <option value="delete-column">Delete column</option>
          <option value="delete-table">Delete table</option>
        </select>
      </div>
    </div>

    <EditorContent
      :editor="editor"
      class="editor"
      :style="{ minHeight: minHeight }"
      aria-label="Rich text editor"
    />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'
import Image from '@tiptap/extension-image'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableHeader from '@tiptap/extension-table-header'
import TableCell from '@tiptap/extension-table-cell'
import Superscript from '@tiptap/extension-superscript'
import Subscript from '@tiptap/extension-subscript'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Placeholder from '@tiptap/extension-placeholder'
import { TextStyle } from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'

const props = withDefaults(
  defineProps<{
    modelValue: string
    placeholder?: string
    minHeight?: string
  }>(),
  {
    modelValue: '',
    placeholder: '',
    minHeight: '220px',
  }
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

type HeadingSelection = 'paragraph' | '1' | '2' | '3' | '4'
type ColorOption = 'default' | 'black' | 'red' | 'blue' | 'green'

const headingSelection = ref<HeadingSelection>('paragraph')
const listSelection = ref('')
const highlightSelection = ref('')
const tableAction = ref('')
const tableRows = ref(2)
const tableCols = ref(2)
const colorSelection = ref<ColorOption>('default')
const imageInput = ref<HTMLInputElement | null>(null)

const highlightMap: Record<string, string> = {
  green: '#22c55e',
  yellow: '#facc15',
  blue: '#60a5fa',
  red: '#f87171',
}

const colorMap: Record<Exclude<ColorOption, 'default'>, string> = {
  black: '#000000',
  red: '#ef4444',
  blue: '#3b82f6',
  green: '#22c55e',
}

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3, 4],
      },
    }),
    Underline,
    Highlight.configure({ multicolor: true }),
    TextStyle,
    Color.configure({ types: ['textStyle'] }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Image.configure({ inline: false, allowBase64: true }),
    Table.configure({ resizable: true }),
    TableRow,
    TableHeader,
    TableCell,
    Superscript,
    Subscript,
    TaskList,
    TaskItem,
    Placeholder.configure({ placeholder: props.placeholder ?? '' }),
  ],
  onUpdate({ editor }) {
    emit('update:modelValue', editor.getHTML())
    updateToolbarState()
  },
  onSelectionUpdate: updateToolbarState,
  onCreate: updateToolbarState,
})

function updateToolbarState() {
  if (!editor?.value) return
  const instance = editor.value

  if (instance.isActive('heading', { level: 1 })) headingSelection.value = '1'
  else if (instance.isActive('heading', { level: 2 })) headingSelection.value = '2'
  else if (instance.isActive('heading', { level: 3 })) headingSelection.value = '3'
  else if (instance.isActive('heading', { level: 4 })) headingSelection.value = '4'
  else headingSelection.value = 'paragraph'

  const textStyleAttrs = instance.getAttributes('textStyle') as { color?: string }
  const activeColor = typeof textStyleAttrs?.color === 'string' ? textStyleAttrs.color.toLowerCase() : ''
  const colorEntry = (Object.entries(colorMap) as [Exclude<ColorOption, 'default'>, string][]).find(
    ([, value]) => value === activeColor
  )
  colorSelection.value = colorEntry ? colorEntry[0] : 'default'
}

watch(
  () => props.modelValue,
  value => {
    if (editor?.value && value !== editor.value.getHTML()) {
      editor.value.commands.setContent(value || '', false)
      updateToolbarState()
    }
  }
)

function applyHeading() {
  if (!editor?.value) return
  const level = headingSelection.value
  const chain = editor.value.chain().focus()
  if (level === 'paragraph') {
    chain.setParagraph().run()
  } else {
    chain.setHeading({ level: Number(level) as 1 | 2 | 3 | 4 }).run()
  }
  updateToolbarState()
}

function applyList() {
  if (!editor?.value) return
  const chain = editor.value.chain().focus()
  switch (listSelection.value) {
    case 'bullet':
      chain.toggleBulletList().run()
      break
    case 'ordered':
      chain.toggleOrderedList().run()
      break
    case 'task':
      chain.toggleTaskList().run()
      break
    case 'remove':
      chain.liftListItem('listItem').liftListItem('taskItem').run()
      break
  }
  listSelection.value = ''
  updateToolbarState()
}

function toggleInline(type: 'bold' | 'italic' | 'strike' | 'underline') {
  if (!editor?.value) return
  const chain = editor.value.chain().focus()
  switch (type) {
    case 'bold':
      chain.toggleBold().run()
      break
    case 'italic':
      chain.toggleItalic().run()
      break
    case 'strike':
      chain.toggleStrike().run()
      break
    case 'underline':
      chain.toggleUnderline().run()
      break
  }
  updateToolbarState()
}

function applyHighlight() {
  if (!editor?.value) return
  const value = highlightSelection.value
  const chain = editor.value.chain().focus()
  if (value === 'remove') {
    chain.unsetHighlight().run()
  } else if (value in highlightMap) {
    chain.setHighlight({ color: highlightMap[value] }).run()
  }
  highlightSelection.value = ''
  updateToolbarState()
}

function toggleSuperscript() {
  if (!editor?.value) return
  editor.value.chain().focus().toggleSuperscript().run()
  updateToolbarState()
}

function toggleSubscript() {
  if (!editor?.value) return
  editor.value.chain().focus().toggleSubscript().run()
  updateToolbarState()
}

function setAlignment(alignment: 'left' | 'center' | 'right' | 'justify') {
  if (!editor?.value) return
  editor.value.chain().focus().setTextAlign(alignment).run()
  updateToolbarState()
}

function applyColor() {
  if (!editor?.value) return
  const selection = colorSelection.value
  const chain = editor.value.chain().focus()
  if (selection === 'default') {
    chain.unsetColor().run()
  } else {
    chain.setColor(colorMap[selection]).run()
  }
  updateToolbarState()
}

function triggerImageUpload() {
  imageInput.value?.click()
}

function handleImageSelection(event: Event) {
  if (!editor?.value) return
  const target = event.target as HTMLInputElement | null
  const file = target?.files?.[0]

  if (!file) {
    if (target) target.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    const result = reader.result
    if (typeof result === 'string') {
      editor.value?.chain().focus().setImage({ src: result }).run()
      updateToolbarState()
    }
    if (target) {
      target.value = ''
    }
  }
  reader.onerror = () => {
    console.error('Failed to read the selected image file.')
    if (target) {
      target.value = ''
    }
  }
  reader.readAsDataURL(file)
}

function insertTable() {
  if (!editor?.value) return
  const rows = Math.max(1, tableRows.value || 1)
  const cols = Math.max(1, tableCols.value || 1)
  editor.value.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run()
  updateToolbarState()
}

function handleTableAction() {
  if (!editor?.value) return
  const chain = editor.value.chain().focus()
  switch (tableAction.value) {
    case 'delete-row':
      chain.deleteRow().run()
      break
    case 'delete-column':
      chain.deleteColumn().run()
      break
    case 'delete-table':
      chain.deleteTable().run()
      break
  }
  tableAction.value = ''
  updateToolbarState()
}

onBeforeUnmount(() => {
  editor?.value?.destroy()
})
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  background: rgba(55, 65, 81, 0.35);
  border: 1px solid #374151;
  border-radius: 10px;
  padding: 12px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-group.format-group {
  border-left: 1px solid rgba(148, 163, 184, 0.2);
  padding-left: 12px;
  margin-left: 4px;
}

.toolbar-group.table-group {
  gap: 8px;
  border-left: 1px solid rgba(148, 163, 184, 0.2);
  padding-left: 12px;
}

.toolbar-label {
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.toolbar-select {
  background: #0f172a;
  border: 1px solid #334155;
  color: var(--text);
  border-radius: 6px;
  padding: 4px 8px;
}

.toolbar-button {
  background: #1f2937;
  border: 1px solid #334155;
  color: var(--text);
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s, transform 0.1s;
}

.toolbar-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-button:not(:disabled):hover {
  background: #374151;
  transform: translateY(-1px);
}

.toolbar-button.active {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.table-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.table-inputs input {
  width: 60px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  color: var(--text);
  padding: 4px 6px;
}

.editor {
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 16px;
  background: rgba(15, 23, 42, 0.6);
  color: var(--text);
  line-height: 1.6;
  width: 100%;
  cursor: text;
}

.editor :deep(p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: rgba(148, 163, 184, 0.6);
  float: left;
  height: 0;
  pointer-events: none;
}

.editor :deep(.ProseMirror) {
  min-height: inherit;
  outline: none;
}

.editor :deep(table) {
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}

.editor :deep(th),
.editor :deep(td) {
  border: 1px solid #4b5563;
  padding: 6px 10px;
  position: relative;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  cursor: text;
}

.editor :deep(th:hover),
.editor :deep(td:hover) {
  border-color: rgba(59, 130, 246, 0.7);
  box-shadow: inset 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.editor :deep(th:hover)::after,
.editor :deep(td:hover)::after {
  content: '';
  position: absolute;
  right: 4px;
  bottom: 4px;
  width: 10px;
  height: 10px;
  border-right: 2px solid rgba(59, 130, 246, 0.8);
  border-bottom: 2px solid rgba(59, 130, 246, 0.8);
  pointer-events: none;
}

.editor :deep(.selectedCell) {
  border-color: rgba(59, 130, 246, 0.9);
  box-shadow: inset 0 0 0 2px rgba(59, 130, 246, 0.4);
}

.editor :deep(.tableWrapper) {
  position: relative;
  overflow-x: auto;
}

.editor :deep(.tableWrapper:hover .column-resize-handle),
.editor :deep(.tableWrapper:hover .row-resize-handle) {
  opacity: 1;
}

.editor :deep(.column-resize-handle),
.editor :deep(.row-resize-handle) {
  position: absolute;
  background: rgba(59, 130, 246, 0.6);
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: auto;
  z-index: 1;
}

.editor :deep(.column-resize-handle) {
  cursor: col-resize;
  top: 0;
  bottom: 0;
  width: 6px;
  right: -3px;
}

.editor :deep(.row-resize-handle) {
  cursor: row-resize;
  left: 0;
  right: 0;
  height: 6px;
  bottom: -3px;
}

.editor :deep(ul),
.editor :deep(ol) {
  padding-left: 24px;
}

.editor :deep(.task-list-item) {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.editor :deep(.task-list-item input) {
  margin-top: 6px;
}
</style>
