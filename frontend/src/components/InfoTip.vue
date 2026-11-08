<script setup>
// Tooltip para encabezados de tabla y términos: se abre al pasar el mouse, con
// el foco del teclado o al tocar (celular). La burbuja se dibuja en <body> con
// posición fija para que el scroll horizontal de la tabla no la recorte.
import { nextTick, onBeforeUnmount, ref } from 'vue'

defineProps({
  text: { type: String, required: true },
})

const id = `tip-${Math.random().toString(36).slice(2, 9)}`
const open = ref(false)
const pinned = ref(false)
const anchor = ref(null)
const bubble = ref(null)
const position = ref({ top: '0px', left: '0px' })

const GAP = 6
const GUTTER = 8

async function place() {
  await nextTick()
  if (!anchor.value || !bubble.value) return
  const rect = anchor.value.getBoundingClientRect()
  const width = bubble.value.offsetWidth
  const height = bubble.value.offsetHeight
  const left = Math.min(Math.max(GUTTER, rect.left + rect.width / 2 - width / 2), window.innerWidth - width - GUTTER)
  const below = rect.bottom + GAP
  const top = below + height > window.innerHeight - GUTTER ? rect.top - height - GAP : below
  position.value = { top: `${Math.max(GUTTER, top)}px`, left: `${left}px` }
}

function show() {
  open.value = true
  place()
  document.addEventListener('pointerdown', outside, true)
  window.addEventListener('scroll', hide, true)
  window.addEventListener('resize', hide)
}

function hide() {
  open.value = false
  pinned.value = false
  document.removeEventListener('pointerdown', outside, true)
  window.removeEventListener('scroll', hide, true)
  window.removeEventListener('resize', hide)
}

function outside(event) {
  if (!anchor.value?.contains(event.target)) hide()
}

// Toque o clic: fija la burbuja abierta (o la cierra si ya estaba fija).
function toggle() {
  if (pinned.value) return hide()
  pinned.value = true
  show()
}

function leave() {
  if (!pinned.value) hide()
}

onBeforeUnmount(hide)
</script>

<template>
  <button
    ref="anchor"
    type="button"
    class="info-tip"
    :aria-describedby="open ? id : undefined"
    :aria-expanded="open"
    @click="toggle"
    @mouseenter="show"
    @mouseleave="leave"
    @focus="show"
    @blur="leave"
    @keydown.esc="hide"
  >
    <slot />
  </button>
  <Teleport to="body">
    <span v-if="open" :id="id" ref="bubble" role="tooltip" class="info-tip-bubble" :style="position">{{ text }}</span>
  </Teleport>
</template>

<style scoped>
.info-tip {
  padding: 0;
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: help;
  text-decoration: underline dotted;
  text-underline-offset: 3px;
}

.info-tip:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
  border-radius: 2px;
}

.info-tip-bubble {
  position: fixed;
  z-index: 1000;
  max-width: min(280px, calc(100vw - 16px));
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  color: var(--color-ink);
  box-shadow: var(--shadow-interactive-hover);
  font-size: var(--text-small);
  font-weight: normal;
  line-height: 1.4;
  text-align: left;
  white-space: normal;
}
</style>
