// Contenido teórico de la fórmula de 3 puntos: fórmulas en LaTeX, el ejemplo
// resuelto (datos reales del solver), la tabla de redondeo y los pasos del
// algoritmo.
//
// La notación es la del Resolver (D^med, D^ad, D^at, cotas (h²/6)·M₃ y
// (h²/3)·M₃) y el paso a paso se dibuja con los mismos componentes
// (DifferenceStepDetail, RefinementTable, DataPointsTable,
// DifferentiationVerification).
import { formatNumber } from '../../../utils/iterationSteps'
import { latexNumber } from '../../../utils/latexFormulas'
import { identityLatex } from '../formulas'
import { stepDetail as stepDetailOf } from './content'
// Respuestas reales del backend (POST /api/solve/tres-puntos/), sin recortar:
// «function» es el ejemplo «x·eˣ en x₀ = 2 (Burden y Faires)» y «table», «Tabla
// de x·eˣ (Burden y Faires, tabla + función)». El test
// test_three_point.TheoryExampleTests comprueba que siguen coincidiendo con el
// solver.
import EXAMPLES from './threePointExample.json'

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const TABLE_EXAMPLE = EXAMPLES.table

const rows = FUNCTION_EXAMPLE.iterations
const FORMULAS = FUNCTION_EXAMPLE.formulas
const byKey = Object.fromEntries(FORMULAS.map((f) => [f.key, f]))
export const MID = byKey.punto_medio
export const AHEAD = byKey.extremo_adelante
export const BEHIND = byKey.extremo_atras
export { FORMULAS }

export const tex = {
  // Definición formal (Burden y Faires, con el término exacto del error)
  mid:
    "f'(x_0) = \\frac{f(x_0 + h) - f(x_0 - h)}{2h} - \\frac{h^2}{6} f'''(\\xi), \\qquad \\xi \\in (x_0 - h,\\, x_0 + h)",
  ahead:
    "f'(x_0) = \\frac{-3f(x_0) + 4f(x_0 + h) - f(x_0 + 2h)}{2h} + \\frac{h^2}{3} f'''(\\xi), \\qquad \\xi \\in (x_0,\\, x_0 + 2h)",
  behind:
    "f'(x_0) = \\frac{3f(x_0) - 4f(x_0 - h) + f(x_0 - 2h)}{2h} + \\frac{h^2}{3} f'''(\\xi), \\qquad \\xi \\in (x_0 - 2h,\\, x_0)",

  // Interpretación geométrica: signo del error
  midSign: "D^{\\text{med}} - f'(x_0) \\approx +\\frac{h^2}{6} f'''(x_0)",
  endSign: "D^{\\text{ad}} - f'(x_0) \\approx D^{\\text{at}} - f'(x_0) \\approx -\\frac{h^2}{3} f'''(x_0)",

  // Derivación con Lagrange (extremo hacia adelante)
  lagrange: 'P_2(x) = f(x_0) L_0(x) + f(x_1) L_1(x) + f(x_2) L_2(x)',
  lagrangeBasis: 'L_j(x) = \\prod_{m \\ne j} \\frac{x - x_m}{x_j - x_m}',
  l0: "L_0'(x_0) = \\frac{2x_0 - x_1 - x_2}{(x_0 - x_1)(x_0 - x_2)} = \\frac{-3h}{2h^2} = -\\frac{3}{2h}",
  l1: "L_1'(x_0) = \\frac{x_0 - x_2}{(x_1 - x_0)(x_1 - x_2)} = \\frac{-2h}{-h^2} = \\frac{2}{h}",
  l2: "L_2'(x_0) = \\frac{x_0 - x_1}{(x_2 - x_0)(x_2 - x_1)} = \\frac{-h}{2h^2} = -\\frac{1}{2h}",
  lagrangeSum: "P_2'(x_0) = \\frac{-3f(x_0) + 4f(x_1) - f(x_2)}{2h}",

  // Derivación con Taylor (punto medio)
  taylorBoth:
    "f(x_0 \\pm h) = f(x_0) \\pm h f'(x_0) + \\frac{h^2}{2} f''(x_0) \\pm \\frac{h^3}{6} f'''(x_0) + \\frac{h^4}{24} f^{(4)}(x_0) \\pm \\cdots",
  taylorMid:
    "\\frac{f(x_0 + h) - f(x_0 - h)}{2h} = f'(x_0) + \\frac{h^2}{6} f'''(x_0) + \\frac{h^4}{120} f^{(5)}(x_0) + \\cdots",

  // Richardson
  average: '\\frac{D^{+}(h) + D^{-}(h)}{2} = \\frac{f(x_0 + h) - f(x_0 - h)}{2h}',
  richardson:
    '2 \\cdot \\frac{f(x_0 + h) - f(x_0)}{h} - \\frac{f(x_0 + 2h) - f(x_0)}{2h} = \\frac{-3f(x_0) + 4f(x_0 + h) - f(x_0 + 2h)}{2h}',

  // Error y convergencia
  bounds:
    "|D^{\\text{med}} - f'(x_0)| \\le \\frac{h^2}{6} M_3, \\qquad |D^{\\text{ext}} - f'(x_0)| \\le \\frac{h^2}{3} M_3, \\qquad M_3 = \\max |f'''(x)|",
  totalError: 'E(h) \\approx \\frac{h^2}{6} M_3 + \\frac{\\varepsilon\\,|f(x_0)|}{h}',
  optimalH: 'h^{*} = \\left(\\frac{3\\varepsilon\\,|f(x_0)|}{M_3}\\right)^{1/3}',
}

