<script setup>
// Vista completa del resultado de integración numérica (`resultView`).
// Modo función: resumen → datos del problema → gráfico de trapecios (con
// selector de fila) → tabla de refinamiento (con paso a paso) → gráfico de
// convergencia → comprobación.
// Modo tabla: resumen → gráfico de trapecios → tabla de segmentos (con paso a
// paso) → comprobación.
import { computed, ref, watch } from 'vue'
import ConvergenceChart from '../../components/ConvergenceChart.vue'
import DerivationSteps from '../../components/DerivationSteps.vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import MathFormula from '../../components/MathFormula.vue'
import TrapezoidChart from '../../components/TrapezoidChart.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import IntegrationRefinementTable from './IntegrationRefinementTable.vue'
import IntegrationVerification from './IntegrationVerification.vue'
import SegmentsTable from './SegmentsTable.vue'
import { integralLatex, percent } from './formulas'
import { APPROX_GLOSSARY, BOUND_GLOSSARY, COMPOSITE_GLOSSARY } from './glossary'
import { exportIntegrationPdf } from './pdf'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  methodName: { type: String, required: true },
})

const isTable = computed(() => props.result.mode === 'table')
const fn = computed(() => props.result.function)
const integral = computed(() => props.result.integral)
const last = computed(() => props.result.iterations.at(-1)?.extra ?? null)
const approximation = computed(() => (isTable.value ? props.result.total : last.value.T))
const finalErrors = computed(() =>
  isTable.value ? props.result.verification.final : last.value
)

const status = computed(() => {
  if (isTable.value) return { ok: true, label: 'Calculado' }
  return props.result.converged
    ? { ok: true, label: 'Alcanzó la tolerancia' }
    : { ok: false, label: 'No alcanzó la tolerancia' }
})

const integralName = computed(() => {
  const i = integral.value
  if (!i || i.kind === null) return null
  return i.kind === 'exact' ? 'Integral exacta' : 'Valor de referencia'
})
const aboutReference = computed(() => (integral.value?.kind === 'reference' ? ' (respecto al valor de referencia)' : ''))

// --- Gráfico de trapecios ------------------------------------------------------
// Filas con n ≤ 64 (las que llegan en chart_rows). Por defecto la fila 1, o la
// de mayor n ≤ 8 si n₀ > 1.
const chartRows = computed(() => props.result.chart_rows)
function defaultRow() {
  const rows = chartRows.value
  if (!rows.length) return null
  if (isTable.value || props.result.n0 === 1) return rows[0].k
  const small = rows.filter((r) => r.n <= 8)
  return (small.at(-1) ?? rows[0]).k
}
const selectedK = ref(defaultRow())
watch(
  () => props.result,
  () => {
    selectedK.value = defaultRow()
  }
)
const selectedRow = computed(() => chartRows.value.find((r) => r.k === selectedK.value) ?? null)
const selectedArea = computed(() => {
  if (!selectedRow.value) return null
  return isTable.value ? props.result.total : props.result.iterations[selectedRow.value.k - 1].extra.T
})
const areaLabel = computed(() =>
  selectedRow.value ? `Trapecios (n = ${selectedRow.value.n}): área T = ${formatNumber(selectedArea.value)}` : ''
)
const curveLabel = computed(() => {
  const i = integral.value
  if (!i || i.value === null) return 'f(x)'
  return `f(x) · I = ${formatNumber(i.value)} (${i.kind === 'exact' ? 'exacta' : 'referencia'})`
})
const hasMoreRows = computed(() => !isTable.value && chartRows.value.length < props.result.iterations.length)

// --- Gráfico de convergencia -------------------------------------------------------
const series = computed(() => {
  const rows = props.result.iterations
  const list = [{ label: 'Error estimado', values: rows.map((s) => s.extra.estimated_error), color: '--color-series-1' }]
  if (integral.value?.value !== null && integral.value?.value !== undefined) {
    list.push({
      label: `|Eₜ|${aboutReference.value}`,
      values: rows.map((s) => (s.extra.true_error === null ? null : Math.abs(s.extra.true_error))),
      color: '--color-series-2',
    })
  }
  return list
})
const toleranceLabel = computed(() => `Tolerancia (${formatNumber(props.result.tolerance)})`)

