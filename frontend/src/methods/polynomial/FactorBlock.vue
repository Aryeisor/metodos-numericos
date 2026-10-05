<script setup>
// Un factor del resultado de Bairstow, como sección plegable (con un botón
// propio en lugar de <details>: el contenido plegado conserva su tamaño, así
// el gráfico se dibuja bien y puede exportarse al PDF aunque esté cerrado):
//  - obtenido por Bairstow: encabezado (polinomio que se divide, r₀ y s₀),
//    tabla de iteraciones con paso a paso expandible, gráfico de convergencia
//    (ε_r y ε_s) y cierre (factor, discriminante, raíces, división final,
//    cociente y residuo);
//  - cierre directo (cociente de grado 2 o 1): sólo el cálculo directo.
import { computed, ref, watch } from 'vue'
import ConvergenceChart from '../../components/ConvergenceChart.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import BairstowIterationDetail from './BairstowIterationDetail.vue'
import SyntheticTable from './SyntheticTable.vue'
import { discriminantLatex, formatComplex, rootsLatex } from './formulas'

const PAGE_SIZE = 10

const props = defineProps({
  factor: { type: Object, required: true },
  // Iteraciones de este factor (las de result.iterations que le pertenecen).
  iterations: { type: Array, required: true },
  // Tolerancia εs en %.
  tolerance: { type: Number, required: true },
  open: { type: Boolean, default: false },
})

const isOpen = ref(props.open)
const bodyId = `factor-body-${props.factor.index}`

const isBairstow = computed(() => props.factor.method === 'bairstow')
const number = computed(() => props.factor.index + 1)
const closed = computed(() => props.factor.converged && props.factor.factor_latex)

const title = computed(() => {
  if (props.factor.method === 'lineal_directa') return 'cierre directo (grado 1)'
  if (props.factor.method === 'cuadratica_directa') return 'cierre directo (grado 2)'
  const n = props.factor.iterations_used
  return `${n} ${n === 1 ? 'iteración' : 'iteraciones'} · ${props.factor.converged ? 'convergió' : 'no convergió'}`
})

// --- Tabla paginada con detalle expandible ---------------------------------
const expanded = ref(new Set())
const page = ref(1)
watch(
  () => props.iterations,
  () => {
    expanded.value = new Set()
    page.value = 1
  }
)
const pages = computed(() => Math.max(1, Math.ceil(props.iterations.length / PAGE_SIZE)))
const pagedRows = computed(() =>
  props.iterations.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE)
)

function toggle(k) {
  const next = new Set(expanded.value)
  if (next.has(k)) next.delete(k)
  else next.add(k)
  expanded.value = next
}

const cell = (value) => (value === null || value === undefined ? '—' : formatNumber(value))

// --- Gráfico: ε_r y ε_s por separado ---------------------------------------
const chartRef = ref(null)
const series = computed(() => [
  { label: 'ε_r (%)', values: props.iterations.map((row) => row.extra.eps_r ?? null), color: '#2563eb' },
  { label: 'ε_s (%)', values: props.iterations.map((row) => row.extra.eps_s ?? null), color: '#9333ea' },
])
const toleranceLabel = computed(() => `Tolerancia εs (${formatNumber(props.tolerance)} %)`)

defineExpose({ toImage: () => chartRef.value?.toImage() ?? null })

// --- Cierre ------------------------------------------------------------------
const linearLatex = computed(() => {
  if (props.factor.method !== 'lineal_directa') return ''
  const [a1, a0] = props.factor.dividend.coefficients
  return `x = -\\frac{a_0}{a_1} = -\\frac{${latexNumber(a0)}}{${latexNumber(a1)}} = \\mathbf{${latexNumber(props.factor.roots[0].re)}}`
})
const quadraticFormLatex = computed(() => {
  if (props.factor.method !== 'cuadratica_directa') return ''
  const [a, b, c] = props.factor.dividend.coefficients
  return (
    `r = -\\frac{b}{a} = -\\frac{${latexNumber(b)}}{${latexNumber(a)}} = ${latexNumber(props.factor.r)}, \\qquad ` +
    `s = -\\frac{c}{a} = -\\frac{${latexNumber(c)}}{${latexNumber(a)}} = ${latexNumber(props.factor.s)}`
  )
})
</script>

