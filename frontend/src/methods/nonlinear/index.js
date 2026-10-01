// Interfaz de la categoría "nonlinear_system" (Punto Fijo).
// Cumple el contrato documentado en methods/linear/index.js.
//
// Sin teoría escrita todavía: `theorySections` vacío hace que los métodos de
// esta categoría aparezcan en "Resolver ▾" pero no en "Teoría ▾".
import NonlinearIterationDetail from './NonlinearIterationDetail.vue'
import NonlinearResultSummary from './NonlinearResultSummary.vue'
import NonlinearSystemInput from './NonlinearSystemInput.vue'
import { nonlinearPdfReport } from './pdf'
import { createNonlinearSystemStore } from './store'

export default {
  createStore: createNonlinearSystemStore,

  configTitle: 'Configuración del sistema',
  formTitle: 'Sistema de ecuaciones f(x) = 0',
  // El número de ecuaciones se controla en el propio formulario (agregar/quitar).
  configFields: null,
  configExtras: null,

  form: NonlinearSystemInput,
  formBindings: (store) => ({ store }),

  invalidMessage:
    'El punto inicial x0 tiene un valor inválido (marcado en rojo). Corrígelo antes de resolver.',

  // x0 tal como se usó (el backend pone ceros si no se envió).
  solvedSystem: (payload, response) => ({ ...payload, x0: response.x0 }),

  resultSummary: NonlinearResultSummary,
  iterationDetail: NonlinearIterationDetail,
  pdfReport: nonlinearPdfReport,

  theoryPage: null,
  theorySections: {},
}