/* Desarrollo de D − f'(x₀) de cada fórmula (coeficientes verificados). */
export const ERROR_EXPANSION = [
  ['Progresiva (2 puntos)', "\\frac{h}{2} f'' + \\frac{h^2}{6} f''' + \\frac{h^3}{24} f^{(4)} + \\cdots"],
  ['Punto medio', "\\frac{h^2}{6} f''' + \\frac{h^4}{120} f^{(5)} + \\cdots"],
  ['Extremo hacia adelante', "-\\frac{h^2}{3} f''' - \\frac{h^3}{4} f^{(4)} - \\frac{7h^4}{60} f^{(5)} - \\cdots"],
  ['Extremo hacia atrás', "-\\frac{h^2}{3} f''' + \\frac{h^3}{4} f^{(4)} - \\frac{7h^4}{60} f^{(5)} - \\cdots"],
]

// --- Ejemplo de la función (ejemplo 1 del Resolver) ------------------------------

const first = rows[0].extra
const fn = FUNCTION_EXAMPLE.function
const n = (value) => latexNumber(value)

/** Props de DifferenceStepDetail para la fila k (como en RefinementTable). */
export const stepDetail = (k, formula) => stepDetailOf(k, formula, FUNCTION_EXAMPLE)

export const example = {
  function: `f(x) = ${fn.latex}`,
  derivative: `f'(x) = ${fn.derivative.latex}`,
  third: `f'''(x) = ${fn.higher_derivatives[3].latex}`,
  exact: `f'(${FUNCTION_EXAMPLE.x0_display.latex}) = 3e^2 = ${n(FUNCTION_EXAMPLE.exact)}`,
  data:
    `x_0 = ${FUNCTION_EXAMPLE.x0_display.latex}, \\quad h_0 = ${first.h.latex}, \\quad ` +
    `\\text{tolerancia} = ${n(FUNCTION_EXAMPLE.tolerance)}`,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
  last: rows.at(-1).extra,
  // 22.032305 < 22.054521 < 22.167168 < 22.228787
  order:
    `${n(first.extremo_adelante.D)} < ${n(first.extremo_atras.D)} < ` +
    `${n(FUNCTION_EXAMPLE.exact)} < ${n(first.punto_medio.D)}`,
}

/* Evaluaciones de la fila 1: los 5 puntos distintos que usan las tres fórmulas. */
export const evaluations = Object.values(
  Object.fromEntries(
    FORMULAS.flatMap((f) => first[f.key].points).map((p) => [p.x, { x: p.display.text, f: formatNumber(p.f) }])
  )
).sort((a, b) => Number(a.x) - Number(b.x))

/* Resumen de una fila: D, error real y cota de cada fórmula. */
export const rowSummary = (k) =>
  FORMULAS.map((f) => ({ key: f.key, name: f.name, symbol: f.symbol_latex, ...rows[k - 1].extra[f.key] }))

