// Contenido teórico de Newton: fórmulas en LaTeX, el ejemplo resuelto y los
// pasos del algoritmo. Se apoya en el fundamento común de la categoría
// (content.js, NonlinearFundamentalsSection) sin repetirlo.
//
// Las fórmulas de iteración y todo el paso a paso del ejemplo se generan con
// las mismas funciones que el detalle de Newton en Resolver
// (../newtonFormulas.js), así que la notación es idéntica en ambas vistas.
import { formatNumber } from '../../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR } from '../../../utils/latexFormulas'
import {
  determinantStepsLatex,
  errorLatex,
  evaluationLatex,
  functionSubstitutionLatex,
  functionsLatex,
  generalStepLatex,
  incrementLatex,
  jacobianLatex,
  linearSystemLatex,
  partialSteps,
  partialTitleLatex,
  updateLatex,
} from '../newtonFormulas'
// Respuesta real del backend (POST /api/solve/newton/) para el ejemplo
// «Clásico 2x2 (Chapra)», recortada a las tres primeras iteraciones: el
// desglose de cada derivada parcial, los términos de cada f_i y todos los
// valores intermedios de cada iteración.
import EXAMPLE from './newtonExample.json'

export { CURRENT_COLOR, PREVIOUS_COLOR, formatNumber }

export const tex = {
  // De dónde sale: forma escalar
  scalarNewton: 'x_{k+1} = x_k - \\frac{f(x_k)}{f\'(x_k)}',
  tangent: 'y = f(x_k) + f\'(x_k)\\,(x - x_k)',
  scalarAsFixedPoint: 'g(x) = x - \\frac{f(x)}{f\'(x)}',
  scalarDerivative: "g'(x) = \\frac{f(x)\\, f''(x)}{f'(x)^2} \\;\\Rightarrow\\; g'(p) = 0",
  fPrimeNonzero: "f'(p) \\neq 0",
  scalarEquation: 'x^2 - x - 2 = 0',
  scalarNewtonExample: 'g_N(x) = x - \\frac{x^2 - x - 2}{2x - 1}',
  scalarDerivativeAtRoot: "\\left| g_N'(2) \\right| = 0",
  scalarStart: 'x^{(0)} = 1.5',

  // Generalización a sistemas
  system: 'F(x) = 0',
  vectorMap: 'F : \\mathbb{R}^n \\to \\mathbb{R}^n',
  jacobianDefinition:
    'J(x) = \\begin{pmatrix} \\dfrac{\\partial f_1}{\\partial x_1} & \\cdots & \\dfrac{\\partial f_1}{\\partial x_n} \\\\ \\vdots & \\ddots & \\vdots \\\\ \\dfrac{\\partial f_n}{\\partial x_1} & \\cdots & \\dfrac{\\partial f_n}{\\partial x_n} \\end{pmatrix}, \\qquad J_{ij} = \\frac{\\partial f_i}{\\partial x_j}',
  inverseForm: 'x^{(k+1)} = x^{(k)} - J\\left(x^{(k)}\\right)^{-1} F\\left(x^{(k)}\\right)',
  practicalForm: generalStepLatex(),
  newtonG: 'G(x) = x - J(x)^{-1} F(x)',
  newtonJG: 'J_G(p) = 0',
  rhoZero: '\\rho\\left(J_G(p)\\right) = 0',
  xk: 'x^{(k)}',
  xNext: 'x^{(k+1)}',
  deltaX: '\\Delta x',
  J: 'J(x)',

  // Cramer
  linearSystem: 'J\\left(x^{(k)}\\right)\\, \\Delta x = -F\\left(x^{(k)}\\right)',
  determinant: 'D = \\det J\\left(x^{(k)}\\right)',
  columnDeterminant: 'D_i = \\det J_i',
  increment: '\\Delta x_i = \\frac{D_i}{D}, \\qquad i = 1, \\dots, n',
  nonSingular: 'D \\neq 0',
  Ji: 'J_i',
  minusF: '-F\\left(x^{(k)}\\right)',

  // Convergencia
  quadratic:
    '\\left\\| x^{(k+1)} - p \\right\\|_\\infty \\leq C \\left\\| x^{(k)} - p \\right\\|_\\infty^{2}',
  linear: '\\left\\| x^{(k+1)} - p \\right\\|_\\infty \\leq K \\left\\| x^{(k)} - p \\right\\|_\\infty',
  jacobianAtRoot: 'J(p)',
  p: 'p',
  K: 'K',
  eps: '\\varepsilon',
  // Igual que el bloque «Error de la iteración» del detalle en Resolver.
  error: '\\text{error} = \\max_{i} \\left| \\Delta x_i \\right|',

  // Ejemplo
  exampleSystem: '\\begin{cases} x^{2} + x y - 10 = 0 \\\\ y + 3 x y^{2} - 57 = 0 \\end{cases}',
  exampleStart: 'x^{(0)} = (1.5,\\ 3.5)',
  exampleSolution: 'p = (2,\\ 3)',
  exampleF: functionsLatex(EXAMPLE),
  exampleJ: jacobianLatex(EXAMPLE),
}

// Newton aplicado a la ecuación escalar del fundamento común (x² − x − 2 = 0,
// raíz 2), desde x⁽⁰⁾ = 1.5. Calculado y verificado con Python.
export const scalarNewtonIterates = [2.125, 2.004808, 2.0000077, '2.00000000002']

/* Derivación de la Jacobiana del ejemplo, entrada por entrada (la misma que
   muestra Resolver una sola vez antes de la tabla de iteraciones). */
