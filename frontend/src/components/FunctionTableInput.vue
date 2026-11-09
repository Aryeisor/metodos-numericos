<script setup>
// Formulario de dos modos (diferenciación e integración numérica):
//  - Función: f(x) con la barra de símbolos y la vista previa en vivo de los
//    métodos no lineales (mismo parser y endpoint, variable x) y una fila de
//    campos numéricos (x₀ y h₀ en diferenciación; a y b en integración).
//  - Tabla de datos: puntos (xᵢ, yᵢ) con filas para agregar y quitar, y una
//    función opcional para comparar (también con vista previa).
// Los campos numéricos aceptan fracciones, como en los demás formularios.
//
// Lo que cambia por categoría sale del store (opcional; por defecto, lo de
// diferenciación): maxPoints, startFields { title, labels, errorLabels },
// compareHint y tableUnavailable { text, links } (sin modo tabla: una nota con
// enlaces en lugar del selector de modo).
import { computed, reactive, ref, watch } from 'vue'
import EquationPreview from './EquationPreview.vue'
import MathSymbolToolbar from './MathSymbolToolbar.vue'
import MathSyntaxHelp from './MathSyntaxHelp.vue'
import NumericFieldsInput from './NumericFieldsInput.vue'
import { useExpressionPreviews } from '../composables/useExpressionPreviews'
import { solveRouteName } from '../methods/routeNames'
import { formatNumber } from '../utils/iterationSteps'
import { INPUT_ERROR_MESSAGES, parseNumericInput } from '../utils/numberInput'

const MODES = { FUNCTION: 'function', TABLE: 'table' }
const DEFAULT_START_FIELDS = {
  title: 'Punto x₀ y paso inicial h₀ (h₀ > 0, por defecto 0.1)',
  labels: ['x₀', 'h₀'],
  errorLabels: ['Punto x₀', 'Paso inicial h₀'],
}
const DEFAULT_COMPARE_HINT =
  'Si conoces la función de la que salen los datos, escríbela para comparar con la derivada ' +
  'exacta, ver el error real y la cota, y comprobar los datos.'

const props = defineProps({
  store: { type: Object, required: true },
})

const state = computed(() => props.store.state)
const isTable = computed(() => state.value.mode === MODES.TABLE)
const MIN_POINTS = computed(() => props.store.minPoints)
const MAX_POINTS = computed(() => props.store.maxPoints ?? 20)
const startFields = computed(() => props.store.startFields ?? DEFAULT_START_FIELDS)
const compareHint = computed(() => props.store.compareHint ?? DEFAULT_COMPARE_HINT)

// --- f(x) o la función para comparar: un solo campo de texto visible ------
const functionText = computed({
  get: () => (isTable.value ? state.value.compare : state.value.function),
  set: (text) => {
    if (isTable.value) state.value.compare = text
    else state.value.function = text
  },
})
const { previews } = useExpressionPreviews(
  () => [functionText.value],
  () => ['x']
)
const preview = computed(() => previews.value[0] ?? { status: 'empty', stale: false })
const isInvalid = computed(() => preview.value.status === 'invalid' && !preview.value.stale)
const functionRef = ref(null)
const symbolTarget = () => functionRef.value

// --- Tabla de puntos ---------------------------------------------------------
// El componente es dueño del texto de cada casilla; el estado guarda números
// (null si está vacía, NaN si el texto no es válido).
const texts = ref([])
const errors = reactive({})
const editing = ref(null)

const shown = (value) => (value === null || Number.isNaN(value) ? '' : formatNumber(value))

function syncTexts() {
  texts.value = state.value.points.map((point, i) =>
    point.map((value, j) => (editing.value === `${i}-${j}` ? texts.value[i]?.[j] ?? '' : shown(value)))
  )
}
syncTexts()
watch(() => state.value.points, syncTexts, { deep: true })
watch(
  () => state.value.points.length,
  () => {
    for (const key of Object.keys(errors)) delete errors[key]
  }
)

function onCellInput(i, j, text) {
  texts.value[i][j] = text
  delete errors[`${i}-${j}`]
  const value = text.trim() === '' ? null : parseNumericInput(text).value
  const points = state.value.points.map((point) => [...point])
  points[i][j] = value
  state.value.points = points
}

