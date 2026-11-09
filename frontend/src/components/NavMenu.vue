<script setup>
// Menú de métodos de la barra superior: un panel con todas las categorías en
// columnas y un buscador. «Resolver ▾» y «Teoría ▾» abren el mismo panel en su
// modo; en pantallas de menos de 1024 px un botón «Métodos» lo abre a
// pantalla completa, con las categorías como acordeones. Todo sale del
// registro (nombre, línea, sinónimos y datos de la categoría): un método o una
// categoría nuevos aparecen solos.
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import MathFormula from './MathFormula.vue'
import {
  hasTheory,
  methodRegistry,
  methodsByCategory,
  solveRouteName,
  theoryRouteName,
} from '../methods/registry'

const DESKTOP_QUERY = '(min-width: 1024px)'
const MAIN_ID = 'contenido'
const PANEL_ID = 'nav-panel'
const MODES = [
  { key: 'solve', label: 'Resolver' },
  { key: 'theory', label: 'Teoría' },
]

const route = useRoute()
const router = useRouter()

const desktopMedia = window.matchMedia(DESKTOP_QUERY)
const isDesktop = ref(desktopMedia.matches)
const onMediaChange = (event) => {
  isDesktop.value = event.matches
}

const isOpen = ref(false)
const mode = ref('solve')
const query = ref('')
const openGroups = ref(new Set()) // acordeones abiertos (celular)
let opener = null // botón al que vuelve el foco al cerrar

const rootRef = ref(null)
const panelRef = ref(null)
const searchRef = ref(null)
const solveTriggerRef = ref(null)
const mobileTriggerRef = ref(null)

// ---- Datos -----------------------------------------------------------------

const currentSection = computed(() => {
  if (route.meta.theoryMethod || route.name === 'theory') return 'theory'
  if (route.meta.method || route.name === 'home') return 'solve'
  return null
})
const currentSlug = computed(() => route.meta.method ?? route.meta.theoryMethod ?? null)

