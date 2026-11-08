<script setup>
// Segmentos iniciales n₀, dentro de la cuadrícula de configuración (sólo en
// modo «Función»: la tabla de datos ya fija sus segmentos).
import { MODES } from './store'

defineProps({
  store: { type: Object, required: true },
})
</script>

<template>
  <div v-if="store.state.mode === MODES.FUNCTION" class="field">
    <label for="integration-n0">Segmentos iniciales n₀ (de 1 a 1000)</label>
    <input id="integration-n0" v-model.number="store.state.n0" type="number" min="1" max="1000" step="1" />
  </div>
</template>
