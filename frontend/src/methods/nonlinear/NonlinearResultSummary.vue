<script setup>
// Información propia de un sistema no lineal en el resumen del resultado: el
// despeje x_i = g_i(...) que se obtuvo automáticamente de cada ecuación y que
// es lo que realmente se iteró.
import MathFormula from '../../components/MathFormula.vue'
import { isolationLatex } from './formulas'

defineProps({
  result: { type: Object, required: true },
})
</script>

<template>
  <div class="isolations">
    <p class="isolations-caption">Despeje automático de cada ecuación</p>
    <div class="table-scroll">
      <table class="isolations-table">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col">Ecuación ingresada</th>
            <th scope="col">Función de iteración</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(equation, i) in result.equations" :key="i">
            <th scope="row">{{ i + 1 }}</th>
            <td><MathFormula :expression="equation.equation_latex" /></td>
            <td><MathFormula :expression="isolationLatex(result, i)" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.isolations {
  margin-bottom: var(--space-4);
}

.isolations-caption {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.isolations-table th,
.isolations-table td {
  text-align: left;
  vertical-align: middle;
  padding: var(--space-2) var(--space-3);
  white-space: nowrap;
}

.isolations-table tbody th {
  width: 2rem;
  color: var(--color-ink-muted);
  font-weight: var(--weight-semibold);
}

.isolations-table tbody tr:nth-child(even) {
  background: transparent;
}
</style>
