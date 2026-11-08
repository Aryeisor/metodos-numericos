<script setup>
// Integral por otro camino, común a todas las reglas de integración:
//  - con valor exacto: la antiderivada paso a paso, la verificación F' = f y
//    F(b) − F(a) término a término;
//  - con valor de referencia: por qué no hay antiderivada y qué es la referencia;
//  - sin ninguno: que no hay con qué comparar.
import { computed } from 'vue'
import DerivationSteps from '../../components/DerivationSteps.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import { substitutionLatex } from '../differentiation/formulas'
import { referenceExplanation } from './explain'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const isTable = computed(() => props.result.mode === 'table')
const integral = computed(() => props.result.integral)
const hasExact = computed(() => integral.value?.kind === 'exact' && check.value.upper)
const aLatex = computed(() => props.result.a_display.latex)
const bLatex = computed(() => props.result.b_display.latex)
const lowerLatex = computed(() =>
  check.value.lower.all_zero
    ? `F(${aLatex.value}) = 0`
    : substitutionLatex(check.value.lower, 'F')
)
const differenceLatex = computed(() => {
  const up = latexNumber(check.value.upper.value)
  const low = latexNumber(check.value.lower.value)
  return (
    `I = F(${bLatex.value}) - F(${aLatex.value}) = ${up} - ${low.startsWith('-') ? `\\left(${low}\\right)` : low}` +
    ` = ${latexNumber(integral.value.value)}`
  )
})
const reason = computed(() => referenceExplanation(integral.value))
const antiderivative = computed(() => integral.value?.antiderivative)
</script>

<template>
  <template v-if="hasExact">
    <p class="section-text">
      Antiderivada de f{{ isTable ? ' (la función para comparar)' : '' }}: una función F cuya derivada es f.
      <template v-if="antiderivative.steps.detailed">Se integra f término a término, con la regla de cada término:</template>
    </p>
    <DerivationSteps
      v-if="antiderivative.steps.detailed"
      :steps="antiderivative.steps"
      :result="`F(x) = ${antiderivative.latex}`"
    />
    <template v-else>
      <div class="formula-box"><MathFormula :expression="`F(x) = ${antiderivative.latex}`" display-mode /></div>
      <p class="section-text note">
        Antiderivada obtenida con integración simbólica; la técnica no se detalla aquí.
      </p>
    </template>
    <p class="section-text">Verificación de la antiderivada: al derivar F debe salir f.</p>
    <DerivationSteps :steps="antiderivative.check">
      <template #after-sum>
        <MathFormula :expression="antiderivative.check.ok ? `= f(x)` : `\\ne f(x)`" />
        <span :class="antiderivative.check.ok ? 'mark mark-ok' : 'mark mark-warn'">
          {{ antiderivative.check.ok ? '✔' : '⚠' }}
        </span>
      </template>
    </DerivationSteps>
    <p class="section-text">
      Teorema fundamental del cálculo: la integral de a a b es F(b) − F(a). Se evalúa F en los límites, término a
      término:
    </p>
    <div class="check-list table-scroll">
      <div class="check-line"><MathFormula :expression="substitutionLatex(check.upper, 'F')" /></div>
      <div class="check-line">
        <MathFormula :expression="lowerLatex" />
        <span v-if="check.lower.all_zero" class="zero-note">(todos sus términos se anulan)</span>
      </div>
      <div class="check-line"><MathFormula :expression="differenceLatex" /></div>
    </div>
    <p v-if="result.function?.uses_trigonometry" class="section-text note">
      Las funciones trigonométricas se evalúan en radianes.
    </p>
  </template>
  <p v-else-if="integral && integral.kind === 'reference'" class="section-text">
    {{ reason }} Se compara con el {{ integral.label }}, I ≈ {{ formatNumber(integral.value) }}.
  </p>
  <p v-else-if="integral" class="section-text note">
    No se pudo calcular la integral exacta ni un valor de referencia: no hay con qué comparar.
  </p>
</template>

<style scoped>
.section-text {
  margin: var(--space-3) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.note {
  font-style: italic;
}

.formula-box {
  overflow-x: auto;
  margin-bottom: var(--space-3);
}

.check-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.check-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
}

.zero-note {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
