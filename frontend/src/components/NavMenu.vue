<script setup>
// Menú desplegable de la barra superior: métodos agrupados por categoría.
// Lo usan "Resolver ▾" y "Teoría ▾"; cada uno decide qué grupos mostrar y a
// qué ruta lleva cada método.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const props = defineProps({
  label: { type: String, required: true },
  menuId: { type: String, required: true },
  // [{ category, label, methods: [{ slug, name }] }]
  groups: { type: Array, required: true },
  // slug -> ubicación para RouterLink
  linkTo: { type: Function, required: true },
  activeSlug: { type: String, default: null },
  // Resalta el disparador (la sección actual pertenece a este menú).
  active: { type: Boolean, default: false },
  // Mensaje cuando no hay grupos que mostrar (ej. el catálogo no cargó).
  emptyMessage: { type: String, default: '' },
})

const route = useRoute()
const open = ref(false)
const menuRef = ref(null)
const triggerRef = ref(null)

function close({ restoreFocus = false } = {}) {
  open.value = false
  if (restoreFocus) triggerRef.value?.focus()
}

function onDocumentPointerDown(event) {
  if (open.value && !menuRef.value?.contains(event.target)) close()
}

function onDocumentKeydown(event) {
  if (open.value && event.key === 'Escape') close({ restoreFocus: true })
}

watch(() => route.fullPath, () => close())
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
  <div ref="menuRef" class="nav-menu">
    <button
      ref="triggerRef"
      type="button"
      class="nav-link nav-trigger"
      :class="{ 'is-active': active }"
      :aria-expanded="open"
      :aria-controls="menuId"
      @click="open = !open"
    >
      {{ label }} <span class="nav-caret" aria-hidden="true">▾</span>
    </button>

    <div v-if="open" :id="menuId" class="methods-menu">
      <p v-if="!groups.length && emptyMessage" class="methods-empty">{{ emptyMessage }}</p>
      <div v-for="group in groups" :key="group.category" class="methods-group">
        <p :id="`${menuId}-${group.category}`" class="methods-group-label">{{ group.label }}</p>
        <ul :aria-labelledby="`${menuId}-${group.category}`">
          <li v-for="method in group.methods" :key="method.slug">
            <RouterLink
              :to="linkTo(method.slug)"
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
</template>

<style scoped>
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
</style>
