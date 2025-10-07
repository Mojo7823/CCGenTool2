<template>
  <div class="toe-reference-page">
    <div class="card page-header">
      <div>
        <h1>Target of Evaluation (TOE) Reference</h1>
        <p>Please describe the Target of Evaluation references.</p>
      </div>
      <div class="save-status" :class="[`state-${saveStatus.state}`, { empty: !saveStatus.text }]" role="status" aria-live="polite">
        {{ saveStatus.text || ' ' }}
      </div>
    </div>

    <div class="card content">
      <div class="editor-grid">
        <label>
          <span>TOE Name</span>
          <RichTextEditor v-model="form.toe_name" placeholder="Describe the TOE name" />
        </label>
        <label>
          <span>TOE Version</span>
          <RichTextEditor v-model="form.toe_version" placeholder="Describe the TOE version" />
        </label>
        <label>
          <span>TOE Identification</span>
          <RichTextEditor v-model="form.toe_identification" placeholder="Describe the TOE identification" />
        </label>
        <label>
          <span>TOE Type</span>
          <RichTextEditor v-model="form.toe_type" placeholder="Describe the TOE type" />
        </label>
      </div>
      <p v-if="loadError" class="load-error">{{ loadError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import RichTextEditor from '../components/RichTextEditor.vue'
import { useStSection } from '../composables/useStSection'
import { fetchToeReferenceSection, saveToeReferenceSection } from '../services/stIntroductionApi'
import type { ToeReferenceFormData } from '../types/st-introduction'

const { form, saveStatus, loadError } = useStSection<ToeReferenceFormData>({
  sectionKey: 'toe-reference',
  defaults: () => ({
    toe_name: '',
    toe_version: '',
    toe_identification: '',
    toe_type: '',
  }),
  fetchSection: async (userId: string) => (await fetchToeReferenceSection(userId)).data,
  saveSection: (userId: string, data: ToeReferenceFormData) => saveToeReferenceSection(userId, data),
})
</script>

<style scoped>
.toe-reference-page {
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

.editor-grid {
  display: grid;
  gap: 24px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label span {
  font-weight: 600;
}

.load-error {
  margin-top: 16px;
  color: var(--danger);
}
</style>
