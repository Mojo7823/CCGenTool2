<template>
  <div class="rich-text-editor">
    <div class="editor-toolbar">
      <div class="toolbar-group">
        <button type="button" class="btn" @click="chainCommand('undo')" :disabled="!canCommand('undo')">↺</button>
        <button type="button" class="btn" @click="chainCommand('redo')" :disabled="!canCommand('redo')">↻</button>
      </div>

      <div class="toolbar-group">
        <select class="toolbar-select" @change="onHeadingChange($event)">
          <option value="">Paragraph</option>
          <option value="1">Heading 1</option>
          <option value="2">Heading 2</option>
          <option value="3">Heading 3</option>
          <option value="4">Heading 4</option>
        </select>
      </div>

      <div class="toolbar-group">
        <select class="toolbar-select" @change="onListChange($event)">
          <option value="">Lists</option>
          <option value="bullet">Bullet List</option>
          <option value="ordered">Ordered List</option>
          <option value="task">Task List</option>
        </select>
      </div>

      <div class="toolbar-group">
        <button type="button" class="btn" :class="{ active: editor?.isActive('bold') }" @click="toggleMark('bold')"><strong>B</strong></button>
        <button type="button" class="btn" :class="{ active: editor?.isActive('italic') }" @click="toggleMark('italic')"><em>I</em></button>
        <button type="button" class="btn" :class="{ active: editor?.isActive('strike') }" @click="toggleMark('strike')"><s>S</s></button>
        <button type="button" class="btn" :class="{ active: editor?.isActive('underline') }" @click="toggleMark('underline')"><u>U</u></button>
      </div>

      <div class="toolbar-group highlight-group">
        <select class="toolbar-select" @change="onHighlightChange($event)">
          <option value="">Highlight</option>
          <option v-for="color in highlightOptions" :key="color.value" :value="color.value">
            {{ color.label }}
          </option>
        </select>
      </div>

      <div class="toolbar-group">
        <button type="button" class="btn" :class="{ active: editor?.isActive('superscript') }" @click="toggleMark('superscript')">X⁺</button>
        <button type="button" class="btn" :class="{ active: editor?.isActive('subscript') }" @click="toggleMark('subscript')">X₋</button>
      </div>

      <div class="toolbar-group">
        <select class="toolbar-select" @change="onAlignmentChange($event)">
          <option value="">Align</option>
          <option value="left">Left</option>
          <option value="center">Center</option>
          <option value="right">Right</option>
          <option value="justify">Justify</option>
        </select>
      </div>

      <div class="toolbar-group">
        <button type="button" class="btn" @click="insertImage">🖼</button>
      </div>

      <div class="toolbar-group table-controls">
        <div class="table-inputs">
          <input type="number" min="1" v-model.number="tableRows" class="table-input" aria-label="Table rows" />
          <span>x</span>
          <input type="number" min="1" v-model.number="tableCols" class="table-input" aria-label="Table columns" />
        </div>
        <button type="button" class="btn" @click="createTable">Insert Table</button>
        <select class="toolbar-select" @change="onTableActionChange($event)">
          <option value="">Delete Table</option>
          <option value="row">Delete Row</option>
          <option value="column">Delete Column</option>
          <option value="table">Delete Table</option>
        </select>
      </div>
    </div>

    <EditorContent v-if="editor" :editor="editor" class="editor-content" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, shallowRef, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import { TextStyle } from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'
import Superscript from '@tiptap/extension-superscript'
import Subscript from '@tiptap/extension-subscript'
import Image from '@tiptap/extension-image'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'

interface HighlightOption {
  label: string
  value: string
}

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  minHeight: {
    type: String,
    default: '200px',
  },
})

const emit = defineEmits(['update:modelValue'])
const editor = shallowRef<Editor | null>(null)
const tableRows = shallowRef(2)
const tableCols = shallowRef(2)

const highlightOptions = computed<HighlightOption[]>(() => [
  { label: 'Green', value: '#22c55e' },
  { label: 'Yellow', value: '#facc15' },
  { label: 'Blue', value: '#38bdf8' },
  { label: 'Red', value: '#f87171' },
  { label: 'Remove Highlight', value: 'none' },
])

onMounted(() => {
  editor.value = new Editor({
    content: props.modelValue || '',
    extensions: [
      StarterKit.configure({
        bulletList: {
          keepMarks: true,
        },
        orderedList: {
          keepMarks: true,
        },
      }),
      Underline,
      TextStyle,
      Color,
      Highlight.configure({ multicolor: true }),
      Superscript,
      Subscript,
      TaskList,
      TaskItem.configure({ nested: true }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Placeholder.configure({ placeholder: props.placeholder }),
      Image.configure({ inline: false }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
    ],
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
        style: `min-height: ${props.minHeight};`,
      },
    },
    onUpdate: ({ editor }) => {
      emit('update:modelValue', editor.getHTML())
    },
  })
})

