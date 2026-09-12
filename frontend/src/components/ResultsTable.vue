<script setup>
import { computed, ref, watch } from 'vue'
import ConvergenceChart from './ConvergenceChart.vue'
import MathFormula from './MathFormula.vue'
import { buildIterationDetail, formatNumber } from '../utils/iterationSteps'
import {
  errorFormulaLatex,
  errorResultLatex,
  errorSubstitutionLatex,
  generalFormulaLatex,
  substitutionLatex,
} from '../utils/latexFormulas'
import { exportResultToPdf } from '../utils/exportPdf'

const PAGE_SIZE = 10

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, default: null },
})

const n = computed(() => props.result.solution?.length ?? 0)
const methodLabel = computed(() =>
  props.result.method === 'gauss-seidel' ? 'Gauss-Seidel' : 'Jacobi'
)
const isGaussSeidel = computed(() => props.result.method === 'gauss-seidel')
const canExplain = computed(() => Boolean(props.system))

const expanded = ref(new Set())
const currentPage = ref(1)
const chartRef = ref(null)

watch(
  () => props.result,
  () => {
    currentPage.value = 1
    expanded.value = new Set()
  }
)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.result.iterations.length / PAGE_SIZE))
)

// Cada fila conserva su índice absoluto para poder reconstruir su detalle.
const pagedIterations = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return props.result.iterations
    .slice(start, start + PAGE_SIZE)
    .map((row, offset) => ({ row, index: start + offset }))
})

// Lista de páginas con ventana alrededor de la actual y '…' cuando hay muchas.
const visiblePages = computed(() => {
  const total = totalPages.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const current = currentPage.value
  const pages = new Set([1, total, current])
  for (let d = 1; d <= 2; d++) {
    if (current - d > 1) pages.add(current - d)
    if (current + d < total) pages.add(current + d)
  }

  const sorted = [...pages].sort((a, b) => a - b)
  const withGaps = []
  sorted.forEach((page, i) => {
    if (i > 0 && page - sorted[i - 1] > 1) withGaps.push('…')
    withGaps.push(page)
  })
  return withGaps
})

const lastIteration = computed(
  () => props.result.iterations[props.result.iterations.length - 1] ?? null
)

function goToPage(page) {
  if (typeof page !== 'number') return
  currentPage.value = Math.min(Math.max(1, page), totalPages.value)
}

const exporting = ref(false)

function handleExportPdf() {
  exporting.value = true
  try {
    exportResultToPdf({
      result: props.result,
      system: props.system,
      chartImage: chartRef.value?.toImage() ?? null,
    })
  } finally {
    exporting.value = false
  }
}

function toggleRow(iteration) {
  const next = new Set(expanded.value)
  if (next.has(iteration)) next.delete(iteration)
  else next.add(iteration)
  expanded.value = next
}

function detailFor(index) {
  return buildIterationDetail({
    A: props.system.A,
    b: props.system.b,
    x0: props.system.x0,
    method: props.result.method,
    iterations: props.result.iterations,
    index,
  })
}

</script>

