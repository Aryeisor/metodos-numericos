<script>
// Símbolos por defecto. `insert` termina en "()" para las funciones: el
// cursor queda entre los paréntesis (o se envuelve el texto seleccionado).
export const DEFAULT_SYMBOLS = [
  { label: '√', insert: 'sqrt()', name: 'Raíz cuadrada' },
  { label: 'xⁿ', insert: '^', name: 'Potencia' },
  { label: 'log', insert: 'log()', name: 'Logaritmo en base 10' },
  { label: 'ln', insert: 'ln()', name: 'Logaritmo natural' },
  { label: 'exp', insert: 'exp()', name: 'Exponencial' },
  { label: 'sin', insert: 'sin()', name: 'Seno' },
  { label: 'cos', insert: 'cos()', name: 'Coseno' },
  { label: 'tan', insert: 'tan()', name: 'Tangente' },
  { label: 'π', insert: 'pi', name: 'Número pi' },
  { label: 'e', insert: 'e', name: 'Número e' },
  { label: '|x|', insert: 'abs()', name: 'Valor absoluto' },
  // Sobre todo para móvil: evita cambiar de teclado sólo por un paréntesis.
  { label: '( )', insert: '()', name: 'Paréntesis' },
]

// Funciones menos frecuentes, en el desplegable "Más funciones ▾".
export const DEFAULT_MORE_GROUPS = [
  {
    label: 'Trigonométricas inversas',
    symbols: [
      { label: 'asin', insert: 'asin()', name: 'Arcoseno' },
      { label: 'acos', insert: 'acos()', name: 'Arcocoseno' },
      { label: 'atan', insert: 'atan()', name: 'Arcotangente' },
    ],
  },
  {
    label: 'Hiperbólicas',
    symbols: [
      { label: 'sinh', insert: 'sinh()', name: 'Seno hiperbólico' },
      { label: 'cosh', insert: 'cosh()', name: 'Coseno hiperbólico' },
      { label: 'tanh', insert: 'tanh()', name: 'Tangente hiperbólica' },
    ],
  },
]

const NAME_CHAR = /[A-Za-z0-9_)]/

/**
 * Inserta `insert` en `input` en la posición del cursor (reemplazando la
 * selección, o envolviéndola si es una función) y avisa con un evento
 * `input`, igual que si el usuario lo hubiera escrito.
 */
export function insertIntoInput(input, insert) {
  const value = input.value
  const start = input.selectionStart ?? value.length
  const end = input.selectionEnd ?? start
  const selected = value.slice(start, end)

  let text
  let caret
  if (insert.endsWith('()')) {
    const open = insert.slice(0, -1)
    text = `${open}${selected})`
    // Sin selección, el cursor queda entre los paréntesis.
    caret = selected ? text.length : open.length
  } else {
    text = insert
    caret = text.length
  }

  // Un nombre pegado a otro ("x" + "sqrt(") formaría uno solo ("xsqrt"):
  // se separa con un "*" explícito.
  if (/^[A-Za-z]/.test(text) && start > 0 && NAME_CHAR.test(value[start - 1])) {
    text = `*${text}`
    caret += 1
  }

  input.focus()
  input.setRangeText(text, start, end, 'end')
  input.setSelectionRange(start + caret, start + caret)
  input.dispatchEvent(new Event('input', { bubbles: true }))
}

let instances = 0
</script>

<script setup>
// Barra de símbolos matemáticos, una sola para todo un formulario: inserta
// en el campo que devuelva `target` (normalmente el último que tuvo el foco).
// No depende de ningún método.
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  // () => HTMLInputElement | null, evaluada en cada clic.
  target: { type: Function, required: true },
  // Texto opcional que indica dónde se va a insertar (ej. "ecuación 2").
  targetLabel: { type: String, default: '' },
  symbols: { type: Array, default: () => DEFAULT_SYMBOLS },
  // [{ label, symbols }]; vacío oculta el desplegable.
  moreGroups: { type: Array, default: () => DEFAULT_MORE_GROUPS },
})

function onInsert(symbol) {
  const input = props.target()
  if (input) insertIntoInput(input, symbol.insert)
}

// Desplegable "Más funciones": mismo comportamiento que los menús del nav
// (NavMenu.vue): se abre con clic/tap y se cierra al elegir, al hacer clic
// fuera o con Escape.
const menuId = `symbol-more-${++instances}`
const open = ref(false)
const moreRef = ref(null)
const triggerRef = ref(null)

