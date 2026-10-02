<script setup>
import { computed, ref, shallowRef, watch } from 'vue'
import { useRouter } from 'vue-router'
import ResultsTable from '../components/ResultsTable.vue'
import { fetchExamples, solveSystem } from '../api/client'
import { getMethod, siblingMethods, solveRouteName } from '../methods/registry'
import { exportResultToPdf } from '../utils/exportPdf'

const props = defineProps({
  // Slug del método activo; lo fija la ruta /resolver/<slug>.
  method: { type: String, default: null },
})

const router = useRouter()

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

const tolerance = ref(0.000001)
const maxIterations = ref(100)

const examples = ref([])
const selectedExampleId = ref('')

const loading = ref(false)
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
  () => {
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
}

async function handleSolve() {
  formErrors.value = []
  result.value = null
  solvedSystem.value = null

  if (store.value.hasInvalidValues()) {
    formErrors.value = [ui.value.invalidMessage]
    return
  }

  loading.value = true
  try {
    const payload = {
      ...store.value.buildPayload(),
      tolerance: tolerance.value,
      max_iterations: maxIterations.value,
    }
    const response = await solveSystem(props.method, payload)
    result.value = response
    solvedSystem.value = ui.value.solvedSystem(payload, response)
  } catch (err) {
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
    loading.value = false
  }
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
    <div class="card">
      <h2>Ejemplos precargados</h2>
      <p class="hint">Selecciona un ejemplo para cargarlo en el formulario.</p>
      <div class="examples-grid">
        <button
          v-for="ex in examples"
          :key="ex.id"
          class="example-btn"
          :class="{ active: ex.id === selectedExampleId }"
          type="button"
          @click="loadExample(ex)"
        >
          <span class="example-name">{{ ex.name }}</span>
          <span class="example-desc">{{ ex.description }}</span>
        </button>
      </div>
    </div>

    <div class="card">
      <h2>{{ ui.configTitle }}</h2>
      <div class="grid-2">
        <component
          :is="ui.configFields"
          v-if="ui.configFields"
          :store="store"
          @structure-changed="selectedExampleId = ''"
        />
        <div class="field">
          <label>Método</label>
          <select v-model="selectedMethod">
            <option v-for="m in siblings" :key="m.slug" :value="m.slug">{{ m.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Tolerancia (criterio de parada)</label>
          <input type="number" step="any" v-model.number="tolerance" />
        </div>
        <div class="field">
          <label>Máximo de iteraciones (mínimo real: 6)</label>
          <input type="number" min="1" v-model.number="maxIterations" />
        </div>
      </div>

      <component :is="ui.configExtras" v-if="ui.configExtras" :store="store" />
    </div>

    <div class="card">
      <h2>{{ ui.formTitle }}</h2>
      <component :is="ui.form" v-bind="ui.formBindings(store)" />
    </div>

    <div v-if="formErrors.length" class="alert alert-danger">
      <div v-for="(msg, idx) in formErrors" :key="idx">{{ msg }}</div>
    </div>

    <button class="btn btn-primary solve-btn" type="button" :disabled="loading" @click="handleSolve">
      {{ loading ? 'Resolviendo...' : 'Resolver' }}
    </button>

    <div v-if="result" class="card results-card">
      <ResultsTable
        :result="result"
        :method-name="resultMethodName"
        :tolerance="solvedSystem ? solvedSystem.tolerance : null"
        @export-pdf="handleExportPdf"
      >
        <template v-if="ui.resultSummary" #summary>
          <component :is="ui.resultSummary" :result="result" />
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
      </ResultsTable>
    </div>
  </div>
</template>

<style scoped>
.hint {
  color: var(--color-ink-muted);
  font-size: var(--text-small);
  margin: 0 0 var(--space-5);
}

/* Flexbox en vez de grid: con columnas de grid los tracks ocupan todo el
   ancho y no hay espacio libre que repartir, así que las tarjetas sobrantes
   de la última fila quedan siempre pegadas a la izquierda. */
.examples-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-3);
}

/* Elementos clicables: única familia con sombra, para diferenciarlos de los
   contenedores estáticos que sólo llevan borde.

   El ancho se fija por breakpoint (ver abajo) en vez de dejar que crezcan:
   así una fila completa llena el ancho igual que antes, y las tarjetas
   sobrantes de la última fila conservan su tamaño y sólo quedan centradas. */
.example-btn {
  flex: 0 1 100%;
  text-align: left;
  border: 1px solid var(--color-line);
  background: var(--color-surface);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
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

.example-desc {
  font-size: var(--text-small);
  line-height: 1.45;
  color: var(--color-ink-muted);
}

/* Aire entre el título de sección y su contenido (formulario o matriz). */
.card > h2 + div {
  margin-top: var(--space-5);
}

/* Tarjetas por fila según el ancho de pantalla. El ancho es
   (100% - huecos) / columnas, de modo que una fila completa llena
   exactamente el contenedor, como hacía la grilla anterior. */
@media (min-width: 641px) {
  .example-btn {
    flex-basis: calc(50% - var(--space-3) * 0.5);
  }
}

@media (min-width: 800px) {
  .example-btn {
    flex-basis: calc(33.3333% - var(--space-3) * 0.6667);
  }
}

@media (min-width: 1024px) {
  .example-btn {
    flex-basis: calc(25% - var(--space-3) * 0.75);
  }
}

.solve-btn {
  margin-bottom: var(--space-6);
  padding: var(--space-3) var(--space-6);
  font-size: 1rem;
}

.results-card {
  margin-top: 0;
}
</style>
