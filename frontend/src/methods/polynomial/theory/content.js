// Contenido teórico de la categoría «Polinomios» (Bairstow): fórmulas en
// LaTeX, el ejemplo resuelto y los pasos del algoritmo.
//
// La notación es la del Resolver: factor x² − r·x − s, coeficientes a_i, b_i,
// c_i con el índice igual a la potencia, errores ε_r y ε_s en %. Las fórmulas
// de la iteración del ejemplo se generan con las mismas funciones que el
// detalle de cada iteración en Resolver (../formulas.js).
import { formatNumber } from '../../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, latexNumber } from '../../../utils/latexFormulas'
import {
  B_FORMULA,
  C_FORMULA,
  FACTOR_FORMULA,
  checkLatex,
  currentValuesLatex,
  determinantStepsLatex,
  discriminantLatex,
  errorsLatex,
  formatComplex,
  incrementsLatex,
  rootsLatex,
  systemLatex,
  updatesLatex,
} from '../formulas'
// Respuesta real del backend (POST /api/solve/bairstow/) para el ejemplo
// «Clásico de Chapra y Canale», recortada: la iteración 1 completa (tablas b
// y c, matrices de Cramer), las demás iteraciones del factor 1 sólo con los
// valores de su tabla, y los factores, las raíces y la factorización.
import EXAMPLE from './bairstowExample.json'

export { CURRENT_COLOR, PREVIOUS_COLOR, EXAMPLE, formatNumber }

const cases = (...rows) => `\\begin{cases} ${rows.join(' \\\\ ')} \\end{cases}`

