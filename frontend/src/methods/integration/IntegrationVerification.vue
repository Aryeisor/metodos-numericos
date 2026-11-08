<script setup>
// Comprobación al final del resultado (result.verification, calculada por el
// backend):
//  - modo función con valor exacto: F(x), F(b) − F(a) término a término (como
//    en Newton y diferenciación) y la comparación final T / I / Eₜ / εₜ / cota;
//  - con valor de referencia: la comparación con la referencia;
//  - modo tabla: la suma de las áreas es el total, la fórmula compuesta (si el
//    espaciado es uniforme) y, con función para comparar, los datos y la integral.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import { substitutionLatex } from '../differentiation/formulas'
import { areasSumLatex, boundMark, cell, compositeLatex, percent } from './formulas'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const isTable = computed(() => props.result.mode === 'table')
const integral = computed(() => props.result.integral)
const final = computed(() => (isTable.value ? check.value.final : { ...check.value.final, I: integral.value?.value }))
const lastRow = computed(() => props.result.iterations.at(-1)?.iteration)
const hasExact = computed(() => integral.value?.kind === 'exact' && check.value.upper)
const aLatex = computed(() => props.result.a_display.latex)
const bLatex = computed(() => props.result.b_display.latex)
const lowerLatex = computed(() =>
  check.value.lower.all_zero
    ? `F(${aLatex.value}) = 0`
    : substitutionLatex(check.value.lower, 'F')
)
const differenceLatex = computed(() => {
  const up = latexNumber(check.value.upper.value)
  const low = latexNumber(check.value.lower.value)
  return (
    `I = F(${bLatex.value}) - F(${aLatex.value}) = ${up} - ${low.startsWith('-') ? `\\left(${low}\\right)` : low}` +
    ` = ${latexNumber(integral.value.value)}`
  )
})
const referenceLabel = computed(() => (integral.value?.kind === 'reference' ? ' (respecto al valor de referencia)' : ''))
const reason = computed(() => {
  const i = integral.value
  if (i.special) return `${i.special}.`
  if (i.timed_out) return 'La integración simbólica superó el límite de tiempo.'
  return 'sympy no encontró una antiderivada utilizable en [a, b].'
})
</script>

