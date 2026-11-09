// Contenido teórico de la cuadratura gaussiana: fórmulas en LaTeX, glosarios,
// las tablas que salen de las respuestas reales del solver y los pasos de
// restricciones y algoritmo.
//
// La notación es la del Resolver (m, N, tᵢ, wᵢ, xᵢ, Gₘ, H, cⱼ); las fórmulas
// del Resolver y sus glosarios vienen de ../gaussExplain.js.
import { formatNumber } from '../../../utils/iterationSteps'
import { sci } from './rombergContent'
// Respuestas reales del backend (POST /api/solve/gauss/): «function» es el
// ejemplo 1 del Resolver (Chapra, con su gráfico de rectángulos), «gauss» el 2
// (e^(−x²)), «sixth» el 4 (x⁶, error = cota), «root» el 5 (1/√x, con gráfico)
// y «composite» el 7 (Chapra con N = 2). El test test_gauss.TheoryExampleTests
// comprueba que siguen coincidiendo.
import EXAMPLES from './gaussExample.json'

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const GAUSS_EXAMPLE = EXAMPLES.gauss
export const SIXTH_EXAMPLE = EXAMPLES.sixth
export const ROOT_EXAMPLE = EXAMPLES.root
export const COMPOSITE_EXAMPLE = EXAMPLES.composite

export const rowsOf = (result) => result.iterations.map((step) => step.extra)
const chapraRows = rowsOf(FUNCTION_EXAMPLE)
const gaussRows = rowsOf(GAUSS_EXAMPLE)
const rootRows = rowsOf(ROOT_EXAMPLE)
const compositeRows = rowsOf(COMPOSITE_EXAMPLE)
const sixthRow3 = rowsOf(SIXTH_EXAMPLE)[2]

// --- Fórmulas -----------------------------------------------------------------------

export const tex = {
  // 2. definición formal
  rule: String.raw`\int_{-1}^{1} g(t)\,dt \approx \sum_{i=1}^{m} w_i\,g(t_i)`,
  change: String.raw`x = \frac{b + a}{2} + \frac{b - a}{2}\,t, \qquad dx = \frac{b - a}{2}\,dt`,
  mapped: String.raw`\int_a^b f(x)\,dx \approx \frac{b - a}{2}\sum_{i=1}^{m} w_i\,f\!\Big(\frac{b + a}{2} + \frac{b - a}{2}\,t_i\Big)`,

  // 4.1 Gauss de 2 puntos
  conditions: String.raw`\int_{-1}^{1} t^k\,dt = w_1t_1^k + w_2t_2^k, \qquad k = 0, 1, 2, 3`,
  system: String.raw`w_1 + w_2 = 2,\quad w_1t_1 + w_2t_2 = 0,\quad w_1t_1^2 + w_2t_2^2 = \tfrac{2}{3},\quad w_1t_1^3 + w_2t_2^3 = 0`,
  symmetry: String.raw`t_2 = -t_1,\quad w_1 = w_2 \;\Longrightarrow\; 2w_1 = 2 \;\Longrightarrow\; w_1 = w_2 = 1`,
  third: String.raw`t_1^2 + t_1^2 = 2t_1^2 = \tfrac{2}{3} \;\Longrightarrow\; t_1^2 = \tfrac{1}{3} \;\Longrightarrow\; t_1 = -\tfrac{1}{\sqrt{3}},\quad t_2 = \tfrac{1}{\sqrt{3}}`,
  result2: String.raw`\int_{-1}^{1} g(t)\,dt \approx g\!\left(-\tfrac{1}{\sqrt{3}}\right) + g\!\left(\tfrac{1}{\sqrt{3}}\right)`,
  t4: [
    String.raw`\int_{-1}^{1} t^4\,dt = \tfrac{2}{5} = 0.4`,
    String.raw`\text{Simpson (3 evaluaciones): } \tfrac{1}{3}\big(1 + 4\cdot 0 + 1\big) = \tfrac{2}{3},\qquad |E_t| = 0.266667`,
    String.raw`\text{Gauss, 2 puntos (2 evaluaciones): } \big(\tfrac{1}{\sqrt{3}}\big)^4 + \big(\tfrac{1}{\sqrt{3}}\big)^4 = \tfrac{2}{9},\qquad |E_t| = 0.177778`,
    String.raw`\text{Gauss, 3 puntos: } \tfrac{5}{9}\big(\tfrac{3}{5}\big)^2 + \tfrac{8}{9}\cdot 0 + \tfrac{5}{9}\big(\tfrac{3}{5}\big)^2 = \tfrac{2}{5},\qquad E_t = 0`,
  ],

  // 4.3 Legendre
  recurrence: String.raw`P_0 = 1,\qquad P_1 = t,\qquad P_k(t) = \frac{(2k - 1)\,t\,P_{k-1}(t) - (k - 1)\,P_{k-2}(t)}{k}`,
  firstCases: [
    String.raw`P_2(t) = \frac{3t^2 - 1}{2} \quad\Rightarrow\quad t = \pm\tfrac{1}{\sqrt{3}}`,
    String.raw`P_3(t) = \frac{5t^3 - 3t}{2} \quad\Rightarrow\quad t = 0,\ \pm\sqrt{\tfrac{3}{5}}`,
    String.raw`P_4(t) = \frac{35t^4 - 30t^2 + 3}{8}`,
  ],
  orthogonality: String.raw`\int_{-1}^{1} P_j(t)\,P_k(t)\,dt = 0 \quad (j \ne k);\qquad \int_{-1}^{1} P_2P_3\,dt = 0,\quad \int_{-1}^{1} P_1P_3\,dt = 0,\quad \int_{-1}^{1} P_2^2\,dt = \tfrac{2}{5}`,
  split: String.raw`p(t) = q(t)\,P_m(t) + r(t), \qquad \text{grado de } q \text{ y de } r < m`,
  weights: String.raw`w_i = \frac{2}{(1 - t_i^2)\,\big[P_m'(t_i)\big]^2}`,

  // 4.4 error
  error: String.raw`E_t = \frac{(b - a)^{2m+1}\,(m!)^4}{(2m + 1)\,\big[(2m)!\big]^3}\,f^{(2m)}(\xi)`,
  sixth: String.raw`E_t = \frac{1}{15750}\cdot 720 = 0.045714 = \frac{2}{7} - 0.24`,
}

