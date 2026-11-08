// Contenido teórico del método de Simpson (reglas 1/3 y 3/8): fórmulas en
// LaTeX, glosarios, las tablas que salen de las respuestas reales del solver
// (convergencia, ejemplo resuelto, combinación) y los pasos de restricciones y
// algoritmo.
//
// La notación es la del Resolver (S, Eₜ = I − S, εₜ, Eₐ, f̄⁽⁴⁾, M₄); los
// glosarios comunes vienen de ../glossary.js y ../simpsonGlossary.js.
import { formatNumber } from '../../../utils/iterationSteps'
import { latexNumber } from '../../../utils/latexFormulas'
import { COMPOSITE_GLOSSARY } from '../glossary'
import { identityLatex } from '../simpsonExplain'
import { simpsonApproxGlossary, simpsonBoundGlossary } from '../simpsonGlossary'
// Respuestas reales del backend (POST /api/solve/simpson/): «function» es el
// ejemplo 1 del Resolver (polinomio de Chapra, las dos reglas) y «table», el
// ejemplo 8 (n = 5: combinación 1/3 + 3/8). Sin `chart_rows` (la figura se
// calcula aquí) y con las filas de muchos puntos recortadas a 16. El test
// test_simpson.TheoryExampleTests comprueba que siguen coincidiendo.
import EXAMPLES from './simpsonExample.json'

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const TABLE_EXAMPLE = EXAMPLES.table

const n = (value) => latexNumber(value)
const I = FUNCTION_EXAMPLE.integral.value
export const CHAPRA_EXACT = I

export const BLOCK_13 = FUNCTION_EXAMPLE.rules.find((b) => b.rule.key === 'simpson13')
export const BLOCK_38 = FUNCTION_EXAMPLE.rules.find((b) => b.rule.key === 'simpson38')
const row13 = (k) => BLOCK_13.rows[k - 1]
const row38 = (k) => BLOCK_38.rows[k - 1]

// --- Fórmulas -----------------------------------------------------------------------

