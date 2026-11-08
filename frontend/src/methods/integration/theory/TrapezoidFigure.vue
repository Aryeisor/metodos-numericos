<script setup>
// Interpretación geométrica: la curva f(x), los n trapecios sombreados y, con
// otro color tenue, lo que el trapecio pierde (curva por encima de la recta)
// y lo que agrega (recta por encima de la curva). Un selector elige n.
// Los valores se calculan aquí con JavaScript: es sólo ilustrativo (el ejemplo
// resuelto usa los datos del solver). Colores de theme.css: sigue el tema.
import { computed, ref } from 'vue'
import MathFormula from '../../../components/MathFormula.vue'
import { formatNumber } from '../../../utils/iterationSteps'

const props = defineProps({
  f: { type: Function, required: true },
  a: { type: Number, required: true },
  b: { type: Number, required: true },
  exact: { type: Number, required: true },
  nValues: { type: Array, required: true },
  // [{ x, label }] marcas del eje x
  ticks: { type: Array, required: true },
  label: { type: String, required: true },
  compact: { type: Boolean, default: false },
})

const SAMPLES = 240
const BOX = { left: 12, right: 548, top: 14, bottom: 0 }
const height = props.compact ? 240 : 320
BOX.bottom = height - 34

const curvePoints = Array.from({ length: SAMPLES + 1 }, (_, i) => {
  const x = props.a + ((props.b - props.a) * i) / SAMPLES
  return [x, props.f(x)]
})
const ys = curvePoints.map((p) => p[1])
const yMin = Math.min(0, ...ys)
const yMax = Math.max(0, ...ys) * 1.08

const sx = (x) => BOX.left + ((x - props.a) / (props.b - props.a)) * (BOX.right - BOX.left)
const sy = (y) => BOX.bottom - ((y - yMin) / (yMax - yMin)) * (BOX.bottom - BOX.top)
const pt = (x, y) => `${sx(x).toFixed(1)},${sy(y).toFixed(1)}`

const curve = curvePoints.map(([x, y]) => pt(x, y)).join(' ')

const n = ref(props.nValues[0])

/** Área de los trapecios con n segmentos. */
function trapezoid(count) {
  const h = (props.b - props.a) / count
  let sum = (props.f(props.a) + props.f(props.b)) / 2
  for (let i = 1; i < count; i++) sum += props.f(props.a + i * h)
  return h * sum
}

const shapes = computed(() => {
  const count = n.value
  const h = (props.b - props.a) / count
  const traps = []
  const lost = []
  const added = []
  for (let i = 0; i < count; i++) {
    const x0 = props.a + i * h
    const x1 = x0 + h
    const y0 = props.f(x0)
    const y1 = props.f(x1)
    traps.push([pt(x0, 0), pt(x0, y0), pt(x1, y1), pt(x1, 0)].join(' '))
    // Entre la recta y la curva: max(f, recta) arriba (lo que se pierde) y
    // min(f, recta) abajo (lo que se agrega), cada uno cerrado con la recta.
    const steps = Math.max(8, Math.ceil(SAMPLES / count))
    const top = []
    const bottom = []
    const chord = []
    for (let j = 0; j <= steps; j++) {
      const x = x0 + (h * j) / steps
      const fx = props.f(x)
      const line = y0 + ((y1 - y0) * j) / steps
      top.push(pt(x, Math.max(fx, line)))
      bottom.push(pt(x, Math.min(fx, line)))
      chord.push(pt(x, line))
    }
    const back = chord.slice().reverse()
    lost.push([...top, ...back].join(' '))
    added.push([...bottom, ...back].join(' '))
  }
  return { traps, lost, added }
})

const area = computed(() => trapezoid(n.value))
const error = computed(() => props.exact - area.value)
const reading = computed(() => {
  const e = error.value
  if (formatNumber(e) === '0') return 'con 6 decimales, el área coincide con la exacta.'
  return e > 0 ? 'el trapecio subestima (se queda corto).' : 'el trapecio sobreestima (se pasa).'
})
</script>