// --- Glosarios -------------------------------------------------------------------

const g = (symbol, text) => ({ symbol, text })

export const GLOSSARIES = {
  rule: [
    g('m', 'Cuántos puntos (evaluaciones de la función) usa la regla.'),
    g('t_i', 'Los nodos: dónde se evalúa, dentro de [−1, 1]. Son las raíces del polinomio de Legendre de grado m.'),
    g('w_i', 'Los pesos: cuánto cuenta cada evaluación. Siempre suman 2, el ancho de [−1, 1].'),
    g('g(t)', 'La función ya escrita en la variable t (después del cambio de variable).'),
  ],
  change: [
    g('t', 'La variable nueva: recorre [−1, 1] cuando x recorre [a, b].'),
    g('\\tfrac{b + a}{2}', 'El centro del intervalo: ahí cae t = 0.'),
    g('\\tfrac{b - a}{2}', 'La mitad del ancho: cuánto se estira [−1, 1] para cubrir [a, b].'),
    g('dx', 'Al cambiar de variable, dx = (b − a)/2 · dt: por eso aparece ese factor delante de la suma.'),
  ],
  mapped: [
    g('x_i', 'El nodo tᵢ llevado a [a, b]: xᵢ = (b + a)/2 + (b − a)/2 · tᵢ.'),
    g('f(x_i)', 'La altura de la curva en ese punto.'),
    g('w_i\\,f(x_i)', 'Cada altura multiplicada por cuánto cuenta.'),
    g('G_m', 'Así llama el Resolver al resultado con m puntos.'),
  ],
  system: [
    g('2', 'La integral exacta de 1 en [−1, 1].'),
    g('0', 'La integral exacta de t (y de t³) en [−1, 1]: son funciones impares, lo de la izquierda cancela lo de la derecha.'),
    g('\\tfrac{2}{3}', 'La integral exacta de t² en [−1, 1].'),
    g('t_1,\\ t_2,\\ w_1,\\ w_2', 'Las 4 incógnitas: los 2 nodos y los 2 pesos.'),
  ],
  recurrence: [
    g('P_k(t)', 'El polinomio de Legendre de grado k.'),
    g('P_{k-1},\\ P_{k-2}', 'Los dos anteriores: con ellos se calcula el siguiente, sin fórmulas largas.'),
    g('(2k - 1),\\ (k - 1),\\ k', 'Números fijos que dependen sólo del grado k.'),
  ],
  orthogonality: [
    g('P_jP_k', 'El producto de dos polinomios de Legendre distintos.'),
    g('0', 'Su integral en [−1, 1] es 0: se dice que son «ortogonales».'),
    g('q,\\ r', 'El cociente y el resto de dividir p entre Pₘ, ambos de grado menor que m.'),
  ],
  weights: [
    g('t_i', 'El nodo (raíz de Pₘ), que el Resolver calcula con el método de Newton.'),
    g("P_m'(t_i)", 'La derivada del polinomio de Legendre en el nodo.'),
    g('1 - t_i^2', 'Se achica cerca de los extremos ±1, pero P′ₘ crece más: por eso los pesos de los nodos externos son chicos.'),
  ],
  error: [
    g('E_t', 'El error verdadero, I − Gₘ (fórmula simple, N = 1).'),
    g('(b - a)^{2m+1}', 'El ancho del intervalo elevado a 2m + 1: con intervalos chicos el error cae muy rápido.'),
    g('\\tfrac{(m!)^4}{(2m+1)[(2m)!]^3}', 'Una constante que se achica muy rápido al crecer m.'),
    g('f^{(2m)}(\\xi)', 'La derivada de orden 2m en algún punto ξ de [a, b] (no se sabe cuál).'),
  ],
}

