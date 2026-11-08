<script setup>
// Gráfico de una regla de integración: la curva f(x) y, debajo, los paneles
// de la regla (trapecios: la poligonal que une los puntos (xᵢ, f(xᵢ))),
// sombreados hasta el eje con un color sobre el eje y otro debajo (f < 0).
// Con `row.pieces` (Simpson) cada panel es la parábola o la cúbica que manda
// el backend, alternando dos tonos para que se vea dónde empieza y termina.
//
//   curve   { x: [...], y: [...] } muestreada por el backend, o null (tabla sin función)
//   row     { n, x: [...], y: [...], pieces?: [{ rule, x: [...], y: [...] }] }
//   partLabels  { [rule]: texto }: con más de una regla (combinación 1/3 + 3/8),
//               cada parte con su color y su entrada en la leyenda
//   areaLabel / curveLabel  textos de la leyenda (área de la fila, integral exacta)
//
// Mismo tratamiento de colores y de la imagen del PDF que ConvergenceChart.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'
import { useTheme } from '../composables/useTheme'
import { formatNumber } from '../utils/iterationSteps'

const props = defineProps({
  curve: { type: Object, default: null },
  row: { type: Object, required: true },
  title: { type: String, default: 'Trapecios' },
  areaLabel: { type: String, required: true },
  curveLabel: { type: String, default: 'f(x)' },
  partLabels: { type: Object, default: null },
})

const canvasRef = ref(null)
let chart = null
const { theme } = useTheme()

const TOKENS = [
  '--color-ink',
  '--color-ink-muted',
  '--color-surface',
  '--color-line',
  '--color-chart-grid',
  '--color-series-1',
  '--color-series-2',
  '--color-series-3',
  '--color-area-positive',
  '--color-area-negative',
  '--color-area-positive-alt',
  '--color-area-negative-alt',
  '--color-area-part2',
  '--color-area-part2-alt',
]

function readPalette(forcedTheme = null) {
  let source = document.documentElement
  if (forcedTheme) {
    source = document.createElement('div')
    source.dataset.theme = forcedTheme
    source.hidden = true
    document.body.append(source)
  }
  const style = getComputedStyle(source)
  const palette = Object.fromEntries(TOKENS.map((token) => [token, style.getPropertyValue(token).trim()]))
  if (forcedTheme) source.remove()
  return palette
}

// Series auxiliares, sin entrada en la leyenda.
const HIDDEN = ['bordes', 'puntos']

const finite = (value) => (value !== null && value !== undefined && Number.isFinite(value) ? value : null)

// Parábolas o cúbicas: una serie por pieza, sin entrada propia en la leyenda
// (label ''), salvo la primera de cada parte.
function pieceDatasets(palette) {
  const { x, y, pieces } = props.row
  const rules = [...new Set(pieces.map((p) => p.rule))]
  const second = (rule) => props.partLabels && rules.indexOf(rule) === 1
  const named = new Set()
  const datasets = pieces.map((piece, j) => {
    const alt = j % 2 === 1
    const part2 = second(piece.rule)
    const line = palette[part2 ? '--color-series-2' : '--color-series-1']
    let label = ''
    if (!named.has(piece.rule)) {
      named.add(piece.rule)
      label = props.partLabels ? props.partLabels[piece.rule] : props.areaLabel
    }
    return {
      label,
      data: piece.x.map((xi, i) => ({ x: xi, y: piece.y[i] })),
      borderColor: line,
      backgroundColor: palette[part2 ? '--color-area-part2' : '--color-area-positive'],
      borderWidth: 1.5,
      pointRadius: 0,
      tension: 0,
      fill: {
        target: 'origin',
        above: palette[part2 ? (alt ? '--color-area-part2-alt' : '--color-area-part2') : alt ? '--color-area-positive-alt' : '--color-area-positive'],
        below: palette[alt ? '--color-area-negative-alt' : '--color-area-negative'],
      },
      order: 2,
    }
  })
  const edges = [...new Set(pieces.flatMap((p) => [p.x[0], p.x.at(-1)]))]
  datasets.push(
    {
      // Lados verticales donde empieza y termina cada pieza.
      label: 'bordes',
      data: edges.flatMap((xi) => {
        const i = x.findIndex((v) => Math.abs(v - xi) <= 1e-12 * Math.max(1, Math.abs(xi)))
        return [{ x: xi, y: 0 }, { x: xi, y: i >= 0 ? y[i] : 0 }, { x: xi, y: null }]
      }),
      borderColor: palette['--color-series-1'],
      borderWidth: 1,
      pointRadius: 0,
      spanGaps: false,
      fill: false,
      order: 1,
    },
    {
      label: 'puntos',
      data: x.map((xi, i) => ({ x: xi, y: y[i] })),
      borderColor: palette['--color-series-1'],
      backgroundColor: palette['--color-series-1'],
      showLine: false,
      pointRadius: x.length > 33 ? 1.5 : 3,
      fill: false,
      order: 1,
    }
  )
  return datasets
}

