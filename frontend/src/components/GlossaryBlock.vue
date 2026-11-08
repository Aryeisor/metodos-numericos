<script setup>
// Bloque plegable que explica, en una línea cada uno, los símbolos de una
// fórmula o las columnas de una tabla. Visible por defecto.
// items: [{ symbol: LaTeX, text }] y, opcional, `summary` (una frase final).
import { ref } from 'vue'
import MathFormula from './MathFormula.vue'

defineProps({
  title: { type: String, default: '¿Qué significa cada símbolo?' },
  items: { type: Array, required: true },
  summary: { type: String, default: '' },
})

const open = ref(true)
const id = `glossary-${Math.random().toString(36).slice(2, 9)}`
</script>

<template>
  <div class="glossary">
    <button type="button" class="glossary-toggle" :aria-expanded="open" :aria-controls="id" @click="open = !open">
      <span aria-hidden="true">{{ open ? '▾' : '▸' }}</span> {{ title }}
    </button>
    <div v-show="open" :id="id">
      <dl class="glossary-list">
        <div v-for="item in items" :key="item.symbol" class="glossary-row">
          <dt><MathFormula :expression="item.symbol" /></dt>
          <dd>{{ item.text }}</dd>
        </div>
      </dl>
      <p v-if="summary" class="glossary-summary">{{ summary }}</p>
    </div>
  </div>
</template>

<style scoped>
.glossary {
  margin: var(--space-2) 0 var(--space-4);
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  background: var(--color-surface);
  font-size: var(--text-small);
}

.glossary-toggle {
  padding: var(--space-1) 0;
  border: none;
  background: transparent;
  color: var(--color-accent);
  font: inherit;
  font-weight: var(--weight-semibold);
  cursor: pointer;
}

.glossary-toggle:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
  border-radius: 2px;
}

.glossary-list {
  margin: var(--space-2) 0 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.glossary-row {
  display: grid;
  grid-template-columns: minmax(64px, max-content) 1fr;
  gap: var(--space-3);
  align-items: baseline;
}

.glossary-row dt {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
  overflow-x: auto;
}

.glossary-row dd {
  margin: 0;
  color: var(--color-ink-muted);
}

.glossary-summary {
  margin: var(--space-3) 0 var(--space-1);
  color: var(--color-ink);
  font-style: italic;
}

@media (max-width: 480px) {
  .glossary-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
