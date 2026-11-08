<script setup>
// Paso a paso de una fila de la tabla de refinamiento (modo función):
//  - fila 1: h, puntos xᵢ con f(xᵢ) y su peso, sustitución en la fórmula compuesta;
//  - filas siguientes: h_k, puntos nuevos (en verde), T_(k−1) (en azul) y la recurrencia;
//  - después: error estimado, Eₜ, εₜ, Eₐ con f̄'', la cota con M₂ y la razón.
// Todos los valores vienen del backend; aquí sólo se escriben.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import {
  approxErrorLatex,
  boundLatex,
  criterionLatex,
  estimatedErrorLatex,
  firstRowLatex,
  interiorSumLatex,
  meanSecondLatex,
  newSumLatex,
  pointLatex,
  ratioLatex,
  recurrenceLatex,
  relativeErrorLatex,
  stepSizeLatex,
  trueErrorLatex,
} from './formulas'

const props = defineProps({
  result: { type: Object, required: true },
  row: { type: Object, required: true },
  k: { type: Number, required: true },
  previous: { type: Object, default: null },
})

const step = computed(() => props.row.step)
const isFirst = computed(() => step.value.kind === 'formula')
const I = computed(() => props.result.integral.value)
// Con muchos puntos sólo llegan los 8 primeros y los 8 últimos: «…» entre ellos.
const folded = computed(() => step.value.count > step.value.points.length)
const rowsShown = computed(() => {
  const points = step.value.points
  if (!folded.value) return points
  return [...points.slice(0, 8), null, ...points.slice(8)]
})
const interior = computed(() => (isFirst.value ? interiorSumLatex(props.row) : null))
const criterion = computed(() => criterionLatex(props.row))
const M2 = computed(() => props.result.M2)
</script>

<template>
  <ol class="steps">
    <li>
      <span class="step-name">Paso</span>
      <MathFormula :expression="stepSizeLatex(result, row, k)" />
    </li>
    <li>
      <span class="step-name">
        {{ isFirst ? 'Puntos xᵢ = a + i·h y evaluaciones' : 'Puntos nuevos x = a + (2j − 1)·h y evaluaciones' }}
      </span>
      <div class="table-scroll">
        <table class="eval-table">
          <thead>
            <tr>
              <th>i</th>
              <th>xᵢ</th>
              <th>f(xᵢ)</th>
              <th v-if="isFirst">Peso</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(p, idx) in rowsShown" :key="p ? p.i : `gap-${idx}`">
              <template v-if="p">
                <td>{{ p.i }}</td>
                <td><MathFormula :expression="pointLatex(p.x_display)" /></td>
                <td :class="{ 'value-new': !isFirst }">{{ p.f_display }}</td>
                <td v-if="isFirst">{{ p.weight }}</td>
              </template>
              <td v-else :colspan="isFirst ? 4 : 3" class="gap-cell">
                … ({{ step.count - step.points.length }} puntos más)
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <small class="step-note">
        Con {{ step.decimals }} decimales, para que el resultado sea coherente con los valores que se ven.
        <template v-if="!isFirst">Los puntos de la fila anterior ya están en T<sub>{{ k - 1 }}</sub>: sólo se evalúan los nuevos.</template>
      </small>
    </li>
    <li>
      <span class="step-name">{{ isFirst ? 'Fórmula' : 'Recurrencia' }}</span>
      <div v-if="interior" class="step-formula"><MathFormula :expression="interior" /></div>
      <div v-if="!isFirst" class="step-formula"><MathFormula :expression="newSumLatex(row)" /></div>
      <div class="step-formula">
        <MathFormula :expression="isFirst ? firstRowLatex(row) : recurrenceLatex(row, k)" />
      </div>
    </li>
    <li v-if="row.estimated_error !== null">
      <span class="step-name">Error estimado</span>
      <div class="step-formula"><MathFormula :expression="estimatedErrorLatex(row, k)" /></div>
    </li>
    <li v-if="row.true_error !== null">
      <span class="step-name">
        Error verdadero<template v-if="result.integral.kind === 'reference'"> (respecto al valor de referencia)</template>
      </span>
      <div class="step-formula"><MathFormula :expression="trueErrorLatex(row, I, k)" /></div>
      <div v-if="row.relative_error !== null" class="step-formula">
        <MathFormula :expression="relativeErrorLatex(row, I)" />
      </div>
      <small v-else class="step-note">|I| ≈ 0: el error relativo no se calcula.</small>
    </li>
    <li v-if="row.approx_error !== null">
      <span class="step-name">Error aproximado (Chapra)</span>
      <div class="step-formula"><MathFormula :expression="meanSecondLatex(result)" /></div>
      <div class="step-formula"><MathFormula :expression="approxErrorLatex(result, row)" /></div>
    </li>
    <li v-if="row.bound !== null">
      <span class="step-name">Cota</span>
      <div class="step-formula"><MathFormula :expression="boundLatex(result, row)" /></div>
      <small class="step-note">
        <MathFormula expression="M_2 = \max_{x \in [a,\, b]} |f''(x)|" /> ≈ {{ formatNumber(M2.value) }}, alcanzado en
        x ≈ {{ M2.x_display.exact ? M2.x_display.text : formatNumber(M2.x) }} (estimado por muestreo con
        {{ result.sampling_points }} puntos).
      </small>
      <div v-if="criterion" class="step-formula criterion">
        <span>|Eₜ| ≤ cota:</span>
        <MathFormula :expression="criterion" />
        <span v-if="row.within_bound" class="mark mark-ok" aria-label="cumple">✔</span>
        <span v-else class="mark mark-warn" aria-label="no cumple">⚠</span>
      </div>
      <small v-if="row.by_rounding" class="step-note">
        |Eₜ| supera la cota sólo por el redondeo de la computadora, R = 2ε·Σ|wᵢ·f(xᵢ)|·h/2.
      </small>
    </li>
    <li v-if="row.ratio !== null && previous">
      <span class="step-name">Razón</span>
      <div class="step-formula"><MathFormula :expression="ratioLatex(row, previous, k)" /></div>
    </li>
  </ol>
</template>

<style scoped>
.steps {
  margin: 0;
  padding-left: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.step-name {
  display: block;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  margin-bottom: var(--space-1);
}

.step-formula {
  overflow-x: auto;
}

.step-note {
  display: block;
  margin-top: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.criterion {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: var(--text-small);
}

.eval-table {
  width: auto;
  min-width: min(100%, 280px);
}

.eval-table th,
.eval-table td {
  padding: var(--space-1) var(--space-3);
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.value-new {
  color: var(--color-value-new);
}

.gap-cell {
  text-align: center !important;
  color: var(--color-ink-muted);
}
</style>
