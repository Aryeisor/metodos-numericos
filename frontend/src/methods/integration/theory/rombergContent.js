// Contenido teórico de la integración de Romberg: fórmulas en LaTeX,
// glosarios, las tablas que salen de las respuestas reales del solver
// (tabla triangular, errores, razones, ejemplo resuelto) y los pasos de
// restricciones y algoritmo.
//
// La notación es la del Resolver (Rᵢ,ₖ con índices desde 1, columna 1 =
// trapecios, diagonal Rᵢ,ᵢ, error estimado |Rᵢ,ᵢ − Rᵢ₋₁,ᵢ₋₁| y εₐ); las
// fórmulas del método y sus glosarios vienen de ../rombergExplain.js y
// ../rombergGlossary.js.
import { formatNumber } from '../../../utils/iterationSteps'
import { extrapolationLatex } from '../rombergExplain'
// Respuestas reales del backend (POST /api/solve/romberg/): «function» es el
// ejemplo 1 del Resolver (polinomio de Chapra, con su gráfico de segmentos),
// «gauss» el ejemplo 2 (e^(−x²) en [0, 1]) y «sqrt» el ejemplo 5 (√x en
// [0, 1]). Las filas con muchos puntos nuevos guardan sólo los 8 primeros y
// los 8 últimos. El test test_romberg.TheoryExampleTests comprueba que
// siguen coincidiendo.
import EXAMPLES from './rombergExample.json'

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const GAUSS_EXAMPLE = EXAMPLES.gauss
export const SQRT_EXAMPLE = EXAMPLES.sqrt

const rowsOf = (result) => result.iterations.map((step) => step.extra)
const chapraRows = rowsOf(FUNCTION_EXAMPLE)
const gaussRows = rowsOf(GAUSS_EXAMPLE)
const sqrtRows = rowsOf(SQRT_EXAMPLE)
const R = (i, k) => formatNumber(chapraRows[i - 1].values[k - 1])

// --- Fórmulas -----------------------------------------------------------------------

export const tex = {
  // 2. definición formal
  column1: 'R_{i,1} = T\\big(n = 2^{\\,i-1}\\big), \\qquad i = 1, 2, 3, \\dots',
  general: 'R_{i,k} = \\frac{4^{k-1}\\,R_{i,k-1} - R_{i-1,k-1}}{4^{k-1} - 1}, \\qquad k = 2, \\dots, i',
  cases:
    'R_{i,2} = \\frac{4R_{i,1} - R_{i-1,1}}{3}, \\qquad R_{i,3} = \\frac{16R_{i,2} - R_{i-1,2}}{15}, \\qquad R_{i,4} = \\frac{64R_{i,3} - R_{i-1,3}}{63}',
  stop: '\\left|R_{i,i} - R_{i-1,i-1}\\right| \\le \\text{tolerancia}, \\qquad \\varepsilon_a = \\left|\\frac{R_{i,i} - R_{i-1,i-1}}{R_{i,i}}\\right| \\cdot 100\\,\\%',

  // 4.1 Euler-Maclaurin
  euler: 'T(h) = I + c_1h^2 + c_2h^4 + c_3h^6 + \\cdots',

  // 4.2 primer escalón
  step1: [
    'T(h/2) = I + c_1\\frac{h^2}{4} + c_2\\frac{h^4}{16} + \\cdots',
    '4T(h/2) - T(h) = 3I - \\frac{3}{4}c_2h^4 + \\cdots',
    '\\frac{4T(h/2) - T(h)}{3} = I - \\frac{1}{4}c_2h^4 + \\cdots',
  ],

  // 4.3 segundo escalón
  step2: [
    'S(h) = I + d_2h^4 + d_3h^6 + \\cdots, \\qquad S(h/2) = I + d_2\\frac{h^4}{16} + d_3\\frac{h^6}{64} + \\cdots',
    '16S(h/2) - S(h) = 15I - \\frac{3}{4}d_3h^6 + \\cdots',
    '\\frac{16S(h/2) - S(h)}{15} = I - \\frac{1}{20}d_3h^6 + \\cdots',
  ],

  // 4.4 regla general
  halving: '\\left(\\frac{h}{2}\\right)^{2k} = \\frac{h^{2k}}{4^k}',

  // 4.5 pesos
  weights22: 'R_{2,2} = \\frac{1}{6}f(0) + \\frac{2}{3}f\\!\\left(\\tfrac{1}{2}\\right) + \\frac{1}{6}f(1)',
  weights33: 'R_{3,3} = \\frac{7f_0 + 32f_1 + 12f_2 + 32f_3 + 7f_4}{90} = \\frac{2h}{45}\\big(7f_0 + 32f_1 + 12f_2 + 32f_3 + 7f_4\\big),\\quad h = \\tfrac{1}{4}',
  weights44: 'R_{4,4}:\\quad \\frac{(108.5,\\ 512,\\ 176,\\ 512,\\ 218,\\ 512,\\ 176,\\ 512,\\ 108.5)}{2835}',
  newtonCotes9: '\\text{Newton-Cotes, 9 puntos:}\\quad \\frac{(98.9,\\ 588.8,\\ -92.8,\\ 1049.6,\\ -454,\\ \\dots)}{2835}',
}

