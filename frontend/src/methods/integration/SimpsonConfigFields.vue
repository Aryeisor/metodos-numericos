<script setup>
// Regla de Simpson y segmentos iniciales de cada regla visible (sólo en modo
// «Función»: la tabla de datos ya fija sus segmentos).
import { computed } from 'vue'
import { MODES } from './store'

const props = defineProps({
  store: { type: Object, required: true },
})

const isFunction = computed(() => props.store.state.mode === MODES.FUNCTION)
const shows = (rule) => props.store.state.rule === 'both' || props.store.state.rule === rule
</script>

<template>
  <div class="field">
    <label for="simpson-rule">Regla</label>
    <select id="simpson-rule" v-model="store.state.rule">
      <option v-for="option in store.ruleOptions" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </div>
  <div v-if="isFunction && shows('simpson13')" class="field">
    <label for="simpson-n0-13">n₀ de Simpson 1/3 (par, de 2 a 1000)</label>
    <input id="simpson-n0-13" v-model.number="store.state.n0_13" type="number" min="2" max="1000" step="2" />
  </div>
  <div v-if="isFunction && shows('simpson38')" class="field">
    <label for="simpson-n0-38">n₀ de Simpson 3/8 (múltiplo de 3, de 3 a 999)</label>
    <input id="simpson-n0-38" v-model.number="store.state.n0_38" type="number" min="3" max="999" step="3" />
  </div>
</template>
