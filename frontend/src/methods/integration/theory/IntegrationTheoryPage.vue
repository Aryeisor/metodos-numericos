<script>
import IntegrationFundamentalsSection from './IntegrationFundamentalsSection.vue'
import IntegrationReferencesSection from './IntegrationReferencesSection.vue'
import RombergSection from './RombergSection.vue'
import SimpsonSection from './SimpsonSection.vue'
import TrapezoidSection from './TrapezoidSection.vue'

/**
 * Métodos de la categoría que tienen teoría escrita, y su sección propia.
 * La cuadratura gaussiana se agrega aquí cuando tenga la suya (una línea más).
 */
export const THEORY_SECTIONS = {
  trapecio: TrapezoidSection,
  simpson: SimpsonSection,
  romberg: RombergSection,
}
</script>

<script setup>
// Página de teoría de un método de la categoría "integración numérica".
//
// Misma estructura que las de las otras categorías: el fundamento común y las
// referencias se muestran en todas las páginas de la categoría, y en medio va
// la sección propia del método (que incluye la tabla comparativa compartida).
import { computed } from 'vue'
import TheoryLayout from '../../../components/theory/TheoryLayout.vue'

const props = defineProps({
  method: { type: String, required: true },
})

const section = computed(() => THEORY_SECTIONS[props.method])
</script>

<template>
  <TheoryLayout>
    <IntegrationFundamentalsSection />
    <component :is="section" />
    <IntegrationReferencesSection :method="method" />
  </TheoryLayout>
</template>
