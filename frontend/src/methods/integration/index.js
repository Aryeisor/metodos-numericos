// Interfaz de la categoría "integration" (método del trapecio; después
// Simpson, Romberg y cuadratura gaussiana).
// Cumple el contrato documentado en methods/linear/index.js, con los mismos
// campos opcionales que diferenciación (resultView, toleranceLabel,
// defaultTolerance, maxIterationsLabel, defaultMaxIterations,
// hidesIterationFields).
//
// El formulario de dos modos es el de diferenciación (components/FunctionTableInput.vue);
// la regla de integración es un dato del resultado (result.rule).
//
// Los métodos con entrada en THEORY_SECTIONS aparecen en "Teoría ▾".
import FunctionTableInput from '../../components/FunctionTableInput.vue'
import IntegrationConfigFields from './IntegrationConfigFields.vue'
import IntegrationResult from './IntegrationResult.vue'
import SimpsonConfigFields from './SimpsonConfigFields.vue'
import RombergResult from './RombergResult.vue'
import SimpsonResult from './SimpsonResult.vue'
import { MODES, createIntegrationStore, createRombergStore, createSimpsonStore } from './store'
import IntegrationTheoryPage, { THEORY_SECTIONS } from './theory/IntegrationTheoryPage.vue'

export default {
  createStore: createIntegrationStore,

  configTitle: 'Configuración del método',
  formTitle: 'Datos',
  configFields: IntegrationConfigFields,
  configExtras: null,

  form: FunctionTableInput,
  formBindings: (store) => ({ store }),

  invalidMessage: 'Hay campos con un valor inválido (marcados en rojo). Corrígelos antes de resolver.',

  solvedSystem: (payload) => ({ ...payload }),

  toleranceLabel: 'Tolerancia del error estimado',
  defaultTolerance: 0.000001,
  maxIterationsLabel: 'Máximo de refinamientos (de 6 a 22)',
  defaultMaxIterations: 20,
  hidesIterationFields: (store) => store?.state.mode === MODES.TABLE,

  resultView: IntegrationResult,
  resultSummary: null,
  iterationDetail: null,
  pdfReport: null,

  theoryPage: IntegrationTheoryPage,
  theorySections: THEORY_SECTIONS,

  // Lo que cambia por método (sobrescribe la base). Simpson: la regla y un n₀
  // por regla en la configuración, y su propia vista del resultado.
  methods: {
    simpson: {
      createStore: createSimpsonStore,
      configFields: SimpsonConfigFields,
      resultView: SimpsonResult,
    },
    // Romberg: sin n₀ (siempre empieza con n = 1) y con máximo de filas.
    romberg: {
      createStore: createRombergStore,
      configFields: null,
      maxIterationsLabel: 'Máximo de filas (de 6 a 20)',
      defaultMaxIterations: 15,
      resultView: RombergResult,
    },
  },
}
