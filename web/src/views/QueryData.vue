<template>
  <div class="card">
    <div class="actions" style="margin-bottom: 12px;">
      <input class="input" v-model="q" placeholder="Search..." @input="debouncedFetch" />
      <button class="btn" @click="fetchItems">Refresh</button>
    </div>
    <table class="table">
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

type Item = { id: number, class: string, family?: string, component?: string, component_name?: string, element?: string, element_item?: string }

const items = ref<Item[]>([])
const q = ref('')
let timer: any

function debouncedFetch(){
  clearTimeout(timer)
  timer = setTimeout(fetchItems, 300)
}

async function fetchItems(){
  const res = await api.get('/components', { params: { q: q.value || undefined } })
  items.value = res.data
}

onMounted(fetchItems)
</script>

<style scoped>
</style>
