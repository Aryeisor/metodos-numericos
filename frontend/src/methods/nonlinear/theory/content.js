// Contenido teórico de la categoría "ecuaciones no lineales": fórmulas en
// LaTeX, el ejemplo resuelto y los pasos del algoritmo.
//
// La fórmula de iteración y las sustituciones del ejemplo se generan con las
// mismas funciones que el paso a paso de Resolver (../formulas.js), así que la
// notación es idéntica en ambas vistas.
import { formatNumber } from '../../../utils/iterationSteps'
import {
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  colorize,
  errorFormulaLatex,
} from '../../../utils/latexFormulas'
import { generalFormulaLatex, substitutionLatex } from '../formulas'

export { CURRENT_COLOR, PREVIOUS_COLOR, formatNumber }

export const tex = {
  // Fundamento común
  system:
    '\\begin{cases} f_1(x_1, x_2, \\dots, x_n) = 0 \\\\ f_2(x_1, x_2, \\dots, x_n) = 0 \\\\ \\quad\\vdots \\\\ f_n(x_1, x_2, \\dots, x_n) = 0 \\end{cases}',
  vectorForm: 'F(x) = 0',
  vectorMap: 'F : \\mathbb{R}^n \\to \\mathbb{R}^n',
  linearForm: 'A \\cdot x = b',
  x0: 'x^{(0)}',
  sequence: 'x^{(1)},\\ x^{(2)},\\ \\dots',
  nMin: 'n \\geq 2',
  fixedPointForm: 'x = G(x)',
  fixedPointComponents: 'x_i = g_i(x_1, \\dots, x_n), \\qquad i = 1, \\dots, n',
  fixedPoint: 'p = G(p) \\iff F(p) = 0',
  p: 'p',
  G: 'G',
  gi: 'g_i',
  fi: 'f_i',
  xi: 'x_i',
  iterationScheme: 'x^{(k+1)} = G\\left(x^{(k)}\\right)',
  contraction:
    '\\left\\| G(x) - G(y) \\right\\|_\\infty \\leq K \\left\\| x - y \\right\\|_\\infty, \\qquad 0 \\leq K < 1',
  K: 'K',
  D: 'D',
  GofD: 'G(D) \\subseteq D',
  errorBound:
    '\\left\\| x^{(k)} - p \\right\\|_\\infty \\leq \\frac{K^{k}}{1 - K} \\left\\| x^{(1)} - x^{(0)} \\right\\|_\\infty',
  jacobian:
    'J_G(x) = \\begin{pmatrix} \\dfrac{\\partial g_1}{\\partial x_1} & \\cdots & \\dfrac{\\partial g_1}{\\partial x_n} \\\\ \\vdots & \\ddots & \\vdots \\\\ \\dfrac{\\partial g_n}{\\partial x_1} & \\cdots & \\dfrac{\\partial g_n}{\\partial x_n} \\end{pmatrix}',
  jacobianNorm:
    '\\left\\| J_G(x) \\right\\|_\\infty = \\max_{i} \\sum_{j=1}^{n} \\left| \\frac{\\partial g_i}{\\partial x_j}(x) \\right| \\leq K < 1',
  localRadius: '\\rho\\left(J_G(p)\\right) < 1',
  linearCase: 'G(x) = T\\,x + c \\;\\Rightarrow\\; J_G(x) = T',
  rhoT: '\\rho(T) < 1',

  // Ilustración escalar: una ecuación, tres despejes
  scalarEquation: 'x^2 - x - 2 = 0',
  scalarRoot: 'p = 2',
  scalarStart: 'x^{(0)} = 1.5',
  gA: 'g_a(x) = x^2 - 2',
  gB: 'g_b(x) = \\sqrt{x + 2}',
  gC: 'g_c(x) = 1 + \\frac{2}{x}',
  derivative: "\\left| g'(2) \\right|",

  // Sección de Punto Fijo
  sequential: generalFormulaLatex(),
  simultaneous: `x_i^{(k+1)} = g_i\\left(${colorize('x_1^{(k)}, \\ldots, x_n^{(k)}', PREVIOUS_COLOR)}\\right)`,
  before: 'x_1^{(k+1)}, \\dots, x_{i-1}^{(k+1)}',
  after: 'x_{i+1}^{(k)}, \\dots, x_n^{(k)}',
  xNext: 'x^{(k+1)}',
  xCurrent: 'x^{(k)}',
  xiNext: 'x_i^{(k+1)}',
  iRange: 'i = 1, \\dots, n',
  kRange: 'k = 0, 1, 2, \\dots',
  jBefore: 'j < i',
  eps: '\\varepsilon',
  error: errorFormulaLatex(),
  simultaneousMatrix: 'T_{\\text{sim}} = J_G(p)',
  sequentialMatrix: 'T_{\\text{sec}} = (I - L)^{-1}\\, U',
  splitting: 'J_G(p) = L + U',

  // Ejemplo resuelto (mismo sistema que el ejemplo «Algebraico 2x2» de Resolver)
  exampleSystem: '\\begin{cases} 3x - y^{2} - 1 = 0 \\\\ x^{2} + 4y - 2 = 0 \\end{cases}',
  exampleG: '\\begin{cases} x = g_1(y) = \\dfrac{1}{3} + \\dfrac{y^{2}}{3} \\\\[6pt] y = g_2(x) = \\dfrac{1}{2} - \\dfrac{x^{2}}{4} \\end{cases}',
  exampleStart: 'x^{(0)} = (0,\\ 0)',
  exampleJacobian: 'J_G(x, y) = \\begin{pmatrix} 0 & \\dfrac{2y}{3} \\\\[6pt] -\\dfrac{x}{2} & 0 \\end{pmatrix}',
  exampleSolution: 'p \\approx (0.403642,\\ 0.459268)',
  exampleJacobianNorm: '\\left\\| J_G(p) \\right\\|_\\infty \\approx 0.306179 < 1',
  rhoSimultaneous: '\\rho(T_{\\text{sim}}) \\approx 0.248583',
  rhoSequential: '\\rho(T_{\\text{sec}}) \\approx 0.061793',
}

