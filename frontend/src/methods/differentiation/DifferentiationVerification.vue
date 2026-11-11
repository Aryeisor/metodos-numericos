<script setup>
// Comprobación al final del resultado (result.verification, calculada por el
// backend):
//  - modo función: x₀ sustituido en f'(x) término a término (como en Newton
//    y Punto Fijo) y la comparación final aproximación / exacta / error / cota;
//  - modo tabla: la secante común (D⁺ en xᵢ = D⁻ en xᵢ₊₁) y, con función para
//    comparar, los datos contra f, f'(xᵢ) sustituida y error ≤ cota;
//  - fórmula de 3 puntos: en lugar de la secante, las identidades punto medio
//    = (D⁺ + D⁻)/2 y extremo = 2·D(h) − D(2h) (fila 1 o cada punto).
// Con `explained` (diferencias progresiva y regresiva): introducción, tooltips
// y leyenda de la tabla de comparación, frase de conclusión y nota del error
// que se ve 0.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import { conclusionText, tinyRealErrorNote } from './differenceExplain'
import { comparisonColumns } from './differenceGlossary'
import { boundMark, cell, identityLatex, substitutionLatex } from './formulas'
import { ENDPOINTS_NOTE, IDENTITY_TEXTS, RICHARDSON_ROUNDING_NOTE, RICHARDSON_TEXT } from './threePointExplain'

const props = defineProps({
  result: { type: Object, required: true },
  explained: { type: Boolean, default: false },
})

const check = computed(() => props.result.verification)
const COMPARISON_COLUMNS = computed(() => comparisonColumns(props.result.method !== 'diferencias-finitas'))
// Identidades explicadas (3 puntos): una frase por cada tipo que aparece.
const identityTexts = computed(() => {
  if (!props.explained || !check.value.identities) return []
  const groups = isTable.value ? check.value.identities : [{ items: check.value.identities }]
  const kinds = new Set(groups.flatMap((g) => g.items.map((item) => item.kind)))
  return ['average', 'richardson'].filter((k) => kinds.has(k)).map((k) => IDENTITY_TEXTS[k])
})
const isTable = computed(() => props.result.mode === 'table')
const formulas = computed(() => props.result.formulas)
const lastRow = computed(() => props.result.iterations.at(-1)?.iteration)

const failedLines = computed(() =>
  formulas.value
    .map((f) => ({ name: f.name, rows: check.value.failed_rows?.[f.key] ?? [] }))
    .filter((line) => line.rows.length)
)

// Identidades (fórmula de 3 puntos): en modo función, una lista; en modo
// tabla, una por punto con las fórmulas que aplican allí.
const identityGroups = computed(() => {
  const ids = check.value.identities
  if (!ids) return []
  const groups = isTable.value ? ids : [{ i: null, items: ids }]
  return groups
    .filter((group) => group.items.length)
    .map((group) => ({
      key: group.i ?? 0,
      label: group.i === null ? null : `x_{${group.i}} = ${group.x_display.latex}`,
      lines: group.items.map((item) => ({
        key: item.key,
        latex: identityLatex(item, formulas.value.find((f) => f.key === item.key)),
        ok: item.ok,
        name: item.name,
        rounding: Boolean(item.rounding_difference),
      })),
    }))
})

// Fórmula de 5 puntos: identidad de Richardson del punto medio.
const isFivePoint = computed(() => props.result.method === 'cinco-puntos')
const rombergFormula = computed(
  () =>
    'D_{5}(h) = \\frac{4D_{3}(h) - D_{3}(2h)}{3},\\quad ' +
    (isTable.value
      ? 'D_{3}(h) = \\frac{y_{i+1} - y_{i-1}}{2h},\\quad D_{3}(2h) = \\frac{y_{i+2} - y_{i-2}}{4h}'
      : 'D_{3}(h) = \\frac{f(x_0 + h) - f(x_0 - h)}{2h}')
)
// Alguna línea con «(diferencia por redondeo)»: se explica debajo.
const roundingCase = computed(() => identityGroups.value.some((g) => g.lines.some((l) => l.rounding)))

const secantLines = computed(() =>
  (check.value.secant ?? []).map((pair) => ({
    key: pair.i,
    latex:
      `D^{+}(x_{${pair.i}}) = D^{-}(x_{${pair.i + 1}}) = ${latexNumber(pair.forward)}` +
      (pair.equal ? '' : ` \\ne ${latexNumber(pair.backward)}`),
    ok: pair.equal,
  }))
)

