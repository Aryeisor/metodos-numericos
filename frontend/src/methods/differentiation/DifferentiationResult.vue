<script setup>
// Vista completa del resultado de diferenciación numérica (`resultView`).
// Modo función: resumen → derivada exacta → una tabla de refinamiento por
// fórmula (con paso a paso) → gráfico de errores → comprobación.
// Modo tabla: resumen → derivada exacta (si hay función) → tabla de puntos
// (con paso a paso) → gráfico de aproximaciones → comprobación.
import { computed, ref } from 'vue'
import ConvergenceChart from '../../components/ConvergenceChart.vue'
import DerivationSteps from '../../components/DerivationSteps.vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import DataPointsTable from './DataPointsTable.vue'
import DifferentiationVerification from './DifferentiationVerification.vue'
import RefinementTable from './RefinementTable.vue'
import {
  ERRORS_GLOSSARY,
  ERRORS_LATEX,
  THREE_POINT_ERRORS_GLOSSARY,
  THREE_POINT_ERRORS_LATEX,
  formulaGlossary,
} from './differenceGlossary'
import { derivativeName, derivativeText, listNames } from './formulas'
import { exportDifferentiationPdf } from './pdf'
import { COMPARISON_LEGEND, UNIFORM_NOTE } from './threePointExplain'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  methodName: { type: String, required: true },
})

const isTable = computed(() => props.result.mode === 'table')
// Explicaciones para quien no conoce el método (glosarios, tooltips, paso a
// paso explicado): diferencias progresiva y regresiva y fórmula de 3 puntos;
// 5 puntos se ve como siempre.
const explained = computed(() => ['diferencias-finitas', 'tres-puntos'].includes(props.result.method))
const isThreePoint = computed(() => props.result.method === 'tres-puntos')
const errorsLatex = computed(() => (isThreePoint.value ? THREE_POINT_ERRORS_LATEX : ERRORS_LATEX))
const errorsGlossary = computed(() => (isThreePoint.value ? THREE_POINT_ERRORS_GLOSSARY : ERRORS_GLOSSARY))
const formulas = computed(() => props.result.formulas)
const fn = computed(() => props.result.function)
const last = computed(() => props.result.iterations.at(-1)?.extra ?? null)

const status = computed(() => {
  if (isTable.value) return { ok: true, label: 'Calculado' }
  return props.result.converged
    ? { ok: true, label: 'Alcanzó la tolerancia' }
    : { ok: false, label: 'No alcanzó la tolerancia' }
})

const higher = computed(() =>
  Object.entries(fn.value?.higher_derivatives ?? {}).map(([n, d]) => ({
    n,
    latex: `${derivativeName(Number(n))}(x) = ${d.latex}`,
    // Fórmulas de 3 y 5 puntos: cada derivada se obtiene derivando la anterior.
    steps: d.steps ?? null,
    from: derivativeText(Number(n) - 1),
    name: derivativeText(Number(n)),
  }))
)
const higherSteps = computed(() => higher.value.filter((d) => d.steps))

// --- Gráfico -------------------------------------------------------------------
// Modo función: error estimado y error real de cada fórmula (hasta 4 series),
// escala log; los valores null o 0 quedan como huecos (ConvergenceChart).
// Modo tabla: aproximaciones frente a xᵢ, escala lineal.
// Con n fórmulas: error estimado con los colores 1..n y error real con n+1..2n
// (hasta 6 series con las fórmulas de 3 y 5 puntos).
const COLORS = [
  '--color-series-1',
  '--color-series-2',
  '--color-series-3',
  '--color-series-4',
  '--color-series-5',
  '--color-series-6',
]
const series = computed(() => {
  const rows = props.result.iterations
  if (isTable.value) {
    const list = formulas.value.map((f, i) => ({
      label: f.name,
      values: rows.map((step) => step.extra[f.key]?.D ?? null),
      color: COLORS[i],
    }))
    if (fn.value) {
      list.push({
        label: "f′(x) exacta",
        values: rows.map((step) => step.extra.exact),
        color: COLORS[Math.max(2, formulas.value.length)],
      })
    }
    return list
  }
  return formulas.value.flatMap((f, i) => [
    {
      label: `Error estimado (${f.name.toLowerCase()})`,
      values: rows.map((step) => step.extra[f.key].estimated_error),
      color: COLORS[i],
    },
    ...(props.result.differentiable
      ? [{
          label: `Error real (${f.name.toLowerCase()})`,
          values: rows.map((step) => step.extra[f.key].real_error),
          color: COLORS[i + formulas.value.length],
        }]
      : []),
  ])
})
const chartLabels = computed(() =>
  isTable.value ? props.result.iterations.map((step) => step.extra.x_display.text) : null
)
// Notas que dependen de la fórmula (orden del error) y del método (regla de R).
const order = computed(() => formulas.value[0].order)
const roundingText = computed(() => props.result.rounding_text ?? 'R = 4ε·máx|f|/h')
const hasRecommended = computed(() => Boolean(props.result.iterations[0]?.extra.recommended))
// |f⁽⁵⁾(x)|, y «o |f′′′(x)| (según la fórmula)» con el punto medio de 3 puntos de referencia.
const boundNames = computed(() => {
  const names = [...new Set(formulas.value.map((f) => f.bound_derivative))].map((n) => `|${derivativeText(n)}(x)|`)
  return names.length > 1 ? `${names.join(' o ')} (según la fórmula)` : names[0]
})
const isFivePoint = computed(() => props.result.method === 'cinco-puntos')

