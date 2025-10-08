<template>
  <div class="toe-description-page">
    <div class="card toe-description-menubar">
      <div class="toe-description-menubar-left">
        <h1>Target of Evaluation (TOE) Description</h1>
        <span class="menubar-subtitle">Please describe your Target of Evaluation (TOE) Physical boundary scope and Logical boundary scope</span>
      </div>
    </div>

    <div class="card toe-description-body">
      <form class="toe-description-form">
        <div class="form-section">
          <h3>TOE Physical Scope:</h3>
          <TipTapEditor v-model="form.toePhysicalScope" placeholder="Enter TOE Physical Scope description" />
        </div>

        <div class="form-section">
          <h3>TOE Logical Scope:</h3>
          <TipTapEditor v-model="form.toeLogicalScope" placeholder="Enter TOE Logical Scope description" />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { sessionService } from '../services/sessionService'
import TipTapEditor from '../components/editor/TipTapEditor.vue'

const form = ref({
  toePhysicalScope: '',
  toeLogicalScope: ''
})

function saveSessionData() {
  sessionService.saveTOEDescriptionData({
    toePhysicalScope: form.value.toePhysicalScope,
    toeLogicalScope: form.value.toeLogicalScope
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEDescriptionData()
  if (data) {
    form.value.toePhysicalScope = data.toePhysicalScope
    form.value.toeLogicalScope = data.toeLogicalScope
  }
}

watch(form, () => {
  saveSessionData()
}, { deep: true })

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.toe-description-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toe-description-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toe-description-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.toe-description-body {
  padding: 24px;
}

.toe-description-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 1200px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-section h3 {
  margin: 0;
  color: var(--text);
  font-size: 18px;
}
</style>
