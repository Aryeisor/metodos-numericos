<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { getMethod, methodRegistry, methodsByCategory, solveRouteName } from './methods/registry'

const route = useRoute()

// Menú "Resolver": métodos agrupados por categoría, tal como los entrega el
// registro. Una categoría nueva aparece aquí sola al registrarse.
const groups = computed(() => methodsByCategory())
const activeSlug = computed(() => route.meta.method ?? null)
const isSolverRoute = computed(() => Boolean(activeSlug.value) || route.name === 'home')

// "Teoría" lleva a la sección del método activo, si lo hay.
const theoryLink = computed(() => {
  const method = getMethod(activeSlug.value)
  return method ? { path: '/teoria', hash: `#${method.ui.theoryAnchor(method.slug)}` } : '/teoria'
})

const menuOpen = ref(false)
const menuRef = ref(null)
const triggerRef = ref(null)

function closeMenu({ restoreFocus = false } = {}) {
  menuOpen.value = false
  if (restoreFocus) triggerRef.value?.focus()
}

function onDocumentPointerDown(event) {
  if (menuOpen.value && !menuRef.value?.contains(event.target)) closeMenu()
}

function onDocumentKeydown(event) {
  if (menuOpen.value && event.key === 'Escape') closeMenu({ restoreFocus: true })
}

watch(() => route.fullPath, () => closeMenu())
onMounted(() => {
  document.addEventListener('pointerdown', onDocumentPointerDown)
  document.addEventListener('keydown', onDocumentKeydown)
})
onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onDocumentPointerDown)
  document.removeEventListener('keydown', onDocumentKeydown)
})
</script>

<template>
  <header class="app-header">
    <div class="container header-inner">
      <span class="brand">Métodos Iterativos</span>
      <nav class="nav" aria-label="Principal">
        <div ref="menuRef" class="nav-menu">
          <button
            ref="triggerRef"
            type="button"
            class="nav-link nav-trigger"
            :class="{ 'is-active': isSolverRoute }"
            :aria-expanded="menuOpen"
            aria-controls="methods-menu"
            @click="menuOpen = !menuOpen"
          >
            Resolver <span class="nav-caret" aria-hidden="true">▾</span>
          </button>

          <div v-if="menuOpen" id="methods-menu" class="methods-menu">
            <p v-if="methodRegistry.status === 'error'" class="methods-empty">
              No fue posible cargar los métodos.
            </p>
            <div v-for="group in groups" :key="group.category" class="methods-group">
              <p :id="`group-${group.category}`" class="methods-group-label">{{ group.label }}</p>
              <ul :aria-labelledby="`group-${group.category}`">
                <li v-for="method in group.methods" :key="method.slug">
                  <RouterLink
                    :to="{ name: solveRouteName(method.slug) }"
                    class="methods-link"
                    :class="{ 'is-active': method.slug === activeSlug }"
                    :aria-current="method.slug === activeSlug ? 'page' : undefined"
                  >
                    {{ method.name }}
                  </RouterLink>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <RouterLink :to="theoryLink" class="nav-link">Teoría</RouterLink>
      </nav>
    </div>
  </header>

  <main class="container">
    <RouterView />
  </main>

  <footer class="app-footer">
    <div class="container">
      Sistemas de ecuaciones lineales · Jacobi &amp; Gauss-Seidel
      Sitemas de ecuaciones no lineales . Itereacion secuenciales, Newton &amp; Bairstow
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

.nav-link.router-link-exact-active,
.nav-link.is-active {
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

/* --- Menú de métodos ---------------------------------------------------- */
.nav-menu {
  position: relative;
  display: flex;
}

/* El disparador es un <button> con el mismo aspecto que los enlaces. */
.nav-trigger {
  gap: var(--space-1);
  padding: 0;
  background: none;
  border-top: none;
  border-left: none;
  border-right: none;
  cursor: pointer;
}

.nav-caret {
  font-size: 0.75em;
}

.methods-menu {
  position: absolute;
  top: calc(100% + var(--space-1));
  right: 0;
  z-index: 20;
  min-width: 220px;
  padding: var(--space-2);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  box-shadow: var(--shadow-interactive-hover);
}

.methods-group + .methods-group {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-line);
}

.methods-group-label {
  margin: 0;
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
}

.methods-group ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.methods-link {
  display: block;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-control);
  color: var(--color-ink);
  text-decoration: none;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.methods-link:hover {
  background: var(--color-sunken);
}

.methods-link.is-active {
  color: var(--color-accent);
  font-weight: var(--weight-semibold);
  background: var(--color-accent-soft);
}

.methods-empty {
  margin: 0;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-small);
  color: var(--color-danger);
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
