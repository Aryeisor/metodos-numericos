// Estado del formulario de Bairstow: el polinomio como texto o como
// coeficientes (dos modos de entrada que conservan cada uno lo escrito), y los
// valores iniciales r₀ y s₀. Lo crea SolverView y se comparte con los
// componentes de la categoría; las mutaciones pasan por estas funciones.
import { reactive } from 'vue'

// Mismos límites que el backend (solvers/polynomial/validation.py).
export const MIN_DEGREE = 3
export const MAX_DEGREE = 10
export const DEFAULT_R0 = -1
export const DEFAULT_S0 = -1

export const MODES = { TEXT: 'text', COEFFICIENTS: 'coefficients' }

export function createPolynomialStore() {
  const state = reactive({
    mode: MODES.TEXT,
    text: '',
    degree: MIN_DEGREE,
    // Descendentes: aₙ … a₀.
    coefficients: Array(MIN_DEGREE + 1).fill(0),
    initial: [DEFAULT_R0, DEFAULT_S0], // [r₀, s₀]
  })

  function setMode(mode) {
    state.mode = mode
  }

  // Cambia el grado conservando los coeficientes de cada potencia (los de
  // las potencias bajas no se mueven; las nuevas potencias altas valen 0).
  function setDegree(degree) {
    const size = Math.max(MIN_DEGREE, Math.min(MAX_DEGREE, Math.floor(degree) || MIN_DEGREE))
    const old = state.coefficients
    state.coefficients = Array.from({ length: size + 1 }, (_, p) => {
      const power = size - p
      const oldIndex = old.length - 1 - power
      return oldIndex >= 0 ? old[oldIndex] : 0
    })
    state.degree = size
  }

  function loadExample(example) {
    state.mode = example.mode
    if (example.mode === MODES.TEXT) {
      state.text = example.polynomial
    } else {
      state.coefficients = [...example.coefficients]
      state.degree = example.coefficients.length - 1
    }
    state.initial = [example.r0, example.s0]
  }

  // Los campos numéricos aceptan fracciones; NaN marca un campo inválido. El
  // texto del polinomio lo valida el backend (parser seguro).
  function hasInvalidValues() {
    const numbers = state.mode === MODES.COEFFICIENTS ? [...state.coefficients, ...state.initial] : state.initial
    return numbers.some((v) => !Number.isFinite(v))
  }

  function buildPayload() {
    const [r0, s0] = state.initial
    return state.mode === MODES.TEXT
      ? { polynomial: state.text.trim(), r0, s0 }
      : { coefficients: [...state.coefficients], r0, s0 }
  }

  return { state, setMode, setDegree, loadExample, hasInvalidValues, buildPayload }
}
