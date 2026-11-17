<script setup>
// Tarjeta de respuesta: lo primero del resultado. Sólo el valor (o los
// valores), una línea de estado y los botones de PDF y Limpiar. Cuando sale de
// la pantalla por arriba, en ventanas de 1024 px o más, la reemplaza una
// franja fija bajo la barra superior con lo mismo resumido.
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { scrollBehavior } from '../utils/motion'

const props = defineProps({
  methodName: { type: String, required: true },
  // De methods/answer.js: { values: [{ label, value }], noun, ok, status }.
  answer: { type: Object, required: true },
})
defineEmits(['export-pdf', 'clear'])

const HEADER_HEIGHT = 61 // --header-height: rootMargin no acepta variables CSS
const MANY_VALUES = 4 // con más, los valores bajan a --text-section para caber

const cardRef = ref(null)
const headingRef = ref(null)

// La franja resume la respuesta a un solo valor, o a cuántos hay.
const barAnswer = computed(() => {
  const { values, noun } = props.answer
  return values.length === 1 ? `${values[0].label} = ${values[0].value}` : `${values.length} ${noun}`
})

// --- Franja fija ------------------------------------------------------------
const wideMedia = window.matchMedia('(min-width: 1024px)')
const wide = ref(wideMedia.matches)
const onWideChange = (event) => (wide.value = event.matches)
// Fuera de la pantalla *por arriba*: si la tarjeta queda por debajo (el
// usuario volvió al formulario), el resultado no está a la vista.
const cardGone = ref(false)
const barVisible = computed(() => wide.value && cardGone.value)

let observer = null
onMounted(() => {
  wideMedia.addEventListener('change', onWideChange)
  observer = new IntersectionObserver(
    ([entry]) => (cardGone.value = !entry.isIntersecting && entry.boundingClientRect.top < 0),
    { rootMargin: `-${HEADER_HEIGHT}px 0px 0px 0px` }
  )
  observer.observe(cardRef.value)
})

// Con la franja a la vista, las anclas y el foco dejan libre también su alto
// (scroll-padding-top en style.css).
watch(barVisible, (visible) => document.documentElement.classList.toggle('has-result-bar', visible))

onBeforeUnmount(() => {
  wideMedia.removeEventListener('change', onWideChange)
  observer?.disconnect()
  document.documentElement.classList.remove('has-result-bar')
})

function goTop() {
  window.scrollTo({ top: 0, behavior: scrollBehavior() })
  // La franja desaparece al subir: el foco sigue en el contenido, no en <body>.
  document.getElementById('contenido')?.focus({ preventScroll: true })
}

/** Lleva la página hasta la tarjeta y deja el foco en su encabezado. */
function reveal() {
  cardRef.value?.scrollIntoView({ behavior: scrollBehavior(), block: 'start' })
  headingRef.value?.focus({ preventScroll: true })
}
defineExpose({ reveal })
</script>

<template>
  <section ref="cardRef" class="card answer-card" aria-labelledby="answer-heading">
    <h2 id="answer-heading" ref="headingRef" class="answer-heading" tabindex="-1">Resultado ({{ methodName }})</h2>

    <dl class="answer-values" :class="{ 'is-compact': answer.values.length > MANY_VALUES }">
      <div v-for="(item, i) in answer.values" :key="i" class="answer-item">
        <dt class="answer-label">{{ item.label }}</dt>
        <dd class="answer-value">{{ item.value }}</dd>
      </div>
    </dl>

    <p v-if="answer.ok" class="answer-status">
      <span class="mark mark-ok" aria-hidden="true">✔</span> {{ answer.status }}
    </p>
    <p v-else class="answer-status alert alert-warning">
      <strong>⚠ {{ answer.status }}</strong>
      {{ answer.values.length === 1 ? 'El valor mostrado es el último calculado' : 'Los valores mostrados son los últimos calculados' }},
      no una solución.
    </p>

    <div class="answer-actions">
      <button type="button" class="btn btn-outline" @click="$emit('export-pdf')">Descargar PDF</button>
      <button type="button" class="btn btn-outline" aria-label="Limpiar formulario y resultado" @click="$emit('clear')">
        Limpiar
      </button>
    </div>
  </section>

  <div v-if="barVisible" class="result-bar" role="region" aria-label="Resultado">
    <div class="result-bar-inner">
      <span class="bar-method">{{ methodName }}</span>
      <span class="bar-answer">
        <template v-if="!answer.ok">No alcanzó la tolerancia · </template>{{ barAnswer }}
      </span>
      <button type="button" class="btn btn-outline" @click="$emit('export-pdf')">Descargar PDF</button>
      <button type="button" class="btn btn-outline" aria-label="Limpiar formulario y resultado" @click="$emit('clear')">
        Limpiar
      </button>
      <a href="#contenido" class="bar-top" @click.prevent="goTop">Ir arriba</a>
    </div>
  </div>
</template>

<style scoped>
/* La tarjeta principal del resultado: superficie y borde completos (.card). */
.answer-card {
  margin-bottom: var(--space-5);
}

.answer-heading {
  margin: 0 0 var(--space-4);
  border-radius: var(--radius-control);
}

.answer-values {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4) var(--space-6);
  margin: 0 0 var(--space-4);
}

.answer-item {
  min-width: 0;
}

.answer-label {
  font-size: var(--text-small);
  line-height: var(--leading-tight);
  color: var(--color-ink-muted);
}

/* Tamaño, peso e interlineado: la regla global de h1 (--text-display), que es
   la única que usa ese tamaño. */
.answer-value {
  margin: 0;
  color: var(--color-ink);
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}

.answer-values.is-compact .answer-value {
  font-size: var(--text-section);
}

.answer-status {
  margin: 0 0 var(--space-4);
  font-size: var(--text-body);
}

.answer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

/* Franja fija bajo la barra superior. Por debajo de los menús (z-index 20+). */
.result-bar {
  position: fixed;
  top: var(--header-height);
  left: 0;
  right: 0;
  z-index: 10;
  height: var(--result-bar-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-line);
}

.result-bar-inner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  max-width: var(--container-width);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
  font-size: var(--text-small);
}

.bar-method {
  color: var(--color-ink-muted);
  white-space: nowrap;
}

.bar-answer {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: var(--weight-semibold);
  font-variant-numeric: tabular-nums;
  color: var(--color-ink);
}

.bar-top {
  margin-left: var(--space-2);
  font-weight: var(--weight-medium);
  white-space: nowrap;
}
</style>