export const tex = {
  // Fundamento
  polynomial: 'f(x) = a_n x^n + a_{n-1} x^{n-1} + \\dots + a_1 x + a_0, \\qquad a_n \\neq 0',
  fundamentalTheorem: 'f(x) = a_n (x - x_1)(x - x_2) \\cdots (x - x_n)',
  conjugatePair: '(x - (a + bi))\\,(x - (a - bi)) = x^2 - 2a\\,x + (a^2 + b^2)',
  realFactorization:
    'f(x) = a_n \\underbrace{(x - x_1) \\cdots}_{\\text{factores lineales}} \\; \\underbrace{(x^2 - r_1 x - s_1) \\cdots}_{\\text{factores cuadráticos}}',
  factor: FACTOR_FORMULA,
  factorRoots: 'x = \\frac{r \\pm \\sqrt{r^2 + 4s}}{2}',
  deflation: 'f(x) = (x^2 - r\\,x - s)\\, q(x), \\qquad \\operatorname{grado} q = n - 2',

  // Definición formal
  division:
    'f(x) = (x^2 - r\\,x - s)\\left(b_n x^{n-2} + b_{n-1} x^{n-3} + \\dots + b_2\\right) + b_1 (x - r) + b_0',
  residue: 'b_1 (x - r) + b_0',
  exactFactor: 'x^2 - r\\,x - s \\text{ es factor de } f(x) \\iff b_1 = 0 \\;\\text{ y }\\; b_0 = 0',
  goal: cases('b_1(r, s) = 0', 'b_0(r, s) = 0'),
  bRecurrence: cases(
    'b_n = a_n',
    'b_{n-1} = a_{n-1} + r\\, b_n',
    `${B_FORMULA}, \\quad i = n-2, \\dots, 0`
  ),
  cRecurrence: cases(
    'c_n = b_n',
    'c_{n-1} = b_{n-1} + r\\, c_n',
    `${C_FORMULA}, \\quad i = n-2, \\dots, 1`
  ),
  bRecurrenceShort: B_FORMULA,
  cRecurrenceShort: C_FORMULA,
  system: cases('c_2\\, \\Delta r + c_3\\, \\Delta s = -b_1', 'c_1\\, \\Delta r + c_2\\, \\Delta s = -b_0'),
  determinant: 'D = \\begin{vmatrix} c_2 & c_3 \\\\ c_1 & c_2 \\end{vmatrix} = c_2^2 - c_1 c_3',
  determinantR:
    'D_r = \\begin{vmatrix} -b_1 & c_3 \\\\ -b_0 & c_2 \\end{vmatrix} = -b_1 c_2 + b_0 c_3',
  determinantS:
    'D_s = \\begin{vmatrix} c_2 & -b_1 \\\\ c_1 & -b_0 \\end{vmatrix} = -b_0 c_2 + b_1 c_1',
  increments: '\\Delta r = \\frac{D_r}{D}, \\qquad \\Delta s = \\frac{D_s}{D}',
  update: 'r \\leftarrow r + \\Delta r, \\qquad s \\leftarrow s + \\Delta s',
  errors:
    '\\varepsilon_r = \\left| \\frac{\\Delta r}{r} \\right| \\cdot 100\\,\\%, \\qquad \\varepsilon_s = \\left| \\frac{\\Delta s}{s} \\right| \\cdot 100\\,\\%',
  discriminant: '\\Delta = r^2 + 4s',
  nonzero: 'D \\neq 0',

  // Derivación
  matching:
    '\\begin{aligned} x^{n}&: & a_n &= b_n \\\\ x^{n-1}&: & a_{n-1} &= b_{n-1} - r\\, b_n \\\\ ' +
    'x^{n-2}&: & a_{n-2} &= b_{n-2} - r\\, b_{n-1} - s\\, b_n \\end{aligned}',
  matchI: 'x^{i}: \\quad a_i = b_i - r\\, b_{i+1} - s\\, b_{i+2} \\;\\Longrightarrow\\; ' + B_FORMULA,
  // Con fracciones en tamaño completo, las filas de `cases` necesitan aire.
  linearization:
    '\\begin{cases} b_1 + \\dfrac{\\partial b_1}{\\partial r}\\, \\Delta r + \\dfrac{\\partial b_1}{\\partial s}\\, \\Delta s = 0 \\\\[2.5ex] ' +
    'b_0 + \\dfrac{\\partial b_0}{\\partial r}\\, \\Delta r + \\dfrac{\\partial b_0}{\\partial s}\\, \\Delta s = 0 \\end{cases}',
  partialR:
    '\\frac{\\partial b_i}{\\partial r} = b_{i+1} + r\\, \\frac{\\partial b_{i+1}}{\\partial r} + s\\, \\frac{\\partial b_{i+2}}{\\partial r}',
  partialS:
    '\\frac{\\partial b_i}{\\partial s} = b_{i+2} + r\\, \\frac{\\partial b_{i+1}}{\\partial s} + s\\, \\frac{\\partial b_{i+2}}{\\partial s}',
  partialRResult: '\\frac{\\partial b_i}{\\partial r} = c_{i+1}',
  partialSResult: '\\frac{\\partial b_i}{\\partial s} = c_{i+2}',
  partialRStart:
    '\\frac{\\partial b_n}{\\partial r} = 0, \\quad \\frac{\\partial b_{n-1}}{\\partial r} = b_n = c_n, \\quad \\frac{\\partial b_{n-2}}{\\partial r} = b_{n-1} + r\\, c_n = c_{n-1}, \\; \\dots',
  partialSStart:
    '\\frac{\\partial b_n}{\\partial s} = \\frac{\\partial b_{n-1}}{\\partial s} = 0, \\quad \\frac{\\partial b_{n-2}}{\\partial s} = b_n = c_n, \\quad \\frac{\\partial b_{n-3}}{\\partial s} = b_{n-1} + r\\, c_n = c_{n-1}, \\; \\dots',
  jacobian:
    'J = \\begin{pmatrix} \\dfrac{\\partial b_1}{\\partial r} & \\dfrac{\\partial b_1}{\\partial s} \\\\[1.2ex] \\dfrac{\\partial b_0}{\\partial r} & \\dfrac{\\partial b_0}{\\partial s} \\end{pmatrix} = \\begin{pmatrix} c_2 & c_3 \\\\ c_1 & c_2 \\end{pmatrix}',
  newtonForm:
    'J \\begin{pmatrix} \\Delta r \\\\ \\Delta s \\end{pmatrix} = -\\begin{pmatrix} b_1 \\\\ b_0 \\end{pmatrix}',

  // Convergencia
  quadratic: '\\left| r_{k+1} - r^{*} \\right| + \\left| s_{k+1} - s^{*} \\right| \\leq C \\left( \\left| r_k - r^{*} \\right| + \\left| s_k - s^{*} \\right| \\right)^{2}',
  // La tolerancia se escribe εs como en Resolver; su subíndice es texto para
  // no confundirla con el error ε_s de la variable s.
  stop: '\\varepsilon_r \\leq \\varepsilon_{\\text{s}} \\quad \\text{y} \\quad \\varepsilon_s \\leq \\varepsilon_{\\text{s}}',
  singularStart: 'x^3 - x^2 + x - 1',
  singularStep: 'c_3 = 1,\\; c_2 = -1,\\; c_1 = 1 \\;\\Longrightarrow\\; D = (-1)^2 - (1)(1) = 0',
  missingCoefficients: 'x^4 - 5x^2 + 4 \\;\\rightarrow\\; [1,\\ 0,\\ -5,\\ 0,\\ 4]',
  zeroRoots: 'f(x) = x^{k}\\, g(x), \\qquad g(0) \\neq 0',
}

