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

const examples = ref([])
const selectedExampleId = ref('')

const loading = ref(false)
const formErrors = ref([])
const result = ref(null)

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

function toNumber(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

async function handleSolve() {
  formErrors.value = []
  result.value = null
  loading.value = true
  try {
    const payload = {
      A: A.value.map((row) => row.map(toNumber)),
      b: b.value.map(toNumber),
      x0: x0.value.map(toNumber),
      tolerance: tolerance.value,
      max_iterations: maxIterations.value,
    }
    result.value = await solveSystem(method.value, payload)
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
      <ResultsTable :result="result" />
    </div>
  </div>
</template>

<style scoped>
.hint {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-top: -6px;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}

.example-btn {
  text-align: left;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.example-btn:hover {
  border-color: var(--color-primary);
}

.example-btn.active {
  border-color: var(--color-primary);
  background: #eef4ff;
}

.example-name {
  font-weight: 700;
  font-size: 0.9rem;
}

.example-desc {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.solve-btn {
  margin-bottom: 20px;
  padding: 10px 24px;
  font-size: 1rem;
}

.results-card {
  margin-top: 0;
}
</style>
