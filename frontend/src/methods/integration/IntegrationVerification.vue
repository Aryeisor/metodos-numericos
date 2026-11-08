<script setup>
// Comprobación al final del resultado (result.verification, calculada por el
// backend):
//  - modo función con valor exacto: F(x), F(b) − F(a) término a término (como
//    en Newton y diferenciación) y la comparación final T / I / Eₜ / εₜ / cota;
//  - con valor de referencia: la comparación con la referencia;
//  - modo tabla: la suma de las áreas es el total, la fórmula compuesta (si el
//    espaciado es uniforme) y, con función para comparar, los datos y la integral.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import AntiderivativeCheck from './AntiderivativeCheck.vue'
import { conclusionText, tinyErrorNote } from './explain'
import { areasSumLatex, boundMark, cell, compositeLatex, percent } from './formulas'
import { comparisonColumns } from './glossary'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const isTable = computed(() => props.result.mode === 'table')
const integral = computed(() => props.result.integral)
const final = computed(() => (isTable.value ? check.value.final : { ...check.value.final, I: integral.value?.value }))
const lastRow = computed(() => props.result.iterations.at(-1)?.iteration)
const hasExact = computed(() => integral.value?.kind === 'exact' && check.value.upper)
const referenceLabel = computed(() => (integral.value?.kind === 'reference' ? ' (respecto al valor de referencia)' : ''))
const reference = computed(() => integral.value?.kind === 'reference')
const headers = computed(() => comparisonColumns({ reference: reference.value, isTable: isTable.value }))
const tiny = computed(() => tinyErrorNote(final.value, reference.value))
const conclusion = computed(() => conclusionText(props.result, final.value))
</script>

<template>
  <section class="verification">
    <h4>Comprobación</h4>

    <p v-if="!isTable" class="section-text intro">
      La comprobación calcula la integral {{ hasExact ? 'exacta por otro camino (con la antiderivada)' : 'por otro camino' }}
      y la compara con el resultado del trapecio.
    </p>

    <!-- Modo tabla: suma de las áreas y fórmula compuesta -->
    <template v-if="isTable">
      <p class="section-text intro">
        Con datos, el área total es la suma de las áreas de los trapecios de cada segmento. Se comprueba que esa suma
        da el total{{ result.function ? ', que cada dato coincide con la función para comparar y cuánto se aleja el total de su integral' : '' }}.
      </p>
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

    <!-- Integral por otro camino (antiderivada o referencia) -->
    <AntiderivativeCheck :result="result" />

    <!-- Comparación final -->
    <template v-if="final && final.true_error !== null && final.true_error !== undefined">
      <p class="section-text">
        {{ isTable ? 'Comparación del total con la integral' : `Comparación de la última fila (k = ${lastRow})` }}{{ referenceLabel }}:
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
      <small v-if="tiny" class="table-note">{{ tiny }}</small>
      <GlossaryBlock
        title="¿Qué significa cada columna?"
        :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))"
      />
      <p v-if="conclusion" class="section-text final-line">{{ conclusion }}</p>
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


.intro {
  color: var(--color-ink);
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
