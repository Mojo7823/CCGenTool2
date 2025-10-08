<template>
  <div class="rich-text-editor" @click.stop>
    <div class="rich-text-toolbar">
      <div class="toolbar-group">
        <button type="button" class="toolbar-button" @click="runCommand('undo')" :disabled="!canRun('undo')">
          ↺
        </button>
        <button type="button" class="toolbar-button" @click="runCommand('redo')" :disabled="!canRun('redo')">
          ↻
        </button>
      </div>

      <div class="toolbar-group dropdown" :class="{ open: openDropdown === 'heading' }">
        <button type="button" class="toolbar-button" @click="toggleDropdown('heading')">
          {{ currentHeadingLabel }}
        </button>
        <div v-if="openDropdown === 'heading'" class="dropdown-menu">
          <button type="button" class="dropdown-item" @click="setHeading(0)">Paragraph</button>
          <button type="button" class="dropdown-item" @click="setHeading(1)">Heading 1</button>
          <button type="button" class="dropdown-item" @click="setHeading(2)">Heading 2</button>
          <button type="button" class="dropdown-item" @click="setHeading(3)">Heading 3</button>
          <button type="button" class="dropdown-item" @click="setHeading(4)">Heading 4</button>
        </div>
      </div>

      <div class="toolbar-group dropdown" :class="{ open: openDropdown === 'list' }">
        <button type="button" class="toolbar-button" @click="toggleDropdown('list')">Lists ▾</button>
        <div v-if="openDropdown === 'list'" class="dropdown-menu">
          <button type="button" class="dropdown-item" :class="{ active: editor?.isActive('bulletList') }" @click="toggleBulletList">
            Bullet List
          </button>
          <button type="button" class="dropdown-item" :class="{ active: editor?.isActive('orderedList') }" @click="toggleOrderedList">
            Ordered List
          </button>
          <button type="button" class="dropdown-item" :class="{ active: editor?.isActive('taskList') }" @click="toggleTaskList">
            Task List
          </button>
        </div>
      </div>

      <div class="toolbar-group">
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive('bold') }" @click="toggleBold">
          <strong>B</strong>
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive('italic') }" @click="toggleItalic">
          <em>I</em>
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive('strike') }" @click="toggleStrike">
          <span class="strike">S</span>
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive('underline') }" @click="toggleUnderline">
          <span class="underline">U</span>
        </button>
      </div>

      <div class="toolbar-group dropdown" :class="{ open: openDropdown === 'highlight' }">
        <button type="button" class="toolbar-button" @click="toggleDropdown('highlight')">Highlight ▾</button>
        <div v-if="openDropdown === 'highlight'" class="dropdown-menu highlight-menu">
          <button
            v-for="option in highlightOptions"
            :key="option.name"
            type="button"
            class="dropdown-item"
            @click="setHighlight(option)"
          >
            <span class="color-preview" :style="{ backgroundColor: option.color || 'transparent' }"></span>
            {{ option.label }}
          </button>
        </div>
      </div>

      <div class="toolbar-group">
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive('superscript') }" @click="toggleSuperscript">
          x<sup>2</sup>
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive('subscript') }" @click="toggleSubscript">
          x<sub>2</sub>
        </button>
      </div>

      <div class="toolbar-group">
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive({ textAlign: 'left' }) }" @click="setAlign('left')">
          ⬅
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive({ textAlign: 'center' }) }" @click="setAlign('center')">
          ⬌
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive({ textAlign: 'right' }) }" @click="setAlign('right')">
          ➡
        </button>
        <button type="button" class="toolbar-button" :class="{ active: editor?.isActive({ textAlign: 'justify' }) }" @click="setAlign('justify')">
          ☰
        </button>
      </div>

      <div class="toolbar-group">
        <button type="button" class="toolbar-button" @click="insertImage">🖼</button>
      </div>

      <div class="toolbar-group dropdown" :class="{ open: openDropdown === 'table' }">
        <button type="button" class="toolbar-button" @click="toggleDropdown('table')">Table ▾</button>
        <div v-if="openDropdown === 'table'" class="dropdown-menu table-menu">
          <div class="table-create">
            <label>
              Rows
              <input v-model.number="tableRows" type="number" min="1" />
            </label>
            <label>
              Columns
              <input v-model.number="tableCols" type="number" min="1" />
            </label>
            <button type="button" class="btn" @click="createTable">Insert Table</button>
          </div>
          <div class="table-actions">
            <button type="button" class="dropdown-item" @click="deleteTable('row')">Delete Row</button>
            <button type="button" class="dropdown-item" @click="deleteTable('column')">Delete Column</button>
            <button type="button" class="dropdown-item" @click="deleteTable('table')">Delete Table</button>
          </div>
        </div>
      </div>
    </div>

    <EditorContent
      v-if="editor"
      :editor="editor"
      class="rich-text-editor__content"
      :style="{ minHeight }"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
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
import Placeholder from '@tiptap/extension-placeholder'
import { TextStyle } from '@tiptap/extension-text-style'

interface HighlightOption {
  name: string
  label: string
  color?: string
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
    default: '160px',
  },
})

const emit = defineEmits(['update:modelValue'])

const openDropdown = ref<string | null>(null)
const tableRows = ref(2)
const tableCols = ref(2)

