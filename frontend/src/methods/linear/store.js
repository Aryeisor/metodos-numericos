// Estado del formulario de un sistema lineal A·x = b (n, A, b, x0, reordenar).
// Lo crea SolverView y se comparte con los componentes de la categoría; las
// mutaciones pasan por estas funciones.
import { reactive } from 'vue'

const MIN_VARIABLES = 3
const MAX_VARIABLES = 12

function makeZeroMatrix(size) {
  return Array.from({ length: size }, () => Array(size).fill(0))
}

function makeZeroVector(size) {
  return Array(size).fill(0)
}

export function createLinearSystemStore() {
  const state = reactive({
    n: 3,
    A: makeZeroMatrix(3),
    b: makeZeroVector(3),
    x0: makeZeroVector(3),
    autoReorder: true,
  })

  // Cambia el tamaño conservando los valores que ya estaban escritos.
  function setN(newN) {
    const size = Math.max(MIN_VARIABLES, Math.min(MAX_VARIABLES, Math.floor(newN) || MIN_VARIABLES))
    const newA = makeZeroMatrix(size)
    const newB = makeZeroVector(size)
    const newX0 = makeZeroVector(size)

    for (let i = 0; i < Math.min(size, state.n); i++) {
      for (let j = 0; j < Math.min(size, state.n); j++) {
        newA[i][j] = state.A[i][j]
      }
      newB[i] = state.b[i]
      newX0[i] = state.x0[i]
    }

    state.n = size
    state.A = newA
    state.b = newB
    state.x0 = newX0
  }

  function loadExample(example) {
    state.n = example.n
    state.A = example.A.map((row) => [...row])
    state.b = [...example.b]
    state.x0 = example.x0 ? [...example.x0] : makeZeroVector(example.n)
  }

  // Los campos de A, b y x0 entregan números ya parseados (con la precisión
  // completa de la fracción escrita); un NaN significa que ese campo es inválido.
  function hasInvalidValues() {
    return (
      state.A.some((row) => row.some((v) => !Number.isFinite(v))) ||
      state.b.some((v) => !Number.isFinite(v)) ||
      state.x0.some((v) => !Number.isFinite(v))
    )
  }

  function buildPayload() {
    return {
      A: state.A.map((row) => [...row]),
      b: [...state.b],
      x0: [...state.x0],
      auto_reorder: state.autoReorder,
    }
  }

  return { state, setN, loadExample, hasInvalidValues, buildPayload }
}
