<template>
  <div class="toe-reference-page">
    <div class="card toe-reference-menubar">
      <div class="toe-reference-menubar-left">
        <h1>Target of Evaluation (TOE) Reference</h1>
        <span class="menubar-subtitle">Please describe the Target of Evaluation references</span>
      </div>
    </div>

    <div class="card toe-reference-body">
      <form class="toe-reference-form">
        <div class="form-group">
          <label for="toeName">TOE Name:</label>
          <TipTapEditor v-model="form.toeName" placeholder="Enter TOE Name" />
        </div>

        <div class="form-group">
          <label for="toeVersion">TOE Version:</label>
          <TipTapEditor v-model="form.toeVersion" placeholder="Enter TOE Version" />
        </div>

        <div class="form-group">
          <label for="toeIdentification">TOE Identification:</label>
          <TipTapEditor v-model="form.toeIdentification" placeholder="Enter TOE Identification" />
        </div>

        <div class="form-group">
          <label for="toeType">TOE Type:</label>
          <TipTapEditor v-model="form.toeType" placeholder="Enter TOE Type" />
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
  toeName: '',
  toeVersion: '',
  toeIdentification: '',
  toeType: ''
})

function saveSessionData() {
  sessionService.saveTOEReferenceData({
    toeName: form.value.toeName,
    toeVersion: form.value.toeVersion,
    toeIdentification: form.value.toeIdentification,
    toeType: form.value.toeType
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEReferenceData()
  if (data) {
    form.value.toeName = data.toeName
    form.value.toeVersion = data.toeVersion
    form.value.toeIdentification = data.toeIdentification
    form.value.toeType = data.toeType
  }
}

watch(form, () => {
  saveSessionData()
}, { deep: true })

watch(form, () => {
  saveSessionData()
}, { deep: true })

onMounted(() => {
  loadSessionData()
})
</script>

<style scoped>
.toe-reference-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toe-reference-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toe-reference-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.toe-reference-body {
  padding: 24px;
}

.toe-reference-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1200px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text);
}
</style>
