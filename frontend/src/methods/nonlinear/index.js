// Interfaz de la categoría "nonlinear_system" (Punto Fijo, Newton).
// Cumple el contrato documentado en methods/linear/index.js.
//
// Los métodos de esta categoría no comparten formulario: Punto Fijo asocia
// cada ecuación a la variable que se despeja de ella, y Newton declara las
// variables aparte y muestra otro paso a paso. Lo común es la base; lo propio
// de cada método va en `methods[slug]` y methods/registry.js lo combina.
//
// Los métodos con entrada en THEORY_SECTIONS aparecen en "Teoría ▾"; uno que
// no la tenga aparece sólo en "Resolver ▾".
import NewtonIterationDetail from './NewtonIterationDetail.vue'
import NewtonJacobianSection from './NewtonJacobianSection.vue'
import NewtonSystemInput from './NewtonSystemInput.vue'
import NonlinearIterationDetail from './NonlinearIterationDetail.vue'
import NonlinearResultSummary from './NonlinearResultSummary.vue'
import NonlinearSystemInput from './NonlinearSystemInput.vue'
import { newtonPdfReport } from './newtonPdf'
import { createNewtonStore } from './newtonStore'
import { nonlinearPdfReport } from './pdf'
import { createNonlinearSystemStore } from './store'
import NonlinearTheoryPage, { THEORY_SECTIONS } from './theory/NonlinearTheoryPage.vue'

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

  theoryPage: NonlinearTheoryPage,
  theorySections: THEORY_SECTIONS,

  // Lo que cambia por método (sobrescribe la base).
  methods: {
    newton: {
      createStore: createNewtonStore,
      form: NewtonSystemInput,
      // El sistema y la Jacobiana (con su derivación) no cambian entre
      // iteraciones: van una sola vez antes de la tabla, no en el resumen.
      resultSummary: null,
      beforeIterations: NewtonJacobianSection,
      iterationDetail: NewtonIterationDetail,
      pdfReport: newtonPdfReport,
    },
  },
}
