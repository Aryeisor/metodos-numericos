// Contenido teórico de la fórmula de 5 puntos: fórmulas en LaTeX, el ejemplo
// resuelto (datos reales del solver), la escalera de Richardson, la tabla de
// redondeo y los pasos del algoritmo.
//
// La notación es la del Resolver (D^{med,5}, D^{ad,5}, D^{at,5}, cotas
// (h⁴/30)·M₅ y (h⁴/5)·M₅) y el paso a paso se dibuja con los mismos
// componentes que en la página de 3 puntos.
import { formatNumber } from '../../../utils/iterationSteps'
import { latexNumber } from '../../../utils/latexFormulas'
import { identityLatex } from '../formulas'
import { stepDetail as stepDetailOf } from './content'
import { FUNCTION_EXAMPLE as THREE_POINT, V_FORWARD, V_MID, power10 } from './threePointContent'
// Respuestas reales del backend (POST /api/solve/cinco-puntos/), sin recortar:
// «function» es el ejemplo «x·eˣ en x₀ = 2 (Burden y Faires)» y «table», «Tabla
// de x·eˣ (Burden y Faires, tabla + función)». El test
// test_five_point.TheoryExampleTests comprueba que siguen coincidiendo con el
// solver.
import EXAMPLES from './fivePointExample.json'

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const TABLE_EXAMPLE = EXAMPLES.table

const rows = FUNCTION_EXAMPLE.iterations
const FORMULAS = FUNCTION_EXAMPLE.formulas
const byKey = Object.fromEntries(FORMULAS.map((f) => [f.key, f]))
export const MID = byKey.punto_medio_5
export const AHEAD = byKey.extremo_adelante_5
export const BEHIND = byKey.extremo_atras_5
export { FORMULAS }

const exact = FUNCTION_EXAMPLE.exact
const n = (value) => latexNumber(value)

/** Número en potencias de 10 (sólo donde la página lo indica): 1.73 · 10^{-4}. */
export function scientific(value) {
  const [mantissa, exponent] = value.toExponential(2).split('e')
  return `${Number(mantissa)} \\cdot 10^{${Number(exponent)}}`
}

