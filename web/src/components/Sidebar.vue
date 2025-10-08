<template>
  <ul class="menu">
    <li>
      <RouterLink to="/" active-class="active">Home</RouterLink>
    </li>
    <li>
      <RouterLink to="/generator" active-class="active">Generator</RouterLink>
    </li>
    <li>
      <div class="accordion">
        <div class="accordion-header" @click="stIntroOpen = !stIntroOpen">
          <span>ST Introduction</span>
          <span>{{ stIntroOpen ? '▾' : '▸' }}</span>
        </div>
        <div v-if="stIntroOpen" class="accordion-content">
          <ul class="menu">
            <li><RouterLink to="/st-intro/cover" active-class="active">Cover</RouterLink></li>
            <li><RouterLink to="/st-intro/reference" active-class="active">ST Reference</RouterLink></li>
            <li><RouterLink to="/st-intro/toe-reference" active-class="active">TOE Reference</RouterLink></li>
            <li><RouterLink to="/st-intro/toe-overview" active-class="active">TOE Overview</RouterLink></li>
            <li><RouterLink to="/st-intro/toe-description" active-class="active">TOE Description</RouterLink></li>
            <li><RouterLink to="/st-intro/preview" active-class="active">ST Introduction Preview</RouterLink></li>
          </ul>
        </div>
      </div>
    </li>
    <li>
      <RouterLink to="/conformanceclaims" active-class="active">Conformance Claims</RouterLink>
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
    <li>
      <RouterLink to="/final-document-preview" active-class="active">Final Document Preview</RouterLink>
    </li>
    <li>
      <RouterLink to="/settings" active-class="active">Settings</RouterLink>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const stIntroOpen = ref(true)
const securityOpen = ref(true)
</script>

<style scoped>
</style>
