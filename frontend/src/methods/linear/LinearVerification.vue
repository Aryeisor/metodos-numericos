<script setup>
// Comprobación al final del resultado de Jacobi y Gauss-Seidel: la solución
// reemplazada en cada ecuación del sistema tal como lo escribió el usuario
// (result.verification). Misma grilla y marcas ✔ / ⚠ que la comprobación de
// Bairstow (clases globales check-* y mark-* de style.css).
import { computed } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { equationCheckParts, residueLatex, solutionLine } from './verification'

const props = defineProps({
  result: { type: Object, required: true },
})

const check = computed(() => props.result.verification)
const lines = computed(() => check.value.equations.map((equation) => equationCheckParts(equation)))
const solution = computed(() => solutionLine(props.result.variables, check.value.solution))

// Líneas largas (muchas variables o valores con decimales): los términos
// calculados y el resultado pasan a un segundo renglón, como en Bairstow.
const CHECK_LINE_MAX_CHARS = 70
const stacked = computed(() =>
  lines.value.some((line) => line.substitution.length + line.evaluated.length > CHECK_LINE_MAX_CHARS)
)

const hasResidue = computed(() => lines.value.some((line) => !line.ok))
</script>

<template>
  <section v-if="check" class="verification">
    <h4>Comprobación</h4>
    <div v-if="!result.converged" class="alert alert-warning">
      ⚠ El método no convergió; esta comprobación usa la última aproximación calculada.
    </div>
    <p class="section-text">
      Se reemplaza la solución en cada ecuación del sistema original; el lado izquierdo debe dar el
      término independiente b.
    </p>
    <p class="section-text">Solución usada: <MathFormula :expression="solution" /></p>
    <p v-if="check.rounded_to_integers" class="section-text reorder-note">
      La solución calculada se ve entera con 6 decimales, así que se comprueba con esos valores enteros.
    </p>
    <p v-if="check.reordered" class="section-text reorder-note">
      El método trabajó con las filas reordenadas; la comprobación usa el orden original. Las
      ecuaciones son las mismas, así que la solución también.
    </p>

    <div class="table-scroll">
      <div class="check-grid" :class="{ 'is-stacked': stacked }">
        <template v-for="line in lines" :key="line.label">
          <span class="check-label">Ecuación {{ line.label }}:</span>
          <MathFormula :expression="line.substitution" />
          <span v-if="stacked"></span>
          <MathFormula v-else :expression="line.evaluated" />
          <span class="check-result">
            <MathFormula v-if="stacked" :expression="line.evaluated" />
            <MathFormula :expression="`${line.result} \\quad ${line.comparison}`" />
            <span v-if="line.ok" class="mark mark-ok" aria-label="correcto">✔</span>
            <span v-else class="mark mark-warn" aria-label="residuo apreciable">⚠</span>
            <small v-if="line.residue" class="check-exact">
              (residuo <MathFormula :expression="line.residue" />)
            </small>
          </span>
        </template>
      </div>
    </div>

    <p class="section-text">
      Residuo máximo: <strong><MathFormula :expression="residueLatex(check.max_residual)" /></strong>
    </p>
    <p v-if="hasResidue" class="alert alert-warning check-note">
      ⚠ La solución es aproximada; el residuo depende de la tolerancia usada.
    </p>
  </section>
</template>

<style scoped>
/* Mismo marco que las secciones del resultado (ver .iterations-title en ResultsTable). */
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

.reorder-note {
  font-style: italic;
}

.check-label {
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  white-space: nowrap;
}

.check-note {
  margin-top: var(--space-4);
}
</style>
