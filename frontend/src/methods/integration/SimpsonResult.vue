<script setup>
// Vista completa del resultado del método de Simpson (`resultView`), con la
// misma organización que la del trapecio (IntegrationResult.vue):
// Modo función: resumen y comparación con el trapecio → datos del problema
// (derivadas hasta f⁽⁴⁾) → gráfico de parábolas o cúbicas (selector de regla y
// de n) → una tabla de refinamiento por regla, con sus fórmulas y glosarios →
// gráfico de convergencia → comprobación.
// Modo tabla: resumen → gráfico → tabla de puntos y cálculo por partes de
// cada regla aplicada → comprobación.
import { computed, ref, watch } from 'vue'
import ConvergenceChart from '../../components/ConvergenceChart.vue'
import DerivationSteps from '../../components/DerivationSteps.vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import MathFormula from '../../components/MathFormula.vue'
import TrapezoidChart from '../../components/TrapezoidChart.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import IntegrationRefinementTable from './IntegrationRefinementTable.vue'
import SimpsonPointsTable from './SimpsonPointsTable.vue'
import SimpsonVerification from './SimpsonVerification.vue'
import { integralLatex, percent } from './formulas'
import { ruleShort, trapezoidComparisonText } from './simpsonExplain'
import { SIMPSON_GLOSSARIES, simpsonApproxGlossary, simpsonBoundGlossary } from './simpsonGlossary'
import { exportSimpsonPdf } from './simpsonPdf'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  methodName: { type: String, required: true },
})

const isTable = computed(() => props.result.mode === 'table')
const fn = computed(() => props.result.function)
const integral = computed(() => props.result.integral)
const blocks = computed(() => props.result.rules ?? [])
const applications = computed(() => props.result.applications ?? [])
const aboutReference = computed(() => (integral.value?.kind === 'reference' ? ' (respecto al valor de referencia)' : ''))

const status = computed(() => {
  if (isTable.value) return { ok: true, label: 'Calculado' }
  return props.result.converged
    ? { ok: true, label: 'Alcanzó la tolerancia' }
    : { ok: false, label: 'No alcanzó la tolerancia' }
})

// Una tarjeta del resumen por regla (modo función) o por regla aplicada (tabla).
const summaries = computed(() => {
  if (isTable.value) {
    return applications.value.map((app) => ({ name: app.name, value: app.total, note: `n = ${props.result.n} segmentos`, final: app.final }))
  }
  return blocks.value.map((b) => {
    const last = b.rows.at(-1)
    return { name: b.rule.name, value: last.S, note: `n = ${last.n} segmentos`, final: last }
  })
})

// Comparación con el trapecio: fila 1 y última de cada regla.
const comparisons = computed(() =>
  blocks.value.map((b) => {
    const rows = b.rows.length > 1 ? [b.rows[0], b.rows.at(-1)] : [b.rows[0]]
    return { key: b.rule.key, lines: rows.map((row) => trapezoidComparisonText(b.rule, row)) }
  })
)

