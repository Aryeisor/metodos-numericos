<script setup>
// Tabla de refinamiento de una fórmula (modo función), paginada como
// ResultsTable, con el paso a paso expandible de cada fila.
import { computed, ref, watch } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import DifferenceStepDetail from './DifferenceStepDetail.vue'
import { boundMark, cell, stepSizeLatex, stepText } from './formulas'

const PAGE_SIZE = 10

const props = defineProps({
  result: { type: Object, required: true },
  formula: { type: Object, required: true },
})

const rows = computed(() =>
  props.result.iterations.map((step, i) => ({
    k: step.iteration,
    h: step.extra.h,
    item: step.extra[props.formula.key],
    previous: i > 0 ? props.result.iterations[i - 1].extra[props.formula.key] : null,
  }))
)
const h0 = computed(() => props.result.iterations[0].extra.h)
const showReal = computed(() => props.result.differentiable)

const expanded = ref(new Set())
const page = ref(1)
watch(
  () => props.result,
  () => {
    expanded.value = new Set()
    page.value = 1
  }
)
const pages = computed(() => Math.max(1, Math.ceil(rows.value.length / PAGE_SIZE)))
const pagedRows = computed(() => rows.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE))
const columns = computed(() => (showReal.value ? 9 : 7))

function toggle(k) {
  const next = new Set(expanded.value)
  if (next.has(k)) next.delete(k)
  else next.add(k)
  expanded.value = next
}
</script>

<template>
  <div class="refinement">
    <h5 class="table-title">
      {{ formula.name }}: <MathFormula :expression="formula.formula_latex" />
    </h5>
    <div class="table-scroll">
      <table class="iterations-table">
        <thead>
          <tr>
            <th class="expand-col"></th>
            <th>k</th>
            <th>h</th>
            <th>D</th>
            <th>Error estimado</th>
            <th v-if="showReal">Error real</th>
            <th>Cota</th>
            <th v-if="showReal">Razón</th>
            <th v-if="showReal" title="Error real ≤ cota">≤ cota</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="row in pagedRows" :key="row.k">
            <tr>
              <td class="expand-col">
                <button
                  type="button"
                  class="expand-btn"
                  :aria-expanded="expanded.has(row.k)"
                  :title="expanded.has(row.k) ? 'Ocultar cálculo' : 'Ver cálculo'"
                  @click="toggle(row.k)"
                >
                  {{ expanded.has(row.k) ? '▾' : '▸' }}
                </button>
              </td>
              <td>{{ row.k }}</td>
              <td class="h-cell">
                <MathFormula v-if="!row.h.exact" :expression="row.h.latex" />
                <template v-else>{{ stepText(row.h) }}</template>
              </td>
              <td>{{ cell(row.item.D) }}</td>
              <td>{{ cell(row.item.estimated_error) }}</td>
              <td v-if="showReal">{{ cell(row.item.real_error) }}</td>
              <td>{{ row.item.bound === null ? 'no disponible' : cell(row.item.bound) }}</td>
              <td v-if="showReal">{{ cell(row.item.ratio) }}</td>
              <td v-if="showReal" class="mark-cell">
                <span :class="row.item.within_bound ? 'mark mark-ok' : 'mark mark-warn'">{{ boundMark(row.item) }}</span>
                <sup v-if="row.item.by_rounding" class="rounding-mark" title="Sólo gracias al redondeo R">R</sup>
              </td>
            </tr>
            <tr v-if="expanded.has(row.k)" class="detail-row">
              <td :colspan="columns">
                <DifferenceStepDetail
                  :formula="formula"
                  :item="row.item"
                  :label="row.k"
                  :step-line="stepSizeLatex(row.k, row.h, h0)"
                  :h="row.h"
                  :template="result.function.template"
                  :exact="result.exact"
                  :exact-source="result.verification.substitution"
                  :derivative-latex="result.function.derivative.latex"
                  :bound-derivative-latex="result.function.higher_derivatives[formula.bound_derivative]?.latex ?? null"
                  :previous="row.previous"
                  :samples="result.sampling_points"
                />
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
  </div>
</template>

<style scoped>
.refinement + .refinement {
  margin-top: var(--space-6);
}

.table-title {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
  margin: 0 0 var(--space-3);
  font-size: var(--text-card-title);
  color: var(--color-ink);
}

.iterations-table td,
.iterations-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.iterations-table .expand-col {
  width: 40px;
  text-align: center;
}

.mark-cell {
  text-align: center !important;
}

.rounding-mark {
  margin-left: 2px;
  color: var(--color-ink-muted);
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
  white-space: normal;
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
</style>
