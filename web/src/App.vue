<template>
  <div class="layout">
    <aside class="sidebar">
      <Sidebar />
    </aside>
    <header class="navbar">
      <div class="brand">CCGenTool2</div>
      <div class="status">
        <span>DB:</span>
        <span :class="['badge', health.status]">{{ health.status }} ({{ health.latency_ms }}ms)</span>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
  
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import api from './services/api'

type Health = { status: 'ok'|'degraded'|string, latency_ms: number }
const health = ref<Health>({ status: 'degraded', latency_ms: 0 })

async function poll() {
  try{
    const res = await api.get('/health')
    health.value = { status: res.data.status, latency_ms: res.data.latency_ms }
  } catch {
    health.value = { status: 'degraded', latency_ms: 0 }
  }
}

onMounted(() => {
  poll()
  setInterval(poll, 5000)
})
</script>

<style scoped>
</style>
