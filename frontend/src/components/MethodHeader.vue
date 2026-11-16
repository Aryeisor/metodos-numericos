<script setup>
// Encabezado común de Resolver y Teoría: categoría, nombre del método y su
// resumen de una línea. Va sobre el fondo de la página, sin tarjeta. Es el
// único <h1> (y el único uso de --text-display) de esas dos vistas.
defineProps({
  // Entrada del registro: { name, categoryLabel, summary }.
  method: { type: Object, required: true },
})
</script>

<template>
  <header class="method-header">
    <p class="method-category">{{ method.categoryLabel }}</p>
    <h1 class="method-name">{{ method.name }}</h1>
    <p v-if="method.summary" class="method-summary">{{ method.summary }}</p>
  </header>
</template>

<style scoped>
/* Compacto: el espacio entre líneas lo pone el interlineado, no los márgenes. */
.method-header {
  margin-top: calc(-1 * var(--space-2));
  margin-bottom: var(--space-3);
}

.method-category {
  margin: 0;
  font-size: var(--text-small);
  font-weight: var(--weight-medium);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--color-ink-muted);
}

/* Tamaño y peso vienen de la regla global de h1; el interlineado se cierra
   porque es una sola línea. */
.method-name {
  margin: 0;
  line-height: 1.2;
  color: var(--color-ink);
}

.method-summary {
  margin: 0;
  max-width: 65ch;
  font-size: var(--text-body);
  line-height: var(--leading-snug);
  color: var(--color-ink-muted);
}
</style>