// --- Ejemplo resuelto ------------------------------------------------------

const [FIRST_FACTOR, SECOND_FACTOR, THIRD_FACTOR] = EXAMPLE.factors
const FIRST = EXAMPLE.iterations[0].extra

export { FIRST_FACTOR, SECOND_FACTOR, THIRD_FACTOR }

export const example = {
  polynomial: `f(x) = ${EXAMPLE.polynomial.latex}`,
  start: `r_0 = ${latexNumber(EXAMPLE.r0)}, \\quad s_0 = ${latexNumber(EXAMPLE.s0)}, \\quad \\varepsilon_{\\text{s}} = ${latexNumber(EXAMPLE.tolerance_percent)}\\,\\%`,
  tolerance: `${latexNumber(EXAMPLE.tolerance_percent)}\\,\\%`,
  coefficients: EXAMPLE.polynomial.coefficients,
  degree: EXAMPLE.polynomial.degree,
}

/* Iteración 1 completa, con los mismos sub-pasos y fórmulas que el detalle
   de la iteración en Resolver. Las tablas sintéticas se dibujan aparte. */
export const firstIteration = {
  extra: FIRST,
  current: currentValuesLatex(FIRST),
  system: systemLatex(FIRST),
  D: determinantStepsLatex('D', FIRST.matrix, FIRST.D),
  Dr: determinantStepsLatex('D_r', FIRST.matrices[0], FIRST.D_r, 0),
  Ds: determinantStepsLatex('D_s', FIRST.matrices[1], FIRST.D_s, 1),
  increments: incrementsLatex(FIRST),
  updates: updatesLatex(FIRST),
  errors: errorsLatex(FIRST),
}

/* Tabla de iteraciones del factor 1. `firstMet` marca la primera iteración
   en que ambos errores quedan bajo la tolerancia. */
const firstMetIndex = EXAMPLE.iterations.findIndex((row) => row.extra.meets_tolerance)
export const firstMetIteration = EXAMPLE.iterations[firstMetIndex].iteration

// Incrementos y errores en notación científica cuando son muy pequeños (como
// |f(x)| en Resolver): con 6 decimales las últimas iteraciones mostrarían 0 y
// no se vería la caída cuadrática.
function smallLatex(value) {
  if (value === 0 || Math.abs(value) >= 1e-3) return latexNumber(value)
  const [mantissa, exponent] = value.toExponential(2).split('e')
  return `${mantissa} \\times 10^{${Number(exponent)}}`
}

export const iterationRows = EXAMPLE.iterations.map((row, i) => ({
  iteration: row.iteration,
  r: formatNumber(row.x[0]),
  s: formatNumber(row.x[1]),
  deltaR: smallLatex(row.extra.delta_r),
  deltaS: smallLatex(row.extra.delta_s),
  epsR: smallLatex(row.extra.eps_r),
  epsS: smallLatex(row.extra.eps_s),
  meets: row.extra.meets_tolerance,
  firstMet: i === firstMetIndex,
}))

/* Cierre de cada factor iterado: el factor, el discriminante y las raíces,
   con las mismas fórmulas que el cierre de factor en Resolver. */
function closure(factor) {
  return {
    factor: `x^2 - r\\,x - s = ${factor.factor_latex}`,
    values: `r = ${latexNumber(factor.r)}, \\qquad s = ${latexNumber(factor.s)}`,
    discriminant: discriminantLatex(factor.r, factor.s, factor.discriminant),
    roots: rootsLatex(factor.r, factor.discriminant, factor.roots),
    dividend: factor.dividend.latex,
    quotient: factor.quotient?.latex ?? null,
    residue: `b_1 = ${smallLatex(factor.residue.b1)}, \\quad b_0 = ${smallLatex(factor.residue.b0)}`,
  }
}

