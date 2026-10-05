<script setup>
// Tabla de división sintética como se escribe a mano: una columna por
// potencia y cuatro filas (entrada, r·(anterior), s·(dos atrás), resultado).
// Las casillas que no existen quedan vacías; la que no se calcula (c₀) lleva
// «—» y una nota.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'

const props = defineProps({
  // { coefficients, r_terms, s_terms, result }, listas descendentes.
  table: { type: Object, required: true },
  // Letra de la fila de entrada y de la de resultado: "a"/"b" o "b"/"c".
  input: { type: String, required: true },
  output: { type: String, required: true },
})

const degree = computed(() => props.table.coefficients.length - 1)
const powers = computed(() => props.table.coefficients.map((_, p) => degree.value - p))
const skipsLast = computed(() => props.table.result[props.table.result.length - 1] === null)

const rows = computed(() => [
  { label: `${props.input}_i`, values: props.table.coefficients, kind: 'input' },
  { label: `r\\, ${props.output}_{i+1}`, values: props.table.r_terms, kind: 'term' },
  { label: `s\\, ${props.output}_{i+2}`, values: props.table.s_terms, kind: 'term' },
  { label: `${props.output}_i`, values: props.table.result, kind: 'result' },
])

function cell(row, p) {
  const value = row.values[p]
  if (value !== null && value !== undefined) return formatNumber(value)
  // c₀: existe la columna pero no se calcula.
  if (row.kind === 'result' && skipsLast.value && p === row.values.length - 1) return '—'
  return ''
}
</script>

<template>
  <div class="table-scroll">
    <table class="synthetic-table">
      <thead>
        <tr>
          <th scope="col"></th>
          <th v-for="power in powers" :key="power" scope="col">
            <MathFormula :expression="power === 0 ? 'x^0' : power === 1 ? 'x' : `x^{${power}}`" />
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.label" :class="`row-${row.kind}`">
          <th scope="row"><MathFormula :expression="row.label" /></th>
          <td v-for="(power, p) in powers" :key="power">{{ cell(row, p) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <p v-if="skipsLast" class="table-footnote">
    <MathFormula :expression="`${output}_0`" /> no se calcula: Bairstow no lo usa.
  </p>
</template>

<style scoped>
.synthetic-table {
  width: auto;
  min-width: min(100%, 360px);
}

.synthetic-table th,
.synthetic-table td {
  padding: var(--space-1) var(--space-3);
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.synthetic-table thead th {
  text-align: center;
  color: var(--color-ink-muted);
}

.synthetic-table tbody th {
  text-align: left;
  background: var(--color-sunken);
}

.synthetic-table tbody tr {
  background: var(--color-surface);
}

.synthetic-table .row-term td {
  color: var(--color-ink-muted);
}

/* La fila del resultado se separa con una línea, como bajo la raya a mano. */
.synthetic-table .row-result td,
.synthetic-table .row-result th {
  border-top: 2px solid var(--color-line-strong);
  font-weight: var(--weight-semibold);
}

.table-footnote {
  margin: var(--space-1) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