// --- Glosarios -------------------------------------------------------------------

const g = (symbol, text) => ({ symbol, text })

export const GLOSSARIES = {
  column1: [
    g('R_{i,1}', 'La celda de la fila i en la columna 1: un trapecio.'),
    g('T(n)', 'La regla del trapecio compuesta con n segmentos.'),
    g('n = 2^{\\,i-1}', 'Los segmentos de la fila i: 1, 2, 4, 8, … Cada fila duplica los de la anterior.'),
  ],
  general: [
    g('i', 'La fila: cada una duplica los segmentos (n = 2^(i−1)).'),
    g('k', 'La columna: cada una es un escalón de mejora, que elimina un término más del error.'),
    g('R_{i,k-1}', 'El valor de la misma fila, columna anterior: el más preciso de los dos (usa h más chico).'),
    g('R_{i-1,k-1}', 'El valor de la fila anterior, columna anterior.'),
    g('4^{k-1}', 'Los factores 4, 16, 64, … (para k = 2, 3, 4, …).'),
    g('4^{k-1} - 1', 'El denominador: 3, 15, 63, … Hace que el resultado siga valiendo I (4I − I = 3I, 16I − I = 15I, …).'),
    g('R_{i,i}', 'La diagonal: el valor más refinado de cada fila.'),
  ],
  generalSummary:
    'En resumen: cada celda combina la de su izquierda con la de arriba a la izquierda, dando más peso a la más precisa.',
  cases: [
    g('3,\\ 15,\\ 63', 'Los denominadores de las columnas 2, 3 y 4: 4 − 1, 16 − 1 y 64 − 1.'),
    g('R_{i,2}', 'La columna 2: exactamente Simpson 1/3 con n = 2^(i−1) segmentos.'),
    g('R_{i,3}', 'La columna 3: la regla de Boole.'),
    g('R_{i,4}', 'La columna 4: ya no es una regla de Newton-Cotes (ver «Las columnas como reglas con pesos»).'),
  ],
  stop: [
    g('R_{i,i} - R_{i-1,i-1}', 'Cuánto cambió el mejor valor (la diagonal) respecto a la fila anterior: el error estimado.'),
    g('\\text{tolerancia}', 'El error que se acepta. Si el cambio ya es menor, se considera que el valor dejó de mejorar.'),
    g('\\varepsilon_a', 'El error aproximado de Chapra: el mismo cambio, en porcentaje del valor nuevo. Sólo informa.'),
  ],
  euler: [
    g('T(h)', 'El trapecio compuesto con segmentos de ancho h.'),
    g('I', 'La integral exacta.'),
    g('c_1,\\ c_2,\\ c_3', 'Números que no dependen de h: sólo dependen de f, a y b.'),
    g('h^2,\\ h^4,\\ h^6', 'Sólo potencias pares de h: es lo que hace funcionar a Romberg.'),
  ],
  step1: [
    g('T(h/2)', 'El trapecio con el doble de segmentos (la fila siguiente).'),
    g('\\frac{h^2}{4}', 'Al reducir h a la mitad, h² se divide entre 4.'),
    g('4T(h/2) - T(h)', 'Con el factor 4, el término c₁h² vale lo mismo en los dos y se cancela al restar.'),
    g('3', 'Lo que queda de I: 4I − I = 3I. Por eso se divide entre 3.'),
    g('-\\frac{1}{4}c_2h^4', 'El primer término que queda: el error ya es O(h⁴).'),
  ],
  step2: [
    g('S(h)', 'Un valor de la columna 2 (Simpson): su error empieza en h⁴.'),
    g('d_2,\\ d_3', 'Nuevos números que no dependen de h (salen de los c anteriores).'),
    g('16', 'Porque (h/2)⁴ = h⁴/16: con este factor se cancela el término d₂h⁴.'),
    g('15', 'Lo que queda de I: 16I − I = 15I.'),
    g('-\\frac{1}{20}d_3h^6', 'El primer término que queda: el error ya es O(h⁶).'),
  ],
  halving: [
    g('h^{2k}', 'El término del error que se quiere eliminar.'),
    g('4^k', 'Cuánto se achica ese término al reducir h a la mitad: 4, 16, 64, …'),
  ],
  weights: [
    g('f_0, \\dots, f_4', 'Las alturas de f en los puntos igualmente espaciados de [0, 1].'),
    g('7,\\ 32,\\ 12,\\ 32,\\ 7', 'Los pesos de la regla de Boole: suman 90.'),
    g('\\frac{2h}{45}', 'El factor de la regla de Boole; con h = 1/4 da 1/90.'),
    g('2835', 'El denominador común de los pesos de 9 puntos.'),
  ],
}

