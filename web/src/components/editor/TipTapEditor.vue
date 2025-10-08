<template>
  <div class="tiptap-editor-wrapper">
    <div v-if="editor" class="tiptap-toolbar">
      <!-- Undo / Redo -->
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()" title="Undo">
        ↶
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()" title="Redo">
        ↷
      </button>
      
      <div class="toolbar-divider"></div>
      
      <!-- Text Size -->
      <select class="toolbar-select" @change="setHeading($event)" :value="getCurrentHeading()">
        <option value="">Normal</option>
        <option value="1">Heading 1</option>
        <option value="2">Heading 2</option>
        <option value="3">Heading 3</option>
        <option value="4">Heading 4</option>
      </select>
      
      <div class="toolbar-divider"></div>
      
      <!-- Lists -->
      <div class="toolbar-dropdown">
        <button type="button" class="toolbar-btn" title="Lists">
          ≡
        </button>
        <div class="dropdown-content">
          <button type="button" @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }">
            Bullet List
          </button>
          <button type="button" @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }">
            Ordered List
          </button>
        </div>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <!-- Bold, Italic, Strikethrough, Underline -->
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" title="Bold">
        <strong>B</strong>
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" title="Italic">
        <em>I</em>
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" title="Strikethrough">
        <s>S</s>
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }" title="Underline">
        <u>U</u>
      </button>
      
      <!-- Highlight -->
      <div class="toolbar-dropdown">
        <button type="button" class="toolbar-btn" title="Highlight">
          🖍
        </button>
        <div class="dropdown-content">
          <button type="button" @click="editor.chain().focus().toggleHighlight({ color: '#fef08a' }).run()">Yellow</button>
          <button type="button" @click="editor.chain().focus().toggleHighlight({ color: '#86efac' }).run()">Green</button>
          <button type="button" @click="editor.chain().focus().toggleHighlight({ color: '#93c5fd' }).run()">Blue</button>
          <button type="button" @click="editor.chain().focus().toggleHighlight({ color: '#fca5a5' }).run()">Red</button>
          <button type="button" @click="editor.chain().focus().unsetHighlight().run()">Remove Highlight</button>
        </div>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <!-- Superscript, Subscript -->
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().toggleSuperscript().run()" :class="{ 'is-active': editor.isActive('superscript') }" title="Superscript">
        x²
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().toggleSubscript().run()" :class="{ 'is-active': editor.isActive('subscript') }" title="Subscript">
        x₂
      </button>
      
      <div class="toolbar-divider"></div>
      
      <!-- Text Align -->
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" title="Align Left">
        ≡
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" title="Align Center">
        ≣
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" title="Align Right">
        ≡
      </button>
      <button type="button" class="toolbar-btn" @click="editor.chain().focus().setTextAlign('justify').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'justify' }) }" title="Align Justify">
        ≣
      </button>
      
      <div class="toolbar-divider"></div>
      
      <!-- Insert Image -->
      <button type="button" class="toolbar-btn" @click="addImage" title="Insert Image">
        🖼
      </button>
      
      <!-- Insert Table -->
      <div class="toolbar-dropdown">
        <button type="button" class="toolbar-btn" title="Table">
          ⊞
        </button>
        <div class="dropdown-content">
          <div class="table-input-group">
            <input type="number" v-model.number="tableRows" min="1" max="10" placeholder="Rows" class="table-input" />
            <span>×</span>
            <input type="number" v-model.number="tableCols" min="1" max="10" placeholder="Cols" class="table-input" />
            <button type="button" @click="insertTable" class="insert-table-btn">Insert</button>
          </div>
          <button type="button" @click="editor.chain().focus().deleteRow().run()" :disabled="!editor.can().deleteRow()">
            Delete Row
          </button>
          <button type="button" @click="editor.chain().focus().deleteColumn().run()" :disabled="!editor.can().deleteColumn()">
            Delete Column
          </button>
          <button type="button" @click="editor.chain().focus().deleteTable().run()" :disabled="!editor.can().deleteTable()">
            Delete Table
          </button>
        </div>
      </div>
    </div>
    
    <editor-content :editor="editor" class="tiptap-editor" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Underline } from '@tiptap/extension-underline'
import { Highlight } from '@tiptap/extension-highlight'
import { TextAlign } from '@tiptap/extension-text-align'
import { Superscript } from '@tiptap/extension-superscript'
import { Subscript } from '@tiptap/extension-subscript'
import { Image } from '@tiptap/extension-image'

