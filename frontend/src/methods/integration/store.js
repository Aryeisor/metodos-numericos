// Estado del formulario de integración numérica. Dos modos de entrada que
// conservan cada uno lo escrito:
//  - «Función»: f(x), a, b y los segmentos iniciales n₀;
//  - «Tabla de datos»: puntos (xᵢ, yᵢ) con espaciado libre y, opcional, una
//    función para comparar.
// La tolerancia y el máximo de refinamientos los maneja SolverView (ver index.js).
import { reactive } from 'vue'

// Mismos límites que el backend (solvers/integration/trapezoid.py).
export const MIN_POINTS = 2
export const MAX_POINTS = 30
export const DEFAULT_ROWS = 9
export const DEFAULT_N0 = 1

export const MODES = { FUNCTION: 'function', TABLE: 'table' }

const emptyRows = (n) => Array.from({ length: n }, () => [null, null])

export function createIntegrationStore() {
  const state = reactive({
    mode: MODES.FUNCTION,
    function: '',
    // [a, b]; null = campo vacío.
    start: [null, null],
    n0: DEFAULT_N0,
    points: emptyRows(DEFAULT_ROWS),
    compare: '',
  })

  function setMode(mode) {
    state.mode = mode
  }

  function addRow() {
    if (state.points.length < MAX_POINTS) state.points = [...state.points, [null, null]]
  }

  function removeRow(index) {
    if (state.points.length > MIN_POINTS) state.points = state.points.filter((_, i) => i !== index)
  }

  function loadExample(example) {
    state.mode = example.mode
    if (example.mode === MODES.TABLE) {
      state.points = example.points.map(([x, y]) => [x, y])
      state.compare = example.compare_function ?? ''
    } else {
      state.function = example.function
      state.start = [example.a, example.b]
      state.n0 = example.n0
    }
  }

  // Los campos numéricos aceptan fracciones; NaN marca un campo inválido. Un
  // campo vacío (null) lo informa el backend con el nombre del campo.
  function hasInvalidValues() {
    const numbers = state.mode === MODES.TABLE ? state.points.flat() : state.start
    return numbers.some((v) => v !== null && !Number.isFinite(v))
  }

  function buildPayload() {
    if (state.mode === MODES.TABLE) {
      return {
        mode: MODES.TABLE,
        points: state.points.map(([x, y]) => [x, y]),
        compare_function: state.compare.trim(),
      }
    }
    const [a, b] = state.start
    return { mode: MODES.FUNCTION, function: state.function.trim(), a, b, n0: state.n0 }
  }

  return {
    state,
    minPoints: MIN_POINTS,
    maxPoints: MAX_POINTS,
    // Textos del formulario compartido (components/FunctionTableInput.vue).
    startFields: {
      title: 'Límites de integración (a < b)',
      labels: ['a', 'b'],
      errorLabels: ['Límite inferior a', 'Límite superior b'],
    },
    compareHint:
      'Si conoces la función de la que salen los datos, escríbela para comparar con su integral, ' +
      'ver el error verdadero y la cota, y comprobar los datos.',
    setMode,
    addRow,
    removeRow,
    loadExample,
    hasInvalidValues,
    buildPayload,
  }
}
