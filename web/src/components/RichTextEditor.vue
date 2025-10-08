<template>
  <div v-if="editor" class="rich-text-editor">
    <div class="toolbar">
      <div class="toolbar-group">
        <button type="button" class="toolbar-button" title="Undo" :disabled="!editor.can().undo()" @click="editor.chain().focus().undo().run()">
          ⟲
        </button>
        <button type="button" class="toolbar-button" title="Redo" :disabled="!editor.can().redo()" @click="editor.chain().focus().redo().run()">
          ⟳
        </button>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="heading-select">Text Size</label>
        <select id="heading-select" class="toolbar-select" v-model="headingSelection" @change="applyHeading">
          <option value="paragraph">Paragraph</option>
          <option value="1">Heading 1</option>
          <option value="2">Heading 2</option>
          <option value="3">Heading 3</option>
          <option value="4">Heading 4</option>
        </select>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="list-select">Lists</label>
        <select id="list-select" class="toolbar-select" v-model="listSelection" @change="applyList">
          <option value="">Select</option>
          <option value="bullet">Bullet list</option>
          <option value="ordered">Ordered list</option>
          <option value="task">Task list</option>
          <option value="remove">Remove list</option>
        </select>
      </div>

      <div class="toolbar-group format-group">
        <button type="button" class="toolbar-button" title="Bold" :class="{ active: editor.isActive('bold') }" @click="toggleInline('bold')">
          B
        </button>
        <button type="button" class="toolbar-button" title="Italic" :class="{ active: editor.isActive('italic') }" @click="toggleInline('italic')">
          I
        </button>
        <button type="button" class="toolbar-button" title="Strikethrough" :class="{ active: editor.isActive('strike') }" @click="toggleInline('strike')">
          S
        </button>
        <button type="button" class="toolbar-button" title="Underline" :class="{ active: editor.isActive('underline') }" @click="toggleInline('underline')">
          U
        </button>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="text-color-select">Text Color</label>
        <select id="text-color-select" class="toolbar-select" v-model="textColorSelection" @change="applyTextColor">
          <option value="">Select</option>
          <option value="red">Red</option>
          <option value="blue">Blue</option>
          <option value="green">Green</option>
          <option value="black">Black</option>
          <option value="remove">Remove color</option>
        </select>
      </div>

      <div class="toolbar-group">
        <label class="toolbar-label" for="highlight-select">Highlight</label>
        <select id="highlight-select" class="toolbar-select" v-model="highlightSelection" @change="applyHighlight">
          <option value="">Select</option>
          <option value="green">Green</option>
          <option value="yellow">Yellow</option>
          <option value="blue">Blue</option>
          <option value="red">Red</option>
          <option value="remove">Remove highlight</option>
        </select>
      </div>

      <div class="toolbar-group format-group">
        <button type="button" class="toolbar-button" title="Superscript" :class="{ active: editor.isActive('superscript') }" @click="toggleSuperscript">
          X<sup>2</sup>
        </button>
        <button type="button" class="toolbar-button" title="Subscript" :class="{ active: editor.isActive('subscript') }" @click="toggleSubscript">
          X<sub>2</sub>
        </button>
      </div>

      <div class="toolbar-group format-group">
        <button type="button" class="toolbar-button" title="Align Left" :class="{ active: editor.isActive({ textAlign: 'left' }) }" @click="setAlignment('left')">
          ⬅
        </button>
        <button type="button" class="toolbar-button" title="Align Center" :class="{ active: editor.isActive({ textAlign: 'center' }) }" @click="setAlignment('center')">
          ⬍
        </button>
        <button type="button" class="toolbar-button" title="Align Right" :class="{ active: editor.isActive({ textAlign: 'right' }) }" @click="setAlignment('right')">
          ➡
        </button>
        <button type="button" class="toolbar-button" title="Justify" :class="{ active: editor.isActive({ textAlign: 'justify' }) }" @click="setAlignment('justify')">
          ☰
        </button>
      </div>

      <div class="toolbar-group">
        <button type="button" class="toolbar-button" title="Insert Image" @click="triggerImageUpload">🖼</button>
        <input
          ref="imageFileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleImageUpload"
        />
      </div>

      <div class="toolbar-group table-group">
        <label class="toolbar-label">Insert Table</label>
        <div class="table-inputs">
          <input type="number" min="1" v-model.number="tableRows" />
          <span>×</span>
          <input type="number" min="1" v-model.number="tableCols" />
          <button type="button" class="toolbar-button" title="Insert Table" @click="insertTable">Insert</button>
        </div>
        <label class="toolbar-label" for="table-action-select">Delete</label>
        <select id="table-action-select" class="toolbar-select" v-model="tableAction" @change="handleTableAction">
          <option value="">Select</option>
          <option value="delete-row">Delete row</option>
          <option value="delete-column">Delete column</option>
          <option value="delete-table">Delete table</option>
        </select>
      </div>
    </div>

    <EditorContent :editor="editor" class="editor" :style="{ minHeight: minHeight }" />
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
import Color from '@tiptap/extension-color'
import TextStyle from '@tiptap/extension-text-style'

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

