<template>
  <div class="st-intro-page">
    <div class="card section-header">
      <h1>Target of Evaluation (TOE) Description</h1>
      <p class="section-subtitle">Please describe your Target of Evaluation physical and logical scope</p>
    </div>
    <div class="card">
      <form class="form-grid" @submit.prevent>
        <label class="full-width">
          <span>TOE Physical Scope</span>
          <RichTextEditor
            v-model="fields.physicalScope"
            placeholder="Describe the TOE physical scope"
          />
        </label>
        <label class="full-width">
          <span>TOE Logical Scope</span>
          <RichTextEditor
            v-model="fields.logicalScope"
            placeholder="Describe the TOE logical scope"
          />
        </label>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import { useSessionStore } from '../stores/session'
import { ensureParagraph } from '../utils/html'

const sessionStore = useSessionStore()
const fields = sessionStore.toeDescription
const isReady = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

function buildHtml(): string {
  return `
    <h3>1.4 TOE Description</h3>
    <h4>1.4.1 TOE Physical Scope</h4>
    ${ensureParagraph(fields.physicalScope)}
    <h4>1.4.2 TOE Logical Scope</h4>
    ${ensureParagraph(fields.logicalScope)}
  `
}

async function persist() {
  if (!isReady.value) return
  const html = buildHtml()
  fields.html = html
  try {
    await sessionStore.saveSection('toeDescription', {
      data: {
        physicalScope: fields.physicalScope,
        logicalScope: fields.logicalScope,
      },
      html,
    })
  } catch (error) {
    console.error('Failed to persist TOE Description data', error)
  }
}

function scheduleSave() {
  if (!isReady.value) return
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveTimer = null
    void persist()
  }, 400)
}

onMounted(async () => {
  await sessionStore.initialize()
  isReady.value = true
  if (!fields.html) {
    await persist()
  }
})

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer)
})

watch(
  [
    () => fields.physicalScope,
    () => fields.logicalScope,
  ],
  scheduleSave,
  { deep: false }
)
</script>

<style scoped>
.st-intro-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-subtitle {
  color: var(--muted);
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 500;
}

.full-width {
  grid-column: 1 / -1;
}
</style>
