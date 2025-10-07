<template>
  <div class="toe-overview-page">
    <div class="card page-header">
      <div>
        <h1>TOE Overview</h1>
        <p>Please describe your TOE across the sections below.</p>
      </div>
      <div class="save-status" :class="[`state-${saveStatus.state}`, { empty: !saveStatus.text }]" role="status" aria-live="polite">
        {{ saveStatus.text || ' ' }}
      </div>
    </div>

    <div class="card content">
      <section class="editor-section">
        <h2>TOE Overview</h2>
        <p class="hint">Please describe your TOE in a short sentence (~100 words).</p>
        <RichTextEditor v-model="form.overview" placeholder="Provide an overview of the TOE" />
      </section>

      <section class="editor-section">
        <h2>TOE Type</h2>
        <p class="hint">Describe your TOE Type (device, function, features) in a short description (~200 words).</p>
        <RichTextEditor v-model="form.toe_type" placeholder="Describe the TOE type" />
      </section>

      <section class="editor-section">
        <h2>TOE Usage</h2>
        <p class="hint">Describe how your TOE will be used and its intended environment.</p>
        <RichTextEditor v-model="form.toe_usage" placeholder="Describe the TOE usage" />
      </section>

      <section class="editor-section">
        <h2>TOE Major Security Features</h2>
        <p class="hint">List and describe the major security features (firewall, encryption, management, etc.).</p>
        <RichTextEditor v-model="form.toe_security_features" placeholder="Describe security features" />
      </section>

      <section class="editor-section">
        <h2>Non-TOE Hardware/Software/Firmware</h2>
        <p class="hint">Describe the hardware/software/firmware excluded from the TOE (excluded from evaluation).</p>
        <RichTextEditor v-model="form.non_toe" placeholder="Describe non-TOE elements" />
      </section>

      <p v-if="loadError" class="load-error">{{ loadError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import RichTextEditor from '../components/RichTextEditor.vue'
import { useStSection } from '../composables/useStSection'
import { fetchToeOverviewSection, saveToeOverviewSection } from '../services/stIntroductionApi'
import type { ToeOverviewFormData } from '../types/st-introduction'

const { form, saveStatus, loadError } = useStSection<ToeOverviewFormData>({
  sectionKey: 'toe-overview',
  defaults: () => ({
    overview: '',
    toe_type: '',
    toe_usage: '',
    toe_security_features: '',
    non_toe: '',
  }),
  fetchSection: async (userId: string) => (await fetchToeOverviewSection(userId)).data,
  saveSection: (userId: string, data: ToeOverviewFormData) => saveToeOverviewSection(userId, data),
})
</script>

<style scoped>
.toe-overview-page {
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
  margin: 0 0 4px 0;
}

.hint {
  margin: 0 0 12px 0;
  color: var(--muted);
}

.load-error {
  margin-top: 8px;
  color: var(--danger);
}
</style>
