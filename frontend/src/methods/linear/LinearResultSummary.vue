<script setup>
// Información propia de un sistema lineal que se muestra en el resumen del
// resultado: el reordenamiento automático de filas y la matriz que se resolvió.
import { computed } from 'vue'
import { formatNumber } from '../../utils/iterationSteps'

const props = defineProps({
  result: { type: Object, required: true },
})

const n = computed(() => props.result.solution?.length ?? 0)

// row_order[i] = fila original que quedó en la posición i (ambas 0-based).
const reorderDescription = computed(() => {
  if (!props.result.row_order) return ''
  return props.result.row_order
    .map((originalRow, position) => `fila ${originalRow + 1} → posición ${position + 1}`)
    .join(', ')
})
</script>

<template>
  <div v-if="result.reordered" class="alert alert-info">
    <strong>↻ Filas reordenadas automáticamente.</strong>
    El sistema no era diagonalmente dominante en el orden ingresado, pero se
    reordenaron las filas ({{ reorderDescription }}) para garantizar la convergencia.
    La solución es la misma; sólo cambió el orden de las ecuaciones.

    <p class="reordered-caption">Sistema que se resolvió:</p>
    <div class="table-scroll">
      <!-- A y b vienen tal cual de la respuesta: son los valores que el
           backend usó realmente, no una reconstrucción a partir del mapeo. -->
      <table class="reordered-table">
        <thead>
          <tr>
            <th class="origin-col"><span class="visually-hidden">Fila original</span></th>
            <th v-for="j in n" :key="'rh-' + j">x{{ j }}</th>
            <th></th>
            <th>b</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in result.A" :key="'rr-' + i">
            <th scope="row" class="origin-col">Fila {{ result.row_order[i] + 1 }} →</th>
            <td v-for="(value, j) in row" :key="'rv-' + j">{{ formatNumber(value) }}</td>
            <td class="eq-sign">=</td>
            <td>{{ formatNumber(result.b[i]) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* Matriz reordenada dentro del banner: mismo lenguaje visual que la tabla del
   formulario "Sistema A·x = b", pero en modo solo lectura. */
.reordered-caption {
  margin: var(--space-3) 0 var(--space-2);
  font-weight: var(--weight-semibold);
}

.reordered-table {
  background: var(--color-surface);
  width: auto;
  min-width: min(100%, 320px);
}

.reordered-table th,
.reordered-table td {
  text-align: center;
  padding: var(--space-2) var(--space-3);
  color: var(--color-ink);
  border-color: var(--color-line);
}

.reordered-table thead th {
  font-style: italic;
  color: var(--color-ink-muted);
}

.reordered-table tbody tr {
  background: var(--color-surface);
}

.reordered-table .origin-col {
  text-align: right;
  white-space: nowrap;
  font-style: normal;
  font-weight: var(--weight-semibold);
  font-size: var(--text-small);
  color: var(--color-accent);
  background: var(--color-sunken);
}

.reordered-table .eq-sign {
  border-left: none;
  border-right: none;
  color: var(--color-ink-muted);
  padding: 0 var(--space-1);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>
