<template>
  <div class="page">
    <div class="card">
      <header class="card-header">
        <div>
          <h1>Target of Evaluation (TOE) Description</h1>
          <p class="subtitle">Describe the TOE physical and logical boundary scope</p>
        </div>
        <span class="status" :class="statusClass">{{ statusMessage }}</span>
      </header>
      <section class="form-grid">
        <RichTextEditor
          label="TOE Physical Scope"
          v-model="data.physicalScope"
          placeholder="Describe the TOE physical scope"
        />
        <RichTextEditor
          label="TOE Logical Scope"
          v-model="data.logicalScope"
          placeholder="Describe the TOE logical scope"
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
import { buildToeDescriptionHtml } from '../utils/stIntroductionHtml'
import { saveSectionHtml } from '../services/stIntroductionService'
import RichTextEditor from '../components/RichTextEditor.vue'

const stStore = useStIntroductionStore()
const { toeDescription: data } = storeToRefs(stStore)
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
    const html = buildToeDescriptionHtml(data.value)
    await saveSectionHtml(userId.value, 'toe-description', html)
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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
