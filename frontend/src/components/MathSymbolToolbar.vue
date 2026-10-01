<script>
// Símbolos por defecto. `insert` termina en "()" para las funciones: el
// cursor queda entre los paréntesis (o se envuelve el texto seleccionado).
export const DEFAULT_SYMBOLS = [
  { label: '√', insert: 'sqrt()', name: 'Raíz cuadrada' },
  { label: 'xⁿ', insert: '^', name: 'Potencia' },
  { label: 'log', insert: 'log()', name: 'Logaritmo en base 10' },
  { label: 'ln', insert: 'ln()', name: 'Logaritmo natural' },
  { label: 'sin', insert: 'sin()', name: 'Seno' },
  { label: 'cos', insert: 'cos()', name: 'Coseno' },
  { label: 'tan', insert: 'tan()', name: 'Tangente' },
  { label: 'π', insert: 'pi', name: 'Número pi' },
  { label: 'e', insert: 'e', name: 'Número e' },
  { label: '|x|', insert: 'abs()', name: 'Valor absoluto' },
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
</script>

<script setup>
// Barra de símbolos matemáticos, una sola para todo un formulario: inserta
// en el campo que devuelva `target` (normalmente el último que tuvo el foco).
// No depende de ningún método.
const props = defineProps({
  // () => HTMLInputElement | null, evaluada en cada clic.
  target: { type: Function, required: true },
  // Texto opcional que indica dónde se va a insertar (ej. "ecuación 2").
  targetLabel: { type: String, default: '' },
  symbols: { type: Array, default: () => DEFAULT_SYMBOLS },
})

function onInsert(symbol) {
  const input = props.target()
  if (input) insertIntoInput(input, symbol.insert)
}
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

.symbol-target {
  margin-left: auto;
  padding: 0 var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

@media (max-width: 480px) {
  .symbol-btn {
    flex: 1 0 calc(20% - var(--space-1));
    min-width: 0;
  }

  .symbol-target {
    flex-basis: 100%;
    margin-left: 0;
    padding-top: var(--space-1);
  }
}
</style>
