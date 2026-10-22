<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import NavMenu from './components/NavMenu.vue'
import { useTheme } from './composables/useTheme'
import {
  getMethod,
  hasTheory,
  methodRegistry,
  methodsByCategory,
  solveRouteName,
  theoryRouteName,
} from './methods/registry'

const route = useRoute()
const { theme, toggleTheme } = useTheme()

// El botón dice lo que hace al pulsarlo: luna en claro, sol en oscuro.
const themeToggleLabel = computed(() =>
  theme.value === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'
)

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
        <button
          type="button"
          class="theme-toggle"
          :aria-label="themeToggleLabel"
          :title="themeToggleLabel"
          @click="toggleTheme"
        >
          <svg v-if="theme === 'dark'" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        </button>
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

.theme-toggle {
  align-self: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--color-ink-muted);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast),
    border-color var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--color-sunken);
  color: var(--color-ink);
  border-color: var(--color-line-strong);
}

.theme-toggle svg {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* En móvil el botón de tema quita espacio: se juntan los elementos para que
   el nombre de la app no se parta en dos líneas. */
@media (max-width: 480px) {
  .header-inner,
  .nav {
    gap: var(--space-3);
  }

  .theme-toggle {
    width: 32px;
    height: 32px;
  }
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
