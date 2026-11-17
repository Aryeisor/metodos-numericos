<script setup>
// Dirección que no corresponde a ninguna página: un método que ya no existe,
// un enlace viejo o un error al escribir. Mismo encabezado que Resolver y Teoría.
import { RouterLink } from 'vue-router'
import MethodHeader from '../components/MethodHeader.vue'
import { methodRegistry } from '../methods/registry'

const PAGE = {
  categoryLabel: 'Dirección no encontrada',
  name: 'Esta página no existe',
  summary: 'La dirección no corresponde a ninguna página del sistema; puede ser un enlace viejo o tener un error de escritura.',
}

// El menú de métodos escucha «/» en todo el documento; este botón lo abre igual.
function openMethodsMenu() {
  document.dispatchEvent(new KeyboardEvent('keydown', { key: '/' }))
}
</script>

<template>
  <!-- Si el catálogo no cargó, las rutas de los métodos no existen: el problema
       real es la conexión, no la dirección. -->
  <div v-if="methodRegistry.status === 'error'" class="alert alert-danger">
    No fue posible cargar los métodos desde el servidor. Verifica que el backend esté corriendo.
  </div>
  <section v-else class="not-found">
    <MethodHeader :method="PAGE" />
    <div class="not-found-actions">
      <button type="button" class="btn btn-primary" @click="openMethodsMenu">Ver los métodos</button>
      <RouterLink to="/" class="btn btn-secondary">Ir al inicio</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.not-found-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-5);
}

.not-found-actions .btn {
  text-decoration: none;
}
</style>
