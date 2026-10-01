// Contenido teórico compartido por las páginas de Jacobi y Gauss-Seidel:
// fórmulas en LaTeX, el ejemplo resuelto y los pasos del algoritmo.
import { buildIterationDetail, formatNumber } from '../../../utils/iterationSteps'
import {
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  errorFormulaLatex,
  generalFormulaLatex,
  substitutionLatex,
} from '../../../utils/latexFormulas'

export { CURRENT_COLOR, PREVIOUS_COLOR, formatNumber }

// Las fórmulas de iteración y de error vienen de las mismas funciones que usa
// el paso a paso de Resolver, para que ambas vistas compartan la notación exacta.
export const tex = {
  system: 'A \\cdot x = b',
  nByN: 'n \\times n',
  nMin: 'n \\geq 3',
  x0: 'x^{(0)}',
  sequence: 'x^{(1)},\\ x^{(2)},\\ \\dots',
  aii: 'a_{ii}',
  xi: 'x_i',
  dominance: '\\left| a_{ii} \\right| > \\sum_{j \\neq i} \\left| a_{ij} \\right|',
  decomposition: 'A = D + R',
  jacobi: `${generalFormulaLatex('jacobi')}, \\qquad i = 1, \\dots, n`,
  gaussSeidel: generalFormulaLatex('gauss-seidel'),
  error: errorFormulaLatex(),
  xNext: 'x^{(k+1)}',
  xCurrent: 'x^{(k)}',
  xiNext: 'x_i^{(k+1)}',
  kRange: 'k = 1, 2, \\dots',
  iRange: 'i = 1, \\dots, n',
  before: 'x_1, \\dots, x_{i-1}',
  after: 'x_{i+1}, \\dots, x_n',
  jBefore: 'j < i',
  eps: '\\varepsilon',

  // Radio espectral
  recurrence: 'x^{(k+1)} = T\\, x^{(k)} + c',
  splitting: 'A = D + L + U',
  jacobiMatrix: 'T_J = -D^{-1} (L + U)',
  gaussSeidelMatrix: 'T_{GS} = -(D + L)^{-1} U',
  spectralRadius: '\\rho(T) = \\max_i \\left| \\lambda_i \\right| < 1',
  rho: '\\rho(T)',
  exampleSize: '3 \\times 3',
  rhoJacobi: '\\rho(T_J) = 0.3',
  rhoGaussSeidel: '\\rho(T_{GS}) \\approx 0.089443',

  // Ejemplo resuelto
  exampleSystem:
    '\\begin{cases} 10x_1 + 2x_2 + x_3 = 17 \\\\ x_1 + 10x_2 + 2x_3 = 27 \\\\ 2x_1 + x_2 + 10x_3 = 34 \\end{cases}',
  exampleSolution: 'x = (1,\\ 2,\\ 3)',
  exampleStart: 'x^{(0)} = (0,\\ 0,\\ 0)',
}

/* Ejemplo trabajado a mano. Los vectores de cada iteración son datos ya
   verificados contra los solvers del backend; las sustituciones numéricas se
   generan con las mismas utilidades que el paso a paso de Resolver, así que
   la notación y la aritmética mostrada son idénticas en toda la app. */
const EXAMPLE = {
  A: [
    [10, 2, 1],
    [1, 10, 2],
    [2, 1, 10],
  ],
  b: [17, 27, 34],
  x0: [0, 0, 0],
}

const EXAMPLE_ITERATIONS = {
  jacobi: [
    [1.7, 2.7, 3.4],
    [0.82, 1.85, 2.79],
    [1.051, 2.06, 3.0509999999999997],
  ],
  'gauss-seidel': [
    [1.7, 2.5300000000000002, 2.807],
    [0.9132999999999999, 2.04727, 3.012613],
    [0.9892847, 1.9985489300000001, 3.002288167],
  ],
}

function workedSteps(method) {
  const iterations = EXAMPLE_ITERATIONS[method].map((x, i) => ({
    iteration: i + 1,
    x,
    error: null,
  }))

  return iterations.map((row, index) => {
    const detail = buildIterationDetail({ ...EXAMPLE, method, iterations, index })
    return {
      iteration: row.iteration,
      x: row.x,
      substitutions: detail.variables.map((variable) => substitutionLatex(variable, row.iteration)),
    }
  })
}

export const jacobiSteps = workedSteps('jacobi')
export const gaussSeidelSteps = workedSteps('gauss-seidel')

/* Pasos del algoritmo como datos: cada descripción es una lista de fragmentos
   donde las cadenas son texto y los objetos { m } son fórmulas que se
   renderizan con MathFormula en línea. Así los dos métodos comparten los tres
   pasos que son idénticos y sólo cambia el segundo. */
const STEP_START = {
  title: 'Vector inicial',
  body: [
    'Se parte de una aproximación inicial ',
    { m: tex.x0 },
    ' (por defecto, ceros) y se fija una tolerancia ',
    { m: tex.eps },
    '.',
  ],
}

const STEP_ERROR = {
  title: 'Medir el error',
  body: [
    'Se calcula la norma infinito entre dos iteraciones sucesivas: ',
    { m: tex.error },
    '.',
  ],
}

const STEP_STOP = {
  title: 'Criterio de parada',
  body: [
    'El proceso se detiene cuando el error es menor que ',
    { m: tex.eps },
    ' y se han ejecutado al menos 6 iteraciones, o al alcanzar el número máximo de iteraciones configurado.',
  ],
}

export const ALGORITHM_STEPS = {
  jacobi: [
    STEP_START,
    {
      title: 'Calcular la nueva iteración',
      body: [
        'En cada iteración ',
        { m: tex.kRange },
        ' se calcula ',
        { m: tex.xiNext },
        ' para todo ',
        { m: 'i' },
        ' con la fórmula anterior, usando únicamente los valores de ',
        { m: tex.xCurrent },
        '.',
      ],
    },
    STEP_ERROR,
    STEP_STOP,
  ],
  'gauss-seidel': [
    STEP_START,
    {
      title: 'Actualizar componente a componente',
      body: [
        'En cada iteración se recorre ',
        { m: tex.iRange },
        ' actualizando ',
        { m: tex.xi },
        ' in situ, de modo que para ',
        { m: tex.jBefore },
        ' ya se usan los valores recalculados en esa misma iteración.',
      ],
    },
    STEP_ERROR,
    STEP_STOP,
  ],
}

export function vectorLatex(name, x) {
  const values = x.map((value) => formatNumber(value)).join(',\\ ')
  return `${name ? `${name} = ` : ''}(${values})`
}

// Filas de la tabla comparativa: las dos trayectorias intercaladas por iteración.
export const comparisonRows = jacobiSteps.flatMap((step, i) => [
  { key: `j${i}`, iteration: step.iteration, method: 'Jacobi', x: step.x, first: true },
  { key: `g${i}`, iteration: step.iteration, method: 'Gauss-Seidel', x: gaussSeidelSteps[i].x },
])
