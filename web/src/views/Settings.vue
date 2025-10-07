<template>
  <div class="settings-page">
    <div class="card settings-overview">
      <div class="settings-header">
        <div>
          <h1>Settings</h1>
          <p>Manage database records and import Common Criteria XML assets.</p>
        </div>
      </div>
      <div class="settings-tabs" role="tablist">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-button', { active: tab.key === activeTab }]"
          type="button"
          role="tab"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="tab-panel">
      <component :is="activeComponent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import QueryDataPanel from '../components/settings/QueryDataPanel.vue'
import ModifyDataPanel from '../components/settings/ModifyDataPanel.vue'
import XmlParserPanel from '../components/settings/XmlParserPanel.vue'

type TabKey = 'query' | 'modify' | 'xml'

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'query', label: 'Database Query' },
  { key: 'modify', label: 'Database Modify' },
  { key: 'xml', label: 'XML Parser' },
]

const activeTab = ref<TabKey>('query')

const tabComponents: Record<TabKey, any> = {
  query: QueryDataPanel,
  modify: ModifyDataPanel,
  xml: XmlParserPanel,
}

const activeComponent = computed(() => tabComponents[activeTab.value])
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-overview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-header h1 {
  margin: 0 0 6px 0;
  font-size: 1.5rem;
}

.settings-header p {
  margin: 0;
  color: var(--muted);
}

.settings-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tab-button {
  padding: 10px 18px;
  border-radius: 999px;
  border: 1px solid #374151;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, transform 0.2s;
  font-weight: 500;
}

.tab-button.active {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
  transform: translateY(-1px);
}

.tab-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
