<script setup>
// Paso a paso explicado de una fila de la cuadratura gaussiana. Los pasos salen
// de gaussExplain.js; aquí sólo se dibujan, con las tablas propias de Gauss
// (nodos y pesos, cambio de variable, evaluaciones y productos). Con m·N > 16
// las tablas de puntos se pliegan («Mostrar todos los puntos»).
import { computed, ref, watch } from 'vue'
import MathFormula from '../../components/MathFormula.vue'
import { substitutionLatex } from '../differentiation/formulas'
import { gaussRowSteps, gaussSubstitution, mappingLatex } from './gaussExplain'

const FOLD = 16

const props = defineProps({
  result: { type: Object, required: true },
  row: { type: Object, required: true },
  previous: { type: Object, default: null },
})

const steps = computed(() => gaussRowSteps(props.result, props.row, props.previous))
const step = computed(() => props.row.step)
const composite = computed(() => props.result.subintervals > 1)

const showAll = ref(false)
watch(
  () => props.row,
  () => {
    showAll.value = false
  }
)
// Todos los puntos con su subintervalo; plegados: los 8 primeros, «…» y los 8 últimos.
const allPoints = computed(() => step.value.groups.flatMap((g) => g.points.map((p) => ({ group: g, p }))))
const folds = computed(() => step.value.count > FOLD)
const points = computed(() =>
  folds.value && !showAll.value ? [...allPoints.value.slice(0, 8), null, ...allPoints.value.slice(-8)] : allPoints.value
)
const hidden = computed(() => step.value.count - 16)
const weight = (i) => step.value.nodes[i - 1]
const substitution = (p) => substitutionLatex(gaussSubstitution(props.result, p), 'f')
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

        <!-- Nodos y pesos -->
        <div v-else-if="block.kind === 'nodes'" class="table-scroll">
          <table class="eval-table">
            <thead>
              <tr>
                <th>i</th>
                <th>tᵢ (forma exacta)</th>
                <th>tᵢ</th>
                <th>wᵢ (forma exacta)</th>
                <th>wᵢ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="n in step.nodes" :key="n.i">
                <td>{{ n.i }}</td>
                <td><MathFormula v-if="n.t_latex" :expression="n.t_latex" /><span v-else class="muted">—</span></td>
                <td>{{ n.t_display }}</td>
                <td><MathFormula v-if="n.w_latex" :expression="n.w_latex" /><span v-else class="muted">—</span></td>
                <td>{{ n.w_display }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cambio de variable de cada nodo -->
        <ul v-else-if="block.kind === 'mapping'" class="mapping-list">
          <template v-for="(item, i) in points" :key="item ? `${item.group.j}-${item.p.i}` : `gap-${i}`">
            <li v-if="item && composite && item.p.i === 1" class="group-head">
              Subintervalo {{ item.group.j }}: c<sub>{{ item.group.j }}</sub> = {{ item.group.center.exact ? item.group.center.text : item.group.center.approx }},
              H/2 = {{ result.half_display.exact ? result.half_display.text : result.half_display.approx }}
            </li>
            <li v-if="item"><MathFormula :expression="mappingLatex(result, row, item.group, item.p)" /></li>
            <li v-else class="gap-cell">… ({{ hidden }} nodos más)</li>
          </template>
        </ul>

        <!-- f en cada nodo -->
        <div v-else-if="block.kind === 'evals'" class="table-scroll">
          <table class="eval-table">
            <thead>
              <tr>
                <th v-if="composite">j</th>
                <th>i</th>
                <th>xᵢ</th>
                <th>Sustitución</th>
                <th>f(xᵢ)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in points" :key="item ? `${item.group.j}-${item.p.i}` : `gap-${i}`">
                <template v-if="item">
                  <td v-if="composite">{{ item.group.j }}</td>
                  <td>{{ item.p.i }}</td>
                  <td>{{ item.p.x_display }}</td>
                  <td class="substitution"><MathFormula :expression="substitution(item.p)" /></td>
                  <td class="value-new">{{ item.p.f_display }}</td>
                </template>
                <td v-else :colspan="composite ? 5 : 4" class="gap-cell">… ({{ hidden }} puntos más)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Productos -->
        <template v-else-if="block.kind === 'products'">
          <div class="table-scroll">
            <table class="eval-table">
              <thead>
                <tr>
                  <th v-if="composite">j</th>
                  <th>i</th>
                  <th>wᵢ</th>
                  <th>f(xᵢ)</th>
                  <th>wᵢ · f(xᵢ)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, i) in points" :key="item ? `${item.group.j}-${item.p.i}` : `gap-${i}`">
                  <template v-if="item">
                    <td v-if="composite">{{ item.group.j }}</td>
                    <td>{{ item.p.i }}</td>
                    <td>{{ weight(item.p.i).w_display }}</td>
                    <td class="value-new">{{ item.p.f_display }}</td>
                    <td>{{ item.p.product }}</td>
                  </template>
                  <td v-else :colspan="composite ? 5 : 4" class="gap-cell">… ({{ hidden }} puntos más)</td>
                </tr>
              </tbody>
            </table>
          </div>
          <small class="step-note">
            Con {{ step.decimals }} decimales, para que el resultado sea coherente con los valores que se ven.
            <template v-if="folds && !showAll">Se muestran 16 de {{ step.count }} puntos; la suma usa todos.</template>
          </small>
          <button v-if="folds" type="button" class="btn btn-outline show-all" @click="showAll = !showAll">
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

.mapping-list {
  margin: 0;
  padding-left: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  overflow-x: auto;
}

.group-head {
  list-style: none;
  margin-top: var(--space-2);
  margin-left: calc(-1 * var(--space-4));
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
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

.muted,
.gap-cell {
  color: var(--color-ink-muted);
}

.gap-cell {
  text-align: center !important;
  list-style: none;
}

.show-all {
  margin-top: var(--space-2);
}
</style>
