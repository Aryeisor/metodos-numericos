// Estado del formulario de diferenciación numérica. Dos modos de entrada que
// conservan cada uno lo escrito:
//  - «Función»: f(x), x₀ y h₀;
//  - «Tabla de datos»: puntos (xᵢ, yᵢ) y, opcional, una función para comparar.
// En ambos, la fórmula (las opciones dependen del método: ver abajo). La tolerancia y el
// máximo de refinamientos los maneja SolverView (ver index.js).
import { reactive } from 'vue'

// Mismos límites que el backend (solvers/differentiation/finite_differences.py).
export const MIN_POINTS = 2
export const MAX_POINTS = 20
export const DEFAULT_ROWS = 6
export const DEFAULT_H0 = 0.1

export const MODES = { FUNCTION: 'function', TABLE: 'table' }

export const FORMULA_OPTIONS = [
  { value: 'forward', label: 'Progresiva' },
  { value: 'backward', label: 'Regresiva' },
  { value: 'both', label: 'Ambas' },
]

// Fórmula de 3 puntos (mismos valores que THREE_POINT_CHOICES del backend).
export const THREE_POINT_OPTIONS = [
  { value: 'punto_medio', label: 'Punto medio' },
  { value: 'extremo_adelante', label: 'Extremo hacia adelante' },
  { value: 'extremo_atras', label: 'Extremo hacia atrás' },
  { value: 'all', label: 'Todas' },
]

// Fórmula de 5 puntos (mismos valores que FIVE_POINT_CHOICES del backend).
export const FIVE_POINT_OPTIONS = [
  { value: 'punto_medio_5', label: 'Punto medio' },
  { value: 'extremo_adelante_5', label: 'Extremo hacia adelante' },
  { value: 'extremo_atras_5', label: 'Extremo hacia atrás' },
  { value: 'all', label: 'Todas' },
]

const emptyRows = (n) => Array.from({ length: n }, () => [null, null])

/**
 * Cada método de la categoría pasa sus opciones del selector, la fórmula por
 * defecto, el mínimo de puntos del modo tabla y las filas vacías iniciales.
 */
export function createDifferentiationStore({
  formulaOptions = FORMULA_OPTIONS,
  defaultFormula = 'both',
  minPoints = MIN_POINTS,
  defaultRows = DEFAULT_ROWS,
} = {}) {
  const state = reactive({
    mode: MODES.FUNCTION,
    function: '',
    // [x₀, h₀]; null = campo vacío.
    start: [null, DEFAULT_H0],
    formula: defaultFormula,
    points: emptyRows(defaultRows),
    compare: '',
  })

  function setMode(mode) {
    state.mode = mode
  }

  function addRow() {
    if (state.points.length < MAX_POINTS) state.points = [...state.points, [null, null]]
  }

  function removeRow(index) {
    if (state.points.length > minPoints) state.points = state.points.filter((_, i) => i !== index)
  }

  function loadExample(example) {
    state.mode = example.mode
    state.formula = example.formula
    if (example.mode === MODES.TABLE) {
      state.points = example.points.map(([x, y]) => [x, y])
      state.compare = example.compare_function ?? ''
    } else {
      state.function = example.function
      state.start = [example.x0, example.h0]
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
        formula: state.formula,
        points: state.points.map(([x, y]) => [x, y]),
        compare_function: state.compare.trim(),
      }
    }
    const [x0, h0] = state.start
    return { mode: MODES.FUNCTION, formula: state.formula, function: state.function.trim(), x0, h0 }
  }

  return {
    state,
    formulaOptions,
    minPoints,
    setMode,
    addRow,
    removeRow,
    loadExample,
    hasInvalidValues,
    buildPayload,
  }
}

export const createThreePointStore = () =>
  createDifferentiationStore({ formulaOptions: THREE_POINT_OPTIONS, defaultFormula: 'all', minPoints: 3 })

export const createFivePointStore = () =>
  createDifferentiationStore({
    formulaOptions: FIVE_POINT_OPTIONS,
    defaultFormula: 'all',
    minPoints: 5,
    defaultRows: 9,
  })
