<script setup>
// Formulario de un sistema no lineal: una fila por ecuación con la variable
// que se despeja de ella, controles para agregar/quitar ecuaciones y el punto
// inicial x0 (acepta fracciones, como los campos de los sistemas lineales).
// Una barra de símbolos inserta en la última ecuación que tuvo el foco y cada
// ecuación muestra en vivo cómo la interpretó el parser del backend.
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

// Vista previa por fila: LaTeX si la ecuación es válida, o su error.
const { previews } = useExpressionPreviews(
  () => state.value.equations,
  () => state.value.variables
)

const previewOf = (i) => previews.value[i] ?? { status: 'empty', stale: false }
const isInvalid = (i) => previewOf(i).status === 'invalid' && !previewOf(i).stale

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

function removeEquation(index) {
  props.store.removeEquation(index)
  // La fila activa de la barra de símbolos sigue apuntando a la misma ecuación.
  if (index < activeIndex.value) activeIndex.value -= 1
  activeIndex.value = Math.min(activeIndex.value, n.value - 1)
}
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
        <EquationPreview :id="`equation-preview-${i}`" :preview="previewOf(i)" :text="text" />
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

    <NumericFieldsInput
      :values="state.x0"
      :labels="state.variables"
      @update:values="(values) => (state.x0 = values)"
    />
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

/* Vista previa debajo del campo de la ecuación, en la misma columna. */
.equation-preview {
  grid-column: 3 / 4;
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

.is-invalid {
  border-color: var(--color-danger);
}

.is-invalid:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px var(--color-danger-bg);
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

}
</style>
