<script setup>
// Tabla del modo «Tabla de datos»: en cada xᵢ, cada fórmula con sus vecinos y,
// si hay función para comparar, la derivada exacta, el error real y la cota.
// Cada punto tiene su paso a paso expandible.
// Con `explained` (diferencias progresiva y regresiva): encabezados con
// tooltip, leyenda de columnas y el paso a paso explicado de integración.
import { computed, ref, watch } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import TrapezoidStepDetail from '../integration/TrapezoidStepDetail.vue'
import DifferenceStepDetail from './DifferenceStepDetail.vue'
import { tableContext } from './differenceExplain'
import { tableColumns } from './differenceGlossary'
import { boundMark, cell } from './formulas'
import { explainSteps } from './threePointExplain'

const props = defineProps({
  result: { type: Object, required: true },
  explained: { type: Boolean, default: false },
})

const formulas = computed(() => props.result.formulas)
const hasFunction = computed(() => Boolean(props.result.function))
// Fórmula de 3 puntos: columna «Recomendada» (la elige el backend).
const hasRecommended = computed(() => Boolean(props.result.iterations[0]?.extra.recommended))
const columns = computed(
  () =>
    4 +
    formulas.value.length +
    (hasRecommended.value ? 1 : 0) +
    (hasFunction.value ? 1 + formulas.value.length * 2 + 1 : 0)
)

const expanded = ref(new Set())
watch(
  () => props.result,
  () => (expanded.value = new Set())
)
function toggle(i) {
  const next = new Set(expanded.value)
  if (next.has(i)) next.delete(i)
  else next.add(i)
  expanded.value = next
}

const headers = computed(() => tableColumns(formulas.value, hasFunction.value, hasRecommended.value))
const explainedSteps = (f, i) =>
  explainSteps(props.result, f, props.result.iterations[i - 1].extra[f.key], tableContext(props.result, f, i))

const pointName = (p) => `x_{${p.index + 1}}`
const marks = (extra) =>
  formulas.value
    .map((f) => extra[f.key])
    .filter((item) => item && item.within_bound !== null)
    .map((item) => ({ mark: boundMark(item), ok: item.within_bound, rounding: item.by_rounding }))

// h se mide con el nodo +1 (o el −1 si la fórmula no lo tiene), como en el backend.
function stepLine(item, extra, i) {
  const offsets = item.points.map((p) => p.offset).filter((o) => o !== 0)
  const step = offsets.some((o) => o > 0) ? Math.min(...offsets.filter((o) => o > 0)) : Math.max(...offsets)
  const node = item.points.find((p) => p.offset === step)
  const here = { index: i - 1, display: extra.x_display }
  const [right, left] = step > 0 ? [node, here] : [here, node]
  return (
    `h = x_{${right.index + 1}} - x_{${left.index + 1}} = ${right.display.latex} - ${left.display.latex.startsWith('-') ? `(${left.display.latex})` : left.display.latex} = ` +
    (item.h.exact ? item.h.latex : `${item.h.approx}`)
  )
}
</script>

