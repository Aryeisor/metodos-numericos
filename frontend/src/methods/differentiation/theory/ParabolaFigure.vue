<script setup>
// Interpretación geométrica de la fórmula de 3 puntos: f(x) = ln x cerca de
// x₀ = 1.8 (la misma función y el mismo deslizador de h que la figura de las
// diferencias), su recta tangente, la parábola que pasa por los 3 puntos de la
// fórmula elegida y, tenue, la secante de la progresiva. Los valores se
// calculan aquí con Math.log: es sólo ilustrativo (el ejemplo resuelto usa los
// datos del solver). Colores de theme.css, así que sigue el tema.
import { computed, ref } from 'vue'
import MathFormula from '../../../components/MathFormula.vue'
import { formatNumber } from '../../../utils/iterationSteps'

const H_VALUES = [0.4, 0.2, 0.1, 0.05, 0.025, 0.0125]
const X0 = 1.8
const EXACT = 1 / X0
const f = Math.log

// Desplazamientos (en múltiplos de h) de los 3 puntos de cada fórmula.
const FORMULAS = [
  { key: 'med', name: 'Punto medio', offsets: [-1, 0, 1], symbol: 'D^{\\text{med}}' },
  { key: 'ad', name: 'Extremo hacia adelante', offsets: [0, 1, 2], symbol: 'D^{\\text{ad}}' },
  { key: 'at', name: 'Extremo hacia atrás', offsets: [-2, -1, 0], symbol: 'D^{\\text{at}}' },
]

// Ventana del gráfico (cabe x₀ ± 2h con el h más grande) y su caja en el SVG.
const X_MIN = 0.9
const X_MAX = 2.7
const Y_MIN = -0.15
const Y_MAX = 1.15
const BOX = { left: 16, right: 544, top: 12, bottom: 290 }

const sx = (x) => BOX.left + ((x - X_MIN) / (X_MAX - X_MIN)) * (BOX.right - BOX.left)
const sy = (y) => BOX.bottom - ((y - Y_MIN) / (Y_MAX - Y_MIN)) * (BOX.bottom - BOX.top)

const index = ref(0)
const selected = ref('med')
const h = computed(() => H_VALUES[index.value])
const formula = computed(() => FORMULAS.find((item) => item.key === selected.value))

/** Polilínea de una función sobre toda la ventana. */
function path(g) {
  return Array.from({ length: 121 }, (_, i) => {
    const x = X_MIN + ((X_MAX - X_MIN) * i) / 120
    return `${sx(x).toFixed(1)},${sy(g(x)).toFixed(1)}`
  }).join(' ')
}

const curve = path(f)

/** Recta de pendiente m por (x, y), de lado a lado del gráfico. */
function line(x, y, m) {
  return { x1: sx(X_MIN), y1: sy(y + m * (X_MIN - x)), x2: sx(X_MAX), y2: sy(y + m * (X_MAX - x)) }
}

const f0 = f(X0)
const tangent = line(X0, f0, EXACT)
const forwardSlope = computed(() => (f(X0 + h.value) - f0) / h.value)
const secant = computed(() => line(X0, f0, forwardSlope.value))

const nodes = computed(() => formula.value.offsets.map((o) => ({ o, x: X0 + o * h.value })))

/** Polinomio de Lagrange de grado 2 por los 3 puntos. */
const parabola = computed(() => {
  const xs = nodes.value.map((p) => p.x)
  const lagrange = (x) =>
    xs.reduce((sum, xj, j) => {
      const basis = xs.reduce((prod, xm, m) => (m === j ? prod : (prod * (x - xm)) / (xj - xm)), 1)
      return sum + f(xj) * basis
    }, 0)
  return path(lagrange)
})

/** Valores en vivo de las tres fórmulas con el h elegido. */
const live = computed(() => {
  const at = (o) => f(X0 + o * h.value)
  const values = {
    med: (at(1) - at(-1)) / (2 * h.value),
    ad: (-3 * at(0) + 4 * at(1) - at(2)) / (2 * h.value),
    at: (3 * at(0) - 4 * at(-1) + at(-2)) / (2 * h.value),
  }
  return FORMULAS.map((item) => ({ ...item, value: formatNumber(values[item.key]) }))
})

const label = (o) => (o === 0 ? 'x₀' : `x₀ ${o > 0 ? '+' : '−'} ${Math.abs(o) === 1 ? '' : Math.abs(o)}h`)
</script>

