<script setup>
// Comparación de dónde evalúan Simpson 1/3 y Gauss de 3 puntos sobre la misma
// curva (Chapra en [0, 0.8]): un panel por regla, con el peso escrito sobre
// cada punto (en la escala de [−1, 1], donde los pesos suman 2).
// Colores de theme.css: sigue el tema.
const f = (x) => 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5
const A = 0
const B = 0.8
const W = 560
const PANEL = 150
const LEFT = 30
const RIGHT = W - 30
const Y_MAX = 4
const sx = (x) => LEFT + ((x - A) / (B - A)) * (RIGHT - LEFT)
const sy = (y, top) => top + PANEL - 26 - (y / Y_MAX) * (PANEL - 50)

const S = Math.sqrt(3 / 5)
const PANELS = [
  {
    title: 'Simpson 1/3: extremos y centro',
    cls: 'simpson',
    points: [
      { t: -1, w: '1/3' },
      { t: 0, w: '4/3' },
      { t: 1, w: '1/3' },
    ],
  },
  {
    title: 'Gauss, 3 puntos: nunca toca los extremos',
    cls: 'gauss',
    points: [
      { t: -S, w: '5/9' },
      { t: 0, w: '8/9' },
      { t: S, w: '5/9' },
    ],
  },
].map((panel, idx) => {
  const top = idx * PANEL
  const curve = Array.from({ length: 81 }, (_, i) => {
    const x = A + ((B - A) * i) / 80
    return `${sx(x).toFixed(1)},${sy(f(x), top).toFixed(1)}`
  }).join(' ')
  const points = panel.points.map((p) => {
    const x = (B + A) / 2 + ((B - A) / 2) * p.t
    return { ...p, cx: sx(x), cy: sy(f(x), top), base: sy(0, top) }
  })
  return { ...panel, top, curve, points, axis: sy(0, top) }
})
</script>

<template>
  <figure class="nodes-figure">
    <svg
      :viewBox="`0 0 ${W} ${PANEL * 2}`"
      role="img"
      aria-label="Simpson evalúa en 0, 0.4 y 0.8 con pesos 1/3, 4/3 y 1/3; Gauss evalúa en 0.09, 0.4 y 0.71 con pesos 5/9, 8/9 y 5/9"
    >
      <g v-for="p in PANELS" :key="p.cls">
        <text class="panel-title" :x="LEFT" :y="p.top + 16">{{ p.title }}</text>
        <line class="axis" :x1="LEFT" :y1="p.axis" :x2="RIGHT" :y2="p.axis" />
        <line class="end" :x1="sx(A)" :y1="p.top + 24" :x2="sx(A)" :y2="p.axis" />
        <line class="end" :x1="sx(B)" :y1="p.top + 24" :x2="sx(B)" :y2="p.axis" />
        <polyline class="curve" :points="p.curve" />
        <g v-for="(pt, i) in p.points" :key="i">
          <line class="stem" :class="p.cls" :x1="pt.cx" :y1="pt.base" :x2="pt.cx" :y2="pt.cy" />
          <circle class="dot" :class="p.cls" :cx="pt.cx" :cy="pt.cy" r="6" />
          <text class="weight" :x="pt.cx + 6 * Math.sign(-pt.t) * (Math.abs(pt.t) === 1)" :y="pt.cy - 12" :text-anchor="pt.t === -1 ? 'start' : pt.t === 1 ? 'end' : 'middle'">w = {{ pt.w }}</text>
        </g>
        <text class="tick" :x="sx(A)" :y="p.axis + 18" text-anchor="middle">a = 0</text>
        <text class="tick" :x="sx(B)" :y="p.axis + 18" text-anchor="middle">b = 0.8</text>
      </g>
    </svg>
    <figcaption>
      Los dos usan 3 evaluaciones. Simpson gasta dos en los extremos; Gauss las mueve hacia adentro
      (x ≈ 0.09, 0.4 y 0.71). Con el mismo número de evaluaciones, Gauss ubica mejor los puntos. Los pesos están
      en la escala de [−1, 1], donde suman 2.
    </figcaption>
  </figure>
</template>

<style scoped>
.nodes-figure {
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

.axis {
  stroke: var(--color-ink-muted);
  stroke-width: 1.2;
}

.end {
  stroke: var(--color-line-strong);
  stroke-dasharray: 4 4;
}

.curve {
  fill: none;
  stroke: var(--color-ink);
  stroke-width: 2.5;
}

.stem {
  stroke-width: 1.5;
  stroke-dasharray: 3 3;
}

.stem.simpson,
.dot.simpson {
  stroke: var(--color-series-3);
}

.stem.gauss,
.dot.gauss {
  stroke: var(--color-series-1);
}

.dot.simpson {
  fill: var(--color-series-3);
}

.dot.gauss {
  fill: var(--color-series-1);
}

.panel-title,
.weight {
  fill: var(--color-ink);
  font-size: 14px;
}

.panel-title {
  font-weight: var(--weight-semibold);
}

.tick {
  fill: var(--color-ink-muted);
  font-size: 13px;
}

@media (max-width: 480px) {
  .panel-title,
  .weight {
    font-size: 22px;
  }

  .tick {
    font-size: 20px;
  }
}

figcaption {
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
