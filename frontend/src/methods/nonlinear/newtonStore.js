// Estado del formulario de Newton: las ecuaciones como texto, las variables
// declaradas en orden (un único campo, "x, y, z") y el punto inicial. A
// diferencia de Punto Fijo, ninguna variable pertenece a una ecuación: el
// orden declarado fija las columnas del Jacobiano y el orden de x0.
import { reactive } from 'vue'
import { MAX_EQUATIONS, MIN_EQUATIONS } from './store'

const DEFAULT_NAMES = ['x', 'y', 'z', 'w', 'u', 'v']

/** "x, y z" -> ["x", "y", "z"]: separa por comas y/o espacios. */
export function parseVariables(text) {
  return String(text ?? '')
    .split(/[\s,;]+/)
    .filter(Boolean)
}

function nextVariableName(used) {
  return (
    DEFAULT_NAMES.find((name) => !used.includes(name)) ??
    Array.from({ length: used.length + 1 }, (_, i) => `x${i + 1}`).find((n) => !used.includes(n))
  )
}

// x0 con un valor por variable, conservando los que ya estaban escritos.
function resize(values, size) {
  return Array.from({ length: size }, (_, i) => values[i] ?? 0)
}

export function createNewtonStore() {
  const state = reactive({
    equations: ['', ''],
    variablesText: 'x, y',
    x0: [0, 0],
  })

  const variables = () => parseVariables(state.variablesText)

  function setVariablesText(text) {
    state.variablesText = text
    state.x0 = resize(state.x0, variables().length)
  }

  // Al agregar una ecuación se propone también una variable nueva, si hasta
  // ahora había tantas variables como ecuaciones (el sistema debe ser cuadrado).
  function addEquation() {
    if (state.equations.length >= MAX_EQUATIONS) return
    const names = variables()
    if (names.length === state.equations.length) {
      setVariablesText([...names, nextVariableName(names)].join(', '))
    }
    state.equations = [...state.equations, '']
  }

  function removeEquation(index) {
    if (state.equations.length <= MIN_EQUATIONS) return
    state.equations = state.equations.filter((_, i) => i !== index)
  }

  function loadExample(example) {
    state.equations = [...example.equations]
    state.variablesText = example.variables.join(', ')
    state.x0 = example.x0 ? [...example.x0] : Array(example.variables.length).fill(0)
  }

  function hasInvalidValues() {
    return state.x0.some((v) => !Number.isFinite(v))
  }

  function buildPayload() {
    return {
      equations: state.equations.map((text) => text.trim()),
      variables: variables(),
      x0: [...state.x0],
    }
  }

  return {
    state,
    variables,
    setVariablesText,
    addEquation,
    removeEquation,
    loadExample,
    hasInvalidValues,
    buildPayload,
  }
}