<template>
  <figure class="parabola-figure">
    <div class="formula-picker" role="radiogroup" aria-label="Fórmula de la figura">
      <label v-for="item in FORMULAS" :key="item.key" class="picker-option">
        <input v-model="selected" type="radio" name="parabola-formula" :value="item.key" />
        {{ item.name }}
      </label>
    </div>

    <svg
      viewBox="0 0 560 330"
      role="img"
      :aria-label="`Curva ln x cerca de x₀ = 1.8 con su tangente, la parábola por los 3 puntos del ${formula.name.toLowerCase()} y la secante progresiva`"
    >
      <defs>
        <clipPath id="parabola-plot">
          <rect :x="BOX.left" :y="BOX.top" :width="BOX.right - BOX.left" :height="BOX.bottom - BOX.top" />
        </clipPath>
      </defs>

      <line class="axis" :x1="BOX.left" :y1="BOX.bottom" :x2="BOX.right" :y2="BOX.bottom" />

      <g clip-path="url(#parabola-plot)">
        <line class="secant" v-bind="secant" />
        <line class="tangent" v-bind="tangent" />
        <polyline class="curve" :points="curve" />
        <polyline class="parabola" :points="parabola" />
      </g>

      <g v-for="p in nodes" :key="p.o">
        <line class="guide" :x1="sx(p.x)" :y1="sy(f(p.x))" :x2="sx(p.x)" :y2="BOX.bottom" />
        <line class="tick" :x1="sx(p.x)" :y1="BOX.bottom - 4" :x2="sx(p.x)" :y2="BOX.bottom + 4" />
        <circle :class="['dot', p.o === 0 ? 'dot-center' : 'dot-node']" :cx="sx(p.x)" :cy="sy(f(p.x))" r="4.5" />
      </g>
      <!-- Con h pequeño los rótulos se encimarían: sólo se rotula x₀. -->
      <template v-if="h >= 0.2">
        <text v-for="p in nodes" :key="`t${p.o}`" class="tick-label" :x="sx(p.x)" :y="BOX.bottom + 22" text-anchor="middle">
          {{ label(p.o) }}
        </text>
      </template>
      <text v-else class="tick-label" :x="sx(X0)" :y="BOX.bottom + 22" text-anchor="middle">x₀</text>

      <text class="curve-label" :x="sx(0.95)" :y="sy(1.02)">f(x) = ln x</text>
    </svg>

    <figcaption>
      <ul class="figure-legend">
        <li><span class="swatch swatch-curve"></span>Curva <MathFormula expression="f(x) = \ln x" /></li>
        <li><span class="swatch swatch-tangent"></span>Tangente en <MathFormula expression="x_0" /> (pendiente <MathFormula expression="f'(x_0)" />)</li>
        <li><span class="swatch swatch-parabola"></span>Parábola por los 3 puntos ({{ formula.name.toLowerCase() }})</li>
        <li><span class="swatch swatch-secant"></span>Secante progresiva (2 puntos), como referencia</li>
      </ul>

      <label class="h-control">
        <span>Paso <MathFormula :expression="`h = ${h}`" /></span>
        <input
          v-model.number="index"
          type="range"
          min="0"
          :max="H_VALUES.length - 1"
          step="1"
          :aria-valuetext="`h = ${h}`"
        />
      </label>

      <div class="live-values">
        <span v-for="item in live" :key="item.key" :class="['live', { 'live-selected': item.key === selected }]">
          <MathFormula :expression="`${item.symbol} = ${item.value}`" />
        </span>
        <span class="live"><MathFormula :expression="`f'(1.8) = ${formatNumber(EXACT)}`" /></span>
        <span class="live secant-text"><MathFormula :expression="`D^{+} = ${formatNumber(forwardSlope)}`" /></span>
      </div>
      <p class="figure-note">
        La aproximación es la pendiente de la parábola en <MathFormula expression="x_0" />. La parábola
        se pega a la curva mucho más que la secante, y por eso su pendiente se acerca más a la de la
        tangente. Calculado en el navegador con <code>Math.log</code>, sólo como ilustración.
      </p>
    </figcaption>
  </figure>
</template>

<style scoped>
.parabola-figure {
  margin: var(--space-3) 0 var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
}

svg {
  display: block;
  width: 100%;
  max-width: 720px;
  height: auto;
  margin: var(--space-3) auto 0;
}

.formula-picker {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
  color: var(--color-ink);
}

.picker-option {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.picker-option input {
  accent-color: var(--color-accent);
}

.axis,
.tick {
  stroke: var(--color-ink-muted);
  stroke-width: 1.2;
}

.guide {
  stroke: var(--color-line);
  stroke-dasharray: 3 4;
}

.curve {
  fill: none;
  stroke: var(--color-ink);
  stroke-width: 2.5;
}

.tangent {
  stroke: var(--color-ink-muted);
  stroke-width: 1.6;
  stroke-dasharray: 7 5;
}

.parabola {
  fill: none;
  stroke: var(--color-series-5);
  stroke-width: 2;
  stroke-dasharray: 2 3;
}

.secant {
  stroke: var(--color-series-1);
  stroke-width: 1.6;
  opacity: 0.4;
}

.dot {
  stroke: var(--color-surface);
  stroke-width: 1.5;
}

.dot-center {
  fill: var(--color-ink);
}

.dot-node {
  fill: var(--color-series-5);
}

.tick-label,
.curve-label {
  fill: var(--color-ink-muted);
  font-size: 14px;
}

/* El SVG se escala con el ancho: en móvil el texto necesita más unidades. */
@media (max-width: 480px) {
  .tick-label,
  .curve-label {
    font-size: 22px;
  }
}

.figure-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
  margin: var(--space-3) 0 0;
  padding: 0 !important;
  list-style: none;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.figure-legend li {
  margin: 0 !important;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.swatch {
  display: inline-block;
  width: 22px;
  height: 0;
  border-top: 3px solid;
}

.swatch-curve {
  border-color: var(--color-ink);
}

.swatch-tangent {
  border-top: 2px dashed var(--color-ink-muted);
}

.swatch-parabola {
  border-top: 3px dotted var(--color-series-5);
}

.swatch-secant {
  border-color: var(--color-series-1);
  opacity: 0.4;
}

.h-control {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-3);
  margin: var(--space-3) 0 0;
  color: var(--color-ink);
}

.h-control input {
  flex: 1 1 200px;
  accent-color: var(--color-accent);
}

.live-values {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-5);
  margin-top: var(--space-3);
}

.live-selected {
  color: var(--color-series-5);
  font-weight: var(--weight-semibold);
}

.secant-text {
  color: var(--color-ink-muted);
}

.figure-note {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
