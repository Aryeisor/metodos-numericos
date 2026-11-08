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
// Sin teoría todavía: theorySections vacío, así que el método no aparece en
// "Teoría ▾" (igual que se hizo con los métodos nuevos antes de su página).
import FunctionTableInput from '../../components/FunctionTableInput.vue'
import IntegrationConfigFields from './IntegrationConfigFields.vue'
import IntegrationResult from './IntegrationResult.vue'
import { MODES, createIntegrationStore } from './store'

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

  theoryPage: null,
  theorySections: {},
}
