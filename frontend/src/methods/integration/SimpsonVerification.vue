<script setup>
// Comprobación del método de Simpson, con lo mismo que la del trapecio:
//  - la integral por otro camino (AntiderivativeCheck: antiderivada paso a
//    paso, F' = f y F(b) − F(a), o el valor de referencia);
//  - por regla, la comparación S / I / Eₜ / εₜ / cota, su leyenda y la conclusión;
//  - la identidad con el trapecio S_n = (4T_n − T_(n/2))/3 (sólo Simpson 1/3);
//  - en modo tabla, la suma de las partes y los datos contra la función.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import AntiderivativeCheck from './AntiderivativeCheck.vue'
import { tinyErrorNote } from './explain'
import { boundMark, cell, percent } from './formulas'
import { comparisonColumns, simpsonWords } from './glossary'
import { IDENTITY_SENTENCE, NO_IDENTITY_38, identityLatex, partsTotalLatex, simpsonConclusion } from './simpsonExplain'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const isTable = computed(() => props.result.mode === 'table')
const integral = computed(() => props.result.integral)
const reference = computed(() => integral.value?.kind === 'reference')
const referenceLabel = computed(() => (reference.value ? ' (respecto al valor de referencia)' : ''))
const headers = computed(() =>
  comparisonColumns({ reference: reference.value, isTable: isTable.value, words: simpsonWords('simpson13') })
)

// Una entrada por regla (modo función) o por regla aplicada (modo tabla).
const entries = computed(() => {
  if (isTable.value) {
    return props.result.applications.map((app) => ({
      key: app.key,
      name: app.name,
      n: props.result.n,
      final: app.final,
      identities: app.identity ? [{ k: null, identity: app.identity }] : [],
      noIdentity: app.key !== 'simpson13',
      app,
    }))
  }
  return props.result.rules.map((b) => {
    const rows = b.rows.length > 1 ? [b.rows[0], b.rows.at(-1)] : [b.rows[0]]
    const last = b.rows.at(-1)
    return {
      key: b.rule.key,
      name: b.rule.name,
      n: last.n,
      k: last.k,
      final: { ...b.verification.final, I: integral.value?.value },
      identities: b.rule.key === 'simpson13' ? rows.map((row) => ({ k: row.k, identity: row.identity })) : [],
      noIdentity: b.rule.key === 'simpson38',
      verification: b.verification,
    }
  })
})
const hasFinal = (final) => final && final.true_error !== null && final.true_error !== undefined
const tiny = (final) => tinyErrorNote(final, reference.value)
const conclusion = (entry) => simpsonConclusion(props.result, entry.name, entry.n, entry.final)
</script>

<template>
  <section class="verification">
    <h4>Comprobación</h4>

    <p class="section-text intro">
      <template v-if="isTable">
        Con datos, se comprueba la suma de las partes{{ result.function ? ', que cada dato coincide con la función para comparar y cuánto se aleja el resultado de su integral' : '' }}.
      </template>
      <template v-else>
        La comprobación calcula la integral {{ integral.kind === 'exact' ? 'exacta por otro camino (con la antiderivada)' : 'por otro camino' }}
        y la compara con el resultado de Simpson.
      </template>
    </p>

    <!-- Modo tabla: suma de las partes y datos -->
    <template v-if="isTable">
      <template v-for="e in entries" :key="'parts' + e.key">
        <template v-if="e.key === 'combined'">
          <p class="section-text">En la combinación, el resultado es la suma de la parte 1/3 y la parte 3/8:</p>
          <div class="check-line table-scroll">
            <MathFormula :expression="partsTotalLatex(e.app)" />
            <span class="mark mark-ok">✔</span>
          </div>
        </template>
      </template>
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

    <AntiderivativeCheck :result="result" />

    <!-- Comparación final, por regla -->
    <template v-for="e in entries" :key="e.key">
      <template v-if="hasFinal(e.final)">
        <p class="section-text">
          {{ e.name }}: {{ isTable ? 'comparación del resultado con la integral' : `comparación de la última fila (k = ${e.k})` }}{{ referenceLabel }}:
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
                <td>{{ cell(e.final.S) }}</td>
                <td>{{ cell(e.final.I) }}</td>
                <td>{{ cell(e.final.true_error) }}</td>
                <td>{{ percent(e.final.relative_error) }}</td>
                <td>{{ e.final.bound === null ? 'no disponible' : cell(e.final.bound) }}</td>
                <td>
                  <span :class="e.final.within_bound ? 'mark mark-ok' : 'mark mark-warn'">{{ boundMark(e.final) }}</span>
                  <small v-if="e.final.by_rounding" class="check-exact">(con el redondeo R)</small>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <small v-if="tiny(e.final)" class="table-note">{{ tiny(e.final) }}</small>
        <p v-if="conclusion(e)" class="section-text final-line">{{ conclusion(e) }}</p>
        <template v-if="!isTable && integral.value !== null && result.M4">
          <p v-if="e.verification.all_within" class="section-text final-line">
            En todas las filas de {{ e.name }} |Eₜ| quedó por debajo de la cota teórica <span class="mark mark-ok">✔</span>
          </p>
          <div v-else-if="e.verification.failed_rows.length" class="alert alert-warning">
            ⚠ {{ e.name }}: |Eₜ| supera la cota en las filas {{ e.verification.failed_rows.join(', ') }}.
          </div>
        </template>
      </template>
    </template>
    <GlossaryBlock
      v-if="entries.some((e) => hasFinal(e.final))"
      title="¿Qué significa cada columna?"
      :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))"
    />

    <!-- Identidad con el trapecio -->
    <template v-if="entries.some((e) => e.identities.length || e.noIdentity)">
      <h5 class="subheading">Identidad con el trapecio</h5>
      <template v-if="entries.some((e) => e.identities.length)">
        <p class="section-text">{{ IDENTITY_SENTENCE }}</p>
        <div class="formula-box"><MathFormula expression="S_{n} = \frac{4\,T_{n} - T_{n/2}}{3}" display-mode /></div>
        <p class="section-text">
          Se calculan T<sub>n</sub> y T<sub>n/2</sub> con la regla del trapecio
          {{ isTable ? '(con todos los datos y con uno de cada dos)' : '(con los mismos puntos de la fila y con uno de cada dos)' }}
          y se sustituyen; la sustitución usa los valores que se ven y el ✔ se decide con los valores sin redondear.
        </p>
        <template v-for="e in entries" :key="'id' + e.key">
          <div v-for="item in e.identities" :key="e.key + item.k" class="check-line table-scroll">
            <span v-if="item.k" class="row-label">Fila {{ item.k }}:</span>
            <MathFormula
              :expression="`T_{${item.identity.n}} = ${item.identity.T_n_display},\\quad T_{${item.identity.n / 2}} = ${item.identity.T_half_display}`"
            />
            <MathFormula :expression="identityLatex(item.identity)" />
            <span :class="item.identity.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ item.identity.ok ? '✔' : '⚠' }}</span>
          </div>
        </template>
      </template>
      <p v-if="entries.some((e) => e.noIdentity)" class="section-text note">
        {{ NO_IDENTITY_38 }}{{ isTable && entries.some((e) => e.key === 'combined') ? ' En la combinación tampoco aplica: no usa 1/3 en todos los segmentos.' : '' }}
      </p>
    </template>

    <p v-if="isTable && !result.function" class="section-text note">
      Sin función para comparar no hay integral exacta: sólo se comprueba el cálculo con los datos.
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

.formula-box {
  overflow-x: auto;
  margin-bottom: var(--space-3);
}

.check-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.row-label {
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
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