<template>
  <section class="verification">
    <h4>Comprobación</h4>

    <!-- Modo tabla: suma de las áreas y fórmula compuesta -->
    <template v-if="isTable">
      <p class="section-text">La suma de las áreas de los trapecios individuales es el total:</p>
      <div class="check-line table-scroll">
        <MathFormula :expression="areasSumLatex(check)" />
        <span class="mark mark-ok">✔</span>
      </div>
      <p v-if="check.areas_sum !== check.total_display" class="section-text note">
        Las áreas se muestran a 6 decimales; el total sale de las áreas sin redondear.
      </p>
      <template v-if="result.composite">
        <p class="section-text">
          El espaciado es uniforme (h = {{ result.composite.h.text }}): la fórmula compuesta da lo mismo que la suma.
        </p>
        <div class="check-line table-scroll">
          <MathFormula :expression="compositeLatex(result)" />
          <span :class="result.composite.equal ? 'mark mark-ok' : 'mark mark-warn'">
            {{ result.composite.equal ? '✔' : '⚠' }}
          </span>
        </div>
      </template>
      <p v-else class="section-text">Espaciado no uniforme: cada trapecio usa su propio ancho.</p>

      <template v-if="check.data">
        <p class="section-text">
          Cada dato contra la función para comparar: debe cumplir
          <MathFormula expression="|y_i - f(x_i)| \le 10^{-6} \cdot \max(1, |f(x_i)|)" />.
        </p>
        <div class="table-scroll">
          <table class="check-table">
            <thead>
              <tr>
                <th>i</th>
                <th>xᵢ</th>
                <th>yᵢ</th>
                <th>f(xᵢ)</th>
                <th>|yᵢ − f(xᵢ)|</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in check.data" :key="row.i">
                <td>{{ row.i }}</td>
                <td>{{ row.x_display.exact ? row.x_display.text : row.x_display.approx }}</td>
                <td>{{ formatNumber(row.y) }}</td>
                <td>{{ cell(row.f) }}</td>
                <td>{{ cell(row.difference) }}</td>
                <td>
                  <span :class="row.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ row.ok ? '✔' : '⚠' }}</span>
                  <small v-if="!row.ok" class="check-exact">el dato no coincide con la función</small>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>

    <!-- Integral exacta: F(b) − F(a) término a término -->
    <template v-if="hasExact">
      <p class="section-text">
        Antiderivada de f{{ isTable ? ' (la función para comparar)' : '' }}:
      </p>
      <div class="formula-box"><MathFormula :expression="`F(x) = ${integral.antiderivative.latex}`" display-mode /></div>
      <p class="section-text">Se evalúa F en los límites, término a término:</p>
      <div class="check-list table-scroll">
        <div class="check-line"><MathFormula :expression="substitutionLatex(check.upper, 'F')" /></div>
        <div class="check-line">
          <MathFormula :expression="lowerLatex" />
          <span v-if="check.lower.all_zero" class="zero-note">(todos sus términos se anulan)</span>
        </div>
        <div class="check-line"><MathFormula :expression="differenceLatex" /></div>
      </div>
      <p v-if="result.function?.uses_trigonometry" class="section-text note">
        Las funciones trigonométricas se evalúan en radianes.
      </p>
    </template>
    <p v-else-if="integral && integral.kind === 'reference'" class="section-text">
      No hay una antiderivada elemental: {{ reason }} Se compara con el {{ integral.label }},
      I ≈ {{ formatNumber(integral.value) }}.
    </p>
    <p v-else-if="integral" class="section-text note">
      No se pudo calcular la integral exacta ni un valor de referencia: no hay con qué comparar.
    </p>

    <!-- Comparación final -->
    <template v-if="final && final.true_error !== null && final.true_error !== undefined">
      <p class="section-text">
        {{ isTable ? 'Comparación del total con la integral' : `Comparación de la última fila (k = ${lastRow})` }}{{ referenceLabel }}:
      </p>
      <div class="table-scroll">
        <table class="check-table">
          <thead>
            <tr>
              <th>T</th>
              <th>I</th>
              <th>Eₜ = I − T</th>
              <th>εₜ</th>
              <th>Cota</th>
              <th>|Eₜ| ≤ cota</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ cell(final.T) }}</td>
              <td>{{ cell(final.I) }}</td>
              <td>{{ cell(final.true_error) }}</td>
              <td>{{ percent(final.relative_error) }}</td>
              <td>{{ final.bound === null ? 'no disponible' : cell(final.bound) }}</td>
              <td>
                <span :class="final.within_bound ? 'mark mark-ok' : 'mark mark-warn'">{{ boundMark(final) }}</span>
                <small v-if="final.by_rounding" class="check-exact">(con el redondeo R)</small>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Línea final (modo función) -->
    <template v-if="!isTable && integral.value !== null && result.M2">
      <p v-if="check.all_within" class="section-text final-line">
        En todas las filas |Eₜ| quedó por debajo de la cota teórica <span class="mark mark-ok">✔</span>
      </p>
      <div v-else-if="check.failed_rows.length" class="alert alert-warning">
        ⚠ |Eₜ| supera la cota en las filas {{ check.failed_rows.join(', ') }}.
      </div>
    </template>
    <p v-if="isTable && !result.function" class="section-text note">
      Sin función para comparar no hay integral exacta: sólo se comprueba la suma de las áreas.
    </p>
  </section>
</template>

<style scoped>
.verification {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
}

.verification h4 {
  margin: 0 0 var(--space-3);
  font-size: var(--text-subsection);
  color: var(--color-ink);
}

.section-text {
  margin: var(--space-3) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.note {
  font-style: italic;
}

.formula-box {
  overflow-x: auto;
  margin-bottom: var(--space-3);
}

.check-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.check-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
}

.check-table {
  width: auto;
  min-width: min(100%, 360px);
}

.check-table th,
.check-table td {
  padding: var(--space-2) var(--space-3);
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.check-exact {
  margin-left: var(--space-2);
  color: var(--color-ink-muted);
}

.zero-note {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.final-line {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}
</style>
