<script setup>
// Comprobación de Romberg:
//  - la integral por otro camino (AntiderivativeCheck, igual que el trapecio)
//    y la comparación R / I / Eₜ / εₜ con su leyenda y la conclusión;
//  - las identidades (siempre): columna 1 = trapecio directo, columna 2 = Simpson 1/3;
//  - la comparación de costo con el trapecio y Simpson (con exacta o referencia);
//  - en modo tabla, los datos contra la función para comparar.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import AntiderivativeCheck from './AntiderivativeCheck.vue'
import { tinyErrorNote } from './explain'
import { cell, percent } from './formulas'
import { COST_NOTE, IDENTITY_SENTENCE, rombergConclusion } from './rombergExplain'
import { IDENTITY_COLUMNS, rombergComparisonColumns } from './rombergGlossary'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const isTable = computed(() => props.result.mode === 'table')
const integral = computed(() => props.result.integral)
const reference = computed(() => integral.value?.kind === 'reference')
const final = computed(() => check.value.final)
const headers = computed(() => rombergComparisonColumns(reference.value))
const conclusion = computed(() => rombergConclusion(props.result, final.value))
const tiny = computed(() => tinyErrorNote(final.value, reference.value))
const identities = computed(() => check.value.identities)
const allOk = computed(() => identities.value.every((r) => r.trapezoid.ok && (!r.simpson || r.simpson.ok)))
const mark = (item) => (item.ok ? '✔' : '⚠')
// Diferencias del orden del redondeo (10⁻¹⁶): en notación científica, 0 si no hay.
const difference = (item) => (item.difference === 0 ? '0' : item.difference.toExponential(1))
</script>

<template>
  <section class="verification">
    <h4>Comprobación</h4>
    <p class="section-text intro">
      <template v-if="isTable">
        Con datos se comprueban las identidades de las columnas 1 y 2{{ result.function ? ', que cada dato coincide con la función para comparar y cuánto se aleja el resultado de su integral' : '' }}.
      </template>
      <template v-else>
        La comprobación calcula la integral {{ integral.kind === 'exact' ? 'exacta por otro camino (con la antiderivada)' : 'por otro camino' }},
        la compara con el mejor valor de Romberg y revisa que las columnas 1 y 2 sean el trapecio y Simpson.
      </template>
    </p>

    <!-- Modo tabla: datos contra la función -->
    <template v-if="isTable && check.data">
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

    <!-- Integral por otro camino y comparación final -->
    <AntiderivativeCheck :result="result" />
    <template v-if="final">
      <p class="section-text">
        Comparación del mejor valor (R{{ result.iterations.length }},{{ result.iterations.length }}) con la
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
              <td>{{ cell(final.R) }}</td>
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

    <!-- Identidades -->
    <h5 class="subheading">Identidades: columna 1 = trapecio, columna 2 = Simpson 1/3</h5>
    <p class="section-text">
      Cada valor de las dos primeras columnas se calcula otra vez por separado, con n = 2<sup>i−1</sup> segmentos:
      <MathFormula expression="R_{i,1} = T(n)" /> con la fórmula de pesos del trapecio y
      <MathFormula expression="R_{i,2} = S(n)" /> con el motor de Simpson 1/3.
    </p>
    <div class="table-scroll">
      <table class="check-table">
        <thead>
          <tr>
            <th>i</th>
            <th>n</th>
            <th>Rᵢ,₁</th>
            <th>T(n)</th>
            <th>|diferencia|</th>
            <th></th>
            <th>Rᵢ,₂</th>
            <th>S(n)</th>
            <th>|diferencia|</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in identities" :key="row.i">
            <td>{{ row.i }}</td>
            <td>{{ row.n }}</td>
            <td>{{ cell(row.trapezoid.value) }}</td>
            <td>{{ cell(row.trapezoid.other) }}</td>
            <td>{{ difference(row.trapezoid) }}</td>
            <td><span :class="row.trapezoid.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ mark(row.trapezoid) }}</span></td>
            <template v-if="row.simpson">
              <td>{{ cell(row.simpson.value) }}</td>
              <td>{{ cell(row.simpson.other) }}</td>
              <td>{{ difference(row.simpson) }}</td>
              <td><span :class="row.simpson.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ mark(row.simpson) }}</span></td>
            </template>
            <td v-else colspan="4" class="empty-note">Simpson necesita n ≥ 2</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="section-text final-line">
      {{ IDENTITY_SENTENCE }}
      <span v-if="allOk" class="mark mark-ok">✔</span>
    </p>
    <GlossaryBlock title="¿Qué significa cada columna?" :items="IDENTITY_COLUMNS" />

    <!-- Comparación de costo -->
    <template v-if="result.cost">
      <h5 class="subheading">Comparación de costo</h5>
      <p class="section-text">
        Cuántas evaluaciones de f necesita cada método para que |Eₜ| ≤ {{ formatNumber(result.tolerance) }}: el
        trapecio y Simpson 1/3 duplican n desde 1 y desde 2 (hasta n = 2²²).
      </p>
      <p class="section-text final-line">{{ result.cost.text }}</p>
      <p class="section-text note">{{ COST_NOTE }}</p>
    </template>

    <p v-if="isTable && !result.function" class="section-text note">
      Sin función para comparar no hay integral exacta: sólo se comprueban las identidades con los datos.
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