<template>
  <section class="factor-block">
    <button
      type="button"
      class="factor-toggle"
      :aria-expanded="isOpen"
      :aria-controls="bodyId"
      @click="isOpen = !isOpen"
    >
      <span class="factor-caret" aria-hidden="true">{{ isOpen ? '▾' : '▸' }}</span>
      <span class="factor-name">Factor {{ number }}</span>
      <MathFormula v-if="factor.factor_latex" :expression="factor.factor_latex" />
      <span class="factor-meta" :class="{ 'is-failed': !factor.converged }">{{ title }}</span>
    </button>

    <div :id="bodyId" class="factor-body" :class="{ 'is-collapsed': !isOpen }">
      <p class="factor-header">
        Polinomio que se divide:
        <MathFormula :expression="`${factor.dividend.latex}`" />
        <template v-if="isBairstow">
          · valores iniciales <MathFormula :expression="`r_0 = ${latexNumber(factor.r0)},\\ s_0 = ${latexNumber(factor.s0)}`" />
        </template>
      </p>
      <p v-if="factor.note" class="factor-note">{{ factor.note }}</p>

      <!-- Cierre directo: sin iteraciones -->
      <template v-if="factor.method === 'lineal_directa'">
        <p class="sub-caption">El cociente es de grado 1: se despeja x directamente.</p>
        <div class="formula-box"><MathFormula :expression="linearLatex" display-mode /></div>
      </template>
      <template v-else-if="factor.method === 'cuadratica_directa'">
        <p class="sub-caption">
          El cociente es de grado 2: se resuelve con la fórmula cuadrática, escrito como
          <MathFormula :expression="`${latexNumber(factor.dividend.coefficients[0])} \\left(x^2 - r\\,x - s\\right)`" />
          para que se vea igual que los demás factores.
        </p>
        <div class="formula-box"><MathFormula :expression="quadraticFormLatex" display-mode /></div>
      </template>

      <!-- Bairstow: iteraciones, gráfico y paso a paso -->
      <template v-else>
        <div class="table-scroll">
          <table class="iterations-table">
            <thead>
              <tr>
                <th class="expand-col"></th>
                <th>k</th>
                <th>r</th>
                <th>s</th>
                <th>Δr</th>
                <th>Δs</th>
                <th>ε_r (%)</th>
                <th>ε_s (%)</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in pagedRows" :key="row.iteration">
                <tr>
                  <td class="expand-col">
                    <button
                      type="button"
                      class="expand-btn"
                      :aria-expanded="expanded.has(row.iteration)"
                      :title="expanded.has(row.iteration) ? 'Ocultar cálculo' : 'Ver cálculo'"
                      @click="toggle(row.iteration)"
                    >
                      {{ expanded.has(row.iteration) ? '▾' : '▸' }}
                    </button>
                  </td>
                  <td>{{ row.iteration }}</td>
                  <td>{{ cell(row.x[0]) }}</td>
                  <td>{{ cell(row.x[1]) }}</td>
                  <td>{{ cell(row.extra.delta_r) }}</td>
                  <td>{{ cell(row.extra.delta_s) }}</td>
                  <td>{{ cell(row.extra.eps_r) }}</td>
                  <td>{{ cell(row.extra.eps_s) }}</td>
                </tr>
                <tr v-if="expanded.has(row.iteration)" class="detail-row">
                  <td colspan="8">
                    <BairstowIterationDetail :row="row" :tolerance="tolerance" />
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <div v-if="pages > 1" class="pagination">
          <button type="button" class="btn btn-secondary page-btn" :disabled="page === 1" @click="page -= 1">
            ‹ Anterior
          </button>
          <span class="page-info">Página {{ page }} de {{ pages }}</span>
          <button type="button" class="btn btn-secondary page-btn" :disabled="page === pages" @click="page += 1">
            Siguiente ›
          </button>
        </div>

        <ConvergenceChart
          ref="chartRef"
          :iterations="iterations"
          :tolerance="tolerance"
          :converged="factor.converged"
          :series="series"
          y-label="Error relativo (%), escala log"
          :tolerance-label="toleranceLabel"
        />
      </template>

      <!-- Cierre del factor (Bairstow convergido o cierre cuadrático) -->
      <template v-if="closed && factor.method !== 'lineal_directa'">
        <h5 class="closure-title">Cierre del factor</h5>
        <div class="closure-grid">
          <div class="formula-box">
            <MathFormula :expression="`x^2 - r\\,x - s = ${factor.factor_latex}`" display-mode />
          </div>
          <div class="formula-box">
            <MathFormula :expression="discriminantLatex(factor.r, factor.s, factor.discriminant)" display-mode />
          </div>
        </div>
        <div class="formula-box">
          <MathFormula
            v-for="(latex, i) in rootsLatex(factor.r, factor.discriminant, factor.roots)"
            :key="i"
            :expression="latex"
            display-mode
          />
        </div>
        <p class="sub-caption">
          Raíces: <strong>{{ factor.roots.map((root) => formatComplex(root.re, root.im)).join(' ; ') }}</strong>
        </p>

        <template v-if="isBairstow">
          <p class="sub-caption">
            División sintética final, con los r y s finales (deflación):
          </p>
          <div class="formula-box"><SyntheticTable :table="factor.final_b" input="a" output="b" /></div>
          <p class="sub-caption">
            Cociente (grado {{ factor.quotient.degree }}):
            <MathFormula :expression="factor.quotient.latex" /> · residuo
            <MathFormula :expression="`b_1 = ${latexNumber(factor.residue.b1)},\\ b_0 = ${latexNumber(factor.residue.b0)}`" />
            (≈ 0)
          </p>
        </template>
      </template>
      <p v-else-if="factor.method === 'lineal_directa'" class="sub-caption">
        Raíz: <strong>{{ formatComplex(factor.roots[0].re, 0) }}</strong>
      </p>
    </div>
  </section>
