<template>
  <div class="card home-card">
    <h1 class="home-title">Welcome to Common Criteria Security Target Generation (CCGen) Tools</h1>
    <div class="home-actions">
      <RouterLink class="home-button primary" to="/settings">Open an existing Security Target Project</RouterLink>
      <RouterLink class="home-button" to="/st-intro/cover">Create New Security Target</RouterLink>
      <RouterLink class="home-button outline" to="/generator">Automatically Generate Security Target</RouterLink>
    </div>
    <div class="data-management">
      <h2>Project Management</h2>
      <div class="data-actions">
        <button class="btn primary" @click="saveProject">Save Project</button>
        <label for="file-input" class="btn">
          Load Project
          <input
            id="file-input"
            type="file"
            accept=".json"
            @change="loadProject"
            style="display: none"
          />
        </label>
        <button class="btn danger" @click="confirmClearData">Clear Data</button>
      </div>
      <p v-if="statusMessage" :class="['status-message', statusMessageType]">{{ statusMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { sessionService } from '../services/sessionService'

const statusMessage = ref('')
const statusMessageType = ref<'success' | 'error'>('success')

function showStatus(message: string, type: 'success' | 'error' = 'success') {
  statusMessage.value = message
  statusMessageType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

function saveProject() {
  try {
    const projectData = {
      coverData: sessionService.loadCoverData(),
      stReferenceData: sessionService.loadSTReferenceData(),
      toeReferenceData: sessionService.loadTOEReferenceData(),
      toeOverviewData: sessionService.loadTOEOverviewData(),
      toeDescriptionData: sessionService.loadTOEDescriptionData(),
      conformanceClaimsData: sessionService.loadConformanceClaimsData(),
      sfrData: sessionService.loadSfrData(),
      sarData: sessionService.loadSarData(),
      assumptionsData: sessionService.loadAssumptionsData(),
      threatsData: sessionService.loadThreatsData(),
      ospData: sessionService.loadOspData(),
      exportedAt: new Date().toISOString(),
    }

    const jsonStr = JSON.stringify(projectData, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `CCGenTool_Project_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    showStatus('Project saved successfully!', 'success')
  } catch (error) {
    console.error('Error saving project:', error)
    showStatus('Error saving project. Please try again.', 'error')
  }
}

function loadProject(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      const projectData = JSON.parse(content)

      // Load all data back into session storage
      if (projectData.coverData) {
        sessionService.saveCoverData(
          projectData.coverData.form,
          projectData.coverData.uploadedImagePath,
          projectData.coverData.uploadedImageData || null
        )
      }
      if (projectData.stReferenceData) {
        sessionService.saveSTReferenceData({
          stTitle: projectData.stReferenceData.stTitle,
          stVersion: projectData.stReferenceData.stVersion,
          stDate: projectData.stReferenceData.stDate,
          author: projectData.stReferenceData.author,
        })
      }
      if (projectData.toeReferenceData) {
        sessionService.saveTOEReferenceData({
          toeName: projectData.toeReferenceData.toeName,
          toeVersion: projectData.toeReferenceData.toeVersion,
          toeIdentification: projectData.toeReferenceData.toeIdentification,
          toeType: projectData.toeReferenceData.toeType,
        })
      }
      if (projectData.toeOverviewData) {
        sessionService.saveTOEOverviewData({
          toeOverview: projectData.toeOverviewData.toeOverview,
          toeType: projectData.toeOverviewData.toeType,
          toeUsage: projectData.toeOverviewData.toeUsage,
          toeMajorSecurityFeatures: projectData.toeOverviewData.toeMajorSecurityFeatures,
          nonToeHardwareSoftwareFirmware: projectData.toeOverviewData.nonToeHardwareSoftwareFirmware,
        })
      }
      if (projectData.toeDescriptionData) {
        sessionService.saveTOEDescriptionData({
          toeDescription: projectData.toeDescriptionData.toeDescription,
          toePhysicalScope: projectData.toeDescriptionData.toePhysicalScope,
          toeLogicalScope: projectData.toeDescriptionData.toeLogicalScope,
        })
      }
      if (projectData.conformanceClaimsData) {
        sessionService.saveConformanceClaimsData({
          ccConformance: projectData.conformanceClaimsData.ccConformance,
          ppClaims: projectData.conformanceClaimsData.ppClaims,
          additionalNotes: projectData.conformanceClaimsData.additionalNotes,
        })
      }
      if (projectData.sfrData) {
        sessionService.saveSfrData(
          projectData.sfrData.sfrList,
          projectData.sfrData.selectedSfrId,
          projectData.sfrData.nextSfrId
        )
      }
      if (projectData.sarData) {
        sessionService.saveSarData(
          projectData.sarData.sarList,
          projectData.sarData.selectedSarId,
          projectData.sarData.nextSarId,
          projectData.sarData.selectedEal
        )
      }
      if (projectData.assumptionsData) {
        const items = Array.isArray(projectData.assumptionsData.items)
          ? projectData.assumptionsData.items
          : []
        const nextId =
          typeof projectData.assumptionsData.nextId === 'number'
            ? projectData.assumptionsData.nextId
            : items.length + 1
        sessionService.saveAssumptionsData(items, nextId)
      } else {
        sessionService.clearAssumptionsData()
      }
      if (projectData.threatsData) {
        const items = Array.isArray(projectData.threatsData.items)
          ? projectData.threatsData.items
          : []
        const nextId =
          typeof projectData.threatsData.nextId === 'number'
            ? projectData.threatsData.nextId
            : items.length + 1
        sessionService.saveThreatsData(items, nextId)
      } else {
        sessionService.clearThreatsData()
      }
      if (projectData.ospData) {
        const items = Array.isArray(projectData.ospData.items)
          ? projectData.ospData.items
          : []
        const nextId =
          typeof projectData.ospData.nextId === 'number'
            ? projectData.ospData.nextId
            : items.length + 1
        sessionService.saveOspData(items, nextId)
      } else {
        sessionService.clearOspData()
      }

      showStatus('Project loaded successfully!', 'success')
      
      // Reload the page to reflect changes
      setTimeout(() => {
        window.location.reload()
      }, 1500)
    } catch (error) {
      console.error('Error loading project:', error)
      showStatus('Error loading project. Please check the file format.', 'error')
    }
  }

  reader.readAsText(file)
  // Reset input so the same file can be loaded again if needed
  input.value = ''
}

function confirmClearData() {
  if (confirm('Are you sure you want to clear all project data? This action cannot be undone.')) {
    clearAllData()
  }
}

function clearAllData() {
  try {
    sessionService.clearCoverData()
    sessionService.clearSfrData()
    sessionService.clearSarData()
    sessionService.clearConformanceClaimsData()
    
    // Clear all other session data by iterating localStorage
    const keysToRemove: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith('ccgentool2_')) {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key))

    showStatus('All data cleared successfully!', 'success')
    
    // Reload the page to reflect changes
    setTimeout(() => {
      window.location.reload()
    }, 1500)
  } catch (error) {
    console.error('Error clearing data:', error)
    showStatus('Error clearing data. Please try again.', 'error')
  }
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

.home-button.outline {
  background: transparent;
}

.home-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
}

.data-management {
  width: 100%;
  max-width: 720px;
  padding: 24px;
  border: 1px solid #374151;
  border-radius: 12px;
  background: rgba(55, 65, 81, 0.18);
  margin-top: 16px;
}

.data-management h2 {
  margin: 0 0 16px 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.data-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  font-weight: 500;
}

.btn:hover {
  background: #374151;
  transform: translateY(-1px);
}

.btn.primary {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
}

.btn.primary:hover {
  background: #2563eb;
}

.btn.danger {
  background: #dc2626;
  border-color: #991b1b;
  color: #fff;
}

.btn.danger:hover {
  background: #b91c1c;
}

.status-message {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.status-message.success {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.45);
}

.status-message.error {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
}
</style>
