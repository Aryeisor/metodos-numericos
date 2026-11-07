<script>
import DifferentiationFundamentalsSection from './DifferentiationFundamentalsSection.vue'
import DifferentiationReferencesSection from './DifferentiationReferencesSection.vue'
import FiniteDifferencesSection from './FiniteDifferencesSection.vue'
import ThreePointSection from './ThreePointSection.vue'

/**
 * Métodos de la categoría que tienen teoría escrita, y su sección propia.
 * La fórmula de 5 puntos se agrega aquí con su sección (y su nota en
 * DifferentiationReferencesSection).
 */
export const THEORY_SECTIONS = {
  'diferencias-finitas': FiniteDifferencesSection,
  'tres-puntos': ThreePointSection,
}
</script>

<script setup>
// Página de teoría de un método de la categoría "diferenciación numérica".
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
    <DifferentiationFundamentalsSection />
    <component :is="section" />
    <DifferentiationReferencesSection :method="method" />
  </TheoryLayout>
</template>
