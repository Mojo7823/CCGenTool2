<template>
  <div v-if="editor" class="rich-text-editor">
    <div class="toolbar">
      <div class="toolbar-group">
        <button
          type="button"
          class="toolbar-button"
          title="Undo"
          :disabled="!editor.can().undo()"
          @click="editor.chain().focus().undo().run()"
        >
          ⟲
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Redo"
          :disabled="!editor.can().redo()"
          @click="editor.chain().focus().redo().run()"
        >
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

      <div class="toolbar-group">
        <label class="toolbar-label" for="color-select">Text Color</label>
        <select id="color-select" class="toolbar-select" v-model="textColorSelection" @change="applyTextColor">
          <option value="">Select</option>
          <option value="black">Black</option>
          <option value="red">Red</option>
          <option value="blue">Blue</option>
          <option value="green">Green</option>
          <option value="remove">Remove color</option>
        </select>
      </div>

      <div class="toolbar-group format-group">
        <button
          type="button"
          class="toolbar-button"
          title="Bold"
          :class="{ active: editor.isActive('bold') }"
          @click="toggleInline('bold')"
        >
          B
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Italic"
          :class="{ active: editor.isActive('italic') }"
          @click="toggleInline('italic')"
        >
          I
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Strikethrough"
          :class="{ active: editor.isActive('strike') }"
          @click="toggleInline('strike')"
        >
          S
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Underline"
          :class="{ active: editor.isActive('underline') }"
          @click="toggleInline('underline')"
        >
          U
        </button>
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
        <button
          type="button"
          class="toolbar-button"
          title="Superscript"
          :class="{ active: editor.isActive('superscript') }"
          @click="toggleSuperscript"
        >
          X<sup>2</sup>
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Subscript"
          :class="{ active: editor.isActive('subscript') }"
          @click="toggleSubscript"
        >
          X<sub>2</sub>
        </button>
      </div>

      <div class="toolbar-group format-group">
        <button
          type="button"
          class="toolbar-button"
          title="Align left"
          :class="{ active: editor.isActive({ textAlign: 'left' }) }"
          @click="setAlignment('left')"
        >
          ⬅
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Align center"
          :class="{ active: editor.isActive({ textAlign: 'center' }) }"
          @click="setAlignment('center')"
        >
          ⬍
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Align right"
          :class="{ active: editor.isActive({ textAlign: 'right' }) }"
          @click="setAlignment('right')"
        >
          ➡
        </button>
        <button
          type="button"
          class="toolbar-button"
          title="Justify"
          :class="{ active: editor.isActive({ textAlign: 'justify' }) }"
          @click="setAlignment('justify')"
        >
          ☰
        </button>
      </div>

      <div class="toolbar-group">
        <button type="button" class="toolbar-button" title="Insert image" @click="insertImage">🖼</button>
      </div>

      <div class="toolbar-group table-group">
        <label class="toolbar-label">Insert Table</label>
        <div class="table-inputs">
          <input type="number" min="1" v-model.number="tableRows" title="Table rows" />
          <span>×</span>
          <input type="number" min="1" v-model.number="tableCols" title="Table columns" />
          <button type="button" class="toolbar-button" title="Insert table" @click="insertTable">Insert</button>
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

    <input
      ref="imageInput"
      type="file"
      accept="image/*"
      class="visually-hidden"
      @change="handleImageSelection"
    />

    <div class="editor-shell" :style="{ '--editor-min-height': minHeight }">
      <EditorContent :editor="editor" class="editor" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import { ResizableImage } from 'tiptap-extension-resizable-image'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableHeader from '@tiptap/extension-table-header'
import TableCell from '@tiptap/extension-table-cell'
import Superscript from '@tiptap/extension-superscript'
import Subscript from '@tiptap/extension-subscript'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Placeholder from '@tiptap/extension-placeholder'
import 'tiptap-extension-resizable-image/styles.css'

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
const imageInput = ref<HTMLInputElement | null>(null)

const highlightMap: Record<string, string> = {
  green: '#22c55e',
  yellow: '#facc15',
  blue: '#60a5fa',
  red: '#f87171',
}

const textColorMap: Record<string, string> = {
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
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    TextStyle,
    Color.configure({ types: ['textStyle'] }),
    ResizableImage.configure({
      allowBase64: true,
      HTMLAttributes: { class: 'editor-image' },
      minWidth: 100,
    }),
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

  const activeColor = instance.getAttributes('textStyle')?.color as string | undefined
  if (activeColor) {
    const match = Object.entries(textColorMap).find(([, hex]) => hex.toLowerCase() === activeColor.toLowerCase())
    textColorSelection.value = match ? match[0] : ''
  } else {
    textColorSelection.value = ''
  }
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

function insertImage() {
  imageInput.value?.click()
}

function insertTable() {
  if (!editor?.value) return
  const rows = Math.max(1, tableRows.value || 1)
  const cols = Math.max(1, tableCols.value || 1)
  editor.value.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run()
}

async function handleImageSelection(event: Event) {
  if (!editor?.value) return
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    target.value = ''
    return
  }

  try {
    const dataUrl = await readFileAsDataUrl(file)
    editor.value
      .chain()
      .focus()
      .setResizableImage({ src: dataUrl, 'data-keep-ratio': true })
      .run()
  } catch (error) {
    console.error('Failed to insert image:', error)
  } finally {
    target.value = ''
  }
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
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

.visually-hidden {
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

.editor-shell {
  border: 1px solid #374151;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.6);
  min-height: var(--editor-min-height, 220px);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
}

.editor-shell:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.4);
}

.editor {
  min-height: var(--editor-min-height, 220px);
  padding: 16px;
  color: var(--text);
  line-height: 1.6;
  width: 100%;
  box-sizing: border-box;
  cursor: text;
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
}

.editor :deep(.tableWrapper) {
  overflow-x: auto;
  position: relative;
  border-radius: 8px;
  transition: box-shadow 0.2s ease;
}

.editor :deep(.tableWrapper .selectedCell) {
  position: relative;
  background: rgba(37, 99, 235, 0.18);
  box-shadow: inset 0 0 0 2px rgba(37, 99, 235, 0.45);
}

.editor :deep(.tableWrapper .selectedCell::after) {
  content: '';
  position: absolute;
  inset: 0;
  border: 1px solid rgba(59, 130, 246, 0.8);
  pointer-events: none;
}

.editor :deep(.column-resize-handle) {
  background-color: rgba(59, 130, 246, 0.8);
  width: 3px;
}

.editor :deep(.editor-image) {
  max-width: 100%;
  height: auto;
}

.editor :deep(th),
.editor :deep(td) {
  border: 1px solid #4b5563;
  padding: 6px 10px;
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
