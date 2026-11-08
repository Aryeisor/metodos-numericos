// Contenido teórico del método del trapecio: fórmulas en LaTeX, glosarios,
// las tablas que salen de las respuestas reales del solver (convergencia,
// Richardson, ejemplo resuelto) y los pasos de restricciones y algoritmo.
//
// La notación es la del Resolver (T, Eₜ = I − T, εₜ, Eₐ, f̄'', M₂) y los
// glosarios comunes vienen de ../glossary.js.
import { formatNumber } from '../../../utils/iterationSteps'
import { latexNumber } from '../../../utils/latexFormulas'
import { APPROX_GLOSSARY, BOUND_GLOSSARY, COMPOSITE_GLOSSARY } from '../glossary'
// Respuestas reales del backend (POST /api/solve/trapecio/): «function» es el
// ejemplo 1 del Resolver (polinomio de Chapra) y «table», el ejemplo 8
// (segmentos desiguales). Las filas con muchos puntos nuevos guardan sólo los
// 8 primeros y los 8 últimos, como hace el solver con más de 1024. El test
// test_trapezoid.TheoryExampleTests comprueba que siguen coincidiendo.
import EXAMPLES from './trapezoidExample.json'

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const TABLE_EXAMPLE = EXAMPLES.table

const rows = FUNCTION_EXAMPLE.iterations.map((step) => step.extra)
const I = FUNCTION_EXAMPLE.integral.value
const n = (value) => latexNumber(value)

// --- Funciones de las figuras (sólo ilustrativas) ---------------------------------

export const chapra = (x) => 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5
export const CHAPRA_EXACT = I
export const square = (x) => x * x

/** Trapecio compuesto con n segmentos (figuras y tarjeta de funciones periódicas). */
function trapezoid(f, a, b, count) {
  const h = (b - a) / count
  let sum = (f(a) + f(b)) / 2
  for (let i = 1; i < count; i++) sum += f(a + i * h)
  return h * sum
}

// ∫₀^{2π} e^{cos x} dx = 2π·I₀(1); I₀(1) por su serie Σ (1/4)^k/(k!)².
let besselI0 = 0
for (let k = 0, term = 1; k < 30; k++, term /= 4 * k * k) besselI0 += term
const PERIODIC_EXACT = 2 * Math.PI * besselI0
export const periodic = {
  exact: formatNumber(PERIODIC_EXACT),
  errors: [4, 8, 16].map((count) => ({
    n: count,
    error: formatNumber(Math.abs(trapezoid((x) => Math.exp(Math.cos(x)), 0, 2 * Math.PI, count) - PERIODIC_EXACT)),
  })),
}

// --- Fórmulas -----------------------------------------------------------------------

