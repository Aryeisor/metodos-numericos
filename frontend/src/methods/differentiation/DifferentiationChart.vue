<script setup>
// Gráfica de la aproximación (diferencias, 3 y 5 puntos): la curva f, la
// tangente exacta en x₀, los puntos que usa la fórmula, la curva que pasa por
// ellos (recta, parábola o polinomio de grado 4) y la recta aproximada, que
// tiene pendiente D y es tangente a esa curva en x₀. Todo lo calcula el
// backend (`result.chart`, ver solvers/differentiation/chart.py); aquí sólo
// se elige qué mostrar. Misma paleta, modo oscuro e imagen del PDF que
// TrapezoidChart.
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'
import GlossaryBlock from '../../components/GlossaryBlock.vue'
import { useTheme } from '../../composables/useTheme'
import { formatNumber } from '../../utils/iterationSteps'

const props = defineProps({
  chart: { type: Object, required: true },
  method: { type: String, required: true },
})

const isTable = computed(() => props.chart.mode === 'table')
const isDifferences = computed(() => props.method === 'diferencias-finitas')
const isFivePoint = computed(() => props.method === 'cinco-puntos')
const COMPARE = 'compare'

// --- Selección -------------------------------------------------------------------
const rowIndex = ref(0)
const formulaKey = ref(null)
const allSecants = ref(false)
function reset() {
  rowIndex.value = isTable.value ? props.chart.default_point - 1 : 0
  formulaKey.value = isTable.value ? row.value.default : Object.keys(row.value.formulas)[0]
  allSecants.value = false
}
const row = computed(() => props.chart.rows[rowIndex.value])
watch(() => props.chart, reset)
// En la tabla cada punto tiene sus fórmulas: si la elegida no aplica, la recomendada.
watch(rowIndex, () => {
  if (formulaKey.value !== COMPARE && !row.value.formulas[formulaKey.value]) formulaKey.value = row.value.default
})
reset()

const comparing = computed(() => formulaKey.value === COMPARE)
const piece = computed(() => (comparing.value ? null : row.value.formulas[formulaKey.value]))
const canCompare = computed(() => !isTable.value && row.value.compare.lines.length > 1)
const formulaOptions = computed(() => [
  ...Object.values(row.value.formulas).map((p) => ({ key: p.key, label: p.name })),
  ...(canCompare.value ? [{ key: COMPARE, label: 'Comparar' }] : []),
])
const rowOptions = computed(() =>
  props.chart.rows.map((r, i) =>
    isTable.value
      ? { index: i, label: `x${sub(r.i)} = ${formatNumber(r.x)}` }
      : { index: i, label: `Fila ${r.k} (h = ${hText(r.h)})` }
  )
)
const SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'
const sub = (n) => String(n).replace(/\d/g, (d) => SUBSCRIPTS[d])
const hText = (h) => (h.exact ? h.text : `${h.text} ≈ ${h.approx}`)
const shape = (p) => ({ 2: 'recta (secante)', 3: 'parábola', 5: 'polinomio de grado 4' })[p.points.length] ?? 'curva'

