<script setup>
// Teoría de un método: monta la página de teoría que aporta su categoría.
import { computed } from 'vue'
import { getMethod, hasTheory } from '../methods/registry'

const props = defineProps({
  // Slug del método; lo fija la ruta /teoria/<slug>.
  method: { type: String, default: null },
})

const activeMethod = computed(() => {
  const method = getMethod(props.method)
  return method && hasTheory(method) ? method : null
})
</script>

<template>
  <component :is="activeMethod.ui.theoryPage" v-if="activeMethod" :method="activeMethod.slug" />
  <div v-else class="alert alert-danger">
    No fue posible cargar los métodos desde el servidor. Verifica que el backend esté corriendo.
  </div>
</template>
