<script setup>
// Detalle expandible de una iteración de Newton, en el mismo orden en que se
// resuelve a mano en clase: Jacobiana simbólica → F y J evaluados → sistema
// lineal J·Δx = −F → D → D_i por variable (regla de Cramer) → Δx_i = D_i / D →
// actualización x^(k+1) = x^(k) + Δx → error.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import {
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  columnDeterminantLatex,
  determinantLatex,
  errorLatex,
  evaluationLatex,
  generalStepLatex,
  incrementLatex,
  linearSystemLatex,
  symbolicSystemLatex,
  updateLatex,
} from './newtonFormulas'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  index: { type: Number, required: true },
  methodName: { type: String, required: true },
})

const row = computed(() => props.result.iterations[props.index])
const k = computed(() => row.value.iteration - 1) // punto en el que se evalúa
const variables = computed(() => props.result.variables.map((_, j) => j))
const evaluation = computed(() => evaluationLatex(row.value))

// Hasta dónde llegó el cálculo (si el método se detuvo en esta iteración).
const hasValues = computed(() => Boolean(row.value.extra.F && row.value.extra.J))
const hasDeterminant = computed(() => row.value.extra.D !== undefined && row.value.extra.D !== null)
const solved = computed(() => Boolean(row.value.extra.D_i))
const finished = computed(() => row.value.error !== null)
const singular = computed(() => props.result.failure?.reason === 'singular' && !solved.value)
</script>

<template>
  <div class="detail">
    <div class="detail-block">
      <span class="detail-caption">1. Sistema y matriz Jacobiana ({{ methodName }})</span>
      <div class="formula-box">
        <MathFormula :expression="symbolicSystemLatex(result)" display-mode />
      </div>
      <div class="formula-box general-step">
        <MathFormula :expression="generalStepLatex()" display-mode />
      </div>
    </div>

    <div class="detail-block">
      <span class="detail-caption">2. Evaluación en el punto actual</span>
      <div class="step-card">
        <MathFormula :expression="evaluation.point" display-mode />
      </div>
      <div v-if="hasValues" class="step-grid">
        <div class="step-card"><MathFormula :expression="evaluation.F" display-mode /></div>
        <div class="step-card"><MathFormula :expression="evaluation.J" display-mode /></div>
      </div>
      <div v-else class="alert alert-danger failure-note">
        F o la Jacobiana no dan números reales finitos en <MathFormula :expression="`x^{(${k})}`" />
        (raíz de un negativo, logaritmo de cero, desbordamiento...). El método se detuvo aquí.
      </div>
    </div>

    <template v-if="hasValues">
      <div class="detail-block">
        <span class="detail-caption">3. Sistema lineal planteado</span>
        <div class="step-card">
          <MathFormula :expression="linearSystemLatex(result, row)" display-mode />
        </div>
      </div>

      <div v-if="hasDeterminant" class="detail-block">
        <span class="detail-caption">4. Determinante de la Jacobiana</span>
        <div class="step-card">
          <MathFormula :expression="determinantLatex(row)" display-mode />
        </div>
        <div v-if="singular" class="alert alert-danger failure-note">
          El determinante es (prácticamente) cero: la Jacobiana es singular y el sistema no
          tiene solución única. No se puede continuar desde este punto.
        </div>
      </div>
    </template>

    <template v-if="solved">
      <div class="detail-block">
        <span class="detail-caption">5. Determinantes por variable (regla de Cramer)</span>
        <p class="detail-hint">
          <span class="legend-current">■</span> columna reemplazada por
          <MathFormula expression="-F" />
        </p>
        <div class="step-grid">
          <div v-for="j in variables" :key="j" class="step-card">
            <MathFormula :expression="columnDeterminantLatex(result, row, j)" display-mode />
          </div>
        </div>
      </div>

      <div class="detail-block">
        <span class="detail-caption">6. Incrementos</span>
        <div class="step-grid">
          <div v-for="j in variables" :key="j" class="step-card">
            <MathFormula :expression="incrementLatex(result, row, j)" display-mode />
          </div>
        </div>
      </div>
    </template>

    <template v-if="finished">
      <div class="detail-block">
        <span class="detail-caption">7. Actualización</span>
        <p class="detail-hint">
          <span class="legend-prev">■</span> valores de la iteración anterior
        </p>
        <div class="step-grid">
          <div v-for="j in variables" :key="j" class="step-card">
            <MathFormula :expression="updateLatex(result, row, j)" display-mode />
          </div>
        </div>
      </div>

      <div class="detail-block">
        <span class="detail-caption">8. Error de la iteración</span>
        <div class="step-card">
          <MathFormula :expression="errorLatex(result, row)" display-mode />
        </div>
      </div>
    </template>
    <div v-else-if="solved" class="alert alert-danger failure-note">
      El paso Δx o el nuevo punto no son números reales finitos. El método se detuvo aquí.
    </div>
  </div>
</template>

<style scoped>
/* Mismo aspecto que el detalle de Jacobi, Gauss-Seidel y Punto Fijo. */
.detail-caption {
  font-weight: var(--weight-semibold);
  font-size: var(--text-small);
  color: var(--color-ink);
  display: block;
  margin-bottom: var(--space-2);
}

.detail-block {
  margin-bottom: var(--space-5);
}

.detail-block:last-child {
  margin-bottom: 0;
}

.detail-hint {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.legend-prev {
  color: v-bind(PREVIOUS_COLOR);
}

.legend-current {
  color: v-bind(CURRENT_COLOR);
}

.general-step {
  margin-top: var(--space-2);
}

/* Una tarjeta por variable; dos columnas cuando caben. */
.step-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.step-card {
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
}

.step-card + .step-grid {
  margin-top: var(--space-3);
}

.failure-note {
  margin: var(--space-2) 0 0;
}

.formula-box,
.step-card {
  min-width: 0;
}

.step-card :deep(.katex),
.formula-box :deep(.katex) {
  font-size: 1em;
}

.formula-box {
  overflow-x: auto;
}
</style>
