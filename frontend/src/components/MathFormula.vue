<script setup>
import { computed } from 'vue'
import katex from 'katex'

const props = defineProps({
  expression: { type: String, required: true },
  displayMode: { type: Boolean, default: false },
})

// Único punto de la app donde se invoca KaTeX. Con `trust: false` (por defecto)
// KaTeX no emite HTML arbitrario — sólo su propio marcado —, así que la salida
// es segura para v-html; además la entrada la genera la propia app, no el usuario.
const html = computed(() => {
  try {
    return katex.renderToString(props.expression, {
      displayMode: props.displayMode,
      throwOnError: false,
      trust: false,
      strict: 'ignore',
    })
  } catch {
    return `<span class="math-fallback">${props.expression}</span>`
  }
})
</script>

<template>
  <span class="math" :class="{ 'math-display': displayMode }" v-html="html"></span>
</template>

<style scoped>
.math-display {
  display: block;
}

.math-fallback {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.85rem;
}
</style>