export const tex = {
  // 2. definición formal
  simple13:
    'I \\approx \\frac{h}{3}\\big[f(x_0) + 4f(x_1) + f(x_2)\\big] = (b - a)\\,\\frac{f(x_0) + 4f(x_1) + f(x_2)}{6}',
  composite13:
    'I \\approx \\frac{h}{3}\\Big[f(x_0) + 4\\sum_{i\\ \\text{impar}} f(x_i) + 2\\sum_{i\\ \\text{par interior}} f(x_i) + f(x_n)\\Big]',
  simple38:
    'I \\approx \\frac{3h}{8}\\big[f(x_0) + 3f(x_1) + 3f(x_2) + f(x_3)\\big] = (b - a)\\,\\frac{f(x_0) + 3f(x_1) + 3f(x_2) + f(x_3)}{8}',
  composite38: BLOCK_38.rule.formula_latex,
  weights38: '\\frac{3h}{8}\\,\\big(1,\\ 3,\\ 3,\\ 2,\\ 3,\\ 3,\\ 2,\\ \\dots,\\ 2,\\ 3,\\ 3,\\ 1\\big)',
  combination:
    'I \\approx \\underbrace{S_{1/3}\\big[x_0,\\ x_{n-3}\\big]}_{n - 3\\ \\text{segmentos (par)}} + \\underbrace{S_{3/8}\\big[x_{n-3},\\ x_n\\big]}_{3\\ \\text{segmentos}}',

  // 4.1 pesos por Lagrange
  lagrange:
    'p_2(x) = f_0\\,\\frac{x(x - h)}{2h^2} + f_1\\,\\frac{(h - x)(h + x)}{h^2} + f_2\\,\\frac{x(x + h)}{2h^2}',
  lagrangeIntegrals:
    '\\int_{-h}^{h}\\frac{x(x - h)}{2h^2}\\,dx = \\frac{h}{3}, \\qquad \\int_{-h}^{h}\\frac{h^2 - x^2}{h^2}\\,dx = \\frac{4h}{3}, \\qquad \\int_{-h}^{h}\\frac{x(x + h)}{2h^2}\\,dx = \\frac{h}{3}',
  lagrangeFirst: [
    '\\int_{-h}^{h}\\frac{x(x - h)}{2h^2}\\,dx = \\frac{1}{2h^2}\\int_{-h}^{h}\\left(x^2 - h\\,x\\right)dx',
    '= \\frac{1}{2h^2}\\left[\\frac{x^3}{3} - \\frac{h\\,x^2}{2}\\right]_{-h}^{h} = \\frac{1}{2h^2}\\cdot\\frac{2h^3}{3} = \\frac{h}{3}',
  ],
  lagrangeResult:
    '\\int_{-h}^{h} p_2(x)\\,dx = \\frac{h}{3}\\,f_0 + \\frac{4h}{3}\\,f_1 + \\frac{h}{3}\\,f_2 = \\frac{h}{3}\\big(f_0 + 4f_1 + f_2\\big)',
  lagrangeCheck: 'h = 1:\\quad w_0 = \\frac{1}{3},\\quad w_1 = \\frac{4}{3},\\quad w_2 = \\frac{1}{3}\\ \\checkmark',
  lagrange38: 'h = 1:\\quad w = \\frac{3}{8},\\ \\frac{9}{8},\\ \\frac{9}{8},\\ \\frac{3}{8} = \\frac{3h}{8}\\,(1,\\ 3,\\ 3,\\ 1)\\ \\checkmark',

  // 4.2 punto medio y trapecio
  midpoint: 'M = (b - a)\\,f\\!\\left(\\frac{a + b}{2}\\right)',
  midTrap: 'S = \\frac{2M + T}{3}',
  midTrapCheck:
    'M = 0.8 \\cdot f(0.4) = 0.8 \\cdot 2.456 = 1.9648, \\qquad T = 0.1728, \\qquad \\frac{2(1.9648) + 0.1728}{3} = 1.367467\\ \\checkmark',
  midTrapWhy: [
    'E_M \\approx -\\tfrac{1}{2}\\,E_T',
    '2(I - M) + (I - T) \\approx -E_T + E_T = 0 \\quad\\Longrightarrow\\quad I \\approx \\frac{2M + T}{3}',
  ],

  // 4.3 exacta para cúbicas
  cubicSymmetry: '\\int_{-h}^{h} x^3\\,dx = 0, \\qquad \\frac{h}{3}\\Big[(-h)^3 + 4 \\cdot 0^3 + h^3\\Big] = 0',
  cubicCheck: '\\int_0^2 x^3\\,dx = 4, \\qquad \\frac{2}{6}\\big(0 + 4 \\cdot 1 + 8\\big) = 4\\ \\checkmark',

  // 4.4 error
  simpleErrors:
    'E_t = -\\frac{(b - a)^5}{2880}\\,f^{(4)}(\\xi)\\quad(1/3), \\qquad E_t = -\\frac{(b - a)^5}{6480}\\,f^{(4)}(\\xi)\\quad(3/8)',
  compositeErrors:
    'E_t = -\\frac{(b - a)\\,h^4}{180}\\,\\bar{f}^{(4)}\\quad(1/3), \\qquad E_t = -\\frac{(b - a)\\,h^4}{80}\\,\\bar{f}^{(4)}\\quad(3/8)',
  compositeSteps13: [
    '\\text{una parábola: ancho } 2h \\;\\Rightarrow\\; \\frac{(2h)^5}{2880} = \\frac{32\\,h^5}{2880} = \\frac{h^5}{90}',
    '\\frac{n}{2}\\ \\text{parábolas:}\\quad \\frac{n}{2}\\cdot\\frac{h^5}{90} = \\frac{n\\,h \\cdot h^4}{180} = \\frac{(b - a)\\,h^4}{180}',
  ],
  compositeSteps38: [
    '\\text{una cúbica: ancho } 3h \\;\\Rightarrow\\; \\frac{(3h)^5}{6480} = \\frac{243\\,h^5}{6480} = \\frac{3\\,h^5}{80}',
    '\\frac{n}{3}\\ \\text{cúbicas:}\\quad \\frac{n}{3}\\cdot\\frac{3\\,h^5}{80} = \\frac{n\\,h \\cdot h^4}{80} = \\frac{(b - a)\\,h^4}{80}',
  ],
  meanFourth: "\\bar{f}^{(4)} \\approx \\frac{1}{b - a}\\int_a^b f^{(4)}(x)\\,dx = \\frac{f'''(b) - f'''(a)}{b - a}",
  approx13: BLOCK_13.rule.approx_latex,
  quarticCheck13:
    '\\int_{-1}^{1} x^4\\,dx = \\frac{2}{5}, \\quad S = \\frac{1}{3}(1 + 0 + 1) = \\frac{2}{3}, \\quad E_t = \\frac{2}{5} - \\frac{2}{3} = -\\frac{4}{15} = -\\frac{2^5}{2880}\\cdot 24\\ \\checkmark',
  quarticCheck38:
    '\\int_0^3 x^4\\,dx = 48.6, \\quad S = \\frac{3}{8}(0 + 3 + 48 + 81) = 49.5, \\quad E_t = -0.9 = -\\frac{3^5}{6480}\\cdot 24\\ \\checkmark',

  // 4.6 Richardson
  richardson: 'S_{n} = \\frac{4\\,T_{n} - T_{n/2}}{3}',
  richardsonWhy: [
    'T_{n/2} \\approx I + c\\,(2h)^2 = I + 4c\\,h^2',
    'T_{n} \\approx I + c\\,h^2',
    '4\\,T_{n} - T_{n/2} \\approx 4I + 4c\\,h^2 - I - 4c\\,h^2 = 3I',
  ],
  richardsonCheck: identityLatex(row13(1).identity),

  // 5. cotas
  bounds:
    '|E_t| \\le \\frac{(b - a)\\,h^4}{180}\\,M_4\\ (1/3), \\qquad |E_t| \\le \\frac{(b - a)\\,h^4}{80}\\,M_4\\ (3/8), \\qquad M_4 = \\max_{[a,\\, b]}\\left|f^{(4)}(x)\\right|',
}