// --- Leyenda, lectura y descripción -------------------------------------------------
const exact = computed(() => {
  if (!isTable.value) return props.chart.exact
  const p = piece.value ?? Object.values(row.value.formulas)[0]
  return p.tangent ? (p.tangent[1][1] - p.tangent[0][1]) / (p.tangent[1][0] - p.tangent[0][0]) : null
})
const base = computed(() => (isTable.value ? `x${sub(row.value.i)}` : 'x₀'))
const shownH = computed(() => hText(isTable.value ? (piece.value ?? Object.values(row.value.formulas)[0]).h : row.value.h))
const legend = computed(() => {
  const lines = comparing.value ? row.value.compare.lines : [piece.value]
  const items = [`h = ${shownH.value}`]
  for (const l of lines) items.push(`D (${l.name.toLowerCase()}) = ${formatNumber(l.D)}`)
  if (exact.value !== null) {
    items.push(`f′(${base.value}) exacta = ${formatNumber(exact.value)}`)
    for (const l of lines) items.push(`Error real (${l.name.toLowerCase()}) = ${formatNumber(Math.abs(l.D - exact.value))}`)
  }
  return items
})
const phrase = computed(() => (comparing.value ? row.value.compare.phrase : piece.value.phrase))
const title = computed(() => (comparing.value ? 'Comparar las fórmulas' : `${piece.value.name}: ${shape(piece.value)} por los puntos`))
const description = computed(() => {
  const where = `en ${base.value} = ${formatNumber(isTable.value ? row.value.x : props.chart.x0)}, h = ${shownH.value}`
  const tangent = exact.value === null ? '' : `, tangente con pendiente ${formatNumber(exact.value)}`
  const lines = comparing.value ? row.value.compare.lines : [piece.value]
  const approx = lines.map((l) => `${l.name.toLowerCase()} con pendiente ${formatNumber(l.D)}`).join(', ')
  const curve = isTable.value ? (props.chart.curve ? 'datos y curva f' : 'datos') : 'curva f'
  return `Gráfica: ${curve}${tangent} y ${comparing.value ? 'rectas aproximadas' : 'recta aproximada'}: ${approx} ${where}.`
})

const GLOSSARY = [
  { symbol: '\\text{Tangente}', text: 'La tangente es la derivada que buscamos: su pendiente es f′(x₀) exacta.' },
  {
    symbol: '\\text{Curva interpolante}',
    text: 'La fórmula pasa una recta o curva por los puntos marcados y toma su pendiente en x₀ (línea discontinua).',
  },
  {
    symbol: '\\text{Aproximación}',
    text: 'Mientras más se parezca esa curva a f cerca de x₀, más se acerca la recta aproximada a la tangente.',
  },
]

