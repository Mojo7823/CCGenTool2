<template>
  <div class="page">
    <div class="card">
      <header class="card-header">
        <div>
          <h1>TOE Overview</h1>
          <p class="subtitle">Provide an overview of your TOE and its characteristics</p>
        </div>
        <span class="status" :class="statusClass">{{ statusMessage }}</span>
      </header>
      <section class="form-grid">
        <RichTextEditor
          label="TOE Overview"
          v-model="data.overview"
          placeholder="Describe your TOE in ~100 words"
        />
        <RichTextEditor
          label="TOE Type"
          v-model="data.toeType"
          placeholder="Describe your TOE type and features (~200 words)"
        />
        <RichTextEditor
          label="TOE Usage"
          v-model="data.usage"
          placeholder="Describe how your TOE will be used and its intended environment"
        />
        <RichTextEditor
          label="TOE Major Security Features"
          v-model="data.securityFeatures"
          placeholder="Describe the major security features of your TOE"
        />
        <RichTextEditor
          label="Non-TOE Hardware/Software/Firmware"
          v-model="data.nonToe"
          placeholder="List excluded hardware/software/firmware"
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
import { buildToeOverviewHtml } from '../utils/stIntroductionHtml'
import { saveSectionHtml } from '../services/stIntroductionService'
import RichTextEditor from '../components/RichTextEditor.vue'

const stStore = useStIntroductionStore()
const { toeOverview: data } = storeToRefs(stStore)
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
    const html = buildToeOverviewHtml(data.value)
    await saveSectionHtml(userId.value, 'toe-overview', html)
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
