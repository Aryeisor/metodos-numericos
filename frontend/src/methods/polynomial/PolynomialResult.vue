<script setup>
// Vista completa del resultado de Bairstow (`resultView` de la categoría):
// un polinomio se resuelve en varios factores, cada uno con su tabla de
// iteraciones y su gráfico, así que no encaja en la tabla única de
// ResultsTable. Orden: estado y advertencias → polinomio y coeficientes →
// paso previo (raíces nulas) → un bloque por factor → resumen de raíces y
// factorización → comprobación (cada raíz sustituida en el polinomio).
import { computed, ref } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import FactorBlock from './FactorBlock.vue'
import { checkLatex, complexCheckRows, complexLatex, formatComplex, realCheckParts } from './formulas'
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

// --- Comprobación ---------------------------------------------------------
// Valor exacto de f(x) en letra pequeña cuando se muestra «≈ 0» o el residuo.
function exactLatex(check) {
  if (check.abs === 0) return null
  if (check.value.im !== 0) return `|f| = ${checkLatex(check.abs)}`
  return `${check.value.re < 0 ? '-' : ''}${checkLatex(check.abs)}`
}

// Raíces reales: una línea cada una. Las raíces nulas del paso previo son
// todas iguales (f(0) = a₀ = 0), así que van en una sola línea.
const realChecks = computed(() => {
  const lines = []
  props.result.roots.forEach((root, i) => {
    if (root.im !== 0 || !root.verification) return
    const zeroLine = root.re === 0 && lines.find((line) => line.zero)
    if (zeroLine) {
      zeroLine.multiplicity += 1
      return
    }
    const parts = realCheckParts(root)
    lines.push({
      key: i,
      zero: root.re === 0,
      multiplicity: 1,
      ...parts,
      // Con residuo apreciable el valor ya se ve completo en `result`.
      exact: parts.ok ? exactLatex(root.verification) : null,
    })
  })
  return lines
})

// Líneas largas (grado alto o raíces con decimales): los términos calculados
// y el resultado pasan a un segundo renglón, alineado bajo la sustitución.
const CHECK_LINE_MAX_CHARS = 70
const stackedChecks = computed(() =>
  realChecks.value.some(
    (line) => line.substitution.length + (line.evaluated?.length ?? 0) > CHECK_LINE_MAX_CHARS
  )
)

// Pares complejos: se comprueba la raíz con parte imaginaria positiva; la
// conjugada se marca con el mismo resultado.
const complexChecks = computed(() =>
  props.result.roots.flatMap((root, i) => {
    if (!(root.im > 0) || !root.verification) return []
    const conjugate = props.result.roots.findIndex(
      (other, j) => j !== i && other.re === root.re && other.im === -root.im
    )
    const parts = complexCheckRows(root)
    // La suma ya redondeada; si redondea a 0 pero no es 0 exacto, «≈ 0».
    let sumDisplay = parts.sum
    if (parts.ok && root.verification.abs !== 0) {
      sumDisplay = parts.sum === '0' ? '\\approx 0' : `${parts.sum} \\approx 0`
    }
    return [{
      key: i,
      ...parts,
      sumDisplay,
      exact: exactLatex(root.verification),
      names: [i, conjugate].filter((j) => j >= 0).map((j) => `x_{${j + 1}}`),
      conjugate: complexLatex(root.re, -root.im),
    }]
  })
)

