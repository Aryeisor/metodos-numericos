<script setup>
// Vista previa en vivo de una ecuación (ver composables/useExpressionPreviews):
// su LaTeX si es válida o el mensaje de error. Aparece cuando llega la
// primera respuesta; mientras se consulta un cambio se sigue viendo la
// anterior, atenuada. Vacía no ocupa espacio.
import { computed } from 'vue'
import MathFormula from './MathFormula.vue'

const props = defineProps({
  // { status: 'empty' | 'pending' | 'valid' | 'invalid', latex, error, stale }
  preview: { type: Object, required: true },
  // Texto de la ecuación: sin '=' se interpreta como "expresión = 0", y así
  // se muestra para que se vea exactamente lo que se va a resolver.
  text: { type: String, required: true },
})

const latex = computed(() =>
  props.text.includes('=') ? props.preview.latex : `${props.preview.latex} = 0`
)
</script>

<template>
  <div
    class="equation-preview"
    :class="{ 'is-stale': preview.stale, 'is-error': preview.status === 'invalid' }"
    aria-live="polite"
  >
    <MathFormula v-if="preview.status === 'valid'" :expression="latex" />
    <span v-else-if="preview.status === 'invalid'">{{ preview.error }}</span>
  </div>
</template>

<style scoped>
.equation-preview {
  margin-top: calc(-1 * var(--space-1));
  padding: var(--space-1) var(--space-2);
  overflow-x: auto;
  font-size: var(--text-small);
  color: var(--color-ink);
  background: var(--color-sunken);
  border-radius: var(--radius-control);
  transition: opacity var(--transition-fast);
}

.equation-preview:empty {
  display: none;
}

.equation-preview.is-error {
  color: var(--color-danger);
  background: var(--color-danger-bg);
}

/* Se está consultando un cambio: se ve la vista previa anterior, atenuada. */
.equation-preview.is-stale {
  opacity: 0.5;
}

.equation-preview :deep(.katex) {
  font-size: 1.1em;
}
</style>
