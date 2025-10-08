<template>
  <div class="st-reference-page">
    <div class="card st-reference-menubar">
      <div class="st-reference-menubar-left">
        <h1>Security Target (ST) Reference</h1>
        <span class="menubar-subtitle">Please describe the Security target references</span>
      </div>
    </div>

    <div class="card st-reference-body">
      <form class="st-reference-form">
        <div class="form-group">
          <label for="stTitle">ST Title:</label>
          <input
            id="stTitle"
            v-model="form.stTitle"
            type="text"
            class="input"
            placeholder="Enter ST Title"
          />
        </div>

        <div class="form-group">
          <label for="stVersion">ST Version:</label>
          <input
            id="stVersion"
            v-model="form.stVersion"
            type="text"
            class="input"
            placeholder="Enter ST Version"
          />
        </div>

        <div class="form-group">
          <label for="stDate">ST Date:</label>
          <input
            id="stDate"
            v-model="form.stDate"
            type="date"
            class="input"
          />
        </div>

        <div class="form-group">
          <label for="author">Author:</label>
          <textarea
            id="author"
            v-model="form.author"
            class="input textarea"
            placeholder="Enter Author(s)"
            rows="4"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, watch } from 'vue'
import { sessionService } from '../services/sessionService'

const form = reactive({
  stTitle: '',
  stVersion: '',
  stDate: '',
  author: ''
})

function saveSessionData() {
  sessionService.saveSTReferenceData({
    stTitle: form.stTitle,
    stVersion: form.stVersion,
    stDate: form.stDate,
    author: form.author
  })
}

function loadSessionData() {
  const data = sessionService.loadSTReferenceData()
  if (data) {
    form.stTitle = data.stTitle
    form.stVersion = data.stVersion
    form.stDate = data.stDate
    form.author = data.author
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
.st-reference-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.st-reference-menubar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.st-reference-menubar-left h1 {
  margin: 0;
}

.menubar-subtitle {
  color: var(--muted);
}

.st-reference-body {
  padding: 24px;
}

.st-reference-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
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

.input {
  padding: 10px 14px;
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}
</style>
