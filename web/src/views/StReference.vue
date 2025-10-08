<template>
  <div class="st-page">
    <div class="card intro-card">
      <h1>Security Target (ST) Reference</h1>
      <p>Please describe the Security Target references.</p>
    </div>

    <div class="card form-card">
      <div class="form-grid">
        <div class="field">
          <span class="field-label">ST Title</span>
          <input class="input" v-model="form.st_title" type="text" placeholder="Enter ST title" />
        </div>
        <div class="field">
          <span class="field-label">ST Version</span>
          <input class="input" v-model="form.st_version" type="text" placeholder="Enter ST version" />
        </div>
        <div class="field">
          <span class="field-label">ST Date</span>
          <input class="input" v-model="form.st_date" type="date" />
        </div>
        <div class="field field-span">
          <span class="field-label">Author</span>
          <textarea class="input textarea" v-model="form.author" placeholder="Enter author information"></textarea>
        </div>
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
import { useSessionStore } from '../stores/session'
import { saveStReference } from '../services/stIntroduction'

const session = useSessionStore()

const form = reactive({
  st_title: '',
  st_version: '',
  st_date: '',
  author: '',
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
      st_title: form.st_title,
      st_version: form.st_version,
      st_date: form.st_date,
      author: form.author,
    }
    const result = await saveStReference(payload)
    session.updateStReference(result)
    lastSaved.value = new Date()
  } catch (error: any) {
    console.error('Failed to save ST Reference', error)
    saveError.value = error?.response?.data?.detail || 'Unable to save data.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  session.ensureUserId()
  await session.loadSession()

  Object.assign(form, session.stReference.fields)
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

.intro-card h1 {
  margin-bottom: 8px;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-span {
  grid-column: 1 / -1;
}

.field-label {
  font-weight: 600;
}

.textarea {
  min-height: 120px;
  resize: vertical;
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
