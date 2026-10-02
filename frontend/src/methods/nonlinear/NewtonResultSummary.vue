<script setup>
// Información propia de Newton en el resumen del resultado: las ecuaciones,
// la función F(x) y la matriz Jacobiana simbólica, que se calcula una sola
// vez (en cada iteración sólo cambian sus valores numéricos).
import MathFormula from '../../components/MathFormula.vue'
import { symbolicSystemLatex } from './newtonFormulas'

defineProps({
  result: { type: Object, required: true },
})
</script>

<template>
  <div class="newton-summary">
    <p class="summary-caption">
      Sistema y matriz Jacobiana (variables en orden:
      <MathFormula :expression="result.variables_latex.join(',\\ ')" />)
    </p>
    <div class="formula-box summary-formula">
      <MathFormula :expression="symbolicSystemLatex(result)" display-mode />
    </div>
  </div>
</template>

<style scoped>
.newton-summary {
  margin-bottom: var(--space-4);
}

.summary-caption {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.summary-formula {
  overflow-x: auto;
}
</style>
