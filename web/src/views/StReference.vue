<template>
  <div class="st-intro-page">
    <div class="card section-header">
      <h1>Security Target (ST) Reference</h1>
      <p class="section-subtitle">Please describe the Security target references</p>
    </div>
    <div class="card">
      <form class="form-grid" @submit.prevent>
        <label>
          <span>ST Title</span>
          <input class="input" v-model="fields.title" type="text" placeholder="Enter the Security Target title" />
        </label>
        <label>
          <span>ST Version</span>
          <input class="input" v-model="fields.version" type="text" placeholder="Enter the version" />
        </label>
        <label>
          <span>ST Date</span>
          <input class="input" v-model="fields.date" type="date" />
        </label>
        <label class="full-width">
          <span>Author</span>
          <textarea
            class="input textarea"
            v-model="fields.author"
            placeholder="List the authors contributing to the Security Target"
          ></textarea>
        </label>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useSessionStore } from '../stores/session'
import { formatMultilineText, safeText } from '../utils/html'

const sessionStore = useSessionStore()
const fields = sessionStore.stReference
const isReady = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

function buildHtml(): string {
  const title = safeText(fields.title)
  const version = safeText(fields.version)
  const date = safeText(fields.date)
  const author = fields.author.trim() ? formatMultilineText(fields.author) : '—'

  return `
    <h2>1. Security Target Introduction</h2>
    <p>This section presents the following information required for a Common Criteria (CC) evaluation:</p>
    <ul>
      <li>Identifies the Security Target (ST) and the Target of Evaluation (TOE)</li>
      <li>Specifies the security target conventions,</li>
      <li>Describes the organization of the security target</li>
    </ul>
    <h3>1.1 ST Reference</h3>
    <table>
      <tr><th>ST Title</th><td>${title}</td></tr>
      <tr><th>ST Version</th><td>${version}</td></tr>
      <tr><th>ST Date</th><td>${date}</td></tr>
      <tr><th>Author</th><td>${author}</td></tr>
    </table>
    <p>Table 1 Security Target reference</p>
  `
}

async function persist() {
  if (!isReady.value) return
  const html = buildHtml()
  fields.html = html
  try {
    await sessionStore.saveSection('stReference', {
      data: {
        title: fields.title,
        version: fields.version,
        date: fields.date,
        author: fields.author,
      },
      html,
    })
  } catch (error) {
    console.error('Failed to persist ST Reference data', error)
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
    () => fields.title,
    () => fields.version,
    () => fields.date,
    () => fields.author,
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

.textarea {
  min-height: 160px;
  resize: vertical;
}

.full-width {
  grid-column: 1 / -1;
}
</style>
