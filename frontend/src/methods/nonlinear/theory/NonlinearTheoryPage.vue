<script>
import FixedPointSection from './FixedPointSection.vue'
import NonlinearFundamentalsSection from './NonlinearFundamentalsSection.vue'
import NonlinearReferencesSection from './NonlinearReferencesSection.vue'

/** Métodos de la categoría que tienen teoría escrita, y su sección propia. */
export const THEORY_SECTIONS = {
  'punto-fijo': FixedPointSection,
}
</script>

<script setup>
// Página de teoría de un método de la categoría "ecuaciones no lineales".
//
// Misma estructura que la de sistemas lineales: el fundamento común y las
// referencias se muestran en todas las páginas de la categoría (un único
// componente cada uno), y en medio va la sección propia del método. Cuando
// se agregue Newton, basta con añadir su sección a THEORY_SECTIONS: hereda el
// fundamento y las referencias sin reescribirlos.
import { computed } from 'vue'
import TheoryLayout from '../../../components/theory/TheoryLayout.vue'

const props = defineProps({
  method: { type: String, required: true },
})

const section = computed(() => THEORY_SECTIONS[props.method])
</script>

<template>
  <TheoryLayout>
    <NonlinearFundamentalsSection />
    <component :is="section" />
    <NonlinearReferencesSection />
  </TheoryLayout>
</template>