export const tex = {
  // Definición formal (Burden y Faires, con el término exacto del error)
  mid:
    "f'(x_0) = \\frac{f(x_0 - 2h) - 8f(x_0 - h) + 8f(x_0 + h) - f(x_0 + 2h)}{12h} + \\frac{h^4}{30} f^{(5)}(\\xi), \\qquad \\xi \\in (x_0 - 2h,\\, x_0 + 2h)",
  ahead:
    "f'(x_0) = \\frac{-25f(x_0) + 48f(x_0 + h) - 36f(x_0 + 2h) + 16f(x_0 + 3h) - 3f(x_0 + 4h)}{12h} + \\frac{h^4}{5} f^{(5)}(\\xi), \\qquad \\xi \\in (x_0,\\, x_0 + 4h)",
  behind:
    "f'(x_0) = \\frac{25f(x_0) - 48f(x_0 - h) + 36f(x_0 - 2h) - 16f(x_0 - 3h) + 3f(x_0 - 4h)}{12h} + \\frac{h^4}{5} f^{(5)}(\\xi), \\qquad \\xi \\in (x_0 - 4h,\\, x_0)",

  // Interpretación geométrica: signo del error
  midSign: "D^{\\text{med},5} - f'(x_0) \\approx -\\frac{h^4}{30} f^{(5)}(x_0)",
  endSign: "D^{\\text{ad},5} - f'(x_0) \\approx D^{\\text{at},5} - f'(x_0) \\approx -\\frac{h^4}{5} f^{(5)}(x_0)",

  // Derivación por Richardson (punto medio)
  d3h: "D_3(h) = f'(x_0) + \\frac{h^2}{6} f'''(x_0) + \\frac{h^4}{120} f^{(5)}(x_0) + \\cdots",
  d32h: "D_3(2h) = f'(x_0) + \\frac{4h^2}{6} f'''(x_0) + \\frac{16h^4}{120} f^{(5)}(x_0) + \\cdots",
  combination: "\\frac{4D_3(h) - D_3(2h)}{3} = f'(x_0) - \\frac{h^4}{30} f^{(5)}(x_0) + \\cdots",
  algebra: [
    '\\frac{1}{3}\\left[4 \\cdot \\frac{f(x_0 + h) - f(x_0 - h)}{2h} - \\frac{f(x_0 + 2h) - f(x_0 - 2h)}{4h}\\right]',
    '= \\frac{1}{3} \\cdot \\frac{8\\left[f(x_0 + h) - f(x_0 - h)\\right] - \\left[f(x_0 + 2h) - f(x_0 - 2h)\\right]}{4h}',
    '= \\frac{f(x_0 - 2h) - 8f(x_0 - h) + 8f(x_0 + h) - f(x_0 + 2h)}{12h}',
  ],
  coefficient: '\\frac{4 \\cdot \\frac{1}{120} - \\frac{16}{120}}{3} = \\frac{-\\frac{12}{120}}{3} = -\\frac{1}{30}',

  // Coeficientes indeterminados (extremo)
  ansatz: 'D = \\frac{c_0 f_0 + c_1 f_1 + c_2 f_2 + c_3 f_3 + c_4 f_4}{12h}, \\qquad f_j = f(x_0 + j\\,h)',
  conditions:
    '\\sum c_j = 0, \\quad \\sum c_j\\,j = 12, \\quad \\sum c_j\\,j^2 = 0, \\quad \\sum c_j\\,j^3 = 0, \\quad \\sum c_j\\,j^4 = 0',
  solution: 'c = (-25,\\ 48,\\ -36,\\ 16,\\ -3)',
  checks: [
    '-25 + 48 - 36 + 16 - 3 = 0',
    '48 - 72 + 48 - 12 = 12',
    '48 - 144 + 144 - 48 = 0',
    '48 - 288 + 432 - 192 = 0',
    '48 - 576 + 1296 - 768 = 0',
  ],
  fifth: '\\sum c_j\\,j^5 = 48 - 1152 + 3888 - 3072 = -288',
  endError: "\\frac{-288}{12 \\cdot 5!}\\, h^4 f^{(5)} = -\\frac{h^4}{5} f^{(5)}",

  // Error y convergencia
  bounds:
    "|D_{\\text{medio}} - f'(x_0)| \\le \\frac{h^4}{30} M_5, \\qquad |D_{\\text{extremo}} - f'(x_0)| \\le \\frac{h^4}{5} M_5, \\qquad M_5 = \\max |f^{(5)}(x)|",
  totalError: 'E(h) \\approx \\frac{h^4}{30} M_5 + \\frac{3\\varepsilon\\,|f(x_0)|}{2h}',
  optimalH: 'h^{*} = \\left(\\frac{45\\,\\varepsilon\\,|f(x_0)|}{4M_5}\\right)^{1/5}',
}

/* Desarrollo de D − f'(x₀) de cada fórmula (coeficientes verificados). */
export const ERROR_EXPANSION = [
  ['Punto medio de 3 puntos', "+\\frac{h^2}{6} f''' + \\frac{h^4}{120} f^{(5)} + \\cdots"],
  ['Punto medio de 5 puntos', '-\\frac{h^4}{30} f^{(5)} - \\frac{h^6}{252} f^{(7)} - \\cdots'],
  ['Extremo hacia adelante de 5 puntos', '-\\frac{h^4}{5} f^{(5)} - \\frac{h^5}{3} f^{(6)} - \\frac{13h^6}{42} f^{(7)} - \\cdots'],
  ['Extremo hacia atrás de 5 puntos', '-\\frac{h^4}{5} f^{(5)} + \\frac{h^5}{3} f^{(6)} - \\frac{13h^6}{42} f^{(7)} - \\cdots'],
]

// --- Ejemplo de la función (ejemplo 1 del Resolver) ------------------------------

const first = rows[0].extra
const fn = FUNCTION_EXAMPLE.function

/** Props de DifferenceStepDetail para la fila k (como en RefinementTable). */
export const stepDetail = (k, formula) => stepDetailOf(k, formula, FUNCTION_EXAMPLE)

