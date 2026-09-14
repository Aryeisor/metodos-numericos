<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  iterations: { type: Array, required: true },
  tolerance: { type: Number, default: null },
  converged: { type: Boolean, default: false },
})

const canvasRef = ref(null)
let chart = null

// La escala logarítmica no admite ceros: esos puntos se dejan como huecos y la
// línea se continúa con spanGaps.
function buildData() {
  const labels = props.iterations.map((it) => it.iteration)
  const errors = props.iterations.map((it) =>
    it.error !== null && it.error > 0 && Number.isFinite(it.error) ? it.error : null
  )

  const datasets = [
    {
      label: 'Error por iteración',
      data: errors,
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
      label: `Tolerancia (${props.tolerance})`,
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
        title: { display: true, text: 'Error (escala log)' },
        grid: { color: 'rgba(0,0,0,0.05)' },
      },
    },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 14, font: { size: 11 } } },
      tooltip: {
        callbacks: {
          title: (items) => `Iteración ${items[0].label}`,
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
