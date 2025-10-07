<template>
  <div class="st-reference-page">
    <div class="card page-header">
      <div>
        <h1>Security Target (ST) Reference</h1>
        <p>Please describe the Security target references.</p>
      </div>
      <div class="save-status" :class="[`state-${saveStatus.state}`, { empty: !saveStatus.text }]" role="status" aria-live="polite">
        {{ saveStatus.text || ' ' }}
      </div>
    </div>

    <div class="card content">
      <form class="form-grid" @submit.prevent>
        <label>
          <span>ST Title</span>
          <input class="input" type="text" v-model="form.st_title" placeholder="Enter ST title" />
        </label>
        <label>
          <span>ST Version</span>
          <input class="input" type="text" v-model="form.st_version" placeholder="Enter ST version" />
        </label>
        <label>
          <span>ST Date</span>
          <input class="input" type="date" v-model="form.st_date" />
        </label>
        <label class="full">
          <span>Author</span>
          <textarea class="input textarea" v-model="form.author" placeholder="Enter author details"></textarea>
        </label>
      </form>
      <p v-if="loadError" class="load-error">{{ loadError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStSection } from '../composables/useStSection'
import { fetchStReferenceSection, saveStReferenceSection } from '../services/stIntroductionApi'
import type { StReferenceFormData } from '../types/st-introduction'

const { form, saveStatus, loadError } = useStSection<StReferenceFormData>({
  sectionKey: 'st-reference',
  defaults: () => ({
    st_title: '',
    st_version: '',
    st_date: '',
    author: '',
  }),
  fetchSection: async (userId: string) => (await fetchStReferenceSection(userId)).data,
  saveSection: (userId: string, data: StReferenceFormData) => saveStReferenceSection(userId, data),
})
</script>

<style scoped>
.st-reference-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
}

.page-header p {
  margin: 0;
  color: var(--muted);
}

.save-status {
  min-width: 160px;
  text-align: right;
  font-size: 0.875rem;
  color: var(--muted);
  white-space: nowrap;
}

.save-status.empty {
  color: transparent;
}

.save-status.state-saving {
  color: var(--muted);
}

.save-status.state-error {
  color: var(--danger);
}

.save-status.state-saved {
  color: #34d399;
}

.content {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px 24px;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-grid label span {
  font-weight: 600;
}

.form-grid .full {
  grid-column: 1 / -1;
}

.textarea {
  min-height: 140px;
  resize: vertical;
}

.load-error {
  margin-top: 16px;
  color: var(--danger);
}
</style>
