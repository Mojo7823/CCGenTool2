<template>
  <div class="st-intro-page">
    <div class="card section-header">
      <h1>Target of Evaluation (TOE) Reference</h1>
      <p class="section-subtitle">Please describe the Target of Evaluation references</p>
    </div>
    <div class="card">
      <form class="form-grid" @submit.prevent>
        <label>
          <span>TOE Name</span>
          <RichTextEditor v-model="fields.toeName" placeholder="Describe the TOE name" />
        </label>
        <label>
          <span>TOE Version</span>
          <RichTextEditor v-model="fields.toeVersion" placeholder="Provide the TOE version" />
        </label>
        <label>
          <span>TOE Identification</span>
          <RichTextEditor v-model="fields.toeIdentification" placeholder="Describe TOE identification details" />
        </label>
        <label>
          <span>TOE Type</span>
          <RichTextEditor v-model="fields.toeType" placeholder="Describe the TOE type" />
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
const fields = sessionStore.toeReference
const isReady = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

function buildHtml(): string {
  return `
    <h3>1.2 TOE Reference</h3>
    <table>
      <tr><th>TOE Name</th><td>${ensureParagraph(fields.toeName)}</td></tr>
      <tr><th>TOE Version</th><td>${ensureParagraph(fields.toeVersion)}</td></tr>
      <tr><th>TOE Identification</th><td>${ensureParagraph(fields.toeIdentification)}</td></tr>
      <tr><th>TOE Type</th><td>${ensureParagraph(fields.toeType)}</td></tr>
    </table>
    <p>Table 2 TOE reference</p>
  `
}

async function persist() {
  if (!isReady.value) return
  const html = buildHtml()
  fields.html = html
  try {
    await sessionStore.saveSection('toeReference', {
      data: {
        toeName: fields.toeName,
        toeVersion: fields.toeVersion,
        toeIdentification: fields.toeIdentification,
        toeType: fields.toeType,
      },
      html,
    })
  } catch (error) {
    console.error('Failed to persist TOE Reference data', error)
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
    () => fields.toeName,
    () => fields.toeVersion,
    () => fields.toeIdentification,
    () => fields.toeType,
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 500;
}
</style>