// --- Escalones de la derivación con números (ejemplo 1, mismo formato del Resolver) --

const extrapolation = (i, k) => extrapolationLatex(i, chapraRows[i - 1].extrapolations.find((e) => e.k === k))
// R₃,₃ con 8 decimales no cabe en un renglón: se parte después de la sustitución.
const split = (latex) => {
  const parts = latex.split(' = ')
  return [parts.slice(0, 3).join(' = '), `= ${parts.slice(3).join(' = ')}`]
}
export const numericSteps = [[extrapolation(2, 2)], [extrapolation(3, 2)], split(extrapolation(3, 3))]

// --- Lectura por columnas --------------------------------------------------------

export const COLUMN_ROWS = [
  { k: '1', name: 'Trapecio', shape: 'Rectas', order: 'O(h^2)', degree: '\\le 1' },
  { k: '2', name: 'Simpson 1/3', shape: 'Parábolas', order: 'O(h^4)', degree: '\\le 3' },
  { k: '3', name: 'Boole', shape: 'Polinomios de grado 4', order: 'O(h^6)', degree: '\\le 5' },
  { k: 'k \\ge 4', name: 'Nivel k', shape: '— (ya no es Newton-Cotes)', order: 'O(h^{2k})', degree: '\\le 2k - 1' },
]

// Gráfico de segmentos: fila 3 (n = 4) del ejemplo 1, columnas 1 a 3.
export const CHART_ROW = FUNCTION_EXAMPLE.chart_rows.find((r) => r.n === 4)
export const CHART_COLUMNS = [
  { k: 1, label: 'Trapecio (columna 1)', shape: 'Rectas' },
  { k: 2, label: 'Simpson 1/3 (columna 2)', shape: 'Parábolas' },
  { k: 3, label: 'Boole (columna 3)', shape: 'Curvas de grado 4' },
]
export const chartArea = (k) => {
  const row = chapraRows[CHART_ROW.i - 1]
  return `${CHART_COLUMNS[k - 1].shape} (n = 4): área R${CHART_ROW.i},${k} = ${formatNumber(row.values[k - 1])} · Eₜ = ${formatNumber(row.errors[k - 1])}`
}
export const chartCurveLabel = `f(x) · I = ${formatNumber(FUNCTION_EXAMPLE.integral.value)} (exacta)`

