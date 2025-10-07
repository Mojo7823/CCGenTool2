<template>
  <div class="toe-description-page">
    <div class="card page-header">
      <div>
        <h1>Target of Evaluation (TOE) Description</h1>
        <p>Please describe your TOE physical boundary scope and logical boundary scope.</p>
      </div>
      <div class="save-status" :class="[`state-${saveStatus.state}`, { empty: !saveStatus.text }]" role="status" aria-live="polite">
        {{ saveStatus.text || ' ' }}
      </div>
    </div>

    <div class="card content">
      <section class="editor-section">
        <h2>TOE Physical Scope</h2>
        <RichTextEditor v-model="form.physical_scope" placeholder="Describe the TOE physical scope" />
      </section>

      <section class="editor-section">
        <h2>TOE Logical Scope</h2>
        <RichTextEditor v-model="form.logical_scope" placeholder="Describe the TOE logical scope" />
      </section>

      <p v-if="loadError" class="load-error">{{ loadError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import RichTextEditor from '../components/RichTextEditor.vue'
import { useStSection } from '../composables/useStSection'
import { fetchToeDescriptionSection, saveToeDescriptionSection } from '../services/stIntroductionApi'
import type { ToeDescriptionFormData } from '../types/st-introduction'

const { form, saveStatus, loadError } = useStSection<ToeDescriptionFormData>({
  sectionKey: 'toe-description',
  defaults: () => ({
    physical_scope: '',
    logical_scope: '',
  }),
  fetchSection: async (userId: string) => (await fetchToeDescriptionSection(userId)).data,
  saveSection: (userId: string, data: ToeDescriptionFormData) => saveToeDescriptionSection(userId, data),
})
</script>

<style scoped>
.toe-description-page {
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
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 24px;
}

.editor-section h2 {
  margin: 0 0 12px 0;
}

.load-error {
  margin-top: 8px;
  color: var(--danger);
}
</style>
