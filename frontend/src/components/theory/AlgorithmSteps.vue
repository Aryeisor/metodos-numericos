<script setup>
// Pasos del algoritmo como tarjetas numeradas. Cada paso: { title, body },
// donde body mezcla texto y fórmulas { m } que se renderizan en línea.
import MathFormula from '../MathFormula.vue'

defineProps({
  steps: { type: Array, required: true },
})
</script>

<template>
<ol class="steps">
  <li v-for="(step, i) in steps" :key="i" class="step">
    <span class="step-number" aria-hidden="true">{{ i + 1 }}</span>
    <h4 class="step-title">{{ step.title }}</h4>
    <p class="step-text">
      <template v-for="(part, j) in step.body" :key="j">
        <MathFormula v-if="part.m" :expression="part.m" /><template v-else>{{
          part
        }}</template>
      </template>
    </p>
  </li>
</ol>
</template>
