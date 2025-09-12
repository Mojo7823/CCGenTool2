<template>
  <div class="card">
    <div class="actions" style="margin-bottom: 12px;">
      <select class="input" v-model="selectedTable" @change="fetchItems">
        <option v-for="tbl in tables" :key="tbl.name" :value="tbl.name">
          {{ tbl.name }}
        </option>
      </select>
      <input class="input" v-model="q" placeholder="Search..." @input="debouncedFetch" />
      <button class="btn" @click="fetchItems">Refresh</button>
    </div>
    <table class="table" v-if="items.length">
      <thead>
        <tr>
          <th>ID</th>
          <th>Class</th>
          <th>Family</th>
          <th>Component</th>
          <th>Component Name</th>
          <th>Element</th>
          <th>Element Item</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.class }}</td>
          <td>{{ item.family }}</td>
          <td>{{ item.component }}</td>
          <td>{{ item.component_name }}</td>
          <td>{{ item.element }}</td>
          <td>{{ item.element_item }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../services/api'

type Item = {
  id: number,
  class?: string,
  family?: string,
  component?: string,
  component_name?: string,
  element?: string,
  element_item?: string
}

type TableInfo = { name: string; description: string }

const tables = ref<TableInfo[]>([])
const selectedTable = ref('')
const items = ref<Item[]>([])
const q = ref('')
let timer: any

async function loadTables() {
  const res = await api.get('/families')
  tables.value = Object.values(res.data).flat()
  if (tables.value.length && !selectedTable.value) {
    selectedTable.value = tables.value[0].name
    await fetchItems()
  }
}

function debouncedFetch() {
  clearTimeout(timer)
  timer = setTimeout(fetchItems, 300)
}

async function fetchItems() {
  if (!selectedTable.value) return
  const res = await api.get(`/families/${selectedTable.value}`, {
    params: { q: q.value || undefined }
  })
  items.value = res.data
}

onMounted(loadTables)
</script>

<style scoped>
</style>
