<script setup>
// Tabla de convergencia de la diagonal de Romberg, con tooltip en cada
// encabezado y la leyenda de las columnas debajo.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import { tinyErrorNote } from './explain'
import { cell, percent } from './formulas'
import { convergenceColumns } from './rombergGlossary'

const props = defineProps({
  result: { type: Object, required: true },
})

const rows = computed(() => props.result.iterations.map((s) => s.extra))
const isTable = computed(() => props.result.mode === 'table')
const showTrue = computed(() => props.result.integral?.value !== null && props.result.integral?.value !== undefined)
const reference = computed(() => props.result.integral?.kind === 'reference')
const headers = computed(() => convergenceColumns({ showTrue: showTrue.value, reference: reference.value, isTable: isTable.value }))
const tinyRows = computed(() => rows.value.filter((r) => tinyErrorNote(r, reference.value)).map((r) => r.i))
</script>

<template>
  <div class="table-scroll">
    <table class="convergence-table">
      <thead>
        <tr>
          <th v-for="col in headers" :key="col.key">
            <InfoTip :text="col.text">{{ col.label }}</InfoTip>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.i">
          <td>{{ row.i }}</td>
          <td>{{ row.n }}</td>
          <td>{{ row.evaluations }}</td>
          <td>{{ cell(row.values[0]) }}</td>
          <td class="best">{{ cell(row.best) }}</td>
          <td>{{ cell(row.estimated_error) }}</td>
          <td>{{ percent(row.approx_error) }}</td>
          <td v-if="showTrue">{{ cell(row.true_error) }}</td>
          <td v-if="showTrue">{{ percent(row.relative_error) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <small v-if="tinyRows.length" class="table-note">
    Filas {{ tinyRows.join(', ') }}: {{ tinyErrorNote(rows[tinyRows[0] - 1], reference) }}
  </small>
  <GlossaryBlock title="¿Qué significa cada columna?" :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))" />
</template>

<style scoped>
.convergence-table td,
.convergence-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.convergence-table td.best {
  background: var(--color-cell-diagonal);
  font-weight: var(--weight-semibold);
}

.table-note {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