// --- Glosarios -------------------------------------------------------------------

const g = (symbol, text) => ({ symbol, text })
const common = (symbol) => COMPOSITE_GLOSSARY.items.find((item) => item.symbol === symbol)

export const GLOSSARIES = {
  simple13: [
    g('h', 'El ancho de cada uno de los 2 segmentos: h = (b − a)/2.'),
    g('x_0,\\ x_1,\\ x_2', 'Los 3 puntos: x₀ = a, x₁ = el punto medio y x₂ = b.'),
    g('f(x_0),\\ f(x_1),\\ f(x_2)', 'Las alturas de la curva en esos puntos: por ellas pasa la parábola.'),
    g('1,\\ 4,\\ 1', 'Los pesos: el punto del medio cuenta 4 veces y los extremos, 1 vez cada uno.'),
    g('\\frac{h}{3}', 'El factor de la regla. De aquí sale el nombre «Simpson 1/3».'),
    g('\\frac{\\cdots}{6}', 'Los pesos suman 1 + 4 + 1 = 6: dividir entre 6 da una altura promedio ponderada.'),
  ],
  simple13Summary:
    'En resumen: área = ancho × altura promedio ponderada, igual que el trapecio, pero con el punto del medio pesando 4 de 6.',
  composite13: [
    common('I'),
    g('\\approx', '«Aproximadamente igual»: Simpson da una aproximación, no el valor exacto.'),
    g('n', 'El número de segmentos; debe ser par porque cada parábola ocupa 2 segmentos.'),
    g('h', 'El ancho de cada segmento: h = (b − a)/n.'),
    common('x_i'),
    g('f(x_0),\\ f(x_n)', 'Los extremos pesan 1: cada uno pertenece a una sola parábola.'),
    g('\\sum_{i\\ \\text{impar}}', 'La suma de las alturas en x₁, x₃, x₅, …: el punto del medio de cada parábola. Pesan 4.'),
    g(
      '\\sum_{i\\ \\text{par interior}}',
      'La suma en x₂, x₄, …, xₙ₋₂: donde termina una parábola y empieza la siguiente. Pesan 2 porque se cuentan en las dos (1 + 1).'
    ),
    g('\\frac{h}{3}', 'El mismo factor de la regla simple, aplicado a cada parábola.'),
  ],
  composite13Summary: 'En resumen: se suman las áreas bajo las n/2 parábolas.',
  simple38: [
    g('h', 'El ancho de cada uno de los 3 segmentos: h = (b − a)/3.'),
    g('x_0, \\dots, x_3', 'Los 4 puntos igualmente espaciados, de x₀ = a a x₃ = b.'),
    g('1,\\ 3,\\ 3,\\ 1', 'Los pesos: los dos puntos del medio cuentan 3 veces y los extremos, 1 vez.'),
    g('\\frac{3h}{8}', 'El factor de la regla. De aquí sale el nombre «Simpson 3/8».'),
    g('\\frac{\\cdots}{8}', 'Los pesos suman 1 + 3 + 3 + 1 = 8: otra vez, una altura promedio ponderada.'),
  ],
  composite38: [
    g('n', 'El número de segmentos; debe ser múltiplo de 3 porque cada cúbica ocupa 3 segmentos.'),
    g('\\sum_{i\\ \\text{no múltiplo de 3}}', 'Los dos puntos del medio de cada cúbica (x₁, x₂, x₄, x₅, …). Pesan 3.'),
    g('\\sum_{i\\ \\text{múltiplo de 3}}', 'Los puntos de unión entre dos cúbicas (x₃, x₆, …). Pesan 2 = 1 + 1.'),
    g('f(x_0),\\ f(x_n)', 'Los extremos pesan 1: pertenecen a una sola cúbica.'),
  ],
  combination: [
    g('S_{1/3}', 'Simpson 1/3 en los primeros n − 3 segmentos (un número par).'),
    g('S_{3/8}', 'Simpson 3/8 en los últimos 3 segmentos.'),
    g('x_{n-3}', 'El punto de unión: pertenece a las dos partes, así que su peso es 1 + 1.'),
  ],
  lagrange: [
    g('f_0,\\ f_1,\\ f_2', 'Las alturas f(−h), f(0) y f(h) de los tres puntos.'),
    g('\\frac{x(x - h)}{2h^2}', 'Vale 1 en x = −h y 0 en x = 0 y en x = h: «enciende» sólo a f₀.'),
    g('\\frac{(h - x)(h + x)}{h^2}', 'Vale 1 en x = 0 y 0 en x = ±h: «enciende» sólo a f₁.'),
    g('\\frac{x(x + h)}{2h^2}', 'Vale 1 en x = h y 0 en los otros dos: «enciende» sólo a f₂.'),
    g('p_2(x)', 'La parábola: en cada punto, dos fracciones valen 0 y una vale 1, así que pasa exactamente por los 3 puntos.'),
  ],
  midTrap: [
    g('M', 'La regla del punto medio: un rectángulo de altura f en el centro del intervalo.'),
    g('T', 'La regla del trapecio simple en el mismo intervalo.'),
    g('2,\\ 1', 'El error de M es la mitad del de T y de signo opuesto: con estos pesos los dos errores se cancelan.'),
    g('3', 'Para que el resultado siga siendo I: 2I + I = 3I.'),
  ],
  simpleErrors: [
    g('E_t', 'El error verdadero, I − S: lo que le falta (o le sobra) a Simpson.'),
    g('f^{(4)}(\\xi)', 'La cuarta derivada en algún punto ξ de (a, b). Para polinomios de grado ≤ 3 vale 0 y no hay error.'),
    g('(b - a)^5', 'A la quinta: al reducir el ancho a la mitad, el error de una sola pieza se divide entre 32.'),
    g('2880,\\ 6480', 'Salen de integrar el error de interpolación; 3/8 tiene la constante menor porque usa un punto más.'),
  ],
  compositeErrors: [
    g('\\bar{f}^{(4)}', 'El promedio de f⁽⁴⁾ en las piezas.'),
    g('h^4', 'El error es O(h⁴): al duplicar n, se divide entre unas 16 veces.'),
    g('180,\\ 80', 'Salen de sumar los errores de las n/2 parábolas (180) o de las n/3 cúbicas (80).'),
  ],
  richardson: [
    g('T_n,\\ T_{n/2}', 'Dos resultados del trapecio: con n segmentos y con la mitad.'),
    g('4', 'Porque el error de T_n es unas 4 veces menor que el de T_(n/2) (h² se divide entre 4).'),
    g('3', 'Para que el resultado siga siendo I: 4I − I = 3I.'),
    g('S_n', 'El resultado es exactamente Simpson 1/3 con n segmentos.'),
  ],
}

