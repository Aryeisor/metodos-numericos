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
  border-bottom: 1px solid var(--color-line);
}

/* La cabecera ocupa su propia banda: sin el padding vertical del contenedor. */
.header-inner {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: var(--space-4);
  padding-top: 0;
  padding-bottom: 0;
  min-height: 60px;
}

.brand {
  display: flex;
  align-items: center;
  font-size: var(--text-app-title);
  font-weight: var(--weight-bold);
  letter-spacing: -0.015em;
  color: var(--color-ink);
}

.nav {
  display: flex;
  gap: var(--space-5);
}

.nav-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--color-ink-muted);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color var(--transition-fast), border-color var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-ink);
}

.nav-link.router-link-exact-active {
  color: var(--color-accent);
  font-weight: var(--weight-semibold);
  border-bottom-color: var(--color-accent);
}

.nav-link:focus-visible {
  box-shadow: none;
  outline: 2px solid var(--color-accent);
  outline-offset: 4px;
  border-radius: 2px;
}

.app-footer {
  margin-top: auto;
  padding: var(--space-5) 0;
  color: var(--color-ink-muted);
  font-size: var(--text-small);
  text-align: center;
  border-top: 1px solid var(--color-line);
}

.app-footer .container {
  padding-top: 0;
  padding-bottom: 0;
}
</style>