// --- Tabla de nodos y pesos (formas exactas del Resolver, ejemplo 1) ---------------

/** Para cada m ≤ 4, los nodos y pesos distintos (t ≥ 0), con su forma exacta y decimales. */
const withDecimals = (latex, value) => (latex === formatNumber(value) ? latex : `${latex} \\approx ${formatNumber(value)}`)
export const NODE_TABLE = chapraRows.slice(0, 4).map((row) => {
  const half = row.step.nodes.filter((n) => n.t >= 0).sort((p, q) => p.t - q.t)
  const pm = (n) => (n.t === 0 ? '' : '\\pm ')
  return {
    m: row.m,
    t: half.map((n) => `${pm(n)}${withDecimals(n.t_latex, n.t).replace('\\approx ', `\\approx ${pm(n)}`)}`),
    w: half.map((n) => withDecimals(n.w_latex, n.w)),
  }
})

// --- Interpretación: gráfico de rectángulos del ejemplo 1 (m = 1 a 4) --------------

export const CHART_ROWS = FUNCTION_EXAMPLE.chart_rows.filter((r) => r.m <= 4)
export const CHAPRA_EXACT = formatNumber(FUNCTION_EXAMPLE.integral.value)
export const chartLive = (m) => {
  const row = chapraRows[m - 1]
  return { G: formatNumber(row.G), error: formatNumber(row.true_error) }
}
export const chartArea = (m) => {
  const { G, error } = chartLive(m)
  return `Rectángulos (m = ${m}): área G = ${G} · Eₜ = ${error}`
}
export const chartCurveLabel = `f(x) · I = ${CHAPRA_EXACT} (exacta)`

// --- Error y convergencia ---------------------------------------------------------

export const gaussReference = formatNumber(GAUSS_EXAMPLE.integral.value)
export const errorRows = gaussRows.map((row) => ({ m: row.m, G: formatNumber(row.G), error: sci(row.true_error) }))

export const ERROR_CONSTANTS = [
  { m: 1, c: '\\tfrac{1}{3}' },
  { m: 2, c: '\\tfrac{1}{135}' },
  { m: 3, c: '\\tfrac{1}{15750}' },
  { m: 4, c: '\\tfrac{1}{3472875}' },
  { m: 5, c: '\\tfrac{1}{1237732650}' },
]

