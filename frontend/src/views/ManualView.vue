<script setup>
// Manual de usuario incrustado. Los PDF están en public/manuales/ y Vite (o
// nginx en Docker) los sirve tal cual desde la raíz del sitio.
import { onBeforeUnmount, onMounted, ref } from 'vue'

const USER_MANUAL = '/manuales/manual-de-usuario.pdf'
const TECH_MANUAL = '/manuales/manual-tecnico.pdf'
// shortcut: número de páginas escrito a mano; actualizarlo si se reemplaza el PDF.
const USER_MANUAL_PAGES = 70
const PAGE_TITLE = 'Manual de usuario · Métodos Iterativos'

// Muchos navegadores de celular dejan el iframe en blanco y no se puede
// detectar: por debajo de 768 px se ofrece abrirlo a pantalla completa.
const wideMedia = window.matchMedia('(min-width: 768px)')
const isWide = ref(wideMedia.matches)
const onMediaChange = (event) => {
  isWide.value = event.matches
}

let previousTitle = ''
onMounted(() => {
  previousTitle = document.title
  document.title = PAGE_TITLE
  wideMedia.addEventListener('change', onMediaChange)
})
onBeforeUnmount(() => {
  document.title = previousTitle
  wideMedia.removeEventListener('change', onMediaChange)
})
</script>

<template>
  <section class="manual">
    <header class="manual-head">
      <div>
        <h1 class="manual-title">Manual de usuario</h1>
        <p class="manual-subtitle">
          Cómo usar el sistema paso a paso: elegir un método, ingresar los datos e interpretar los
          resultados. {{ USER_MANUAL_PAGES }} páginas.
        </p>
      </div>
      <div class="manual-actions">
        <a class="btn btn-secondary" :href="USER_MANUAL" target="_blank" rel="noopener">
          Abrir en una pestaña nueva
        </a>
        <a class="btn btn-primary" :href="USER_MANUAL" download="manual-de-usuario.pdf">
          Descargar PDF
        </a>
      </div>
    </header>

    <template v-if="isWide">
      <div class="manual-viewer">
        <iframe title="Manual de usuario" :src="`${USER_MANUAL}#view=FitH`"></iframe>
      </div>
      <p class="manual-hint">
        Si no ves el documento aquí arriba,
        <a :href="USER_MANUAL" target="_blank" rel="noopener">ábrelo en una pestaña nueva</a>.
      </p>
    </template>
    <div v-else class="card manual-mobile">
      <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6M8 13h8M8 17h8M8 9h2" />
      </svg>
      <p>En pantallas pequeñas el manual se ve mejor a pantalla completa</p>
      <a class="btn btn-primary manual-open" :href="USER_MANUAL" target="_blank" rel="noopener">
        Abrir el manual
      </a>
    </div>

    <p class="manual-tech">
      ¿Buscas el manual técnico?
      <a :href="TECH_MANUAL" target="_blank" rel="noopener">Ábrelo aquí</a>
    </p>
  </section>
</template>

<style scoped>
.manual-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.manual-title {
  margin: 0;
}

.manual-subtitle {
  margin: var(--space-2) 0 0;
  color: var(--color-ink-muted);
}

.manual-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.manual-actions .btn {
  text-decoration: none;
}

/* El PDF siempre se dibuja en claro: fondo neutro y borde para que no
   deslumbre flotando sobre el tema oscuro. */
.manual-viewer {
  overflow: hidden;
  background: var(--color-sunken);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-container);
  box-shadow: var(--shadow-card);
}

.manual-viewer iframe {
  display: block;
  width: 100%;
  height: 80vh;
  min-height: 600px;
  border: 0;
}

.manual-hint,
.manual-tech {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.manual-tech {
  margin-top: var(--space-5);
}

.manual-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  text-align: center;
}

.manual-mobile p {
  margin: 0;
}

.manual-mobile svg {
  fill: none;
  stroke: var(--color-accent);
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.manual-open {
  justify-content: center;
  min-height: 48px;
  width: 100%;
  max-width: 320px;
  text-decoration: none;
}
</style>
