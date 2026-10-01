<script setup>
// Formulario de un sistema no lineal: una fila por ecuación con la variable
// que se despeja de ella, controles para agregar/quitar ecuaciones y el punto
// inicial x0 (acepta fracciones, como los campos de los sistemas lineales).
// Una barra de símbolos inserta en la última ecuación que tuvo el foco y cada
// ecuación muestra en vivo cómo la interpretó el parser del backend.
import { computed, reactive, ref, watch } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import MathSymbolToolbar from '../../components/MathSymbolToolbar.vue'
import MathSyntaxHelp from '../../components/MathSyntaxHelp.vue'
import { useExpressionPreviews } from '../../composables/useExpressionPreviews'
import { formatNumber } from '../../utils/iterationSteps'
import { INPUT_ERROR_MESSAGES, parseNumericInput } from '../../utils/numberInput'
import { MAX_EQUATIONS, MIN_EQUATIONS } from './store'

const props = defineProps({
  store: { type: Object, required: true },
})

const state = computed(() => props.store.state)
const n = computed(() => state.value.equations.length)

// Vista previa por fila: LaTeX si la ecuación es válida, o su error.
const { previews } = useExpressionPreviews(
  () => state.value.equations,
  () => state.value.variables
)

const previewOf = (i) => previews.value[i] ?? { status: 'empty', stale: false }
const isInvalid = (i) => previewOf(i).status === 'invalid' && !previewOf(i).stale

// Punto Fijo interpreta una expresión sin '=' como "expresión = 0"; la vista
// previa lo muestra así para que se vea exactamente lo que se va a resolver.
function previewLatex(i) {
  const { latex } = previewOf(i)
  return state.value.equations[i].includes('=') ? latex : `${latex} = 0`
}

// Barra de símbolos: inserta en la última ecuación que tuvo el foco (la
// primera, si todavía ninguna lo tuvo).
const listRef = ref(null)
const activeIndex = ref(0)
const symbolTarget = () =>
  listRef.value?.querySelectorAll('.equation-input')[Math.min(activeIndex.value, n.value - 1)] ??
  null

function updateEquation(index, text) {
  state.value.equations = state.value.equations.map((v, i) => (i === index ? text : v))
}

function updateVariable(index, text) {
  state.value.variables = state.value.variables.map((v, i) => (i === index ? text : v))
}

// x0: el componente es dueño del TEXTO; al store sólo llega el número con su
// precisión completa (NaN mientras el texto no sea válido). Mismo criterio
// que MatrixInput: el error se muestra al salir del campo.
const x0Texts = ref([])
const x0Errors = reactive({})
const editingIndex = ref(null)

function displayText(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return ''
  return formatNumber(value)
}

function syncX0Texts() {
  x0Texts.value = state.value.x0.map((value, i) =>
    editingIndex.value === i ? x0Texts.value[i] : displayText(value)
  )
}

syncX0Texts()
watch(() => state.value.x0, syncX0Texts)

function onX0Input(index, text) {
  x0Texts.value[index] = text
  delete x0Errors[index]
  const { value } = parseNumericInput(text)
  state.value.x0 = state.value.x0.map((v, i) => (i === index ? value : v))
}

function onX0Blur(index) {
  editingIndex.value = null
  const { error } = parseNumericInput(x0Texts.value[index])
  if (error) {
    x0Errors[index] = INPUT_ERROR_MESSAGES[error]
    return
  }
  x0Texts.value[index] = displayText(state.value.x0[index])
}

function removeEquation(index) {
  props.store.removeEquation(index)
  // La fila activa de la barra de símbolos sigue apuntando a la misma ecuación.
  if (index < activeIndex.value) activeIndex.value -= 1
  activeIndex.value = Math.min(activeIndex.value, n.value - 1)
  // Los errores de x0 están indexados por posición: se descartan al quitar filas.
  for (const key of Object.keys(x0Errors)) delete x0Errors[key]
}