interface Props {
  modelValue: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Start typing...'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const tableRows = ref(3)
const tableCols = ref(3)

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Underline,
    Highlight.configure({
      multicolor: true
    }),
    TextAlign.configure({
      types: ['heading', 'paragraph']
    }),
    Superscript,
    Subscript,
    Image,
    Table.configure({
      resizable: true
    }),
    TableRow,
    TableHeader,
    TableCell
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
  editorProps: {
    attributes: {
      class: 'tiptap-content'
    }
  }
})

watch(() => props.modelValue, (newValue) => {
  if (editor.value && newValue !== editor.value.getHTML()) {
    editor.value.commands.setContent(newValue, false)
  }
})

function setHeading(event: Event) {
  const level = (event.target as HTMLSelectElement).value
  if (!editor.value) return
  
  if (level === '') {
    editor.value.chain().focus().setParagraph().run()
  } else {
    editor.value.chain().focus().toggleHeading({ level: parseInt(level) as 1 | 2 | 3 | 4 | 5 | 6 }).run()
  }
}

function getCurrentHeading() {
  if (!editor.value) return ''
  
  for (let i = 1; i <= 6; i++) {
    if (editor.value.isActive('heading', { level: i })) {
      return i.toString()
    }
  }
  return ''
}

function addImage() {
  const url = window.prompt('Enter image URL:')
  if (url && editor.value) {
    editor.value.chain().focus().setImage({ src: url }).run()
  }
}

function insertTable() {
  if (editor.value && tableRows.value > 0 && tableCols.value > 0) {
    editor.value.chain().focus().insertTable({ rows: tableRows.value, cols: tableCols.value, withHeaderRow: true }).run()
  }
}

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
.tiptap-editor-wrapper {
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--bg);
  overflow: hidden;
}

.tiptap-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px;
  background: #1f2937;
  border-bottom: 1px solid #374151;
  align-items: center;
}

.toolbar-btn {
  padding: 6px 12px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  min-width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-btn:hover:not(:disabled) {
  background: #4b5563;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-btn.is-active {
  background: var(--primary);
  border-color: var(--primary);
}

.toolbar-select {
  padding: 6px 8px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #4b5563;
  margin: 0 4px;
}

.toolbar-dropdown {
  position: relative;
}

.toolbar-dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-content {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 6px;
  padding: 4px;
  min-width: 150px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dropdown-content button {
  display: block;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  color: var(--text);
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}

.dropdown-content button:hover {
  background: #374151;
}

.dropdown-content button.is-active {
  background: var(--primary);
  color: white;
}

.dropdown-content button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.table-input-group {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px solid #374151;
  margin-bottom: 4px;
}

.table-input {
  width: 50px;
  padding: 4px 8px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 4px;
  color: var(--text);
  font-size: 14px;
}

.insert-table-btn {
  padding: 4px 8px;
  background: var(--primary);
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  cursor: pointer;
}

.insert-table-btn:hover {
  background: #2563eb;
}

.tiptap-editor {
  min-height: 150px;
}

:deep(.tiptap-content) {
  padding: 12px;
  min-height: 150px;
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
  outline: none;
}

:deep(.tiptap-content:focus) {
  outline: none;
}

:deep(.tiptap-content p) {
  margin: 0.5em 0;
}

:deep(.tiptap-content h1) {
  font-size: 2em;
  font-weight: bold;
  margin: 0.67em 0;
}

:deep(.tiptap-content h2) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0.75em 0;
}

:deep(.tiptap-content h3) {
  font-size: 1.17em;
  font-weight: bold;
  margin: 0.83em 0;
}

:deep(.tiptap-content h4) {
  font-size: 1em;
  font-weight: bold;
  margin: 1em 0;
}

:deep(.tiptap-content ul),
:deep(.tiptap-content ol) {
  padding-left: 2em;
  margin: 0.5em 0;
}

:deep(.tiptap-content table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

:deep(.tiptap-content table td),
:deep(.tiptap-content table th) {
  border: 1px solid #4b5563;
  padding: 8px;
  text-align: left;
}

:deep(.tiptap-content table th) {
  background: #374151;
  font-weight: bold;
}

:deep(.tiptap-content img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1em 0;
}

:deep(.tiptap-content mark) {
  padding: 2px 4px;
  border-radius: 2px;
}

:deep(.tiptap-content .ProseMirror-selectednode) {
  outline: 2px solid var(--primary);
}
</style>