// --- Gráfico de parábolas / cúbicas ---------------------------------------------------
// Modo función: selector de regla (con «Ambas») y de fila (n ≤ 64).
// Modo tabla: selector de la regla aplicada si hay más de una.
const chartKey = ref(null)
const selectedK = ref(null)
function resetChart() {
  chartKey.value = isTable.value ? applications.value[0]?.key : blocks.value[0]?.rule.key
  selectedK.value = isTable.value ? 1 : (blocks.value[0]?.chart_rows[0]?.k ?? null)
}
resetChart()
watch(() => props.result, resetChart)
watch(chartKey, () => {
  if (!isTable.value) selectedK.value = chartBlock.value?.chart_rows[0]?.k ?? null
})
const chartBlock = computed(() => blocks.value.find((b) => b.rule.key === chartKey.value) ?? null)
const chartApp = computed(() => applications.value.find((a) => a.key === chartKey.value) ?? null)
const chartRows = computed(() => (isTable.value ? [] : (chartBlock.value?.chart_rows ?? [])))
const selectedRow = computed(() => {
  if (isTable.value) return chartApp.value?.chart_row ?? null
  return chartRows.value.find((r) => r.k === selectedK.value) ?? null
})
const chartChoices = computed(() =>
  isTable.value
    ? applications.value.map((a) => ({ key: a.key, label: a.name }))
    : blocks.value.map((b) => ({ key: b.rule.key, label: b.rule.name }))
)
const partLabels = computed(() =>
  chartApp.value?.key === 'combined'
    ? { simpson13: 'Parte 1/3 (parábolas)', simpson38: 'Parte 3/8 (cúbica)' }
    : null
)
const areaLabel = computed(() => {
  const row = selectedRow.value
  if (!row) return ''
  if (isTable.value) return `${chartApp.value.name} (n = ${row.n}): área S = ${formatNumber(chartApp.value.total)}`
  const S = chartBlock.value.rows[row.k - 1].S
  const shape = chartBlock.value.rule.key === 'simpson38' ? 'Cúbicas' : 'Parábolas'
  return `${shape} (n = ${row.n}): área S = ${formatNumber(S)}`
})
const curveLabel = computed(() => {
  const i = integral.value
  if (!i || i.value === null) return 'f(x)'
  return `f(x) · I = ${formatNumber(i.value)} (${i.kind === 'exact' ? 'exacta' : 'referencia'})`
})
const hasMoreRows = computed(() => !isTable.value && chartBlock.value && chartRows.value.length < chartBlock.value.rows.length)
const chartTitle = computed(() => {
  const keys = isTable.value ? applications.value.map((a) => a.key) : blocks.value.map((b) => b.rule.key)
  if (keys.length === 1 && keys[0] === 'simpson38') return 'Gráfico de las cúbicas'
  if (keys.length === 1 && keys[0] === 'simpson13') return 'Gráfico de las parábolas'
  return 'Gráfico de las parábolas y cúbicas'
})

// --- Gráfico de convergencia -------------------------------------------------------
const SERIES_COLORS = [
  ['--color-series-1', '--color-series-2'],
  ['--color-series-3', '--color-series-4'],
]
const series = computed(() =>
  blocks.value.flatMap((b, i) => {
    const [estimatedColor, trueColor] = SERIES_COLORS[i]
    const label = ruleShort(b.rule.key)
    const list = [{ label: `Error estimado (${label})`, values: b.rows.map((r) => r.estimated_error), color: estimatedColor }]
    if (integral.value?.value !== null && integral.value?.value !== undefined) {
      list.push({
        label: `|Eₜ| (${label})${aboutReference.value}`,
        values: b.rows.map((r) => (r.true_error === null ? null : Math.abs(r.true_error))),
        color: trueColor,
      })
    }
    return list
  })
)
const toleranceLabel = computed(() => `Tolerancia (${formatNumber(props.result.tolerance)})`)

