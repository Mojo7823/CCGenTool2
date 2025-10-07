<template>
  <div class="card">
    <h3 style="margin-top:0">Create / Modify Components</h3>
    
    <!-- Table Selection -->
    <div class="table-selection" style="margin-bottom: 20px;">
      <h4>Table Location</h4>
      <select class="input" v-model="selectedTable" @change="onTableChange" style="width: 300px;">
        <option value="">Select a table...</option>
        <optgroup label="Functional Requirements">
          <option v-for="table in familyTables.functional" :key="table.name" :value="table.name">
            {{ table.name }} - {{ table.description }}
          </option>
        </optgroup>
        <optgroup label="Assurance Requirements">
          <option v-for="table in familyTables.assurance" :key="table.name" :value="table.name">
            {{ table.name }} - {{ table.description }}
          </option>
        </optgroup>
        <optgroup label="Special Tables">
          <option v-for="table in familyTables.special" :key="table.name" :value="table.name">
            {{ table.name }} - {{ table.description }}
          </option>
        </optgroup>
        <optgroup label="General">
          <option value="components">components - General components table</option>
        </optgroup>
      </select>
    </div>

    <div v-if="selectedTable">
      <form class="actions" @submit.prevent="create">
        <input class="input" v-model="form.class" placeholder="Class*" required />
        <input class="input" v-model="form.family" placeholder="Family" />
        <input class="input" v-model="form.component" placeholder="Component" />
        <input class="input" v-model="form.component_name" placeholder="Component Name" />
        <input class="input" v-model="form.element" placeholder="Element" />
        <input class="input" v-model="form.element_item" placeholder="Element Item" />
        <button class="btn primary" type="submit">Add</button>
      </form>
      <table class="table" style="margin-top:12px">
        <thead>
          <tr>
            <th>ID</th>
            <th>Class</th>
            <th>Family</th>
            <th>Component</th>
            <th>Component Name</th>
            <th>Element</th>
            <th>Element Item</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, i) in items" :key="item.id">
            <td>{{ item.id }}</td>
            <td><input class="input" v-model="item.class_display" /></td>
            <td><input class="input" v-model="item.family" /></td>
            <td><input class="input" v-model="item.component" /></td>
            <td><input class="input" v-model="item.component_name" /></td>
            <td><input class="input" v-model="item.element" /></td>
            <td><input class="input" v-model="item.element_item" /></td>
            <td class="actions">
              <button class="btn" @click="save(item)">Save</button>
              <button class="btn danger" @click="remove(item)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-else class="no-selection">
      <p>Please select a table from the dropdown above to view and modify its data.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../../services/api'

type Item = { 
  id: number, 
  class?: string, 
  class_field?: string,
  class_display?: string,
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

const form = reactive({ class: '', family: '', component: '', component_name: '', element: '', element_item: '' })
const items = ref<Item[]>([])
const selectedTable = ref<string>('')
const familyTables = ref<FamilyTables>({})

async function fetchFamilyTables() {
  try {
    const res = await api.get('/families')
    familyTables.value = res.data
  } catch (error) {
    console.error('Error fetching family tables:', error)
  }
}

async function onTableChange() {
  if (selectedTable.value) {
    await load()
  } else {
    items.value = []
  }
}

async function load(){
  if (!selectedTable.value) return
  
  try {
    let res
    if (selectedTable.value === 'components') {
      res = await api.get('/components')
    } else {
      res = await api.get(`/families/${selectedTable.value}`)
    }
    // Process items to add class_display field
    items.value = res.data.map((item: Item) => ({
      ...item,
      class_display: item.class || item.class_field || ''
    }))
  } catch (error) {
    console.error('Error loading data:', error)
    items.value = []
  }
}

async function create(){
  if(!form.class || !selectedTable.value) return
  
  try {
    const payload = {
      class_name: form.class,
      family: form.family,
      component: form.component,
      component_name: form.component_name,
      element: form.element,
      element_item: form.element_item
    }
    
    if (selectedTable.value === 'components') {
      await api.post('/components', payload)
    } else {
      await api.post(`/families/${selectedTable.value}`, payload)
    }
    
    Object.assign(form, { class: '', family: '', component: '', component_name: '', element: '', element_item: '' })
    await load()
  } catch (error) {
    console.error('Error creating item:', error)
  }
}

async function save(row: Item){
  if (!selectedTable.value) return
  
  try {
    const payload = {
      class_name: row.class_display || row.class || row.class_field,
      family: row.family,
      component: row.component,
      component_name: row.component_name,
      element: row.element,
      element_item: row.element_item
    }
    
    if (selectedTable.value === 'components') {
      await api.put(`/components/${row.id}`, payload)
    } else {
      await api.put(`/families/${selectedTable.value}/${row.id}`, payload)
    }
    
    await load()
  } catch (error) {
    console.error('Error saving item:', error)
  }
}

async function remove(row: Item){
  if (!selectedTable.value) return
  
  try {
    if (selectedTable.value === 'components') {
      await api.delete(`/components/${row.id}`)
    } else {
      await api.delete(`/families/${selectedTable.value}/${row.id}`)
    }
    
    await load()
  } catch (error) {
    console.error('Error deleting item:', error)
  }
}

onMounted(async () => {
  await fetchFamilyTables()
})
</script>

<style scoped>
.table-selection {
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 16px;
  background: var(--panel);
}

.table-selection h4 {
  margin: 0 0 12px 0;
  color: var(--text);
  font-size: 1.1em;
}

.no-selection {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>
