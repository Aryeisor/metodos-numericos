<script setup>
// Formulario de un sistema no lineal: una fila por ecuación con la variable
// que se despeja de ella, controles para agregar/quitar ecuaciones y el punto
// inicial x0 (acepta fracciones, como los campos de los sistemas lineales).
import { computed, reactive, ref, watch } from 'vue'
import { formatNumber } from '../../utils/iterationSteps'
import { INPUT_ERROR_MESSAGES, parseNumericInput } from '../../utils/numberInput'
import { MAX_EQUATIONS, MIN_EQUATIONS } from './store'

const props = defineProps({
  store: { type: Object, required: true },
})

const state = computed(() => props.store.state)
const n = computed(() => state.value.equations.length)

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
    <div class="equation-list">
      <div class="equation-head" aria-hidden="true">
        <span></span>
        <span>Variable</span>
        <span>Ecuación</span>
        <span></span>
      </div>
      <div v-for="(text, i) in state.equations" :key="i" class="equation-row">
        <span class="equation-index">{{ i + 1 }}</span>
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
          @input="updateEquation(i, $event.target.value)"
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
      (<code>y = (sin(x) + 2)/4</code>). Usa <code>^</code> para potencias y las funciones
      sin, cos, tan, exp, log, sqrt, abs (entre otras) y las constantes pi y e.
    </p>

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

.variable-input,
.equation-input {
  font-family: 'Consolas', 'Courier New', monospace;
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

  .x0-item input {
    width: 72px;
  }
}
</style>
