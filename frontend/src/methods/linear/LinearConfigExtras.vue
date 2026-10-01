<script setup>
// Opciones de un sistema lineal que van debajo de la cuadrícula de
// configuración: el reordenamiento automático de filas.
defineProps({
  store: { type: Object, required: true },
})
</script>

<template>
  <label class="checkbox-field">
    <input type="checkbox" v-model="store.state.autoReorder" />
    <span>
      Reordenar filas automáticamente si mejora la convergencia
      <small>
        Si la matriz no es diagonalmente dominante, se busca un orden de ecuaciones
        que sí lo sea. No cambia la solución del sistema.
      </small>
    </span>
  </label>
</template>

<style scoped>
.checkbox-field {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin: var(--space-1) 0 0;
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-line);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  color: var(--color-ink);
  cursor: pointer;
}

.checkbox-field input {
  margin: 3px 0 0;
  width: 16px;
  height: 16px;
  cursor: pointer;
  flex-shrink: 0;
}

.checkbox-field small {
  display: block;
  font-weight: var(--weight-regular);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  margin-top: 2px;
}
</style>
