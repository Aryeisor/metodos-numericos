<script setup>
// Detalle expandible de una iteración de Punto Fijo: fórmula secuencial,
// sustitución de cada x_i = g_i(...) indicando qué valores son nuevos (de esta
// iteración) y cuáles de la anterior, y cálculo del error.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import {
  errorFormulaLatex,
  errorResultLatex,
  errorSubstitutionLatex,
} from '../../utils/latexFormulas'
import { errorDetail, generalFormulaLatex, substitutionLatex } from './formulas'

const props = defineProps({
  result: { type: Object, required: true },
  system: { type: Object, required: true },
  index: { type: Number, required: true },
  methodName: { type: String, required: true },
})

const row = computed(() => props.result.iterations[props.index])
// Si un valor salió no real, sólo se evaluaron las g_i hasta esa variable.
const evaluated = computed(() => row.value.extra.inputs.map((_, i) => i))
const failed = computed(() => row.value.error === null)
const n = computed(() => props.result.variables.length)
const detail = computed(() => errorDetail(props.result, props.index))
</script>

<template>
  <div class="detail">
    <div class="detail-block">
      <span class="detail-caption">Fórmula ({{ methodName }})</span>
      <div class="formula-box">
        <MathFormula :expression="generalFormulaLatex()" display-mode />
      </div>
      <p class="detail-hint">
        <span class="legend-current">■</span> valores ya recalculados en esta misma iteración
        · <span class="legend-prev">■</span> valores de la iteración anterior
      </p>
    </div>

    <div class="detail-block">
      <span class="detail-caption">Sustitución numérica</span>
      <div class="substitution-grid" :class="{ 'wide-formulas': n >= 3 }">
        <div v-for="i in evaluated" :key="i" class="substitution-card">
          <MathFormula :expression="substitutionLatex(result, index, i)" display-mode />
        </div>
      </div>
    </div>

    <div class="detail-block">
      <span class="detail-caption">Error de la iteración</span>
      <div v-if="failed" class="alert alert-danger failure-note">
        No se calcula el error: un valor de esta iteración no es un número real finito,
        así que el método se detuvo aquí.
      </div>
      <div v-else class="error-grid">
        <div class="error-card">
          <MathFormula :expression="errorFormulaLatex()" display-mode />
        </div>
        <div class="error-card">
          <MathFormula :expression="errorSubstitutionLatex(detail)" display-mode />
        </div>
        <div class="error-card">
          <MathFormula :expression="errorResultLatex(detail)" display-mode />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Mismo aspecto que el detalle de los sistemas lineales. */
.detail-caption {
  font-weight: var(--weight-semibold);
  font-size: var(--text-small);
  color: var(--color-ink);
  display: block;
  margin-bottom: var(--space-2);
}

.detail-block {
  margin-bottom: var(--space-5);
}

.detail-block:last-child {
  margin-bottom: 0;
}

.detail-hint {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.legend-prev {
  color: #2563eb;
}

.legend-current {
  color: #15803d;
}

.substitution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: var(--space-3);
}

/* Las g_i con tres o más variables son largas: una por fila. */
.substitution-grid.wide-formulas {
  grid-template-columns: 1fr;
}

.substitution-card,
.error-card {
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
}

.error-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.failure-note {
  margin: 0;
}

.substitution-card :deep(.katex),
.error-card :deep(.katex) {
  font-size: 1em;
}
</style>