export const tex = {
  problem: 'I = \\int_a^b f(x)\\,dx',
  ftc: 'I = F(b) - F(a), \\qquad F\'(x) = f(x)',
  quadrature: 'I \\approx \\sum_{i} w_i\\, f(x_i)',
  noise: '\\left|\\,T(\\tilde y) - T(y)\\,\\right| \\le \\sum_i w_i\\,\\delta = \\delta\\,(b - a)',
  simple: 'I = \\int_a^b f(x)\\,dx \\approx (b - a)\\,\\frac{f(a) + f(b)}{2}',
  composite: FUNCTION_EXAMPLE.rule.formula_latex,
  weights: 'w_0 = w_n = \\frac{h}{2}, \\qquad w_1 = w_2 = \\cdots = w_{n-1} = h',
  unequal: 'I \\approx \\sum_{i=0}^{n-1} (x_{i+1} - x_i)\\,\\frac{y_i + y_{i+1}}{2}',

  // 4.1 regla simple
  line: 'p_1(x) = f(a) + \\frac{f(b) - f(a)}{b - a}\\,(x - a)',
  integrateLine: [
    '\\int_a^b p_1(x)\\,dx = f(a)\\int_a^b dx + \\frac{f(b) - f(a)}{b - a}\\int_a^b (x - a)\\,dx',
    '= f(a)(b - a) + \\frac{f(b) - f(a)}{b - a} \\cdot \\frac{(b - a)^2}{2}',
    '= (b - a)\\left[f(a) + \\frac{f(b) - f(a)}{2}\\right] = (b - a)\\,\\frac{f(a) + f(b)}{2}',
  ],

  // 4.2 error de la regla simple
  interpolationError: "f(x) - p_1(x) = \\frac{f''(\\xi_x)}{2}\\,(x - a)(x - b)",
  errorIntegral: "E_t = \\int_a^b \\left[f(x) - p_1(x)\\right] dx = \\int_a^b \\frac{f''(\\xi_x)}{2}\\,(x - a)(x - b)\\,dx",
  meanValue: "= \\frac{f''(\\xi)}{2} \\int_a^b (x - a)(x - b)\\,dx",
  productIntegral: '\\int_a^b (x - a)(x - b)\\,dx = -\\frac{(b - a)^3}{6}',
  simpleError: "E_t = -\\frac{(b - a)^3}{12}\\, f''(\\xi), \\qquad \\xi \\in (a, b)",
  squareCheck: "E_t = I - T = \\frac{8}{3} - 4 = -\\frac{4}{3}, \\qquad -\\frac{2^3}{12} \\cdot 2 = -\\frac{16}{12} = -\\frac{4}{3}\\ \\checkmark",

  // 4.3 error de la regla compuesta
  compositeError: "E_t = -\\frac{h^3}{12}\\sum_{i=1}^{n} f''(\\xi_i) = -\\frac{(b - a)\\,h^2}{12}\\,\\bar{f''}",
  nh: "h^3 \\cdot n = h^2 \\cdot (n\\,h) = (b - a)\\,h^2, \\qquad \\bar{f''} = \\frac{1}{n}\\sum_{i=1}^{n} f''(\\xi_i)",
  meanSecond: "\\bar{f''} \\approx \\frac{1}{b - a}\\int_a^b f''(x)\\,dx = \\frac{f'(b) - f'(a)}{b - a}",
  approx: "E_a = -\\frac{(b - a)\\,h^2}{12}\\,\\bar{f''}",

  // 4.4 Euler-Maclaurin
  eulerMaclaurin:
    "T(h) - I = \\frac{h^2}{12}\\big[f'(b) - f'(a)\\big] - \\frac{h^4}{720}\\big[f'''(b) - f'''(a)\\big] + \\cdots",

  // 4.5 recurrencia
  recurrence: 'T_{2n} = \\frac{T_n}{2} + h_{2n}\\sum_{\\text{nuevos}} f(x_i)',

  // 4.6 Richardson
  richardson: '\\frac{4\\,T_{2n} - T_n}{3}',
  richardsonWhy: [
    'T_n \\approx I + c\\,h^2',
    'T_{2n} \\approx I + c\\left(\\frac{h}{2}\\right)^2 = I + \\frac{c\\,h^2}{4}',
    '4\\,T_{2n} - T_n \\approx 4I + c\\,h^2 - I - c\\,h^2 = 3I',
  ],

  // 5. error y convergencia
  bound: FUNCTION_EXAMPLE.rule.bound_latex,
}

// --- Glosarios -------------------------------------------------------------------

const g = (symbol, text) => ({ symbol, text })

