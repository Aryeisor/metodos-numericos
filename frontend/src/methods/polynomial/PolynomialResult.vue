<script setup>
// Vista completa del resultado de Bairstow (`resultView` de la categoría):
// un polinomio se resuelve en varios factores, cada uno con su tabla de
// iteraciones y su gráfico, así que no encaja en la tabla única de
// ResultsTable. Orden: estado y advertencias → polinomio y coeficientes →
// paso previo (raíces nulas) → un bloque por factor → resumen de raíces y
// factorización.
import { computed, ref } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import FactorBlock from './FactorBlock.vue'
import { checkLatex, formatComplex } from './formulas'
import { exportBairstowPdf } from './pdf'

const props = defineProps({
  result: { type: Object, required: true },
  // Datos de entrada tal como se resolvieron (tolerancia en %, máximo...).
  system: { type: Object, required: true },
  methodName: { type: String, required: true },
})

const polynomial = computed(() => props.result.polynomial)
const tolerance = computed(() => props.result.tolerance_percent)

const coefficientRows = computed(() =>
  polynomial.value.coefficients.map((value, p) => ({
    power: polynomial.value.degree - p,
    value,
  }))
)

const factorIterations = (factor) =>
  (factor.iteration_indices ?? []).map((i) => props.result.iterations[i])

const totalIterations = computed(() =>
  props.result.factors.reduce((sum, f) => sum + (f.iterations_used ?? 0), 0)
)

const rootRows = computed(() =>
  props.result.roots.map((root, i) => ({
    name: `x_{${i + 1}}`,
    value: formatComplex(root.re, root.im),
    re: formatNumber(root.re),
    im: formatNumber(root.im),
    kind: root.im === 0 ? 'real' : 'compleja',
    check: root.check,
  }))
)

const reduced = computed(() => {
  const k = props.result.zero_roots
  if (!k) return null
  const coefficients = polynomial.value.coefficients.slice(0, polynomial.value.coefficients.length - k)
  return { k, degree: coefficients.length - 1 }
})
const firstDividend = computed(() => props.result.factors[0]?.dividend?.latex ?? null)

// --- PDF: los gráficos se toman de cada bloque de factor -------------------
const factorRefs = ref([])
function handleExportPdf() {
  const chartImages = props.result.factors.map((factor, i) =>
    factor.method === 'bairstow' ? factorRefs.value[i]?.toImage() ?? null : null
  )
  exportBairstowPdf({
    result: props.result,
    system: props.system,
    methodName: props.methodName,
    chartImages,
  })
}
</script>

<template>
  <div class="results">
    <div class="summary-header">
      <h3>Resultado ({{ methodName }})</h3>
      <div class="summary-actions">
        <span class="badge" :class="result.converged ? 'badge-success' : 'badge-danger'">
          {{ result.converged ? 'Convergió' : 'No convergió' }}
        </span>
        <button type="button" class="btn btn-outline" @click="handleExportPdf">Exportar PDF</button>
      </div>
    </div>

    <div v-for="(w, idx) in result.warnings" :key="'w' + idx" class="alert alert-warning">⚠ {{ w }}</div>
    <div v-for="(note, idx) in result.notes" :key="'n' + idx" class="alert alert-info">{{ note }}</div>

    <p class="meta">
      Raíces encontradas: <strong>{{ result.roots.length }}</strong> de {{ polynomial.degree }}
      · Iteraciones de Bairstow en total: <strong>{{ totalIterations }}</strong>
      · Tolerancia εs: <strong>{{ formatNumber(tolerance) }} %</strong>
    </p>

    <!-- 1. Polinomio y coeficientes -->
    <section class="result-section">
      <h4>Polinomio y coeficientes</h4>
      <div class="formula-box"><MathFormula :expression="`f(x) = ${polynomial.latex}`" display-mode /></div>
      <div class="table-scroll">
        <table class="coefficients-table">
          <thead>
            <tr>
              <th scope="row">Potencia</th>
              <th v-for="row in coefficientRows" :key="row.power">
                <MathFormula :expression="row.power === 0 ? 'x^0' : row.power === 1 ? 'x' : `x^{${row.power}}`" />
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Coeficiente</th>
              <td v-for="row in coefficientRows" :key="row.power">{{ formatNumber(row.value) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 2. Paso previo -->
    <section v-if="reduced" class="result-section">
      <h4>Paso previo: raíces nulas</h4>
      <p class="section-text">
        Como el término independiente es 0, se extrae primero el factor
        <MathFormula :expression="reduced.k === 1 ? 'x' : `x^{${reduced.k}}`" />:
        {{ reduced.k }} {{ reduced.k === 1 ? 'raíz' : 'raíces' }} <MathFormula expression="x = 0" />.
        <template v-if="firstDividend">
          El polinomio reducido es <MathFormula :expression="firstDividend" /> (grado {{ reduced.degree }}).
        </template>
        <template v-else>El polinomio reducido es de grado {{ reduced.degree }}.</template>
      </p>
    </section>

    <!-- 3. Factores -->
    <section v-if="result.factors.length" class="result-section">
      <h4>Factores</h4>
      <FactorBlock
        v-for="(factor, i) in result.factors"
        :key="`${result.factors.length}-${i}`"
        :ref="(el) => (factorRefs[i] = el)"
        :factor="factor"
        :iterations="factorIterations(factor)"
        :tolerance="tolerance"
        :open="i === 0"
      />
    </section>

    <!-- 4. Resumen -->
    <section class="result-section">
      <h4>Resumen de raíces</h4>
      <div class="table-scroll">
        <table class="roots-table">
          <thead>
            <tr>
              <th>Raíz</th>
              <th>Valor</th>
              <th>Parte real</th>
              <th>Parte imaginaria</th>
              <th>Tipo</th>
              <th>Comprobación |f(x)|</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rootRows" :key="row.name">
              <td><MathFormula :expression="row.name" /></td>
              <td class="root-value">{{ row.value }}</td>
              <td>{{ row.re }}</td>
              <td>{{ row.im }}</td>
              <td>{{ row.kind }}</td>
              <td><MathFormula :expression="checkLatex(row.check)" /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <template v-if="result.factorization">
        <p class="section-text">Factorización completa:</p>
        <div class="formula-box">
          <MathFormula :expression="`f(x) = ${result.factorization}`" display-mode />
        </div>
      </template>
      <p v-else class="section-text">
        No se muestra la factorización completa porque el método no encontró todas las raíces.
      </p>
    </section>
  </div>
</template>

<style scoped>
/* Encabezado con el mismo aspecto que el de ResultsTable. */
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

.meta {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
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

.formula-box {
  overflow-x: auto;
  margin-bottom: var(--space-3);
}

.coefficients-table,
.roots-table {
  width: auto;
  min-width: min(100%, 360px);
}

.coefficients-table th,
.coefficients-table td,
.roots-table th,
.roots-table td {
  padding: var(--space-2) var(--space-3);
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.coefficients-table tbody th,
.coefficients-table thead th:first-child {
  text-align: left;
}

.roots-table td:nth-child(5),
.roots-table th:nth-child(5) {
  text-align: left;
}

.root-value {
  font-weight: var(--weight-semibold);
}

.alert {
  margin-top: var(--space-3);
}
</style>
