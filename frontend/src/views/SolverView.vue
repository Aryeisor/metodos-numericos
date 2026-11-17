<script setup>
import { computed, nextTick, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import MethodHeader from '../components/MethodHeader.vue'
import ResultAnswer from '../components/ResultAnswer.vue'
import ResultsTable from '../components/ResultsTable.vue'
import { fetchExamples, solveSystem } from '../api/client'
import { resultAnswer } from '../methods/answer'
import { getMethod, siblingMethods, solveRouteName } from '../methods/registry'
import { exportResultToPdf } from '../utils/exportPdf'
import { scrollBehavior } from '../utils/motion'

const props = defineProps({
  // Slug del método activo; lo fija la ruta /resolver/<slug>.
  method: { type: String, default: null },
})

const router = useRouter()
const route = useRoute()

const activeMethod = computed(() => getMethod(props.method))
const ui = computed(() => activeMethod.value?.ui ?? null)
const siblings = computed(() => siblingMethods(props.method))

// Selector "Método": cambia de ruta. Como todas las rutas de resolución usan
// esta misma vista, los datos del formulario se conservan entre métodos de la
// misma categoría.
const selectedMethod = computed({
  get: () => props.method,
  set: (slug) => router.push({ name: solveRouteName(slug) }),
})

const DEFAULT_TOLERANCE = 0.000001
const DEFAULT_MAX_ITERATIONS = 100
const tolerance = ref(DEFAULT_TOLERANCE)
const maxIterations = ref(DEFAULT_MAX_ITERATIONS)
let previousDefaults = {}

// Valores por defecto del método activo (Bairstow tiene su tolerancia en %;
// diferencias finitas, su máximo de refinamientos de h).
const defaultTolerance = () => ui.value?.defaultTolerance ?? DEFAULT_TOLERANCE
const defaultMaxIterations = () => ui.value?.defaultMaxIterations ?? DEFAULT_MAX_ITERATIONS

const examples = ref([])
const selectedExampleId = ref('')
const selectedExample = computed(
  () => examples.value.find((ex) => ex.id === selectedExampleId.value) ?? null
)
// Sección de ejemplos plegable: abierta al entrar; se pliega sola al cargar un
// ejemplo o al escribir en el formulario. No se guarda entre visitas.
const examplesOpen = ref(true)

const loading = ref(false)
// El estado «Resolviendo…» sólo se ve si el cálculo pasa de BUSY_DELAY_MS: por
// debajo, un indicador que aparece y desaparece molesta más que no poner nada.
// Mientras tanto `loading` ya impide volver a enviar.
const BUSY_DELAY_MS = 300
const busy = ref(false)
let busyTimer = null
watch(loading, (isLoading) => {
  clearTimeout(busyTimer)
  busy.value = false
  if (isLoading) busyTimer = setTimeout(() => (busy.value = true), BUSY_DELAY_MS)
})
onBeforeUnmount(() => clearTimeout(busyTimer))
const formErrors = ref([])
const result = ref(null)
// Datos de entrada tal como se resolvieron: permiten reconstruir en el
// frontend el paso a paso de cada iteración sin pedir nada extra al backend.
const solvedSystem = ref(null)

// Estado del formulario (para sistemas lineales: n, A, b, x0...). Se recrea
// sólo si cambia el formulario, no al cambiar entre métodos que lo comparten
// (Jacobi y Gauss-Seidel). Métodos de una misma categoría pueden tener
// formularios distintos (Punto Fijo y Newton), así que la clave es la función
// que crea el estado, no la categoría. Al cambiar también se descarta el
// resultado anterior: su forma es distinta y lo dibujan otros componentes.
const store = shallowRef(null)
watch(
  () => ui.value?.createStore,
  (_, previousCreateStore) => {
    // Una categoría puede tener su propia tolerancia o máximo por defecto
    // (Bairstow usa %). Al entrar en ella se aplican; al salir, se vuelve a
    // los generales. Entre categorías sin valores propios se conserva lo que
    // haya escrito.
    const own = { tolerance: ui.value?.defaultTolerance, max: ui.value?.defaultMaxIterations }
    if (own.tolerance !== undefined) tolerance.value = own.tolerance
    else if (previousCreateStore && previousDefaults.tolerance !== undefined) tolerance.value = DEFAULT_TOLERANCE
    if (own.max !== undefined) maxIterations.value = own.max
    else if (previousCreateStore && previousDefaults.max !== undefined) maxIterations.value = DEFAULT_MAX_ITERATIONS
    previousDefaults = own

    store.value = ui.value ? ui.value.createStore() : null
    result.value = null
    solvedSystem.value = null
    formErrors.value = []
    selectedExampleId.value = ''
  },
  { immediate: true }
)

watch(
  () => props.method,
  async (slug) => {
    if (!getMethod(slug)) return
    try {
      examples.value = await fetchExamples(slug)
      // «Resolver este ejemplo» de la Teoría: /resolver/<slug>?ejemplo=<id> lo carga y lo resuelve.
      const requested = examples.value.find((ex) => ex.id === route.query.ejemplo)
      if (requested) {
        router.replace({ query: {} })
        loadExample(requested)
        handleSolve()
      }
    } catch (err) {
      formErrors.value = ['No fue posible cargar los ejemplos desde el servidor.']
    }
  },
  { immediate: true }
)

function loadExample(example) {
  store.value.loadExample(example)
  tolerance.value = example.tolerance
  maxIterations.value = example.max_iterations
  selectedExampleId.value = example.id
  result.value = null
  formErrors.value = []
  examplesOpen.value = false
}

// Cada petición de resolver lleva un número; «Limpiar» lo incrementa, así que
// una respuesta que llega después (de una petición ya descartada) se ignora.
let solveRequestId = 0

// Al terminar de resolver la página va sola a lo que apareció, y el foco con
// ella (así lo anuncia un lector de pantalla): el encabezado del resultado o,
// si falló, el mensaje de error.
const answerRef = ref(null)
const detailRef = ref(null)
const errorsRef = ref(null)
const answer = computed(() => (result.value ? resultAnswer(result.value) : null))

async function revealOutcome() {
  await nextTick()
  if (result.value) return answerRef.value?.reveal()
  errorsRef.value?.scrollIntoView({ behavior: scrollBehavior(), block: 'center' })
  errorsRef.value?.focus({ preventScroll: true })
}

async function handleSolve() {
  if (loading.value) return
  formErrors.value = []
  result.value = null
  solvedSystem.value = null

  if (store.value.hasInvalidValues()) {
    formErrors.value = [ui.value.invalidMessage]
    revealOutcome()
    return
  }

  const requestId = ++solveRequestId
  const isCurrent = () => requestId === solveRequestId
  loading.value = true
  try {
    const payload = {
      ...store.value.buildPayload(),
      tolerance: tolerance.value,
      max_iterations: maxIterations.value,
    }
    const response = await solveSystem(props.method, payload)
    if (!isCurrent()) return
    result.value = response
    solvedSystem.value = ui.value.solvedSystem(payload, response)
  } catch (err) {
    if (!isCurrent()) return
    if (err.response && err.response.data) {
      const data = err.response.data
      const messages = []
      if (Array.isArray(data.detail)) {
        messages.push(...data.detail)
      } else if (typeof data.detail === 'string') {
        messages.push(data.detail)
      } else {
        for (const key of Object.keys(data)) {
          const val = data[key]
          if (Array.isArray(val)) messages.push(...val)
          else messages.push(String(val))
        }
      }
      formErrors.value = messages.length ? messages : ['Ocurrió un error al validar los datos.']
    } else {
      formErrors.value = ['No fue posible conectar con el servidor. Verifica que el backend esté corriendo.']
    }
  } finally {
    if (isCurrent()) {
      loading.value = false
      revealOutcome()
    }
  }
}

// --- Limpiar -----------------------------------------------------------------
// Deja la vista como al abrir el método: el estado inicial sale de la misma
// función que crea el formulario al entrar (ui.createStore), y la tolerancia y
// el máximo de iteraciones de los mismos valores por defecto. El método, la
// ruta y la categoría no cambian.
//
// Los formularios guardan estado propio (el texto de cada casilla, sus
// errores, las vistas previas LaTeX): `formKey` los vuelve a montar desde cero.
const formKey = ref(0)
const formCardRef = ref(null)
const confirmOpen = ref(false)

const snapshot = (s) => JSON.stringify(s.state)

// Una categoría puede ocultar la tolerancia y el máximo según su formulario
// (diferencias finitas en modo «Tabla de datos» no itera).
const showIterationFields = computed(() => !ui.value?.hidesIterationFields?.(store.value))
// Estado inicial del formulario del método activo, para compararlo.
const initialSnapshot = computed(() => (ui.value ? snapshot(ui.value.createStore()) : null))

const formIsInitial = computed(
  () =>
    !store.value ||
    (snapshot(store.value) === initialSnapshot.value &&
      tolerance.value === defaultTolerance() &&
      maxIterations.value === defaultMaxIterations())
)
// Al cambiar de método los ejemplos vuelven a abrirse, salvo que el formulario
// conserve datos (Jacobi y Gauss-Seidel lo comparten).
watch(
  () => props.method,
  () => {
    examplesOpen.value = formIsInitial.value && !selectedExampleId.value
  }
)

// Con datos escritos o un resultado en pantalla se pide confirmación; sólo
// con errores o una marca de ejemplo se limpia directamente.
const clearNeedsConfirm = computed(() => !formIsInitial.value || Boolean(result.value))
const canClear = computed(
  () => clearNeedsConfirm.value || formErrors.value.length > 0 || Boolean(selectedExampleId.value) || loading.value
)

function requestClear() {
  if (!canClear.value) return
  if (clearNeedsConfirm.value) confirmOpen.value = true
  else clearExercise()
}

function confirmClear() {
  confirmOpen.value = false
  clearExercise()
}

const FIRST_FIELD = 'input:not([disabled]):not([readonly]), textarea:not([disabled]), select:not([disabled])'

async function clearExercise() {
  solveRequestId++ // descarta la respuesta de una petición en curso
  loading.value = false
  store.value = ui.value.createStore()
  tolerance.value = defaultTolerance()
  maxIterations.value = defaultMaxIterations()
  result.value = null
  solvedSystem.value = null
  formErrors.value = []
  selectedExampleId.value = ''
  examplesOpen.value = true
  formKey.value++

  await nextTick()
  const card = formCardRef.value
  card?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  card?.querySelector(FIRST_FIELD)?.focus({ preventScroll: true })
}

// Nombre del método con el que se obtuvo el resultado (puede diferir del
// método activo si el usuario cambió de método sin volver a resolver).
const resultMethodName = computed(
  () => getMethod(result.value?.method)?.name ?? result.value?.method ?? ''
)

function handleExportPdf(chartImage) {
  exportResultToPdf({
    result: result.value,
    methodName: resultMethodName.value,
    chartImage,
    report: ui.value.pdfReport({ result: result.value, system: solvedSystem.value }),
  })
}
</script>

<template>
  <div v-if="!activeMethod" class="alert alert-danger">
    No fue posible cargar los métodos desde el servidor. Verifica que el backend esté corriendo.
  </div>

  <div v-else>
    <MethodHeader :method="activeMethod" />

    <section class="examples">
      <h2 class="examples-heading">
        <button
          type="button"
          class="examples-toggle"
          :aria-expanded="examplesOpen"
          aria-controls="examples-panel"
          @click="examplesOpen = !examplesOpen"
        >
          <span class="examples-caret" aria-hidden="true">{{ examplesOpen ? '▾' : '▸' }}</span>
          <span class="examples-title">
            Ejemplos precargados<template v-if="!examplesOpen && !selectedExample"> ({{ examples.length }})</template>
            <template v-if="!examplesOpen && selectedExample">
              · <em class="examples-current">{{ selectedExample.name }}</em>
            </template>
          </span>
          <span class="examples-action">
            {{ examplesOpen ? 'Ocultar' : selectedExample ? 'Cambiar' : 'Mostrar' }}
          </span>
        </button>
      </h2>
      <div v-show="examplesOpen" id="examples-panel" class="examples-panel">
        <p class="hint">Selecciona un ejemplo para cargarlo en el formulario.</p>
        <div class="examples-grid" :class="{ 'is-four': examples.length % 3 !== 0 }">
          <button
            v-for="ex in examples"
            :key="ex.id"
            class="example-btn"
            :class="{ active: ex.id === selectedExampleId }"
            type="button"
            @click="loadExample(ex)"
          >
            <span class="example-name">{{ ex.name }}</span>
            <span class="example-desc" :title="ex.description">{{ ex.description }}</span>
          </button>
        </div>
      </div>
    </section>

    <!-- «Escribir en el formulario» = cualquier evento input de sus campos
         (teclear, elegir una opción, marcar una casilla); pliega los ejemplos.
         El selector de método no cuenta: sólo cambia de ruta. -->
    <div @input="examplesOpen = false">
      <div class="card input-card">
        <h2>{{ ui.configTitle }}</h2>
        <div class="grid-2">
          <component
            :is="ui.configFields"
            v-if="ui.configFields"
            :key="formKey"
            :store="store"
            @structure-changed="selectedExampleId = ''"
          />
          <div class="field" @input.stop>
            <label>Método</label>
            <select v-model="selectedMethod">
              <option v-for="m in siblings" :key="m.slug" :value="m.slug">{{ m.name }}</option>
            </select>
          </div>
          <div v-if="showIterationFields" class="field">
            <label>{{ ui.toleranceLabel ?? 'Tolerancia (criterio de parada)' }}</label>
            <input type="number" step="any" v-model.number="tolerance" />
          </div>
          <div v-if="showIterationFields" class="field">
            <label>{{ ui.maxIterationsLabel ?? 'Máximo de iteraciones (mínimo real: 6)' }}</label>
            <input type="number" min="1" v-model.number="maxIterations" />
          </div>
        </div>

        <component :is="ui.configExtras" v-if="ui.configExtras" :key="formKey" :store="store" />
      </div>

      <div ref="formCardRef" class="card input-card form-card">
        <h2>{{ ui.formTitle }}</h2>
        <component :is="ui.form" :key="formKey" v-bind="ui.formBindings(store)" />
      </div>
    </div>

    <div v-if="formErrors.length" ref="errorsRef" class="alert alert-danger" role="alert" tabindex="-1">
      <div v-for="(msg, idx) in formErrors" :key="idx">{{ msg }}</div>
    </div>

    <div class="solve-actions">
      <button
        class="btn btn-primary solve-btn"
        :class="{ 'is-busy': busy }"
        type="button"
        :disabled="busy"
        :aria-disabled="loading || undefined"
        @click="handleSolve"
      >
        <span v-if="busy" class="solve-spinner" aria-hidden="true"></span>
        {{ busy ? 'Resolviendo…' : 'Resolver' }}
      </button>
      <span class="visually-hidden" role="status" aria-live="polite">{{ busy ? 'Resolviendo…' : '' }}</span>
      <button
        class="btn btn-outline solve-btn"
        type="button"
        aria-label="Limpiar formulario y resultado"
        :disabled="!canClear"
        @click="requestClear"
      >
        Limpiar
      </button>
    </div>

    <ConfirmDialog
      :open="confirmOpen"
      message="¿Borrar el ejercicio actual? Se perderán los datos y el resultado."
      confirm-label="Limpiar"
      cancel-label="Cancelar"
      @confirm="confirmClear"
      @cancel="confirmOpen = false"
    />

    <p v-if="!result && !busy" class="result-placeholder">
      Al pulsar Resolver, aquí aparecen la respuesta y el detalle de cada iteración.
    </p>

    <template v-if="result">
      <!-- Lo primero: la respuesta. Sus botones actúan sobre el detalle de abajo
           (el PDF necesita las gráficas que éste dibuja). -->
      <ResultAnswer
        ref="answerRef"
        :method-name="resultMethodName"
        :answer="answer"
        @export-pdf="detailRef?.exportPdf()"
        @clear="requestClear"
      />

      <div class="result-detail">
      <!-- Una categoría cuyo resultado no es una sola tabla de iteraciones
           (Bairstow: varios factores, cada uno con su tabla y su gráfico)
           aporta su propia vista completa, PDF incluido. -->
      <component
        :is="ui.resultView"
        v-if="ui.resultView && solvedSystem"
        ref="detailRef"
        :result="result"
        :system="solvedSystem"
        :method-name="resultMethodName"
      />
      <ResultsTable
        v-else-if="!ui.resultView"
        ref="detailRef"
        :result="result"
        :method-name="resultMethodName"
        :tolerance="solvedSystem ? solvedSystem.tolerance : null"
        @export-pdf="handleExportPdf"
      >
        <template v-if="ui.resultSummary" #summary>
          <component :is="ui.resultSummary" :result="result" />
        </template>
        <!-- Opcional: lo que no cambia entre iteraciones (ej. el Jacobiano de Newton). -->
        <template v-if="ui.beforeIterations" #before-iterations>
          <component :is="ui.beforeIterations" :result="result" />
        </template>
        <template v-if="ui.iterationDetail && solvedSystem" #iteration-detail="{ index }">
          <component
            :is="ui.iterationDetail"
            :result="result"
            :system="solvedSystem"
            :index="index"
            :method-name="resultMethodName"
          />
        </template>
        <!-- Opcional: sección final (ej. la comprobación de los métodos lineales). -->
        <template v-if="ui.afterIterations" #after-iterations>
          <component :is="ui.afterIterations" :result="result" />
        </template>
      </ResultsTable>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* Los ejemplos son ayuda opcional: un escalón por debajo de las tarjetas del
   formulario. Fondo de la página y borde, sin superficie ni sombra. */
.examples {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-container);
  margin-bottom: var(--space-5);
}

