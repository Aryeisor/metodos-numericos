<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import NavMenu from './components/NavMenu.vue'
import { useTheme } from './composables/useTheme'
import { getMethod } from './methods/registry'

const route = useRoute()
const { theme, toggleTheme } = useTheme()

// El botón dice lo que hace al pulsarlo: luna en claro, sol en oscuro.
const themeToggleLabel = computed(() =>
  theme.value === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'
)

const DEFAULT_FOOTER = 'Métodos numéricos iterativos'

// Pie de página: categoría y nombre del método que se está resolviendo.
const footerText = computed(() => {
  const method = getMethod(route.meta.method ?? null)
  return method ? `${method.categoryLabel} · ${method.name}` : DEFAULT_FOOTER
})
</script>

<template>
  <header class="app-header">
    <a class="skip-link" href="#contenido">Saltar al contenido</a>
    <div class="container header-inner">
      <span class="brand">Métodos Iterativos</span>
      <div class="nav">
        <NavMenu />
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
      </div>
    </div>
  </header>

  <main id="contenido" class="container" tabindex="-1">
    <RouterView />
  </main>

  <footer class="app-footer">
    <div class="container">{{ footerText }}</div>
  </footer>
</template>

<style scoped>
/* Barra fija: el menú de métodos y el atajo «/» deben estar a mano en
   cualquier punto de la página (scroll-padding-top en style.css evita que
   tape el elemento enfocado). */
.app-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-line);
}

.skip-link {
  position: absolute;
  left: var(--space-4);
  top: var(--space-2);
  z-index: 60;
  padding: var(--space-2) var(--space-3);
  background: var(--color-accent);
  color: var(--color-on-accent);
  border-radius: var(--radius-control);
  font-weight: var(--weight-semibold);
  text-decoration: none;
  transform: translateY(-200%);
}

.skip-link:focus {
  transform: none;
  outline: 2px solid var(--color-ink);
  outline-offset: 2px;
}

/* Destino del enlace de salto y del foco tras navegar desde el menú: no
   necesita anillo, el foco sólo marca dónde sigue la lectura. */
main:focus {
  outline: none;
  box-shadow: none;
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
