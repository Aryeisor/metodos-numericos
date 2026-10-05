<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  iterations: { type: Array, required: true },
  tolerance: { type: Number, default: null },
  converged: { type: Boolean, default: false },
  // Opcionales (Bairstow). Sin ellos el gráfico es el de siempre: una serie
  // con el `error` de cada iteración.
  //   series         [{ label, values, color }]: varias series en lugar del error
  //   yLabel         título del eje del error
  //   toleranceLabel texto de la línea de tolerancia en la leyenda
  series: { type: Array, default: null },
  yLabel: { type: String, default: 'Error (escala log)' },
  toleranceLabel: { type: String, default: null },
})

const canvasRef = ref(null)
let chart = null

// --- Formato numérico del gráfico ------------------------------------------
// Chart.js formatea por defecto con 3 decimales según el idioma del navegador:
// en el tooltip 0.000001 se veía como "0". Aquí todo número del gráfico (eje,
// tooltip, leyenda) usa el mismo formato: notación científica fuera de
// [0.001, 10000) y decimal normal dentro. Se escribe 1×10⁻⁶ con superíndices
// Unicode (el canvas no puede usar KaTeX), como la notación del resto de la
// app. El punto decimal es el mismo de las tablas.
const SCIENTIFIC_BELOW = 1e-3
const SCIENTIFIC_FROM = 1e4
const SUPERSCRIPTS = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }

function scientific(value, significant) {
  const [mantissa, exponent] = value.toExponential(significant - 1).split('e')
  // "1.000" -> "1"; "4.700" -> "4.7"
  const digits = mantissa.includes('.') ? mantissa.replace(/\.?0+$/, '') : mantissa
  const power = String(Number(exponent)).replace(/./g, (c) => SUPERSCRIPTS[c])
  return `${digits}×10${power}`
}

function formatChartNumber(value, significant = 4) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  if (!Number.isFinite(value)) return '∞'
  if (value === 0) return '0'
  const magnitude = Math.abs(value)
  if (magnitude < SCIENTIFIC_BELOW || magnitude >= SCIENTIFIC_FROM) {
    return scientific(value, significant)
  }
  return String(Number(value.toPrecision(6)))
}

// Eje logarítmico: sólo se rotulan las potencias de 10 (como antes), y como
// cada una es un orden de magnitud se escriben todas como 1×10ⁿ.
function logAxisLabel(value) {
  const exponent = Math.log10(value)
  if (Math.abs(exponent - Math.round(exponent)) > 1e-9) return ''
  return scientific(value, 1)
}

// La escala logarítmica no admite ceros: esos puntos se dejan como huecos y la
// línea se continúa con spanGaps.
function buildData() {
  const labels = props.iterations.map((it) => it.iteration)
  const positive = (value) =>
    value !== null && value !== undefined && value > 0 && Number.isFinite(value) ? value : null

  const datasets = props.series
    ? props.series.map((serie) => ({
        label: serie.label,
        data: serie.values.map(positive),
        borderColor: serie.color,
        backgroundColor: serie.color,
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 5,
        tension: 0.15,
        spanGaps: true,
        fill: false,
      }))
    : [
        {
          label: 'Error por iteración',
          data: props.iterations.map((it) => positive(it.error)),
          borderColor: props.converged ? '#2563eb' : '#b91c1c',
          backgroundColor: props.converged ? 'rgba(37, 99, 235, 0.12)' : 'rgba(185, 28, 28, 0.12)',
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.15,
          spanGaps: true,
          fill: true,
        },
      ]

  if (props.tolerance && props.tolerance > 0) {
    datasets.push({
      label: props.toleranceLabel ?? `Tolerancia (${formatChartNumber(props.tolerance)})`,
      data: labels.map(() => props.tolerance),
      borderColor: '#15803d',
      borderWidth: 2,
      borderDash: [6, 4],
      pointRadius: 0,
      fill: false,
    })
  }

  return { labels, datasets }
}

function buildOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { mode: 'index', intersect: false },
    scales: {
      x: {
        title: { display: true, text: 'Iteración' },
        grid: { color: 'rgba(0,0,0,0.05)' },
      },
      y: {
        type: 'logarithmic',
        title: { display: true, text: props.yLabel },
        grid: { color: 'rgba(0,0,0,0.05)' },
        ticks: { callback: logAxisLabel },
      },
    },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 14, font: { size: 11 } } },
      tooltip: {
        callbacks: {
          title: (items) => `Iteración ${items[0].label}`,
          label: (item) => `${item.dataset.label}: ${formatChartNumber(item.parsed.y)}`,
        },
      },
    },
  }
}

// Fondo blanco al exportar: el canvas es transparente por defecto y en el PDF
// se vería sobre el color de la página.
function toImage() {
  if (!chart) return null
  const source = chart.canvas
  const target = document.createElement('canvas')
  target.width = source.width
  target.height = source.height
  const ctx = target.getContext('2d')
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, target.width, target.height)
  ctx.drawImage(source, 0, 0)
  return {
    dataUrl: target.toDataURL('image/png'),
    width: target.width,
    height: target.height,
  }
}

defineExpose({ toImage })

onMounted(() => {
  chart = new Chart(canvasRef.value, {
    type: 'line',
    data: buildData(),
    options: buildOptions(),
  })
})

watch(
  () => props.iterations,
  () => {
    if (!chart) return
    chart.data = buildData()
    chart.update()
  }
)

onBeforeUnmount(() => {
  if (chart) chart.destroy()
  chart = null
})
</script>

<template>
  <div class="chart-block">
    <h4 class="chart-title">Convergencia del error</h4>
    <div class="chart-canvas-wrapper">
      <canvas ref="canvasRef"></canvas>
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
  height: 300px;
}
</style>
