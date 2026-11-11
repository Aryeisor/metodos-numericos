<script setup>
// Tabla triangular de Romberg: filas i (con su n y su h) y columnas k (nombre
// y orden del error, con tooltip). La diagonal se resalta; al pasar el cursor,
// enfocar o tocar una celda R_i,k (k ≥ 2) se resaltan las dos celdas de las
// que sale: R_i,(k−1) en verde (misma fila) y R_(i−1),(k−1) en azul (fila
// anterior), como en el paso a paso. Con field = 'errors' muestra Eₜ = I − R_i,k.
import { computed, ref, watch } from 'vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber, tableValue } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize } from '../../utils/latexFormulas'
import { cellText } from './rombergExplain'
import { columnTip } from './rombergGlossary'

const props = defineProps({
  result: { type: Object, required: true },
  field: { type: String, default: 'values' },
})

const rows = computed(() => props.result.iterations.map((s) => s.extra))
const columns = computed(() => props.result.columns)
const active = ref(null)
watch(
  () => props.result,
  () => {
    active.value = null
  }
)

const has = (row, k) => k <= row.i
const value = (row, k) => formatNumber(row[props.field][k - 1])

function cellClass(row, k) {
  if (!has(row, k)) return 'is-empty'
  const a = active.value
  return {
    'is-diagonal': k === row.i,
    'is-active': a && a.i === row.i && a.k === k,
    'is-same': a && a.k >= 2 && row.i === a.i && k === a.k - 1,
    'is-previous': a && a.k >= 2 && row.i === a.i - 1 && k === a.k - 1,
  }
}

function activate(row, k) {
  if (has(row, k)) active.value = { i: row.i, k }
}
function toggle(row, k) {
  if (active.value && active.value.i === row.i && active.value.k === k) active.value = null
  else activate(row, k)
}

const factor = (k) => 4 ** (k - 1)
// Línea bajo la tabla: de qué celdas sale la celda activa.
const origin = computed(() => {
  const a = active.value
  if (!a) return null
  if (a.k === 1) {
    return a.i === 1 ? 'R₁,₁ es el trapecio simple con n = 1.' : `${cellText(a.i, 1)} es el trapecio con n = ${2 ** (a.i - 1)}, calculado con la recurrencia.`
  }
  return null
})
const originLatex = computed(() => {
  const a = active.value
  if (!a || a.k === 1) return null
  const f = factor(a.k)
  const same = colorize(`R_{${a.i},${a.k - 1}}`, CURRENT_COLOR)
  const previous = colorize(`R_{${a.i - 1},${a.k - 1}}`, PREVIOUS_COLOR)
  return `R_{${a.i},${a.k}} = \\frac{${f}\\,${same} - ${previous}}{${f - 1}}`
})
const label = (row, k) =>
  `${cellText(row.i, k)} = ${value(row, k)}` +
  (k >= 2 ? `, sale de ${cellText(row.i, k - 1)} y ${cellText(row.i - 1, k - 1)}` : '')
</script>

<template>
  <div class="table-scroll">
    <table class="romberg-table">
      <thead>
        <tr>
          <th>i</th>
          <th>n</th>
          <th>h</th>
          <th v-for="col in columns" :key="col.k" class="col-head">
            <InfoTip :text="columnTip(col)">
              <span class="col-name">k = {{ col.k }} · {{ col.name }}</span>
              <span class="col-order">{{ col.order_text }}</span>
            </InfoTip>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.i">
          <td>{{ row.i }}</td>
          <td>{{ row.n }}</td>
          <td class="h-cell" :title="tableValue(row.h).title">{{ tableValue(row.h).text }}</td>
          <td
            v-for="col in columns"
            :key="col.k"
            :class="cellClass(row, col.k)"
            :tabindex="has(row, col.k) ? 0 : undefined"
            :aria-label="has(row, col.k) ? label(row, col.k) : undefined"
            @mouseenter="activate(row, col.k)"
            @focus="activate(row, col.k)"
            @click="toggle(row, col.k)"
          >
            <template v-if="has(row, col.k)">{{ value(row, col.k) }}</template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <p class="origin" aria-live="polite">
    <template v-if="originLatex">
      <MathFormula :expression="originLatex" />
      <span>: en verde la celda de la misma fila y en azul la de la fila anterior.</span>
    </template>
    <template v-else-if="origin">{{ origin }}</template>
    <template v-else>Toca o pasa el cursor sobre una celda para ver de qué celdas sale.</template>
  </p>
</template>

<style scoped>
.romberg-table td,
.romberg-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.col-head .col-name,
.col-head .col-order {
  display: block;
}

.col-order {
  font-weight: normal;
  color: var(--color-ink-muted);
}

.romberg-table td[tabindex] {
  cursor: pointer;
}

.romberg-table td[tabindex]:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

/* Las celdas sobre la diagonal no existen: invisibles (sin bordes, fondo de
   fila alterna ni texto). */
.romberg-table td.is-empty {
  background: var(--color-surface);
  border-style: hidden;
}

.romberg-table td.is-diagonal {
  background: var(--color-cell-diagonal);
  box-shadow: inset 0 0 0 1px var(--color-cell-diagonal-line);
  font-weight: var(--weight-semibold);
}

.romberg-table td.is-same {
  background: var(--color-cell-same);
  color: var(--color-value-new);
  font-weight: var(--weight-semibold);
}

.romberg-table td.is-previous {
  background: var(--color-cell-previous);
  color: var(--color-value-old);
  font-weight: var(--weight-semibold);
}

.romberg-table td.is-active {
  box-shadow: inset 0 0 0 2px var(--color-accent);
}

.origin {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  overflow-x: auto;
}
</style>