</template>

<style scoped>
.factor-block {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  background: var(--color-surface);
}

.factor-block + .factor-block {
  margin-top: var(--space-3);
}

.factor-toggle {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  font: inherit;
  color: inherit;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-3);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  border-radius: var(--radius-nested);
}

.factor-toggle:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.factor-toggle[aria-expanded="true"] {
  border-bottom: 1px solid var(--color-line);
  border-radius: var(--radius-nested) var(--radius-nested) 0 0;
}

.factor-caret {
  color: var(--color-accent);
  font-size: var(--text-small);
}

/* Plegado sin display: none: el contenido conserva su ancho (los gráficos se
   dibujan con su tamaño real), pero no ocupa alto, no se ve y queda fuera del
   orden de tabulación y de los lectores de pantalla. */
.factor-body.is-collapsed {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
  visibility: hidden;
}

.factor-name {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.factor-meta {
  margin-left: auto;
  font-size: var(--text-small);
  color: var(--color-success);
}

.factor-meta.is-failed {
  color: var(--color-danger);
}

.factor-body {
  padding: var(--space-4);
  min-width: 0;
}

.factor-header,
.factor-note,
.sub-caption {
  margin: 0 0 var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.factor-note {
  color: var(--color-warning);
}

.iterations-table td,
.iterations-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.iterations-table .expand-col {
  width: 40px;
  text-align: center;
}

.expand-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-accent);
  font-size: var(--text-small);
  line-height: 1;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-control);
}

.expand-btn:hover {
  background: var(--color-accent-soft);
}

.iterations-table .detail-row td {
  background: var(--color-page);
  text-align: left;
  padding: var(--space-4);
  font-size: 0.9rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-3);
}

.page-info {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.closure-title {
  margin: var(--space-5) 0 var(--space-3);
  font-size: var(--text-card-title);
  color: var(--color-ink);
}

.closure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.formula-box {
  overflow-x: auto;
  margin-bottom: var(--space-3);
}

.formula-box :deep(.katex) {
  font-size: 1em;
}
</style>
