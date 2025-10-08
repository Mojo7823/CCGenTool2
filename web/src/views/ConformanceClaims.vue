<template>
  <div class="conformance-page">
    <div class="card conformance-header">
      <div>
        <h1>Conformance Claims</h1>
        <span class="subtitle">Write your TOE Conformance</span>
      </div>
    </div>

    <div class="card conformance-body">
      <section class="conformance-section">
        <h2>Common Criteria (CC) Conformance Claims</h2>
        <RichTextEditor
          v-model="form.ccConformance"
          placeholder="Describe the Common Criteria (CC) conformance claims"
          min-height="220px"
        />
      </section>

      <section class="conformance-section">
        <h2>Protection Profile (PP) Claims</h2>
        <RichTextEditor
          v-model="form.ppClaims"
          placeholder="Describe the Protection Profile (PP) claims"
          min-height="220px"
        />
      </section>

      <section class="conformance-section">
        <h2>Additional Notes</h2>
        <RichTextEditor
          v-model="form.additionalNotes"
          placeholder="Add any supplementary notes for the conformance claims"
          min-height="220px"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, watch } from 'vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import { sessionService } from '../services/sessionService'

const form = reactive({
  ccConformance: '',
  ppClaims: '',
  additionalNotes: '',
})

const saveSessionData = () => {
  sessionService.saveConformanceClaimsData({
    ccConformance: form.ccConformance,
    ppClaims: form.ppClaims,
    additionalNotes: form.additionalNotes,
  })
}

const loadSessionData = () => {
  const data = sessionService.loadConformanceClaimsData()
  if (data) {
    form.ccConformance = data.ccConformance
    form.ppClaims = data.ppClaims
    form.additionalNotes = data.additionalNotes
  }
}

watch(form, saveSessionData, { deep: true })

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.conformance-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.conformance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.conformance-header h1 {
  margin: 0;
}

.subtitle {
  color: var(--muted);
}

.conformance-body {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 24px;
}

.conformance-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.conformance-section h2 {
  margin: 0;
}
</style>