const allGroups = computed(() => methodsByCategory())
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`
const catalogSummary = computed(
  () =>
    `${plural(methodRegistry.methods.length, 'método', 'métodos')} en ` +
    plural(allGroups.value.length, 'categoría', 'categorías')
)

/** Minúsculas y sin tildes: «Diferenciación» y «diferenciacion» son iguales. */
const fold = (text) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

const tokens = computed(() => fold(query.value).split(/\s+/).filter(Boolean))

function matches(method) {
  const haystack = fold([method.name, method.summary, method.categoryLabel, ...method.keywords].join(' '))
  return tokens.value.every((token) => haystack.includes(token))
}

const groups = computed(() =>
  methodsByCategory((method) => (mode.value === 'solve' || hasTheory(method)) && matches(method))
)
const resultCount = computed(() => groups.value.reduce((n, group) => n + group.methods.length, 0))

const status = computed(() => {
  if (!tokens.value.length) return ''
  if (resultCount.value) return plural(resultCount.value, 'método', 'métodos')
  return `No hay métodos que coincidan con «${query.value.trim()}». Prueba con «integral», «derivada» o «sistema».`
})

const registryError = computed(() => methodRegistry.status === 'error')

/** Partes del nombre con las coincidencias de la búsqueda marcadas. */
function highlight(name) {
  const plain = [{ text: name, match: false }]
  if (!tokens.value.length) return plain
  const chars = [...name]
  const folded = chars.map(fold)
  // shortcut: si un carácter cambia de largo al plegarlo no se resalta nada (no pasa en español).
  if (folded.some((c) => c.length !== 1)) return plain
  const flat = folded.join('')
  const marks = chars.map(() => false)
  for (const token of tokens.value) {
    for (let i = flat.indexOf(token); i !== -1; i = flat.indexOf(token, i + token.length)) {
      marks.fill(true, i, i + token.length)
    }
  }
  const parts = []
  chars.forEach((char, i) => {
    const last = parts.at(-1)
    if (last && last.match === marks[i]) last.text += char
    else parts.push({ text: char, match: marks[i] })
  })
  return parts
}

const linkTo = (slug) => ({ name: mode.value === 'theory' ? theoryRouteName(slug) : solveRouteName(slug) })
const isCurrent = (slug) =>
  slug === (mode.value === 'theory' ? route.meta.theoryMethod : route.meta.method)
const triggerActive = (key) => (isOpen.value ? mode.value === key : currentSection.value === key)

const isGroupOpen = (category) => tokens.value.length > 0 || openGroups.value.has(category)
function toggleGroup(category) {
  const next = new Set(openGroups.value)
  if (next.has(category)) next.delete(category)
  else next.add(category)
  openGroups.value = next
}

// ---- Abrir y cerrar --------------------------------------------------------

async function openPanel(nextMode, from) {
  mode.value = nextMode
  opener = from
  const current = methodRegistry.methods.find((m) => m.slug === currentSlug.value)
  openGroups.value = new Set(current ? [current.category] : [])
  isOpen.value = true
  await nextTick()
  searchRef.value?.focus()
}

/** focus: 'opener' (vuelve al botón), 'main' (tras navegar) o 'none'. */
function close({ focus = 'opener' } = {}) {
  if (!isOpen.value) return
  isOpen.value = false
  query.value = ''
  if (focus === 'opener') opener?.focus()
  else if (focus === 'main') nextTick(() => document.getElementById(MAIN_ID)?.focus())
}

function onTrigger(key, event) {
  if (!isOpen.value) openPanel(key, event.currentTarget)
  else if (mode.value === key) close()
  else {
    mode.value = key
    opener = event.currentTarget
  }
}

function onMobileTrigger(event) {
  if (isOpen.value) close()
  else openPanel(currentSection.value ?? 'solve', event.currentTarget)
}

function go(slug) {
  router.push(linkTo(slug))
  close({ focus: 'main' })
}

// ---- Teclado ---------------------------------------------------------------

function onSearchKeydown(event) {
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    panelRef.value?.querySelector('a.nav-item')?.focus()
  } else if (event.key === 'Enter') {
    event.preventDefault()
    const first = groups.value[0]?.methods[0]
    if (first) go(first.slug)
  }
}

const ARROWS = { ArrowDown: [0, 1], ArrowUp: [0, -1], ArrowRight: [1, 0], ArrowLeft: [-1, 0] }

/** Escritorio: ↑ ↓ dentro de una columna y ← → entre columnas. */
function onItemKeydown(event, col, row) {
  const move = ARROWS[event.key]
  if (!isDesktop.value || !move) return
  event.preventDefault()
  const [dCol, dRow] = move
  if (dRow === -1 && row === 0) return searchRef.value?.focus()
  const nextCol = col + dCol
  const target = groups.value[nextCol]
  if (!target) return
  const nextRow = dCol ? Math.min(row, target.methods.length - 1) : row + dRow
  panelRef.value?.querySelector(`[data-col="${nextCol}"][data-row="${nextRow}"]`)?.focus()
}

/** Con el foco en un campo de texto, «/» se escribe: no abre el menú. */
function isTyping(target) {
  return (
    target instanceof Element &&
    (target.isContentEditable || Boolean(target.closest('input, textarea, select')))
  )
}

/** Celular: el foco no sale del panel a pantalla completa. */
function trapFocus(event) {
  const items = [...panelRef.value.querySelectorAll('a[href], button, input')].filter(
    (el) => el.offsetParent !== null
  )
  if (!items.length) return
  const first = items[0]
  const last = items.at(-1)
  const active = document.activeElement
  if (!panelRef.value.contains(active)) {
    event.preventDefault()
    first.focus()
  } else if (event.shiftKey && active === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && active === last) {
    event.preventDefault()
    first.focus()
  }
}

function onDocumentKeydown(event) {
  if (isOpen.value && event.key === 'Escape') {
    event.preventDefault()
    close()
  } else if (isOpen.value && event.key === 'Tab' && !isDesktop.value) {
    trapFocus(event)
  } else if (
    event.key === '/' &&
    !event.ctrlKey &&
    !event.metaKey &&
    !event.altKey &&
    !isTyping(event.target)
  ) {
    event.preventDefault()
    if (isOpen.value) searchRef.value?.focus()
    else openPanel('solve', (isDesktop.value ? solveTriggerRef : mobileTriggerRef).value)
  }
}

function onDocumentPointerdown(event) {
  if (isOpen.value && isDesktop.value && !rootRef.value?.contains(event.target)) close()
}

// Al navegar por otro camino (atrás, un enlace de la página) se cierra.
watch(
  () => route.fullPath,
  () => close({ focus: 'none' })
)

// El panel a pantalla completa no deja desplazar la página de fondo.
watch([isOpen, isDesktop], ([open, desktop]) => {
  document.body.style.overflow = open && !desktop ? 'hidden' : ''
})

onMounted(() => {
  desktopMedia.addEventListener('change', onMediaChange)
  document.addEventListener('keydown', onDocumentKeydown)
  document.addEventListener('pointerdown', onDocumentPointerdown)
})
onBeforeUnmount(() => {
  desktopMedia.removeEventListener('change', onMediaChange)
  document.removeEventListener('keydown', onDocumentKeydown)
  document.removeEventListener('pointerdown', onDocumentPointerdown)
  document.body.style.overflow = ''
})
</script>

<template>
  <nav ref="rootRef" class="nav-menu" aria-label="Métodos">
    <template v-if="isDesktop">
      <button
        ref="solveTriggerRef"
        type="button"
        class="nav-link"
        :class="{ 'is-active': triggerActive('solve') }"
        :aria-expanded="isOpen && mode === 'solve'"
        :aria-controls="PANEL_ID"
        @click="onTrigger('solve', $event)"
      >
        Resolver <span class="nav-caret" aria-hidden="true">▾</span>
      </button>
      <button
        type="button"
        class="nav-link"
        :class="{ 'is-active': triggerActive('theory') }"
        :aria-expanded="isOpen && mode === 'theory'"
        :aria-controls="PANEL_ID"
        @click="onTrigger('theory', $event)"
      >
        Teoría <span class="nav-caret" aria-hidden="true">▾</span>
      </button>
    </template>
    <button
      v-else
      ref="mobileTriggerRef"
      type="button"
      class="nav-mobile-trigger"
      aria-label="Métodos"
      :aria-expanded="isOpen"
      :aria-controls="PANEL_ID"
      @click="onMobileTrigger"
    >
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <span>Métodos</span>
    </button>

    <div
      v-if="isOpen"
      :id="PANEL_ID"
      ref="panelRef"
      class="nav-panel"
      :class="isDesktop ? 'is-desktop' : 'is-mobile'"
      :role="isDesktop ? undefined : 'dialog'"
      :aria-modal="isDesktop ? undefined : 'true'"
      :aria-labelledby="isDesktop ? undefined : 'nav-dialog-title'"
    >
      <div class="nav-panel-inner">
        <div v-if="!isDesktop" class="nav-dialog-head">
          <h2 id="nav-dialog-title" class="nav-dialog-title">Métodos</h2>
          <button type="button" class="nav-close" @click="close()">Cerrar</button>
        </div>

        <div class="nav-toolbar">
          <div class="nav-segmented" role="group" aria-label="Los enlaces llevan a">
            <button
              v-for="item in MODES"
              :key="item.key"
              type="button"
              :aria-pressed="mode === item.key"
              @click="mode = item.key"
            >
              {{ item.label }}
            </button>
          </div>
          <div class="nav-search">
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              ref="searchRef"
              v-model="query"
              type="search"
              aria-label="Buscar método"
              placeholder="Buscar método…"
              autocomplete="off"
              spellcheck="false"
              @keydown="onSearchKeydown"
            />
          </div>
        </div>

        <p class="nav-status" :class="{ 'is-empty': tokens.length && !resultCount }" aria-live="polite">{{ status }}</p>
        <p v-if="registryError" class="nav-error">No fue posible cargar los métodos.</p>

        <div class="nav-groups">
          <section
            v-for="(group, col) in groups"
            :key="group.category"
            class="nav-group"
            :aria-labelledby="`nav-group-${group.category}`"
          >
            <template v-if="isDesktop">
              <div v-if="group.latex" class="nav-glyph" aria-hidden="true">
                <MathFormula :expression="group.latex" />
              </div>
              <h2 :id="`nav-group-${group.category}`" class="nav-group-title">{{ group.label }}</h2>
              <p v-if="group.description" class="nav-group-desc">{{ group.description }}</p>
            </template>
            <h2 v-else class="nav-group-title">
              <button
                type="button"
                class="nav-accordion"
                :aria-expanded="isGroupOpen(group.category)"
                :aria-controls="`nav-list-${group.category}`"
                @click="toggleGroup(group.category)"
              >
                <span :id="`nav-group-${group.category}`">{{ group.label }}</span>
                <span v-if="group.latex" class="nav-glyph-small" aria-hidden="true">
                  <MathFormula :expression="group.latex" />
                </span>
                <svg class="nav-chevron" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </button>
            </h2>

            <ul
              v-show="isDesktop || isGroupOpen(group.category)"
              :id="`nav-list-${group.category}`"
              class="nav-list"
            >
              <li v-for="(method, row) in group.methods" :key="method.slug">
                <RouterLink
                  :to="linkTo(method.slug)"
                  class="nav-item"
                  :class="{ 'is-current': isCurrent(method.slug) }"
                  :aria-current="isCurrent(method.slug) ? 'page' : undefined"
                  :title="method.summary ? `${method.name}: ${method.summary}` : method.name"
                  :data-col="col"
                  :data-row="row"
                  @click="close({ focus: 'main' })"
                  @keydown="onItemKeydown($event, col, row)"
                >
                  <span class="nav-item-name">
                    <template v-for="(part, i) in highlight(method.name)" :key="i">
                      <mark v-if="part.match">{{ part.text }}</mark>
                      <template v-else>{{ part.text }}</template>
                    </template>
                  </span>
                  <span v-if="method.summary" class="nav-item-summary">{{ method.summary }}</span>
                </RouterLink>
              </li>
            </ul>
          </section>
        </div>

        <p class="nav-footer">
          {{ catalogSummary }}.<template v-if="isDesktop"> Pulsa / para buscar y Esc para cerrar.</template>
        </p>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="isOpen && isDesktop" class="nav-backdrop" aria-hidden="true"></div>
    </Teleport>
  </nav>
</template>

<style scoped>
.nav-menu {
  display: flex;
  gap: var(--space-5);
}

/* ---- Botones de la barra ------------------------------------------------ */

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: 0;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  color: var(--color-ink-muted);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  cursor: pointer;
  transition: color var(--transition-fast), border-color var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-ink);
}

.nav-link.is-active {
  color: var(--color-accent);
  font-weight: var(--weight-semibold);
  border-bottom-color: var(--color-accent);
}

.nav-caret {
  font-size: 0.75em;
}

.nav-mobile-trigger {
  align-self: center;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 40px;
  padding: 0 var(--space-3);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--color-ink);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  cursor: pointer;
}

.nav-mobile-trigger:hover {
  background: var(--nav-item-hover);
}

svg {
  flex-shrink: 0;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Foco: contorno de 2 px en el color de acento (≥ 3:1 en ambos temas). */
.nav-link:focus-visible,
.nav-mobile-trigger:focus-visible,
.nav-panel :focus-visible {
  box-shadow: none;
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.nav-link:focus-visible {
  outline-offset: 4px;
  border-radius: 2px;
}

.nav-panel .nav-item:focus-visible,
.nav-panel .nav-accordion:focus-visible {
  outline-offset: -2px;
}

/* ---- Panel -------------------------------------------------------------- */

.nav-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  background: var(--nav-backdrop);
}

/* Escritorio: bajo la barra, alineado con el contenedor de la app. */
.nav-panel.is-desktop {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  padding: 0 var(--space-4);
  pointer-events: none; /* los lados transparentes dejan pasar el clic al fondo */
}

.is-desktop .nav-panel-inner {
  pointer-events: auto;
  max-width: calc(var(--container-width) - 2 * var(--space-4));
  max-height: calc(100vh - var(--header-height) - var(--space-5));
  overflow-y: auto;
  overscroll-behavior: contain;
  margin: var(--space-2) auto 0;
  padding: var(--space-5);
  background: var(--nav-panel-bg);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-container);
  box-shadow: var(--shadow-interactive-hover);
}

/* Celular y tablet: diálogo a pantalla completa. */
.nav-panel.is-mobile {
  position: fixed;
  inset: 0;
  z-index: 50;
  overflow-y: auto;
  overscroll-behavior: contain;
  background: var(--nav-panel-bg);
}

.is-mobile .nav-panel-inner {
  padding: var(--space-3) var(--space-4) var(--space-5);
}

@media (prefers-reduced-motion: no-preference) {
  .is-desktop .nav-panel-inner,
  .nav-panel.is-mobile {
    animation: nav-in 150ms ease-out;
  }
}

@keyframes nav-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
}

.nav-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.nav-dialog-title {
  margin: 0;
  font-size: var(--text-subsection);
}

.nav-close {
  min-height: 44px;
  padding: 0 var(--space-4);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: transparent;
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  cursor: pointer;
}

.nav-close:hover {
  background: var(--nav-item-hover);
}

/* ---- Barra del panel: modo y buscador ----------------------------------- */

.nav-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3) var(--space-4);
}

.nav-segmented {
  display: inline-flex;
  padding: 2px;
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: var(--color-input);
}

.nav-segmented button {
  min-height: 32px;
  padding: 0 var(--space-4);
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--color-ink-muted);
  font-size: var(--text-small);
  font-weight: var(--weight-medium);
  cursor: pointer;
}

.nav-segmented button:hover {
  color: var(--color-ink);
}

.nav-segmented button[aria-pressed='true'] {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.nav-search {
  position: relative;
  flex: 0 1 340px;
  margin-left: auto;
  color: var(--color-ink-muted);
}

.nav-search svg {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.nav-search input {
  width: 100%;
  min-height: 40px;
  padding: 0 var(--space-3) 0 36px;
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: var(--color-input);
  color: var(--color-ink);
  font-size: var(--text-body);
}

.nav-search input::placeholder {
  color: var(--color-ink-muted);
}

.nav-search input:focus-visible {
  outline-offset: 0;
  border-color: var(--color-accent);
}

.is-mobile .nav-segmented,
.is-mobile .nav-search {
  flex: 1 1 100%;
  margin-left: 0;
}

.is-mobile .nav-segmented button {
  flex: 1;
  min-height: 40px;
}

.is-mobile .nav-search input {
  min-height: 44px;
}

.nav-status {
  margin: 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.nav-status:not(:empty) {
  margin-top: var(--space-3);
}

.nav-status.is-empty {
  font-size: var(--text-body);
  color: var(--color-ink);
}

.nav-error {
  margin: var(--space-3) 0 0;
  color: var(--color-danger);
  font-size: var(--text-small);
}

/* ---- Categorías --------------------------------------------------------- */

.nav-groups {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--space-5) var(--space-5);
  margin-top: var(--space-5);
}

/* Entre 1024 y 1279 px cinco columnas no caben con holgura: tres y una
   segunda fila. */
@media (max-width: 1279px) {
  .nav-groups {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.is-mobile .nav-groups {
  display: block;
  margin-top: var(--space-3);
}

.nav-glyph {
  display: flex;
  align-items: flex-end;
  min-height: 2.6rem;
  margin-bottom: var(--space-2);
  font-size: 1.35rem;
  color: var(--nav-glyph);
}

.nav-group-title {
  margin: 0;
  font-size: var(--text-card-title);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.nav-group-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: var(--space-1) 0 0;
  font-size: var(--text-small);
  line-height: var(--leading-tight);
  color: var(--color-ink-muted);
}

.nav-list {
  margin: var(--space-3) 0 0;
  padding: var(--space-2) 0 0;
  list-style: none;
  border-top: 1px solid var(--color-line);
}

/* El texto de los ítems queda alineado con el del encabezado. */
.is-desktop .nav-list li {
  margin-inline: calc(-1 * (var(--space-3) + 3px));
}

.nav-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 44px;
  padding: var(--space-2) var(--space-3);
  border-left: 3px solid transparent;
  border-radius: var(--radius-control);
  color: var(--color-ink);
  text-decoration: none;
  line-height: var(--leading-tight);
  transition: background-color var(--transition-fast);
}

.nav-item:hover {
  background: var(--nav-item-hover);
}

.nav-item.is-current {
  background: var(--nav-item-active);
  border-left-color: var(--color-accent);
}

.nav-item-name {
  font-weight: var(--weight-medium);
}

.nav-item-summary {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 2px;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

mark {
  background: transparent;
  color: var(--color-accent);
  font-weight: var(--weight-semibold);
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* Acordeones (celular). */
.is-mobile .nav-group {
  border-bottom: 1px solid var(--color-line);
}

.nav-accordion {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  min-height: 52px;
  padding: var(--space-2) var(--space-1);
  border: none;
  background: transparent;
  font-size: var(--text-body);
  font-weight: var(--weight-semibold);
  text-align: left;
  cursor: pointer;
}

.nav-glyph-small {
  margin-left: auto;
  font-size: 0.95rem;
  font-weight: var(--weight-regular);
  color: var(--nav-glyph);
}

.nav-chevron {
  color: var(--color-ink-muted);
}

.nav-accordion[aria-expanded='true'] .nav-chevron {
  transform: rotate(180deg);
}

.is-mobile .nav-list {
  margin: 0 0 var(--space-3);
  padding: 0;
  border-top: none;
}

.nav-footer {
  margin: var(--space-5) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}
</style>
