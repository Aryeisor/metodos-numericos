<script setup>
// Selector «Fórmula», dentro de la cuadrícula de configuración.
import { FORMULA_OPTIONS } from './store'

defineProps({
  store: { type: Object, required: true },
})
</script>

<template>
  <div class="field">
    <label for="difference-formula">Fórmula</label>
    <select id="difference-formula" v-model="store.state.formula">
      <option v-for="option in FORMULA_OPTIONS" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </div>
</template>
