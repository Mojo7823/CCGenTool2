<template>
  <div class="card">
    <h2>Query Database Tables</h2>
    
    <!-- Table Selection -->
    <div class="table-selection" style="margin-bottom: 20px;">
      <h3>Available Tables</h3>
      <div class="table-categories">
        <!-- Functional Requirements Tables -->
        <div class="category" v-if="familyTables.functional?.length">
          <h4>Functional Requirements</h4>
          <div class="table-grid">
            <button 
              v-for="table in familyTables.functional" 
              :key="table.name"
              class="table-btn"
              :class="{ active: selectedTable === table.name }"
              @click="selectTable(table.name)"
            >
              <div class="table-name">{{ table.name }}</div>
              <div class="table-description">{{ table.description }}</div>
              <div class="table-count" v-if="tableCounts[table.name] !== undefined">
                {{ tableCounts[table.name] }} items
              </div>
            </button>
          </div>
        </div>

        <!-- Assurance Requirements Tables -->
        <div class="category" v-if="familyTables.assurance?.length">
          <h4>Assurance Requirements</h4>
          <div class="table-grid">
            <button 
              v-for="table in familyTables.assurance" 
              :key="table.name"
              class="table-btn"
              :class="{ active: selectedTable === table.name }"
              @click="selectTable(table.name)"
            >
              <div class="table-name">{{ table.name }}</div>
              <div class="table-description">{{ table.description }}</div>
              <div class="table-count" v-if="tableCounts[table.name] !== undefined">
                {{ tableCounts[table.name] }} items
              </div>
            </button>
          </div>
        </div>

        <!-- Special Tables -->
        <div class="category" v-if="familyTables.special?.length">
          <h4>Special Tables</h4>
          <div class="table-grid">
            <button 
              v-for="table in familyTables.special" 
              :key="table.name"
              class="table-btn"
              :class="{ active: selectedTable === table.name }"
              @click="selectTable(table.name)"
            >
              <div class="table-name">{{ table.name }}</div>
              <div class="table-description">{{ table.description }}</div>
              <div class="table-count" v-if="tableCounts[table.name] !== undefined">
                {{ tableCounts[table.name] }} items
              </div>
            </button>
          </div>
        </div>

        <!-- General Components Table -->
        <div class="category">
          <h4>General</h4>
          <div class="table-grid">
            <button 
              class="table-btn"
              :class="{ active: selectedTable === 'components' }"
              @click="selectTable('components')"
            >
              <div class="table-name">components</div>
              <div class="table-description">General components table</div>
              <div class="table-count" v-if="tableCounts.components !== undefined">
                {{ tableCounts.components }} items
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Display -->
    <div v-if="selectedTable" class="data-section">
      <div class="actions" style="margin-bottom: 12px;">
        <h3>{{ selectedTable }} Table Data</h3>
        <div style="display: flex; gap: 10px; align-items: center;">
          <input class="input" v-model="q" placeholder="Search..." @input="debouncedFetch" />
          <button class="btn" @click="fetchItems">Refresh</button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">Loading...</div>
      
      <div v-else class="data-table-wrapper">
        <EasyDataTable
          :headers="tableHeaders"
          :items="items"
          :rows-per-page="25"
          :show-index="true"
          search-field=""
          search-value=""
          alternating
          buttons-pagination
          :must-sort="false"
          table-class-name="customize-table"
          :loading="loading"
        >
          <template #item-element_item="{ item }">
            <div class="element-item-cell">{{ item.element_item }}</div>
          </template>
          <template #item-component_name="{ item }">
            <div class="component-name-cell">{{ item.component_name }}</div>
          </template>
          <template #empty-message>
            <p>No data found in {{ selectedTable }} table.
               {{ selectedTable !== 'components' ? 'Try importing XML data first.' : '' }}
            </p>
          </template>
        </EasyDataTable>
      </div>
    </div>

    <div v-else class="no-selection">
      <p>Select a table above to view its data.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../services/api'
import type { Header } from 'vue3-easy-data-table'
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

type Item = { 
  id: number, 
  class?: string, 
  class_field?: string,  // For family tables
  family?: string, 
  component?: string, 
  component_name?: string, 
  element?: string, 
  element_item?: string 
}

type Table = {
  name: string
  description: string
}

type FamilyTables = {
  functional?: Table[]
  assurance?: Table[]
  special?: Table[]
}

