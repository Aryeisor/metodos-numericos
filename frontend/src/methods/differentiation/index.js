// Interfaz de la categoría "differentiation" (diferencias finitas).
// Cumple el contrato documentado en methods/linear/index.js, con los campos
// opcionales:
//   resultView            vista completa del resultado (tablas por fórmula,
//                         gráfico, paso a paso, comprobación y PDF)
//   toleranceLabel / defaultTolerance / maxIterationsLabel / defaultMaxIterations
//   hidesIterationFields  en modo «Tabla de datos» no hay refinamiento
//
// La fórmula es un dato del resultado (result.formulas): la misma vista sirve
// para cualquier fórmula de derivación que el backend agregue.
//
// Sin teoría todavía: `theorySections` vacío, así que el método no aparece en
// «Teoría ▾» ni tiene ruta /teoria/<slug>.
import DifferentiationConfigFields from './DifferentiationConfigFields.vue'
import DifferentiationInput from './DifferentiationInput.vue'
import DifferentiationResult from './DifferentiationResult.vue'
import { MODES, createDifferentiationStore } from './store'

export default {
  createStore: createDifferentiationStore,

  configTitle: 'Configuración del método',
  formTitle: 'Datos',
  configFields: DifferentiationConfigFields,
  configExtras: null,

  form: DifferentiationInput,
  formBindings: (store) => ({ store }),

  invalidMessage: 'Hay campos con un valor inválido (marcados en rojo). Corrígelos antes de resolver.',

  solvedSystem: (payload) => ({ ...payload }),

  toleranceLabel: 'Tolerancia del error estimado',
  defaultTolerance: 0.0001,
  maxIterationsLabel: 'Máximo de refinamientos de h',
  defaultMaxIterations: 25,
  hidesIterationFields: (store) => store?.state.mode === MODES.TABLE,

  resultView: DifferentiationResult,
  resultSummary: null,
  iterationDetail: null,
  pdfReport: null,

  theoryPage: null,
  theorySections: {},
}