.examples-heading {
  margin: 0;
  font-size: var(--text-subsection);
}

/* Mismo patrón de plegado que el paso a paso: ▸ / ▾ y aria-expanded. Toda la
   fila es el control. */
.examples-toggle {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: none;
  border-radius: var(--radius-container);
  background: transparent;
  font: inherit;
  letter-spacing: inherit;
  text-align: left;
  cursor: pointer;
}

.examples-caret {
  color: var(--color-accent);
  font-size: var(--text-small);
}

.examples-title {
  flex: 1;
  min-width: 0;
}

.examples-current {
  font-weight: var(--weight-regular);
}

.examples-action {
  font-size: var(--text-small);
  font-weight: var(--weight-medium);
  letter-spacing: 0;
  color: var(--color-accent);
}

.examples-toggle:hover .examples-action {
  text-decoration: underline;
}

.examples-panel {
  padding: 0 var(--space-4) var(--space-4);
}

.hint {
  color: var(--color-ink-muted);
  font-size: var(--text-small);
  margin: 0 0 var(--space-3);
}

/* Grid: la última fila queda alineada al inicio, nunca centrada. Columnas por
   ancho: 1, 2, 3 y, desde 1024px, 4 si el total no es múltiplo de 3 (4, 7 u
   8 ejemplos); con 3, 6 o 9 se queda en 3 y no deja tarjetas huérfanas. */