<template>
  <div class="results">
    <div class="summary">
      <div class="summary-header">
        <h3>Resultado ({{ methodLabel }})</h3>
        <div class="summary-actions">
          <span class="badge" :class="result.converged ? 'badge-success' : 'badge-danger'">
            {{ result.converged ? 'Convergió' : 'No convergió' }}
          </span>
          <button
            v-if="system"
            type="button"
            class="btn btn-outline"
            :disabled="exporting"
            @click="handleExportPdf"
          >
            Exportar PDF
          </button>
        </div>
      </div>

      <div v-for="(w, idx) in result.warnings" :key="idx" class="alert alert-warning">
        ⚠ {{ w }}
      </div>

      <p class="meta">
        Iteraciones ejecutadas: <strong>{{ result.iterations_used }}</strong>
      </p>

      <div class="solution-grid">
        <div v-for="(value, i) in result.solution" :key="i" class="solution-item">
          <span class="solution-label">x{{ i + 1 }}</span>
          <span class="solution-value">{{ formatNumber(value) }}</span>
        </div>
      </div>
    </div>

    <ConvergenceChart
      ref="chartRef"
      :iterations="result.iterations"
      :tolerance="system ? system.tolerance : null"
      :converged="result.converged"
    />

    <h4 class="iterations-title">Detalle de iteraciones</h4>

    <div v-if="!result.converged && lastIteration" class="alert alert-danger divergence-summary">
      <strong>⚠ El método no convergió.</strong>
      <span>
        Iteración final: <strong>{{ lastIteration.iteration }}</strong> · Error final:
        <strong>{{
          lastIteration.error === null ? '—' : formatNumber(lastIteration.error)
        }}</strong>
        · Tolerancia solicitada:
        <strong>{{ system ? formatNumber(system.tolerance) : '—' }}</strong>
      </span>
    </div>

    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th v-if="canExplain" class="expand-col"></th>
            <th>Iter.</th>
            <th v-for="i in n" :key="'th-' + i">x{{ i }}</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="{ row, index: idx } in pagedIterations" :key="row.iteration">
            <tr>
              <td v-if="canExplain" class="expand-col">
                <button
                  type="button"
                  class="expand-btn"
                  :aria-expanded="expanded.has(row.iteration)"
                  :title="expanded.has(row.iteration) ? 'Ocultar cálculo' : 'Ver cálculo'"
                  @click="toggleRow(row.iteration)"
                >
                  {{ expanded.has(row.iteration) ? '▾' : '▸' }}
                </button>
              </td>
              <td>{{ row.iteration }}</td>
              <td v-for="(value, i) in row.x" :key="'v-' + i">{{ formatNumber(value) }}</td>
              <td>{{ row.error === null ? '—' : formatNumber(row.error) }}</td>
            </tr>

            <tr v-if="canExplain && expanded.has(row.iteration)" class="detail-row">
              <td :colspan="n + 3">
                <div class="detail">
                  <div class="detail-block">
                    <span class="detail-caption">Fórmula ({{ methodLabel }})</span>
                    <div class="formula-box">
                      <MathFormula :expression="generalFormulaLatex(result.method)" display-mode />
                    </div>
                    <p class="detail-hint">
                      <span class="legend-prev">■</span> valores de la iteración anterior
                      <template v-if="isGaussSeidel">
                        · <span class="legend-current">■</span> valores ya recalculados en esta
                        misma iteración
                      </template>
                    </p>
                  </div>

                  <div class="detail-block">
                    <span class="detail-caption">Sustitución numérica</span>
                    <div class="substitution-grid" :class="{ 'wide-formulas': n >= 4 }">
                      <div
                        v-for="v in detailFor(idx).variables"
                        :key="v.index"
                        class="substitution-card"
                      >
                        <MathFormula
                          :expression="substitutionLatex(v, row.iteration)"
                          display-mode
                        />
                      </div>
                    </div>
                  </div>

                  <div class="detail-block">
                    <span class="detail-caption">Error de la iteración</span>
                    <div class="error-grid">
                      <div class="error-card">
                        <MathFormula :expression="errorFormulaLatex()" display-mode />
                      </div>
                      <div class="error-card">
                        <MathFormula
                          :expression="errorSubstitutionLatex(detailFor(idx))"
                          display-mode
                        />
                      </div>
                      <div class="error-card">
                        <MathFormula
                          :expression="errorResultLatex(detailFor(idx))"
                          display-mode
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button
        type="button"
        class="btn btn-secondary page-btn"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        ‹ Anterior
      </button>

      <template v-for="(page, i) in visiblePages" :key="'p-' + i">
        <span v-if="page === '…'" class="page-gap">…</span>
        <button
          v-else
          type="button"
          class="btn page-btn"
          :class="page === currentPage ? 'btn-primary' : 'btn-secondary'"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
      </template>

      <button
        type="button"
        class="btn btn-secondary page-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Siguiente ›
      </button>

      <span class="page-info">
        Mostrando {{ pagedIterations.length }} de {{ result.iterations.length }} iteraciones
      </span>
    </div>
  </div>
</template>

<style scoped>
.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.summary-header h3 {
  margin: 0;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.solution-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
}

.solution-item {
  background: #eef4ff;
  border-radius: 8px;
  padding: 8px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 90px;
}

.solution-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.solution-value {
  font-weight: 700;
  font-size: 1rem;
}

.iterations-title {
  margin: 28px 0 10px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.expand-col {
  width: 34px;
  text-align: center;
}

.expand-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-primary);
  font-size: 0.9rem;
  padding: 2px 6px;
  border-radius: 4px;
}

.expand-btn:hover {
  background: #eef4ff;
}

.detail-row td {
  background: #fafbfc;
  text-align: left;
  padding: 14px 16px;
}

/* Las etiquetas conservan la tipografía de la app; las fórmulas usan la fuente
   matemática propia de KaTeX (no se sobrescribe font-family en sus contenedores). */
.detail-caption {
  font-weight: 700;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  display: block;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-block {
  margin-bottom: 18px;
}

.detail-block:last-child {
  margin-bottom: 0;
}

.formula-box {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 16px;
  overflow-x: auto;
}

.detail-hint {
  margin: 8px 0 0;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.legend-prev {
  color: #2563eb;
}

.legend-current {
  color: #15803d;
}

/* Dos columnas en escritorio y una sola en pantallas angostas. El min() evita
   que la columna quede más ancha que el contenedor en móvil. */
.substitution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: 12px;
}

/* Con 4 o más variables la sustitución es demasiado larga para dos columnas. */
.substitution-grid.wide-formulas {
  grid-template-columns: 1fr;
}

.substitution-card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 14px 16px;
  overflow-x: auto;
}

/* Los tres pasos del error son encadenados (fórmula → sustitución → resultado):
   se apilan a ancho completo porque son expresiones largas. */
.error-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 16px;
  overflow-x: auto;
}

.substitution-card :deep(.katex),
.error-card :deep(.katex) {
  font-size: 1em;
}

.divergence-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.pagination {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
}

.page-btn {
  padding: 5px 11px;
  font-size: 0.85rem;
}

.page-gap {
  color: var(--color-text-muted);
  padding: 0 2px;
}

.page-info {
  margin-left: auto;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
</style>
