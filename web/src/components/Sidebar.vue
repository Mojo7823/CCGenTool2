<template>
  <ul class="menu">
    <li>
      <RouterLink to="/" active-class="active">Home</RouterLink>
    </li>
    <li>
      <div class="accordion">
        <div class="accordion-header" @click="databaseOpen = !databaseOpen">
          <span>Database</span>
          <span>{{ databaseOpen ? '▾' : '▸' }}</span>
        </div>
        <div v-if="databaseOpen" class="accordion-content">
          <ul class="menu">
            <li><RouterLink to="/database/query" active-class="active">Query Data</RouterLink></li>
            <li><RouterLink to="/database/modify" active-class="active">Modify Data</RouterLink></li>
          </ul>
        </div>
      </div>
    </li>
    <li>
      <div class="accordion">
        <div class="accordion-header" @click="securityOpen = !securityOpen">
          <span>Security Requirements</span>
          <span>{{ securityOpen ? '▾' : '▸' }}</span>
        </div>
        <div v-if="securityOpen" class="accordion-content">
          <ul class="menu">
            <li><RouterLink to="/security/sfr" active-class="active">Security Functional Requirements</RouterLink></li>
          </ul>
        </div>
      </div>
    </li>
    <li>
      <RouterLink to="/xml-parser" active-class="active">XML Parser</RouterLink>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const databaseOpen = ref(true)
const securityOpen = ref(true)
</script>

<style scoped>
</style>
