<script setup>
// Formulario de Bairstow. Dos modos de entrada:
//  - Escribir polinomio: un campo de texto en x, con barra de símbolos
//    limitada a lo útil para polinomios y vista previa en vivo (el mismo
//    composable y endpoint que las ecuaciones no lineales, con la variable x).
//  - Coeficientes: grado de 3 a 10 y una casilla por coeficiente.
// En ambos, r₀ y s₀ (aceptan fracciones como los demás formularios).
import { computed, ref } from 'vue'
import EquationPreview from '../../components/EquationPreview.vue'
import MathFormula from '../../components/MathFormula.vue'
import MathSymbolToolbar from '../../components/MathSymbolToolbar.vue'
import NumericFieldsInput from '../../components/NumericFieldsInput.vue'
import { useExpressionPreviews } from '../../composables/useExpressionPreviews'
import { MAX_DEGREE, MIN_DEGREE, MODES } from './store'

const props = defineProps({
  store: { type: Object, required: true },
})

const state = computed(() => props.store.state)

// Sólo lo útil para escribir un polinomio: potencia, la variable,
// paréntesis y fracciones. Sin desplegable de funciones.
const POLYNOMIAL_SYMBOLS = [
  { label: 'xⁿ', insert: '^', name: 'Potencia' },
  { label: 'x', insert: 'x', name: 'La variable x' },
  { label: '( )', insert: '()', name: 'Paréntesis' },
  { label: 'a/b', insert: '/', name: 'Fracción' },
]

const { previews } = useExpressionPreviews(
  () => (state.value.mode === MODES.TEXT ? [state.value.text] : []),
  () => ['x']
)
const preview = computed(() => previews.value[0] ?? { status: 'empty', stale: false })
const isInvalid = computed(() => preview.value.status === 'invalid' && !preview.value.stale)

const textRef = ref(null)
const symbolTarget = () => textRef.value

const SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'
const SUPERSCRIPTS = '⁰¹²³⁴⁵⁶⁷⁸⁹'
const sub = (n) => String(n).replace(/\d/g, (d) => SUBSCRIPTS[d])
const sup = (n) => String(n).replace(/\d/g, (d) => SUPERSCRIPTS[d])

// a₅·x⁵, a₄·x⁴, …, a₁·x, a₀
const coefficientLabels = computed(() =>
  state.value.coefficients.map((_, p) => {
    const power = state.value.degree - p
    if (power === 0) return `a${sub(0)}`
    if (power === 1) return `a${sub(1)}·x`
    return `a${sub(power)}·x${sup(power)}`
  })
)
const coefficientErrorLabels = computed(() =>
  coefficientLabels.value.map((label) => `Coeficiente ${label}`)
)

const degrees = Array.from({ length: MAX_DEGREE - MIN_DEGREE + 1 }, (_, i) => MIN_DEGREE + i)
</script>

<template>
  <div>
    <div class="mode-switch" role="radiogroup" aria-label="Modo de entrada">
      <button
        v-for="option in [
          { mode: MODES.TEXT, label: 'Escribir polinomio' },
          { mode: MODES.COEFFICIENTS, label: 'Coeficientes' },
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

    <template v-if="state.mode === MODES.TEXT">
      <MathSymbolToolbar
        class="polynomial-toolbar"
        :target="symbolTarget"
        :symbols="POLYNOMIAL_SYMBOLS"
        :more-groups="[]"
      />
      <label for="polynomial-text">Polinomio en x</label>
      <input
        id="polynomial-text"
        ref="textRef"
        type="text"
        class="polynomial-input"
        spellcheck="false"
        autocomplete="off"
        placeholder="ej. x^3 - 6x^2 + 11x - 6"
        :value="state.text"
        :class="{ 'is-invalid': isInvalid }"
        :aria-invalid="isInvalid"
        aria-describedby="polynomial-preview"
        @input="state.text = $event.target.value"
      />
      <EquationPreview id="polynomial-preview" :preview="preview" :text="state.text" />
      <p class="input-hint">
        Escribe un polinomio en x de grado 3 a 10: potencias con <code>^</code>
        (<code>x^3</code>), productos con <code>*</code> o implícitos (<code>3x^2</code>),
        fracciones (<code>x/2</code>) y paréntesis (<code>(x - 1)(x + 2)</code>). Puedes igualarlo
        a cero o escribir dos lados (<code>x^3 = 2x - 1</code>).
      </p>
    </template>

    <template v-else>
      <div class="field degree-field">
        <label for="polynomial-degree">Grado del polinomio</label>
        <select
          id="polynomial-degree"
          :value="state.degree"
          @change="store.setDegree(Number($event.target.value))"
        >
          <option v-for="degree in degrees" :key="degree" :value="degree">{{ degree }}</option>
        </select>
      </div>
      <NumericFieldsInput
        title="Coeficientes, de la potencia más alta a la más baja"
        suffix=""
        :values="state.coefficients"
        :labels="coefficientLabels"
        :error-labels="coefficientErrorLabels"
        @update:values="(values) => (state.coefficients = values)"
      />
    </template>

    <NumericFieldsInput
      title="Valores iniciales (opcional, por defecto −1 y −1)"
      suffix=""
      :values="state.initial"
      :labels="['r₀', 's₀']"
      :error-labels="['Valor inicial r₀', 'Valor inicial s₀']"
      @update:values="(values) => (state.initial = values)"
    />

    <p class="factor-note">
      Factor cuadrático: <MathFormula expression="x^2 - r\,x - s" />
    </p>
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
  color: #ffffff;
  font-weight: var(--weight-semibold);
}

.mode-btn:focus-visible {
  outline: none;
  box-shadow: inset var(--focus-ring);
}

.polynomial-toolbar {
  margin-bottom: var(--space-3);
}

.polynomial-input {
  font-family: 'Consolas', 'Courier New', monospace;
}

/* La vista previa va pegada bajo el campo. */
.equation-preview {
  margin-top: var(--space-2);
}

.degree-field {
  max-width: 220px;
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

.factor-note {
  margin: var(--space-5) 0 0;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-line);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.is-invalid {
  border-color: var(--color-danger);
}

.is-invalid:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px var(--color-danger-bg);
}
</style>