const hasResidue = computed(
  () => realChecks.value.some((line) => !line.ok) || complexChecks.value.some((pair) => !pair.ok)
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

    <!-- 5. Comprobación -->
    <section v-if="realChecks.length || complexChecks.length" class="result-section">
      <h4>Comprobación</h4>
      <p class="section-text">Cada raíz se reemplaza en el polinomio original; el resultado debe dar 0.</p>

      <div v-if="realChecks.length" class="table-scroll">
        <div class="check-grid" :class="{ 'is-stacked': stackedChecks }">
          <template v-for="line in realChecks" :key="line.key">
            <MathFormula :expression="line.lhs" />
            <MathFormula :expression="`= ${line.substitution}`" />
            <span v-if="stackedChecks"></span>
            <MathFormula v-if="line.evaluated && !stackedChecks" :expression="`= ${line.evaluated}`" />
            <span v-else-if="!stackedChecks"></span>
            <span class="check-result">
              <MathFormula v-if="line.evaluated && stackedChecks" :expression="`= ${line.evaluated}`" />
              <MathFormula :expression="line.result" />
              <span v-if="line.ok" class="mark mark-ok" aria-label="correcto">✔</span>
              <span v-else class="mark mark-warn" aria-label="residuo apreciable">⚠</span>
              <small v-if="line.exact" class="check-exact">(<MathFormula :expression="line.exact" />)</small>
              <small v-if="line.multiplicity > 1" class="check-exact">
                (raíz de multiplicidad {{ line.multiplicity }})
              </small>
            </span>
          </template>
        </div>
      </div>

      <div v-for="pair in complexChecks" :key="pair.key" class="complex-check">
        <p class="complex-title"><MathFormula :expression="pair.lhs" /></p>
        <div class="table-scroll">
          <table class="check-table">
            <thead>
              <tr>
                <th>Término</th>
                <th>Potencia de x</th>
                <th>Coeficiente · potencia</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in pair.rows" :key="idx">
                <td><MathFormula :expression="row.term" /></td>
                <td>
                  <MathFormula v-if="row.power" :expression="row.power" />
                  <span v-else>—</span>
                </td>
                <td><MathFormula :expression="row.value" /></td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <th scope="row">Suma</th>
                <td></td>
                <td>
                  <span class="check-result">
                    <strong><MathFormula :expression="pair.sumDisplay" /></strong>
                    <span v-if="pair.ok" class="mark mark-ok" aria-label="correcto">✔</span>
                    <span v-else class="mark mark-warn" aria-label="residuo apreciable">⚠</span>
                    <small v-if="pair.exact" class="check-exact">(<MathFormula :expression="pair.exact" />)</small>
                  </span>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
        <p v-if="pair.ok" class="section-text">
          La raíz conjugada <MathFormula :expression="pair.conjugate" /> también cumple f = 0,
          porque los coeficientes del polinomio son reales.
        </p>
        <p v-else class="section-text">
          La raíz conjugada <MathFormula :expression="pair.conjugate" /> da el valor conjugado
          (el mismo residuo), porque los coeficientes del polinomio son reales.
        </p>
        <p class="pair-marks">
          <span v-for="name in pair.names" :key="name">
            <MathFormula :expression="name" />
            <span :class="pair.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ pair.ok ? ' ✔' : ' ⚠' }}</span>
          </span>
        </p>
      </div>

      <p v-if="hasResidue" class="alert alert-warning check-note">
        ⚠ La raíz es aproximada; el residuo depende de la tolerancia usada.
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

/* Comprobación: las cuatro partes de cada línea quedan alineadas en columnas
   (f(x) | sustitución | términos calculados | resultado). */
.check-grid {
  display: grid;
  grid-template-columns: repeat(4, max-content);
  column-gap: var(--space-3);
  row-gap: var(--space-3);
  align-items: baseline;
  padding-bottom: var(--space-2);
}

/* Dos renglones por raíz: f(x) | sustitución, y debajo | términos = resultado. */
.check-grid.is-stacked {
  grid-template-columns: repeat(2, max-content);
  row-gap: var(--space-1);
}

.check-grid.is-stacked > :nth-child(4n) {
  margin-bottom: var(--space-3);
}

.check-result {
  display: inline-flex;
  align-items: baseline;
  gap: var(--space-2);
  white-space: nowrap;
}

.mark {
  font-weight: var(--weight-semibold);
}

.mark-ok {
  color: var(--color-success);
}

.mark-warn {
  color: var(--color-warning);
}

.check-exact {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.complex-check {
  margin-top: var(--space-5);
}

.complex-title {
  margin: 0 0 var(--space-2);
}

.check-table {
  width: auto;
  min-width: min(100%, 360px);
}

.check-table th,
.check-table td {
  padding: var(--space-2) var(--space-3);
  text-align: left;
  white-space: nowrap;
}

.check-table td:last-child {
  text-align: right;
}

.pair-marks {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin: 0;
}

.check-note {
  margin-top: var(--space-4);
}
</style>
