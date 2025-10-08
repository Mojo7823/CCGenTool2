<template>
  <div class="st-page">
    <div class="card intro-card">
      <h1>Target of Evaluation (TOE) Reference</h1>
      <p>Please describe the Target of Evaluation references.</p>
    </div>

    <div class="card form-card">
      <div class="field">
        <span class="field-label">TOE Name</span>
        <RichTextEditor v-model="form.toe_name" placeholder="Describe the TOE name" />
      </div>
      <div class="field">
        <span class="field-label">TOE Version</span>
        <RichTextEditor v-model="form.toe_version" placeholder="Describe the TOE version" />
      </div>
      <div class="field">
        <span class="field-label">TOE Identification</span>
        <RichTextEditor v-model="form.toe_identification" placeholder="Describe the TOE identification" />
      </div>
      <div class="field">
        <span class="field-label">TOE Type</span>
        <RichTextEditor v-model="form.toe_type" placeholder="Describe the TOE type" />
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
import { saveToeReference } from '../services/stIntroduction'

const session = useSessionStore()

const form = reactive({
  toe_name: '',
  toe_version: '',
  toe_identification: '',
  toe_type: '',
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
      toe_name: form.toe_name,
      toe_version: form.toe_version,
      toe_identification: form.toe_identification,
      toe_type: form.toe_type,
    }
    const result = await saveToeReference(payload)
    session.updateToeReference(result)
    lastSaved.value = new Date()
  } catch (error: any) {
    console.error('Failed to save TOE Reference', error)
    saveError.value = error?.response?.data?.detail || 'Unable to save data.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  session.ensureUserId()
  await session.loadSession()
  Object.assign(form, session.toeReference.rich_text)
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

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-weight: 600;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