const x0ErrorList = computed(() =>
  Object.keys(x0Errors).map((index) => ({
    index,
    label: `${state.value.variables[index] || `variable ${Number(index) + 1}`} inicial`,
    message: x0Errors[index],
  }))
)
</script>

<template>
  <div>
    <MathSymbolToolbar
      class="equation-toolbar"
      :target="symbolTarget"
      :target-label="`ecuación ${Math.min(activeIndex, n - 1) + 1}`"
    />

    <div ref="listRef" class="equation-list">
      <div class="equation-head" aria-hidden="true">
        <span></span>
        <span>Variable</span>
        <span>Ecuación</span>
        <span></span>
      </div>
      <div v-for="(text, i) in state.equations" :key="i" class="equation-row">
        <span class="equation-index" :class="{ 'is-target': i === activeIndex }">{{ i + 1 }}</span>
        <input
          type="text"
          class="variable-input"
          spellcheck="false"
          autocomplete="off"
          :value="state.variables[i]"
          :aria-label="`Variable que se despeja de la ecuación ${i + 1}`"
          @input="updateVariable(i, $event.target.value)"
        />
        <input
          type="text"
          class="equation-input"
          spellcheck="false"
          autocomplete="off"
          :value="text"
          :placeholder="i === 0 ? 'ej. 3*x - cos(y) - 1 = 0' : ''"
          :aria-label="`Ecuación ${i + 1}`"
          :class="{ 'is-invalid': isInvalid(i) }"
          :aria-invalid="isInvalid(i)"
          :aria-describedby="`equation-preview-${i}`"
          @input="updateEquation(i, $event.target.value)"
          @focus="activeIndex = i"
        />
        <button
          type="button"
          class="btn btn-secondary remove-btn"
          :disabled="n <= MIN_EQUATIONS"
          :aria-label="`Quitar la ecuación ${i + 1}`"
          :title="n <= MIN_EQUATIONS ? `Se necesitan al menos ${MIN_EQUATIONS} ecuaciones` : 'Quitar ecuación'"
          @click="removeEquation(i)"
        >
          ×
        </button>
        <!-- Vista previa: aparece cuando llega la primera respuesta; mientras
             se consulta un cambio se sigue viendo la anterior, atenuada. -->
        <div
          :id="`equation-preview-${i}`"
          class="equation-preview"
          :class="{ 'is-stale': previewOf(i).stale, 'is-error': previewOf(i).status === 'invalid' }"
          aria-live="polite"
        >
          <MathFormula v-if="previewOf(i).status === 'valid'" :expression="previewLatex(i)" />
          <span v-else-if="previewOf(i).status === 'invalid'">{{ previewOf(i).error }}</span>
        </div>
      </div>
    </div>

    <button
      type="button"
      class="btn btn-outline add-btn"
      :disabled="n >= MAX_EQUATIONS"
      @click="store.addEquation()"
    >
      + Agregar ecuación
    </button>
    <span v-if="n >= MAX_EQUATIONS" class="limit-note">Máximo {{ MAX_EQUATIONS }} ecuaciones.</span>

    <p class="input-hint">
      La ecuación de cada fila se despeja automáticamente para la variable de esa fila.
      Puedes escribirla igualada a cero (<code>3*x - cos(y) - 1 = 0</code>) o con dos lados
      (<code>y = (sin(x) + 2)/4</code>). Debajo de cada ecuación verás cómo se interpretó.
    </p>

    <div class="syntax-block">
      <p class="syntax-caption">Cómo escribir cada operación</p>
      <MathSyntaxHelp />
    </div>

    <div class="x0-row">
      <label>Punto inicial x0 (opcional, por defecto ceros)</label>
      <div class="x0-inputs">
        <div v-for="(value, i) in state.x0" :key="'x0-' + i" class="x0-item">
          <span class="x0-label">{{ state.variables[i] || '?' }}⁽⁰⁾</span>
          <input
            type="text"
            inputmode="decimal"
            :value="x0Texts[i]"
            :class="{ 'is-invalid': x0Errors[i] }"
            :aria-invalid="Boolean(x0Errors[i])"
            :aria-label="`Valor inicial de ${state.variables[i] || `la variable ${i + 1}`}`"
            :title="x0Errors[i]"
            @input="onX0Input(i, $event.target.value)"
            @focus="editingIndex = i"
            @blur="onX0Blur(i)"
          />
        </div>
      </div>
      <p class="input-hint">
        Admite fracciones, por ejemplo <strong>1/3</strong>; el cálculo usa el valor exacto.
      </p>
    </div>

    <ul v-if="x0ErrorList.length" class="input-errors">
      <li v-for="item in x0ErrorList" :key="item.index">{{ item.label }}: {{ item.message }}</li>
    </ul>
  </div>