const highlightOptions: HighlightOption[] = [
  { name: 'green', label: 'Green', color: '#bbf7d0' },
  { name: 'yellow', label: 'Yellow', color: '#fef08a' },
  { name: 'blue', label: 'Blue', color: '#bfdbfe' },
  { name: 'red', label: 'Red', color: '#fecaca' },
  { name: 'remove', label: 'Remove highlight' },
]

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      bulletList: {
        keepMarks: true,
      },
      orderedList: {
        keepMarks: true,
      },
      history: true,
    }),
    Underline,
    TextStyle,
    Highlight.configure({ multicolor: true }),
    Superscript,
    Subscript,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
      alignments: ['left', 'center', 'right', 'justify'],
    }),
    Image.configure({ inline: false }),
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableHeader,
    TableCell,
    TaskList.configure({ nested: true }),
    TaskItem.configure({ nested: true }),
    Placeholder.configure({
      placeholder: () => props.placeholder,
    }),
  ],
  onUpdate({ editor }) {
    emit('update:modelValue', editor.getHTML())
  },
})

const currentHeadingLabel = computed(() => {
  if (!editor.value) return 'Paragraph'
  if (editor.value.isActive('heading', { level: 1 })) return 'Heading 1'
  if (editor.value.isActive('heading', { level: 2 })) return 'Heading 2'
  if (editor.value.isActive('heading', { level: 3 })) return 'Heading 3'
  if (editor.value.isActive('heading', { level: 4 })) return 'Heading 4'
  return 'Paragraph'
})

watch(
  () => props.modelValue,
  value => {
    const editorInstance = editor.value
    if (!editorInstance) return
    const html = value || ''
    if (html === editorInstance.getHTML()) {
      return
    }
    editorInstance.commands.setContent(html, false)
  }
)

const closeDropdowns = () => {
  openDropdown.value = null
}

onMounted(() => {
  document.addEventListener('click', closeDropdowns)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdowns)
  editor.value?.destroy()
})

const toggleDropdown = (name: string) => {
  openDropdown.value = openDropdown.value === name ? null : name
}

function runCommand(command: 'undo' | 'redo') {
  if (!editor.value) return
  editor.value.chain().focus()[command]().run()
}

function canRun(command: 'undo' | 'redo') {
  const editorInstance = editor.value
  if (!editorInstance) return false
  return editorInstance.can().chain().focus()[command]().run()
}

function setHeading(level: number) {
  if (!editor.value) return
  if (level === 0) {
    editor.value.chain().focus().setParagraph().run()
  } else {
    editor.value.chain().focus().setHeading({ level }).run()
  }
  closeDropdowns()
}

function toggleBold() {
  editor.value?.chain().focus().toggleBold().run()
}

function toggleItalic() {
  editor.value?.chain().focus().toggleItalic().run()
}

function toggleStrike() {
  editor.value?.chain().focus().toggleStrike().run()
}

function toggleUnderline() {
  editor.value?.chain().focus().toggleUnderline().run()
}

function setHighlight(option: HighlightOption) {
  if (!editor.value) return
  if (option.name === 'remove') {
    editor.value.chain().focus().unsetHighlight().run()
  } else if (option.color) {
    editor.value.chain().focus().setHighlight({ color: option.color }).run()
  }
  closeDropdowns()
}

function toggleSuperscript() {
  editor.value?.chain().focus().toggleSuperscript().run()
}

function toggleSubscript() {
  editor.value?.chain().focus().toggleSubscript().run()
}

function setAlign(alignment: 'left' | 'center' | 'right' | 'justify') {
  editor.value?.chain().focus().setTextAlign(alignment).run()
}

function toggleBulletList() {
  editor.value?.chain().focus().toggleBulletList().run()
}

function toggleOrderedList() {
  editor.value?.chain().focus().toggleOrderedList().run()
}

function toggleTaskList() {
  editor.value?.chain().focus().toggleTaskList().run()
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
  closeDropdowns()
}

function deleteTable(target: 'row' | 'column' | 'table') {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  switch (target) {
    case 'row':
      chain.deleteRow().run()
      break
    case 'column':
      chain.deleteColumn().run()
      break
    case 'table':
      chain.deleteTable().run()
      break
  }
  closeDropdowns()
}
</script>

<style scoped>
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rich-text-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 8px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
}

.toolbar-button {
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: var(--text);
  padding: 6px 10px;
  cursor: pointer;
  font-size: 14px;
  min-width: 32px;
  transition: background 0.2s, border-color 0.2s;
}

.toolbar-button:hover {
  background: #4b5563;
}

.toolbar-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-button.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #0f172a;
}

.toolbar-group.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 10;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 8px;
  min-width: 160px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dropdown-item {
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 6px;
  padding: 6px 10px;
  color: var(--text);
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover,
.dropdown-item.active {
  background: var(--primary);
  color: #0f172a;
}

.highlight-menu {
  min-width: 200px;
}

.color-preview {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.table-menu {
  gap: 12px;
  min-width: 220px;
}

.table-create {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-create label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.table-create input {
  width: 60px;
  padding: 4px 6px;
  border-radius: 4px;
  border: 1px solid #4b5563;
  background: #111827;
  color: var(--text);
}

.table-create .btn {
  align-self: flex-end;
  padding: 6px 12px;
  border-radius: 6px;
  background: var(--primary);
  border: none;
  color: #0f172a;
  cursor: pointer;
  font-weight: 600;
}

.table-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rich-text-editor__content {
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 12px;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.rich-text-editor__content :deep(p) {
  margin: 0 0 0.75rem;
}

.rich-text-editor__content :deep(ul),
.rich-text-editor__content :deep(ol) {
  padding-left: 1.5rem;
  margin: 0.75rem 0;
}

.rich-text-editor__content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
}

.rich-text-editor__content :deep(th),
.rich-text-editor__content :deep(td) {
  border: 1px solid #4b5563;
  padding: 8px;
}

.rich-text-editor__content :deep(img) {
  max-width: 100%;
  height: auto;
}

.strike {
  text-decoration: line-through;
}

.underline {
  text-decoration: underline;
}
</style>
