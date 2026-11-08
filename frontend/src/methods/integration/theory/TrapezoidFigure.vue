<script setup>
// Interpretación geométrica: la curva f(x), las piezas de la regla sombreadas
// (trapecios; con `rules`, también parábolas de Simpson 1/3 o cúbicas de 3/8,
// alternando dos tonos) y, con otro color tenue, lo que la regla pierde (curva
// por encima de la pieza) y lo que agrega (pieza por encima de la curva).
// Un selector elige n y, con `rules`, otro elige la regla.
// Los valores se calculan aquí con JavaScript: es sólo ilustrativo (el ejemplo
// resuelto usa los datos del solver). Colores de theme.css: sigue el tema.
import { computed, ref, watch } from 'vue'
import MathFormula from '../../../components/MathFormula.vue'
import { formatNumber } from '../../../utils/iterationSteps'

const props = defineProps({
  f: { type: Function, required: true },
  a: { type: Number, required: true },
  b: { type: Number, required: true },
  exact: { type: Number, required: true },
  // Valores de n del trapecio (sin `rules`).
  nValues: { type: Array, default: null },
  // [{ key: 'trapecio' | 'simpson13' | 'simpson38', nValues }]: agrega el selector de regla.
  rules: { type: Array, default: null },
  // [{ x, label }] marcas del eje x
  ticks: { type: Array, required: true },
  label: { type: String, required: true },
  compact: { type: Boolean, default: false },
})

// Cada pieza es el polinomio que pasa por degree + 1 puntos seguidos; el área
// de la regla compuesta es factor·h·Σ wⱼ·f(xⱼ), pieza por pieza.
const RULES = {
  trapecio: {
    name: 'Trapecio',
    degree: 1,
    weights: [1, 1],
    factor: 1 / 2,
    value: 'T',
    pieces: 'Trapecios',
    shape: 'la recta',
    subject: 'el trapecio',
    units: 'trapecios',
  },
  simpson13: {
    name: 'Simpson 1/3',
    degree: 2,
    weights: [1, 4, 1],
    factor: 1 / 3,
    value: 'S',
    pieces: 'Parábolas',
    shape: 'la parábola',
    subject: 'Simpson',
    units: 'segmentos',
  },
  simpson38: {
    name: 'Simpson 3/8',
    degree: 3,
    weights: [1, 3, 3, 1],
    factor: 3 / 8,
    value: 'S',
    pieces: 'Cúbicas',
    shape: 'la cúbica',
    subject: 'Simpson',
    units: 'segmentos',
  },
}
const choices = props.rules ?? [{ key: 'trapecio', nValues: props.nValues }]

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

const ruleKey = ref(choices[0].key)
const choice = computed(() => choices.find((c) => c.key === ruleKey.value))
const rule = computed(() => RULES[ruleKey.value])
const n = ref(choices[0].nValues[0])
watch(ruleKey, () => {
  n.value = choice.value.nValues[0]
})

/** Polinomio de interpolación (Lagrange) por los nodos (xs, fs), evaluado en x. */
function lagrange(xs, fs, x) {
  let sum = 0
  for (let i = 0; i < xs.length; i++) {
    let term = fs[i]
    for (let j = 0; j < xs.length; j++) if (j !== i) term *= (x - xs[j]) / (xs[i] - xs[j])
    sum += term
  }
  return sum
}

/** Área de la regla compuesta con n segmentos. */
function ruleArea(count) {
  const { degree, weights, factor } = rule.value
  const h = (props.b - props.a) / count
  let sum = 0
  for (let start = 0; start < count; start += degree) {
    weights.forEach((w, j) => {
      sum += w * props.f(props.a + (start + j) * h)
    })
  }
  return factor * h * sum
}