const chartRef = ref(null)
const convergenceRef = ref(null)
function handleExportPdf() {
  exportSimpsonPdf({
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
      <div v-for="s in summaries" :key="s.name" class="summary-item">
        <span class="summary-label">{{ s.name }}</span>
        <MathFormula :expression="`I \\approx S = \\mathbf{${latexNumber(s.value)}}`" />
        <span class="summary-note">
          {{ s.note }}
          <template v-if="s.final && s.final.true_error !== null && s.final.true_error !== undefined">
            · Eₜ = {{ formatNumber(s.final.true_error) }} (εₜ = {{ percent(s.final.relative_error) }})
          </template>
        </span>
      </div>
      <div v-if="integral && integral.kind" class="summary-item">
        <span class="summary-label">{{ integral.kind === 'exact' ? 'Integral exacta' : 'Valor de referencia' }}</span>
        <MathFormula :expression="`I = \\mathbf{${latexNumber(integral.value)}}`" />
        <span class="summary-note">{{ integral.label }}</span>
      </div>
    </div>
    <div v-if="comparisons.length" class="comparison">
      <p class="comparison-title">Comparación con el trapecio (mismo n):</p>
      <ul>
        <template v-for="c in comparisons" :key="c.key">
          <li v-for="(line, idx) in c.lines" :key="c.key + idx">{{ line }}</li>
        </template>
      </ul>
    </div>
    <p class="meta">
      <template v-if="isTable">
        Puntos: <strong>{{ result.points.length }}</strong> · Segmentos: <strong>n = {{ result.n }}</strong> · h =
        <strong>{{ result.h.text }}</strong>
      </template>
      <template v-else>
        Filas usadas: <strong>{{ result.iterations_used }}</strong>
        · Estado:
        <strong>{{ result.converged ? 'alcanzó la tolerancia' : 'no alcanzó la tolerancia' }}</strong>
        ({{ formatNumber(result.tolerance) }})
        <template v-for="b in blocks" :key="b.rule.key"> · n₀ ({{ ruleShort(b.rule.key) }}) = <strong>{{ b.n0 }}</strong></template>
      </template>
    </p>
    <div v-for="(note, idx) in result.notes" :key="'n' + idx" class="alert alert-info">{{ note }}</div>
    <div v-for="(w, idx) in result.warnings" :key="'w' + idx" class="alert alert-warning">⚠ {{ w }}</div>

    <!-- 2. Datos del problema -->
    <section v-if="fn" class="result-section">
      <h4>Datos del problema</h4>
      <div v-if="!isTable" class="formula-box"><MathFormula :expression="integralLatex(result)" display-mode /></div>
      <div v-else class="formula-box">
        <MathFormula :expression="`f(x) = ${fn.latex} \\quad \\text{(función para comparar)}`" display-mode />
      </div>
      <h5 class="subheading">Derivadas de f(x)</h5>
      <p class="section-text">
        Para qué se necesitan: f′′′(x) se usa en el error aproximado de Chapra (con ella se obtiene el promedio de
        f⁽⁴⁾), y f⁽⁴⁾(x) en la cota del error: mide qué tanto se aleja la función de un polinomio de grado 3 (para esos,
        f⁽⁴⁾ = 0 y Simpson es exacto). f′ y f′′ se muestran sólo porque son pasos intermedios para llegar a f′′′.
      </p>
      <p class="section-text">Primera derivada: se deriva f término a término, con la regla de cada término.</p>
      <DerivationSteps :steps="fn.first.steps" :result="`f'(x) = ${fn.first.latex}`" />
      <p class="section-text">Segunda derivada: se deriva f′(x) con el mismo desglose.</p>
      <DerivationSteps :steps="fn.second.steps" :result="`f''(x) = ${fn.second.latex}`" />
      <p class="section-text">Tercera derivada: se deriva f′′(x).</p>
      <DerivationSteps :steps="fn.third.steps" :result="`f'''(x) = ${fn.third.latex}`" />
      <p class="section-text">Cuarta derivada: se deriva f′′′(x).</p>
      <DerivationSteps :steps="fn.fourth.steps" :result="`f^{(4)}(x) = ${fn.fourth.latex}`" />
      <p v-if="fn.uses_trigonometry" class="section-text note">Las funciones trigonométricas se evalúan en radianes.</p>
    </section>

    <!-- 3. Gráfico de parábolas / cúbicas -->
    <TrapezoidChart
      v-if="selectedRow"
      ref="chartRef"
      :curve="result.curve"
      :row="selectedRow"
      :title="chartTitle"
      :area-label="areaLabel"
      :curve-label="curveLabel"
      :part-labels="partLabels"
    >
      <div v-if="chartChoices.length > 1" class="row-picker" role="radiogroup" aria-label="Regla del gráfico">
        <span class="picker-label">Regla:</span>
        <button
          v-for="c in chartChoices"
          :key="c.key"
          type="button"
          role="radio"
          class="row-btn"
          :class="{ 'is-active': c.key === chartKey }"
          :aria-checked="c.key === chartKey"
          @click="chartKey = c.key"
        >
          {{ c.label }}
        </button>
      </div>
      <div v-if="chartRows.length > 1" class="row-picker" role="radiogroup" aria-label="Fila del gráfico">
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
      <p class="section-text note">
        Cada pieza sombreada es el área bajo una parábola (3 puntos) o una cúbica (4 puntos); los dos tonos alternan
        para que se vea dónde empieza y termina cada una.
      </p>
      <p v-if="hasMoreRows" class="section-text note">
        Sólo se pueden ver las filas con n ≤ 64: con más segmentos las piezas ya no se distinguen de la curva.
      </p>
    </TrapezoidChart>
    <p v-else class="section-text note">
      Con estos n₀ las piezas ya no se distinguen de la curva: el gráfico sólo se dibuja con n ≤ 64.
    </p>

    <!-- 4. Tablas -->
    <template v-if="!isTable">
      <section v-for="b in blocks" :key="b.rule.key" class="result-section">
        <h4>{{ b.rule.name }}: tabla de refinamiento</h4>
        <p class="section-text">
          La fila k usa <MathFormula expression="n_k = n_0 \cdot 2^{k-1}" /> segmentos (n₀ = {{ b.n0 }}) y
          <MathFormula expression="h_k = (b - a)/n_k" />. Al duplicar n la condición se mantiene
          ({{ b.rule.key === 'simpson38' ? 'n sigue siendo múltiplo de 3' : 'n sigue siendo par' }}). Cada fila se
          calcula con la fórmula de pesos; las alturas de la fila anterior se reutilizan. Despliega una fila para ver el
          cálculo paso a paso.
        </p>
        <div class="formula-list">
          <p class="formula-caption">Regla compuesta de {{ b.rule.name }}</p>
          <div class="formula-box"><MathFormula :expression="b.rule.formula_latex" /></div>
          <GlossaryBlock :items="SIMPSON_GLOSSARIES[b.rule.key].items" :summary="SIMPSON_GLOSSARIES[b.rule.key].summary" />
          <p class="formula-caption">Error de la regla (simple y compuesta)</p>
          <div class="formula-box"><MathFormula :expression="b.rule.simple_error_latex" /></div>
          <div class="formula-box"><MathFormula :expression="b.rule.error_latex" /></div>
          <p class="formula-caption">Error aproximado (Chapra)</p>
          <div class="formula-box"><MathFormula :expression="b.rule.approx_latex" /></div>
          <GlossaryBlock :items="simpsonApproxGlossary(b.rule.divisor).items" />
          <p class="formula-caption">Cota del error</p>
          <div class="formula-box"><MathFormula :expression="b.rule.bound_latex" /></div>
          <GlossaryBlock :items="simpsonBoundGlossary(b.rule.divisor).items" />
        </div>
        <IntegrationRefinementTable :result="result" :block="b" />
      </section>
      <p v-if="integral.value !== null" class="section-text">
        Eₜ = I − S con signo{{ aboutReference }}. La razón entre errores verdaderos consecutivos se acerca a 0.0625:
        el error es <MathFormula expression="O(h^{4})" />, así que dividir h entre 2 divide el error entre 16.
      </p>
      <p v-if="result.M4" class="section-text">
        La cota usa M₄, el máximo de |f⁽⁴⁾(x)| en [a, b], estimado por muestreo con {{ result.sampling_points }}
        puntos. La marca <sup>R</sup> aparece sólo cuando |Eₜ| supera la cota (más allá de una diferencia relativa de
        10⁻⁹) y el ✔ depende del margen de redondeo de la computadora, R = 2ε·Σ|wᵢ·f(xᵢ)|·(factor·h).
      </p>
    </template>
    <template v-else>
      <section v-for="app in applications" :key="app.key" class="result-section">
        <h4>{{ app.name }}: tabla de puntos</h4>
        <SimpsonPointsTable :result="result" :app="app" />
      </section>
    </template>

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
    <SimpsonVerification :result="result" />
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

.comparison {
  margin-top: var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink);
}

.comparison-title {
  margin: 0 0 var(--space-1);
  font-weight: var(--weight-semibold);
}

.comparison ul {
  margin: 0;
  padding-left: var(--space-5);
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
