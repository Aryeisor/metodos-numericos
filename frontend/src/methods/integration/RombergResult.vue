<script setup>
// Vista completa del resultado de la integración de Romberg (`resultView`):
// resumen → datos del problema (sólo la integral: Romberg no usa derivadas) →
// gráfico de segmentos (columnas 1 a 3) → tabla triangular (fórmulas y glosarios encima, leyenda debajo, tabla de
// errores opcional) → tabla de convergencia de la diagonal → gráfico de
// convergencia → paso a paso de cada fila → comprobación. Modo tabla: la
// misma vista, con los datos que usa cada fila.
import { computed, ref, watch } from 'vue'
import ConvergenceChart from '../../components/ConvergenceChart.vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import TrapezoidChart from '../../components/TrapezoidChart.vue'
import RombergConvergenceTable from './RombergConvergenceTable.vue'
import RombergRowSteps from './RombergRowSteps.vue'
import RombergTable from './RombergTable.vue'
import RombergVerification from './RombergVerification.vue'
import { integralLatex, percent } from './formulas'
import { RECURRENCE_LATEX, RICHARDSON_LATEX, STOP_LATEX } from './rombergExplain'
import {
  CHART_GLOSSARY,
  CHART_UNDRAWABLE,
  RECURRENCE_GLOSSARY,
  RICHARDSON_GLOSSARY,
  TABLE_LEGEND,
} from './rombergGlossary'
import { exportRombergPdf } from './rombergPdf'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  methodName: { type: String, required: true },
})

const isTable = computed(() => props.result.mode === 'table')
const fn = computed(() => props.result.function)
const integral = computed(() => props.result.integral)
const rows = computed(() => props.result.iterations.map((s) => s.extra))
const last = computed(() => rows.value.at(-1))
const hasI = computed(() => integral.value?.value !== null && integral.value?.value !== undefined)
const reference = computed(() => integral.value?.kind === 'reference')

const status = computed(() => {
  if (isTable.value) return { ok: true, label: 'Calculado' }
  return props.result.converged ? { ok: true, label: 'Alcanzó la tolerancia' } : { ok: false, label: 'No alcanzó la tolerancia' }
})

const showErrors = ref(false)
watch(
  () => props.result,
  () => {
    showErrors.value = false
  }
)

// --- Gráfico de segmentos: columnas 1 a 3 (Newton-Cotes), filas con n ≤ 64 -----------
// Por defecto la columna 1 en la fila de mayor n ≤ 8 (la misma que va al PDF).
const CHART_COLUMNS = [
  { k: 1, label: 'Trapecio (columna 1)', shape: 'Rectas' },
  { k: 2, label: 'Simpson 1/3 (columna 2)', shape: 'Parábolas' },
  { k: 3, label: 'Boole (columna 3)', shape: 'Curvas de grado 4' },
]
const chartRows = computed(() => props.result.chart_rows ?? [])
const rowsFor = (k) => chartRows.value.filter((r) => r.columns.length >= k)
const chartColumns = computed(() => CHART_COLUMNS.filter((c) => rowsFor(c.k).length))
const chartK = ref(1)
const selectedI = ref(null)
// Al cambiar de columna se conserva n si existe; si no, la de mayor n ≤ 8.
function pickRow(k, n = null) {
  const list = rowsFor(k)
  return (list.find((r) => r.n === n) ?? list.filter((r) => r.n <= 8).at(-1) ?? list[0])?.i ?? null
}
function resetChart() {
  chartK.value = 1
  selectedI.value = pickRow(1)
}
resetChart()
watch(() => props.result, resetChart)
const columnRows = computed(() => rowsFor(chartK.value))
const selectedRow = computed(() => {
  const row = chartRows.value.find((r) => r.i === selectedI.value)
  return row && row.columns.length >= chartK.value ? { ...row, pieces: row.columns[chartK.value - 1] } : null
})
function selectColumn(k) {
  selectedI.value = pickRow(k, selectedRow.value?.n)
  chartK.value = k
}
const areaLabel = computed(() => {
  const row = selectedRow.value
  if (!row) return ''
  const k = chartK.value
  const cell = rows.value[row.i - 1]
  const error = cell.errors ? ` · Eₜ = ${formatNumber(cell.errors[k - 1])}` : ''
  return `${CHART_COLUMNS[k - 1].shape} (n = ${row.n}): área R${row.i},${k} = ${formatNumber(cell.values[k - 1])}${error}`
})
const curveLabel = computed(() => {
  const i = integral.value
  if (!i || i.value === null) return 'f(x)'
  return `f(x) · I = ${formatNumber(i.value)} (${i.kind === 'exact' ? 'exacta' : 'referencia'})`
})
const hasMoreRows = computed(() => chartRows.value.length < rows.value.length)
const chartTitle = computed(() => `Gráfico de segmentos: ${CHART_COLUMNS[chartK.value - 1].label}`)

