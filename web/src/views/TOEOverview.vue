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
            min-height="160px"
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
import { onMounted, reactive, ref, watch } from 'vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import { sessionService } from '../services/sessionService'

const form = reactive({
  toeOverview: '',
  toeType: '',
  toeUsage: '',
  toeMajorSecurityFeatures: '',
  nonToeHardwareSoftwareFirmware: ''
})

const initialized = ref(false)

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

watch(
  form,
  () => {
    if (!initialized.value) return
    saveSessionData()
  },
  { deep: true }
)

onMounted(() => {
  loadSessionData()
  initialized.value = true
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
}

.toe-overview-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: rgba(148, 163, 184, 0.9);
}

.toe-overview-body {
  padding: 24px;
}

.toe-overview-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section h3 {
  margin-bottom: 8px;
}

.section-description {
  margin: 0 0 12px 0;
  color: rgba(148, 163, 184, 0.9);
}
</style>
