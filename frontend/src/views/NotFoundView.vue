<script setup>
// Dirección que no corresponde a ninguna página: un método que ya no existe,
// un enlace viejo o un error al escribir. Si el último segmento se parece a
// algún método, se sugiere (en la misma sección: Resolver o Teoría).
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import MethodHeader from '../components/MethodHeader.vue'
import { hasTheory, methodRegistry, solveRouteName, theoryRouteName } from '../methods/registry'
import { parseMissingPath, suggestMethods } from '../methods/suggest'

const MAX_SHOWN = 40
const clip = (text) => (text.length > MAX_SHOWN ? `${text.slice(0, MAX_SHOWN - 1)}…` : text)

const route = useRoute()
const segments = computed(() => [route.params.pathMatch ?? []].flat())
const missing = computed(() => parseMissingPath(segments.value))

const suggestions = computed(() =>
  suggestMethods(missing.value.text, methodRegistry.methods).map((method) => ({
    method,
    to: {
      name:
        missing.value.section === 'teoria' && hasTheory(method)
          ? theoryRouteName(method.slug)
          : solveRouteName(method.slug),
    },
  }))
)

// Texto escrito por el usuario: sólo con interpolación (Vue lo escapa) y recortado.
const typed = computed(() => clip(missing.value.raw))
const typedPath = computed(() => clip(`/${segments.value.join('/')}`))

const header = computed(() => ({
  categoryLabel: 'Dirección no encontrada',
  name: suggestions.value.length ? `No existe un método llamado «${typed.value}»` : 'Esta página no existe',
}))

const methodsLabel = computed(() => `Ver los ${methodRegistry.methods.length} métodos`)

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
    <div class="not-found-intro">
      <div class="not-found-text">
        <MethodHeader :method="header" />
        <p v-if="suggestions.length" class="not-found-lead">
          La dirección <code class="not-found-path">{{ typedPath }}</code> no corresponde a ningún método.
          Puede ser un enlace viejo o un error de escritura.
        </p>
        <p v-else class="not-found-lead">
          La dirección no corresponde a ninguna página del sistema; puede ser un enlace viejo o tener un error de escritura.
        </p>
      </div>

      <!-- Una curva con una discontinuidad justo donde se buscaba. -->
      <svg class="not-found-figure" viewBox="0 0 240 170" aria-hidden="true" focusable="false">
        <line class="fig-axis" x1="16" y1="130" x2="232" y2="130" />
        <line class="fig-axis" x1="24" y1="14" x2="24" y2="138" />
        <line class="fig-gap" x1="130" y1="18" x2="130" y2="130" />
        <path class="fig-curve" d="M 28 112 C 60 108, 96 84, 126 58" />
        <path class="fig-curve" d="M 134 96 C 160 92, 196 66, 228 30" />
        <circle class="fig-hole" cx="130" cy="55" r="4.5" />
        <circle class="fig-hole" cx="130" cy="95" r="4.5" />
        <text class="fig-label" x="130" y="156" text-anchor="middle">x = aquí</text>
      </svg>
    </div>

    <section v-if="suggestions.length" class="not-found-suggestions" aria-labelledby="not-found-suggestions-title">
      <h2 id="not-found-suggestions-title">¿Buscabas alguno de estos?</h2>
      <ul class="suggestion-list">
        <li v-for="{ method, to } in suggestions" :key="method.slug">
          <RouterLink :to="to" class="suggestion">
            <span class="suggestion-name">{{ method.name }}</span>
            <span class="suggestion-category">{{ method.categoryLabel }}</span>
            <span v-if="method.summary" class="suggestion-summary">{{ method.summary }}</span>
          </RouterLink>
        </li>
      </ul>
    </section>

    <div class="not-found-actions">
      <button type="button" class="btn btn-primary" @click="openMethodsMenu">{{ methodsLabel }}</button>
      <RouterLink to="/" class="btn btn-secondary">Ir al inicio</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.not-found-intro {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 260px);
  align-items: center;
  gap: var(--space-6);
}

.not-found-text {
  min-width: 0;
}

/* El titular lleva texto del usuario: que corte palabras largas sin desbordar. */
.not-found-text :deep(.method-name) {
  overflow-wrap: anywhere;
  text-wrap: balance;
}

.not-found-lead {
  margin: 0;
  max-width: 65ch;
  line-height: var(--leading-body);
  color: var(--color-ink-muted);
}

.not-found-path {
  font-family: var(--font-mono);
  font-size: 0.9em;
  overflow-wrap: anywhere;
  color: var(--color-ink);
}

/* Desplazada hacia abajo sin mover el texto: así no queda pegada arriba y
   equilibra el bloque texto + sugerencias. */
.not-found-figure {
  position: relative;
  top: calc(var(--space-7) + var(--space-5)); /* «x = aquí» a la altura de «¿Buscabas…?» */
  display: block;
  width: 100%;
  height: auto;
}

.fig-axis,
.fig-gap {
  stroke: var(--color-line-strong);
  stroke-width: 1.5;
  fill: none;
}

.fig-gap {
  stroke-dasharray: 4 4;
}

.fig-curve {
  stroke: var(--color-accent);
  stroke-width: 3;
  stroke-linecap: round;
  fill: none;
}

.fig-hole {
  fill: var(--color-surface);
  stroke: var(--color-accent);
  stroke-width: 2.5;
}

.fig-label {
  fill: var(--color-ink-muted);
  font-family: var(--font-mono);
  font-size: 13px;
}

.not-found-suggestions {
  margin-top: var(--space-6);
}

.not-found-suggestions h2 {
  margin: 0 0 var(--space-4);
}

.suggestion-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 230px), 1fr));
  gap: var(--space-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

.suggestion {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  height: 100%;
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  box-shadow: var(--shadow-interactive);
  color: var(--color-ink);
  text-decoration: none;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}

.suggestion:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-interactive-hover);
}

.suggestion:focus-visible {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-interactive), var(--focus-ring);
}

.suggestion-name {
  font-size: var(--text-card-title);
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
}

.suggestion-category {
  font-size: var(--text-small);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--color-ink-muted);
}

.suggestion-summary {
  overflow: hidden;
  font-size: var(--text-small);
  white-space: nowrap;
  text-overflow: ellipsis;
  color: var(--color-ink-muted);
}

.not-found-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.not-found-actions .btn {
  text-decoration: none;
}

@media (max-width: 720px) {
  .not-found-intro {
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-4);
  }

  .not-found-figure {
    max-width: 220px;
    top: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .suggestion {
    transition: none;
  }
}
</style>
