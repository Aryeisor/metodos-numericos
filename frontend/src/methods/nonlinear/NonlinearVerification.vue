<script setup>
// Comprobación al final del resultado de Punto Fijo y de Newton: la solución reemplazada
// en cada ecuación original, escrita f_i = 0 (result.verification). Mismas
// marcas ✔ / ⚠ y textos que la comprobación de los métodos lineales.
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { residueLatex } from '../linear/verification'
import { equationCheckParts, rawResidualNote, solutionLine } from './verification'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const lines = computed(() => check.value.equations.map((_, i) => equationCheckParts(check.value, i)))
const solution = computed(() => solutionLine(props.result.variables_latex, check.value.solution))
const rawNote = computed(() => rawResidualNote(check.value))
const hasResidue = computed(() => lines.value.some((line) => !line.ok))
</script>

<template>
  <section v-if="check" class="verification">
    <h4>Comprobación</h4>
    <div v-if="!result.converged" class="alert alert-warning">
      ⚠ El método no convergió; esta comprobación usa la última aproximación calculada.
    </div>
    <p class="section-text">
      Se reemplaza la solución en cada ecuación original, escrita como f(x) = 0; el resultado debe
      dar 0.
    </p>
    <p class="section-text">Solución usada: <MathFormula :expression="solution" /></p>
    <p v-if="check.uses_trigonometry" class="section-text note">
      Las funciones trigonométricas se evalúan en radianes.
    </p>

    <div class="table-scroll">
      <div v-for="line in lines" :key="line.label" class="check-equation">
        <div>
          <span class="check-label">Ecuación {{ line.label }}:</span>
          <MathFormula :expression="line.equation" />
        </div>
        <div class="check-line">
          <MathFormula :expression="line.substitution" />
          <MathFormula v-if="line.evaluated" :expression="line.evaluated" />
          <span class="check-result">
            <MathFormula :expression="line.result" />
            <span v-if="line.ok" class="mark mark-ok" aria-label="correcto">✔</span>
            <span v-else class="mark mark-warn" aria-label="residuo apreciable">⚠</span>
            <small v-if="line.residue" class="check-exact">
              (residuo <MathFormula :expression="line.residue" />)
            </small>
          </span>
        </div>
      </div>
    </div>

    <p class="section-text">
      Residuo máximo: <strong><MathFormula :expression="residueLatex(check.max_residual)" /></strong>
    </p>
    <p v-if="rawNote" class="section-text note">
      <small>
        Con los valores sin redondear de la última iteración, el residuo máximo es
        <MathFormula :expression="rawNote" />.
      </small>
    </p>
    <p v-if="hasResidue" class="alert alert-warning check-note">
      ⚠ La solución es aproximada; el residuo depende de la tolerancia usada.
    </p>
  </section>
</template>

<style scoped>
/* Mismo marco que la comprobación de los métodos lineales. */
.verification {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
}

.verification h4 {
  margin: 0 0 var(--space-3);
  font-size: var(--text-subsection);
  color: var(--color-ink);
}

.section-text {
  margin: var(--space-3) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.note {
  font-style: italic;
}

.check-equation {
  margin-bottom: var(--space-4);
}

.check-label {
  margin-right: var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  white-space: nowrap;
}

/* Sustitución | términos calculados | resultado: pasan a otro renglón si no caben. */
.check-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-1) var(--space-3);
  margin: var(--space-1) 0 0 var(--space-5);
}

.check-note {
  margin-top: var(--space-4);
}
</style>