export const APPROX_GLOSSARY = simpsonApproxGlossary(180)
export const BOUND_GLOSSARY_13 = {
  items: [
    ...simpsonBoundGlossary(180).items.filter((item) => item.symbol !== '180'),
    g('180,\\ 80', 'Los mismos divisores del error compuesto: 180 para 1/3 y 80 para 3/8.'),
  ],
}

// --- Datos del ejemplo de Chapra (ejemplo 1 del Resolver) ----------------------------

const mf = FUNCTION_EXAMPLE.mean_fourth
const M4 = FUNCTION_EXAMPLE.M4

export const example = {
  fn: `f(x) = ${FUNCTION_EXAMPLE.function.latex}`,
  integral: `I = \\int_0^{0.8} f(x)\\,dx = \\frac{3076}{1875} = ${n(I)}`,
  fourth: `f^{(4)}(x) = ${FUNCTION_EXAMPLE.function.fourth.latex}`,
  meanFourth: `\\bar{f}^{(4)} = \\frac{f'''(0.8) - f'''(0)}{0.8} = \\frac{${n(mf.fb)} - ${n(mf.fa)}}{0.8} = ${n(mf.value)}`,
  approxN2: `E_a = -\\frac{0.8^5}{2880}\\,(${n(mf.value)}) = ${n(row13(1).approx_error)} = E_t`,
  M4: formatNumber(M4.value),
  M4x: M4.x_display.text,
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  lastN13: BLOCK_13.rows.at(-1).n,
  lastN38: BLOCK_38.rows.at(-1).n,
  steps13: [1, 2, 3].map((k) => ({ k, row: row13(k), previous: k > 1 ? row13(k - 1) : null })),
  step38: { k: 1, row: row38(1), previous: null },
  S13: (k) => formatNumber(row13(k).S),
  S38: (k) => formatNumber(row38(k).S),
  Et13: formatNumber(row13(1).true_error),
  rel13: `${formatNumber(row13(1).relative_error)} %`,
  Ea13: formatNumber(row13(1).approx_error),
  bound13: formatNumber(row13(1).bound),
  Et38: formatNumber(row38(1).true_error),
  rel38: `${formatNumber(row38(1).relative_error)} %`,
  identity: identityLatex(row13(1).identity),
  // Resultados de la fila 1 (valor más pequeño de n de cada regla) para la tabla comparativa.
  T1: row13(1).identity.T_half_display,
}

