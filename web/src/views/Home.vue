<template>
  <div class="card home-card">
    <h1 class="home-title">Welcome to Common Criteria Security Target Generation (CCGen) Tools</h1>
    <div class="home-actions">
      <RouterLink class="home-button primary" to="/settings">Open an existing Security Target Project</RouterLink>
      <RouterLink class="home-button" to="/st-intro/cover">Create New Security Target</RouterLink>
      <RouterLink class="home-button outline" to="/generator">Automatically Generate Security Target</RouterLink>
    </div>
    <div class="home-actions secondary">
      <button type="button" class="home-button" @click="saveProject">Save Project</button>
      <button type="button" class="home-button" @click="requestLoadProject">Load Project</button>
      <button type="button" class="home-button danger" @click="clearAllData">Clear Data</button>
    </div>
    <input
      ref="fileInput"
      type="file"
      class="hidden-input"
      accept="application/json"
      @change="handleFileSelection"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  applyProjectSnapshot,
  clearProjectData,
  downloadProjectSnapshot,
  loadProjectSnapshotFromFile,
} from '../services/projectPersistence'

const fileInput = ref<HTMLInputElement | null>(null)

const saveProject = () => {
  downloadProjectSnapshot()
}

const requestLoadProject = () => {
  fileInput.value?.click()
}

const handleFileSelection = async (event: Event) => {
  const target = event.target as HTMLInputElement | null
  const files = target?.files

  if (!files || files.length === 0) {
    return
  }

  const file = files[0]

  try {
    const snapshot = await loadProjectSnapshotFromFile(file)
    applyProjectSnapshot(snapshot)
    alert('Project data loaded successfully.')
  } catch (error: any) {
    console.error('Failed to load project snapshot', error)
    alert(error?.message || 'Failed to load project data. Please verify the selected file.')
  } finally {
    if (target) {
      target.value = ''
    }
  }
}

const clearAllData = () => {
  if (!confirm('Are you sure you want to clear all saved data? This action cannot be undone.')) {
    return
  }

  clearProjectData()
  alert('All project data has been cleared.')
}
</script>

<style scoped>
.home-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 32px;
  gap: 32px;
  min-height: 320px;
}

.home-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  max-width: 720px;
}

.home-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.home-actions.secondary {
  margin-top: 16px;
}

.home-button {
  text-decoration: none;
  padding: 14px 20px;
  border-radius: 10px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  min-width: 240px;
  text-align: center;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}

.home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.25);
}

.home-button.primary {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
}

.home-button.danger {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.5);
  color: #f87171;
}

.home-button.outline {
  background: transparent;
}

.home-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
}

.hidden-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
