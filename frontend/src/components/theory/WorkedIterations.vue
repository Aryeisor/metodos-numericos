<script setup>
// Sustituciones numéricas de cada iteración del ejemplo resuelto.
//
// Cada paso es { iteration, substitutions: [latex] } (Jacobi, Gauss-Seidel,
// Punto Fijo), o bien { iteration, groups: [{ title, formulas: [latex] }] }
// cuando una iteración tiene varios sub-pasos con nombre (Newton: evaluación,
// sistema lineal, determinantes, incrementos...).
import MathFormula from '../MathFormula.vue'

defineProps({
  steps: { type: Array, required: true },
})
</script>

<template>
<div v-for="step in steps" :key="step.iteration" class="worked-step">
  <p class="worked-step-title">Iteración {{ step.iteration }}</p>
  <template v-if="step.groups">
    <div v-for="group in step.groups" :key="group.title" class="worked-group">
      <p class="worked-group-title">{{ group.title }}</p>
      <div class="formula-pair">
        <div
          v-for="(latex, i) in group.formulas"
          :key="i"
          class="formula-box theory-formula"
        >
          <MathFormula :expression="latex" display-mode />
        </div>
      </div>
    </div>
  </template>
  <div v-else class="formula-pair">
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