/* Tabla de convergencia: trapecio frente a Simpson 1/3 con los mismos n (filas 1 a 4). */
export const convergenceRows = BLOCK_13.rows.slice(0, 4).map((r) => ({
  n: r.n,
  T: r.trapezoid.T,
  Et_T: r.trapezoid.true_error,
  S: r.S,
  Et_S: r.true_error,
  ratio: r.ratio,
  times: formatNumber(Number(r.trapezoid.times.toFixed(1))),
}))

/* Mini-ejemplo de la combinación (ejemplo 8). */
const combined = TABLE_EXAMPLE.applications[0]
const part = (rule) => combined.parts.find((p) => p.rule === rule)
const interval = (p) => `[${p.x_display[0].text}, ${p.x_display[1].text}]`
export const combination = {
  app: combined,
  n: TABLE_EXAMPLE.n,
  h: TABLE_EXAMPLE.h.text,
  junction: part('simpson38').x_display[0].text,
  S13: formatNumber(part('simpson13').value),
  S38: formatNumber(part('simpson38').value),
  interval13: interval(part('simpson13')),
  interval38: interval(part('simpson38')),
  total: formatNumber(combined.total),
  Et: formatNumber(combined.final.true_error),
  relative: `${formatNumber(combined.final.relative_error)} %`,
  areaLabel: `Combinación (n = ${TABLE_EXAMPLE.n}): área S = ${formatNumber(combined.total)}`,
  curveLabel: `f(x) · I = ${formatNumber(TABLE_EXAMPLE.integral.value)} (exacta)`,
  partLabels: { simpson13: 'Parte 1/3 (parábolas)', simpson38: 'Parte 3/8 (cúbica)' },
}