// --- Chart.js ---------------------------------------------------------------------
const canvasRef = ref(null)
let instance = null
const { theme } = useTheme()
const TOKENS = [
  '--color-ink',
  '--color-ink-muted',
  '--color-surface',
  '--color-line',
  '--color-chart-grid',
  '--color-chart-tangent',
  '--color-chart-approx',
  '--color-chart-curve',
  '--color-series-2',
  '--color-series-3',
  '--color-series-5',
]
// Colores y trazos de «Comparar», en el orden de las líneas (la de 3 puntos de referencia, la última).
const COMPARE_STYLES = [
  ['--color-chart-approx', []],
  ['--color-series-3', [8, 4]],
  ['--color-series-2', [2, 3]],
  ['--color-series-5', [10, 3, 2, 3]],
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

const toPoints = (curve) => curve.x.map((x, i) => ({ x, y: curve.y[i] ?? null }))
const linePoints = (line) => line.map(([x, y]) => ({ x, y }))
const line = (label, data, color, extra = {}) => ({
  label, data, borderColor: color, backgroundColor: color, borderWidth: 2, pointRadius: 0, tension: 0,
  spanGaps: false, fill: false, ...extra,
})

const windowRange = computed(() => {
  if (isTable.value) return props.chart.window
  return comparing.value ? row.value.compare.window : piece.value.window
})

function buildDatasets(palette) {
  const sets = []
  const curve = isTable.value ? props.chart.curve : row.value.curve
  if (curve) sets.push(line('f(x)', toPoints(curve), palette['--color-chart-curve'], { order: 3 }))
  if (isTable.value) {
    sets.push(line('Datos', props.chart.rows.map((r) => {
      const own = Object.values(r.formulas)[0].points.find((p) => p.base)
      return { x: own.x, y: own.y }
    }), palette['--color-ink-muted'], { showLine: allSecants.value, borderWidth: 1.5, pointRadius: 3, pointStyle: 'circle', order: 2 }))
  }
  const tangent = comparing.value ? row.value.compare.tangent : piece.value.tangent
  if (tangent) sets.push(line('Tangente (derivada exacta)', linePoints(tangent), palette['--color-chart-tangent'], { order: 1 }))
  if (comparing.value) {
    row.value.compare.lines.forEach((l, i) => {
      const [color, dash] = COMPARE_STYLES[i % COMPARE_STYLES.length]
      sets.push(line(`${l.name} (pendiente ${formatNumber(l.D)})`, linePoints(l.line), palette[color], { borderDash: dash, order: 0 }))
    })
    return sets
  }
  const p = piece.value
  const approx = palette['--color-chart-approx']
  // En diferencias la interpolante es la misma recta que la aproximada: se dibuja una sola.
  if (p.points.length > 2) {
    sets.push(line(`Curva interpolante (${shape(p)})`, toPoints(p.interpolant), approx, { borderDash: [6, 4], borderWidth: 1.5, order: 0 }))
  }
  sets.push(line(`Aproximación (pendiente ${formatNumber(p.D)})`, linePoints(p.approx), approx, { order: 0 }))
  sets.push({
    label: 'Puntos de la fórmula',
    data: p.points.map((pt) => ({ x: pt.x, y: pt.y })),
    labels: p.points.map((pt) => pt.label),
    showLine: false,
    pointStyle: p.points.map((pt) => (pt.base ? 'rectRot' : 'circle')),
    pointRadius: p.points.map((pt) => (pt.base ? 7 : 4.5)),
    backgroundColor: approx,
    borderColor: palette['--color-surface'],
    pointBorderWidth: 2,
    order: -1,
  })
  return sets
}

// Eje y ajustado a lo que se ve en la ventana, con un margen del 10 %.
function yRange(datasets, [a, b]) {
  const ys = datasets.flatMap((d) => d.data.filter((pt) => pt.x >= a && pt.x <= b && Number.isFinite(pt.y)).map((pt) => pt.y))
  if (!ys.length) return {}
  const low = Math.min(...ys)
  const high = Math.max(...ys)
  const pad = (high - low || Math.abs(high) || 1) * 0.1
  return { min: low - pad, max: high + pad }
}

// Nombre de cada punto (x₀ − h, x₀, …) sobre su marca.
const pointLabels = {
  id: 'pointLabels',
  afterDatasetsDraw(chart) {
    const { ctx } = chart
    chart.data.datasets.forEach((d, i) => {
      if (!d.labels) return
      const meta = chart.getDatasetMeta(i)
      ctx.save()
      ctx.font = '11px sans-serif'
      ctx.fillStyle = chart.options.color
      ctx.textAlign = 'center'
      meta.data.forEach((el, j) => ctx.fillText(d.labels[j], el.x, el.y - 12))
      ctx.restore()
    })
  },
}

function buildOptions(palette, datasets) {
  const text = palette['--color-ink-muted']
  const [a, b] = windowRange.value
  const axis = {
    type: 'linear',
    grid: { color: palette['--color-chart-grid'] },
    border: { color: palette['--color-line'] },
    // Sin marcas en los bordes de la ventana (0.446794, −0.25…): sólo las redondas.
    ticks: { color: text, includeBounds: false, callback: (value) => formatNumber(value) },
  }
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    color: text,
    interaction: { mode: 'nearest', intersect: false },
    scales: {
      x: { ...axis, min: a, max: b, title: { display: true, text: 'x', color: text } },
      y: { ...axis, ...yRange(datasets, [a, b]), title: { display: true, text: 'y', color: text } },
    },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 14, font: { size: 11 }, color: text } },
      tooltip: {
        backgroundColor: palette['--color-ink'],
        titleColor: palette['--color-surface'],
        bodyColor: palette['--color-surface'],
        callbacks: {
          title: (items) => `x = ${formatNumber(items[0].parsed.x)}`,
          label: (item) => `${item.dataset.label}: y = ${formatNumber(item.parsed.y)}`,
        },
      },
    },
  }
}

function render(palette) {
  const datasets = buildDatasets(palette)
  instance.data = { datasets }
  instance.options = buildOptions(palette, datasets)
  instance.update()
}

