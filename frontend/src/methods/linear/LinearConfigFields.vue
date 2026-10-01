<script setup>
// Campos de configuración propios de un sistema lineal que van dentro de la
// cuadrícula de "Configuración del sistema". Raíz única (.field) para que
// ocupe una celda de la cuadrícula igual que los campos genéricos.
const props = defineProps({
  store: { type: Object, required: true },
})
const emit = defineEmits(['structure-changed'])

function onNInput(event) {
  props.store.setN(Number(event.target.value))
  emit('structure-changed')
}
</script>

<template>
  <div class="field">
    <label>Número de variables (n ≥ 3)</label>
    <input type="number" min="3" max="12" :value="store.state.n" @change="onNInput" />
  </div>
</template>
