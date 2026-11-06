// Interfaz de la categoría "differentiation" (diferencias finitas y fórmula
// de 3 puntos).
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
// Los métodos con entrada en THEORY_SECTIONS aparecen en "Teoría ▾".
import DifferentiationConfigFields from './DifferentiationConfigFields.vue'
import DifferentiationInput from './DifferentiationInput.vue'
import DifferentiationResult from './DifferentiationResult.vue'
import { MODES, createDifferentiationStore, createThreePointStore } from './store'
import DifferentiationTheoryPage, { THEORY_SECTIONS } from './theory/DifferentiationTheoryPage.vue'

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

  theoryPage: DifferentiationTheoryPage,
  theorySections: THEORY_SECTIONS,

  // Lo que cambia por método (sobrescribe la base). La fórmula de 3 puntos
  // usa la misma vista; sólo cambian el selector, el mínimo de puntos y la
  // tolerancia por defecto (converge rápido).
  methods: {
    'tres-puntos': {
      createStore: createThreePointStore,
      defaultTolerance: 0.000001,
    },
  },
}