function buildData(palette) {
  const { x, y } = props.row
  const datasets = props.row.pieces ? pieceDatasets(palette) : [
    {
      label: props.areaLabel,
      data: x.map((xi, i) => ({ x: xi, y: y[i] })),
      borderColor: palette['--color-series-1'],
      backgroundColor: palette['--color-series-1'],
      borderWidth: 1.5,
      pointRadius: x.length > 33 ? 1.5 : 3,
      tension: 0,
      fill: { target: 'origin', above: palette['--color-area-positive'], below: palette['--color-area-negative'] },
      order: 2,
    },
    {
      // Lados verticales de cada trapecio; los null separan los segmentos.
      label: 'bordes',
      data: x.flatMap((xi, i) => [{ x: xi, y: 0 }, { x: xi, y: y[i] }, { x: xi, y: null }]),
      borderColor: palette['--color-series-1'],
      borderWidth: 1,
      pointRadius: 0,
      spanGaps: false,
      fill: false,
      order: 1,
    },
  ]
  if (props.curve) {
    datasets.push({
      label: props.curveLabel,
      data: props.curve.x.map((xi, i) => ({ x: xi, y: finite(props.curve.y[i]) })),
      borderColor: palette['--color-series-3'],
      backgroundColor: palette['--color-series-3'],
      borderWidth: 2,
      pointRadius: 0,
      tension: 0,
      spanGaps: false,
      fill: false,
      order: 0,
    })
  }
  return { datasets }
}

function buildOptions(palette) {
  const text = palette['--color-ink-muted']
  const axis = {
    type: 'linear',
    grid: { color: palette['--color-chart-grid'] },
    border: { color: palette['--color-line'] },
    ticks: { color: text, callback: (value) => formatNumber(value) },
  }
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    color: text,
    parsing: true,
    interaction: { mode: 'nearest', intersect: false },
    scales: {
      x: { ...axis, title: { display: true, text: 'x', color: text } },
      y: { ...axis, title: { display: true, text: 'f(x)', color: text } },
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 14,
          font: { size: 11 },
          color: text,
          filter: (item) => item.text && !HIDDEN.includes(item.text),
        },
      },
      tooltip: {
        backgroundColor: palette['--color-ink'],
        titleColor: palette['--color-surface'],
        bodyColor: palette['--color-surface'],
        filter: (item) => item.dataset.label !== 'bordes',
        callbacks: {
          title: (items) => `x = ${formatNumber(items[0].parsed.x)}`,
          label: (item) => `f(x) = ${formatNumber(item.parsed.y)}`,
        },
      },
    },
  }
}

function render(palette) {
  chart.data = buildData(palette)
  chart.options = buildOptions(palette)
  chart.update()
}

// El PDF siempre es claro (mismo procedimiento que ConvergenceChart).
function toImage() {
  if (!chart) return null
  const dark = theme.value === 'dark'
  if (dark) render(readPalette('light'))
  const source = chart.canvas
  const target = document.createElement('canvas')
  target.width = source.width
  target.height = source.height
  const ctx = target.getContext('2d')
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, target.width, target.height)
  ctx.drawImage(source, 0, 0)
  if (dark) render(readPalette())
  return { dataUrl: target.toDataURL('image/png'), width: target.width, height: target.height }
}

defineExpose({ toImage })

onMounted(() => {
  const palette = readPalette()
  chart = new Chart(canvasRef.value, { type: 'line', data: buildData(palette), options: buildOptions(palette) })
})

watch([() => props.row, () => props.curve, () => props.areaLabel, () => props.partLabels, theme], () => {
  if (chart) render(readPalette())
})

onBeforeUnmount(() => {
  if (chart) chart.destroy()
  chart = null
})
</script>

<template>
  <div class="chart-block">
    <h4 class="chart-title">{{ title }}</h4>
    <slot />
    <div class="chart-canvas-wrapper">
      <canvas ref="canvasRef" role="img" :aria-label="`${title}. ${areaLabel}`"></canvas>
    </div>
  </div>
</template>

<style scoped>
.chart-block {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
}

.chart-title {
  margin: 0 0 var(--space-3);
  font-size: var(--text-subsection);
  color: var(--color-ink);
}

.chart-canvas-wrapper {
  position: relative;
  height: 320px;
}
</style>
