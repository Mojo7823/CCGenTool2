<template>
  <ul class="menu">
    <li>
      <RouterLink to="/" active-class="active">Home</RouterLink>
    </li>
    <li>
      <RouterLink to="/cover" active-class="active">Cover Builder</RouterLink>
    </li>
    <li>
      <RouterLink to="/generator" active-class="active">Generator</RouterLink>
    </li>
    <li>
      <RouterLink to="/settings" active-class="active">Settings</RouterLink>
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
            <li><RouterLink to="/security/sar" active-class="active">Security Assurance Requirements</RouterLink></li>
          </ul>
        </div>
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const securityOpen = ref(true)
</script>

<style scoped>
</style>
