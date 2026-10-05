<script setup>
// Detalle expandible de una iteración de Bairstow, en el orden en que se
// resuelve a mano: valores actuales → división sintética de los b → de los c
// → sistema 2×2 → regla de Cramer (D, D_r, D_s) → Δr y Δs → actualización →
// errores. Si el método se detuvo en esta iteración, se muestra hasta donde
// llegó el cálculo.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { latexNumber } from '../../utils/latexFormulas'
import SyntheticTable from './SyntheticTable.vue'
import {
  B_FORMULA,
  C_FORMULA,
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  currentValuesLatex,
  determinantStepsLatex,
  errorsLatex,
  incrementsLatex,
  systemLatex,
  updatesLatex,
} from './formulas'

const props = defineProps({
  // Una iteración del resultado: { iteration, x, error, extra }.
  row: { type: Object, required: true },
  // Tolerancia εs en %.
  tolerance: { type: Number, required: true },
})

const extra = computed(() => props.row.extra)
const hasSystem = computed(() => Array.isArray(extra.value.matrix))
const solved = computed(() => extra.value.D_r !== undefined && extra.value.D_r !== null)
const finished = computed(() => props.row.error !== null)
const toleranceLatex = computed(() => `${latexNumber(props.tolerance)}\\,\\%`)
</script>

<template>
  <div class="detail">
    <div class="detail-block">
      <span class="detail-caption">1. Valores actuales</span>
      <div class="step-card"><MathFormula :expression="currentValuesLatex(extra)" display-mode /></div>
    </div>

    <div class="detail-block">
      <span class="detail-caption">2. División sintética: coeficientes b</span>
      <div class="formula-line"><MathFormula :expression="B_FORMULA" /></div>
      <div class="step-card"><SyntheticTable :table="extra.b_table" input="a" output="b" /></div>
    </div>

    <div class="detail-block">
      <span class="detail-caption">3. Segunda división sintética: coeficientes c (sobre los b)</span>
      <div class="formula-line"><MathFormula :expression="C_FORMULA" /></div>
      <div class="step-card"><SyntheticTable :table="extra.c_table" input="b" output="c" /></div>
    </div>

    <div v-if="!hasSystem" class="alert alert-danger failure-note">
      Aparecieron valores no finitos en las divisiones sintéticas. El método se detuvo aquí.
    </div>

    <template v-else>
      <div class="detail-block">
        <span class="detail-caption">4. Sistema 2×2 planteado</span>
        <div class="step-card"><MathFormula :expression="systemLatex(extra)" display-mode /></div>
      </div>

      <div class="detail-block">
        <span class="detail-caption">5. Regla de Cramer</span>
        <div class="step-card">
          <MathFormula :expression="determinantStepsLatex('D', extra.matrix, extra.D)" display-mode />
        </div>
        <div v-if="!solved" class="alert alert-danger failure-note">
          El determinante D es (prácticamente) cero: el sistema no tiene solución única y no se
          puede continuar desde estos r y s.
        </div>
        <template v-else>
          <p class="detail-hint">
            <span class="legend-current">■</span> columna reemplazada por los términos
            independientes
          </p>
          <div class="step-grid">
            <div class="step-card">
              <MathFormula
                :expression="determinantStepsLatex('D_r', extra.matrices[0], extra.D_r, 0)"
                display-mode
              />
            </div>
            <div class="step-card">
              <MathFormula
                :expression="determinantStepsLatex('D_s', extra.matrices[1], extra.D_s, 1)"
                display-mode
              />
            </div>
          </div>
        </template>
      </div>

      <template v-if="solved">
        <div class="detail-block">
          <span class="detail-caption">6. Incrementos</span>
          <div class="step-grid">
            <div v-for="(latex, i) in incrementsLatex(extra)" :key="i" class="step-card">
              <MathFormula :expression="latex" display-mode />
            </div>
          </div>
        </div>

        <div v-if="finished" class="detail-block">
          <span class="detail-caption">7. Actualización</span>
          <p class="detail-hint"><span class="legend-prev">■</span> valores de la iteración anterior</p>
          <div class="step-grid">
            <div v-for="(latex, i) in updatesLatex(extra)" :key="i" class="step-card">
              <MathFormula :expression="latex" display-mode />
            </div>
          </div>
        </div>

        <div v-if="finished" class="detail-block">
          <span class="detail-caption">8. Errores relativos</span>
          <div class="step-grid">
            <div v-for="(latex, i) in errorsLatex(extra)" :key="i" class="step-card">
              <MathFormula :expression="latex" display-mode />
            </div>
          </div>
          <p class="tolerance-check" :class="extra.meets_tolerance ? 'is-met' : 'is-not-met'">
            <template v-if="extra.meets_tolerance">
              ✓ Ambos errores son ≤ <MathFormula :expression="`\\varepsilon_s = ${toleranceLatex}`" />:
              se cumple la tolerancia.
            </template>
            <template v-else>
              Al menos un error es mayor que
              <MathFormula :expression="`\\varepsilon_s = ${toleranceLatex}`" />: se sigue iterando.
            </template>
          </p>
          <p v-if="extra.absolute?.r || extra.absolute?.s" class="detail-hint">
            Como {{ extra.absolute.r && extra.absolute.s ? 'r y s quedaron' : extra.absolute.r ? 'r quedó' : 's quedó' }}
            prácticamente en 0, su error relativo no está definido: se usa el error absoluto |Δ|.
          </p>
        </div>
        <div v-if="!finished" class="alert alert-danger failure-note">
          Los incrementos o los nuevos r y s no son números reales finitos. El método se detuvo aquí.
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
/* Mismo aspecto que el detalle de iteración de los demás métodos. Con
   width 0 / min-width 100 % el detalle no ensancha la tabla de iteraciones
   (como en Newton): en móvil el texto se ajusta y las fórmulas largas se
   desplazan dentro de su tarjeta. */
.detail {
  width: 0;
  min-width: 100%;
}

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
  margin: var(--space-2) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.formula-line {
  margin-bottom: var(--space-2);
  overflow-x: auto;
}

.legend-prev {
  color: v-bind(PREVIOUS_COLOR);
}

.legend-current {
  color: v-bind(CURRENT_COLOR);
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(380px, 100%), 1fr));
  gap: var(--space-3);
}

.step-card {
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
}

.step-card :deep(.katex) {
  font-size: 1em;
}

.tolerance-check {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
}

.tolerance-check.is-met {
  color: var(--color-success);
}

.tolerance-check.is-not-met {
  color: var(--color-ink-muted);
}

.failure-note {
  margin: var(--space-2) 0 0;
}
</style>
