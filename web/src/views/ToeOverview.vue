<template>
  <div class="st-intro-page">
    <div class="card section-header">
      <h1>TOE Overview</h1>
      <p class="section-subtitle">Please provide an overview of your TOE</p>
    </div>
    <div class="card">
      <form class="form-grid" @submit.prevent>
        <label class="full-width">
          <span>TOE Overview</span>
          <RichTextEditor
            v-model="fields.overview"
            placeholder="Describe your TOE in short (~100 words)"
          />
        </label>
        <label class="full-width">
          <span>TOE Type</span>
          <RichTextEditor
            v-model="fields.toeType"
            placeholder="Describe the TOE type, device kind, functions, and features (~200 words)"
          />
        </label>
        <label class="full-width">
          <span>TOE Usage</span>
          <RichTextEditor
            v-model="fields.toeUsage"
            placeholder="Describe how the TOE will be used and its intended environment"
          />
        </label>
        <label class="full-width">
          <span>TOE Major Security Features</span>
          <RichTextEditor
            v-model="fields.securityFeatures"
            placeholder="Describe the TOE's major security features"
          />
        </label>
        <label class="full-width">
          <span>Non-TOE Hardware/Software/Firmware</span>
          <RichTextEditor
            v-model="fields.nonToe"
            placeholder="Describe hardware/software/firmware excluded from the TOE"
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
const fields = sessionStore.toeOverview
const isReady = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

function buildHtml(): string {
  return `
    <h3>1.3 TOE Overview</h3>
    ${ensureParagraph(fields.overview)}
    <h4>1.3.1 TOE Type</h4>
    ${ensureParagraph(fields.toeType)}
    <h4>1.3.2 TOE Usage</h4>
    ${ensureParagraph(fields.toeUsage)}
    <h4>1.3.3 TOE Major Security Features</h4>
    ${ensureParagraph(fields.securityFeatures)}
    <h4>1.3.4 Non-TOE Hardware/Software/Firmware</h4>
    ${ensureParagraph(fields.nonToe)}
  `
}

async function persist() {
  if (!isReady.value) return
  const html = buildHtml()
  fields.html = html
  try {
    await sessionStore.saveSection('toeOverview', {
      data: {
        overview: fields.overview,
        toeType: fields.toeType,
        toeUsage: fields.toeUsage,
        securityFeatures: fields.securityFeatures,
        nonToe: fields.nonToe,
      },
      html,
    })
  } catch (error) {
    console.error('Failed to persist TOE Overview data', error)
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
    () => fields.overview,
    () => fields.toeType,
    () => fields.toeUsage,
    () => fields.securityFeatures,
    () => fields.nonToe,
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
