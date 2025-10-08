<template>
  <div class="card home-card">
    <h1 class="home-title">Welcome to Common Criteria Security Target Generation (CCGen) Tools</h1>
    <div class="home-actions">
      <RouterLink class="home-button primary" to="/settings">Open an existing Security Target Project</RouterLink>
      <RouterLink class="home-button" to="/st-intro/cover">Create New Security Target</RouterLink>
      <RouterLink class="home-button outline" to="/generator">Automatically Generate Security Target</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 32px;
  gap: 32px;
  min-height: 320px;
}

.home-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  max-width: 720px;
}

.home-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.home-button {
  text-decoration: none;
  padding: 14px 20px;
  border-radius: 10px;
  border: 1px solid #374151;
  background: var(--bg);
  color: var(--text);
  min-width: 240px;
  text-align: center;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}

.home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.25);
}

.home-button.primary {
  background: var(--primary);
  border-color: #2563eb;
  color: #fff;
}

.home-button.outline {
  background: transparent;
}

.home-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
}
</style>