export const secondRow = { h: rows[1].extra.h.text, items: rowSummary(2) }

/* Tabla de convergencia: las 6 primeras filas del solver, sin el paso a paso. */
export const convergenceRows = rows.slice(0, 6).map((step) => ({
  k: step.iteration,
  h: step.extra.h.text,
  items: [MID, AHEAD, BEHIND].map((f) => step.extra[f.key]),
}))

// --- Richardson y comparación con las diferencias -------------------------------

const comparison = FUNCTION_EXAMPLE.comparison[0]
export const identities = FUNCTION_EXAMPLE.verification.identities.map((item) => ({
  key: item.key,
  latex: identityLatex(item, byKey[item.key]),
}))
export const differences = {
  forward: formatNumber(comparison.forward.D),
  backward: formatNumber(comparison.backward.D),
  lines: FUNCTION_EXAMPLE.comparison.map((line) => line.text),
}

const forwardError = comparison.forward.real_error
export const comparisonRows = [
  { name: 'Progresiva (2 puntos)', ...comparison.forward },
  { name: 'Regresiva (2 puntos)', ...comparison.backward },
  { name: AHEAD.name, ...first.extremo_adelante },
  { name: BEHIND.name, ...first.extremo_atras },
  { name: MID.name, ...first.punto_medio, best: true },
].map((row) => ({ ...row, times: formatNumber(Math.round((forwardError / row.real_error) * 10) / 10) }))

/* Primera fila en que el punto medio tiene error real ≤ 0.0001. */
const enough = rows.find((step) => step.extra.punto_medio.real_error <= 0.0001)
export const efficiency = { k: enough.iteration, h: enough.extra.h.text }

// --- Redondeo: la «V» de la progresiva y del punto medio ------------------------

/* Error real de x·eˣ en x₀ = 2 con h = 10⁻¹ … 10⁻¹², calculado en Python con
   doble precisión (como el backend). No se calcula aquí con Math.exp porque
   difiere de math.exp en el último bit y, en h = 10⁻⁸, eso cambia el
   resultado. Es sólo ilustrativo. */
const V_POWERS = Array.from({ length: 12 }, (_, i) => i + 1)
export const V_FORWARD = [1.54, 0.148, 0.0148, 0.00148, 0.000148, 1.48e-5, 1.44e-6, 1.07e-7, 1.14e-6, 6.47e-6, 1.13e-5, 0.00177]
export const V_MID = [0.0616, 0.000616, 6.16e-6, 6.16e-8, 7.79e-10, 6.01e-10, 1.81e-8, 1.96e-7, 1.14e-6, 6.47e-6, 7.75e-5, 0.00177]

const SUPERSCRIPT = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }
export const power10 = (p) => `10${String(p).replace(/./g, (c) => SUPERSCRIPT[c])}`

export const roundingCurve = {
  iterations: V_POWERS.map((p) => ({ iteration: p })),
  labels: V_POWERS.map((p) => power10(-p)),
  series: [
    { label: 'Error real de la progresiva', values: V_FORWARD, color: '--color-series-1' },
    { label: 'Error real del punto medio', values: V_MID, color: '--color-series-5' },
  ],
}

/* Orden de magnitud del error real (10^⌊log₁₀ E⌋) en los h de la tabla. */
const TABLE_POWERS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12]
const order = (value) => `10^{${Math.floor(Math.log10(value))}}`
export const roundingTable = {
  h: TABLE_POWERS.map((p) => `10^{-${p}}`),
  forward: TABLE_POWERS.map((p) => order(V_FORWARD[p - 1])),
  mid: TABLE_POWERS.map((p) => order(V_MID[p - 1])),
}

// --- Restricciones y algoritmo --------------------------------------------------

