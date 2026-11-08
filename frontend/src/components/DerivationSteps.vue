<script setup>
// Desglose término a término de una derivada o una integral, con la regla de
// cada término y la suma final (el mismo formato de Newton y diferenciación).
// steps: { terms: [{ latex, rule }], sum_latex? }; `result`: LaTeX que se
// muestra al final si no hay suma (un solo término).
import MathFormula from './MathFormula.vue'

defineProps({
  steps: { type: Object, required: true },
  result: { type: String, default: '' },
})
</script>

<template>
  <div class="derivation-card">
    <ul class="derivation-terms">
      <li v-for="(term, t) in steps.terms" :key="t">
        <div class="derivation-formula"><MathFormula :expression="term.latex" /></div>
        <span class="derivation-rule">{{ term.rule }}</span>
      </li>
    </ul>
    <div v-if="steps.sum_latex || result" class="derivation-sum">
      <MathFormula :expression="steps.sum_latex || result" />
      <slot name="after-sum" />
    </div>
  </div>
</template>

<style scoped>
.derivation-card {
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-3);
}

.derivation-terms {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.derivation-formula {
  overflow-x: auto;
}

.derivation-rule {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.derivation-sum {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-line);
  font-weight: var(--weight-semibold);
  overflow-x: auto;
}
</style>
