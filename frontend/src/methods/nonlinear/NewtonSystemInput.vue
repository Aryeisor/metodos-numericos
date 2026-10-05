<script setup>
// Formulario de Newton: las variables se declaran en orden en un campo propio
// y las ecuaciones se escriben sin asociarlas a ninguna variable (no se
// despeja nada). Reutiliza la barra de símbolos, la vista previa en vivo y el
// punto inicial con fracciones de Punto Fijo.
import { computed, ref } from 'vue'
import MathSymbolToolbar from '../../components/MathSymbolToolbar.vue'
import MathSyntaxHelp from '../../components/MathSyntaxHelp.vue'
import { useExpressionPreviews } from '../../composables/useExpressionPreviews'
import EquationPreview from '../../components/EquationPreview.vue'
import NumericFieldsInput from '../../components/NumericFieldsInput.vue'
import { MAX_EQUATIONS, MIN_EQUATIONS } from './store'

const props = defineProps({
  store: { type: Object, required: true },
})

const state = computed(() => props.store.state)
const n = computed(() => state.value.equations.length)
const variables = computed(() => props.store.variables())

const { previews } = useExpressionPreviews(
  () => state.value.equations,
  () => variables.value
)
const previewOf = (i) => previews.value[i] ?? { status: 'empty', stale: false }
const isInvalid = (i) => previewOf(i).status === 'invalid' && !previewOf(i).stale

// Newton resuelve un sistema lineal n×n en cada iteración: hacen falta tantas
// variables como ecuaciones.
const countMismatch = computed(() =>
  variables.value.length !== n.value
    ? `Hay ${n.value} ecuaciones y ${variables.value.length} variables: deben coincidir.`
    : ''
)

const listRef = ref(null)
const activeIndex = ref(0)
const symbolTarget = () =>
  listRef.value?.querySelectorAll('.equation-input')[Math.min(activeIndex.value, n.value - 1)] ??
  null

function updateEquation(index, text) {
  state.value.equations = state.value.equations.map((v, i) => (i === index ? text : v))
}

function removeEquation(index) {
  props.store.removeEquation(index)
  if (index < activeIndex.value) activeIndex.value -= 1
  activeIndex.value = Math.min(activeIndex.value, n.value - 1)
}
</script>

<template>
  <div>
    <div class="variables-field">
      <label for="newton-variables">Variables, en orden</label>
      <input
        id="newton-variables"
        type="text"
        class="variables-input"
        spellcheck="false"
        autocomplete="off"
        placeholder="ej. x, y, z"
        :value="state.variablesText"
        aria-describedby="newton-variables-hint"
        @input="store.setVariablesText($event.target.value)"
      />
      <p id="newton-variables-hint" class="input-hint">
        Separadas por comas. El orden fija las columnas del Jacobiano y el de x0.
      </p>
    </div>

    <MathSymbolToolbar
      class="equation-toolbar"
      :target="symbolTarget"
      :target-label="`ecuación ${Math.min(activeIndex, n - 1) + 1}`"
    />

    <div ref="listRef" class="equation-list">
      <div class="equation-head" aria-hidden="true">
        <span></span>
        <span>Ecuación</span>
        <span></span>
      </div>
      <div v-for="(text, i) in state.equations" :key="i" class="equation-row">
        <span class="equation-index" :class="{ 'is-target': i === activeIndex }">{{ i + 1 }}</span>
        <input
          type="text"
          class="equation-input"
          spellcheck="false"
          autocomplete="off"
          :value="text"
          :placeholder="i === 0 ? 'ej. x^2 + x*y - 10 = 0' : ''"
          :aria-label="`Ecuación ${i + 1}`"
          :class="{ 'is-invalid': isInvalid(i) }"
          :aria-invalid="isInvalid(i)"
          :aria-describedby="`newton-preview-${i}`"
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
        <EquationPreview :id="`newton-preview-${i}`" :preview="previewOf(i)" :text="text" />
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
    <p v-if="countMismatch" class="count-mismatch" role="status">{{ countMismatch }}</p>

    <p class="input-hint">
      Escribe cada ecuación igualada a cero (<code>x^2 + x*y - 10 = 0</code>) o con dos lados
      (<code>x^2 + x*y = 10</code>); no hace falta despejar nada. Debajo de cada ecuación verás
      cómo se interpretó.
    </p>

    <div class="syntax-block">
      <p class="syntax-caption">Cómo escribir cada operación</p>
      <MathSyntaxHelp />
    </div>

    <NumericFieldsInput
      :values="state.x0"
      :labels="variables"
      @update:values="(values) => (state.x0 = values)"
    />
  </div>
</template>

<style scoped>
.variables-field {
  margin-bottom: var(--space-4);
}

.variables-input {
  max-width: 320px;
  font-family: 'Consolas', 'Courier New', monospace;
}

.equation-toolbar {
  margin-bottom: var(--space-4);
}

.equation-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Columnas: número | ecuación | quitar. */
.equation-head,
.equation-row {
  display: grid;
  grid-template-columns: 1.5rem minmax(0, 1fr) auto;
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

.equation-input {
  font-family: 'Consolas', 'Courier New', monospace;
}

/* Vista previa debajo del campo de la ecuación, en la misma columna. */
.equation-preview {
  grid-column: 2 / 3;
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

.count-mismatch {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
  color: var(--color-warning);
}

.input-hint {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.variables-field .input-hint {
  margin-top: var(--space-1);
}

.input-hint code {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.95em;
  color: var(--color-ink);
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

.is-invalid {
  border-color: var(--color-danger);
}

.is-invalid:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px var(--color-danger-bg);
}

@media (max-width: 480px) {
  .equation-head,
  .equation-row {
    grid-template-columns: 1rem minmax(0, 1fr) auto;
  }

  .variables-input {
    max-width: none;
  }
}
</style>