export const PRECAUTIONS = [
  {
    title: 'Tercera derivada continua',
    body: [
      'Para que la cota valga, ',
      { m: 'f' },
      ' debe tener ',
      { m: "f'''" },
      ' continua en el intervalo que usa la fórmula.',
    ],
  },
  {
    title: 'Dominio de f',
    body: [
      'Todos los puntos que usa la fórmula deben estar en el dominio. El extremo llega hasta ',
      { m: 'x_0 \\pm 2h' },
      ': por ejemplo, ',
      { m: '\\ln x' },
      ' con ',
      { m: 'x_0 = 0.15' },
      ', ',
      { m: 'h = 0.1' },
      ' y el extremo hacia atrás necesita ',
      { m: '\\ln(-0.05)' },
      '. Es el mismo caso que rechaza el Resolver.',
    ],
  },
  {
    title: 'Espaciado uniforme en tablas',
    body: [
      'Las fórmulas suponen el mismo ',
      { m: 'h' },
      ' entre todos los puntos. Con datos no uniformes, los coeficientes ',
      { m: '-3,\\ 4,\\ -1' },
      ' y ',
      { m: '-1,\\ 0,\\ 1' },
      ' dejan de ser correctos.',
    ],
  },
  {
    title: 'Qué fórmula usar en una tabla',
    body: [
      'En los puntos interiores, el punto medio (la más precisa); en el primer punto, el extremo hacia adelante; en el último, el extremo hacia atrás. Es la columna «Recomendada» del Resolver.',
    ],
  },
  {
    title: 'Datos con ruido',
    body: [
      'Si cada dato tiene un error de hasta ',
      { m: '\\delta' },
      ', el punto medio puede amplificarlo hasta ',
      { m: '\\delta / h' },
      ' y el extremo hasta ',
      { m: '4\\delta / h' },
      ' (la suma de los coeficientes en valor absoluto, ',
      { m: '3 + 4 + 1 = 8' },
      ', entre ',
      { m: '2h' },
      '). Con ',
      { m: '\\delta = 0.001' },
      ' y ',
      { m: 'h = 0.01' },
      ': hasta 0.1 en el punto medio y 0.4 en el extremo.',
    ],
  },
  {
    title: 'Ni muy grande ni muy pequeño',
    body: [{ m: 'h' }, ' grande aumenta el truncamiento; muy pequeño, el redondeo (ver la tabla de redondeo).'],
  },
  {
    title: 'Radianes',
    body: ['Las funciones trigonométricas se evalúan en radianes.'],
  },
]

export const ALGORITHM_STEPS = [
  {
    title: 'Datos',
    body: [
      { m: 'f(x)' },
      ' (o la tabla), ',
      { m: 'x_0' },
      ', ',
      { m: 'h_0' },
      ', la fórmula, la tolerancia y el máximo de refinamientos.',
    ],
  },
  {
    title: 'Puntos',
    body: [
      'Punto medio: ',
      { m: 'x_0 - h,\\ x_0 + h' },
      '; extremo hacia adelante: ',
      { m: 'x_0,\\ x_0 + h,\\ x_0 + 2h' },
      '; extremo hacia atrás: ',
      { m: 'x_0,\\ x_0 - h,\\ x_0 - 2h' },
      '.',
    ],
  },
  {
    title: 'Evaluar',
    body: ['Se calcula ', { m: 'f' }, ' en los puntos.'],
  },
  {
    title: 'Combinar',
    body: [
      'Se calcula cada producto coeficiente·valor, se suman y se divide entre ',
      { m: '2h' },
      ': es ',
      { m: 'D_k' },
      ', la aproximación de la fila ',
      { m: 'k' },
      '.',
    ],
  },
  {
    title: 'Errores',
    body: [
      'Error estimado ',
      { m: '|D_k - D_{k-1}|' },
      '; error real ',
      { m: "|D_k - f'(x_0)|" },
      ' (si se conoce ',
      { m: "f'" },
      '); cota ',
      { m: '\\frac{h^2}{6} M_3' },
      ' o ',
      { m: '\\frac{h^2}{3} M_3' },
      '.',
    ],
  },
  {
    title: 'Refinar',
    body: [{ m: 'h \\leftarrow h / 2' }, ' y se repite desde el paso 2.'],
  },
  {
    title: 'Parar',
    body: [
      'Cuando el error estimado es ',
      { m: '\\le' },
      ' tolerancia y hay al menos 6 filas, o al llegar al máximo de refinamientos.',
    ],
  },
  {
    title: 'Comprobar',
    body: [
      'Se sustituye ',
      { m: 'x_0' },
      ' en ',
      { m: "f'(x)" },
      ', se verifica que el error real quede por debajo de la cota y se comprueban las identidades con las diferencias.',
    ],
  },
]