<template>
  <figure class="trapezoid-figure" :class="{ compact }">
    <svg :viewBox="`0 0 560 ${height}`" role="img" :aria-label="`${label}: ${n} trapecios, área ${formatNumber(area)}`">
      <polygon v-for="(p, i) in shapes.traps" :key="`t${i}`" class="trap" :points="p" />
      <polygon v-for="(p, i) in shapes.lost" :key="`l${i}`" class="lost" :points="p" />
      <polygon v-for="(p, i) in shapes.added" :key="`a${i}`" class="added" :points="p" />
      <line class="axis" :x1="BOX.left" :y1="sy(0)" :x2="BOX.right" :y2="sy(0)" />
      <polyline class="curve" :points="curve" />
      <g v-for="t in ticks" :key="t.label">
        <line class="tick" :x1="sx(t.x)" :y1="sy(0) - 4" :x2="sx(t.x)" :y2="sy(0) + 4" />
        <text class="tick-label" :x="sx(t.x)" :y="BOX.bottom + 24" text-anchor="middle">{{ t.label }}</text>
      </g>
    </svg>

    <figcaption>
      <div class="n-picker" role="radiogroup" :aria-label="`Número de trapecios de ${label}`">
        <span class="picker-label">Segmentos:</span>
        <button
          v-for="value in nValues"
          :key="value"
          type="button"
          role="radio"
          class="n-btn"
          :class="{ 'is-active': value === n }"
          :aria-checked="value === n"
          @click="n = value"
        >
          n = {{ value }}
        </button>
      </div>

      <div class="live-values">
        <span class="live"><MathFormula :expression="`T = ${formatNumber(area)}`" /></span>
        <span class="live"><MathFormula :expression="`I = ${formatNumber(exact)}`" /></span>
        <span class="live"><MathFormula :expression="`E_t = I - T = ${formatNumber(error)}`" /></span>
      </div>
      <p class="figure-note">Con n = {{ n }}, {{ reading }}</p>

      <ul class="figure-legend">
        <li><span class="swatch swatch-curve"></span>{{ label }}</li>
        <li><span class="box box-trap"></span>Trapecios (área T)</li>
        <li><span class="box box-lost"></span>Lo que se pierde (la curva está por encima)</li>
        <li><span class="box box-added"></span>Lo que se agrega (la recta está por encima)</li>
      </ul>
    </figcaption>
  </figure>
</template>

<style scoped>
.trapezoid-figure {
  margin: var(--space-3) 0 var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
  min-width: 0;
}

svg {
  display: block;
  width: 100%;
  max-width: 720px;
  height: auto;
  margin: 0 auto;
}

.trap {
  fill: var(--color-area-positive);
  stroke: var(--color-series-1);
  stroke-width: 1.2;
}

.lost {
  fill: var(--color-series-3);
  fill-opacity: 0.35;
}

.added {
  fill: var(--color-series-5);
  fill-opacity: 0.35;
}

.axis,
.tick {
  stroke: var(--color-ink-muted);
  stroke-width: 1.2;
}

.curve {
  fill: none;
  stroke: var(--color-ink);
  stroke-width: 2.5;
}

.tick-label {
  fill: var(--color-ink-muted);
  font-size: 14px;
}

@media (max-width: 480px) {
  .tick-label {
    font-size: 24px;
  }
}

.n-picker {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.picker-label {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.n-btn {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  color: var(--color-ink);
  font-size: var(--text-small);
  cursor: pointer;
}

.n-btn:hover {
  background: var(--color-accent-soft);
}

.n-btn.is-active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
  font-weight: var(--weight-semibold);
}

.n-btn:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.live-values {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-5);
  margin-top: var(--space-3);
}

.figure-note {
  margin: var(--space-2) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
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
  border-top: 3px solid var(--color-ink);
}

.box {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 2px;
}

.box-trap {
  background: var(--color-area-positive);
  border: 1px solid var(--color-series-1);
}

.box-lost {
  background: var(--color-series-3);
  opacity: 0.45;
}

.box-added {
  background: var(--color-series-5);
  opacity: 0.45;
}
</style>
