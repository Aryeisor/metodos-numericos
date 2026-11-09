<script setup>
// Vista completa del resultado de la cuadratura gaussiana (`resultView`):
// resumen → datos del problema y cambio de variable → derivadas para la cota →
// fórmulas con sus glosarios → gráfico de rectángulos → tabla de refinamiento →
// gráfico de convergencia → paso a paso de cada fila → comprobación.
import { computed, ref, watch } from 'vue'
import ConvergenceChart from '../../components/ConvergenceChart.vue'
import DerivationSteps from '../../components/DerivationSteps.vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import TrapezoidChart from '../../components/TrapezoidChart.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import GaussStepDetail from './GaussStepDetail.vue'
import GaussVerification from './GaussVerification.vue'
import { tinyErrorNote } from './explain'
import { boundMark, cell, integralLatex, percent } from './formulas'
import {
  BOUND_GLOSSARY,
  BOUND_LATEX,
  CHANGE_GLOSSARY,
  CHART_GLOSSARY,
  COMPOSITE_GLOSSARY,
  COMPOSITE_LATEX,
  GAUSS_GLOSSARY,
  GAUSS_LATEX,
  NODES_GLOSSARY,
  NODES_LATEX,
  STOP_LATEX,
  TABLE_LEGEND,
  centersLatex,
  changeOfVariable,
  derivativeLatex,
  derivativeText,
  gaussColumns,
} from './gaussExplain'
import { exportGaussPdf } from './gaussPdf'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  methodName: { type: String, required: true },
})

const fn = computed(() => props.result.function)
const integral = computed(() => props.result.integral)
const rows = computed(() => props.result.iterations.map((s) => s.extra))
const last = computed(() => rows.value.at(-1))
const N = computed(() => props.result.subintervals)
const hasI = computed(() => integral.value?.value !== null && integral.value?.value !== undefined)
const reference = computed(() => integral.value?.kind === 'reference')
const status = computed(() =>
  props.result.converged ? { ok: true, label: 'Alcanzó la tolerancia' } : { ok: false, label: 'No alcanzó la tolerancia' }
)
const headers = computed(() => gaussColumns({ showTrue: hasI.value, reference: reference.value }))
const tinyRows = computed(() => rows.value.filter((r) => tinyErrorNote(r, reference.value)).map((r) => r.m))

// --- Derivadas para la cota: f⁽²ᵐ⁾ de las filas con m ≤ 5, cada una con la impar anterior.
const derivativePairs = computed(() => {
  const list = fn.value.derivatives
  const pairs = []
  for (let order = 2; order <= list.length; order += 2) pairs.push({ m: order / 2, items: [list[order - 2], list[order - 1]] })
  return pairs
})
const usedRows = computed(() => Math.min(rows.value.length, props.result.max_bound_points))
const missingDerivatives = computed(() => fn.value.derivatives.length < 2 * usedRows.value)
const derivativeResult = (d) => `${derivativeLatex(d.order)}(x) = ${d.latex}`
const previousName = (d) => (d.order === 1 ? 'f(x)' : `${derivativeText(d.order - 1)}(x)`)

// --- Gráfico de rectángulos: por defecto m = 3 (la misma fila va al PDF) -------------------
const chartRows = computed(() => props.result.chart_rows)
const selectedM = ref(3)
function resetChart() {
  selectedM.value = Math.min(3, chartRows.value.length)
}
resetChart()
watch(() => props.result, resetChart)
const selectedRow = computed(() => chartRows.value.find((r) => r.m === selectedM.value) ?? null)
const areaLabel = computed(() => {
  const row = rows.value[selectedM.value - 1]
  if (!row) return ''
  const error = row.true_error !== null ? ` · Eₜ = ${formatNumber(row.true_error)}` : ''
  return `Rectángulos (m = ${row.m}${N.value > 1 ? `, N = ${N.value}` : ''}): área G${sub(row.m)} = ${formatNumber(row.G)}${error}`
})
const curveLabel = computed(() => {
  const i = integral.value
  if (!i || i.value === null) return 'f(x)'
  return `f(x) · I = ${formatNumber(i.value)} (${i.kind === 'exact' ? 'exacta' : 'referencia'})`
})
const chartTitle = computed(() => `Gráfico de rectángulos (m = ${selectedM.value})`)
const SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'
function sub(n) {
  return String(n).replace(/\d/g, (d) => SUBSCRIPTS[d])
}

