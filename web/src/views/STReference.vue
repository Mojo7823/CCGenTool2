<template>
  <div class="page">
    <div class="card">
      <header class="card-header">
        <div>
          <h1>Security Target (ST) Reference</h1>
          <p class="subtitle">Please describe the Security Target references</p>
        </div>
        <span class="status" :class="statusClass">{{ statusMessage }}</span>
      </header>
      <section class="form-grid">
        <label>
          <span>ST Title</span>
          <input class="input" v-model="data.stTitle" type="text" placeholder="Enter ST Title" />
        </label>
        <label>
          <span>ST Version</span>
          <input class="input" v-model="data.stVersion" type="text" placeholder="Enter ST Version" />
        </label>
        <label>
          <span>ST Date</span>
          <input class="input" v-model="data.stDate" type="date" />
        </label>
        <label class="span-2">
          <span>Author</span>
          <textarea class="input textarea" v-model="data.author" rows="4" placeholder="Provide author details"></textarea>
        </label>
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
import { buildStReferenceHtml } from '../utils/stIntroductionHtml'
import { saveSectionHtml } from '../services/stIntroductionService'

const stStore = useStIntroductionStore()
const { stReference: data } = storeToRefs(stStore)
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
  const html = buildStReferenceHtml(data.value)
  status.value = 'saving'
  try {
    await saveSectionHtml(userId.value, 'st-reference', html)
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.span-2 {
  grid-column: span 2;
}

.textarea {
  resize: vertical;
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
