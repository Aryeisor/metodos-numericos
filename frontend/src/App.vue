<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import NavMenu from './components/NavMenu.vue'
import {
  getMethod,
  hasTheory,
  methodRegistry,
  methodsByCategory,
  solveRouteName,
  theoryRouteName,
} from './methods/registry'

const route = useRoute()

const REGISTRY_ERROR = 'No fue posible cargar los métodos.'
const DEFAULT_FOOTER = 'Métodos numéricos iterativos'

// Ambos menús salen del registro, agrupados por categoría. Una categoría
// nueva aparece sola; en "Teoría" sólo entran los métodos con teoría escrita,
// así que una categoría sin ninguno no se muestra.
const solveGroups = computed(() => methodsByCategory())
const theoryGroups = computed(() => methodsByCategory(hasTheory))

const solveSlug = computed(() => route.meta.method ?? null)
const theorySlug = computed(() => route.meta.theoryMethod ?? null)

const emptyMessage = computed(() => (methodRegistry.status === 'error' ? REGISTRY_ERROR : ''))

const solveLink = (slug) => ({ name: solveRouteName(slug) })
const theoryLink = (slug) => ({ name: theoryRouteName(slug) })

// Pie de página: categoría y nombre del método que se está resolviendo.
const footerText = computed(() => {
  const method = getMethod(solveSlug.value)
  return method ? `${method.categoryLabel} · ${method.name}` : DEFAULT_FOOTER
})
</script>

<template>
  <header class="app-header">
    <div class="container header-inner">
      <span class="brand">Métodos Iterativos</span>
      <nav class="nav" aria-label="Principal">
        <NavMenu
          label="Resolver"
          menu-id="solve-menu"
          :groups="solveGroups"
          :link-to="solveLink"
          :active-slug="solveSlug"
          :active="Boolean(solveSlug) || route.name === 'home'"
          :empty-message="emptyMessage"
        />
        <NavMenu
          label="Teoría"
          menu-id="theory-menu"
          :groups="theoryGroups"
          :link-to="theoryLink"
          :active-slug="theorySlug"
          :active="Boolean(theorySlug) || route.name === 'theory'"
          :empty-message="emptyMessage"
        />
      </nav>
    </div>
  </header>

  <main class="container">
    <RouterView />
  </main>

  <footer class="app-footer">
    <div class="container">{{ footerText }}</div>
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
