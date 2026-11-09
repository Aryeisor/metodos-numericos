<script setup>
// Subintervalos N de la cuadratura gaussiana (1 = la versión simple de Chapra).
defineProps({
  store: { type: Object, required: true },
})
</script>

<template>
  <div class="field">
    <label for="gauss-subintervals">Subintervalos N (de 1 a 50)</label>
    <input
      id="gauss-subintervals"
      v-model.number="store.state.subintervals"
      type="number"
      min="1"
      max="50"
      step="1"
      aria-describedby="gauss-subintervals-hint"
    />
    <small id="gauss-subintervals-hint" class="field-hint">
      Con N = 1 se aplica Gauss a todo el intervalo; con N &gt; 1 se divide el intervalo en N partes y se aplica Gauss
      en cada una (versión compuesta), útil cuando la función cambia mucho en el intervalo.
    </small>
  </div>
</template>

<style scoped>
.field-hint {
  display: block;
  margin-top: var(--space-1);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
