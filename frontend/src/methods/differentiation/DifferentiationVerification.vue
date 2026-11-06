<script setup>
// Comprobación al final del resultado (result.verification, calculada por el
// backend):
//  - modo función: x₀ sustituido en f'(x) término a término (como en Newton
//    y Punto Fijo) y la comparación final aproximación / exacta / error / cota;
//  - modo tabla: la secante común (D⁺ en xᵢ = D⁻ en xᵢ₊₁) y, con función para
//    comparar, los datos contra f, f'(xᵢ) sustituida y error ≤ cota.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import { boundMark, cell, substitutionLatex } from './formulas'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const isTable = computed(() => props.result.mode === 'table')
const formulas = computed(() => props.result.formulas)
const lastRow = computed(() => props.result.iterations.at(-1)?.iteration)

const failedLines = computed(() =>
  formulas.value
    .map((f) => ({ name: f.name, rows: check.value.failed_rows?.[f.key] ?? [] }))
    .filter((line) => line.rows.length)
)

const secantLines = computed(() =>
  check.value.secant.map((pair) => ({
    key: pair.i,
    latex:
      `D^{+}(x_{${pair.i}}) = D^{-}(x_{${pair.i + 1}}) = ${latexNumber(pair.forward)}` +
      (pair.equal ? '' : ` \\ne ${latexNumber(pair.backward)}`),
    ok: pair.equal,
  }))
)

const substitutions = computed(() =>
  isTable.value
    ? (check.value.substitutions ?? []).map((s, i) => ({ key: i, s })).filter((row) => row.s)
    : check.value.substitution
      ? [{ key: 0, s: check.value.substitution }]
      : []
)
</script>

<template>
  <section class="verification">
    <h4>Comprobación</h4>

    <!-- Modo tabla: secante común (siempre) -->
    <template v-if="isTable">
      <p class="section-text">
        La progresiva en <MathFormula expression="x_i" /> y la regresiva en
        <MathFormula expression="x_{i+1}" /> usan la misma recta secante entre los dos puntos, así
        que deben ser iguales:
      </p>
      <div class="check-list">
        <div v-for="line in secantLines" :key="line.key" class="check-line">
          <MathFormula :expression="line.latex" />
          <span :class="line.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ line.ok ? '✔' : '⚠' }}</span>
        </div>
      </div>

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
                <th>yᵢ</th>
                <th>f(xᵢ)</th>
                <th>|yᵢ − f(xᵢ)|</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in check.data" :key="row.i">
                <td>{{ row.i }}</td>
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

    <!-- f'(x) sustituida término a término -->
    <template v-if="substitutions.length">
      <p class="section-text">
        Se sustituye {{ isTable ? 'cada xᵢ' : 'x₀' }} en la derivada exacta
        <MathFormula :expression="`f'(x) = ${result.function.derivative.latex}`" />, término a término:
      </p>
      <p v-if="result.function.uses_trigonometry" class="section-text note">
        Las funciones trigonométricas se evalúan en radianes.
      </p>
      <div class="table-scroll check-list">
        <div v-for="row in substitutions" :key="row.key" class="check-line">
          <MathFormula :expression="substitutionLatex(row.s)" />
        </div>
      </div>
    </template>

    <!-- Comparación final (modo función) -->
    <template v-if="!isTable && result.differentiable && Object.keys(check.final).length">
      <p class="section-text">Comparación de la última fila (k = {{ lastRow }}):</p>
      <div class="table-scroll">
        <table class="check-table">
          <thead>
            <tr>
              <th>Fórmula</th>
              <th>Aproximación</th>
              <th>Exacta f′(x₀)</th>
              <th>Error real</th>
              <th>Cota</th>
              <th>Error real ≤ cota</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in formulas" :key="f.key">
              <td>{{ f.name }}</td>
              <td>{{ cell(check.final[f.key].D) }}</td>
              <td>{{ cell(result.exact) }}</td>
              <td>{{ cell(check.final[f.key].real_error) }}</td>
              <td>{{ check.final[f.key].bound === null ? 'no disponible' : cell(check.final[f.key].bound) }}</td>
              <td>
                <span :class="check.final[f.key].within_bound ? 'mark mark-ok' : 'mark mark-warn'">
                  {{ boundMark(check.final[f.key]) }}
                </span>
                <small v-if="check.final[f.key].by_rounding" class="check-exact">(con el redondeo R)</small>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Línea final -->
    <template v-if="result.function && (isTable || result.differentiable)">
      <p v-if="check.all_within" class="section-text final-line">
        En {{ isTable ? 'todos los puntos' : 'todas las filas' }} el error real quedó por debajo de la
        cota teórica <span class="mark mark-ok">✔</span>
      </p>
      <div v-else-if="failedLines.length" class="alert alert-warning">
        <div v-for="line in failedLines" :key="line.name">
          ⚠ {{ line.name }}: el error real supera la cota en {{ isTable ? 'los puntos' : 'las filas' }}
          {{ line.rows.join(', ') }}.
        </div>
      </div>
    </template>
    <p v-if="!result.function && isTable" class="section-text note">
      Sin función para comparar no hay derivada exacta: sólo se comprueba la secante común.
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

.check-table td:first-child,
.check-table th:first-child {
  text-align: left;
}

.final-line {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}
</style>
