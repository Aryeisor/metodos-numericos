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
// cada uno), y en medio va la sección propia del método.
import { computed } from 'vue'
import { CURRENT_COLOR, PREVIOUS_COLOR } from './content'

const props = defineProps({
  method: { type: String, required: true },
})

const section = computed(() => THEORY_SECTIONS[props.method])
</script>

<template>
  <div class="theory">
    <FundamentalsSection />
    <component :is="section" />
    <ComparisonSection />
    <ReferencesSection />
  </div>
</template>

<!--
  Estilos globales acotados a .theory: deben alcanzar el interior de las
  secciones (componentes hijo), cosa que un <style scoped> no hace. Cada
  regla conserva la especificidad que tenía como estilo scoped.
-->
<style>
.theory h3 {
  margin-top: var(--space-5);
}

.theory ul,
.theory ol {
  padding-left: var(--space-5);
}

.theory li {
  margin-bottom: var(--space-2);
}

/* font-size fijo: KaTeX se dimensiona en em, y así las fórmulas en bloque
   conservan exactamente el tamaño que tenían antes de la escala tipográfica. */
.theory .theory-formula {
  margin: var(--space-3) 0;
  font-size: 1rem;
}

.theory .formula-legend {
  margin: calc(-1 * var(--space-1)) 0 var(--space-4);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

/* Fórmulas emparejadas (las matrices de iteración, o las componentes de un
   paso del ejemplo). El ancho mínimo es el mismo que usa el paso a paso de
   Resolver: por debajo, las sustituciones con fracción quedan cortadas. */
.theory .formula-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: var(--space-3);
}

.theory .formula-pair .theory-formula {
  margin: 0;
}

/* Pasos del algoritmo: tarjetas numeradas que se recorren de un vistazo, en
   lugar de una lista de párrafos. */
.theory .steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr));
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: none;
}

.theory .step {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-4);
  margin: 0;
}

.theory .step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  margin-bottom: var(--space-2);
}

.theory .step-title {
  margin: 0 0 var(--space-1);
  font-size: var(--text-card-title);
  color: var(--color-ink);
}

.theory .step-text {
  margin: 0;
  font-size: var(--text-small);
  line-height: 1.55;
  color: var(--color-ink-muted);
}

/* Las fórmulas en línea dentro de un paso no deben agrandar el interlineado. */
.theory .step-text .katex {
  font-size: 1em;
}

.theory .worked-step {
  margin-bottom: var(--space-4);
}

.theory .worked-step-title {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
}

.theory .legend-prev {
  color: v-bind(PREVIOUS_COLOR);
  font-weight: var(--weight-semibold);
}

.theory .legend-current {
  color: v-bind(CURRENT_COLOR);
  font-weight: var(--weight-semibold);
}

/* Tablas de texto: a diferencia de las de resultados numéricos, se alinean a
   la izquierda y dejan respirar el contenido. */
.theory .comparison-table th,
.theory .comparison-table td {
  text-align: left;
  vertical-align: top;
  padding: var(--space-3);
  line-height: 1.5;
}

.theory .comparison-table tbody th {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
  background: var(--color-sunken);
  white-space: nowrap;
}

.theory .comparison-table td {
  font-size: var(--text-small);
}

.theory .exact-row td {
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
}

/* Valores numéricos alineados a la derecha; las dos primeras columnas son
   etiquetas y se quedan a la izquierda. */
.theory .numeric-table td:nth-child(n + 3),
.theory .numeric-table th:nth-child(n + 3) {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.theory .numeric-table tbody tr {
  background: transparent;
}

.theory .group-start td {
  border-top: 2px solid var(--color-line);
}

.theory .table-caption {
  margin: var(--space-5) 0 var(--space-2);
  color: var(--color-ink-muted);
}

.theory .table-note {
  margin-top: var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.theory .references {
  padding-left: var(--space-5);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.theory .references li {
  margin-bottom: var(--space-3);
}

/* KaTeX inline trae 1.21em por defecto: se reduce para no alterar el
   interlineado de los párrafos. Las fórmulas en bloque conservan su tamaño. */
.theory .math:not(.math-display) .katex {
  font-size: 1.05em;
}

/* En móvil las fórmulas de iteración (fracción + sumatorias) no caben a
   tamaño completo: se reducen un poco en vez de obligar a desplazarse. */
@media (max-width: 480px) {
  .theory .theory-formula {
    padding: 10px;
  }

  .theory .theory-formula .katex-display > .katex {
    font-size: 0.8em;
  }
}
</style>