// El PDF siempre es claro (mismo procedimiento que TrapezoidChart).
function toImage() {
  if (!instance) return null
  const dark = theme.value === 'dark'
  if (dark) render(readPalette('light'))
  const source = instance.canvas
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

// Lo que el PDF escribe junto a la imagen: título, leyenda y lectura de la elección en pantalla.
const pdfCaption = () => ({ title: title.value, legend: legend.value, phrase: phrase.value })
defineExpose({ toImage, pdfCaption })

onMounted(() => {
  const palette = readPalette()
  const datasets = buildDatasets(palette)
  instance = new Chart(canvasRef.value, {
    type: 'line',
    data: { datasets },
    options: buildOptions(palette, datasets),
    plugins: [pointLabels],
  })
})

watch([rowIndex, formulaKey, allSecants, () => props.chart, theme], () => {
  if (instance) render(readPalette())
})

onBeforeUnmount(() => {
  if (instance) instance.destroy()
  instance = null
})
</script>

<template>
  <section class="chart-block">
    <h4 class="chart-title">Gráfica de la aproximación</h4>
    <p class="section-text">
      La derivada es la pendiente de la recta tangente. Cada fórmula pasa una recta o curva por algunos puntos de
      {{ isTable ? 'los datos' : 'f' }} y toma su pendiente en {{ base }}: esa es la recta aproximada.
    </p>
    <div class="controls">
      <label class="control">
        <span>Fórmula</span>
        <select v-model="formulaKey">
          <option v-for="o in formulaOptions" :key="o.key" :value="o.key">{{ o.label }}</option>
        </select>
      </label>
      <label class="control">
        <span>{{ isTable ? 'Punto' : 'Fila' }}</span>
        <select v-model.number="rowIndex">
          <option v-for="o in rowOptions" :key="o.index" :value="o.index">{{ o.label }}</option>
        </select>
      </label>
      <label v-if="isTable && isDifferences" class="control control-check">
        <input v-model="allSecants" type="checkbox" />
        <span>Todas las secantes</span>
      </label>
    </div>
    <p v-if="!isTable" class="section-text note">
      Con pasos más pequeños, la aproximación y la tangente se ven una encima de la otra: la diferencia sigue estando en
      la leyenda.
    </p>
    <p v-if="!isTable && isFivePoint" class="section-text note">
      En la fórmula de 5 puntos la aproximación es tan buena que las dos rectas coinciden a simple vista; compáralas en
      la leyenda o con la opción Comparar frente a la fórmula de 3 puntos.
    </p>
    <p v-if="comparing" class="section-text note">
      En «Comparar» se dibujan sólo las rectas aproximadas, sin las curvas interpolantes, para no recargar la gráfica.
    </p>
    <p v-if="allSecants" class="section-text note">
      Cada recta entre dos datos sirve como progresiva en su punto izquierdo y como regresiva en su punto derecho.
    </p>

    <h5 class="chart-subtitle">{{ title }}</h5>
    <div class="chart-canvas-wrapper">
      <canvas ref="canvasRef" role="img" :aria-label="description"></canvas>
    </div>

    <ul class="chart-legend" aria-label="Valores de la gráfica">
      <li v-for="item in legend" :key="item">{{ item }}</li>
    </ul>
    <p v-if="phrase" class="reading">{{ phrase }}</p>
    <GlossaryBlock title="¿Cómo leer la gráfica?" :items="GLOSSARY" />
  </section>
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

.chart-subtitle {
  margin: var(--space-3) 0 var(--space-2);
  font-size: var(--text-body);
  color: var(--color-ink);
}

.section-text {
  margin: var(--space-3) 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.note {
  font-style: italic;
}

.controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
  gap: var(--space-3);
  align-items: end;
}

.control {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.control-check {
  flex-direction: row;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-ink);
}

.chart-canvas-wrapper {
  position: relative;
  height: 340px;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1) var(--space-4);
  margin: var(--space-3) 0 0;
  padding: 0;
  list-style: none;
  font-size: var(--text-small);
  color: var(--color-ink);
}

.reading {
  margin: var(--space-2) 0;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}
</style>