// DataTable headers
const tableHeaders: Header[] = [
  { text: 'ID', value: 'id', sortable: true, width: 80 },
  { text: 'Class', value: 'class_display', sortable: true, width: 120 },
  { text: 'Family', value: 'family', sortable: true, width: 120 },
  { text: 'Component', value: 'component', sortable: true, width: 120 },
  { text: 'Component Name', value: 'component_name', sortable: true, width: 300 },
  { text: 'Element', value: 'element', sortable: true, width: 150 },
  { text: 'Element Item', value: 'element_item', sortable: false, width: 400 }
]

const items = ref<Item[]>([])
const q = ref('')
const selectedTable = ref<string>('')
const familyTables = ref<FamilyTables>({})
const tableCounts = ref<Record<string, number>>({})
const loading = ref(false)
let timer: any

function debouncedFetch(){
  clearTimeout(timer)
  timer = setTimeout(fetchItems, 300)
}

async function fetchFamilyTables() {
  try {
    const res = await api.get('/families')
    familyTables.value = res.data
    
    // Fetch counts for all tables
    await fetchTableCounts()
  } catch (error) {
    console.error('Error fetching family tables:', error)
  }
}

async function fetchTableCounts() {
  try {
    // Fetch counts for family tables
    const allTables = [
      ...(familyTables.value.functional || []),
      ...(familyTables.value.assurance || []),
      ...(familyTables.value.special || [])
    ]

    for (const table of allTables) {
      try {
        const res = await api.get(`/families/${table.name}/count`)
        tableCounts.value[table.name] = res.data.count
      } catch (error) {
        console.error(`Error fetching count for ${table.name}:`, error)
        tableCounts.value[table.name] = 0
      }
    }

    // Fetch count for general components table
    try {
      const res = await api.get('/components')
      tableCounts.value.components = res.data.length
    } catch (error) {
      console.error('Error fetching components count:', error)
      tableCounts.value.components = 0
    }
  } catch (error) {
    console.error('Error fetching table counts:', error)
  }
}

async function selectTable(tableName: string) {
  selectedTable.value = tableName
  q.value = '' // Clear search when switching tables
  await fetchItems()
}

async function fetchItems(){
  if (!selectedTable.value) return
  
  loading.value = true
  try {
    let res
    if (selectedTable.value === 'components') {
      res = await api.get('/components', { params: { q: q.value || undefined } })
    } else {
      res = await api.get(`/families/${selectedTable.value}`, { params: { q: q.value || undefined } })
    }
    // Process items to add class_display field
    items.value = res.data.map((item: Item) => ({
      ...item,
      class_display: item.class || item.class_field || ''
    }))
  } catch (error) {
    console.error('Error fetching items:', error)
    items.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchFamilyTables()
})
</script>

<style scoped>
.table-selection {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 16px;
  background: #1a1a1a;
}

.table-categories {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.category h4 {
  margin: 0 0 12px 0;
  color: #fff;
  font-size: 1.1em;
}

.table-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.table-btn {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  color: #ccc;
}

.table-btn:hover {
  background: #333;
  border-color: #555;
}

.table-btn.active {
  background: #0066cc;
  border-color: #0088ff;
  color: white;
}

.table-name {
  font-weight: bold;
  font-size: 1em;
  margin-bottom: 4px;
  color: #fff;
}

.table-description {
  font-size: 0.85em;
  color: #aaa;
  margin-bottom: 6px;
}

.table-count {
  font-size: 0.8em;
  color: #888;
  font-style: italic;
}

.table-btn.active .table-name,
.table-btn.active .table-description,
.table-btn.active .table-count {
  color: white;
}

.data-section h3 {
  margin: 0 0 12px 0;
  color: #fff;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #aaa;
}

.no-selection {
  text-align: center;
  padding: 40px;
  color: #666;
}

.data-table-wrapper {
  border: 1px solid #374151;
  border-radius: 8px;
  background: var(--panel);
  overflow: hidden;
  margin-top: 12px;
}

/* DataTable styling */
.customize-table {
  --easy-table-body-row-background-color: var(--panel);
  --easy-table-body-row-hover-background-color: rgba(55, 65, 81, 0.5);
  --easy-table-body-item-padding: 12px;
  --easy-table-header-background-color: var(--bg-soft);
  --easy-table-header-font-color: var(--text);
  --easy-table-header-item-padding: 12px;
  --easy-table-body-font-color: var(--text);
  --easy-table-border: 1px solid #374151;
  --easy-table-scrollbar-track-color: var(--bg-soft);
  --easy-table-scrollbar-color: #6b7280;
}

.element-item-cell {
  max-width: 400px;
  word-wrap: break-word;
  font-size: 0.9rem;
  line-height: 1.4;
}

.component-name-cell {
  max-width: 300px;
  word-wrap: break-word;
  font-size: 0.9rem;
  line-height: 1.4;
}
</style>
