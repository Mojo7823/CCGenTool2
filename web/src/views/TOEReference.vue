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
          <RichTextEditor
            v-model="form.toeName"
            placeholder="Enter TOE Name"
            min-height="140px"
          />
        </div>

        <div class="form-group">
          <label for="toeVersion">TOE Version:</label>
          <RichTextEditor
            v-model="form.toeVersion"
            placeholder="Enter TOE Version"
            min-height="140px"
          />
        </div>

        <div class="form-group">
          <label for="toeIdentification">TOE Identification:</label>
          <RichTextEditor
            v-model="form.toeIdentification"
            placeholder="Enter TOE Identification"
            min-height="160px"
          />
        </div>

        <div class="form-group">
          <label for="toeType">TOE Type:</label>
          <RichTextEditor
            v-model="form.toeType"
            placeholder="Enter TOE Type"
            min-height="160px"
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
  toeName: '',
  toeVersion: '',
  toeIdentification: '',
  toeType: ''
})

const initialized = ref(false)

function saveSessionData() {
  sessionService.saveTOEReferenceData({
    toeName: form.toeName,
    toeVersion: form.toeVersion,
    toeIdentification: form.toeIdentification,
    toeType: form.toeType
  })
}

function loadSessionData() {
  const data = sessionService.loadTOEReferenceData()
  if (data) {
    form.toeName = data.toeName
    form.toeVersion = data.toeVersion
    form.toeIdentification = data.toeIdentification
    form.toeType = data.toeType
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
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 600;
}
</style>