export const example = {
  function: `f(x) = ${fn.latex}`,
  derivative: `f'(x) = ${fn.derivative.latex}`,
  fifth: `f^{(5)}(x) = ${fn.higher_derivatives[5].latex}`,
  exact: `f'(${FUNCTION_EXAMPLE.x0_display.latex}) = 3e^2 = ${n(exact)}`,
  data:
    `x_0 = ${FUNCTION_EXAMPLE.x0_display.latex}, \\quad h_0 = ${first.h.latex}, \\quad ` +
    `\\text{tolerancia} = ${n(FUNCTION_EXAMPLE.tolerance)}`,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
  // 22.165915 < 22.166312 < 22.166996 < 22.167168
  order:
    `${n(first.extremo_adelante_5.D)} < ${n(first.extremo_atras_5.D)} < ` +
    `${n(first.punto_medio_5.D)} < ${n(exact)}`,
}

/* Evaluaciones de la fila 1: los 9 puntos distintos que usan las tres fórmulas. */
export const evaluations = Object.values(
  Object.fromEntries(
    FORMULAS.flatMap((f) => first[f.key].points).map((p) => [p.x, { x: p.display.text, f: formatNumber(p.f) }])
  )
).sort((a, b) => Number(a.x) - Number(b.x))

/* Resumen de una fila: D, error real y cota de cada fórmula. */
export const rowSummary = (k) =>
  FORMULAS.map((f) => ({ key: f.key, name: f.name, symbol: f.symbol_latex, ...rows[k - 1].extra[f.key] }))

export const secondRow = { h: rows[1].extra.h.text, items: rowSummary(2) }

/* Tabla de convergencia: las 6 primeras filas del solver, con el error también
   en potencias de 10 (a 6 decimales casi todos se ven 0). */
export const convergenceRows = rows.slice(0, 6).map((step) => ({
  k: step.iteration,
  h: step.extra.h.text,
  items: [MID, AHEAD, BEHIND].map((f) => {
    const item = step.extra[f.key]
    return { ...item, magnitude: scientific(item.real_error) }
  }),
}))

// --- Richardson ------------------------------------------------------------------

const identity = FUNCTION_EXAMPLE.verification.identities[0]
export const identities = FUNCTION_EXAMPLE.verification.identities.map((item) => ({
  key: item.key,
  latex: identityLatex(item, byKey[item.key]),
}))

/* Escalera de Richardson: D₃ de la identidad (h = 0.2 y 0.1) y de la fila 2 de
   la fórmula de 3 puntos (h = 0.05); D₅ de las filas 1 y 2. El nivel 3 sólo
   se calcula aquí (no es parte del Resolver). */
const D5 = [rows[0].extra.punto_medio_5.D, rows[1].extra.punto_medio_5.D]
const level3 = (16 * D5[1] - D5[0]) / 15
const rung = (D, small = false) => ({ D, error: Math.abs(D - exact), small })
export const ladder = [
  { h: '0.2', levels: [rung(identity.double)] },
  { h: '0.1', levels: [rung(identity.base), rung(D5[0])] },
  { h: '0.05', levels: [rung(THREE_POINT.iterations[1].extra.punto_medio.D), rung(D5[1]), rung(level3, true)] },
]
export const ladderMagnitude = scientific(Math.abs(level3 - exact))

// --- Comparación con las diferencias y la de 3 puntos ----------------------------

const comparison = FUNCTION_EXAMPLE.comparison[0]
export const differences = { lines: FUNCTION_EXAMPLE.comparison.map((line) => line.text) }

const forwardError = comparison.forward.real_error
export const comparisonRows = [
  // `count`, no `points`: los items del solver ya traen `points` (los nodos).
  { name: 'Progresiva', count: 2, ...comparison.forward },
  { name: 'Punto medio de 3 puntos', count: 3, ...comparison.midpoint_3 },
  { name: 'Extremo de 5 puntos (adelante)', count: 5, ...first.extremo_adelante_5 },
  { name: 'Punto medio de 5 puntos', count: 5, ...first.punto_medio_5, best: true },
].map((row) => ({ ...row, times: String(Math.round(forwardError / row.real_error)) }))

