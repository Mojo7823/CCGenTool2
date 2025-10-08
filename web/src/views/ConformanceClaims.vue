<template>
  <div class="conformance-claims-page">
    <div class="card conformance-claims-menubar">
      <div class="conformance-claims-menubar-left">
        <h1>Conformance Claims</h1>
        <span class="menubar-subtitle">Write your TOE Conformance</span>
      </div>
    </div>

    <div class="card conformance-claims-body">
      <form class="conformance-claims-form">
        <div class="form-section">
          <h3>Common Criteria (CC) Conformance Claims</h3>
          <RichTextEditor
            v-model="form.ccConformance"
            placeholder="Enter Common Criteria Conformance Claims"
            min-height="260px"
          />
        </div>

        <div class="form-section">
          <h3>Protection Profile (PP) Claims</h3>
          <RichTextEditor
            v-model="form.ppClaims"
            placeholder="Enter Protection Profile Claims"
            min-height="260px"
          />
        </div>

        <div class="form-section">
          <h3>Additional Notes</h3>
          <RichTextEditor
            v-model="form.additionalNotes"
            placeholder="Enter Additional Notes"
            min-height="260px"
          />
        </div>
      </form>
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

function saveSessionData() {
  sessionService.saveConformanceClaimsData({
    ccConformance: form.ccConformance,
    ppClaims: form.ppClaims,
    additionalNotes: form.additionalNotes,
  })
}

function loadSessionData() {
  const data = sessionService.loadConformanceClaimsData()
  if (data) {
    form.ccConformance = data.ccConformance || ''
    form.ppClaims = data.ppClaims || ''
    form.additionalNotes = data.additionalNotes || ''
  }
}

watch(form, saveSessionData, { deep: true })

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.conformance-claims-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.conformance-claims-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.conformance-claims-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.conformance-claims-body {
  padding: 24px;
}

.conformance-claims-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 1000px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section h3 {
  margin: 0;
  color: var(--text);
  font-size: 18px;
}
</style>