// --- Gráfico de convergencia: |Eₜ| de las columnas 1 y 2 y de la diagonal, y el error estimado.
const series = computed(() => {
  const about = reference.value ? ' (respecto a la referencia)' : ''
  const list = []
  if (hasI.value) {
    list.push(
      { label: `|Eₜ| trapecio (columna 1)${about}`, values: rows.value.map((r) => Math.abs(r.errors[0])), color: '--color-series-3' },
      { label: `|Eₜ| Simpson 1/3 (columna 2)${about}`, values: rows.value.map((r) => (r.i >= 2 ? Math.abs(r.errors[1]) : null)), color: '--color-series-2' },
      { label: `|Eₜ| Romberg (diagonal)${about}`, values: rows.value.map((r) => Math.abs(r.true_error)), color: '--color-series-1' }
    )
  }
  list.push({ label: 'Error estimado (diagonal)', values: rows.value.map((r) => r.estimated_error), color: '--color-series-4' })
  return list
})
const toleranceLabel = computed(() => `Tolerancia (${formatNumber(props.result.tolerance)})`)

const chartRef = ref(null)
const convergenceRef = ref(null)
function handleExportPdf() {
  exportRombergPdf({
    result: props.result,
    methodName: props.methodName,
    chartImage: chartRef.value?.toImage() ?? null,
    chartTitle: `${chartTitle.value} — ${areaLabel.value}`,
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
        <span class="summary-label">Mejor valor (diagonal de la última fila)</span>
        <MathFormula :expression="`I \\approx R_{${last.i},${last.i}} = \\mathbf{${latexNumber(last.best)}}`" />
        <span class="summary-note">
          n = {{ last.n }} segmentos
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
      Filas usadas: <strong>{{ result.iterations_used }}</strong>
      · {{ isTable ? 'Datos usados' : 'Evaluaciones de f' }}: <strong>{{ result.evaluations }}</strong>
      <template v-if="!isTable">
        (2<sup>{{ result.iterations_used - 1 }}</sup> + 1) · Estado:
        <strong>{{ result.converged ? 'alcanzó la tolerancia' : 'no alcanzó la tolerancia' }}</strong>
        ({{ formatNumber(result.tolerance) }})
      </template>
    </p>
    <div v-for="(note, idx) in result.notes" :key="'n' + idx" class="alert alert-info">{{ note }}</div>
    <div v-for="(w, idx) in result.warnings" :key="'w' + idx" class="alert alert-warning">⚠ {{ w }}</div>

    <!-- 2. Datos del problema -->
    <section class="result-section">
      <h4>Datos del problema</h4>
      <div v-if="!isTable" class="formula-box"><MathFormula :expression="integralLatex(result)" display-mode /></div>
      <template v-else>
        <p class="section-text">
          {{ result.points.length }} datos igualmente espaciados en [{{ result.a_display.text }}, {{ result.b_display.text }}]
          (2<sup>{{ result.iterations_used - 1 }}</sup> + 1 puntos).
        </p>
        <div v-if="fn" class="formula-box">
          <MathFormula :expression="`f(x) = ${fn.latex} \\quad \\text{(función para comparar)}`" display-mode />
        </div>
      </template>
      <p class="section-text">Romberg no usa derivadas: sólo evalúa f (o usa los datos) y combina trapecios.</p>
      <p v-if="fn && fn.uses_trigonometry" class="section-text note">Las funciones trigonométricas se evalúan en radianes.</p>
    </section>

    <!-- 3. Gráfico de segmentos (columnas 1 a 3) -->
    <TrapezoidChart
      v-if="selectedRow"
      ref="chartRef"
      :curve="result.curve"
      :row="selectedRow"
      :title="chartTitle"
      :area-label="areaLabel"
      :curve-label="curveLabel"
    >
      <div v-if="chartColumns.length > 1" class="row-picker" role="radiogroup" aria-label="Columna del gráfico">
        <span class="picker-label">Columna:</span>
        <button
          v-for="c in chartColumns"
          :key="c.k"
          type="button"
          role="radio"
          class="row-btn"
          :class="{ 'is-active': c.k === chartK }"
          :aria-checked="c.k === chartK"
          @click="selectColumn(c.k)"
        >
          {{ c.label }}
        </button>
      </div>
      <div v-if="columnRows.length > 1" class="row-picker" role="radiogroup" aria-label="Fila del gráfico">
        <span class="picker-label">Segmentos:</span>
        <button
          v-for="r in columnRows"
          :key="r.i"
          type="button"
          role="radio"
          class="row-btn"
          :class="{ 'is-active': r.i === selectedI }"
          :aria-checked="r.i === selectedI"
          @click="selectedI = r.i"
        >
          n = {{ r.n }}
        </button>
      </div>
      <p class="section-text note">
        Cada celda Rᵢ,ₖ de las columnas 1 a 3 es una regla de Newton-Cotes compuesta con n = 2^(i−1) segmentos: el área
        sombreada es esa celda. Los dos tonos alternan para que se vea dónde empieza y termina cada pieza.
        <template v-if="isTable">Las piezas pasan por los datos que usa la fila elegida.</template>
      </p>
      <p class="section-text note">{{ CHART_UNDRAWABLE }}</p>
      <p v-if="hasMoreRows" class="section-text note">
        Sólo se pueden ver las filas con n ≤ 64: con más segmentos las piezas ya no se distinguen de la curva.
      </p>
      <GlossaryBlock title="¿Cómo se lee este gráfico?" :items="CHART_GLOSSARY" />
    </TrapezoidChart>

    <!-- 4. Tabla triangular -->
    <section class="result-section">
      <h4>Tabla triangular de Romberg</h4>
      <p class="section-text">
        La columna 1 son trapecios con n = 1, 2, 4, 8, … segmentos, calculados con la recurrencia del trapecio; cada
        columna siguiente combina dos valores de la anterior (extrapolación de Richardson) para eliminar un término del
        error.
      </p>
      <div class="formula-list">
        <p class="formula-caption">Columna 1: trapecios con la recurrencia</p>
        <div class="formula-box"><MathFormula :expression="RECURRENCE_LATEX" /></div>
        <GlossaryBlock :items="RECURRENCE_GLOSSARY.items" :summary="RECURRENCE_GLOSSARY.summary" />
        <p class="formula-caption">Columnas siguientes: extrapolación de Richardson</p>
        <div class="formula-box"><MathFormula :expression="RICHARDSON_LATEX" /></div>
        <GlossaryBlock :items="RICHARDSON_GLOSSARY.items" :summary="RICHARDSON_GLOSSARY.summary" />
        <p class="formula-caption">Criterio de parada</p>
        <div class="formula-box"><MathFormula :expression="STOP_LATEX" /></div>
        <p class="section-text">
          <template v-if="isTable">
            En el modo tabla no hay criterio de parada: con {{ result.points.length }} puntos sólo se pueden armar
            {{ result.iterations_used }} filas.
          </template>
          <template v-else>
            El método se detiene cuando el error estimado es ≤ {{ formatNumber(result.tolerance) }} y ya hay al menos
            {{ result.min_rows }} filas. εₐ (Chapra) sólo informa.
          </template>
        </p>
      </div>
      <RombergTable :result="result" />
      <GlossaryBlock title="¿Cómo se lee esta tabla?" :items="TABLE_LEGEND" />
      <template v-if="hasI">
        <button type="button" class="btn btn-outline" :aria-expanded="showErrors" @click="showErrors = !showErrors">
          {{ showErrors ? 'Ocultar tabla de errores' : 'Ver tabla de errores' }}
        </button>
        <div v-if="showErrors" class="errors-table">
          <p class="section-text">
            La misma tabla con el error verdadero de cada celda, Eₜ = I − Rᵢ,ₖ{{ reference ? ' (respecto al valor de referencia)' : '' }}:
            el error se achica hacia la derecha (cada columna elimina un término) y hacia abajo (h más chico).
          </p>
          <RombergTable :result="result" field="errors" />
        </div>
      </template>
    </section>

    <!-- 5. Convergencia de la diagonal -->
    <section class="result-section">
      <h4>Convergencia de la diagonal</h4>
      <RombergConvergenceTable :result="result" />
    </section>

    <!-- 6. Gráfico de convergencia -->
    <ConvergenceChart
      ref="convergenceRef"
      :iterations="result.iterations"
      :tolerance="isTable ? null : result.tolerance"
      :converged="result.converged"
      :series="series"
      title="Convergencia del error"
      x-label="i (fila)"
      y-label="Error (escala log)"
      :tolerance-label="toleranceLabel"
    />
    <p class="section-text note">
      Los errores iguales a 0 no se pueden dibujar en escala logarítmica: esos puntos se dejan como huecos.
      <template v-if="!hasI">Sin valor exacto ni de referencia sólo se dibuja el error estimado.</template>
    </p>

    <!-- 7. Paso a paso -->
    <section class="result-section">
      <h4>Paso a paso de cada fila</h4>
      <p class="section-text">
        Despliega una fila para ver el trapecio nuevo, cada extrapolación (en verde el valor de la misma fila, en azul
        el de la fila anterior), el error estimado y el error verdadero.
      </p>
      <RombergRowSteps :result="result" />
    </section>

    <!-- 8. Comprobación -->
    <RombergVerification :result="result" />
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

.errors-table {
  margin-top: var(--space-3);
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
</style>
