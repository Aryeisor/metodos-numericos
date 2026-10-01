// Interfaz de la categoría "linear_system" (Jacobi, Gauss-Seidel).
//
// Contrato que SolverView y ResultsTable esperan de cada categoría:
//   createStore()                 estado del formulario + mutaciones
//   configTitle / formTitle       títulos de las tarjetas del formulario
//   configFields                  componente dentro de la cuadrícula de configuración
//   configExtras                  componente debajo de la cuadrícula
//   form + formBindings(store)    componente de entrada y sus props/eventos
//   invalidMessage                error cuando la entrada tiene valores inválidos
//   solvedSystem(payload, resp)   datos de entrada tal como se resolvieron
//   resultSummary                 bloque extra en el resumen del resultado
//   iterationDetail               detalle expandible de cada iteración
//   pdfReport({result, system})   partes del PDF propias de la categoría
//   theoryAnchor(slug)            ancla de la sección de teoría del método
import MatrixInput from '../../components/MatrixInput.vue'
import LinearConfigExtras from './LinearConfigExtras.vue'
import LinearConfigFields from './LinearConfigFields.vue'
import LinearIterationDetail from './LinearIterationDetail.vue'
import LinearResultSummary from './LinearResultSummary.vue'
import { linearPdfReport } from './pdf'
import { createLinearSystemStore } from './store'

export default {
  createStore: createLinearSystemStore,

  configTitle: 'Configuración del sistema',
  formTitle: 'Sistema A·x = b',
  configFields: LinearConfigFields,
  configExtras: LinearConfigExtras,

  form: MatrixInput,
  formBindings: ({ state }) => ({
    n: state.n,
    a: state.A,
    b: state.b,
    x0: state.x0,
    'onUpdate:a': (value) => (state.A = value),
    'onUpdate:b': (value) => (state.b = value),
    'onUpdate:x0': (value) => (state.x0 = value),
  }),

  invalidMessage:
    'Hay campos del sistema con un valor inválido (marcados en rojo). Corrígelos antes de resolver.',

  // El backend puede haber reordenado las filas: se usa el sistema tal como
  // realmente se calculó para que el paso a paso coincida con las iteraciones.
  solvedSystem: (payload, response) => ({ ...payload, A: response.A, b: response.b }),

  resultSummary: LinearResultSummary,
  iterationDetail: LinearIterationDetail,
  pdfReport: linearPdfReport,

  theoryAnchor: (slug) => `metodo-${slug}`,
}
