<script setup>
// Sección fija de Newton, antes de la tabla de iteraciones: lo que no cambia
// de una iteración a otra. El sistema F(x), la derivación de cada ∂f_i/∂x_j
// término a término y la matriz Jacobiana simbólica se calculan una sola vez;
// en cada iteración sólo se evalúan en el punto actual (eso queda en el
// detalle expandible de cada fila).
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import {
  functionsLatex,
  generalStepLatex,
  jacobianLatex,
  partialSteps,
  partialTitleLatex,
} from './newtonFormulas'

const props = defineProps({
  result: { type: Object, required: true },
})

// Entradas del Jacobiano en orden de filas: (f_1, x_1), (f_1, x_2), ...
const entries = computed(() =>
  props.result.equations.flatMap((_, i) => props.result.variables.map((_, j) => ({ i, j })))
)
const PARTIAL = '\\partial f_i / \\partial x_j'
</script>

<template>
  <section class="jacobian-section" aria-labelledby="newton-jacobian-title">
    <h4 id="newton-jacobian-title" class="section-title">Sistema y matriz Jacobiana</h4>
    <p class="section-intro">
      Se calcula una sola vez: la forma de <MathFormula expression="J(x)" /> no cambia entre
      iteraciones. En cada iteración (tabla de abajo) sólo se evalúa en el punto actual.
      Variables, en orden: <MathFormula :expression="result.variables_latex.join(',\\ ')" />.
    </p>

    <div class="formula-box">
      <MathFormula :expression="functionsLatex(result)" display-mode />
    </div>

    <p class="sub-caption">
      Cada entrada <MathFormula :expression="PARTIAL" /> se obtiene derivando
      <MathFormula expression="f_i" /> término a término:
    </p>
    <div class="partials-grid">
      <div v-for="{ i, j } in entries" :key="`${i}-${j}`" class="partial-card">
        <p class="partial-title"><MathFormula :expression="partialTitleLatex(result, i, j)" /></p>
        <ul class="partial-terms">
          <li v-for="(term, t) in partialSteps(result, i, j).terms" :key="t">
            <div class="partial-formula"><MathFormula :expression="term.latex" /></div>
            <span class="partial-rule">{{ term.rule }}</span>
          </li>
        </ul>
        <div v-if="partialSteps(result, i, j).sum_latex" class="partial-sum">
          <MathFormula :expression="partialSteps(result, i, j).sum_latex" />
        </div>
      </div>
    </div>

    <p class="sub-caption">Con todas las entradas se arma la matriz Jacobiana:</p>
    <div class="formula-box">
      <MathFormula :expression="jacobianLatex(result)" display-mode />
    </div>

    <p class="sub-caption">Y en cada iteración se resuelve:</p>
    <div class="formula-box">
      <MathFormula :expression="generalStepLatex()" display-mode />
    </div>
  </section>
</template>

<style scoped>
/* Mismo encabezado que "Convergencia del error" y "Detalle de iteraciones". */
.jacobian-section {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
}

.section-title {
  margin: 0 0 var(--space-2);
  font-size: var(--text-subsection);
  color: var(--color-ink);
}

.section-intro {
  margin: 0 0 var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.sub-caption {
  margin: var(--space-4) 0 var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.formula-box {
  overflow-x: auto;
}

.formula-box :deep(.katex) {
  font-size: 1em;
}

/* Una tarjeta por entrada del Jacobiano, en el orden de la matriz. */
.partials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: var(--space-3);
}

.partial-card {
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
}

.partial-title {
  margin: 0 0 var(--space-2);
}

.partial-terms {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.partial-formula {
  overflow-x: auto;
}

.partial-rule {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.partial-sum {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-line);
  font-weight: var(--weight-semibold);
  overflow-x: auto;
}
</style>
