<script setup>
// Sustituciones numéricas de cada iteración del ejemplo resuelto.
import MathFormula from '../../../components/MathFormula.vue'

defineProps({
  steps: { type: Array, required: true },
})
</script>

<template>
<div v-for="step in steps" :key="step.iteration" class="worked-step">
  <p class="worked-step-title">Iteración {{ step.iteration }}</p>
  <div class="formula-pair">
    <div
      v-for="(latex, i) in step.substitutions"
      :key="i"
      class="formula-box theory-formula"
    >
      <MathFormula :expression="latex" display-mode />
    </div>
  </div>
</div>
</template>
