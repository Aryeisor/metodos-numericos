<script>
import BairstowSection from './BairstowSection.vue'
import PolynomialFundamentalsSection from './PolynomialFundamentalsSection.vue'
import PolynomialReferencesSection from './PolynomialReferencesSection.vue'

/** Métodos de la categoría que tienen teoría escrita, y su sección propia. */
export const THEORY_SECTIONS = {
  bairstow: BairstowSection,
}
</script>

<script setup>
// Página de teoría de un método de la categoría "polinomios".
//
// Misma estructura que las de las otras categorías: el fundamento común y las
// referencias se muestran en todas las páginas de la categoría, y en medio va
// la sección propia del método (que incluye su tabla comparativa).
import { computed } from 'vue'
import TheoryLayout from '../../../components/theory/TheoryLayout.vue'

const props = defineProps({
  method: { type: String, required: true },
})

const section = computed(() => THEORY_SECTIONS[props.method])
</script>

<template>
  <TheoryLayout>
    <PolynomialFundamentalsSection />
    <component :is="section" />
    <PolynomialReferencesSection />
  </TheoryLayout>
</template>