/* Errores de la categoría con h = 0.1 (tabla de cierre). */
const three = THREE_POINT.iterations[0].extra
export const categoryErrors = {
  forward: comparison.forward.real_error,
  backward: comparison.backward.real_error,
  mid3: comparison.midpoint_3.real_error,
  ahead3: three.extremo_adelante.real_error,
  behind3: three.extremo_atras.real_error,
  mid5: first.punto_medio_5.real_error,
  ahead5: first.extremo_adelante_5.real_error,
  behind5: first.extremo_atras_5.real_error,
}

/* h necesario para un error real objetivo, refinando h₀ = 0.1 entre 2. La
   progresiva y el medio de 3 puntos se calcularon en Python con doble
   precisión (más filas de las que guarda esta página); el de 5 puntos sale de
   las filas del solver. */
const rowFor = (target) => rows.find((step) => step.extra.punto_medio_5.real_error <= target)
export const efficiency = [
  { target: '\\le 0.0001', forward: ['15', 'h \\approx 0.000006'], mid3: ['6', 'h = 0.003125'], target_value: 0.0001 },
  { target: '\\le 0.000001', forward: ['22', 'h \\approx 0.00000005'], mid3: ['9', 'h = 0.000390625'], target_value: 0.000001 },
].map((item) => {
  const step = rowFor(item.target_value)
  return { ...item, mid5: [String(step.iteration), `h = ${step.extra.h.latex}`] }
})

// --- Redondeo: la «V» de las tres fórmulas --------------------------------------

/* Error real del punto medio de 5 puntos con h = 10⁻¹ … 10⁻¹², calculado en
   Python con doble precisión, como los de la página de 3 puntos (V_FORWARD y
   V_MID). Es sólo ilustrativo. */
const V_MID_5 = [0.000173, 1.72e-8, 3.55e-12, 3.15e-11, 2.31e-10, 7.49e-10, 2.99e-8, 2.7e-7, 1.14e-6, 1.39e-5, 7.75e-5, 0.00206]
const V_POWERS = Array.from({ length: 12 }, (_, i) => i + 1)

export const roundingCurve = {
  iterations: V_POWERS.map((p) => ({ iteration: p })),
  labels: V_POWERS.map((p) => power10(-p)),
  series: [
    { label: 'Error real de la progresiva', values: V_FORWARD, color: '--color-series-1' },
    { label: 'Error real del punto medio de 3 puntos', values: V_MID, color: '--color-series-5' },
    { label: 'Error real del punto medio de 5 puntos', values: V_MID_5, color: '--color-series-6' },
  ],
}

/* Orden de magnitud del error real (10^⌊log₁₀ E⌋) en los h de la tabla. */
const TABLE_POWERS = [1, 2, 3, 4, 5, 6, 8, 10]
const order = (value) => `10^{${Math.floor(Math.log10(value))}}`
export const roundingTable = {
  h: TABLE_POWERS.map((p) => `10^{-${p}}`),
  rows: [
    ['Progresiva', V_FORWARD],
    ['Punto medio de 3 puntos', V_MID],
    ['Punto medio de 5 puntos', V_MID_5],
  ].map(([name, values]) => ({ name, values: TABLE_POWERS.map((p) => order(values[p - 1])) })),
}

// --- Mini-ejemplo de datos (ejemplo 7 del Resolver) ------------------------------

const tableRows = TABLE_EXAMPLE.iterations.map((step) => step.extra)
const atX = (x) => tableRows.find((extra) => extra.x === x)
const at17 = atX(1.7)
const romberg22 = TABLE_EXAMPLE.verification.identities.find((row) => row.x_display.text === '2.2').items[0]
export const tableHighlights = {
  book: formatNumber(atX(2).punto_medio_5.D),
  recommended17: at17.recommended.name.toLowerCase(),
  ahead17: formatNumber(at17.extremo_adelante_5.real_error),
  mid3_17: formatNumber(at17.punto_medio.real_error),
  rounding22: romberg22.rounding_difference ? romberg22 : null,
}

// --- Restricciones y algoritmo --------------------------------------------------

