<template>
  <div class="toe-overview-page">
    <div class="card toe-overview-menubar">
      <div class="toe-overview-menubar-left">
        <h1>TOE Overview</h1>
        <span class="menubar-subtitle">Please describe your TOE and its features</span>
      </div>
    </div>

    <div class="card toe-overview-body">
      <form class="toe-overview-form">
        <div class="form-section">
          <h3>TOE Overview</h3>
          <p class="section-description">Please describe your TOE in short sentence (~100 words)</p>
          <TipTapEditor v-model="form.toeOverview" placeholder="Enter TOE Overview (~100 words)" />
        </div>

        <div class="form-section">
          <h3>TOE Type</h3>
          <p class="section-description">Please describe your TOE Type (What kind of device, its function, and its features), Short description (~200 Words)</p>
          <TipTapEditor v-model="form.toeType" placeholder="Enter TOE Type description (~200 words)" />
        </div>

        <div class="form-section">
          <h3>TOE Usage</h3>
          <p class="section-description">Please describe how your TOE will be used and its intended environment</p>
          <TipTapEditor v-model="form.toeUsage" placeholder="Enter TOE Usage description" />
        </div>

        <div class="form-section">
          <h3>TOE Major Security Features</h3>
          <p class="section-description">Please describe what security features that your TOE have (Firewall, Security Management, Encryption, etc)</p>
          <TipTapEditor v-model="form.toeMajorSecurityFeatures" placeholder="Enter TOE Major Security Features" />
        </div>

        <div class="form-section">
          <h3>Non-TOE Hardware/Software/Firmware</h3>
          <p class="section-description">Please describe what Hardware/Software/Firmware that will be excluded as TOE (Excluded for evaluation)</p>
          <TipTapEditor v-model="form.nonToeHardwareSoftwareFirmware" placeholder="Enter Non-TOE Hardware/Software/Firmware" />
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
  toeOverview: '',
  toeType: '',
  toeUsage: '',
  toeMajorSecurityFeatures: '',
  nonToeHardwareSoftwareFirmware: ''
})

function saveSessionData() {
  sessionService.saveTOEOverviewData({
    toeOverview: form.value.toeOverview,
    toeType: form.value.toeType,
    toeUsage: form.value.toeUsage,
    toeMajorSecurityFeatures: form.value.toeMajorSecurityFeatures,
    nonToeHardwareSoftwareFirmware: form.value.nonToeHardwareSoftwareFirmware
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEOverviewData()
  if (data) {
    form.value.toeOverview = data.toeOverview
    form.value.toeType = data.toeType
    form.value.toeUsage = data.toeUsage
    form.value.toeMajorSecurityFeatures = data.toeMajorSecurityFeatures
    form.value.nonToeHardwareSoftwareFirmware = data.nonToeHardwareSoftwareFirmware
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
.toe-overview-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toe-overview-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toe-overview-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.toe-overview-body {
  padding: 24px;
}

.toe-overview-form {
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

.section-description {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}
</style>
