<template>
  <ul class="menu">
    <li>
      <RouterLink to="/" active-class="active">Home</RouterLink>
    </li>
    <li>
      <div class="accordion">
        <div class="accordion-header" @click="open = !open">
          <span>Database</span>
          <span>{{ open ? '▾' : '▸' }}</span>
        </div>
        <div v-if="open" class="accordion-content">
          <ul class="menu">
            <li><RouterLink to="/database/query" active-class="active">Query Data</RouterLink></li>
            <li><RouterLink to="/database/modify" active-class="active">Modify Data</RouterLink></li>
          </ul>
        </div>
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const open = ref(true)
</script>

<style scoped>
</style>
