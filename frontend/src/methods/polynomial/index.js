// Interfaz de la categoría "polynomial" (Bairstow).
// Cumple el contrato documentado en methods/linear/index.js, con los campos
// opcionales que necesita un resultado de varios factores:
//   resultView     vista completa del resultado (factores, gráficos y PDF)
//   toleranceLabel / defaultTolerance / maxIterationsLabel
//                  la tolerancia de Bairstow es un error relativo en %, y el
//                  máximo de iteraciones es por factor.
//
// Los métodos con entrada en THEORY_SECTIONS aparecen en "Teoría ▾".
import PolynomialInput from './PolynomialInput.vue'
import PolynomialResult from './PolynomialResult.vue'
import { createPolynomialStore } from './store'
import PolynomialTheoryPage, { THEORY_SECTIONS } from './theory/PolynomialTheoryPage.vue'

export default {
  createStore: createPolynomialStore,

  configTitle: 'Configuración del método',
  formTitle: 'Polinomio f(x)',
  configFields: null,
  configExtras: null,

  form: PolynomialInput,
  formBindings: (store) => ({ store }),

  invalidMessage:
    'Hay coeficientes o valores iniciales con un valor inválido (marcados en rojo). Corrígelos antes de resolver.',

  solvedSystem: (payload) => ({ ...payload }),

  toleranceLabel: 'Tolerancia εs (%)',
  defaultTolerance: 0.0001,
  maxIterationsLabel: 'Máximo de iteraciones por factor (mínimo real: 6)',

  resultView: PolynomialResult,
  resultSummary: null,
  iterationDetail: null,
  pdfReport: null,

  theoryPage: PolynomialTheoryPage,
  theorySections: THEORY_SECTIONS,
}
