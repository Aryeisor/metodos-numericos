<script setup>
// Paso a paso explicado de una fila de la tabla de refinamiento (modo función).
// Los pasos (título, frases, fórmulas sustituidas y resultado) salen de
// explain.js; aquí sólo se dibujan. Azul: valores de la fila anterior; verde:
// valores nuevos. Todos los números vienen del backend.
import { computed, ref, watch } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { substitutionLatex } from '../differentiation/formulas'
import { canShowAll, divisionPointLatex, foldedPoints, pointSubstitution, rowSteps } from './explain'

const props = defineProps({
  result: { type: Object, required: true },
  row: { type: Object, required: true },
  k: { type: Number, required: true },
  previous: { type: Object, default: null },
})

const step = computed(() => props.row.step)
const isFirst = computed(() => step.value.kind === 'formula')
const steps = computed(() => rowSteps(props.result, props.row, props.k, props.previous))

const showAll = ref(false)
watch(
  () => props.row,
  () => {
    showAll.value = false
  }
)
const points = computed(() => foldedPoints(step.value, showAll.value))
const hidden = computed(() => step.value.count - step.value.points.length)
const columns = computed(() => (isFirst.value ? 6 : 4))
const substitution = (p) => substitutionLatex(pointSubstitution(props.result, p), 'f')
</script>

<template>
  <ol class="steps">
    <li v-for="(s, idx) in steps" :key="idx">
      <span class="step-name">{{ s.title }}</span>
      <template v-for="(block, b) in s.blocks" :key="b">
        <p v-if="block.kind === 'text'" class="step-text">{{ block.text }}</p>
        <small v-else-if="block.kind === 'note'" class="step-note">{{ block.text }}</small>
        <div v-else-if="block.kind === 'math'" class="step-formula"><MathFormula :expression="block.latex" /></div>
        <div v-else-if="block.kind === 'check'" class="step-check">
          <MathFormula v-if="block.latex" :expression="block.latex" />
          <span v-if="block.ok === true" class="mark mark-ok" aria-label="cumple">✔</span>
          <span v-else-if="block.ok === false" class="mark mark-warn" aria-label="no cumple">⚠</span>
          <span class="step-text">{{ block.text }}</span>
        </div>

        <!-- Puntos de división (fila 1) -->
        <ul v-else-if="block.kind === 'division'" class="division-list">
          <li v-for="(p, i) in points" :key="p ? p.i : `gap-${i}`">
            <MathFormula v-if="p" :expression="divisionPointLatex(result, row, p)" />
            <span v-else class="gap-cell">…</span>
          </li>
        </ul>

        <!-- Tabla de puntos con su sustitución -->
        <template v-else-if="block.kind === 'points'">
          <div class="table-scroll">
            <table class="eval-table">
              <thead>
                <tr>
                  <th>i</th>
                  <th>{{ isFirst ? 'xᵢ' : 'xᵢ = a + i·h' }}</th>
                  <th>Sustitución</th>
                  <th>f(xᵢ)</th>
                  <th v-if="isFirst">Peso</th>
                  <th v-if="isFirst">Peso × f(xᵢ)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(p, i) in points" :key="p ? p.i : `gap-${i}`">
                  <template v-if="p">
                    <td>{{ p.i }}</td>
                    <td>
                      <MathFormula
                        :expression="isFirst ? (p.x_display.exact ? p.x_display.latex : `\\approx ${p.x_display.approx}`) : divisionPointLatex(result, row, p)"
                      />
                    </td>
                    <td class="substitution"><MathFormula :expression="substitution(p)" /></td>
                    <td :class="{ 'value-new': !isFirst }">{{ p.f_display }}</td>
                    <td v-if="isFirst">{{ p.weight }}</td>
                    <td v-if="isFirst">{{ p.product }}</td>
                  </template>
                  <td v-else :colspan="columns" class="gap-cell">
                    … ({{ step.count - 16 }} puntos más)
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <small class="step-note">
            Con {{ step.decimals }} decimales, para que el resultado sea coherente con los valores que se ven.
            <template v-if="hidden > 0">Se muestran {{ step.points.length }} de {{ step.count }} puntos; la suma usa todos.</template>
          </small>
          <button v-if="canShowAll(step)" type="button" class="btn btn-outline show-all" @click="showAll = !showAll">
            {{ showAll ? 'Mostrar sólo 16 puntos' : `Mostrar todos los puntos (${step.count})` }}
          </button>
        </template>
      </template>
    </li>
  </ol>
</template>

<style scoped>
.steps {
  margin: 0;
  padding-left: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.step-name {
  display: block;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
  margin-bottom: var(--space-1);
}

.step-text {
  margin: var(--space-1) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.step-formula {
  overflow-x: auto;
  margin: var(--space-1) 0;
}

.step-note {
  display: block;
  margin-top: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  font-style: italic;
}

.step-check {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-2);
  margin-top: var(--space-2);
  overflow-x: auto;
}

.division-list {
  margin: 0;
  padding-left: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  overflow-x: auto;
}

.eval-table {
  width: auto;
  min-width: min(100%, 280px);
}

.eval-table th,
.eval-table td {
  padding: var(--space-1) var(--space-3);
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.eval-table .substitution {
  text-align: left;
}

.value-new {
  color: var(--color-value-new);
}

.gap-cell {
  text-align: center !important;
  color: var(--color-ink-muted);
}

.show-all {
  margin-top: var(--space-2);
}
</style>