<template>
  <div class="table-scroll" :class="{ 'detail-scroll': explained }">
    <table class="iterations-table">
      <thead>
        <tr v-if="explained">
          <th class="expand-col"></th>
          <th v-for="col in headers" :key="col.key">
            <InfoTip :text="col.text">{{ col.label }}</InfoTip>
          </th>
        </tr>
        <tr v-else>
          <th class="expand-col"></th>
          <th>i</th>
          <th>xᵢ</th>
          <th>f(xᵢ)</th>
          <th v-for="f in formulas" :key="f.key">{{ f.name }}</th>
          <th v-if="hasRecommended">Recomendada</th>
          <template v-if="hasFunction">
            <th>f′(xᵢ) exacta</th>
            <th v-for="f in formulas" :key="`e-${f.key}`">Error real {{ f.name.toLowerCase() }}</th>
            <th v-for="f in formulas" :key="`c-${f.key}`">Cota {{ f.name.toLowerCase() }}</th>
            <th title="Error real ≤ cota">≤ cota</th>
          </template>
        </tr>
      </thead>
      <tbody>
        <template v-for="step in result.iterations" :key="step.iteration">
          <tr>
            <td class="expand-col">
              <button
                type="button"
                class="expand-btn"
                :aria-expanded="expanded.has(step.iteration)"
                :title="expanded.has(step.iteration) ? 'Ocultar cálculo' : 'Ver cálculo'"
                @click="toggle(step.iteration)"
              >
                {{ expanded.has(step.iteration) ? '▾' : '▸' }}
              </button>
            </td>
            <td>{{ step.iteration }}</td>
            <td>{{ step.extra.x_display.text }}</td>
            <td>{{ cell(step.extra.y) }}</td>
            <td v-for="f in formulas" :key="f.key">{{ cell(step.extra[f.key]?.D) }}</td>
            <td v-if="hasRecommended" class="recommended-cell">
              <strong>{{ cell(step.extra.recommended.D) }}</strong>
              <small class="recommended-name">{{ step.extra.recommended.name.toLowerCase() }}</small>
            </td>
            <template v-if="hasFunction">
              <td>{{ cell(step.extra.exact) }}</td>
              <td v-for="f in formulas" :key="`e-${f.key}`">{{ cell(step.extra[f.key]?.real_error) }}</td>
              <td v-for="f in formulas" :key="`c-${f.key}`">
                {{ step.extra[f.key] && step.extra[f.key].bound === null ? 'no disponible' : cell(step.extra[f.key]?.bound) }}
              </td>
              <td class="mark-cell">
                <span v-for="(m, k) in marks(step.extra)" :key="k" :class="m.ok ? 'mark mark-ok' : 'mark mark-warn'">
                  {{ m.mark }}<sup v-if="m.rounding">R</sup>
                </span>
              </td>
            </template>
          </tr>
          <tr v-if="expanded.has(step.iteration)" class="detail-row">
            <td :colspan="columns">
              <div :class="{ 'detail-inner': explained }">
              <template v-for="f in formulas" :key="f.key">
                <div v-if="step.extra[f.key]" class="detail-block">
                  <p class="detail-title">{{ f.name }} en x{{ step.iteration }}</p>
                  <TrapezoidStepDetail
                    v-if="explained"
                    :result="result"
                    :row="step.extra[f.key]"
                    :k="step.iteration"
                    :custom-steps="explainedSteps(f, step.iteration)"
                  />
                  <DifferenceStepDetail
                    v-else
                    :formula="f"
                    :item="step.extra[f.key]"
                    :label="step.iteration"
                    :step-line="stepLine(step.extra[f.key], step.extra, step.iteration)"
                    :h="step.extra[f.key].h"
                    :exact="step.extra.exact"
                    :exact-source="result.verification.substitutions?.[step.iteration - 1] ?? null"
                    :derivative-latex="result.function?.derivative.latex ?? null"
                    :bound-derivative-latex="result.function?.higher_derivatives[f.bound_derivative]?.latex ?? null"
                    :at="`x_{${step.iteration}}`"
                    :point-name="pointName"
                    :has-function="hasFunction"
                    :samples="result.sampling_points"
                    :rounding-text="result.rounding_text ?? undefined"
                  />
                </div>
                <p v-else class="detail-title muted">
                  {{ f.name }}: no existe en x{{ step.iteration }} (falta el punto vecino).
                </p>
              </template>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>

  <GlossaryBlock
    v-if="explained"
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

.mark-cell {
  text-align: center !important;
}

.recommended-name {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.mark-cell .mark + .mark {
  margin-left: var(--space-2);
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

/* El paso a paso ocupa el ancho visible, no el de la tabla (como en integración). */
.detail-scroll {
  container-type: inline-size;
}

.detail-inner {
  position: sticky;
  left: var(--space-4);
  width: calc(100cqw - 2 * var(--space-4));
}

.detail-block + .detail-block,
.detail-block + .detail-title,
.detail-title + .detail-block {
  margin-top: var(--space-4);
}

.detail-title {
  margin: 0 0 var(--space-2);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.detail-title.muted {
  font-weight: normal;
  color: var(--color-ink-muted);
}
</style>