function close({ restoreFocus = false } = {}) {
  open.value = false
  if (restoreFocus) triggerRef.value?.focus()
}

function onMoreInsert(symbol) {
  onInsert(symbol)
  close()
}

function onDocumentPointerDown(event) {
  if (open.value && !moreRef.value?.contains(event.target)) close()
}

function onDocumentKeydown(event) {
  if (open.value && event.key === 'Escape') close({ restoreFocus: true })
}

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
  <div class="symbol-toolbar" role="toolbar" aria-label="Símbolos matemáticos">
    <!-- mousedown.prevent: el clic no le quita el foco al campo, así que el
         cursor sigue donde estaba (también con el teclado virtual del móvil). -->
    <button
      v-for="symbol in symbols"
      :key="symbol.insert"
      type="button"
      class="symbol-btn"
      :title="`${symbol.name}: ${symbol.insert}`"
      :aria-label="`Insertar ${symbol.name.toLowerCase()} (${symbol.insert})`"
      @mousedown.prevent
      @click="onInsert(symbol)"
    >
      {{ symbol.label }}
    </button>

    <div v-if="moreGroups.length" ref="moreRef" class="symbol-more">
      <button
        ref="triggerRef"
        type="button"
        class="symbol-btn more-trigger"
        :aria-expanded="open"
        :aria-controls="menuId"
        @mousedown.prevent
        @click="open = !open"
      >
        Más funciones <span class="more-caret" aria-hidden="true">▾</span>
      </button>

      <div v-if="open" :id="menuId" class="more-menu">
        <div v-for="(group, g) in moreGroups" :key="group.label" class="more-group">
          <p :id="`${menuId}-${g}`" class="more-group-label">{{ group.label }}</p>
          <div class="more-group-buttons" role="group" :aria-labelledby="`${menuId}-${g}`">
            <button
              v-for="symbol in group.symbols"
              :key="symbol.insert"
              type="button"
              class="symbol-btn"
              :title="`${symbol.name}: ${symbol.insert}`"
              :aria-label="`Insertar ${symbol.name.toLowerCase()} (${symbol.insert})`"
              @mousedown.prevent
              @click="onMoreInsert(symbol)"
            >
              {{ symbol.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <span v-if="targetLabel" class="symbol-target">Se inserta en la {{ targetLabel }}</span>
  </div>
</template>

<style scoped>
.symbol-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2);
  background: var(--color-sunken);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
}

.symbol-btn {
  min-width: 40px;
  min-height: 36px;
  padding: 0 var(--space-2);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-control);
  color: var(--color-ink);
  font-family: 'Cambria Math', 'Times New Roman', serif;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast);
}

.symbol-btn:hover {
  border-color: var(--color-line-strong);
  background: var(--color-accent-soft);
}

.symbol-btn:focus-visible {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--focus-ring);
}

.symbol-more {
  position: relative;
  display: flex;
}

/* El disparador usa la tipografía de la interfaz, no la matemática. */
.more-trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: inherit;
  font-size: var(--text-small);
  font-weight: var(--weight-medium);
}

.more-trigger[aria-expanded='true'] {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.more-caret {
  font-size: 0.75em;
}

/* Mismo aspecto que los menús del nav (NavMenu.vue). */
.more-menu {
  position: absolute;
  top: calc(100% + var(--space-1));
  left: 0;
  z-index: 20;
  min-width: 220px;
  padding: var(--space-2);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  box-shadow: var(--shadow-interactive-hover);
}

.more-group + .more-group {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-line);
}

.more-group-label {
  margin: 0 0 var(--space-1);
  padding: 0 var(--space-1);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
}

.more-group-buttons {
  display: flex;
  gap: var(--space-1);
}

.more-group-buttons .symbol-btn {
  flex: 1;
}

.symbol-target {
  margin-left: auto;
  padding: 0 var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

@media (max-width: 480px) {
  /* Seis por fila: los 12 botones quedan en dos filas parejas. */
  .symbol-toolbar > .symbol-btn {
    flex: 1 0 calc(100% / 6 - var(--space-1));
    min-width: 0;
    padding: 0;
  }

  /* El desplegable ocupa su propia fila y el menú, todo el ancho de la barra. */
  .symbol-more {
    flex-basis: 100%;
  }

  .more-trigger {
    flex: 1;
    justify-content: center;
  }

  .more-menu {
    right: 0;
    min-width: 0;
  }

  .symbol-target {
    flex-basis: 100%;
    margin-left: 0;
    padding-top: var(--space-1);
  }
}
</style>