export const sixth = {
  G: formatNumber(sixthRow3.G),
  error: formatNumber(sixthRow3.true_error),
  bound: formatNumber(sixthRow3.bound),
}

// Evaluaciones de f para |Eₜ| ≤ 0.000001 (comparación de costo del Resolver, ejemplos 1 a 3).
export const COST_ROWS = [
  { label: 'Chapra [0, 0.8]', m: null, ...costOf(FUNCTION_EXAMPLE) },
  { label: null, m: 'e^{-x^2} \\text{ en } [0, 1]', ...costOf(GAUSS_EXAMPLE) },
  { label: null, m: '\\sin x \\text{ en } [0, \\pi]', trapezoid: 2049, simpson: 65, romberg: 17, gauss: 5 },
]
function costOf(result) {
  const c = result.cost
  return { trapezoid: c.trapezoid_evaluations, simpson: c.simpson_evaluations, romberg: c.romberg_evaluations, gauss: c.gauss_evaluations }
}

// --- Funciones singulares: 1/√x (ejemplo 5) -------------------------------------------

export const ROOT_CHART_MS = [1, 4, 12]
export const root = {
  first: rootRows.slice(0, 6).map((r) => formatNumber(r.G)),
  m12: formatNumber(rootRows[11].G),
  note: ROOT_EXAMPLE.notes[0],
  area: (m) => `Rectángulos (m = ${m}): área G = ${formatNumber(rootRows[m - 1].G)} · Eₜ = ${formatNumber(rootRows[m - 1].true_error)}`,
  curveLabel: 'f(x) = 1/√x · I = 2 (exacta)',
}
// Gauss compuesta con m = 4 en 1/√x (verificado con un script; no es un ejemplo del Resolver).
export const ROOT_COMPOSITE = [
  { N: 1, value: '1.806343', evaluations: 4 },
  { N: 4, value: '1.903171', evaluations: 16 },
  { N: 16, value: '1.951586', evaluations: 64 },
  { N: 64, value: '1.975793', evaluations: 256 },
]

// --- Ejemplo resuelto (ejemplo 1) ---------------------------------------------------

export const example = {
  fn: `f(x) = ${FUNCTION_EXAMPLE.function.latex}`,
  integral: `I = \\int_0^{0.8} f(x)\\,dx = \\frac{3076}{1875} = ${CHAPRA_EXACT}`,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  rows: chapraRows,
  row: (m) => chapraRows[m - 1],
  G: (m) => formatNumber(chapraRows[m - 1].G),
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
}

/** Momentos de la regla con m = 3 (nodos y pesos de la fila 3 del ejemplo 1), k = 0..6. */
const EXACT_MOMENTS = ['2', '0', '\\tfrac{2}{3}', '0', '\\tfrac{2}{5}', '0', '\\tfrac{2}{7}']
export const moments3 = EXACT_MOMENTS.map((exact, k) => {
  const value = chapraRows[2].step.nodes.reduce((s, n) => s + n.w * n.t ** k, 0)
  const exactValue = k % 2 ? 0 : 2 / (k + 1)
  return { k, value: formatNumber(Math.abs(value) < 1e-12 ? 0 : value), exact, ok: Math.abs(value - exactValue) <= 1e-12 }
})

export const THREE_EVALUATIONS = [
  { method: 'Trapecio (n = 2)', value: '1.0688', error: '34.85 %' },
  { method: 'Simpson 1/3 (n = 2)', value: '1.367467', error: '16.645 %' },
  { method: 'Gauss (3 puntos)', value: example.G(3), error: '0 %' },
]

export const composite = {
  nodes: compositeRows[1].step.groups.flatMap((gr) => gr.points.map((p) => p.x_display)),
  G2: formatNumber(compositeRows[1].G),
  E2: formatNumber(compositeRows[1].true_error),
  G3: formatNumber(compositeRows[2].G),
  row: compositeRows[1],
  previous: compositeRows[0],
}

// --- Restricciones y algoritmo --------------------------------------------------

