<script setup>
// Tabla de refinamiento del modo función, paginada como ResultsTable, con el
// paso a paso expandible de cada fila. Con `block` (una regla de Simpson:
// result.rules[i]) muestra sus filas, con S en lugar de T.
import { computed, ref, watch } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import TrapezoidStepDetail from './TrapezoidStepDetail.vue'
import { tinyErrorNote } from './explain'
import { boundMark, cell, percent } from './formulas'
import { refinementColumns, simpsonWords } from './glossary'
import { simpsonRowSteps, weightReason } from './simpsonExplain'

const PAGE_SIZE = 10

const props = defineProps({
  result: { type: Object, required: true },
  block: { type: Object, default: null },
})

const items = computed(() =>
  props.block ? props.block.rows.map((row) => ({ k: row.k, item: row })) : props.result.iterations.map((s) => ({ k: s.iteration, item: s.extra }))
)
const rows = computed(() => items.value.map((r, i) => ({ ...r, previous: i > 0 ? items.value[i - 1].item : null })))
const valueKey = computed(() => (props.block ? 'S' : 'T'))
const showTrue = computed(() => props.result.integral.value !== null)
const showApprox = computed(() => (props.block ? props.result.mean_fourth : props.result.mean_second) !== null)
const reference = computed(() => props.result.integral.kind === 'reference')
const headers = computed(() =>
  refinementColumns({
    showTrue: showTrue.value,
    showApprox: showApprox.value,
    reference: reference.value,
    ...(props.block ? { words: simpsonWords(props.block.rule.key) } : {}),
  })
)
const customSteps = (row) =>
  props.block ? simpsonRowSteps(props.result, props.block.rule, row.item, row.k, row.previous) : null
const reason = computed(() => (props.block ? (i, n) => weightReason(props.block.rule, i, n) : null))
// Filas donde Eₜ se ve 0 pero εₜ no: una nota debajo de la tabla.
const tinyRows = computed(() =>
  rows.value.filter((r) => tinyErrorNote(r.item, reference.value)).map((r) => r.k)
)
const tinyExample = computed(() => {
  const k = tinyRows.value[0]
  return k ? tinyErrorNote(rows.value[k - 1].item, reference.value) : null
})

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
const columns = computed(() => 7 + (showTrue.value ? 4 : 0) + (showApprox.value ? 1 : 0))

function toggle(k) {
  const next = new Set(expanded.value)
  if (next.has(k)) next.delete(k)
  else next.add(k)
  expanded.value = next
}
</script>

<template>
  <div class="table-scroll detail-scroll">
    <table class="iterations-table">
      <thead>
        <tr>
          <th class="expand-col"></th>
          <th v-for="col in headers" :key="col.key">
            <InfoTip :text="col.text">{{ col.label }}</InfoTip>
          </th>
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
            <td>{{ row.item.n }}</td>
            <td class="h-cell">
              <MathFormula v-if="!row.item.h.exact" :expression="row.item.h.latex" />
              <template v-else>{{ row.item.h.text }}</template>
            </td>
            <td>{{ cell(row.item[valueKey]) }}</td>
            <td>{{ cell(row.item.estimated_error) }}</td>
            <td v-if="showTrue">{{ cell(row.item.true_error) }}</td>
            <td v-if="showTrue">{{ percent(row.item.relative_error) }}</td>
            <td v-if="showApprox">{{ cell(row.item.approx_error) }}</td>
            <td>{{ row.item.bound === null ? 'no disponible' : cell(row.item.bound) }}</td>
            <td v-if="showTrue">{{ cell(row.item.ratio) }}</td>
            <td v-if="showTrue" class="mark-cell">
              <span :class="row.item.within_bound ? 'mark mark-ok' : 'mark mark-warn'">{{ boundMark(row.item) }}</span>
              <sup v-if="row.item.by_rounding" class="rounding-mark" title="Sólo dentro del margen de redondeo R">R</sup>
            </td>
          </tr>
          <tr v-if="expanded.has(row.k)" class="detail-row">
            <td :colspan="columns">
              <div class="detail-inner">
                <TrapezoidStepDetail
                  :result="result"
                  :row="row.item"
                  :k="row.k"
                  :previous="row.previous"
                  :custom-steps="customSteps(row)"
                  :weight-reason="reason"
                />
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>

  <small v-if="tinyExample" class="table-note">
    Filas {{ tinyRows.join(', ') }}: {{ tinyExample }}
  </small>

  <div v-if="pages > 1" class="pagination">
    <button type="button" class="btn btn-secondary page-btn" :disabled="page === 1" @click="page -= 1">
      ‹ Anterior
    </button>
    <span class="page-info">Página {{ page }} de {{ pages }}</span>
    <button type="button" class="btn btn-secondary page-btn" :disabled="page === pages" @click="page += 1">
      Siguiente ›
    </button>
  </div>

  <GlossaryBlock
    title="¿Qué significa cada columna?"
    :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))"
  />
</template>

<style scoped>
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

/* El paso a paso ocupa el ancho visible, no el de la tabla: se lee sin desplazarse a 390 px. */
.detail-scroll {
  container-type: inline-size;
}

.detail-inner {
  position: sticky;
  left: var(--space-4);
  width: calc(100cqw - 2 * var(--space-4));
}

.table-note {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
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