// --- Error y convergencia (ejemplo 2, e^(−x²)) -----------------------------------

const SUPER = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }
/** −3.56·10⁻⁴: notación científica con 3 cifras (sólo para la tabla de errores). */
export function sci(value) {
  const [mantissa, exponent] = value.toExponential(2).split('e')
  const power = String(Number(exponent)).replace(/[-\d]/g, (c) => SUPER[c])
  return `${mantissa.replace('-', '−')}·10${power}`
}

const ERROR_ROWS = 5
export const errorTable = gaussRows.slice(0, ERROR_ROWS).map((row) => ({
  i: row.i,
  n: row.n,
  cells: Array.from({ length: ERROR_ROWS }, (_, k) => (k < row.i ? sci(row.errors[k]) : '')),
}))
export const gaussReference = formatNumber(GAUSS_EXAMPLE.integral.value)

/** Razones Eₜ(fila i)/Eₜ(fila i − 1) por columna, filas 1 a 5. */
export const columnRatios = [1, 2, 3].map((k) => ({
  k,
  target: ['1/4', '1/16', '1/64'][k - 1],
  values: gaussRows
    .slice(k, ERROR_ROWS)
    .map((row, idx) => (row.errors[k - 1] / gaussRows[k - 1 + idx].errors[k - 1]).toFixed(4)),
}))

// La excepción honesta: en la fila 4, R₄,₃ es mejor que la diagonal.
export const row4 = { r43: sci(Math.abs(gaussRows[3].errors[2])), r44: sci(Math.abs(gaussRows[3].errors[3])) }

// Costo para |Eₜ| ≤ 0.000001 (comparación del Resolver; ejemplos 1 a 5).
export const COST_ROWS = [
  { label: 'Chapra', m: null, romberg: '5 (fila 3)', trapezoid: '2049', simpson: '65' },
  { label: null, m: 'e^{-x^2} \\text{ en } [0, 1]', romberg: '9 (fila 4)', trapezoid: '257', simpson: '17' },
  { label: null, m: '\\sin x \\text{ en } [0, \\pi]', romberg: '17 (fila 5)', trapezoid: '2049', simpson: '65' },
  { label: null, m: 'x^5 \\text{ en } [0, 2]', romberg: '5 (fila 3)', trapezoid: '8193', simpson: '129' },
  { label: null, m: '\\sqrt{x} \\text{ en } [0, 1]', romberg: '2049 (fila 12)', trapezoid: '4097', simpson: '2049' },
]

// √x: razones del trapecio (filas 5 a 10) y la diagonal.
const sqrtTrap = sqrtRows.map((row) => row.errors[0])
export const sqrt = {
  ratios: sqrtTrap.slice(4, 9).map((e, idx) => (sqrtTrap[idx + 5] / e).toFixed(3)),
  diagonal: sqrtRows.slice(0, 6).map((row) => formatNumber(row.best)),
  warning: SQRT_EXAMPLE.warnings[0],
  rows: SQRT_EXAMPLE.iterations_used,
  cost: SQRT_EXAMPLE.cost.text,
}

// --- Ejemplo resuelto (ejemplo 1) ---------------------------------------------------

