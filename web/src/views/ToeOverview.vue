<template>
  <div class="st-page">
    <div class="card intro-card">
      <h1>TOE Overview</h1>
      <p>Please provide high-level information about your TOE.</p>
    </div>

    <div class="card form-card">
      <div class="section">
        <div class="section-header">
          <h2>TOE Overview</h2>
          <p>Please describe your TOE in a short sentence (~100 words).</p>
        </div>
        <RichTextEditor v-model="form.overview" placeholder="Provide a short TOE overview" />
      </div>

      <div class="section">
        <div class="section-header">
          <h2>TOE Type</h2>
          <p>Please describe your TOE Type (device, function, features) in ~200 words.</p>
        </div>
        <RichTextEditor v-model="form.toe_type" placeholder="Describe the TOE type" />
      </div>

      <div class="section">
        <div class="section-header">
          <h2>TOE Usage</h2>
          <p>Please describe how your TOE will be used and its intended environment.</p>
        </div>
        <RichTextEditor v-model="form.toe_usage" placeholder="Describe TOE usage" />
      </div>

      <div class="section">
        <div class="section-header">
          <h2>TOE Major Security Features</h2>
          <p>Describe the security features your TOE provides (e.g., firewall, encryption).</p>
        </div>
        <RichTextEditor v-model="form.toe_security_features" placeholder="List TOE security features" />
      </div>

      <div class="section">
        <div class="section-header">
          <h2>Non-TOE Hardware/Software/Firmware</h2>
          <p>Describe hardware/software/firmware excluded from the TOE (not evaluated).</p>
        </div>
        <RichTextEditor v-model="form.non_toe_hw" placeholder="Describe non-TOE hardware/software/firmware" />
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
import { saveToeOverview } from '../services/stIntroduction'

const session = useSessionStore()

const form = reactive({
  overview: '',
  toe_type: '',
  toe_usage: '',
  toe_security_features: '',
  non_toe_hw: '',
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
      overview: form.overview,
      toe_type: form.toe_type,
      toe_usage: form.toe_usage,
      toe_security_features: form.toe_security_features,
      non_toe_hw: form.non_toe_hw,
    }
    const result = await saveToeOverview(payload)
    session.updateToeOverview(result)
    lastSaved.value = new Date()
  } catch (error: any) {
    console.error('Failed to save TOE Overview', error)
    saveError.value = error?.response?.data?.detail || 'Unable to save data.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  session.ensureUserId()
  await session.loadSession()
  Object.assign(form, session.toeOverview.fields)
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
