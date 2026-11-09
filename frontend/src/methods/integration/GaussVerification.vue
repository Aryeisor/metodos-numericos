<script setup>
// Comprobación de la cuadratura gaussiana:
//  - la integral por otro camino (AntiderivativeCheck, igual que los otros métodos)
//    y la comparación G / I / Eₜ / εₜ con su leyenda y la conclusión;
//  - la exactitud de la regla (siempre): los momentos Σ wᵢtᵢᵏ frente a ∫ tᵏ;
//  - la comparación de costo con el trapecio, Simpson y Romberg.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import AntiderivativeCheck from './AntiderivativeCheck.vue'
import { tinyErrorNote } from './explain'
import { cell, percent } from './formulas'
import { MOMENT_COLUMNS, MOMENT_SENTENCE, comparisonColumns, gaussConclusion, visibleMoments } from './gaussExplain'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const integral = computed(() => props.result.integral)
const reference = computed(() => integral.value?.kind === 'reference')
const final = computed(() => (check.value.final.I === null ? null : check.value.final))
const headers = computed(() => comparisonColumns(reference.value))
const conclusion = computed(() => gaussConclusion(props.result, final.value))
const tiny = computed(() => tinyErrorNote(final.value, reference.value))
const moments = computed(() => check.value.moments)
const momentRows = computed(() => visibleMoments(moments.value.rows))
// Diferencias del orden del redondeo (10⁻¹⁶): en notación científica, 0 si no hay.
const difference = (row) => (row.difference === 0 ? '0' : row.difference < 1e-6 ? row.difference.toExponential(1) : formatNumber(row.difference))
const cost = computed(() => props.result.cost)
const costRows = computed(() => {
  const c = cost.value
  if (!c) return []
  const na = 'no aplicable (evalúan los extremos)'
  const more = `más de ${c.limit + 1}`
  const value = (n) => (!c.applicable ? na : n ?? more)
  return [
    { name: 'Cuadratura gaussiana', value: c.gauss_evaluations ?? `no llegó (${c.total_evaluations} en total)`, own: true },
    { name: 'Romberg', value: value(c.romberg_evaluations) },
    { name: 'Simpson 1/3 (duplicando n)', value: value(c.simpson_evaluations) },
    { name: 'Trapecio (duplicando n)', value: value(c.trapezoid_evaluations) },
  ]
})
</script>

<template>
  <section class="verification">
    <h4>Comprobación</h4>
    <p class="section-text intro">
      La comprobación calcula la integral {{ integral.kind === 'exact' ? 'exacta por otro camino (con la antiderivada)' : 'por otro camino' }},
      la compara con el resultado de Gauss, revisa con qué polinomios la regla es exacta y cuánto le habría costado a los
      otros métodos.
    </p>

    <!-- Integral por otro camino y comparación final -->
    <AntiderivativeCheck :result="result" />
    <template v-if="final">
      <p class="section-text">
        Comparación del resultado (G con m = {{ result.iterations.at(-1).extra.m }}) con la
        integral{{ reference ? ' (respecto al valor de referencia)' : '' }}:
      </p>
      <div class="table-scroll">
        <table class="check-table">
          <thead>
            <tr>
              <th v-for="col in headers" :key="col.key">
                <InfoTip :text="col.text">{{ col.label }}</InfoTip>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ cell(final.G) }}</td>
              <td>{{ cell(final.I) }}</td>
              <td>{{ cell(final.true_error) }}</td>
              <td>{{ percent(final.relative_error) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <small v-if="tiny" class="table-note">{{ tiny }}</small>
      <p v-if="conclusion" class="section-text final-line">{{ conclusion }}</p>
      <GlossaryBlock title="¿Qué significa cada columna?" :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))" />
    </template>

    <!-- Exactitud de la regla: momentos -->
    <h5 class="subheading">Exactitud de la regla (m = {{ moments.m }})</h5>
    <p class="section-text">
      Con los nodos y pesos de la última fila se integra cada potencia tᵏ en [−1, 1] y se compara con su valor exacto,
      <MathFormula expression="\int_{-1}^{1} t^{k}\,dt = \tfrac{2}{k + 1}" /> si k es par y 0 si es impar. La primera fila
      (k = 0) dice que los pesos suman 2.
    </p>
    <div class="table-scroll">
      <table class="check-table">
        <thead>
          <tr>
            <th>k</th>
            <th><InfoTip :text="MOMENT_COLUMNS[1].text">Σ wᵢ·tᵢᵏ</InfoTip></th>
            <th><InfoTip :text="MOMENT_COLUMNS[2].text">∫ tᵏ dt</InfoTip></th>
            <th>|diferencia|</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in momentRows" :key="row ? row.k : `gap-${idx}`" :class="{ 'row-break': row && row.k === 2 * moments.m }">
            <template v-if="row">
              <td>{{ row.k }}{{ row.k === 2 * moments.m ? ' (= 2m)' : '' }}</td>
              <td>{{ formatNumber(row.value) }}</td>
              <td>
                <MathFormula :expression="row.exact_latex" />
                <template v-if="row.k % 2 === 0 && row.k > 0"> = {{ formatNumber(row.exact) }}</template>
              </td>
              <td>{{ difference(row) }}</td>
              <td>
                <span :class="row.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ row.ok ? '✔' : '≠' }}</span>
                <small v-if="row.k === 0" class="check-exact">los pesos suman 2</small>
                <small v-if="!row.ok" class="check-exact">ya no coincide</small>
              </td>
            </template>
            <td v-else colspan="5" class="empty-note">…</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="section-text final-line">{{ MOMENT_SENTENCE }}</p>
    <GlossaryBlock title="¿Qué significa cada columna?" :items="MOMENT_COLUMNS" />

    <!-- Comparación de costo -->
    <template v-if="cost">
      <h5 class="subheading">Comparación de costo</h5>
      <p class="section-text">
        Cuántas evaluaciones de f necesita cada método para que |Eₜ| ≤ {{ formatNumber(result.tolerance) }}: Gauss con
        la primera fila que lo cumple (m·N evaluaciones); el trapecio y Simpson 1/3 duplicando n (hasta n = 2²²) y
        Romberg con la primera fila de su diagonal que lo cumple.
      </p>
      <div class="table-scroll">
        <table class="check-table">
          <thead>
            <tr>
              <th>Método</th>
              <th>Evaluaciones de f</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in costRows" :key="r.name" :class="{ own: r.own }">
              <td class="name-cell">{{ r.name }}</td>
              <td>{{ r.value }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="section-text final-line">{{ cost.text }}</p>
      <p class="section-text note">
        El mínimo de 6 filas es un requisito del curso, no del método: Gauss podría detenerse antes.
      </p>
    </template>
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

.subheading {
  margin: var(--space-5) 0 var(--space-2);
  font-size: var(--text-body);
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

.intro {
  color: var(--color-ink);
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

.check-table .name-cell {
  text-align: left;
}

.own td {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.row-break td {
  border-top: 2px solid var(--color-line-strong);
}

.check-exact {
  margin-left: var(--space-2);
  color: var(--color-ink-muted);
}

.empty-note {
  text-align: center !important;
  color: var(--color-ink-muted);
}

.table-note {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.final-line {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}
</style>