const headingSelection = ref<'paragraph' | '1' | '2' | '3' | '4'>('paragraph')
const listSelection = ref('')
const highlightSelection = ref('')
const textColorSelection = ref('')
const tableAction = ref('')
const tableRows = ref(2)
const tableCols = ref(2)
const imageFileInput = ref<HTMLInputElement | null>(null)

const highlightMap: Record<string, string> = {
  green: '#22c55e',
  yellow: '#facc15',
  blue: '#60a5fa',
  red: '#f87171',
}

const textColorMap: Record<string, string> = {
  red: '#ef4444',
  blue: '#3b82f6',
  green: '#22c55e',
  black: '#000000',
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
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Image.configure({ inline: false, allowBase64: true }),
    Table.configure({ 
      resizable: true,
      cellMinWidth: 50,
    }),
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
}

function applyTextColor() {
  if (!editor?.value) return
  const value = textColorSelection.value
  const chain = editor.value.chain().focus()
  if (value === 'remove') {
    chain.unsetColor().run()
  } else if (value in textColorMap) {
    chain.setColor(textColorMap[value]).run()
  }
  textColorSelection.value = ''
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
}

function toggleSuperscript() {
  if (!editor?.value) return
  editor.value.chain().focus().toggleSuperscript().run()
}

function toggleSubscript() {
  if (!editor?.value) return
  editor.value.chain().focus().toggleSubscript().run()
}

function setAlignment(alignment: 'left' | 'center' | 'right' | 'justify') {
  if (!editor?.value) return
  editor.value.chain().focus().setTextAlign(alignment).run()
}

function triggerImageUpload() {
  imageFileInput.value?.click()
}

function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const src = e.target?.result as string
    if (src && editor?.value) {
      editor.value.chain().focus().setImage({ src }).run()
    }
  }
  reader.readAsDataURL(file)
  
  // Reset input so same file can be selected again
  target.value = ''
}

function insertTable() {
  if (!editor?.value) return
  const rows = Math.max(1, tableRows.value || 1)
  const cols = Math.max(1, tableCols.value || 1)
  editor.value.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run()
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
  cursor: text;
  min-height: inherit;
}

.editor :deep(.ProseMirror) {
  min-height: inherit;
  outline: none;
}

.editor :deep(p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: rgba(148, 163, 184, 0.6);
  float: left;
  height: 0;
  pointer-events: none;
}

.editor :deep(table) {
  border-collapse: collapse;
  width: 100%;
  position: relative;
}

.editor :deep(table:hover) {
  outline: 2px solid rgba(59, 130, 246, 0.4);
  outline-offset: 2px;
}

.editor :deep(th),
.editor :deep(td) {
  border: 1px solid #4b5563;
  padding: 6px 10px;
  position: relative;
}

.editor :deep(.selectedCell) {
  background: rgba(59, 130, 246, 0.15);
}

.editor :deep(.resize-cursor) {
  cursor: col-resize;
}

.editor :deep(.column-resize-handle) {
  background-color: #3b82f6;
  bottom: -2px;
  position: absolute;
  right: -2px;
  pointer-events: none;
  top: 0;
  width: 4px;
}

.editor :deep(th:hover),
.editor :deep(td:hover) {
  background: rgba(59, 130, 246, 0.08);
  cursor: pointer;
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
