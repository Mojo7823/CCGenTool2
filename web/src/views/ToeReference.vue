<template>
  <div class="page">
    <div class="card">
      <header class="card-header">
        <div>
          <h1>Target of Evaluation (TOE) Reference</h1>
          <p class="subtitle">Please describe the Target of Evaluation references</p>
        </div>
        <span class="status" :class="statusClass">{{ statusMessage }}</span>
      </header>
      <section class="form-grid">
        <RichTextEditor
          label="TOE Name"
          v-model="data.toeName"
          placeholder="Enter TOE name"
        />
        <RichTextEditor
          label="TOE Version"
          v-model="data.toeVersion"
          placeholder="Enter TOE version"
        />
        <RichTextEditor
          label="TOE Identification"
          v-model="data.toeIdentification"
          placeholder="Describe the TOE identification"
        />
        <RichTextEditor
          label="TOE Type"
          v-model="data.toeType"
          placeholder="Describe the TOE type"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useStIntroductionStore } from '../stores/stIntroduction'
import { getOrCreateUserId } from '../utils/user'
import { debounce } from '../utils/debounce'
import { buildToeReferenceHtml } from '../utils/stIntroductionHtml'
import { saveSectionHtml } from '../services/stIntroductionService'
import RichTextEditor from '../components/RichTextEditor.vue'

const stStore = useStIntroductionStore()
const { toeReference: data } = storeToRefs(stStore)
const userId = ref(getOrCreateUserId())

const status = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const statusMessage = computed(() => {
  switch (status.value) {
    case 'saving':
      return 'Saving…'
    case 'saved':
      return 'Saved'
    case 'error':
      return 'Save failed'
    default:
      return ''
  }
})
const statusClass = computed(() => `status-${status.value}`)

const persistSection = debounce(async () => {
  if (!userId.value) return
  status.value = 'saving'
  try {
    const html = buildToeReferenceHtml(data.value)
    await saveSectionHtml(userId.value, 'toe-reference', html)
    status.value = 'saved'
  } catch (error) {
    status.value = 'error'
  }
})

watch(data, () => {
  persistSection()
}, { deep: true })

persistSection()
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.subtitle {
  margin: 4px 0 0;
  color: var(--muted);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.status {
  font-size: 0.95rem;
  font-weight: 500;
}

.status-idle {
  color: transparent;
}

.status-saving {
  color: var(--muted);
}

.status-saved {
  color: #34d399;
}

.status-error {
  color: #f87171;
}
</style>
