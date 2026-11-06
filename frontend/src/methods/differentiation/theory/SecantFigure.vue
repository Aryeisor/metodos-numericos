<script setup>
// Interpretación geométrica: f(x) = ln x cerca de x₀ = 1.8, su recta tangente
// y las secantes progresiva y regresiva, con un deslizador de h. Los valores
// se calculan aquí con Math.log: es sólo ilustrativo (el ejemplo resuelto usa
// los datos del solver). Colores de theme.css, así que sigue el tema.
import { computed, ref } from 'vue'
import MathFormula from '../../../components/MathFormula.vue'
import { formatNumber } from '../../../utils/iterationSteps'

const H_VALUES = [0.4, 0.2, 0.1, 0.05, 0.025, 0.0125]
const X0 = 1.8
const EXACT = 1 / X0

// Ventana del gráfico (en unidades de x, y) y su caja en el SVG.
const X_MIN = 1.3
const X_MAX = 2.3
const Y_MIN = 0.25
const Y_MAX = 0.85
const BOX = { left: 16, right: 544, top: 12, bottom: 290 }

const sx = (x) => BOX.left + ((x - X_MIN) / (X_MAX - X_MIN)) * (BOX.right - BOX.left)
const sy = (y) => BOX.bottom - ((y - Y_MIN) / (Y_MAX - Y_MIN)) * (BOX.bottom - BOX.top)

const index = ref(0)
const h = computed(() => H_VALUES[index.value])

const curve = Array.from({ length: 101 }, (_, i) => {
  const x = X_MIN + ((X_MAX - X_MIN) * i) / 100
  return `${sx(x).toFixed(1)},${sy(Math.log(x)).toFixed(1)}`
}).join(' ')

/** Recta de pendiente m por (x, y), de lado a lado del gráfico. */
function line(x, y, m) {
  return {
    x1: sx(X_MIN),
    y1: sy(y + m * (X_MIN - x)),
    x2: sx(X_MAX),
    y2: sy(y + m * (X_MAX - x)),
  }
}

const f0 = Math.log(X0)
const forward = computed(() => (Math.log(X0 + h.value) - f0) / h.value)
const backward = computed(() => (f0 - Math.log(X0 - h.value)) / h.value)
const tangent = line(X0, f0, EXACT)
const forwardLine = computed(() => line(X0, f0, forward.value))
const backwardLine = computed(() => line(X0, f0, backward.value))

const points = computed(() => [
  { x: X0 - h.value, label: 'x₀ − h' },
  { x: X0, label: 'x₀' },
  { x: X0 + h.value, label: 'x₀ + h' },
])
</script>

<template>
  <figure class="secant-figure">
    <svg
      viewBox="0 0 560 330"
      role="img"
      aria-label="Curva ln x cerca de x₀ = 1.8 con su recta tangente y las secantes progresiva y regresiva"
    >
      <defs>
        <clipPath id="secant-plot">
          <rect :x="BOX.left" :y="BOX.top" :width="BOX.right - BOX.left" :height="BOX.bottom - BOX.top" />
        </clipPath>
      </defs>

      <line class="axis" :x1="BOX.left" :y1="BOX.bottom" :x2="BOX.right" :y2="BOX.bottom" />

      <g clip-path="url(#secant-plot)">
        <line class="tangent" v-bind="tangent" />
        <line class="backward" v-bind="backwardLine" />
        <line class="forward" v-bind="forwardLine" />
        <polyline class="curve" :points="curve" />
      </g>

      <g v-for="(p, i) in points" :key="i">
        <line class="guide" :x1="sx(p.x)" :y1="sy(Math.log(p.x))" :x2="sx(p.x)" :y2="BOX.bottom" />
        <line class="tick" :x1="sx(p.x)" :y1="BOX.bottom - 4" :x2="sx(p.x)" :y2="BOX.bottom + 4" />
        <circle
          :class="['dot', i === 0 ? 'dot-backward' : i === 2 ? 'dot-forward' : 'dot-center']"
          :cx="sx(p.x)"
          :cy="sy(Math.log(p.x))"
          r="4.5"
        />
        <text class="tick-label" :x="sx(p.x)" :y="BOX.bottom + 22" text-anchor="middle">{{ p.label }}</text>
      </g>

      <text class="curve-label" :x="sx(1.33)" :y="sy(0.8)">f(x) = ln x</text>
    </svg>

    <figcaption>
      <ul class="figure-legend">
        <li><span class="swatch swatch-tangent"></span>Tangente en <MathFormula expression="x_0" /> (pendiente <MathFormula expression="f'(x_0)" />)</li>
        <li><span class="swatch swatch-forward"></span>Secante progresiva (hacia la derecha)</li>
        <li><span class="swatch swatch-backward"></span>Secante regresiva (hacia la izquierda)</li>
      </ul>

      <label class="h-control">
        <span>
          Paso <MathFormula :expression="`h = ${h}`" />
        </span>
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
        <span class="live forward-text"><MathFormula :expression="`D^{+} = ${formatNumber(forward)}`" /></span>
        <span class="live"><MathFormula :expression="`f'(1.8) = ${formatNumber(EXACT)}`" /></span>
        <span class="live backward-text"><MathFormula :expression="`D^{-} = ${formatNumber(backward)}`" /></span>
      </div>
      <p class="figure-note">
        Al reducir <MathFormula expression="h" />, las dos secantes giran hacia la tangente.
        Calculado en el navegador con <code>Math.log</code>, sólo como ilustración.
      </p>
    </figcaption>
  </figure>
</template>

<style scoped>
.secant-figure {
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
  margin: 0 auto;
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

.forward {
  stroke: var(--color-series-1);
  stroke-width: 2;
}

.backward {
  stroke: var(--color-series-2);
  stroke-width: 2;
}

.dot {
  stroke: var(--color-surface);
  stroke-width: 1.5;
}

.dot-center {
  fill: var(--color-ink);
}

.dot-forward {
  fill: var(--color-series-1);
}

.dot-backward {
  fill: var(--color-series-2);
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
    font-size: 24px;
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

.swatch-tangent {
  border-top: 2px dashed var(--color-ink-muted);
}

.swatch-forward {
  border-color: var(--color-series-1);
}

.swatch-backward {
  border-color: var(--color-series-2);
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

.forward-text {
  color: var(--color-series-1);
}

.backward-text {
  color: var(--color-series-2);
}

.figure-note {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