const shapes = computed(() => {
  const count = n.value
  const { degree } = rule.value
  const h = (props.b - props.a) / count
  const pieces = []
  const lost = []
  const added = []
  for (let start = 0; start < count; start += degree) {
    const xs = Array.from({ length: degree + 1 }, (_, j) => props.a + (start + j) * h)
    const fs = xs.map((x) => props.f(x))
    const x0 = xs[0]
    const x1 = xs[degree]
    // Entre la pieza y la curva: max(f, pieza) arriba (lo que se pierde) y
    // min(f, pieza) abajo (lo que se agrega), cada uno cerrado con la pieza.
    const steps = Math.max(8, Math.ceil((SAMPLES * degree) / count))
    const top = []
    const bottom = []
    const outline = []
    for (let j = 0; j <= steps; j++) {
      const x = x0 + ((x1 - x0) * j) / steps
      const fx = props.f(x)
      const p = degree === 1 ? fs[0] + ((fs[1] - fs[0]) * j) / steps : lagrange(xs, fs, x)
      top.push(pt(x, Math.max(fx, p)))
      bottom.push(pt(x, Math.min(fx, p)))
      outline.push(pt(x, p))
    }
    const back = outline.slice().reverse()
    const edge = degree === 1 ? [pt(x0, fs[0]), pt(x1, fs[1])] : outline
    pieces.push([pt(x0, 0), ...edge, pt(x1, 0)].join(' '))
    lost.push([...top, ...back].join(' '))
    added.push([...bottom, ...back].join(' '))
  }
  return { pieces, lost, added }
})

const area = computed(() => ruleArea(n.value))
const error = computed(() => props.exact - area.value)
const reading = computed(() => {
  const e = error.value
  if (formatNumber(e) === '0') return 'con 6 decimales, el área coincide con la exacta.'
  const who = rule.value.subject
  return e > 0 ? `${who} subestima (se queda corto).` : `${who} sobreestima (se pasa).`
})
</script>

<template>
  <figure class="trapezoid-figure" :class="{ compact }">
    <svg
      :viewBox="`0 0 560 ${height}`"
      role="img"
      :aria-label="`${label}: ${rules ? `${rule.name}, ` : ''}${n} ${rule.units}, área ${formatNumber(area)}`"
    >
      <polygon
        v-for="(p, i) in shapes.pieces"
        :key="`t${i}`"
        class="trap"
        :class="{ alt: rules && i % 2 === 1 }"
        :points="p"
      />
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
      <div v-if="rules" class="n-picker" role="radiogroup" :aria-label="`Regla para ${label}`">
        <span class="picker-label">Regla:</span>
        <button
          v-for="c in rules"
          :key="c.key"
          type="button"
          role="radio"
          class="n-btn"
          :class="{ 'is-active': c.key === ruleKey }"
          :aria-checked="c.key === ruleKey"
          @click="ruleKey = c.key"
        >
          {{ RULES[c.key].name }}
        </button>
      </div>
      <div class="n-picker" role="radiogroup" :aria-label="`Número de ${rule.units} de ${label}`">
        <span class="picker-label">Segmentos:</span>
        <button
          v-for="value in choice.nValues"
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
        <span class="live"><MathFormula :expression="`${rule.value} = ${formatNumber(area)}`" /></span>
        <span class="live"><MathFormula :expression="`I = ${formatNumber(exact)}`" /></span>
        <span class="live"><MathFormula :expression="`E_t = I - ${rule.value} = ${formatNumber(error)}`" /></span>
      </div>
      <p class="figure-note">Con n = {{ n }}, {{ reading }}</p>

      <ul class="figure-legend">
        <li><span class="swatch swatch-curve"></span>{{ label }}</li>
        <li><span class="box box-trap"></span>{{ rule.pieces }} (área {{ rule.value }})</li>
        <li><span class="box box-lost"></span>Lo que se pierde (la curva está por encima)</li>
        <li><span class="box box-added"></span>Lo que se agrega ({{ rule.shape }} está por encima)</li>
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

.trap.alt {
  fill: var(--color-area-positive-alt);
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