watch(
  () => props.modelValue,
  (newValue) => {
    if (!editor.value) return
    const current = editor.value.getHTML()
    if (newValue !== current) {
      editor.value.commands.setContent(newValue || '', false)
    }
  }
)

onBeforeUnmount(() => {
  editor.value?.destroy()
})

function chainCommand(command: 'undo' | 'redo') {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  if (command === 'undo') chain.undo().run()
  if (command === 'redo') chain.redo().run()
}

function canCommand(command: 'undo' | 'redo') {
  if (!editor.value) return false
  if (command === 'undo') {
    return editor.value.can().undo()
  }
  return editor.value.can().redo()
}

function toggleMark(mark: string) {
  editor.value?.chain().focus().toggleMark(mark).run()
}

function applyHeading(level: string) {
  if (!editor.value) return
  if (!level) {
    editor.value.chain().focus().setParagraph().run()
  } else {
    const parsed = Number(level)
    editor.value.chain().focus().setHeading({ level: parsed }).run()
  }
}

function applyList(type: string) {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  switch (type) {
    case 'bullet':
      chain.toggleBulletList().run()
      break
    case 'ordered':
      chain.toggleOrderedList().run()
      break
    case 'task':
      chain.toggleTaskList().run()
      break
    default:
      break
  }
}

function applyHighlight(value: string) {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  if (!value || value === 'none') {
    chain.unsetHighlight().run()
    return
  }
  chain.toggleHighlight({ color: value }).run()
}

function applyAlignment(alignment: string) {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  switch (alignment) {
    case 'left':
      chain.setTextAlign('left').run()
      break
    case 'center':
      chain.setTextAlign('center').run()
      break
    case 'right':
      chain.setTextAlign('right').run()
      break
    case 'justify':
      chain.setTextAlign('justify').run()
      break
    default:
      chain.unsetTextAlign().run()
      break
  }
}

function insertImage() {
  if (!editor.value) return
  const url = window.prompt('Enter image URL')
  if (!url) return
  editor.value.chain().focus().setImage({ src: url }).run()
}

function createTable() {
  if (!editor.value) return
  const rows = Math.max(1, Number(tableRows.value) || 1)
  const cols = Math.max(1, Number(tableCols.value) || 1)
  editor.value.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run()
}

function handleTableAction(action: string) {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  switch (action) {
    case 'row':
      chain.deleteRow().run()
      break
    case 'column':
      chain.deleteColumn().run()
      break
    case 'table':
      chain.deleteTable().run()
      break
    default:
      break
  }
}

function resetSelect(select: EventTarget | null) {
  if (!(select instanceof HTMLSelectElement)) return
  select.selectedIndex = 0
}

function onHeadingChange(event: Event) {
  if (!(event.target instanceof HTMLSelectElement)) return
  applyHeading(event.target.value)
  resetSelect(event.target)
}

function onListChange(event: Event) {
  if (!(event.target instanceof HTMLSelectElement)) return
  applyList(event.target.value)
  resetSelect(event.target)
}

function onHighlightChange(event: Event) {
  if (!(event.target instanceof HTMLSelectElement)) return
  applyHighlight(event.target.value)
  resetSelect(event.target)
}

function onAlignmentChange(event: Event) {
  if (!(event.target instanceof HTMLSelectElement)) return
  applyAlignment(event.target.value)
  resetSelect(event.target)
}

function onTableActionChange(event: Event) {
  if (!(event.target instanceof HTMLSelectElement)) return
  handleTableAction(event.target.value)
  resetSelect(event.target)
}
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.toolbar-group {
  display: flex;
  gap: 6px;
  align-items: center;
}

.btn {
  border: 1px solid #374151;
  background: #1f2937;
  color: #f3f4f6;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  transition: background 0.2s ease;
  font-size: 0.9rem;
}

.btn:hover {
  background: #111827;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn.active {
  background: #2563eb;
  border-color: #2563eb;
}

.toolbar-select {
  border: 1px solid #374151;
  background: #111827;
  color: #f3f4f6;
  border-radius: 6px;
  padding: 6px 10px;
}

.table-controls {
  gap: 8px;
}

.table-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.table-input {
  width: 60px;
  border: 1px solid #374151;
  background: #111827;
  color: #f3f4f6;
  border-radius: 6px;
  padding: 4px 6px;
}

.editor-content {
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 12px;
  background: #0f172a;
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
}

.tiptap-editor {
  outline: none;
}

.tiptap-editor ul,
.tiptap-editor ol {
  padding-left: 24px;
}

.tiptap-editor table {
  width: 100%;
  border-collapse: collapse;
}

.tiptap-editor th,
.tiptap-editor td {
  border: 1px solid #4b5563;
  padding: 6px;
}
</style>