export const GLOSSARIES = {
  problem: [
    g('\\int_a^b', '«La integral de a a b»: acumula los valores de f entre a y b.'),
    g('f(x)', 'La función que se integra (el integrando): la altura de la curva en cada x.'),
    g('dx', 'Indica que la variable de integración es x (un «ancho» muy pequeño).'),
    g('I', 'El resultado: el área con signo. Lo que queda debajo del eje x cuenta como negativo.'),
  ],
  ftc: [
    g('F(x)', 'Una antiderivada de f: una función cuya derivada es f.'),
    g('F(b) - F(a)', 'Se evalúa la antiderivada en los dos límites y se restan los valores.'),
  ],
  quadrature: [
    g('x_i', 'Los nodos: los puntos donde se evalúa la función.'),
    g('w_i', 'Los pesos: cuánto cuenta cada evaluación en la suma.'),
    g('\\sum_i', 'Se suman todas las evaluaciones multiplicadas por su peso.'),
  ],
  quadratureSummary:
    'El trapecio y Simpson son casos particulares de esta forma: usan los mismos nodos igualmente espaciados, con pesos distintos.',
  simple: [
    g('b - a', 'El ancho del trapecio (todo el intervalo).'),
    g('f(a),\\ f(b)', 'Las alturas de la curva en los dos extremos: los dos lados paralelos del trapecio.'),
    g('\\frac{f(a) + f(b)}{2}', 'La altura promedio de los dos lados.'),
  ],
  simpleSummary: 'En resumen: área = ancho × altura promedio.',
  weights: [
    g('w_0,\\ w_n', 'Los extremos pesan h/2: cada uno pertenece a un solo trapecio.'),
    g('w_1, \\dots, w_{n-1}', 'Los puntos interiores pesan h: son compartidos por dos trapecios.'),
  ],
  unequal: [
    g('x_{i+1} - x_i', 'El ancho del segmento i; puede ser distinto en cada segmento.'),
    g('y_i,\\ y_{i+1}', 'Los datos en los extremos del segmento: las alturas del trapecio.'),
    g('\\frac{y_i + y_{i+1}}{2}', 'La altura promedio del segmento.'),
  ],
  simpleError: [
    g('E_t', 'El error verdadero, I − T: lo que le falta (o le sobra) al trapecio.'),
    g('-', "El signo menos: si f'' > 0 (curva convexa), la recta queda por encima y T se pasa, así que Eₜ < 0."),
    g("f''(\\xi)", 'La curvatura de f en algún punto ξ de (a, b). No se sabe cuál es ξ; sólo que existe.'),
    g(
      '(b - a)^3',
      'Al cubo: el error de la recta crece con el cuadrado del ancho, y se acumula a lo largo de todo el ancho.'
    ),
    g('12', 'Sale de multiplicar el 2 del error de interpolación por el 6 de la integral de (x − a)(x − b).'),
  ],
  compositeError: [
    g('\\xi_i', 'Un punto desconocido dentro del segmento i.'),
    g("\\bar{f''}", "El promedio de f'' en los n segmentos."),
    g('h^2', 'El error depende de h²: al duplicar n, el error se divide entre unas 4 veces.'),
  ],
  eulerMaclaurin: [
    g('T(h)', 'El resultado del trapecio con segmentos de ancho h.'),
    g("f'(b) - f'(a)", 'Cuánto cambia la pendiente entre los extremos.'),
    g("f'''(b) - f'''(a)", 'Lo mismo con la tercera derivada; acompaña al término en h⁴.'),
    g('\\cdots', 'Siguen términos en h⁶, h⁸, …: sólo potencias pares de h.'),
  ],
  recurrence: [
    g('T_n', 'El resultado con n trapecios (la fila anterior).'),
    g('\\frac{T_n}{2}', 'Reaprovecha todos los puntos ya evaluados: al reducir h a la mitad, su peso se reduce a la mitad.'),
    g('h_{2n}', 'El nuevo ancho, la mitad del anterior.'),
    g('\\sum_{\\text{nuevos}}', 'La suma de f sólo en los puntos nuevos (el centro de cada trapecio anterior).'),
  ],
  richardson: [
    g('T_n,\\ T_{2n}', 'Dos resultados del trapecio, con n y con 2n segmentos.'),
    g('4', 'Porque el error con 2n es unas 4 veces menor (h² se divide entre 4).'),
    g('3', 'Para que el resultado siga siendo I: 4I − I = 3I.'),
  ],
}

export { APPROX_GLOSSARY, BOUND_GLOSSARY, COMPOSITE_GLOSSARY }

