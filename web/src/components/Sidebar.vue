<template>
  <ul class="menu">
    <li>
      <RouterLink to="/" active-class="active">Home</RouterLink>
    </li>
    <li>
      <div class="accordion">
        <div class="accordion-header" @click="stOpen = !stOpen">
          <span>ST Introduction</span>
          <span>{{ stOpen ? '▾' : '▸' }}</span>
        </div>
        <div v-if="stOpen" class="accordion-content">
          <ul class="menu nested">
            <li><RouterLink to="/cover" active-class="active">Cover</RouterLink></li>
            <li><RouterLink to="/st-introduction/reference" active-class="active">ST Reference</RouterLink></li>
            <li><RouterLink to="/st-introduction/toe-reference" active-class="active">TOE Reference</RouterLink></li>
            <li><RouterLink to="/st-introduction/toe-overview" active-class="active">TOE Overview</RouterLink></li>
            <li><RouterLink to="/st-introduction/toe-description" active-class="active">TOE Description</RouterLink></li>
            <li><RouterLink to="/st-introduction/preview" active-class="active">ST Introduction Preview</RouterLink></li>
          </ul>
        </div>
      </div>
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
          <ul class="menu nested">
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

const stOpen = ref(true)
const securityOpen = ref(true)
</script>

<style scoped>
.menu {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu > li > a,
.menu.nested > li > a {
  display: block;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s ease;
}

.menu > li > a:hover,
.menu.nested > li > a:hover {
  background: rgba(148, 163, 184, 0.15);
}

.active {
  background: rgba(37, 99, 235, 0.35);
  color: #fff;
}

.accordion {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 10px;
  overflow: hidden;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  font-weight: 600;
  background: rgba(15, 23, 42, 0.35);
}

.accordion-content {
  padding: 8px;
}

.menu.nested {
  gap: 4px;
}
</style>
