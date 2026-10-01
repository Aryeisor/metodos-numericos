<script setup>
// Detalle expandible de una iteración de Jacobi / Gauss-Seidel: fórmula
// general, sustitución numérica de cada variable y cálculo del error.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { buildIterationDetail } from '../../utils/iterationSteps'
import {
  errorFormulaLatex,
  errorResultLatex,
  errorSubstitutionLatex,
  generalFormulaLatex,
  substitutionLatex,
} from '../../utils/latexFormulas'

const props = defineProps({
  result: { type: Object, required: true },
  // Sistema tal como se resolvió (A y b ya reordenadas si hubo reordenamiento).
  system: { type: Object, required: true },
  index: { type: Number, required: true },
  methodName: { type: String, required: true },
})

const isGaussSeidel = computed(() => props.result.method === 'gauss-seidel')
const n = computed(() => props.result.solution?.length ?? 0)
const iteration = computed(() => props.result.iterations[props.index].iteration)

const detail = computed(() =>
  buildIterationDetail({
    A: props.system.A,
    b: props.system.b,
    x0: props.system.x0,
    method: props.result.method,
    iterations: props.result.iterations,
    index: props.index,
  })
)
</script>

<template>
  <div class="detail">
    <div class="detail-block">
      <span class="detail-caption">Fórmula ({{ methodName }})</span>
      <div class="formula-box">
        <MathFormula :expression="generalFormulaLatex(result.method)" display-mode />
      </div>
      <p class="detail-hint">
        <span class="legend-prev">■</span> valores de la iteración anterior
        <template v-if="isGaussSeidel">
          · <span class="legend-current">■</span> valores ya recalculados en esta
          misma iteración
        </template>
      </p>
    </div>

    <div class="detail-block">
      <span class="detail-caption">Sustitución numérica</span>
      <div class="substitution-grid" :class="{ 'wide-formulas': n >= 4 }">
        <div v-for="v in detail.variables" :key="v.index" class="substitution-card">
          <MathFormula :expression="substitutionLatex(v, iteration)" display-mode />
        </div>
      </div>
    </div>

    <div class="detail-block">
      <span class="detail-caption">Error de la iteración</span>
      <div class="error-grid">
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
/* Las etiquetas conservan la tipografía de la app; las fórmulas usan la fuente
   matemática propia de KaTeX (no se sobrescribe font-family en sus contenedores). */
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

/* Dos columnas en escritorio y una sola en pantallas angostas. El min() evita
   que la columna quede más ancha que el contenedor en móvil. */
.substitution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: var(--space-3);
}

/* Con 4 o más variables la sustitución es demasiado larga para dos columnas. */
.substitution-grid.wide-formulas {
  grid-template-columns: 1fr;
}

.substitution-card {
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
}

/* Los tres pasos del error son encadenados (fórmula → sustitución → resultado):
   se apilan a ancho completo porque son expresiones largas. */
.error-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.error-card {
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
}

.substitution-card :deep(.katex),
.error-card :deep(.katex) {
  font-size: 1em;
}
</style>