</template>

<style scoped>
.equation-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Columnas: número | variable | ecuación | quitar. */
.equation-head,
.equation-row {
  display: grid;
  grid-template-columns: 1.5rem 6rem minmax(0, 1fr) auto;
  gap: var(--space-2);
  align-items: center;
}

.equation-head span {
  font-size: var(--text-small);
  font-weight: var(--weight-medium);
  color: var(--color-ink-muted);
}

.equation-index {
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  text-align: right;
}

.equation-index.is-target {
  color: var(--color-accent);
}

.variable-input,
.equation-input {
  font-family: 'Consolas', 'Courier New', monospace;
}

.equation-toolbar {
  margin-bottom: var(--space-4);
}

/* Debajo del campo de la ecuación, en la misma columna. Vacía (sin
   respuesta todavía o fila en blanco) no ocupa espacio. */
.equation-preview {
  grid-column: 3 / 4;
  margin-top: calc(-1 * var(--space-1));
  padding: var(--space-1) var(--space-2);
  overflow-x: auto;
  font-size: var(--text-small);
  color: var(--color-ink);
  background: var(--color-sunken);
  border-radius: var(--radius-control);
  transition: opacity var(--transition-fast);
}

.equation-preview:empty {
  display: none;
}

.equation-preview.is-error {
  color: var(--color-danger);
  background: var(--color-danger-bg);
}

/* Se está consultando un cambio: se ve la vista previa anterior, atenuada. */
.equation-preview.is-stale {
  opacity: 0.5;
}

.equation-preview :deep(.katex) {
  font-size: 1.1em;
}

.syntax-block {
  margin-top: var(--space-4);
}

.syntax-caption {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.remove-btn {
  justify-content: center;
  width: 36px;
  min-height: 36px;
  padding: 0;
  font-size: 1.125rem;
  line-height: 1;
}

.add-btn {
  margin-top: var(--space-3);
}

.limit-note {
  margin-left: var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.input-hint {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.input-hint code {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.95em;
  color: var(--color-ink);
}

.x0-row {
  margin-top: var(--space-5);
}

.x0-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.x0-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.x0-label {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  font-weight: var(--weight-medium);
}

.x0-item input {
  width: 92px;
  text-align: right;
}

.is-invalid {
  border-color: var(--color-danger);
}

.is-invalid:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px var(--color-danger-bg);
}

.input-errors {
  margin: var(--space-4) 0 0;
  padding-left: var(--space-5);
  font-size: var(--text-small);
  color: var(--color-danger);
}

/* En pantallas angostas la variable y la ecuación comparten fila con menos
   espacio para el nombre. */
@media (max-width: 480px) {
  .equation-head,
  .equation-row {
    grid-template-columns: 1rem 3.5rem minmax(0, 1fr) auto;
  }

  /* En móvil la vista previa usa también el ancho de la columna de variable. */
  .equation-preview {
    grid-column: 2 / 5;
  }

  .x0-item input {
    width: 72px;
  }
}
</style>