/* Ejemplo trabajado. Los datos son la respuesta real del backend para el
   ejemplo «Algebraico 2x2» (POST /api/solve/punto-fijo/), recortada a las
   tres primeras iteraciones: el despeje g_i, su plantilla de sustitución y
   los valores con los que se evaluó cada g_i. Las sustituciones se generan
   con la misma función que el detalle de iteración de Resolver. */
const EXAMPLE_RESULT = {
  variables: ['x', 'y'],
  variables_latex: ['x', 'y'],
  equations: [
    { g_template: '\\frac{1}{3} + \\frac{@@1@@^{2}}{3}', dependencies: [1] },
    { g_template: '\\frac{1}{2} - \\frac{@@0@@^{2}}{4}', dependencies: [0] },
  ],
  iterations: [
    {
      iteration: 1,
      x: [0.3333333333333333, 0.4722222222222222],
      error: 0.4722222222222222,
      extra: { inputs: [[0], [0.3333333333333333]] },
    },
    {
      iteration: 2,
      x: [0.4076646090534979, 0.4584523916313147],
      error: 0.07433127572016457,
      extra: { inputs: [[0.4722222222222222], [0.4076646090534979]] },
    },
    {
      iteration: 3,
      x: [0.40339286513082406, 0.4593185490903862],
      error: 0.004271743922673821,
      extra: { inputs: [[0.4584523916313147], [0.40339286513082406]] },
    },
  ],
}

export const workedSteps = EXAMPLE_RESULT.iterations.map((row, index) => ({
  iteration: row.iteration,
  x: row.x,
  error: row.error,
  substitutions: EXAMPLE_RESULT.variables.map((_, i) => substitutionLatex(EXAMPLE_RESULT, index, i)),
}))

// Mismo sistema con el esquema simultáneo (ambas componentes con los valores
// de la iteración anterior). Calculado con las mismas g_i y verificado: con
// tolerancia 10⁻⁶ necesita 11 iteraciones, frente a 7 del secuencial.
const SIMULTANEOUS_ITERATIONS = [
  [0.3333333333333333, 0.5],
  [0.41666666666666663, 0.4722222222222222],
  [0.40766460905349794, 0.4565972222222222],
]

export const ITERATIONS_TO_CONVERGE = { sequential: 7, simultaneous: 11 }

// Filas de la tabla comparativa: las dos trayectorias intercaladas por iteración.
export const comparisonRows = workedSteps.flatMap((step, i) => [
  { key: `sec${i}`, iteration: step.iteration, scheme: 'Secuencial', x: step.x, first: true },
  { key: `sim${i}`, iteration: step.iteration, scheme: 'Simultáneo', x: SIMULTANEOUS_ITERATIONS[i] },
])

// Ilustración escalar: los primeros iterados de cada despeje desde x⁽⁰⁾ = 1.5.
export const scalarRows = [
  { g: tex.gA, derivative: '4', iterates: [0.25, -1.9375, 1.753906, 1.076187], verdict: 'Diverge' },
  { g: tex.gB, derivative: '\\tfrac{1}{4}', iterates: [1.870829, 1.967442, 1.991844, 1.99796], verdict: 'Converge rápido' },
  { g: tex.gC, derivative: '\\tfrac{1}{2}', iterates: [2.333333, 1.857143, 2.076923, 1.962963], verdict: 'Converge, oscilando y más lento' },
]

/* Pasos del algoritmo como datos (mismo formato que los de Jacobi y
   Gauss-Seidel): cada descripción mezcla texto y fórmulas { m }. */
export const ALGORITHM_STEPS = {
  'punto-fijo': [
    {
      title: 'Reescribir cada ecuación',
      body: [
        'La ecuación ',
        { m: 'f_i(x) = 0' },
        ' se despeja para su propia variable, obteniendo ',
        { m: 'x_i = g_i(x)' },
        '. La aplicación lo hace automáticamente y exige que el despeje sea único y real.',
      ],
    },
    {
      title: 'Vector inicial',
      body: [
        'Se parte de una aproximación inicial ',
        { m: tex.x0 },
        ' (por defecto, ceros), lo más cercana posible a la solución, y se fija una tolerancia ',
        { m: tex.eps },
        '.',
      ],
    },
    {
      title: 'Calcular la nueva iteración de forma secuencial',
      body: [
        'Se recorre ',
        { m: tex.iRange },
        ' evaluando ',
        { m: tex.xiNext },
        ' con ',
        { m: tex.gi },
        '; para ',
        { m: tex.jBefore },
        ' ya se usan los valores recalculados en esa misma iteración.',
      ],
    },
    {
      title: 'Medir el error',
      body: [
        'Se calcula la norma infinito entre dos iteraciones sucesivas: ',
        { m: tex.error },
        '.',
      ],
    },
    {
      title: 'Criterio de parada',
      body: [
        'El proceso se detiene cuando el error es menor que ',
        { m: tex.eps },
        ' y se han ejecutado al menos 6 iteraciones, al alcanzar el número máximo de iteraciones, o si algún ',
        { m: tex.xiNext },
        ' deja de ser un número real finito.',
      ],
    },
  ],
}

export function vectorLatex(name, x) {
  const values = x.map((value) => formatNumber(value)).join(',\\ ')
  return `${name ? `${name} = ` : ''}(${values})`
}
