<script setup>
// Gráfica de la aproximación (diferencias, 3 y 5 puntos): la curva f, la
// tangente exacta en x₀, los puntos que usa la fórmula, la curva que pasa por
// ellos (recta, parábola o polinomio de grado 4) y la recta aproximada, que
// tiene pendiente D y es tangente a esa curva en x₀. Todo lo calcula el
// backend (`result.chart`, ver solvers/differentiation/chart.py); aquí sólo
// se elige qué mostrar. Misma lectura de la paleta, modo oscuro e imagen del
// PDF que TrapezoidChart. La «vista ilustrativa» dibuja la fila 1 con
// h = m·h₀ sólo para ver la forma: no cambia ningún resultado.
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
// 1 = paso real de la fila; 2, 5 o 10 = vista ilustrativa de la fila 1.
const multiple = ref(1)
function reset() {
  multiple.value = 1
  rowIndex.value = isTable.value ? props.chart.default_point - 1 : 0
  formulaKey.value = isTable.value ? realRow.value.default : Object.keys(realRow.value.formulas)[0]
  allSecants.value = false
}
const realRow = computed(() => props.chart.rows[rowIndex.value])
const illustrative = computed(() => (isTable.value ? [] : (props.chart.rows[0].illustrative ?? [])))
const view = computed(() => illustrative.value.find((v) => v.m === multiple.value) ?? null)
// Lo que se dibuja: la fila elegida o, en la vista ilustrativa, sus datos con h = m·h₀.
const row = computed(() => view.value ?? realRow.value)
watch(() => props.chart, reset)
// En la tabla cada punto tiene sus fórmulas: si la elegida no aplica, la recomendada.
watch(rowIndex, () => {
  if (formulaKey.value !== COMPARE && !realRow.value.formulas[formulaKey.value]) formulaKey.value = realRow.value.default
})
reset()

