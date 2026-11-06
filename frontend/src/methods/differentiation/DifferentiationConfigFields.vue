<script setup>
// Selector «Fórmula», dentro de la cuadrícula de configuración (las opciones
// son las del método: store.formulaOptions).

defineProps({
  store: { type: Object, required: true },
})
</script>

<template>
  <div class="field">
    <label for="difference-formula">Fórmula</label>
    <select id="difference-formula" v-model="store.state.formula">
      <option v-for="option in store.formulaOptions" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </div>
</template>