export const exampleEntries = EXAMPLE.equations.flatMap((_, i) =>
  EXAMPLE.variables.map((_, j) => ({
    key: `${i}-${j}`,
    title: partialTitleLatex(EXAMPLE, i, j),
    ...partialSteps(EXAMPLE, i, j),
  }))
)

const variableLatex = (j) => EXAMPLE.variables_latex[j]
const SUPERSCRIPT = '⁰¹²³⁴⁵⁶⁷⁸⁹'
// "x⁽⁰⁾" para los títulos en texto (fuera de LaTeX).
const pointName = (k) => `x⁽${String(k).replace(/\d/g, (d) => SUPERSCRIPT[d])}⁾`
const indices = EXAMPLE.variables.map((_, j) => j)

/* Tres iteraciones completas, con los mismos sub-pasos y en el mismo orden
   que el detalle de cada iteración en Resolver. */
export const workedSteps = EXAMPLE.iterations.map((row) => {
  const evaluation = evaluationLatex(row)
  return {
    iteration: row.iteration,
    x: row.x,
    groups: [
      {
        title: `Evaluación en ${pointName(row.iteration - 1)}: sustitución en cada fᵢ, y F y J evaluados`,
        formulas: [
          ...EXAMPLE.equations.map((_, i) => functionSubstitutionLatex(EXAMPLE, row, i)),
          evaluation.F,
          evaluation.J,
        ],
      },
      {
        title: 'Sistema lineal planteado y determinante de la Jacobiana',
        formulas: [
          linearSystemLatex(EXAMPLE, row),
          determinantStepsLatex('D', row.extra.J, row.extra.D),
        ],
      },
      {
        title: 'Determinantes por variable (columna reemplazada por −F, en verde)',
        formulas: indices.map((j) =>
          determinantStepsLatex(`D_{${variableLatex(j)}}`, row.extra.matrices[j], row.extra.D_i[j], j)
        ),
      },
      {
        title: 'Incrementos y actualización',
        formulas: [
          ...indices.map((j) => incrementLatex(EXAMPLE, row, j)),
          ...indices.map((j) => updateLatex(EXAMPLE, row, j)),
        ],
      },
      { title: 'Error de la iteración', formulas: [errorLatex(EXAMPLE, row)] },
    ],
  }
})

/* Convergencia del ejemplo hasta llegar a la solución exacta (2, 3). Valores
   del backend; "cifras correctas" = −log10 de la distancia a la solución. */
export const convergenceRows = [
  { iteration: 1, x: 2.0360288230584467, y: 2.843875100080064, distance: '0.156125', digits: '≈ 1' },
  { iteration: 2, x: 1.9987006090558244, y: 3.002288562924508, distance: '0.002289', digits: '≈ 3' },
  { iteration: 3, x: 1.99999998387626, y: 2.999999413388913, distance: '5.87 \\times 10^{-7}', digits: '≈ 6' },
  { iteration: 4, x: 1.99999999999998, y: 3.000000000000075, distance: '7.51 \\times 10^{-14}', digits: '≈ 13' },
]

// El mismo sistema algebraico en ambos métodos (ejemplo «Algebraico 2x2» de
// Resolver), distancia a la solución tras 4 iteraciones. Verificado.
export const ALGEBRAIC_AFTER_4 = { fixedPoint: '1.5 \\times 10^{-5}', newton: '5.9 \\times 10^{-14}' }

/* Pasos del algoritmo como datos (mismo formato que los de los otros tres
   métodos): cada descripción mezcla texto y fórmulas { m }. */
export const ALGORITHM_STEPS = {
  newton: [
    {
      title: 'Definir F(x) y derivar J(x)',
      body: [
        'Se escribe el sistema como ',
        { m: tex.system },
        ' y se calcula una sola vez la matriz Jacobiana ',
        { m: 'J_{ij} = \\partial f_i / \\partial x_j' },
        ', derivando cada ',
        { m: 'f_i' },
        ' término a término.',
      ],
    },
    {
      title: 'Vector inicial',
      body: [
        'Se parte de una aproximación inicial ',
        { m: 'x^{(0)}' },
        ' (por defecto, ceros), cercana a la solución buscada, y se fija una tolerancia ',
        { m: tex.eps },
        '.',
      ],
    },
    {
      title: 'Evaluar F y J en el punto actual',
      body: [
        'Se sustituye ',
        { m: tex.xk },
        ' en cada ',
        { m: 'f_i' },
        ' y en cada entrada de la Jacobiana: se obtienen el vector ',
        { m: 'F\\left(x^{(k)}\\right)' },
        ' y la matriz ',
        { m: 'J\\left(x^{(k)}\\right)' },
        '.',
      ],
    },
    {
      title: 'Resolver J·Δx = −F por la regla de Cramer',
      body: [
        'Se calculan ',
        { m: 'D = \\det J' },
        ' y cada ',
        { m: 'D_i' },
        ' (con la columna ',
        { m: 'i' },
        ' reemplazada por ',
        { m: '-F' },
        '), y ',
        { m: '\\Delta x_i = D_i / D' },
        '. Si ',
        { m: 'D = 0' },
        ', el método no puede continuar.',
      ],
    },
    {
      title: 'Actualizar el punto',
      body: ['Se suma el incremento: ', { m: 'x^{(k+1)} = x^{(k)} + \\Delta x' }, '.'],
    },
    {
      title: 'Medir el error',
      body: ['Se toma la norma infinito del incremento: ', { m: tex.error }, '.'],
    },
    {
      title: 'Criterio de parada',
      body: [
        'El proceso se detiene cuando el error es menor que ',
        { m: tex.eps },
        ' y se han ejecutado al menos 6 iteraciones, al alcanzar el número máximo de iteraciones, o si la Jacobiana resulta singular o algún valor deja de ser un número real finito.',
      ],
    },
  ],
}