.examples-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-3);
}

/* Elementos clicables: única familia con sombra, para diferenciarlos de los
   contenedores estáticos que sólo llevan borde. */
.example-btn {
  text-align: left;
  border: 1px solid var(--color-line);
  background: var(--color-surface);
  border-radius: var(--radius-nested);
  padding: var(--space-3);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  box-shadow: var(--shadow-interactive);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast),
    background-color var(--transition-fast);
}

.example-btn:hover {
  border-color: var(--color-line-strong);
  box-shadow: var(--shadow-interactive-hover);
}

.example-btn:focus-visible {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-interactive), var(--focus-ring);
}

.example-btn.active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
  box-shadow: inset 0 0 0 1px var(--color-accent);
}

.example-name {
  font-size: var(--text-card-title);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-ink);
}

.example-btn.active .example-name {
  color: var(--color-accent-hover);
}

/* Dos líneas como máximo; el texto completo va en el title. */
.example-desc {
  font-size: var(--text-small);
  line-height: 1.45;
  color: var(--color-ink-muted);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

/* Separación entre secciones de la mitad de entrada. */
.input-card {
  margin-bottom: var(--space-5);
}

/* Aire entre el título de sección y su contenido (formulario o matriz). */
.card > h2 + div {
  margin-top: var(--space-5);
}

@media (min-width: 641px) {
  .examples-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 800px) {
  .examples-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .examples-grid.is-four {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

/* Resolver (principal, relleno) y Limpiar (secundario, con borde) en la misma
   fila y con el mismo alto. */
.solve-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.solve-btn {
  justify-content: center;
  padding: var(--space-3) var(--space-6);
  font-size: 1rem;
}

/* Ocupado: deshabilitado pero legible (sin la opacidad de .btn:disabled, que
   dejaría el texto sin contraste). */
.solve-btn.is-busy:disabled {
  opacity: 1;
  cursor: progress;
}

.solve-spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: solve-spin 0.8s linear infinite;
}

@keyframes solve-spin {
  to {
    transform: rotate(360deg);
  }
}

/* Sin giro: el texto «Resolviendo…» basta para saber que está trabajando. */
@media (prefers-reduced-motion: reduce) {
  .solve-spinner {
    animation: none;
  }
}

.result-placeholder {
  margin: 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

/* Al limpiar, la página sube hasta el formulario; el margen deja ver el título. */
.form-card {
  scroll-margin-top: var(--space-5);
}

/* En móvil, los dos botones reparten la fila con el mismo ancho; si no caben,
   quedan uno debajo del otro a todo el ancho. */
@media (max-width: 480px) {
  .solve-btn {
    flex: 1 1 0;
    padding-left: var(--space-4);
    padding-right: var(--space-4);
  }
}

@media (max-width: 300px) {
  .solve-actions {
    flex-direction: column;
  }
}

/* El mensaje de error recibe el foco cuando la resolución falla. */
.alert-danger:focus-visible {
  box-shadow: var(--focus-ring);
}

/* El detalle del resultado, un escalón por debajo de la tarjeta de respuesta
   (como los ejemplos): fondo de la página y borde, sin superficie ni sombra.
   La jerarquía la dan la superficie, el peso y el espacio, no el color. */
.result-detail {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-container);
  padding: var(--space-5) var(--space-6);
}

/* Secciones del detalle (cada componente trae la suya): separadas --space-5. */
.result-detail :deep(.result-section),
.result-detail :deep(.chart-block),
.result-detail :deep(.verification),
.result-detail :deep(.jacobian-section),
.result-detail :deep(.iterations-title) {
  margin-top: var(--space-5);
}

/* Las gráficas conservan debajo la superficie sobre la que se midió el
   contraste de sus colores. Sombra y no borde: un borde cambiaría el tamaño
   del lienzo, que es la imagen que va al PDF. */
.result-detail :deep(.chart-canvas-wrapper) {
  background: var(--color-surface);
  border-radius: var(--radius-nested);
  box-shadow: 0 0 0 1px var(--color-line);
}

/* La primera no necesita la línea que la separa de la anterior. */
.result-detail :deep(.results > :first-child),
.result-detail :deep(.results > .summary:empty + *) {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

@media (max-width: 640px) {
  .result-detail {
    padding: var(--space-5) var(--space-4);
  }
}
</style>