export const PRECAUTIONS = [
  {
    title: 'Necesita la fórmula de f',
    body: [
      'Los nodos son números irracionales (como ',
      { m: '1/\\sqrt{3}' },
      '), así que no sirve con datos tabulados. Para datos medidos: el trapecio, Simpson o Romberg.',
    ],
  },
  {
    title: 'Funciona mejor con funciones suaves',
    body: [
      'Con singularidades o derivadas que no existen (como ',
      { m: '1/\\sqrt{x}' },
      ' en 0), la convergencia es lenta. Ver «Cuándo Gauss no es suficiente».',
    ],
  },
  {
    title: 'Al aumentar m, los puntos cambian',
    body: [
      'Los nodos de ',
      { m: 'm + 1' },
      ' no incluyen a los de ',
      { m: 'm' },
      ': no se reutilizan las evaluaciones anteriores, a diferencia del trapecio y de Romberg. Por eso el Resolver cuenta las evaluaciones de cada fila por separado.',
    ],
  },
  {
    title: 'Funciones que oscilan mucho',
    body: [
      'Si ',
      { m: 'f' },
      ' sube y baja muchas veces en ',
      { m: '[a, b]' },
      ', conviene la versión compuesta (',
      { m: 'N > 1' },
      '): cada subintervalo ve una parte más sencilla de la curva.',
    ],
  },
  {
    title: 'Los nodos deben estar en el dominio',
    body: [
      { m: 'f' },
      ' debe poder evaluarse en todos los nodos ',
      { m: 'x_i' },
      ', aunque no esté definida en los extremos ',
      { m: 'a' },
      ' o ',
      { m: 'b' },
      '. El Resolver lo revisa y lo avisa.',
    ],
  },
  {
    title: 'Radianes',
    body: ['Las funciones trigonométricas se evalúan en radianes.'],
  },
]

export const ALGORITHM_STEPS = [
  {
    title: 'Datos',
    body: [{ m: 'f(x)' }, ', ', { m: 'a' }, ', ', { m: 'b' }, ', ', { m: 'N' }, ', la tolerancia y el máximo de puntos.'],
  },
  {
    title: 'Cambio de variable',
    body: [
      { m: 'x = \\frac{b + a}{2} + \\frac{b - a}{2}\\,t' },
      '; si ',
      { m: 'N > 1' },
      ', en cada subintervalo: ',
      { m: 'x = c_j + \\frac{H}{2}\\,t' },
      '.',
    ],
  },
  {
    title: 'Para m = 1, 2, …',
    body: [
      'Obtener los nodos ',
      { m: 't_i' },
      ' (raíces de ',
      { m: 'P_m' },
      ', con Newton) y los pesos ',
      { m: 'w_i' },
      ', y llevar cada nodo a ',
      { m: '[a, b]' },
      '.',
    ],
  },
  {
    title: 'Evaluar y sumar',
    body: [
      'Evaluar ',
      { m: 'f(x_i)' },
      ', multiplicar por ',
      { m: 'w_i' },
      ', sumar y multiplicar por ',
      { m: '(b - a)/2' },
      ' (o por ',
      { m: 'H/2' },
      ' en cada subintervalo y sumar los subintervalos): es ',
      { m: 'G_m' },
      '.',
    ],
  },
  {
    title: 'Errores',
    body: [
      'Error estimado ',
      { m: '|G_m - G_{m-1}|' },
      ', ',
      { m: 'E_t' },
      ' y ',
      { m: '\\varepsilon_t' },
      ', y la cota si ',
      { m: 'm \\le 5' },
      '.',
    ],
  },
  {
    title: 'Parar o seguir',
    body: [
      'Se para con al menos 6 filas y el error estimado ',
      { m: '\\le' },
      ' tolerancia, o al llegar al máximo de puntos; si no, se vuelve al paso 3 con un punto más.',
    ],
  },
  {
    title: 'Comprobar',
    body: [
      'La integral con la antiderivada; los momentos (',
      { m: '\\sum w_i t_i^k' },
      ' frente a ',
      { m: '\\int_{-1}^{1} t^k\\,dt' },
      ', exactos hasta ',
      { m: 'k = 2m - 1' },
      '); y la comparación de costo con el trapecio, Simpson y Romberg.',
    ],
  },
]