export const firstClosure = closure(FIRST_FACTOR)
export const secondClosure = closure(SECOND_FACTOR)
export const thirdClosure = {
  factor: THIRD_FACTOR.factor_latex,
  root: `${THIRD_FACTOR.factor_latex} = 0 \\;\\Longrightarrow\\; x = \\mathbf{${latexNumber(THIRD_FACTOR.roots[0].re)}}`,
}

export const rootRows = EXAMPLE.roots.map((root, i) => ({
  name: `x_{${i + 1}}`,
  value: formatComplex(root.re, root.im),
  kind: root.im === 0 ? 'real' : 'compleja',
  factor: root.factor + 1,
  check: checkLatex(root.check),
}))

export const factorization = `f(x) = ${EXAMPLE.factorization}`

/* Pasos del algoritmo como datos (mismo formato que los de los otros
   métodos): cada descripción mezcla texto y fórmulas { m }. */
export const ALGORITHM_STEPS = {
  bairstow: [
    {
      title: 'Paso previo: raíces nulas',
      body: [
        'Si ',
        { m: 'a_0 = 0' },
        ', se extrae el factor ',
        { m: 'x^k' },
        ': son ',
        { m: 'k' },
        ' raíces ',
        { m: 'x = 0' },
        ', y se sigue con el polinomio reducido.',
      ],
    },
    {
      title: 'Datos iniciales',
      body: [
        'Se eligen ',
        { m: 'r_0' },
        ' y ',
        { m: 's_0' },
        ' (por defecto, ',
        { m: '-1' },
        '), la tolerancia ',
        { m: '\\varepsilon_{\\text{s}}' },
        ' en % y el máximo de iteraciones por factor.',
      ],
    },
    {
      title: 'Coeficientes b',
      body: ['Primera división sintética del polinomio entre ', { m: FACTOR_FORMULA }, ': ', { m: B_FORMULA }, '.'],
    },
    {
      title: 'Coeficientes c',
      body: [
        'Segunda división sintética, sobre los ',
        { m: 'b' },
        ': ',
        { m: C_FORMULA },
        ', hasta ',
        { m: 'c_1' },
        ' (',
        { m: 'c_0' },
        ' no se usa).',
      ],
    },
    {
      title: 'Sistema 2×2 por Cramer',
      body: [
        'Se plantea ',
        { m: 'c_2 \\Delta r + c_3 \\Delta s = -b_1' },
        ', ',
        { m: 'c_1 \\Delta r + c_2 \\Delta s = -b_0' },
        ' y se resuelve: ',
        { m: 'D = c_2^2 - c_1 c_3' },
        ', ',
        { m: '\\Delta r = D_r / D' },
        ', ',
        { m: '\\Delta s = D_s / D' },
        '. Si ',
        { m: 'D \\approx 0' },
        ', el método se detiene.',
      ],
    },
    {
      title: 'Actualización',
      body: ['Se suman los incrementos: ', { m: tex.update }, '.'],
    },
    {
      title: 'Error',
      body: [
        'Se calculan ',
        { m: '\\varepsilon_r = |\\Delta r / r| \\cdot 100' },
        ' y ',
        { m: '\\varepsilon_s = |\\Delta s / s| \\cdot 100' },
        ' con los valores nuevos. Se repite desde el paso 3 hasta que ambos sean ',
        { m: '\\leq \\varepsilon_{\\text{s}}' },
        ', con un mínimo de 6 iteraciones.',
      ],
    },
    {
      title: 'Raíces del factor',
      body: [
        'Con el discriminante ',
        { m: tex.discriminant },
        ' y ',
        { m: tex.factorRoots },
        ' se obtienen dos raíces reales, una doble o un par complejo conjugado.',
      ],
    },
    {
      title: 'Deflación',
      body: [
        'Se recalculan los ',
        { m: 'b' },
        ' con los ',
        { m: 'r' },
        ' y ',
        { m: 's' },
        ' finales: el cociente es ',
        { m: 'b_n, \\dots, b_2' },
        ' y el residuo ',
        { m: 'b_1, b_0' },
        ' debe ser ',
        { m: '\\approx 0' },
        '.',
      ],
    },
    {
      title: 'Repetir o cerrar',
      body: [
        'Si el cociente tiene grado ',
        { m: '\\geq 3' },
        ', se vuelve al paso 2 con él. Si tiene grado 2 se usa la fórmula cuadrática, y si tiene grado 1 se despeja.',
      ],
    },
  ],
}