export const PRECAUTIONS = [
  {
    title: 'Quinta derivada continua',
    body: [
      'Para que la cota valga, ',
      { m: 'f' },
      ' debe tener ',
      { m: 'f^{(5)}' },
      ' continua en el intervalo que usa la fórmula. Si ',
      { m: 'f' },
      ' no es tan suave, la fórmula de 5 puntos puede no mejorar a la de 3 puntos.',
    ],
  },
  {
    title: 'Dominio de f',
    body: [
      'Todos los puntos deben estar en el dominio de ',
      { m: 'f' },
      '. El extremo llega hasta ',
      { m: 'x_0 \\pm 4h' },
      ': por ejemplo, ',
      { m: '\\ln x' },
      ' con ',
      { m: 'x_0 = 0.35' },
      ', ',
      { m: 'h = 0.1' },
      ' y el extremo hacia atrás necesita ',
      { m: '\\ln(-0.05)' },
      '. Es el mismo caso que rechaza el Resolver.',
    ],
  },
  {
    title: 'Más datos',
    body: [
      'El punto medio necesita dos datos a cada lado y el extremo, cuatro a un lado. Una tabla debe tener al menos 5 datos, con espaciado uniforme.',
    ],
  },
  {
    title: 'Qué fórmula usar en una tabla',
    body: [
      'Es la regla de la columna «Recomendada»: el punto medio de 5 puntos donde existe; si no, el extremo de 5 puntos; el punto medio de 3 puntos sólo cuando no hay ninguna de 5 (por ejemplo, en el segundo punto de una tabla de 5 datos). En ',
      { m: 'x = 1.7' },
      ' de la tabla de 9 datos, el extremo de 5 puntos tiene error ',
      { m: tableHighlights.ahead17 },
      ' y el punto medio de 3 puntos, ',
      { m: tableHighlights.mid3_17 },
      '.',
    ],
  },
  {
    title: 'Datos con ruido',
    body: [
      'Con un error de hasta ',
      { m: '\\delta' },
      ' en cada dato, el punto medio lo amplifica hasta ',
      { m: '(1 + 8 + 8 + 1)\\delta / (12h) = 1.5\\delta / h' },
      ' y el extremo hasta ',
      { m: '(25 + 48 + 36 + 16 + 3)\\delta / (12h) \\approx 10.67\\delta / h' },
      '. Con ',
      { m: '\\delta = 0.001' },
      ' y ',
      { m: 'h = 0.01' },
      ': hasta 0.15 en el punto medio y 1.07 en el extremo. El extremo de 5 puntos es la fórmula de la categoría más sensible al ruido: con datos poco precisos, una fórmula de menor orden puede dar mejor resultado. Ejemplo real: la tabla del libro (datos a 6 decimales) da ',
      { m: tableHighlights.book },
      ' en ',
      { m: 'x = 2' },
      ', frente a ',
      { m: formatNumber(first.punto_medio_5.D) },
      ' con la función exacta: el redondeo de los datos ya cambia el sexto decimal. Con ',
      { m: 'h = 0.1' },
      ' todavía es pequeño frente al truncamiento (',
      { m: formatNumber(first.punto_medio_5.real_error) },
      '), pero con un ',
      { m: 'h' },
      ' más pequeño pasaría a dominar.',
    ],
  },
  {
    title: 'Ni muy grande ni muy pequeño',
    body: [
      { m: 'h' },
      ' grande aumenta el truncamiento; muy pequeño, el redondeo. Con esta fórmula el redondeo aparece antes (ver la tabla de redondeo).',
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
      { m: 'x_0 \\pm h,\\ x_0 \\pm 2h' },
      '; extremos: ',
      { m: 'x_0,\\ x_0 \\pm h,\\ \\dots,\\ x_0 \\pm 4h' },
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
      { m: '12h' },
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
      { m: '\\frac{h^4}{30} M_5' },
      ' o ',
      { m: '\\frac{h^4}{5} M_5' },
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
      ', se verifica que el error real quede por debajo de la cota, se comprueba la identidad de Richardson (sólo en el punto medio) y se compara con la fórmula de 3 puntos y con las diferencias.',
    ],
  },
]
