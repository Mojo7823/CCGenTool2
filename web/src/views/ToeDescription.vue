<template>
  <div class="st-page">
    <div class="card intro-card">
      <h1>Target of Evaluation (TOE) Description</h1>
      <p>Please describe your TOE physical boundary scope and logical boundary scope.</p>
    </div>

    <div class="card form-card">
      <div class="section">
        <div class="section-header">
          <h2>TOE Physical Scope</h2>
          <p>Describe the physical scope of the TOE.</p>
        </div>
        <RichTextEditor v-model="form.physical_scope" placeholder="Describe the TOE physical scope" />
      </div>

      <div class="section">
        <div class="section-header">
          <h2>TOE Logical Scope</h2>
          <p>Describe the logical scope of the TOE.</p>
        </div>
        <RichTextEditor v-model="form.logical_scope" placeholder="Describe the TOE logical scope" />
      </div>

      <div class="save-status" :class="{ saving, error: !!saveError }">
        <span v-if="saveError">{{ saveError }}</span>
        <span v-else-if="saving">Saving…</span>
        <span v-else-if="lastSaved">Saved {{ lastSavedLabel }}</span>
        <span v-else>Changes are saved automatically.</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import { useSessionStore } from '../stores/session'
import { saveToeDescription } from '../services/stIntroduction'

const session = useSessionStore()

const form = reactive({
  physical_scope: '',
  logical_scope: '',
})

const saving = ref(false)
const saveError = ref('')
const lastSaved = ref<Date | null>(null)
const ready = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

const lastSavedLabel = computed(() => {
  if (!lastSaved.value) return ''
  return lastSaved.value.toLocaleTimeString()
})

function scheduleSave() {
  if (!ready.value || !session.userId) return
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
  saveTimer = setTimeout(() => {
    void persist()
  }, 400)
}

async function persist() {
  if (!session.userId) return
  saving.value = true
  saveError.value = ''
  try {
    const payload = {
      user_id: session.userId,
      physical_scope: form.physical_scope,
      logical_scope: form.logical_scope,
    }
    const result = await saveToeDescription(payload)
    session.updateToeDescription(result)
    lastSaved.value = new Date()
  } catch (error: any) {
    console.error('Failed to save TOE Description', error)
    saveError.value = error?.response?.data?.detail || 'Unable to save data.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  session.ensureUserId()
  await session.loadSession()
  Object.assign(form, session.toeDescription.fields)
  ready.value = true
})

onBeforeUnmount(() => {
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
})

watch(form, () => {
  if (!ready.value) return
  scheduleSave()
}, { deep: true })
</script>

<style scoped>
.st-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header h2 {
  margin: 0 0 4px;
}

.section-header p {
  margin: 0;
  color: var(--muted);
}

.save-status {
  font-size: 14px;
  color: var(--muted);
}

.save-status.saving {
  color: var(--text);
}

.save-status.error {
  color: var(--danger);
}
</style>
