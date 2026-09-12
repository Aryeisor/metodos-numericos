<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header class="app-header">
    <div class="container header-inner">
      <span class="brand">Métodos Iterativos</span>
      <nav class="nav">
        <RouterLink to="/" class="nav-link">Resolver</RouterLink>
        <RouterLink to="/teoria" class="nav-link">Teoría</RouterLink>
      </nav>
    </div>
  </header>

  <main class="container">
    <RouterView />
  </main>

  <footer class="app-footer">
    <div class="container">
      Sistemas de ecuaciones lineales · Jacobi &amp; Gauss-Seidel
    </div>
  </footer>
</template>

<style scoped>
.app-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  padding-bottom: 14px;
}

.brand {
  font-weight: 700;
  font-size: 1.1rem;
}

.nav {
  display: flex;
  gap: 18px;
}

.nav-link {
  text-decoration: none;
  color: var(--color-text-muted);
  font-weight: 600;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
}

.nav-link.router-link-exact-active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.app-footer {
  margin-top: auto;
  padding: 16px 0;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  text-align: center;
  border-top: 1px solid var(--color-border);
}
</style>
