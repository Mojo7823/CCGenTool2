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
          <RichTextEditor
            v-model="form.toeOverview"
            placeholder="Enter TOE Overview (~100 words)"
            min-height="180px"
          />
        </div>

        <div class="form-section">
          <h3>TOE Type</h3>
          <p class="section-description">Please describe your TOE Type (What kind of device, its function, and its features), Short description (~200 Words)</p>
          <RichTextEditor
            v-model="form.toeType"
            placeholder="Enter TOE Type description (~200 words)"
            min-height="220px"
          />
        </div>

        <div class="form-section">
          <h3>TOE Usage</h3>
          <p class="section-description">Please describe how your TOE will be used and its intended environment</p>
          <RichTextEditor
            v-model="form.toeUsage"
            placeholder="Enter TOE Usage description"
            min-height="220px"
          />
        </div>

        <div class="form-section">
          <h3>TOE Major Security Features</h3>
          <p class="section-description">Please describe what security features that your TOE have (Firewall, Security Management, Encryption, etc)</p>
          <RichTextEditor
            v-model="form.toeMajorSecurityFeatures"
            placeholder="Enter TOE Major Security Features"
            min-height="220px"
          />
        </div>

        <div class="form-section">
          <h3>Non-TOE Hardware/Software/Firmware</h3>
          <p class="section-description">Please describe what Hardware/Software/Firmware that will be excluded as TOE (Excluded for evaluation)</p>
          <RichTextEditor
            v-model="form.nonToeHardwareSoftwareFirmware"
            placeholder="Enter Non-TOE Hardware/Software/Firmware"
            min-height="220px"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, watch } from 'vue'
import { sessionService } from '../services/sessionService'
import RichTextEditor from '../components/RichTextEditor.vue'

const form = reactive({
  toeOverview: '',
  toeType: '',
  toeUsage: '',
  toeMajorSecurityFeatures: '',
  nonToeHardwareSoftwareFirmware: ''
})

function saveSessionData() {
  sessionService.saveTOEOverviewData({
    toeOverview: form.toeOverview,
    toeType: form.toeType,
    toeUsage: form.toeUsage,
    toeMajorSecurityFeatures: form.toeMajorSecurityFeatures,
    nonToeHardwareSoftwareFirmware: form.nonToeHardwareSoftwareFirmware
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEOverviewData()
  if (data) {
    form.toeOverview = data.toeOverview
    form.toeType = data.toeType
    form.toeUsage = data.toeUsage
    form.toeMajorSecurityFeatures = data.toeMajorSecurityFeatures
    form.nonToeHardwareSoftwareFirmware = data.nonToeHardwareSoftwareFirmware
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
  max-width: 1000px;
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


.rich-text-editor {
  max-width: 100%;
}
</style>