const toleranceLabel = computed(() => `Tolerancia (${formatNumber(props.result.tolerance)})`)

const chartRef = ref(null)
function handleExportPdf() {
  exportDifferentiationPdf({
    result: props.result,
    methodName: props.methodName,
    chartImage: chartRef.value?.toImage() ?? null,
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
    <div v-if="!isTable && last" class="summary-grid">
      <div v-for="f in formulas" :key="f.key" class="summary-item">
        <span class="summary-label">{{ f.name }}</span>
        <MathFormula :expression="`f'(x_0) \\approx ${f.symbol_latex} = \\mathbf{${latexNumber(last[f.key].D)}}`" />
      </div>
      <div class="summary-item">
        <span class="summary-label">Valor exacto</span>
        <MathFormula
          v-if="result.differentiable"
          :expression="`f'(${result.x0_display.latex}) = \\mathbf{${latexNumber(result.exact)}}`"
        />
        <span v-else>f no es derivable en x₀</span>
      </div>
    </div>
    <p class="meta">
      <template v-if="isTable">
        Puntos: <strong>{{ result.iterations_used }}</strong>
        · Fórmula: <strong>{{ listNames(formulas.map((f) => f.name)) }}</strong>
        · Espaciado: <strong>{{ result.uniform ? 'uniforme' : 'no uniforme' }}</strong>
      </template>
      <template v-else>
        Filas usadas: <strong>{{ result.iterations_used }}</strong>
        · Estado:
        <strong>{{ result.converged ? 'alcanzó la tolerancia' : 'no alcanzó la tolerancia' }}</strong>
        ({{ formatNumber(result.tolerance) }})
        · x₀ = <strong>{{ result.x0_display.text }}</strong>
        · h₀ = <strong>{{ result.iterations[0]?.extra.h.text }}</strong>
      </template>
    </p>
    <div v-if="result.comparison?.length" class="comparison">
      <p class="comparison-title">
        {{ result.comparison_title ?? 'Comparación con las diferencias progresiva y regresiva' }}
      </p>
      <p v-if="explained" class="comparison-line">{{ COMPARISON_LEGEND }}</p>
      <p v-for="line in result.comparison" :key="line.k" class="comparison-line">{{ line.text }}</p>
    </div>
    <div v-for="(w, idx) in result.warnings" :key="'w' + idx" class="alert alert-warning">⚠ {{ w }}</div>

    <!-- 2. Derivada exacta (explicada: como en integración) -->
    <section v-if="fn && explained" class="result-section">
      <h4>Derivada exacta</h4>
      <div class="formula-box"><MathFormula :expression="`f(x) = ${fn.latex}`" display-mode /></div>
      <p v-if="isThreePoint" class="section-text">
        Para qué sirve cada una: f′(x) es la derivada <strong>exacta</strong>, sólo para comparar y calcular el error
        real. f′′(x) es un paso intermedio para llegar a f′′′(x). f′′′(x) se usa en la cota del error, porque mide qué
        tanto se aleja la función de una parábola.
      </p>
      <p v-else class="section-text">
        Para qué se necesitan: f′(x) es la derivada <strong>exacta</strong>; el sistema la usa sólo para comparar y
        calcular el error real (el método no la necesita para aproximar). f′′(x) mide qué tan curva es la función y se
        usa para la cota del error: mientras más curva, más se separa la recta secante de la tangente.
      </p>
      <p class="section-text">Primera derivada: se deriva f término a término, con la regla de cada término.</p>
      <DerivationSteps :steps="fn.derivative.steps" :result="`f'(x) = ${fn.derivative.latex}`" />
      <template v-if="fn.higher_derivatives[2]">
        <p class="section-text">Segunda derivada: se deriva f′(x) con el mismo desglose.</p>
        <DerivationSteps
          :steps="fn.higher_derivatives[2].steps"
          :result="`f''(x) = ${fn.higher_derivatives[2].latex}`"
        />
      </template>
      <template v-if="isThreePoint && fn.higher_derivatives[3]">
        <p class="section-text">Tercera derivada: se deriva f′′(x) con el mismo desglose.</p>
        <DerivationSteps
          :steps="fn.higher_derivatives[3].steps"
          :result="`f'''(x) = ${fn.higher_derivatives[3].latex}`"
        />
      </template>
      <p v-if="fn.uses_trigonometry" class="section-text note">
        Las funciones trigonométricas se evalúan en radianes.
      </p>
    </section>

    <!-- 2. Derivada exacta -->
    <section v-else-if="fn" class="result-section">
      <h4>Derivada exacta</h4>
      <div class="formula-box"><MathFormula :expression="`f(x) = ${fn.latex}`" display-mode /></div>
      <p class="section-text">Se deriva f término a término:</p>
      <div class="partial-card">
        <ul class="partial-terms">
          <li v-for="(term, t) in fn.derivative.steps.terms" :key="t">
            <div class="partial-formula"><MathFormula :expression="term.latex" /></div>
            <span class="partial-rule">{{ term.rule }}</span>
          </li>
        </ul>
        <div v-if="fn.derivative.steps.sum_latex" class="partial-sum">
          <MathFormula :expression="fn.derivative.steps.sum_latex" />
        </div>
      </div>
      <template v-for="d in higherSteps" :key="`steps-${d.n}`">
        <p class="section-text">
          Se deriva {{ d.from }} término a término para obtener {{ d.name }}:
        </p>
        <div class="partial-card">
          <ul class="partial-terms">
            <li v-for="(term, t) in d.steps.terms" :key="t">
              <div class="partial-formula"><MathFormula :expression="term.latex" /></div>
              <span class="partial-rule">{{ term.rule }}</span>
            </li>
          </ul>
          <div v-if="d.steps.sum_latex" class="partial-sum">
            <MathFormula :expression="d.steps.sum_latex" />
          </div>
          <div v-else class="partial-sum">
            <MathFormula :expression="d.latex" />
          </div>
        </div>
      </template>
      <div class="formula-box">
        <MathFormula :expression="`f'(x) = ${fn.derivative.latex}`" display-mode />
        <MathFormula v-for="d in higher" :key="d.n" :expression="d.latex" display-mode />
      </div>
      <p v-if="fn.uses_trigonometry" class="section-text note">
        Las funciones trigonométricas se evalúan en radianes.
      </p>
    </section>

    <!-- 3. Tablas -->
    <section class="result-section">
      <h4>{{ isTable ? 'Derivada en cada punto' : 'Tabla de refinamiento' }}</h4>
      <p class="section-text">
        <template v-if="isTable && isFivePoint">
          En cada xᵢ, cada fórmula usa los datos vecinos que necesita; donde faltan se muestra «—».
          El punto medio de 3 puntos se muestra como referencia. La columna «Recomendada» toma el
          punto medio de 5 puntos donde existe; si no, el extremo de 5 puntos (hacia adelante si
          existe; si no, hacia atrás), y el punto medio de 3 puntos sólo donde no aplica ninguna
          fórmula de 5 puntos. Despliega una fila para ver el cálculo.
        </template>
        <template v-else-if="isTable && hasRecommended">
          <template v-if="explained">{{ UNIFORM_NOTE }}</template>
          En cada xᵢ, cada fórmula usa los datos vecinos que necesita; donde faltan se muestra «—».
          La columna «Recomendada» toma el punto medio donde existe (es la más precisa) y, en los
          extremos de la tabla, la fórmula de extremo. Despliega una fila para ver el cálculo.
        </template>
        <template v-else-if="isTable">
          En cada xᵢ, cada fórmula usa su punto vecino con su propio h. Despliega una fila para ver
          el cálculo.
        </template>
        <template v-else>
          La fila k usa <MathFormula expression="h_k = h_0 / 2^{k-1}" />. Despliega una fila para ver
          el cálculo paso a paso.
        </template>
      </p>
      <div v-if="explained" class="formula-column">
        <template v-for="f in formulas" :key="f.key">
          <p class="formula-caption">{{ isThreePoint ? f.name : `Diferencia ${f.name.toLowerCase()}` }}</p>
          <div class="formula-box"><MathFormula :expression="f.formula_latex" /></div>
          <GlossaryBlock :items="formulaGlossary(f.key).items" :summary="formulaGlossary(f.key).summary" />
        </template>
        <template v-if="fn">
          <p class="formula-caption">Errores y cota</p>
          <div class="formula-box"><MathFormula :expression="errorsLatex" /></div>
          <GlossaryBlock :items="errorsGlossary.items" />
        </template>
        <p class="color-legend">
          Colores del paso a paso: <span class="legend-prev">■ azul</span>: el valor en el punto base x₀, o el valor de
          la fila anterior · <span class="legend-current">■ verde</span>: el valor nuevo, en el punto vecino o en la fila
          actual.
        </p>
      </div>
      <div v-else class="formula-list">
        <div v-for="f in formulas" :key="f.key" class="formula-box">
          <MathFormula :expression="f.formula_latex" />
          <MathFormula :expression="f.bound_latex" />
        </div>
      </div>

      <DataPointsTable v-if="isTable" :result="result" :explained="explained" />
      <template v-else>
        <RefinementTable v-for="f in formulas" :key="f.key" :result="result" :formula="f" :explained="explained" />
      </template>

      <p v-if="!isTable && result.differentiable && order === 1" class="section-text">
        La razón entre errores reales consecutivos se acerca a
        {{ formatNumber(formulas[0].expected_ratio) }}: al reducir h a la mitad, el error también se
        reduce a la mitad, que es lo que significa que la fórmula sea de orden O(h).
      </p>
      <p v-else-if="!isTable && result.differentiable" class="section-text">
        La razón entre errores reales consecutivos se acerca a
        {{ formatNumber(formulas[0].expected_ratio) }}: el error es
        <MathFormula :expression="`O(h^{${order}})`" />, así que dividir h entre 2 divide el error entre
        {{ 2 ** order }}.
      </p>
      <p v-if="fn && explained" class="section-text">
        La cota usa M, el máximo de {{ boundNames }} en el intervalo de cada {{ isTable ? 'fórmula' : 'fila' }}, estimado por
        muestreo con {{ result.sampling_points }} puntos equiespaciados. La marca <sup>R</sup> aparece sólo cuando el
        error real supera la cota (más allá de una diferencia relativa de 10⁻⁹) y el ✔ depende del margen de redondeo
        de la computadora, {{ roundingText }}.
      </p>
      <p v-else-if="fn" class="section-text">
        La cota usa M, el máximo de {{ boundNames }}
        en el intervalo de cada {{ isTable ? 'fórmula' : 'fila' }}, estimado por muestreo con
        {{ result.sampling_points }} puntos equiespaciados. La marca <sup>R</sup> indica que el error
        real supera la cota sólo por el redondeo de la computadora ({{ roundingText }}).
      </p>
    </section>

    <!-- 4. Gráfico -->
    <ConvergenceChart
      ref="chartRef"
      :iterations="result.iterations"
      :tolerance="isTable ? null : result.tolerance"
      :converged="result.converged"
      :series="series"
      :labels="chartLabels"
      :logarithmic="!isTable"
      :title="isTable ? 'Aproximaciones de f′(x) en cada punto' : 'Convergencia del error'"
      :x-label="isTable ? 'x' : 'k'"
      :y-label="isTable ? 'f′(x)' : 'Error (escala log)'"
      :tolerance-label="toleranceLabel"
    />

    <!-- 5. Comprobación -->
    <DifferentiationVerification :result="result" :explained="explained" />
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

.summary-label {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  margin-bottom: var(--space-1);
}

.meta {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.alert {
  margin-top: var(--space-3);
}

.comparison {
  margin-top: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  font-size: var(--text-small);
}

.comparison-title {
  margin: 0 0 var(--space-1);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.comparison-line {
  margin: var(--space-1) 0 0;
  color: var(--color-ink-muted);
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
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr));
  gap: var(--space-3);
}

.formula-column {
  display: flex;
  flex-direction: column;
}

.formula-caption {
  margin: var(--space-3) 0 var(--space-1);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.color-legend {
  margin: var(--space-2) 0 var(--space-4);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.legend-prev {
  color: var(--color-value-old);
  font-weight: var(--weight-semibold);
}

.legend-current {
  color: var(--color-value-new);
  font-weight: var(--weight-semibold);
}

.formula-list .formula-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Mismas tarjetas que las derivadas parciales de Newton. */
.partial-card {
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-3);
}

.partial-terms {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.partial-formula {
  overflow-x: auto;
}

.partial-rule {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.partial-sum {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-line);
  font-weight: var(--weight-semibold);
  overflow-x: auto;
}
</style>