export const example = {
  fn: `f(x) = ${FUNCTION_EXAMPLE.function.latex}`,
  integral: `I = \\int_0^{0.8} f(x)\\,dx = \\frac{3076}{1875} = ${formatNumber(FUNCTION_EXAMPLE.integral.value)}`,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
  evaluations: FUNCTION_EXAMPLE.evaluations,
  R,
  estimated: (i) => formatNumber(chapraRows[i - 1].estimated_error),
  approx: (i) => `${formatNumber(chapraRows[i - 1].approx_error)} %`,
  rows: [1, 2, 3].map((i) => ({ row: chapraRows[i - 1], previous: i > 1 ? chapraRows[i - 2] : null })),
}

// --- Restricciones y algoritmo --------------------------------------------------

export const PRECAUTIONS = [
  {
    title: 'f debe ser suave',
    body: [
      { m: 'f' },
      ' debe tener muchas derivadas continuas en ',
      { m: '[a, b]' },
      '. Si no las tiene, Romberg converge, pero sin ventaja. Ejemplos: ',
      { m: '\\sqrt{x}' },
      ' en 0, ',
      { m: '|x - c|' },
      ' y las funciones con saltos.',
    ],
  },
  {
    title: 'Las filas duplican el costo',
    body: [
      'Cada fila nueva evalúa tantos puntos nuevos como todas las anteriores juntas. La fila 15 ya son 16 385 puntos (',
      { m: '2^{14} + 1' },
      ').',
    ],
  },
  {
    title: 'Datos tabulados',
    body: [
      'Sólo funciona con ',
      { m: '2^m + 1' },
      ' puntos igualmente espaciados (3, 5, 9, 17 o 33): cada fila necesita el doble de segmentos que la anterior.',
    ],
  },
  {
    title: 'Dominio y singularidades',
    body: [
      'Igual que en el trapecio: si ',
      { m: 'f' },
      ' no está definida o es infinita en algún punto de ',
      { m: '[a, b]' },
      ' (por ejemplo ',
      { m: '1/x' },
      ' con ',
      { m: 'a = 0' },
      '), no se puede aplicar. El Resolver lo detecta y lo avisa.',
    ],
  },
  {
    title: 'Mínimo de 6 filas',
    body: [
      'Es un requisito del curso, no del método. En muchos ejemplos el resultado ya era exacto en la fila 3.',
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
    body: [{ m: 'f(x)' }, ', ', { m: 'a' }, ', ', { m: 'b' }, ', la tolerancia y el máximo de filas.'],
  },
  {
    title: 'Fila 1',
    body: [{ m: 'R_{1,1}' }, ' es el trapecio simple: ', { m: 'R_{1,1} = (b - a)\\,\\frac{f(a) + f(b)}{2}' }, '.'],
  },
  {
    title: 'Nueva fila i',
    body: [
      { m: 'R_{i,1}' },
      ' con la recurrencia del trapecio: ',
      { m: 'R_{i,1} = \\frac{R_{i-1,1}}{2} + h_i \\sum_{\\text{nuevos}} f(x_j)' },
      ' (sólo se evalúan los puntos nuevos).',
    ],
  },
  {
    title: 'Escalones',
    body: [
      'Para ',
      { m: 'k = 2' },
      ' hasta ',
      { m: 'i' },
      ': ',
      { m: 'R_{i,k} = \\frac{4^{k-1}R_{i,k-1} - R_{i-1,k-1}}{4^{k-1} - 1}' },
      '.',
    ],
  },
  {
    title: 'Error estimado',
    body: [{ m: '|R_{i,i} - R_{i-1,i-1}|' }, ' y ', { m: '\\varepsilon_a' }, '.'],
  },
  {
    title: 'Parar o seguir',
    body: [
      'Se para cuando el error estimado es ',
      { m: '\\le' },
      ' tolerancia y hay al menos 6 filas (o al llegar al máximo de filas); si no, se vuelve al paso 3.',
    ],
  },
  {
    title: 'Comprobar',
    body: [
      'La integral con la antiderivada; las identidades (columna 1 = trapecio, columna 2 = Simpson); y la comparación de costo con el trapecio y Simpson.',
    ],
  },
]
