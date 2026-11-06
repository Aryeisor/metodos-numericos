<script setup>
// Paso a paso de una fórmula en una fila (modo función) o en un punto (modo
// tabla): h, puntos, evaluaciones de f (f(x₀) en azul, los demás nodos en
// verde), sustitución en la fórmula, error estimado, error real, cota y razón.
// Todos los valores vienen del backend; aquí sólo se escriben.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import {
  boundLatex,
  byDistance,
  criterionLatex,
  derivativeName,
  estimatedErrorLatex,
  evaluationLatex,
  intervalLatex,
  nodeValueLatex,
  maxLatex,
  pointsLatex,
  quotientLatex,
  ratioLatex,
  realErrorLatex,
  substitutionLatex,
} from './formulas'

const props = defineProps({
  formula: { type: Object, required: true },
  item: { type: Object, required: true },
  // Fila k (modo función) o número de punto (modo tabla).
  label: { type: Number, required: true },
  // LaTeX de la línea de h, ya armada por quien conoce el modo.
  stepLine: { type: String, required: true },
  h: { type: Object, required: true },
  // Plantilla de f con @@0@@ (null en modo tabla: allí f(xᵢ) es un dato).
  template: { type: String, default: null },
  // f'(x) exacta en el punto (null si no hay función o no es derivable).
  exact: { type: Number, default: null },
  // f'(x) sustituida término a término en el punto (verification del backend):
  // muestra de dónde sale el valor exacto.
  exactSource: { type: Object, default: null },
  derivativeLatex: { type: String, default: null },
  // LaTeX de la derivada que acota el error (f'' en las fórmulas de 2 puntos).
  boundDerivativeLatex: { type: String, default: null },
  // Nombre del punto donde se deriva: x_0 o x_{i}.
  at: { type: String, default: 'x_0' },
  // Nombre LaTeX de cada nodo (modo tabla: x_{i+1}).
  pointName: { type: Function, default: (p) => p.role },
  previous: { type: Object, default: null },
  hasFunction: { type: Boolean, default: true },
  samples: { type: Number, default: 401 },
  // Regla del redondeo R (cada método tiene la suya).
  roundingText: { type: String, default: 'R = 4ε·máx|f|/h' },
})

const evaluations = computed(() =>
  byDistance(props.item.points).map((p) =>
    props.template
      ? evaluationLatex(p, props.template, props.pointName(p))
      : `f(${props.pointName(p)}) = ${nodeValueLatex(p)}`
  )
)
const interval = computed(() => (props.item.interval_display ? intervalLatex(props.item) : null))
const bound = computed(() => boundLatex(props.formula, props.item, props.h))
const criterion = computed(() => criterionLatex(props.item))
const fn = computed(() => derivativeName(props.formula.bound_derivative))
const xMShown = computed(() => {
  const shown = props.item.M_substitution?.x_display
  return shown?.exact ? shown.latex : formatNumber(props.item.x_M)
})
const fnText = computed(() => fn.value.replace(/'/g, '′'))
</script>

<template>
  <ol class="steps">
    <li>
      <span class="step-name">Paso</span>
      <MathFormula :expression="stepLine" />
    </li>
    <li>
      <span class="step-name">Puntos</span>
      <MathFormula :expression="pointsLatex(item.points, pointName)" />
    </li>
    <li>
      <span class="step-name">Evaluaciones</span>
      <div v-for="(latex, i) in evaluations" :key="i" class="step-formula">
        <MathFormula :expression="latex" />
      </div>
      <small class="step-note">
        Con {{ item.decimals }} decimales, para que el cociente sea coherente con los valores que se ven.
      </small>
    </li>
    <li>
      <span class="step-name">Fórmula</span>
      <div class="step-formula"><MathFormula :expression="quotientLatex(formula, item, h, label)" /></div>
    </li>
    <li v-if="item.estimated_error !== null && item.estimated_error !== undefined">
      <span class="step-name">Error estimado</span>
      <div class="step-formula"><MathFormula :expression="estimatedErrorLatex(formula, item, label)" /></div>
    </li>
    <li v-if="exact !== null && item.real_error !== null">
      <span class="step-name">Error real</span>
      <template v-if="exactSource">
        <small class="step-note">
          Valor exacto: la derivada exacta
          <MathFormula v-if="derivativeLatex" :expression="`f'(x) = ${derivativeLatex}`" />
          evaluada en <MathFormula :expression="at" />:
        </small>
        <div class="step-formula"><MathFormula :expression="`f'(${at}) = ${substitutionLatex(exactSource)}`" /></div>
      </template>
      <div class="step-formula"><MathFormula :expression="realErrorLatex(formula, item, exact, label, at)" /></div>
    </li>
    <li v-if="hasFunction">
      <span class="step-name">Cota</span>
      <template v-if="bound">
        <div class="step-formula"><MathFormula :expression="bound" /></div>
        <small v-if="interval" class="step-note">
          <MathFormula :expression="maxLatex(formula, interval)" /> ≈ {{ formatNumber(item.M) }}, alcanzado en
          x ≈ {{ formatNumber(item.x_M) }} (estimado por muestreo con {{ samples }} puntos del intervalo).
        </small>
        <template v-if="item.M_substitution">
          <small class="step-note">
            De dónde sale M: se evalúa
            <MathFormula v-if="boundDerivativeLatex" :expression="`${fn}(x) = ${boundDerivativeLatex}`" />
            en ese punto y se toma el valor absoluto:
          </small>
          <div class="step-formula"><MathFormula :expression="substitutionLatex(item.M_substitution, fn)" /></div>
          <div class="step-formula">
            <MathFormula :expression="`M = \\left|${fn}(${xMShown})\\right| = ${latexNumber(item.M)}`" />
          </div>
        </template>
        <div v-if="criterion" class="step-formula criterion">
          <span>Error real ≤ cota:</span>
          <MathFormula :expression="criterion" />
          <span v-if="item.within_bound" class="mark mark-ok" aria-label="cumple">✔</span>
          <span v-else class="mark mark-warn" aria-label="no cumple">⚠</span>
        </div>
        <small v-if="item.by_rounding" class="step-note">
          El error real supera la cota sólo por el redondeo de la computadora, {{ roundingText }}.
        </small>
      </template>
      <small v-else class="step-note">
        No disponible: {{ fnText }}(x) no es finita en todo el intervalo de la fórmula.
      </small>
    </li>
    <li v-if="item.ratio !== null && item.ratio !== undefined && previous">
      <span class="step-name">Razón</span>
      <div class="step-formula"><MathFormula :expression="ratioLatex(item, previous)" /></div>
    </li>
  </ol>
</template>

<style scoped>
.steps {
  margin: 0;
  padding-left: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.step-name {
  display: block;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  margin-bottom: var(--space-1);
}

.step-formula {
  overflow-x: auto;
}

.step-note {
  display: block;
  margin-top: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.criterion {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: var(--text-small);
}
</style>
