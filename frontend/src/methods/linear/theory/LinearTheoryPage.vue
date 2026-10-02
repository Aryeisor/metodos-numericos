<script>
import ComparisonSection from './ComparisonSection.vue'
import FundamentalsSection from './FundamentalsSection.vue'
import GaussSeidelSection from './GaussSeidelSection.vue'
import JacobiSection from './JacobiSection.vue'
import ReferencesSection from './ReferencesSection.vue'

/** Métodos de la categoría que tienen teoría escrita, y su sección propia. */
export const THEORY_SECTIONS = {
  jacobi: JacobiSection,
  'gauss-seidel': GaussSeidelSection,
}
</script>

<script setup>
// Página de teoría de un método de la categoría "sistemas lineales".
//
// Cada página se lee completa por sí sola: el fundamento común, la
// comparación y las referencias se muestran en todas (un único componente
// cada uno), y en medio va la sección propia del método. Los estilos
// compartidos con las demás categorías están en TheoryLayout.
import { computed } from 'vue'
import TheoryLayout from '../../../components/theory/TheoryLayout.vue'

const props = defineProps({
  method: { type: String, required: true },
})

const section = computed(() => THEORY_SECTIONS[props.method])
</script>

<template>
  <TheoryLayout>
    <FundamentalsSection />
    <component :is="section" />
    <ComparisonSection />
    <ReferencesSection />
  </TheoryLayout>
</template>