// --- Restricciones y algoritmo --------------------------------------------------

export const PRECAUTIONS = [
  {
    title: 'Espaciado uniforme obligatorio',
    body: [
      'Las fórmulas suponen que todos los segmentos miden lo mismo (',
      { m: 'h' },
      '). Con datos desiguales hay que usar el trapecio, como sugiere el Resolver.',
    ],
  },
  {
    title: 'Condición sobre n',
    body: [
      { m: 'n' },
      ' debe ser par para 1/3 y múltiplo de 3 para 3/8. En una tabla con ',
      { m: 'n' },
      ' impar se usa la combinación: 1/3 en los primeros ',
      { m: 'n - 3' },
      ' segmentos y 3/8 en los últimos 3.',
    ],
  },
  {
    title: 'Cuarta derivada continua',
    body: [
      'Para que la cota valga, ',
      { m: 'f' },
      ' debe tener ',
      { m: 'f^{(4)}' },
      ' continua en ',
      { m: '[a, b]' },
      '. Si ',
      { m: 'f' },
      ' es menos suave (por ejemplo ',
      { m: '|x - 0.5|' },
      ' o ',
      { m: '\\sqrt{x}' },
      ' cerca de 0), Simpson sigue convergiendo, pero más lento que ',
      { m: 'O(h^4)' },
      ', y su ventaja sobre el trapecio se reduce.',
    ],
  },
  {
    title: 'Puntos fuera del dominio y singularidades',
    body: [
      'Igual que en el trapecio: si ',
      { m: 'f' },
      ' no está definida o es infinita en algún punto de ',
      { m: '[a, b]' },
      ' (',
      { m: '1/\\sqrt{x}' },
      ' en ',
      { m: '[0, 1]' },
      ', ',
      { m: '1/(x - 1)' },
      ' en ',
      { m: '[0, 2]' },
      '), la regla no se puede aplicar tal cual. El Resolver lo detecta y lo avisa.',
    ],
  },
  {
    title: 'Funciones que oscilan mucho',
    body: [
      'Cada parábola (o cúbica) debe abarcar una parte pequeña de una oscilación; si no, la pieza no puede seguir las subidas y bajadas de la curva.',
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
      ', la regla (1/3, 3/8 o ambas), los segmentos iniciales ',
      { m: 'n_0' },
      ' de cada regla, la tolerancia y el máximo de refinamientos.',
    ],
  },
  {
    title: 'Validar n',
    body: [{ m: 'n_0' }, ' par para 1/3 o múltiplo de 3 para 3/8.'],
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
      ' en ellos, se aplican los pesos (',
      { m: '1, 4, 2, \\dots, 4, 1' },
      ' o ',
      { m: '1, 3, 3, 2, \\dots, 3, 3, 1' },
      '), se suma y se multiplica por ',
      { m: 'h/3' },
      ' o por ',
      { m: '3h/8' },
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
      { m: "f'''(a)" },
      ' y ',
      { m: "f'''(b)" },
      '; la cota con ',
      { m: 'M_4' },
      '.',
    ],
  },
  {
    title: 'Refinar',
    body: [
      'Se duplica ',
      { m: 'n' },
      ': la condición se mantiene (el doble de un par es par, y el de un múltiplo de 3 sigue siéndolo). Las alturas de la fila anterior se reutilizan.',
    ],
  },
  {
    title: 'Error estimado y razón',
    body: [{ m: '|S_k - S_{k-1}|' }, ' y la razón entre errores verdaderos consecutivos (cerca de 0.0625).'],
  },
  {
    title: 'Parar',
    body: [
      'Cuando hay al menos 6 filas y el error estimado es ',
      { m: '\\le' },
      ' tolerancia (en todas las reglas pedidas, en la misma fila), o al llegar al máximo de refinamientos.',
    ],
  },
  {
    title: 'Comprobar',
    body: [
      'Antiderivada paso a paso, ',
      { m: "F' = f" },
      ' y ',
      { m: 'F(b) - F(a)' },
      '; en 1/3, la identidad con el trapecio ',
      { m: 'S_n = (4T_n - T_{n/2})/3' },
      '.',
    ],
  },
]
