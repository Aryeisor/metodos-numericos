<script setup>
import { onMounted, ref } from 'vue'
import MatrixInput from '../components/MatrixInput.vue'
import ResultsTable from '../components/ResultsTable.vue'
import { fetchExamples, solveSystem } from '../api/client'

const MIN_VARIABLES = 3

const n = ref(3)
const A = ref(makeZeroMatrix(3))
const b = ref(makeZeroVector(3))
const x0 = ref(makeZeroVector(3))
const tolerance = ref(0.000001)
const maxIterations = ref(100)
const method = ref('jacobi')
const autoReorder = ref(true)

const examples = ref([])
const selectedExampleId = ref('')

const loading = ref(false)
const formErrors = ref([])
const result = ref(null)
// Copia del sistema tal como se envió a la API: permite reconstruir en el
// frontend el paso a paso de cada iteración sin pedir nada extra al backend.
const solvedSystem = ref(null)

function makeZeroMatrix(size) {
  return Array.from({ length: size }, () => Array(size).fill(0))
}

function makeZeroVector(size) {
  return Array(size).fill(0)
}

function setN(newN) {
  const size = Math.max(MIN_VARIABLES, Math.min(12, Math.floor(newN) || MIN_VARIABLES))
  const newA = makeZeroMatrix(size)
  const newB = makeZeroVector(size)
  const newX0 = makeZeroVector(size)

  for (let i = 0; i < Math.min(size, n.value); i++) {
    for (let j = 0; j < Math.min(size, n.value); j++) {
      newA[i][j] = A.value[i][j]
    }
    newB[i] = b.value[i]
    newX0[i] = x0.value[i]
  }

  n.value = size
  A.value = newA
  b.value = newB
  x0.value = newX0
  selectedExampleId.value = ''
}

function onNInput(event) {
  setN(Number(event.target.value))
}

function loadExample(example) {
  n.value = example.n
  A.value = example.A.map((row) => [...row])
  b.value = [...example.b]
  x0.value = example.x0 ? [...example.x0] : makeZeroVector(example.n)
  tolerance.value = example.tolerance
  maxIterations.value = example.max_iterations
  selectedExampleId.value = example.id
  result.value = null
  formErrors.value = []
}

// Los campos de A, b y x0 entregan números ya parseados (con la precisión
// completa de la fracción escrita); un NaN significa que ese campo es inválido.
function hasInvalidValues() {
  return (
    A.value.some((row) => row.some((v) => !Number.isFinite(v))) ||
    b.value.some((v) => !Number.isFinite(v)) ||
    x0.value.some((v) => !Number.isFinite(v))
  )
}

async function handleSolve() {
  formErrors.value = []
  result.value = null
  solvedSystem.value = null

  if (hasInvalidValues()) {
    formErrors.value = [
      'Hay campos del sistema con un valor inválido (marcados en rojo). ' +
        'Corrígelos antes de resolver.',
    ]
    return
  }

  loading.value = true
  try {
    const payload = {
      A: A.value.map((row) => [...row]),
      b: [...b.value],
      x0: [...x0.value],
      tolerance: tolerance.value,
      max_iterations: maxIterations.value,
      auto_reorder: autoReorder.value,
    }
    const response = await solveSystem(method.value, payload)
    result.value = response
    // El backend puede haber reordenado las filas: se usa el sistema tal como
    // realmente se calculó para que el paso a paso coincida con las iteraciones.
    solvedSystem.value = { ...payload, A: response.A, b: response.b }
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
      formErrors.value = messages.length ? messages : ['Ocurrió un error al validar el sistema.']
    } else {
      formErrors.value = ['No fue posible conectar con el servidor. Verifica que el backend esté corriendo.']
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    examples.value = await fetchExamples()
  } catch (err) {
    formErrors.value = ['No fue posible cargar los ejemplos desde el servidor.']
  }
})
</script>

<template>
  <div>
    <div class="card">
      <h2>Ejemplos precargados</h2>
      <p class="hint">Selecciona un sistema de ejemplo para cargarlo en el formulario.</p>
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
      <h2>Configuración del sistema</h2>
      <div class="grid-2">
        <div class="field">
          <label>Número de variables (n ≥ 3)</label>
          <input type="number" min="3" max="12" :value="n" @change="onNInput" />
        </div>
        <div class="field">
          <label>Método</label>
          <select v-model="method">
            <option value="jacobi">Jacobi</option>
            <option value="gauss-seidel">Gauss-Seidel</option>
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

      <label class="checkbox-field">
        <input type="checkbox" v-model="autoReorder" />
        <span>
          Reordenar filas automáticamente si mejora la convergencia
          <small>
            Si la matriz no es diagonalmente dominante, se busca un orden de ecuaciones
            que sí lo sea. No cambia la solución del sistema.
          </small>
        </span>
      </label>
    </div>

    <div class="card">
      <h2>Sistema A·x = b</h2>
      <MatrixInput
        :n="n"
        :a="A"
        :b="b"
        :x0="x0"
        @update:a="(v) => (A = v)"
        @update:b="(v) => (b = v)"
        @update:x0="(v) => (x0 = v)"
      />
    </div>

    <div v-if="formErrors.length" class="alert alert-danger">
      <div v-for="(msg, idx) in formErrors" :key="idx">{{ msg }}</div>
    </div>

    <button class="btn btn-primary solve-btn" type="button" :disabled="loading" @click="handleSolve">
      {{ loading ? 'Resolviendo...' : 'Resolver' }}
    </button>

    <div v-if="result" class="card results-card">
      <ResultsTable :result="result" :system="solvedSystem" />
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

.checkbox-field {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin: var(--space-1) 0 0;
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-line);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  color: var(--color-ink);
  cursor: pointer;
}

.checkbox-field input {
  margin: 3px 0 0;
  width: 16px;
  height: 16px;
  cursor: pointer;
  flex-shrink: 0;
}

.checkbox-field small {
  display: block;
  font-weight: var(--weight-regular);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  margin-top: 2px;
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