const comparing = computed(() => formulaKey.value === COMPARE)
const unavailable = (v) => (formulaKey.value === COMPARE ? !v.compare : !v.formulas[formulaKey.value])
const stepOptions = computed(() => [
  { m: 1, label: 'Real (h de la fila)', disabled: false, reason: '' },
  ...illustrative.value.map((v) => ({
    m: v.m,
    label: `Ilustrativo ×${v.m}`,
    disabled: unavailable(v),
    reason: unavailable(v) ? (v.reasons[formulaKey.value] ?? '') : '',
  })),
])
// Si la fórmula elegida no tiene datos con este múltiplo, vuelve al paso real.
watch(formulaKey, () => {
  if (view.value && unavailable(view.value)) multiple.value = 1
})
watch(multiple, (m) => {
  if (m !== 1) rowIndex.value = 0
})
const piece = computed(() => (comparing.value ? null : row.value.formulas[formulaKey.value]))
const canCompare = computed(() => !isTable.value && realRow.value.compare.lines.length > 1)
const formulaOptions = computed(() => [
  ...Object.values(realRow.value.formulas).map((p) => ({ key: p.key, label: p.name })),
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
const ofShape = (p) => (p.points.length === 3 ? 'de la parábola' : 'del polinomio de grado 4')

// --- Leyenda, lectura y descripción -------------------------------------------------
const exact = computed(() => {
  if (!isTable.value) return props.chart.exact
  const p = piece.value ?? Object.values(row.value.formulas)[0]
  return p.tangent ? (p.tangent[1][1] - p.tangent[0][1]) / (p.tangent[1][0] - p.tangent[0][0]) : null
})
const base = computed(() => (isTable.value ? `x${sub(row.value.i)}` : 'x₀'))
const shownH = computed(() => hText(isTable.value ? (piece.value ?? Object.values(row.value.formulas)[0]).h : row.value.h))
const realH = computed(() => hText(props.chart.rows[0].h))
const legend = computed(() => {
  const lines = comparing.value ? row.value.compare.lines : [piece.value]
  if (view.value) {
    // Vista ilustrativa: su pendiente y, debajo, el valor real de la fila 1.
    const real = comparing.value ? realRow.value.compare.lines : [realRow.value.formulas[formulaKey.value]]
    const named = (l) => (comparing.value ? ` (${l.name.toLowerCase()})` : '')
    const items = []
    lines.forEach((l, i) => {
      items.push(`D${named(l)} con h = ${shownH.value} (ilustrativo) = ${formatNumber(l.D)}`)
      items.push(`D${named(l)} real (fila 1, h = ${realH.value}) = ${formatNumber(real[i].D)}`)
    })
    if (exact.value !== null) items.push(`f′(${base.value}) exacta = ${formatNumber(exact.value)}`)
    return items
  }
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

const shading = computed(() => (!comparing.value && piece.value.chord ? ofShape(piece.value) : null))
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
// Color de cada fórmula en «Comparar» (la tangente sigue en verde).
const COMPARE_COLORS = {
  forward: '--chart-f-forward',
  backward: '--chart-f-backward',
  punto_medio: '--chart-f-mid',
  punto_medio_5: '--chart-f-mid',
  extremo_adelante: '--chart-f-endfwd',
  extremo_adelante_5: '--chart-f-endfwd',
  extremo_atras: '--chart-f-endbwd',
  extremo_atras_5: '--chart-f-endbwd',
  reference: '--chart-f-ref3',
}
const TOKENS = [
  '--color-ink',
  '--color-ink-muted',
  '--color-surface',
  '--color-line',
  '--color-chart-grid',
  '--chart-fn',
  '--chart-tangent',
  '--chart-approx',
  '--chart-interp',
  '--chart-interp-fill',
  ...new Set(Object.values(COMPARE_COLORS)),
]
// Orden de dibujo (Chart.js dibuja primero el `order` mayor): de atrás hacia adelante.
const ORDER = { shade: 6, fn: 5, tangent: 4, interp: 3, approx: 2, points: 1, base: 0 }

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
// pointStyle 'line': la leyenda dibuja el trazo real (con su borderDash).
const line = (label, data, color, extra = {}) => ({
  label, data, borderColor: color, backgroundColor: color, borderWidth: 3, pointRadius: 0, pointStyle: 'line',
  tension: 0, spanGaps: false, fill: false, ...extra,
})

const windowRange = computed(() => {
  if (isTable.value) return props.chart.window
  return comparing.value ? row.value.compare.window : piece.value.window
})

function buildDatasets(palette) {
  const sets = []
  const curve = isTable.value ? props.chart.curve : row.value.curve
  const p = piece.value
  if (p?.chord) {
    // Curvatura: área entre la interpolante y la cuerda (relleno hasta el dataset siguiente).
    const start = p.interpolant.x.indexOf(p.chord.x[0])
    const bend = p.chord.x.map((x, i) => ({ x, y: p.interpolant.y[start + i] }))
    sets.push(line(`Curvatura ${ofShape(p)} (diferencia con la cuerda)`, bend, palette['--chart-interp-fill'], {
      borderWidth: 0, pointStyle: 'rect', fill: '+1', order: ORDER.shade,
    }))
    sets.push(line('Cuerda', toPoints(p.chord), 'transparent', { borderWidth: 0, order: ORDER.shade, legend: false }))
  }
  if (curve) sets.push(line('f(x)', toPoints(curve), palette['--chart-fn'], { borderWidth: 2, order: ORDER.fn }))
  if (isTable.value) {
    sets.push(line('Datos', props.chart.rows.map((r) => {
      const own = Object.values(r.formulas)[0].points.find((pt) => pt.base)
      return { x: own.x, y: own.y }
    }), palette['--color-ink-muted'], { showLine: allSecants.value, borderWidth: 1.5, pointRadius: 3, pointStyle: 'circle', order: ORDER.fn }))
  }
  const tangent = comparing.value ? row.value.compare.tangent : p.tangent
  if (tangent) sets.push(line('Tangente (derivada exacta)', linePoints(tangent), palette['--chart-tangent'], { order: ORDER.tangent }))
  if (comparing.value) {
    row.value.compare.lines.forEach((l) => {
      sets.push(line(`${l.name} (pendiente ${formatNumber(l.D)})`, linePoints(l.line), palette[COMPARE_COLORS[l.key]], {
        order: ORDER.approx, endLabel: l.name,
      }))
    })
    return sets
  }
  const interp = palette['--chart-interp']
  // En diferencias la interpolante es la misma recta que la aproximada: se dibuja una sola.
  if (p.points.length > 2) {
    sets.push(line(`Curva interpolante (${shape(p)})`, toPoints(p.interpolant), interp, { borderDash: [8, 5], order: ORDER.interp }))
  }
  const approx = palette['--chart-approx']
  sets.push(line(`Aproximación (pendiente ${formatNumber(p.D)})`, linePoints(p.approx), approx, { order: ORDER.approx }))
  const marks = (label, points, color, extra) => ({
    label,
    data: points.map((pt) => ({ x: pt.x, y: pt.y })),
    labels: points.map((pt) => pt.label),
    showLine: false,
    backgroundColor: color,
    borderColor: palette['--color-surface'],
    pointBorderWidth: 2,
    ...extra,
  })
  sets.push(marks('Puntos de la fórmula', p.points.filter((pt) => !pt.base), interp, { pointStyle: 'circle', pointRadius: 6, order: ORDER.points }))
  sets.push(marks(base.value, p.points.filter((pt) => pt.base), approx, { pointStyle: 'rectRot', pointRadius: 9, order: ORDER.base }))
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

// Nombre de cada punto (x₀ − h, x₀, …) sobre su marca y, en «Comparar», el
// nombre de cada recta al final de la línea, en su color y sin encimarse.
const pointLabels = {
  id: 'pointLabels',
  afterDatasetsDraw(chart, _args, options) {
    const { ctx, chartArea } = chart
    ctx.save()
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillStyle = chart.options.color
    chart.data.datasets.forEach((d, i) => {
      if (!d.labels) return
      chart.getDatasetMeta(i).data.forEach((el, j) => ctx.fillText(d.labels[j], el.x, el.y - 14))
    })
    const ends = chart.data.datasets
      .map((d, i) => ({ d, el: d.endLabel ? chart.getDatasetMeta(i).data.at(-1) : null }))
      .filter(({ el }) => el)
      .map(({ d, el }) => ({ text: d.endLabel, color: d.borderColor, y: el.y - 8 }))
      .sort((a, b) => a.y - b.y)
    ends.forEach((e, k) => {
      if (k > 0) e.y = Math.max(e.y, ends[k - 1].y + 13)
    })
    ctx.textAlign = 'right'
    ctx.font = 'bold 11px sans-serif'
    ctx.strokeStyle = options.halo
    ctx.lineWidth = 3
    ctx.lineJoin = 'round'
    for (const e of ends) {
      const y = Math.min(Math.max(e.y, chartArea.top + 10), chartArea.bottom - 4)
      ctx.strokeText(e.text, chartArea.right - 4, y)
      ctx.fillStyle = e.color
      ctx.fillText(e.text, chartArea.right - 4, y)
    }
    ctx.restore()
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
      pointLabels: { halo: palette['--color-surface'] },
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          boxHeight: 16,
          font: { size: 11 },
          color: text,
          // Con usePointStyle Chart.js toma el estilo del punto: se le pasa el trazo real de la línea.
          generateLabels: (chart) =>
            Chart.defaults.plugins.legend.labels.generateLabels(chart).map((item) => ({
              ...item,
              lineDash: chart.data.datasets[item.datasetIndex].borderDash ?? [],
            })),
          filter: (item, data) => data.datasets[item.datasetIndex].legend !== false,
          sort: (a, b) => a.datasetIndex - b.datasetIndex,
        },
      },
      tooltip: {
        backgroundColor: palette['--color-ink'],
        titleColor: palette['--color-surface'],
        bodyColor: palette['--color-surface'],
        // Sin la cuerda ni el sombreado (repiten la interpolante).
        filter: (item) => item.dataset.order !== ORDER.shade,
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

watch([rowIndex, formulaKey, allSecants, multiple, () => props.chart, theme], () => {
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
        <select v-model.number="rowIndex" :disabled="view !== null">
          <option v-for="o in rowOptions" :key="o.index" :value="o.index">{{ o.label }}</option>
        </select>
        <small v-if="view">en la vista ilustrativa se usa h₀ × {{ view.m }}</small>
      </label>
      <label v-if="!isTable && illustrative.length" class="control">
        <span>Paso de la gráfica</span>
        <select v-model.number="multiple">
          <option v-for="o in stepOptions" :key="o.m" :value="o.m" :disabled="o.disabled" :title="o.reason || null">
            {{ o.label }}{{ o.disabled ? ' (no disponible)' : '' }}
          </option>
        </select>
      </label>
      <label v-if="isTable && isDifferences" class="control control-check">
        <input v-model="allSecants" type="checkbox" />
        <span>Todas las secantes</span>
      </label>
    </div>
    <p v-if="view" class="callout" role="note">
      Vista ilustrativa: el paso es h = {{ shownH }} ({{ view.m }} veces el paso real) solo para que se vea la forma de
      la curva. Los resultados del ejercicio usan h = {{ realH }}.
    </p>
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
    <p v-if="shading" class="section-text">
      La zona sombreada muestra cuánto se dobla {{ shading === 'de la parábola' ? 'la parábola' : 'el polinomio' }}: esa
      curvatura es lo que {{ shading === 'de la parábola' ? 'la' : 'lo' }} hace mejor que una recta.
    </p>
    <p v-else-if="isDifferences && !comparing" class="section-text">
      Con 2 puntos solo se puede trazar una recta (la secante); por eso su error es mayor.
    </p>
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

.control select:disabled {
  opacity: 0.6;
}

.callout {
  margin: var(--space-3) 0;
  padding: var(--space-2) var(--space-3);
  border-left: 3px solid var(--color-info-line);
  border-radius: var(--radius-sm, 4px);
  background: var(--color-accent-soft);
  font-size: var(--text-small);
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