function onCellBlur(i, j) {
  editing.value = null
  const text = texts.value[i][j]
  const { error } = parseNumericInput(text)
  if (text.trim() !== '' && error) {
    errors[`${i}-${j}`] = INPUT_ERROR_MESSAGES[error]
    return
  }
  texts.value[i][j] = shown(state.value.points[i][j])
}

const errorList = computed(() =>
  Object.entries(errors).map(([key, message]) => {
    const [i, j] = key.split('-').map(Number)
    return { key, label: `Fila ${i + 1}, ${j === 0 ? 'x' : 'f(x)'}`, message }
  })
)

const SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'
const sub = (n) => String(n).replace(/\d/g, (d) => SUBSCRIPTS[d])
</script>

<template>
  <div>
    <!-- Un método sin modo tabla (cuadratura gaussiana) explica por qué en lugar del selector. -->
    <p v-if="store.tableUnavailable" class="table-unavailable">
      {{ store.tableUnavailable.text }}
      <template v-for="(link, idx) in store.tableUnavailable.links" :key="link.slug">
        <RouterLink :to="{ name: solveRouteName(link.slug) }">{{ link.label }}</RouterLink>{{
          idx === store.tableUnavailable.links.length - 1 ? '.' : idx === store.tableUnavailable.links.length - 2 ? ' o ' : ', '
        }}
      </template>
    </p>
    <div v-else class="mode-switch" role="radiogroup" aria-label="Modo de entrada">
      <button
        v-for="option in [
          { mode: MODES.FUNCTION, label: 'Función' },
          { mode: MODES.TABLE, label: 'Tabla de datos' },
        ]"
        :key="option.mode"
        type="button"
        role="radio"
        class="mode-btn"
        :class="{ 'is-active': state.mode === option.mode }"
        :aria-checked="state.mode === option.mode"
        @click="store.setMode(option.mode)"
      >
        {{ option.label }}
      </button>
    </div>

    <template v-if="isTable">
      <p class="input-hint first-hint">
        Escribe los puntos medidos, con x estrictamente creciente (de {{ MIN_POINTS }} a
        {{ MAX_POINTS }} puntos). Admiten fracciones, por ejemplo <strong>1/3</strong>.
      </p>
      <div class="table-scroll">
        <table class="points-table">
          <thead>
            <tr>
              <th scope="col">i</th>
              <th scope="col">xᵢ</th>
              <th scope="col">f(xᵢ)</th>
              <th scope="col"><span class="visually-hidden">Quitar</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(point, i) in state.points" :key="i">
              <td class="index-cell">{{ i + 1 }}</td>
              <td v-for="j in [0, 1]" :key="j">
                <input
                  type="text"
                  inputmode="decimal"
                  :value="texts[i]?.[j] ?? ''"
                  :class="{ 'is-invalid': errors[`${i}-${j}`] }"
                  :aria-invalid="Boolean(errors[`${i}-${j}`])"
                  :aria-label="`${j === 0 ? 'x' : 'f(x)'} del punto ${i + 1}`"
                  :title="errors[`${i}-${j}`]"
                  :placeholder="j === 0 ? `x${sub(i + 1)}` : `y${sub(i + 1)}`"
                  @input="onCellInput(i, j, $event.target.value)"
                  @focus="editing = `${i}-${j}`"
                  @blur="onCellBlur(i, j)"
                />
              </td>
              <td>
                <button
                  type="button"
                  class="btn btn-secondary remove-btn"
                  :disabled="state.points.length <= MIN_POINTS"
                  :aria-label="`Quitar el punto ${i + 1}`"
                  :title="state.points.length <= MIN_POINTS ? `Se necesitan al menos ${MIN_POINTS} puntos` : 'Quitar punto'"
                  @click="store.removeRow(i)"
                >
                  ×
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <button
        type="button"
        class="btn btn-outline add-btn"
        :disabled="state.points.length >= MAX_POINTS"
        @click="store.addRow()"
      >
        + Agregar punto
      </button>
      <span v-if="state.points.length >= MAX_POINTS" class="limit-note">Máximo {{ MAX_POINTS }} puntos.</span>
      <ul v-if="errorList.length" class="input-errors">
        <li v-for="item in errorList" :key="item.key">{{ item.label }}: {{ item.message }}</li>
      </ul>
    </template>

    <div class="function-block">
      <MathSymbolToolbar class="function-toolbar" :target="symbolTarget" />
      <label for="difference-function">
        {{ isTable ? 'Función para comparar (opcional)' : 'Función f(x)' }}
      </label>
      <input
        id="difference-function"
        ref="functionRef"
        v-model="functionText"
        type="text"
        class="function-input"
        spellcheck="false"
        autocomplete="off"
        :placeholder="isTable ? 'ej. 2x^2' : 'ej. ln(x)'"
        :class="{ 'is-invalid': isInvalid }"
        :aria-invalid="isInvalid"
        aria-describedby="difference-preview"
      />
      <EquationPreview id="difference-preview" :preview="preview" :text="functionText" lhs="f(x)" />
      <p class="input-hint">
        <template v-if="isTable">{{ compareHint }}</template>
        <template v-else>
          Escribe f en la variable x (<code>ln(x)</code>, <code>x^3 - 2x^2 + x</code>,
          <code>x*exp(x)</code>). Las funciones trigonométricas se evalúan en radianes.
        </template>
      </p>
    </div>

    <NumericFieldsInput
      v-if="!isTable"
      :title="startFields.title"
      suffix=""
      :values="state.start"
      :labels="startFields.labels"
      :error-labels="startFields.errorLabels"
      @update:values="(values) => (state.start = values)"
    />

    <div class="syntax-block">
      <p class="syntax-caption">Cómo escribir cada operación</p>
      <MathSyntaxHelp />
    </div>
  </div>