// --- Gráfico de convergencia: |Eₜ| y el error estimado frente a m ---------------------------
const series = computed(() => {
  const list = []
  if (hasI.value) {
    list.push({
      label: `|Eₜ|${reference.value ? ' (respecto a la referencia)' : ''}`,
      values: rows.value.map((r) => Math.abs(r.true_error)),
      color: '--color-series-1',
    })
  }
  list.push({ label: 'Error estimado |Gₘ − Gₘ₋₁|', values: rows.value.map((r) => r.estimated_error), color: '--color-series-4' })
  return list
})
const toleranceLabel = computed(() => `Tolerancia (${formatNumber(props.result.tolerance)})`)

const chartRef = ref(null)
const convergenceRef = ref(null)
function handleExportPdf() {
  exportGaussPdf({
    result: props.result,
    methodName: props.methodName,
    chartImage: chartRef.value?.toImage() ?? null,
    chartTitle: `${chartTitle.value} — ${areaLabel.value}`,
    chartM: selectedM.value,
    convergenceImage: convergenceRef.value?.toImage() ?? null,
  })
}
</script>

<template>
  <div class="results">
    <div class="summary-header">
      <h3>Resultado ({{ methodName }})</h3>
      <div class="summary-actions">
        <span class="badge" :class="status.ok ? 'badge-success' : 'badge-danger'">{{ status.label }}</span>
        <button type="button" class="btn btn-outline" @click="handleExportPdf">Exportar PDF</button>
      </div>
    </div>

    <!-- 1. Resumen -->
    <div class="summary-grid">
      <div class="summary-item">
        <span class="summary-label">Resultado (última fila)</span>
        <MathFormula :expression="`I \\approx G_{${last.m}} = \\mathbf{${latexNumber(last.G)}}`" />
        <span class="summary-note">
          m = {{ last.m }} puntos · N = {{ N }} {{ N === 1 ? 'subintervalo' : 'subintervalos' }}
          <template v-if="last.true_error !== null">
            · Eₜ = {{ formatNumber(last.true_error) }} (εₜ = {{ percent(last.relative_error) }})
          </template>
        </span>
      </div>
      <div v-if="integral && integral.kind" class="summary-item">
        <span class="summary-label">{{ integral.kind === 'exact' ? 'Integral exacta' : 'Valor de referencia' }}</span>
        <MathFormula :expression="`I = \\mathbf{${latexNumber(integral.value)}}`" />
        <span class="summary-note">{{ integral.label }}</span>
      </div>
    </div>
    <p class="meta">
      Filas usadas: <strong>{{ result.iterations_used }}</strong> · Evaluaciones de f:
      <strong>{{ result.evaluations }}</strong> en total ({{ last.evaluations }} en la última fila) · Estado:
      <strong>{{ result.converged ? 'alcanzó la tolerancia' : 'no alcanzó la tolerancia' }}</strong>
      ({{ formatNumber(result.tolerance) }})
    </p>
    <div v-for="(note, idx) in result.notes" :key="'n' + idx" class="alert alert-info">{{ note }}</div>
    <div v-for="(w, idx) in result.warnings" :key="'w' + idx" class="alert alert-warning">⚠ {{ w }}</div>

    <!-- 2. Datos del problema y cambio de variable -->
    <section class="result-section">
      <h4>Datos del problema</h4>
      <div class="formula-box"><MathFormula :expression="integralLatex(result)" display-mode /></div>
      <p class="formula-caption">Cambio de variable{{ N > 1 ? ' (en un subintervalo genérico j)' : '' }}</p>
      <p class="section-text">
        Se lleva el intervalo {{ N === 1 ? '[a, b]' : 'de cada subintervalo' }} a [−1, 1], porque los nodos y pesos están
        calculados para ese intervalo.
      </p>
      <div v-for="(line, idx) in changeOfVariable(result)" :key="idx" class="formula-box">
        <MathFormula :expression="line" />
      </div>
      <p v-if="N > 1" class="section-text">
        Centros de los {{ N }} subintervalos, c<sub>j</sub> = a + (j − ½)H:
        <MathFormula :expression="centersLatex(result)" />
      </p>
      <GlossaryBlock :items="CHANGE_GLOSSARY" />
      <p v-if="fn.uses_trigonometry" class="section-text note">Las funciones trigonométricas se evalúan en radianes.</p>
    </section>

    <!-- 3. Derivadas para la cota -->
    <section class="result-section">
      <h4>Derivadas para la cota</h4>
      <p class="section-text">
        La cota de la fila m usa la derivada de orden 2m de f (hasta m = {{ result.max_bound_points }}, f⁽¹⁰⁾). Se deriva
        término a término, una vez por cada orden; sólo se muestran las que usan las filas calculadas.
      </p>
      <div v-for="pair in derivativePairs" :key="pair.m" class="derivative-pair">
        <p class="formula-caption">{{ derivativeText(2 * pair.m) }}(x): la usa la cota de m = {{ pair.m }}</p>
        <template v-for="d in pair.items" :key="d.order">
          <p class="section-text">{{ d.order % 2 ? 'Primero' : 'Luego' }} se deriva {{ previousName(d) }}:</p>
          <details v-if="d.long" class="long-derivative">
            <summary>Mostrar {{ derivativeText(d.order) }}(x) (expresión larga)</summary>
            <div class="formula-box"><MathFormula :expression="derivativeResult(d)" /></div>
          </details>
          <DerivationSteps v-else-if="d.steps && d.steps.terms.length" :steps="d.steps" :result="derivativeResult(d)" />
          <div v-else class="formula-box"><MathFormula :expression="derivativeResult(d)" /></div>
        </template>
      </div>
      <p v-if="missingDerivatives" class="section-text note">
        No se alcanzó a calcular {{ derivativeText(fn.derivatives.length + 1) }} en el límite de tiempo: la cota de las
        filas siguientes no está disponible.
      </p>
    </section>

    <!-- 4. Fórmulas y glosarios -->
    <section class="result-section">
      <h4>Fórmula de Gauss</h4>
      <div class="formula-list">
        <p class="formula-caption">Fórmula simple (N = 1, notación de Chapra)</p>
        <div class="formula-box"><MathFormula :expression="GAUSS_LATEX" /></div>
        <GlossaryBlock :items="GAUSS_GLOSSARY.items" :summary="GAUSS_GLOSSARY.summary" />
        <template v-if="N > 1">
          <p class="formula-caption">Fórmula compuesta (N = {{ N }})</p>
          <div class="formula-box"><MathFormula :expression="COMPOSITE_LATEX" /></div>
          <GlossaryBlock :items="COMPOSITE_GLOSSARY.items" :summary="COMPOSITE_GLOSSARY.summary" />
        </template>
        <p class="formula-caption">Nodos y pesos</p>
        <div class="formula-box"><MathFormula :expression="NODES_LATEX" /></div>
        <GlossaryBlock :items="NODES_GLOSSARY.items" />
        <p class="formula-caption">Criterio de parada</p>
        <div class="formula-box"><MathFormula :expression="STOP_LATEX" /></div>
        <p class="section-text">
          Cada fila agrega un punto (m = 1, 2, 3, …). El método se detiene cuando el error estimado es ≤
          {{ formatNumber(result.tolerance) }} y ya hay al menos {{ result.min_rows }} filas.
        </p>
        <p class="formula-caption">Cota del error (m ≤ {{ result.max_bound_points }})</p>
        <div class="formula-box"><MathFormula :expression="BOUND_LATEX" /></div>
        <GlossaryBlock :items="BOUND_GLOSSARY" />
      </div>
    </section>

    <!-- 5. Gráfico de rectángulos -->
    <TrapezoidChart
      v-if="selectedRow"
      ref="chartRef"
      :curve="result.curve"
      :row="selectedRow"
      :title="chartTitle"
      :area-label="areaLabel"
      :curve-label="curveLabel"
    >
      <div v-if="chartRows.length > 1" class="row-picker" role="radiogroup" aria-label="Puntos del gráfico">
        <span class="picker-label">Puntos:</span>
        <button
          v-for="r in chartRows"
          :key="r.m"
          type="button"
          role="radio"
          class="row-btn"
          :class="{ 'is-active': r.m === selectedM }"
          :aria-checked="r.m === selectedM"
          @click="selectedM = r.m"
        >
          m = {{ r.m }}
        </button>
      </div>
      <p class="section-text note">
        El área sombreada es G con m = {{ selectedM }}: la suma de las áreas de los rectángulos. Los dos tonos alternan
        para distinguir un rectángulo del siguiente.
        <template v-if="selectedRow.overlap">
          Con m = {{ selectedM }} algunos rectángulos vecinos se superponen: se dibujan semitransparentes, así que donde se
          cruzan el color es más intenso.
        </template>
      </p>
      <GlossaryBlock title="¿Cómo se lee este gráfico?" :items="CHART_GLOSSARY" />
    </TrapezoidChart>

    <!-- 6. Tabla de refinamiento -->
    <section class="result-section">
      <h4>Tabla de refinamiento</h4>
      <div class="table-scroll">
        <table class="iterations-table">
          <thead>
            <tr>
              <th v-for="col in headers" :key="col.key">
                <InfoTip :text="col.text">{{ col.label }}</InfoTip>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.m">
              <td>{{ row.m }}</td>
              <td>{{ row.evaluations }}</td>
              <td>{{ cell(row.G) }}</td>
              <td>{{ cell(row.estimated_error) }}</td>
              <td v-if="hasI">{{ cell(row.true_error) }}</td>
              <td v-if="hasI">{{ percent(row.relative_error) }}</td>
              <td>{{ row.bound === null ? 'no disponible' : cell(row.bound) }}</td>
              <td v-if="hasI" class="mark-cell">
                <span v-if="row.within_bound !== null" :class="row.within_bound ? 'mark mark-ok' : 'mark mark-warn'">{{ boundMark(row) }}</span>
                <template v-else>—</template>
                <sup v-if="row.by_rounding" class="rounding-mark" title="Sólo dentro del margen de redondeo R">R</sup>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <small v-if="tinyRows.length" class="table-note">
        Filas {{ tinyRows.join(', ') }}: {{ tinyErrorNote(rows[tinyRows[0] - 1], reference) }}
      </small>
      <GlossaryBlock title="¿Qué significa cada columna?" :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))" />
      <GlossaryBlock title="¿Cómo se lee esta tabla?" :items="TABLE_LEGEND" />
    </section>

    <!-- 7. Gráfico de convergencia -->
    <ConvergenceChart
      ref="convergenceRef"
      :iterations="result.iterations"
      :tolerance="result.tolerance"
      :converged="result.converged"
      :series="series"
      title="Convergencia del error"
      x-label="m (puntos)"
      y-label="Error (escala log)"
      :tolerance-label="toleranceLabel"
    />
    <p class="section-text note">
      Los errores iguales a 0 no se pueden dibujar en escala logarítmica: esos puntos se dejan como huecos.
      <template v-if="!hasI">Sin valor exacto ni de referencia sólo se dibuja el error estimado.</template>
    </p>

    <!-- 8. Paso a paso -->
    <section class="result-section">
      <h4>Paso a paso de cada fila</h4>
      <p class="section-text">
        Despliega una fila para ver sus nodos y pesos, cómo se llevan a [a, b], la evaluación de f, la suma ponderada, los
        errores y la cota.
      </p>
      <div class="row-list">
        <details v-for="(row, idx) in rows" :key="row.m" class="row-details">
          <summary>Fila {{ row.m }} (m = {{ row.m }}, {{ row.evaluations }} evaluaciones): G{{ sub(row.m) }} = {{ formatNumber(row.G) }}</summary>
          <div class="row-body">
            <GaussStepDetail :result="result" :row="row" :previous="idx > 0 ? rows[idx - 1] : null" />
          </div>
        </details>
      </div>
    </section>

    <!-- 9. Comprobación -->
    <GaussVerification :result="result" />
  </div>
