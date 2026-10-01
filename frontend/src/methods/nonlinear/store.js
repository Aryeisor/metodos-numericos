// Estado del formulario de un sistema no lineal f_i(x) = 0: las ecuaciones
// como texto, el nombre de la variable que se despeja de cada una y el punto
// inicial. Lo crea SolverView y se comparte con los componentes de la
// categoría; las mutaciones pasan por estas funciones.
import { reactive } from 'vue'

// Mismos límites que el backend (solvers/nonlinear/fixed_point.py).
export const MIN_EQUATIONS = 2
export const MAX_EQUATIONS = 6

// Nombres que se proponen al agregar una ecuación, en orden.
const DEFAULT_NAMES = ['x', 'y', 'z', 'w', 'u', 'v']

function nextVariableName(used) {
  return (
    DEFAULT_NAMES.find((name) => !used.includes(name)) ??
    Array.from({ length: used.length + 1 }, (_, i) => `x${i + 1}`).find((n) => !used.includes(n))
  )
}

export function createNonlinearSystemStore() {
  const state = reactive({
    equations: ['', ''],
    variables: ['x', 'y'],
    x0: [0, 0],
  })

  function addEquation() {
    if (state.equations.length >= MAX_EQUATIONS) return
    state.variables = [...state.variables, nextVariableName(state.variables)]
    state.equations = [...state.equations, '']
    state.x0 = [...state.x0, 0]
  }

  function removeEquation(index) {
    if (state.equations.length <= MIN_EQUATIONS) return
    const keep = (_, i) => i !== index
    state.equations = state.equations.filter(keep)
    state.variables = state.variables.filter(keep)
    state.x0 = state.x0.filter(keep)
  }

  function loadExample(example) {
    state.equations = [...example.equations]
    state.variables = [...example.variables]
    state.x0 = example.x0 ? [...example.x0] : Array(example.equations.length).fill(0)
  }

  // El punto inicial acepta fracciones; NaN marca un campo inválido. Las
  // ecuaciones y los nombres los valida el backend (parser seguro).
  function hasInvalidValues() {
    return state.x0.some((v) => !Number.isFinite(v))
  }

  function buildPayload() {
    return {
      equations: state.equations.map((text) => text.trim()),
      variables: state.variables.map((name) => name.trim()),
      x0: [...state.x0],
    }
  }

  return { state, addEquation, removeEquation, loadExample, hasInvalidValues, buildPayload }
}
