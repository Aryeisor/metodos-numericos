<script setup>
// Vista genérica del detalle del resultado: resumen, gráfico de convergencia y
// tabla paginada de iteraciones. La solución, el estado y los botones van en
// la tarjeta de respuesta (ResultAnswer). No asume que la entrada sea una
// matriz: lo propio de cada categoría llega por slots.
//
// Slots:
//   summary                         bloque extra en el resumen (ej. reordenamiento)
//   before-iterations               sección fija entre el gráfico y la tabla de
//                                   iteraciones, para lo que no cambia de una
//                                   iteración a otra (ej. el Jacobiano de Newton)
//   iteration-detail { index, row } detalle expandible de una iteración; si no
//                                   se provee, la tabla no muestra el botón de expandir
//   after-iterations                sección final, después de la tabla de iteraciones
//                                   (ej. la comprobación de los métodos lineales)
import { computed, ref, useSlots, watch } from 'vue'
import ConvergenceChart from './ConvergenceChart.vue'
import { formatNumber } from '../utils/iterationSteps'

const PAGE_SIZE = 10

const props = defineProps({
  result: { type: Object, required: true },
  methodName: { type: String, required: true },
  tolerance: { type: Number, default: null },
})
const emit = defineEmits(['export-pdf'])
const slots = useSlots()

// Nombres de las incógnitas en el orden de la solución y de cada iteración.
const variables = computed(
  () => props.result.variables ?? props.result.solution.map((_, i) => `x${i + 1}`)
)
const canExplain = computed(() => Boolean(slots['iteration-detail']))

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

function handleExportPdf() {
  emit('export-pdf', chartRef.value?.toImage() ?? null)
}
// El botón de PDF está en la tarjeta de respuesta (SolverView).
defineExpose({ exportPdf: handleExportPdf })

function toggleRow(iteration) {
  const next = new Set(expanded.value)
  if (next.has(iteration)) next.delete(iteration)
  else next.add(iteration)
  expanded.value = next
}
</script>

<template>
  <div class="results">
    <!-- Sin reordenamiento ni advertencias queda vacío y no ocupa lugar. -->
    <div class="summary">
      <slot name="summary" />
      <div v-for="(w, idx) in result.warnings" :key="idx" class="alert alert-warning">⚠ {{ w }}</div>
    </div>

    <ConvergenceChart
      ref="chartRef"
      :iterations="result.iterations"
      :tolerance="tolerance"
      :converged="result.converged"
    />

    <slot name="before-iterations" />

    <h4 class="iterations-title">Detalle de iteraciones</h4>

    <div v-if="!result.converged && lastIteration" class="alert alert-danger divergence-summary">
      <strong>⚠ El método no convergió.</strong>
      <span>
        Iteración final: <strong>{{ lastIteration.iteration }}</strong> · Error final:
        <strong>{{
          lastIteration.error === null ? '—' : formatNumber(lastIteration.error)
        }}</strong>
        · Tolerancia solicitada:
        <strong>{{ tolerance !== null ? formatNumber(tolerance) : '—' }}</strong>
      </span>
    </div>

    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th v-if="canExplain" class="expand-col"></th>
            <th>Iter.</th>
            <th v-for="name in variables" :key="'th-' + name">{{ name }}</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="{ row, index } in pagedIterations" :key="row.iteration">
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
              <td :colspan="variables.length + 3">
                <slot name="iteration-detail" :index="index" :row="row" />
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

    <slot name="after-iterations" />
  </div>
</template>

<style scoped>
.summary:empty {
  display: none;
}

.iterations-title {
  margin: var(--space-6) 0 var(--space-3);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
  font-size: var(--text-subsection);
  color: var(--color-ink);
}

.expand-col {
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
  transition: background-color var(--transition-fast);
}

.expand-btn:hover {
  background: var(--color-accent-soft);
}

/* font-size fijo: KaTeX se dimensiona en em, y así las fórmulas del paso a
   paso conservan el tamaño que tenían antes de la escala tipográfica. */
.detail-row td {
  background: var(--color-page);
  text-align: left;
  padding: var(--space-4);
  font-size: 0.9rem;
  line-height: var(--leading-body);
}

.divergence-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-3);
}

.pagination {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-1);
  margin-top: var(--space-4);
}

.page-btn {
  min-width: 34px;
  justify-content: center;
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-small);
}

.page-gap {
  color: var(--color-ink-muted);
  padding: 0 var(--space-1);
}

.page-info {
  margin-left: auto;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