</template>

<style scoped>
.mode-switch {
  display: inline-flex;
  gap: 0;
  margin-bottom: var(--space-4);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  overflow: hidden;
}

.mode-btn {
  padding: var(--space-2) var(--space-4);
  border: none;
  background: var(--color-surface);
  color: var(--color-ink);
  font-size: var(--text-body);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.mode-btn + .mode-btn {
  border-left: 1px solid var(--color-line-strong);
}

.mode-btn:hover {
  background: var(--color-accent-soft);
}

.mode-btn.is-active {
  background: var(--color-accent);
  color: var(--color-on-accent);
  font-weight: var(--weight-semibold);
}

.mode-btn:focus-visible {
  outline: none;
  box-shadow: inset var(--focus-ring);
}

.table-unavailable {
  margin: 0 0 var(--space-4);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  background: var(--color-accent-soft);
  font-size: var(--text-small);
  color: var(--color-ink);
}

.points-table {
  width: auto;
}

.points-table th,
.points-table td {
  padding: var(--space-1) var(--space-2);
  text-align: center;
}

.points-table input {
  width: 120px;
  text-align: right;
}

.index-cell {
  color: var(--color-ink-muted);
  font-variant-numeric: tabular-nums;
}

.remove-btn {
  padding: var(--space-1) var(--space-3);
}

.add-btn {
  margin-top: var(--space-3);
}

.limit-note {
  margin-left: var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.function-block {
  margin-top: var(--space-5);
}

.function-toolbar {
  margin-bottom: var(--space-3);
}

.function-input {
  font-family: 'Consolas', 'Courier New', monospace;
}

.equation-preview {
  margin-top: var(--space-2);
}

.input-hint {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.first-hint {
  margin: 0 0 var(--space-3);
}

.input-hint code {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.95em;
  color: var(--color-ink);
}

.syntax-block {
  margin-top: var(--space-5);
}

.syntax-caption {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
}

.input-errors {
  margin: var(--space-4) 0 0;
  padding-left: var(--space-5);
  font-size: var(--text-small);
  color: var(--color-danger);
}

.is-invalid {
  border-color: var(--color-danger);
}

.is-invalid:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px var(--color-danger-bg);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

@media (max-width: 480px) {
  .points-table input {
    width: 92px;
  }
}
</style>