const conclusions = computed(() =>
  props.explained ? formulas.value.map((f) => conclusionText(props.result, f)).filter(Boolean) : []
)
const tinyNotes = computed(() =>
  props.explained
    ? formulas.value
        .map((f) => ({ name: f.name, text: tinyRealErrorNote(check.value.final?.[f.key]) }))
        .filter((n) => n.text)
    : []
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
    <p v-if="explained && !isTable && result.differentiable" class="section-text intro">
      La comprobación calcula la derivada exacta en x₀ por otro camino (sustituyendo en f′(x)) y la compara con la
      aproximación.
    </p>

    <!-- Fórmulas de 3 y 5 puntos: identidades -->
    <template v-if="identityGroups.length">
      <template v-if="isFivePoint && explained">
        <p class="section-text">
          Identidad de Richardson
          ({{ isTable ? 'en cada punto donde aplica el punto medio de 5 puntos, con los datos' : 'en la fila 1' }}):
          {{ RICHARDSON_TEXT }}
        </p>
        <div class="formula-box"><MathFormula :expression="rombergFormula" /></div>
      </template>
      <p v-else-if="isFivePoint" class="section-text">
        {{ isTable ? 'En cada punto donde aplica el punto medio de 5 puntos, con los datos' : 'En la fila 1' }}:
        el punto medio de 5 puntos combina dos fórmulas de 3 puntos para eliminar su error de orden
        <MathFormula expression="h^2" />, igual que la de 3 puntos combina diferencias (es la idea de Romberg):
        <MathFormula :expression="rombergFormula" />. El ✔ se decide con los valores sin redondear; la
        sustitución se muestra con los valores que se ven.
      </p>
      <template v-else-if="identityTexts.length">
        <p class="section-text">
          Las identidades comprueban el resultado por otro camino, con las diferencias progresiva
          <MathFormula expression="D^{+}" /> y regresiva <MathFormula expression="D^{-}" />
          ({{ isTable ? 'en cada punto, con los datos' : 'en la fila 1, con los valores sin redondear' }}):
        </p>
        <ul class="identity-texts">
          <li v-for="t in identityTexts" :key="t">{{ t }}</li>
        </ul>
        <p class="section-text">
          Cada línea sustituye los valores y marca ✔ si da la misma aproximación de la tabla
          (<MathFormula expression="D(2h)" /> usa el punto a distancia 2h).
        </p>
      </template>
      <p v-else class="section-text">
        {{ isTable ? 'En cada punto, con los datos' : 'En la fila 1, con los valores sin redondear' }}:
        el punto medio es el promedio de la progresiva y la regresiva,
        <MathFormula expression="\frac{D^{+}(h) + D^{-}(h)}{2}" />, y cada extremo es una extrapolación de
        Richardson de la diferencia de su lado, <MathFormula expression="2D(h) - D(2h)" />, que cancela el
        término de orden h del error.
      </p>
      <div class="check-list">
        <div v-for="group in identityGroups" :key="group.key" class="identity-group">
          <MathFormula v-if="group.label" :expression="group.label" class="identity-point" />
          <div v-for="line in group.lines" :key="line.key" class="check-line">
            <span class="identity-name">{{ line.name }}:</span>
            <MathFormula :expression="line.latex" />
            <span :class="line.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ line.ok ? '✔' : '⚠' }}</span>
          </div>
        </div>
      </div>
      <p v-if="explained && roundingCase" class="section-text note">{{ RICHARDSON_ROUNDING_NOTE }}</p>
    </template>
    <p v-if="isFivePoint && explained" class="section-text note">{{ ENDPOINTS_NOTE }}</p>
    <p v-else-if="isFivePoint" class="section-text note">
      Los extremos de 5 puntos no tienen una identidad de este tipo: en ellos sólo se comprueba que el
      error real quede por debajo de la cota.
    </p>

    <!-- Modo tabla: secante común (diferencias) -->
    <template v-if="isTable">
      <p v-if="secantLines.length && explained" class="section-text">
        La progresiva en <MathFormula expression="x_i" /> y la regresiva en <MathFormula expression="x_{i+1}" /> usan
        la misma recta (la que une los dos puntos), por eso deben dar lo mismo:
      </p>
      <p v-else-if="secantLines.length" class="section-text">
        La progresiva en <MathFormula expression="x_i" /> y la regresiva en
        <MathFormula expression="x_{i+1}" /> usan la misma recta secante entre los dos puntos, así
        que deben ser iguales:
      </p>
      <div v-if="secantLines.length" class="check-list">
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
            <tr v-if="explained">
              <th v-for="col in COMPARISON_COLUMNS" :key="col.key">
                <InfoTip :text="col.text">{{ col.label }}</InfoTip>
              </th>
            </tr>
            <tr v-else>
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
      <small v-for="n in tinyNotes" :key="n.name" class="table-note">{{ n.name }}: {{ n.text }}</small>
      <GlossaryBlock
        v-if="explained"
        title="¿Qué significa cada columna?"
        :items="COMPARISON_COLUMNS.map((col) => ({ symbol: col.symbol, text: col.text }))"
      />
      <p v-for="line in conclusions" :key="line" class="section-text final-line">{{ line }}</p>
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
      Sin función para comparar no hay derivada exacta: sólo se comprueba
      {{ identityGroups.length ? 'cada identidad' : 'la secante común' }}.
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

.formula-box {
  overflow-x: auto;
  margin-bottom: var(--space-3);
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

.identity-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.identity-group + .identity-group {
  margin-top: var(--space-2);
}

.identity-point {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.identity-name {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.intro {
  color: var(--color-ink);
}

.identity-texts {
  margin: 0 0 var(--space-3);
  padding-left: var(--space-5);
  font-size: var(--text-small);
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