</template>

<style scoped>
.summary-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.summary-header h3 {
  margin: 0;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
  gap: var(--space-3);
}

.summary-item {
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
}

.summary-label,
.summary-note {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.summary-label {
  margin-bottom: var(--space-1);
}

.summary-note {
  margin-top: var(--space-1);
}

.meta {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.alert {
  margin-top: var(--space-3);
}

.result-section {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
}

.result-section h4 {
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

.formula-list {
  display: flex;
  flex-direction: column;
}

.formula-caption {
  margin: var(--space-3) 0 var(--space-1);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.derivative-pair {
  margin-bottom: var(--space-4);
}

.long-derivative summary {
  cursor: pointer;
  color: var(--color-accent);
  font-size: var(--text-small);
  margin-bottom: var(--space-2);
}

.iterations-table td,
.iterations-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.mark-cell {
  text-align: center !important;
}

.rounding-mark {
  margin-left: 2px;
  color: var(--color-ink-muted);
}

.table-note {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.row-picker {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.picker-label {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.row-btn {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  color: var(--color-ink);
  font-size: var(--text-small);
  cursor: pointer;
}

.row-btn:hover {
  background: var(--color-accent-soft);
}

.row-btn.is-active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
  font-weight: var(--weight-semibold);
}

.row-btn:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.row-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.row-details {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  background: var(--color-surface);
}

.row-details > summary {
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.row-body {
  padding: var(--space-3) var(--space-4) var(--space-4);
  border-top: 1px solid var(--color-line);
  background: var(--color-page);
}
</style>