// --- Datos del ejemplo de Chapra (ejemplo 1 del Resolver) ----------------------------

const ms = FUNCTION_EXAMPLE.mean_second
const row = (k) => rows[k - 1]

export const example = {
  fn: `f(x) = ${FUNCTION_EXAMPLE.function.latex}`,
  integral: `I = \\int_0^{0.8} f(x)\\,dx = \\frac{3076}{1875} = ${n(I)}`,
  fa: formatNumber(ms.fa),
  fb: formatNumber(ms.fb),
  meanSecond: formatNumber(ms.value),
  M2: formatNumber(FUNCTION_EXAMPLE.M2.value),
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
  lastN: rows.at(-1).n,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  rows: [1, 2, 3].map((k) => ({ k, row: row(k), previous: k > 1 ? row(k - 1) : null })),
  T: (k) => formatNumber(row(k).T),
  Et: (k) => formatNumber(row(k).true_error),
  Ea: (k) => formatNumber(row(k).approx_error),
  bound: (k) => formatNumber(row(k).bound),
  relative: (k) => `${formatNumber(row(k).relative_error)} %`,
}

/* f̄'' y Eₐ con los valores del solver (sección 4.3). */
export const approxCheck = {
  mean: `\\bar{f''} = \\frac{${n(ms.fb)} - ${n(ms.fa)}}{0.8} = ${n(ms.value)}`,
  n1: `E_a = -\\frac{0.8^3}{12}\\,(${n(ms.value)}) = ${n(row(1).approx_error)} \\quad\\text{frente a}\\quad E_t = ${n(row(1).true_error)}`,
  n2: `E_a = ${n(row(2).approx_error)} \\quad\\text{frente a}\\quad E_t = ${n(row(2).true_error)}`,
}

/* Comprobación de Euler-Maclaurin con n = 8 (fila 4). */
export const eulerCheck = {
  derivatives: "f'(0.8) - f'(0) = -48, \\qquad f'''(0.8) - f'''(0) = 2130 - 4050 = -1920",
  terms: '\\frac{0.01}{12}(-48) - \\frac{0.0001}{720}(-1920) = -0.04 + 0.000267 = -0.039733',
  solver: `T - I = ${n(row(4).T)} - ${n(I)} = ${n(-row(4).true_error)}`,
}

/* Recurrencia T₂ (sección 4.5), con f(0.4) de la fila 2 del solver. */
const f04 = row(2).step.points[0]
export const recurrenceCheck = `T_2 = \\frac{${n(row(1).T)}}{2} + 0.4 \\cdot f(0.4) = ${n(row(1).T / 2)} + 0.4 \\cdot ${f04.f_display} = ${n(row(2).T)}`

/* Escalera de Richardson con los T del solver. */
export const richardsonRows = rows.slice(0, 6).slice(1).map((current, i) => {
  const previous = rows[i]
  const value = (4 * current.T - previous.T) / 3
  return { label: `${previous.n} → ${current.n}`, value, error: Math.abs(value - I) }
})
export const simpsonN2 = formatNumber(richardsonRows[0].value)

/* Tabla de convergencia: filas 1 a 6 del solver. */
export const convergenceRows = rows.slice(0, 6).map((r, i) => ({
  k: i + 1,
  n: r.n,
  h: r.h.text,
  T: r.T,
  Et: r.true_error,
  relative: r.relative_error,
  ratio: r.ratio,
}))

/* Mini-ejemplo de segmentos desiguales (ejemplo 8). */
const tableFinal = TABLE_EXAMPLE.verification.final
export const tableExample = {
  segments: TABLE_EXAMPLE.iterations.length,
  total: formatNumber(TABLE_EXAMPLE.total),
  Et: formatNumber(tableFinal.true_error),
  relative: `${formatNumber(tableFinal.relative_error)} %`,
  row: TABLE_EXAMPLE.chart_rows[0],
  label: `Trapecios de los datos: área T = ${formatNumber(TABLE_EXAMPLE.total)}`,
  curveLabel: `f(x) · I = ${formatNumber(TABLE_EXAMPLE.integral.value)} (exacta)`,
}