const trapezoidRef = ref(null)
const convergenceRef = ref(null)
function handleExportPdf() {
  exportIntegrationPdf({
    result: props.result,
    methodName: props.methodName,
    trapezoidImage: trapezoidRef.value?.toImage() ?? null,
    trapezoidRow: selectedRow.value,
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
        <span class="summary-label">{{ isTable ? 'Suma de los trapecios' : 'Aproximación' }}</span>
        <MathFormula :expression="`I \\approx T = \\mathbf{${latexNumber(approximation)}}`" />
        <span class="summary-note">
          {{ isTable ? `${result.iterations_used} segmentos` : `n = ${last.n} segmentos` }}
        </span>
      </div>
      <div v-if="integralName" class="summary-item">
        <span class="summary-label">{{ integralName }}</span>
        <MathFormula :expression="`I = \\mathbf{${latexNumber(integral.value)}}`" />
        <span class="summary-note">{{ integral.label }}</span>
      </div>
      <div v-if="finalErrors && finalErrors.true_error !== null && finalErrors.true_error !== undefined" class="summary-item">
        <span class="summary-label">Error verdadero{{ aboutReference }}</span>
        <MathFormula :expression="`E_t = ${latexNumber(finalErrors.true_error)}`" />
        <span class="summary-note">εₜ = {{ percent(finalErrors.relative_error) }}</span>
      </div>
    </div>
    <p class="meta">
      <template v-if="isTable">
        Puntos: <strong>{{ result.points.length }}</strong>
        · Espaciado: <strong>{{ result.uniform ? 'uniforme' : 'no uniforme' }}</strong>
      </template>
      <template v-else>
        Filas usadas: <strong>{{ result.iterations_used }}</strong>
        · Estado:
        <strong>{{ result.converged ? 'alcanzó la tolerancia' : 'no alcanzó la tolerancia' }}</strong>
        ({{ formatNumber(result.tolerance) }})
        · n₀ = <strong>{{ result.n0 }}</strong>
      </template>
    </p>
    <div v-for="(note, idx) in result.notes" :key="'n' + idx" class="alert alert-info">{{ note }}</div>
    <div v-for="(w, idx) in result.warnings" :key="'w' + idx" class="alert alert-warning">⚠ {{ w }}</div>

    <!-- 2. Datos del problema -->
    <section v-if="!isTable || fn" class="result-section">
      <h4>Datos del problema</h4>
      <div v-if="!isTable" class="formula-box"><MathFormula :expression="integralLatex(result)" display-mode /></div>
      <div v-else class="formula-box">
        <MathFormula :expression="`f(x) = ${fn.latex} \\quad \\text{(función para comparar)}`" display-mode />
      </div>
      <h5 class="subheading">Derivadas de f(x)</h5>
      <p class="section-text">
        Para qué se necesitan: f′(x) se usa en el error aproximado de Chapra (con ella se obtiene el promedio de f′′),
        y f′′(x) en la cota del error, porque mide qué tan curva es la función: mientras más curva, más se separan los
        trapecios de la curva.
      </p>
      <p class="section-text">Primera derivada: se deriva f término a término, con la regla de cada término.</p>
      <DerivationSteps :steps="fn.first.steps" :result="`f'(x) = ${fn.first.latex}`" />
      <p class="section-text">Segunda derivada: se deriva f′(x) con el mismo desglose.</p>
      <DerivationSteps :steps="fn.second.steps" :result="`f''(x) = ${fn.second.latex}`" />
      <p v-if="fn.uses_trigonometry" class="section-text note">Las funciones trigonométricas se evalúan en radianes.</p>
    </section>

    <!-- 3. Gráfico de trapecios -->
    <TrapezoidChart
      v-if="selectedRow"
      ref="trapezoidRef"
      :curve="result.curve"
      :row="selectedRow"
      :title="isTable ? 'Trapecios de los datos' : 'Gráfico de los trapecios'"
      :area-label="areaLabel"
      :curve-label="curveLabel"
    >
      <div v-if="!isTable && chartRows.length > 1" class="row-picker" role="radiogroup" aria-label="Fila del gráfico">
        <span class="picker-label">Segmentos:</span>
        <button
          v-for="r in chartRows"
          :key="r.k"
          type="button"
          role="radio"
          class="row-btn"
          :class="{ 'is-active': r.k === selectedK }"
          :aria-checked="r.k === selectedK"
          @click="selectedK = r.k"
        >
          n = {{ r.n }}
        </button>
      </div>
      <p v-if="hasMoreRows" class="section-text note">
        Sólo se pueden ver las filas con n ≤ 64: con más segmentos los trapecios ya no se distinguen de la curva.
      </p>
    </TrapezoidChart>
    <p v-else class="section-text note">
      Con n₀ = {{ result.n0 }} los trapecios ya no se distinguen de la curva: el gráfico sólo se dibuja con n ≤ 64.
    </p>

    <!-- 4. Tablas -->
    <section class="result-section">
      <h4>{{ isTable ? 'Tabla de segmentos' : 'Tabla de refinamiento' }}</h4>
      <template v-if="isTable">
        <div class="formula-box">
          <MathFormula expression="I \approx \sum_{i=0}^{n-1} (x_{i+1} - x_i)\,\frac{y_i + y_{i+1}}{2}" display-mode />
        </div>
        <p class="section-text">
          Cada segmento es un trapecio con su propio ancho hᵢ = xᵢ₊₁ − xᵢ. Despliega una fila para ver el cálculo.
        </p>
        <SegmentsTable :result="result" />
        <p v-if="fn" class="section-text">
          La cota es <MathFormula expression="\sum_i \frac{h_i^{3}}{12} \max |f''|" /> con el máximo de cada
          segmento estimado por muestreo con {{ result.sampling_points }} puntos.
        </p>
      </template>
      <template v-else>
        <p class="section-text">
          La fila k usa <MathFormula expression="n_k = n_0 \cdot 2^{k-1}" /> segmentos y
          <MathFormula expression="h_k = (b - a)/n_k" />. Desde la fila 2 sólo se evalúan los puntos nuevos:
          <MathFormula expression="T_k = \frac{T_{k-1}}{2} + h_k \sum_{\text{nuevos}} f(x_i)" />. Despliega una fila
          para ver el cálculo paso a paso.
        </p>
        <div class="formula-list">
          <p class="formula-caption">Regla compuesta del trapecio</p>
          <div class="formula-box"><MathFormula :expression="result.rule.formula_latex" /></div>
          <GlossaryBlock :items="COMPOSITE_GLOSSARY.items" :summary="COMPOSITE_GLOSSARY.summary" />
          <p class="formula-caption">Error aproximado (Chapra)</p>
          <div class="formula-box">
            <MathFormula expression="E_a = -\frac{(b - a)\,h^{2}}{12}\,\bar{f''},\quad \bar{f''} = \frac{f'(b) - f'(a)}{b - a}" />
          </div>
          <GlossaryBlock :items="APPROX_GLOSSARY.items" />
          <p class="formula-caption">Cota del error</p>
          <div class="formula-box"><MathFormula :expression="result.rule.bound_latex" /></div>
          <GlossaryBlock :items="BOUND_GLOSSARY.items" />
        </div>
        <IntegrationRefinementTable :result="result" />
        <p v-if="integral.value !== null" class="section-text">
          Eₜ = I − T con signo{{ aboutReference }}. La razón entre errores verdaderos consecutivos se acerca a
          {{ formatNumber(result.rule.expected_ratio) }}: el error es <MathFormula expression="O(h^{2})" />, así que
          dividir h entre 2 divide el error entre 4.
        </p>
        <p v-if="result.M2" class="section-text">
          La cota usa M₂, el máximo de |f′′(x)| en [a, b], estimado por muestreo con {{ result.sampling_points }}
          puntos. La marca <sup>R</sup> aparece sólo cuando |Eₜ| supera la cota (más allá de una diferencia relativa
          de 10⁻⁹) y el ✔ depende del margen de redondeo de la computadora, R = 2ε·Σ|wᵢ·f(xᵢ)|·h/2.
        </p>
      </template>
    </section>

    <!-- 5. Gráfico de convergencia -->
    <ConvergenceChart
      v-if="!isTable"
      ref="convergenceRef"
      :iterations="result.iterations"
      :tolerance="result.tolerance"
      :converged="result.converged"
      :series="series"
      title="Convergencia del error"
      x-label="k"
      y-label="Error (escala log)"
      :tolerance-label="toleranceLabel"
    />

    <!-- 6. Comprobación -->
    <IntegrationVerification :result="result" />
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

.subheading {
  margin: var(--space-4) 0 var(--space-2);
  font-size: var(--text-body);
  color: var(--color-ink);
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
