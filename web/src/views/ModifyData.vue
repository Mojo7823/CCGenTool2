<template>
  <div class="card">
    <h3 style="margin-top:0">Create / Modify Components</h3>
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
          <td><input class="input" v-model="item.class" /></td>
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
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../services/api'

type Item = { id: number, class: string, family?: string, component?: string, component_name?: string, element?: string, element_item?: string }

const form = reactive({ class: '', family: '', component: '', component_name: '', element: '', element_item: '' })
const items = ref<Item[]>([])

async function load(){
  const res = await api.get('/components')
  items.value = res.data
}

async function create(){
  if(!form.class) return
  await api.post('/components', { ...form })
  Object.assign(form, { class: '', family: '', component: '', component_name: '', element: '', element_item: '' })
  await load()
}

async function save(row: Item){
  await api.put(`/components/${row.id}`, { ...row })
  await load()
}

async function remove(row: Item){
  await api.delete(`/components/${row.id}`)
  await load()
}

onMounted(load)
</script>

<style scoped>
</style>
