<script setup>
// Información propia de un sistema no lineal en el resumen del resultado: el
// despeje x_i = g_i(...) que se obtuvo automáticamente de cada ecuación y que
// es lo que realmente se iteró. Cada fila se expande para ver el paso a paso
// del despeje (lo calcula el backend: equations[i].isolation).
import { ref, watch } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { isolationLatex } from './formulas'

const props = defineProps({
  result: { type: Object, required: true },
})

// Mismo patrón que las filas de la tabla de iteraciones (ResultsTable).
const expanded = ref(new Set())
watch(
  () => props.result,
  () => {
    expanded.value = new Set()
  }
)

function toggle(i) {
  const next = new Set(expanded.value)
  if (next.has(i)) next.delete(i)
  else next.add(i)
  expanded.value = next
}
</script>

<template>
  <div class="isolations">
    <p class="isolations-caption">Despeje automático de cada ecuación</p>
    <div class="table-scroll isolations-scroll">
      <table class="isolations-table">
        <thead>
          <tr>
            <th class="expand-col"><span class="visually-hidden">Ver paso a paso</span></th>
            <th scope="col">#</th>
            <th scope="col">Ecuación ingresada</th>
            <th scope="col">Función de iteración</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(equation, i) in result.equations" :key="i">
            <tr>
              <td class="expand-col">
                <button
                  type="button"
                  class="expand-btn"
                  :aria-expanded="expanded.has(i)"
                  :aria-controls="`isolation-steps-${i}`"
                  :title="expanded.has(i) ? 'Ocultar el despeje' : 'Ver el despeje paso a paso'"
                  @click="toggle(i)"
                >
                  {{ expanded.has(i) ? '▾' : '▸' }}
                </button>
              </td>
              <th scope="row">{{ i + 1 }}</th>
              <td><MathFormula :expression="equation.equation_latex" /></td>
              <td><MathFormula :expression="isolationLatex(result, i)" /></td>
            </tr>
            <tr v-if="expanded.has(i)" :id="`isolation-steps-${i}`" class="detail-row">
              <td colspan="4">
                <div class="detail-content">
                  <span class="detail-caption">Despeje de {{ equation.variable }} paso a paso</span>
                  <ol class="steps">
                    <li
                      v-for="(step, k) in equation.isolation.steps"
                      :key="k"
                      class="step"
                      :class="{ 'is-note': !step.latex }"
                    >
                      <span class="step-number" aria-hidden="true">{{ k + 1 }}</span>
                      <div class="step-body">
                        <p class="step-description">{{ step.description }}</p>
                        <div v-if="step.latex" class="step-formula">
                          <MathFormula :expression="step.latex" display-mode />
                        </div>
                      </div>
                    </li>
                  </ol>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.isolations {
  margin-bottom: var(--space-4);
}

.isolations-caption {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.isolations-table th,
.isolations-table td {
  text-align: left;
  vertical-align: middle;
  padding: var(--space-2) var(--space-3);
  white-space: nowrap;
}

.isolations-table tbody th {
  width: 2rem;
  color: var(--color-ink-muted);
  font-weight: var(--weight-semibold);
}

.isolations-table tbody tr:nth-child(even) {
  background: transparent;
}

/* Botón ▸/▾: mismo aspecto que en la tabla de iteraciones. */
.expand-col {
  width: 40px;
  text-align: center !important;
}

.expand-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-accent);
  font-size: var(--text-small);
  line-height: 1;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-control);
  transition: background-color var(--transition-fast);
}

.expand-btn:hover {
  background: var(--color-accent-soft);
}

.isolations-table .detail-row td {
  background: var(--color-page);
  padding: var(--space-4);
  white-space: normal;
  font-size: 0.9rem;
}

/* La tabla puede ser más ancha que la pantalla (fórmulas largas) y se
   desplaza en horizontal. El paso a paso se ajusta al ancho VISIBLE del
   contenedor y queda fijo al desplazar, para no cortarse en móvil. */
.isolations-scroll {
  container-type: inline-size;
}

.detail-content {
  position: sticky;
  left: var(--space-4);
  width: calc(100cqw - 2 * var(--space-4));
}

.detail-caption {
  display: block;
  margin-bottom: var(--space-3);
  font-weight: var(--weight-semibold);
  font-size: var(--text-small);
  color: var(--color-ink);
}

/* Pasos en secuencia vertical, cada uno en su tarjeta (como la sustitución
   numérica del detalle de iteraciones). */
.steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}

.step {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
}

.step.is-note {
  background: var(--color-accent-soft);
}

.step-number {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
}

.step.is-note .step-number {
  background: var(--color-surface);
}

.step-body {
  flex: 1;
  min-width: 0;
}

.step-description {
  margin: 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.step-formula {
  overflow-x: auto;
}

.step-formula :deep(.katex-display) {
  margin: var(--space-2) 0 0;
}

.step-formula :deep(.katex) {
  font-size: 1.05em;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>
