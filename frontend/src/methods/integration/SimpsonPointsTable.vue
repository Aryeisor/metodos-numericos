<script setup>
// Modo «Tabla de datos» de Simpson, una regla aplicada (`app`): la tabla de
// puntos con su peso, peso × yᵢ y la regla de cada punto, y el cálculo por
// partes (suma ponderada y resultado de cada parte; en la combinación, la suma
// de las partes). Con función para comparar, Eₐ y la cota de cada parte.
import { computed } from 'vue'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import InfoTip from '../../components/InfoTip.vue'
import MathFormula from '../../components/MathFormula.vue'
import { formatNumber, tableValue } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import {
  approxBlocks,
  boundBlocks,
  partSumLatex,
  partValueLatex,
  partsTotalLatex,
  pointProduct,
  pointRule,
  pointWeight,
  ruleShort,
} from './simpsonExplain'
import { SIMPSON_POINT_COLUMNS } from './simpsonGlossary'

const props = defineProps({
  result: { type: Object, required: true },
  app: { type: Object, required: true },
})

const combined = computed(() => props.app.key === 'combined')
const junction = computed(() => props.app.points.find((p) => p.weights.length > 1) ?? null)
const shown = (d) => tableValue(d).text
const h = computed(() => props.result.h)
const fn = computed(() => props.result.function)
const partBlocks = (part) => {
  const blocks = []
  const width = part.width_display.latex
  if (part.approx_error !== null && part.mean_fourth) {
    blocks.push(...approxBlocks(fn.value, part.mean_fourth, width, h.value, part.coefficient_numerator, part.divisor, part.approx_error))
  }
  if (part.bound !== null && part.M4) {
    blocks.push(...boundBlocks(fn.value, part.M4, props.result.sampling_points, width, h.value, part.coefficient_numerator, part.divisor, part.bound))
  }
  return blocks
}
const sumLatex = (key) => {
  const values = props.app.parts.map((p) => latexNumber(p[key]))
  return `${values.join(' + ')} = ${latexNumber(props.app.final[key])}`
}
</script>

<template>
  <div class="table-scroll">
    <table class="iterations-table">
      <thead>
        <tr>
          <th v-for="col in SIMPSON_POINT_COLUMNS" :key="col.key">
            <InfoTip :text="col.text">{{ col.label }}</InfoTip>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in app.points" :key="p.i" :class="{ junction: p.weights.length > 1 }">
          <td>{{ p.i }}</td>
          <td>{{ shown(p.x_display) }}</td>
          <td>{{ shown(p.y_display) }}</td>
          <td>{{ pointWeight(p) }}</td>
          <td>{{ pointProduct(p) }}</td>
          <td class="rule-cell">{{ pointRule(p) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <p v-if="junction" class="section-text note">
    El punto {{ junction.i }} (x = {{ shown(junction.x_display) }}) es el final de la parte 1/3 y el inicio de la parte
    3/8: pertenece a las dos y entra en las dos sumas, con peso 1 en cada una (1 + 1). Cada suma se multiplica después
    por el factor de su regla (h/3 o 3h/8).
  </p>
  <GlossaryBlock
    title="¿Qué significa cada columna?"
    :items="SIMPSON_POINT_COLUMNS.map((col) => ({ symbol: col.symbol, text: col.text }))"
  />

  <ol class="steps">
    <li>
      <span class="step-name">Ancho de cada segmento</span>
      <p class="step-text">Los datos están igualmente espaciados: h es la distancia entre dos x seguidos.</p>
      <div class="step-formula">
        <MathFormula :expression="`h = x_1 - x_0 = ${h.exact ? h.latex : h.approx}, \\quad n = ${result.n}`" />
      </div>
    </li>
    <li v-for="part in app.parts" :key="part.rule">
      <span class="step-name">
        {{ combined ? `Parte ${ruleShort(part.rule)}: segmentos ${part.start + 1} a ${part.end} (de x = ${shown(part.x_display[0])} a x = ${shown(part.x_display[1])})` : `Simpson ${ruleShort(part.rule)}` }}
      </span>
      <p class="step-text">Se multiplica cada dato por su peso, se suman y la suma se multiplica por {{ part.rule === 'simpson38' ? '3h/8' : 'h/3' }}.</p>
      <div class="step-formula"><MathFormula :expression="partSumLatex(part, app.points)" /></div>
      <div class="step-formula"><MathFormula :expression="partValueLatex(part, h)" /></div>
    </li>
    <li v-if="combined">
      <span class="step-name">Suma de las partes</span>
      <p class="step-text">La integral en toda la tabla es la parte 1/3 más la parte 3/8.</p>
      <div class="step-formula"><MathFormula :expression="partsTotalLatex(app)" /></div>
    </li>
  </ol>

  <template v-if="app.final && fn">
    <details class="part-errors">
      <summary>Ver el cálculo de Eₐ y de la cota{{ combined ? ' (por partes)' : '' }}</summary>
      <div v-for="part in app.parts" :key="part.rule" class="part-block">
        <p v-if="combined" class="step-name">Parte {{ ruleShort(part.rule) }}</p>
        <template v-for="(block, b) in partBlocks(part)" :key="b">
          <p v-if="block.kind === 'text'" class="step-text">{{ block.text }}</p>
          <small v-else-if="block.kind === 'note'" class="step-note">{{ block.text }}</small>
          <div v-else class="step-formula"><MathFormula :expression="block.latex" /></div>
        </template>
      </div>
      <template v-if="combined">
        <p class="step-text">Eₐ y la cota de toda la tabla son la suma de las de cada parte:</p>
        <div v-if="app.final.approx_error !== null" class="step-formula">
          <MathFormula :expression="`E_a = E_{a,1/3} + E_{a,3/8} = ${sumLatex('approx_error')}`" />
        </div>
        <div v-if="app.final.bound !== null" class="step-formula">
          <MathFormula :expression="`\\text{Cota} = ${sumLatex('bound')}`" />
        </div>
      </template>
    </details>
    <p class="section-text">
      Resultado: S = {{ formatNumber(app.total) }}<template v-if="app.final.approx_error !== null">
        · Eₐ = {{ formatNumber(app.final.approx_error) }}</template><template v-if="app.final.bound !== null">
        · cota = {{ formatNumber(app.final.bound) }}</template>.
    </p>
  </template>
</template>

<style scoped>
.iterations-table td,
.iterations-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.iterations-table .rule-cell {
  text-align: left;
}

.junction td {
  font-weight: var(--weight-semibold);
}

.section-text {
  margin: var(--space-3) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.note {
  font-style: italic;
}

.steps {
  margin: var(--space-4) 0 0;
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
  margin: 0 0 var(--space-1);
}

.step-text {
  margin: var(--space-1) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.step-note {
  display: block;
  margin-top: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  font-style: italic;
}

.step-formula {
  overflow-x: auto;
  margin: var(--space-1) 0;
}

.part-errors {
  margin-top: var(--space-4);
  font-size: var(--text-small);
}

.part-errors summary {
  cursor: pointer;
  color: var(--color-accent);
}

.part-block {
  margin-top: var(--space-3);
}
</style>
