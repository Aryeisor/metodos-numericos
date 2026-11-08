<script setup>
// Tabla de segmentos del modo «Tabla de datos»: cada segmento es un trapecio
// con su propio ancho. Despliega una fila para ver hᵢ·(yᵢ + yᵢ₊₁)/2.
import { computed, ref, watch } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber } from '../../utils/iterationSteps'
import { segmentSteps } from './explain'
import { cell } from './formulas'
import { segmentColumns } from './glossary'

const props = defineProps({
  result: { type: Object, required: true },
})

const segments = computed(() => props.result.iterations.map((step) => step.extra))
const hasBound = computed(() => Boolean(props.result.function))
const headers = computed(() => segmentColumns(hasBound.value))
const shown = (d) => (d.exact ? d.text : d.approx)

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
  <div class="table-scroll detail-scroll">
    <table class="iterations-table">
      <thead>
        <tr>
          <th class="expand-col"></th>
          <th v-for="col in headers" :key="col.key">
            <InfoTip :text="col.text">{{ col.label }}</InfoTip>
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-for="s in segments" :key="s.i">
          <tr>
            <td class="expand-col">
              <button
                type="button"
                class="expand-btn"
                :aria-expanded="expanded.has(s.i)"
                :title="expanded.has(s.i) ? 'Ocultar cálculo' : 'Ver cálculo'"
                @click="toggle(s.i)"
              >
                {{ expanded.has(s.i) ? '▾' : '▸' }}
              </button>
            </td>
            <td>{{ s.i }}</td>
            <td>[{{ shown(s.x_display[0]) }}, {{ shown(s.x_display[1]) }}]</td>
            <td>{{ shown(s.width) }}</td>
            <td>{{ formatNumber(s.y[0]) }}</td>
            <td>{{ formatNumber(s.y[1]) }}</td>
            <td>{{ s.area_display }}</td>
            <td>{{ cell(s.cumulative) }}</td>
            <td v-if="hasBound">{{ s.bound === null ? 'no disponible' : cell(s.bound) }}</td>
          </tr>
          <tr v-if="expanded.has(s.i)" class="detail-row">
            <td :colspan="hasBound ? 9 : 8">
              <div class="detail-inner">
              <ol class="steps">
                <li v-for="(st, idx) in segmentSteps(s, s.i > 0 ? segments[s.i - 1] : null)" :key="idx">
                  <span class="step-name">{{ st.title }}</span>
                  <template v-for="(block, b) in st.blocks" :key="b">
                    <p v-if="block.kind === 'text'" class="step-text">{{ block.text }}</p>
                    <div v-else class="step-formula"><MathFormula :expression="block.latex" /></div>
                  </template>
                </li>
              </ol>
              <small v-if="s.M !== null && s.M !== undefined" class="step-note">
                Cota del segmento: <MathFormula :expression="`\\frac{h_{${s.i}}^{3}}{12} M = \\frac{(${shown(s.width)})^{3}}{12} \\cdot ${formatNumber(s.M)} = ${formatNumber(s.bound)}`" />,
                con M = máx|f′′(x)| en el segmento (muestreo con {{ result.sampling_points }} puntos).
              </small>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
  <GlossaryBlock
    title="¿Qué significa cada columna?"
    :items="headers.map((col) => ({ symbol: col.symbol, text: col.text }))"
  />
</template>

<style scoped>
.iterations-table td,
.iterations-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.iterations-table .expand-col {
  width: 40px;
  text-align: center;
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
}

.expand-btn:hover {
  background: var(--color-accent-soft);
}

.iterations-table .detail-row td {
  background: var(--color-page);
  text-align: left;
  padding: var(--space-4);
  font-size: 0.9rem;
  white-space: normal;
}

/* El paso a paso ocupa el ancho visible, no el de la tabla. */
.detail-scroll {
  container-type: inline-size;
}

.detail-inner {
  position: sticky;
  left: var(--space-4);
  width: calc(100cqw - 2 * var(--space-4));
}

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
  color: var(--color-ink);
}

.step-text {
  margin: var(--space-1) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.step-formula {
  overflow-x: auto;
}

.step-note {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