// --- Restricciones y algoritmo --------------------------------------------------

export const PRECAUTIONS = [
  {
    title: 'f definida y finita en [a, b]',
    body: [
      'Una singularidad en un extremo (',
      { m: '1/\\sqrt{x}' },
      ' en ',
      { m: '[0, 1]' },
      ') o en el interior (',
      { m: '1/(x - 1)' },
      ' en ',
      { m: '[0, 2]' },
      ') hace que la regla no se pueda aplicar tal cual: alguna altura sería infinita. El Resolver lo detecta y lo avisa.',
    ],
  },
  {
    title: 'Segunda derivada continua',
    body: [
      'Para que la cota valga, ',
      { m: 'f' },
      ' debe tener ',
      { m: "f''" },
      ' continua en ',
      { m: '[a, b]' },
      '. Si no la tiene (por ejemplo ',
      { m: '\\sqrt{x}' },
      ' en ',
      { m: '[0, 1]' },
      '), el trapecio puede converger, pero más lento que ',
      { m: 'O(h^2)' },
      '.',
    ],
  },
  {
    title: 'Convergencia lenta',
    body: [
      'Para muchas cifras se necesitan muchos segmentos. En el ejemplo de Chapra hacen falta ',
      { m: `n = ${rows.at(-1).n}` },
      ` para que el error estimado baje de ${formatNumber(FUNCTION_EXAMPLE.tolerance)}. Simpson y Romberg lo logran con muchísimas menos evaluaciones.`,
    ],
  },
  {
    title: 'Funciones que oscilan mucho',
    body: [
      { m: 'h' },
      ' debe ser mucho menor que el período de la oscilación; si no, los trapecios «saltan» las subidas y bajadas de la curva.',
    ],
  },
  {
    title: 'Exacta o valor de referencia',
    body: [
      'Cuando la antiderivada no es elemental (por ejemplo ',
      { m: 'e^{-x^2}' },
      '), el sistema compara con un valor numérico de alta precisión en lugar de ',
      { m: 'F(b) - F(a)' },
      '.',
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
      ', los límites ',
      { m: 'a' },
      ' y ',
      { m: 'b' },
      ', los segmentos iniciales ',
      { m: 'n_0' },
      ', la tolerancia y el máximo de refinamientos.',
    ],
  },
  {
    title: 'Fila 1',
    body: [
      'Se calcula ',
      { m: 'h = (b - a)/n_0' },
      ' y los puntos ',
      { m: 'x_i = a + i\\,h' },
      '; se evalúa ',
      { m: 'f' },
      ' en ellos, se aplican los pesos ',
      { m: '1, 2, \\dots, 2, 1' },
      ' y la suma se multiplica por ',
      { m: 'h/2' },
      '.',
    ],
  },
  {
    title: 'Errores',
    body: [
      { m: 'E_t' },
      ' y ',
      { m: '\\varepsilon_t' },
      ' (si hay valor exacto); ',
      { m: 'E_a' },
      ' con ',
      { m: "f'(a)" },
      ' y ',
      { m: "f'(b)" },
      '; la cota con ',
      { m: 'M_2' },
      '.',
    ],
  },
  {
    title: 'Refinar',
    body: [
      'Se duplica ',
      { m: 'n' },
      ' y se usa la recurrencia: sólo se evalúan los puntos nuevos.',
    ],
  },
  {
    title: 'Error estimado',
    body: [{ m: '|T_k - T_{k-1}|' }, ' y la razón entre errores verdaderos consecutivos.'],
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
      'Antiderivada paso a paso, ',
      { m: "F' = f" },
      ', ',
      { m: 'F(b) - F(a)' },
      ' y comparación con ',
      { m: 'T' },
      '.',
    ],
  },
]
