// Interfaz de la categoría "linear_system" (Jacobi, Gauss-Seidel).
//
// Contrato que SolverView y ResultsTable esperan de cada categoría:
//   createStore()                 estado del formulario + mutaciones
//   configTitle / formTitle       títulos de las tarjetas del formulario; los pone
//                                 cada categoría (ej. no lineales: "Sistema de
//                                 ecuaciones f(x) = 0"; polinomios: "Coeficientes
//                                 del polinomio")
//   configFields                  componente dentro de la cuadrícula de configuración
//   configExtras                  componente debajo de la cuadrícula
//   form + formBindings(store)    componente de entrada y sus props/eventos
//   invalidMessage                error cuando la entrada tiene valores inválidos
//   solvedSystem(payload, resp)   datos de entrada tal como se resolvieron
//   resultSummary                 bloque extra en el resumen del resultado
//   iterationDetail               detalle expandible de cada iteración
//   pdfReport({result, system})   partes del PDF propias de la categoría
//   theoryPage                    página de teoría; recibe el prop `method`
//   theorySections                métodos con teoría escrita: { slug: sección }.
//                                 Un método sin entrada aquí no aparece en "Teoría ▾"
//
// Opcionales (si faltan, todo funciona como en esta categoría):
//   methods[slug]                 lo que cambia para un método concreto (ej. Newton)
//   beforeIterations              sección fija entre el gráfico y la tabla de iteraciones
//   resultView                    vista completa del resultado en lugar de ResultsTable
//                                 (recibe result, system y methodName; exporta su PDF)
//   toleranceLabel                texto del campo de tolerancia
//   defaultTolerance              tolerancia por defecto al entrar en la categoría
//   maxIterationsLabel            texto del campo de máximo de iteraciones
import MatrixInput from '../../components/MatrixInput.vue'
import LinearConfigExtras from './LinearConfigExtras.vue'
import LinearConfigFields from './LinearConfigFields.vue'
import LinearIterationDetail from './LinearIterationDetail.vue'
import LinearResultSummary from './LinearResultSummary.vue'
import { linearPdfReport } from './pdf'
import { createLinearSystemStore } from './store'
import LinearTheoryPage, { THEORY_SECTIONS } from './theory/LinearTheoryPage.vue'

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

  theoryPage: LinearTheoryPage,
  theorySections: THEORY_SECTIONS,
}
