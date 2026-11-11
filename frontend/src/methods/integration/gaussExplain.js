// Cuadratura gaussiana: fórmulas, glosarios y el paso a paso explicado de cada
// fila, como datos con los mismos bloques que el trapecio (explain.js):
//   { kind: 'text' | 'math' | 'note' | 'check' }
// más los propios de Gauss, que dibujan GaussStepDetail y el PDF:
//   { kind: 'nodes' }      tabla i, tᵢ, wᵢ (forma exacta si m ≤ 4)
//   { kind: 'mapping' }    xᵢ = c + (H/2)·tᵢ, una línea por nodo (por subintervalo si N > 1)
//   { kind: 'evals' }      f(xᵢ) sustituida término a término
//   { kind: 'products' }   wᵢ·f(xᵢ) y la suma
// Todos los números vienen del backend; aquí sólo se escriben.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
import { substitutionLatex } from '../differentiation/formulas'
import { sub, tinyErrorNote } from './explain'
import { percent } from './formulas'

const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
const shownLatex = (d) => (d.exact ? d.latex : d.approx)
const shownText = (d) => (d.exact ? d.text : d.approx)
const text = (t) => ({ kind: 'text', text: t })
const math = (latex) => ({ kind: 'math', latex })
const note = (t) => ({ kind: 'note', text: t })
const SUPERSCRIPTS = '⁰¹²³⁴⁵⁶⁷⁸⁹'
const sup = (n) => String(n).replace(/\d/g, (d) => SUPERSCRIPTS[d])

/** Nombre de la derivada k: f', f'', f''', f^{(4)}… (LaTeX) y f⁽⁴⁾ (texto). */
export const derivativeLatex = (k) => (k <= 3 ? `f${"'".repeat(k)}` : `f^{(${k})}`)
export const derivativeText = (k) => (k <= 3 ? `f${"'".repeat(k)}` : `f⁽${sup(k)}⁾`)

// --- Fórmulas -------------------------------------------------------------------------

export const GAUSS_LATEX = String.raw`I \approx \frac{b - a}{2}\sum_{i=1}^{m} w_i\,f(x_i),\qquad x_i = \frac{b + a}{2} + \frac{b - a}{2}\,t_i`
export const COMPOSITE_LATEX = String.raw`I \approx \sum_{j=1}^{N} \frac{H}{2}\sum_{i=1}^{m} w_i\,f\!\Big(c_j + \frac{H}{2}\,t_i\Big),\qquad c_j = a + \Big(j - \tfrac{1}{2}\Big)H,\quad H = \frac{b - a}{N}`
export const NODES_LATEX = String.raw`P_m(t_i) = 0,\qquad w_i = \frac{2}{(1 - t_i^{2})\,\left[P_m'(t_i)\right]^{2}}`
export const STOP_LATEX = String.raw`\text{Error estimado} = \left|G_m - G_{m-1}\right|`
export const BOUND_LATEX = String.raw`|E_t| \le (b - a)\,H^{2m}\,\frac{(m!)^{4}}{(2m + 1)\,\left[(2m)!\right]^{3}}\,M_{2m},\qquad M_{2m} = \max_{x \in [a,\, b]}\left|f^{(2m)}(x)\right|`

// --- Glosarios ------------------------------------------------------------------------

export const GAUSS_GLOSSARY = {
  items: [
    { symbol: 'm', text: 'Cuántos puntos se usan (en cada subintervalo).' },
    {
      symbol: 't_i',
      text: 'Los nodos en [−1, 1]: las raíces del polinomio de Legendre de grado m. Son los puntos donde conviene evaluar.',
    },
    { symbol: 'w_i', text: 'Los pesos: cuánto cuenta cada evaluación. Suman 2, el ancho de [−1, 1].' },
    { symbol: 'x_i', text: 'El nodo tᵢ llevado a [a, b] con el cambio de variable.' },
    { symbol: '\\tfrac{b - a}{2}', text: 'El factor que deshace el cambio de variable (dx = (b − a)/2 · dt).' },
  ],
  summary:
    'La idea clave: con m puntos bien elegidos, la fórmula es exacta para polinomios de grado 2m − 1 (el doble que ' +
    'Newton-Cotes, que con m puntos sólo llega a grado m − 1 o m).',
}

export const COMPOSITE_GLOSSARY = {
  items: [
    { symbol: 'N', text: 'Cuántos subintervalos iguales se usan; con N = 1 es la fórmula simple.' },
    { symbol: 'H', text: 'El ancho de cada subintervalo: (b − a)/N.' },
    { symbol: 'c_j', text: 'El centro del subintervalo j: ahí cae t = 0.' },
    { symbol: '\\tfrac{H}{2}', text: 'El factor del cambio de variable de cada subintervalo (la mitad de su ancho).' },
  ],
  summary: 'En resumen: la misma fórmula de Gauss en cada subintervalo, y se suman los resultados.',
}

export const NODES_GLOSSARY = {
  items: [
    { symbol: 'P_m(t)', text: 'El polinomio de Legendre de grado m (P₀ = 1, P₁ = t y una recurrencia para los demás).' },
    {
      symbol: 't_i',
      text: 'Cada raíz se calcula con el método de Newton sobre esa recurrencia, hasta que el cambio sea menor que 10⁻¹⁵.',
    },
    { symbol: "P_m'(t_i)", text: 'La derivada del polinomio en el nodo; con ella sale el peso.' },
  ],
}

export const CHANGE_GLOSSARY = [
  { symbol: 't', text: 'La variable nueva: recorre [−1, 1] cuando x recorre [a, b].' },
  { symbol: '\\tfrac{b + a}{2}', text: 'El centro del intervalo: ahí cae t = 0.' },
  { symbol: '\\tfrac{b - a}{2}', text: 'La mitad del ancho: cuánto se estira [−1, 1] para cubrir [a, b].' },
  { symbol: 'dx', text: 'Al cambiar de variable, dx = (b − a)/2 · dt: por eso aparece ese factor delante de la suma.' },
]

export const BOUND_GLOSSARY = [
  { symbol: 'M_{2m}', text: 'El mayor valor de |f⁽²ᵐ⁾(x)| en [a, b]: la derivada de orden 2m (4 con m = 2, 6 con m = 3, …).' },
  { symbol: 'H^{2m}', text: 'El ancho del subintervalo elevado a 2m: al agregar puntos, el exponente crece y el error cae rápido.' },
  { symbol: '\\tfrac{(m!)^4}{(2m+1)[(2m)!]^3}', text: 'Una constante que se achica muy rápido al crecer m.' },
  { symbol: '\\text{hasta } m = 5', text: 'La cota sólo se calcula hasta m = 5: necesita derivadas cada vez más largas.' },
]

export const CHART_GLOSSARY = [
  {
    symbol: '\\text{Rectángulos}',
    text:
      'Gauss suma rectángulos: cada uno tiene la altura de la curva en un nodo y el ancho que le da su peso. Los ' +
      'anchos suman exactamente b − a. La magia está en dónde se ponen los nodos.',
  },
  { symbol: '\\text{Puntos}', text: 'Los nodos xᵢ sobre la curva.' },
  { symbol: '\\text{Líneas tenues}', text: 'Con N > 1, los bordes de cada subintervalo.' },
]

const REFERENCE = ' (aquí respecto al valor de referencia, que no es exacto)'

/** Columnas de la tabla de refinamiento. */
export function gaussColumns({ showTrue, reference }) {
  const columns = [
    { key: 'm', label: 'm', symbol: 'm', text: 'Los puntos de la fila: la fila k usa m = k nodos en cada subintervalo.' },
    {
      key: 'evaluations',
      label: 'Evaluaciones',
      symbol: '\\text{Evaluaciones}',
      text: 'Cuántas veces se evaluó f en esa fila: m·N. Gauss no reutiliza los nodos de la fila anterior.',
    },
    { key: 'G', label: 'Gₘ', symbol: 'G_m', text: 'La aproximación de la integral con m puntos.' },
    {
      key: 'estimated',
      label: 'Error estimado',
      symbol: '\\text{Error estimado}',
      text: 'Cuánto cambió G respecto a la fila anterior, |Gₘ − Gₘ₋₁|. Decide cuándo parar.',
    },
  ]
  if (showTrue) {
    columns.push(
      { key: 'true', label: 'Eₜ', symbol: 'E_t', text: `Error verdadero, I − Gₘ${reference ? REFERENCE : ''}.` },
      { key: 'relative', label: 'εₜ', symbol: '\\varepsilon_t', text: 'El error verdadero en porcentaje de I, |Eₜ|/|I|·100.' }
    )
  }
  columns.push({
    key: 'bound',
    label: 'Cota',
    symbol: '\\text{Cota}',
    text: 'El máximo error que garantiza la teoría (hasta m = 5): (b − a)·H²ᵐ·constante·M₂ₘ.',
  })
  if (showTrue) {
    columns.push({
      key: 'mark',
      label: '≤ cota',
      symbol: '\\checkmark',
      text: '✔ si |Eₜ| ≤ cota; R si sólo se cumple dentro del margen de redondeo de la computadora.',
    })
  }
  return columns
}

export const TABLE_LEGEND = [
  { symbol: '\\text{Filas}', text: 'Cada fila agrega un punto (m = 1, 2, 3, …) con el mismo N.' },
  {
    symbol: '\\text{Sin razón}',
    text:
      'En el trapecio el error se divide entre 4 en cada fila (razón 0.25). En Gauss la razón entre errores no tiene ' +
      'un valor fijo: el error baja cada vez más rápido al agregar puntos, así que no se muestra esa columna.',
  },
  { symbol: '—', text: 'En la fila 1 no hay fila anterior: el error estimado no existe.' },
]

export function comparisonColumns(reference) {
  return [
    { key: 'G', label: 'G', symbol: 'G', text: 'El resultado de Gauss: la última fila.' },
    {
      key: 'I',
      label: 'I',
      symbol: 'I',
      text: reference ? 'Valor de referencia: la integral calculada numéricamente con 30 dígitos.' : 'Valor exacto, calculado con la antiderivada.',
    },
    { key: 'true', label: 'Eₜ = I − G', symbol: 'E_t = I - G', text: `Error verdadero${reference ? REFERENCE : ''}.` },
    { key: 'relative', label: 'εₜ', symbol: '\\varepsilon_t', text: 'El error en porcentaje del valor de I.' },
  ]
}

export const MOMENT_COLUMNS = [
  { symbol: 'k', text: 'El grado del polinomio tᵏ que se integra.' },
  { symbol: '\\sum w_i t_i^{k}', text: 'Lo que da la regla de Gauss con los nodos y pesos de la última fila.' },
  { symbol: '\\int_{-1}^{1} t^{k}\\,dt', text: 'El valor exacto: 2/(k + 1) si k es par y 0 si es impar.' },
  { symbol: '\\checkmark', text: '✔ si coinciden (diferencia ≤ 10⁻¹²·máx(1, |valor|)).' },
]

export const MOMENT_SENTENCE =
  'La regla integra sin error todos los polinomios hasta grado 2m − 1; desde grado 2m deja de ser exacta.'

export const BOUND_UNAVAILABLE_NOTE =
  'La cota necesita la derivada de orden 2m de f, que para muchos puntos se vuelve muy larga de calcular; el error ' +
  'verdadero y el error estimado siguen disponibles.'

export const NOT_FINITE_NOTE =
  'La derivada de orden 2m de f no es finita en algún punto de [a, b] (por ejemplo, cerca de un extremo donde f no ' +
  'está definida): no hay un máximo M₂ₘ, así que la cota no está disponible.'

export function boundReasonText(row) {
  if (row.bound_reason === 'not_finite') return NOT_FINITE_NOTE
  if (row.bound_reason === 'timeout') return `Se superó el límite de tiempo al derivar. ${BOUND_UNAVAILABLE_NOTE}`
  return BOUND_UNAVAILABLE_NOTE
}

// --- Cambio de variable ---------------------------------------------------------------

/** «0.4 + 0.4t», «-0.5 + 2t», «t», «0.5t». */
function linearLatex(center, half, variable = 't') {
  const c = shownLatex(center)
  const h = shownLatex(half)
  const slope = h === '1' ? variable : `${h}${variable}`
  if (c === '0') return slope
  return `${c} + ${slope}`
}

/** Las líneas del cambio de variable con los números del problema. */
export function changeOfVariable(result) {
  const N = result.subintervals
  if (N === 1) {
    const x = linearLatex(result.center_display, result.half_width_display)
    const h = shownLatex(result.half_width_display)
    const body = result.function.is_sum ? `\\left[${result.function.latex}\\right]_{x = ${x}}` : `f(${x})`
    return [
      String.raw`x = \frac{b + a}{2} + \frac{b - a}{2}\,t = ${x}`,
      String.raw`dx = \frac{b - a}{2}\,dt = ${h}\,dt`,
      String.raw`\int_{${result.a_display.latex}}^{${result.b_display.latex}} f(x)\,dx = \int_{-1}^{1} ${body}\cdot ${h}\,dt`,
    ]
  }
  const h = shownLatex(result.half_display)
  return [
    String.raw`H = \frac{b - a}{N} = \frac{${shownLatex(result.width_display)}}{${N}} ${result.H_display.exact ? '=' : '\\approx'} ${shownLatex(result.H_display)}`,
    String.raw`x = c_j + \frac{H}{2}\,t = c_j + ${h}t,\qquad dx = \frac{H}{2}\,dt = ${h}\,dt`,
    String.raw`\int_{a}^{b} f(x)\,dx = \sum_{j=1}^{${N}} \int_{-1}^{1} f(c_j + ${h}t)\cdot ${h}\,dt`,
  ]
}

/** c₁ = 0.2, c₂ = 0.6, …; con muchos, los 5 primeros y los 2 últimos. */
export function centersLatex(result) {
  const items = result.centers.map((c, j) => `c_{${j + 1}} = ${shownLatex(c)}`)
  return (items.length > 8 ? [...items.slice(0, 5), '\\dots', ...items.slice(-2)] : items).join(',\\quad ')
}

// --- Paso a paso ----------------------------------------------------------------------

/** f(xᵢ) sustituida término a término (mismo formato que el trapecio). */
export function gaussSubstitution(result, point) {
  return {
    x: point.x,
    x_display: { exact: false },
    terms: result.function.substitution_terms.map((t, i) => ({ ...t, value: point.terms[i] })),
    value: point.f,
    all_zero: false,
  }
}

/** Nombre del punto: x_i con N = 1, x_{j,i} con N > 1. */
export const pointName = (result, j, i) => (result.subintervals === 1 ? `x_{${i}}` : `x_{${j},${i}}`)

/** x₁ = 0.4 + 0.4(−0.57735) = 0.16906. */
export function mappingLatex(result, row, group, point) {
  const node = row.step.nodes[point.i - 1]
  const c = shownLatex(group.center)
  const h = shownLatex(result.subintervals === 1 ? result.half_width_display : result.half_display)
  return `${pointName(result, group.j, point.i)} = ${c} + ${h}\\left(${node.t_display}\\right) = ${point.x_display}`
}

/** Σ wᵢ·f(xᵢ) de un subintervalo: 1.291851 + 3.264593 = 4.556444. */
export function groupSumLatex(result, group) {
  const products = group.points.map((p, i) => (i === 0 ? p.product : p.product.startsWith('-') ? `- ${p.product.slice(1)}` : `+ ${p.product}`))
  const name = result.subintervals === 1 ? 'S' : `S_{${group.j}}`
  const symbolic = `\\sum_{i=1}^{${group.points.length}} w_i\\,f(${result.subintervals === 1 ? 'x_i' : `x_{${group.j},i}`})`
  const middle = group.points.length > 1 && group.points.length <= 8 ? ` = ${products.join(' ')}` : ''
  return `${name} = ${symbolic}${middle} = ${group.sum}`
}

/** G_m = (b − a)/2 · S, o Σ_j (H/2)·S_j. */
function totalLatex(result, row) {
  const step = row.step
  const G = `G_{${row.m}}`
  const total = step.total.exact ? step.total.latex : step.total.approx
  const end = total === latexNumber(row.G) ? `\\mathbf{${total}}` : `${total} \\approx \\mathbf{${latexNumber(row.G)}}`
  if (result.subintervals === 1) {
    const h = shownLatex(result.half_width_display)
    return `${G} = \\frac{b - a}{2}\\cdot S = ${h} \\cdot ${paren(step.groups[0].sum)} = ${end}`
  }
  const h = shownLatex(result.half_display)
  const groups = step.groups
  const sums = groups.length <= 6 ? groups.map((g) => paren(g.sum)).join(' + ') : `${paren(groups[0].sum)} + \\dots + ${paren(groups.at(-1).sum)}`
  return `${G} = \\frac{H}{2}\\left(S_1 + \\dots + S_{${groups.length}}\\right) = ${h}\\left(${sums}\\right) = ${end}`
}

function estimatedVerdict(result, row) {
  const tolerance = formatNumber(result.tolerance)
  const value = formatNumber(row.estimated_error)
  const last = row.m === result.iterations.length
  if (!row.below_tolerance) {
    return last && !result.converged
      ? { ok: false, text: `${value} > ${tolerance}: se llegó al máximo de puntos sin cumplir la tolerancia.` }
      : { ok: null, text: `${value} es mayor que la tolerancia ${tolerance}: se agrega otro punto.` }
  }
  if (row.m >= result.min_rows) return { ok: true, text: `${value} ≤ ${tolerance} y ya hay ${result.min_rows} filas: el método se detiene.` }
  return { ok: null, text: `${value} ≤ ${tolerance}, pero todavía no hay ${result.min_rows} filas: se agrega otro punto.` }
}

/** Comparación |Eₜ| con la cota (mismo criterio ✔/⚠/R que los otros métodos). */
function boundCheck(row) {
  if (row.within_bound === null || row.within_bound === undefined) return null
  const size = latexNumber(Math.abs(row.true_error))
  const bound = latexNumber(row.bound)
  const name = derivativeText(2 * row.m)
  if (!row.within_bound) {
    return { kind: 'check', ok: false, latex: `|E_t| = ${size} > ${bound} = \\text{cota}`, text: '|Eₜ| supera la cota: revisa los datos (la teoría dice que no debería pasar).' }
  }
  if (row.equals_bound) {
    const constant = row.bound_info && !row.bound_info.M.substitution
    return {
      kind: 'check',
      ok: true,
      latex: `|E_t| = ${size} = ${bound} = \\text{cota}`,
      text: constant ? `|Eₜ| = cota ✔ (la igualdad ocurre porque ${name} es constante).` : '|Eₜ| = cota ✔.',
    }
  }
  if (row.by_rounding) {
    return {
      kind: 'check',
      ok: true,
      latex: `|E_t| = ${size} \\le ${bound} + R \\quad (R = ${latexNumber(row.rounding)})`,
      text:
        '|Eₜ| supera la cota sólo por el redondeo de la computadora, R = 2ε·[(H/2)·Σ wᵢ·(suma de |términos de f(xᵢ)|) + |G|]: ' +
        'dentro de ese margen se cumple.',
    }
  }
  return { kind: 'check', ok: true, latex: `|E_t| = ${size} \\le ${bound} = \\text{cota}`, text: 'El error verdadero quedó por debajo de la cota, como predice la teoría.' }
}

function boundSteps(result, row) {
  if (!row.bound_info) return [{ title: 'Paso 8. Cota del error', blocks: [note(`Cota no disponible. ${boundReasonText(row)}`)] }]
  const info = row.bound_info
  const order = info.order
  const m = row.m
  const derivative = result.function.derivatives[order - 1]
  const name = derivativeLatex(order)
  const blocks = [text(`La cota usa la derivada de orden 2m = ${order}:`)]
  blocks.push(derivative.long ? note(`${derivativeText(order)}(x) es muy larga; está en «Derivadas para la cota».`) : math(`${name}(x) = ${derivative.latex}`))
  const M = info.M
  const search = `M${sub(order)} es el mayor valor de |${derivativeText(order)}(x)| en [a, b]; se busca evaluando la derivada en ${result.sampling_points} puntos del intervalo.`
  if (!M.substitution) {
    blocks.push(text(derivative.constant
      ? `${search} Aquí ${derivativeText(order)} = ${formatNumber(M.value)} en todo el intervalo, así que M${sub(order)} = ${formatNumber(M.value)}.`
      : `${search} El mayor valor se alcanzó en x = ${shownText(M.x_display)}: M${sub(order)} = ${formatNumber(M.value)}.`))
  } else {
    blocks.push(text(`${search} El mayor valor se alcanzó en x = ${shownText(M.x_display)}:`))
    blocks.push(math(substitutionLatex(M.substitution, name)))
    blocks.push(math(`M_{${order}} = \\left|${name}(${shownLatex(M.x_display)})\\right| = ${latexNumber(M.value)}`))
  }
  const [num, den] = info.constant
  blocks.push(
    text('La constante de la fórmula, con m = ' + m + ':'),
    math(
      `\\frac{(m!)^{4}}{(2m + 1)\\,[(2m)!]^{3}} = \\frac{(${m}!)^{4}}{${2 * m + 1}\\,(${2 * m}!)^{3}} = ` +
        `\\frac{${num}}{${den}} \\approx ${latexNumber(info.constant_value)}`
    ),
    text('Se sustituye en la fórmula de la cota:'),
    math(
      `\\text{cota} = (b - a)\\,H^{${order}} \\cdot \\frac{${num}}{${den}} \\cdot M_{${order}} = ` +
        `${shownLatex(info.width_power)} \\cdot \\frac{${num}}{${den}} \\cdot ${latexNumber(M.value)} = ${latexNumber(row.bound)}`
    )
  )
  if (result.subintervals === 1) blocks.push(note('Con N = 1, H = b − a y la cota queda (b − a)^(2m+1)·constante·M₂ₘ, la fórmula de Chapra.'))
  const check = boundCheck(row)
  if (check) blocks.push(check)
  return [{ title: 'Paso 8. Cota del error', blocks }]
}

/** Todos los pasos de la fila m. */
export function gaussRowSteps(result, row, previous) {
  const N = result.subintervals
  const steps = [
    {
      title: 'Paso 1. Nodos y pesos',
      blocks: [
        text(
          `Se toman de la tabla de Gauss-Legendre (raíces del polinomio de Legendre de grado ${row.m}). ` +
            (row.m <= 4 ? 'Para m ≤ 4 se conoce su forma exacta.' : 'Para m > 4 sólo se muestran sus decimales.')
        ),
        { kind: 'nodes' },
      ],
    },
    {
      title: 'Paso 2. Llevar cada nodo a [a, b]',
      blocks: [
        text(
          N === 1
            ? 'Cada nodo tᵢ de [−1, 1] se lleva al intervalo con el cambio de variable xᵢ = (b + a)/2 + (b − a)/2·tᵢ.'
            : `En cada uno de los ${N} subintervalos, xⱼ,ᵢ = cⱼ + (H/2)·tᵢ: el centro del subintervalo más el nodo escalado.`
        ),
        { kind: 'mapping' },
      ],
    },
    {
      title: 'Paso 3. Evaluar f en cada nodo',
      blocks: [text('Se reemplaza cada xᵢ en f(x). En verde, los valores que se calculan en esta fila.'), { kind: 'evals' }],
    },
    {
      title: 'Paso 4. Multiplicar por el peso y sumar',
      blocks: [
        text('Cada altura f(xᵢ) se multiplica por su peso wᵢ (cuánto cuenta) y se suman los productos.'),
        { kind: 'products' },
        ...row.step.groups.slice(0, 6).map((g) => math(groupSumLatex(result, g))),
        ...(row.step.groups.length > 6 ? [note(`Se muestran las sumas de 6 de los ${row.step.groups.length} subintervalos; el total usa todas.`)] : []),
      ],
    },
    {
      title: N === 1 ? 'Paso 5. Multiplicar por (b − a)/2' : 'Paso 5. Multiplicar por H/2 y sumar los subintervalos',
      blocks: [
        text(N === 1 ? 'El factor (b − a)/2 deshace el cambio de variable (dx = (b − a)/2·dt).' : 'Cada suma se multiplica por H/2 (el factor del cambio de variable) y se suman.'),
        math(totalLatex(result, row)),
        ...(row.step.decimals > 6 ? [note(`Con ${row.step.decimals} decimales: con 6, el resultado de los valores que se ven no coincidiría con Gₘ.`)] : []),
      ],
    },
  ]

  if (previous) {
    const v = estimatedVerdict(result, row)
    steps.push({
      title: 'Paso 6. Error estimado',
      blocks: [
        text('Cuánto cambió el resultado respecto a la fila anterior (en azul Gₘ₋₁, en verde Gₘ); es el criterio de parada.'),
        math(
          `\\left|G_{${row.m}} - G_{${row.m - 1}}\\right| = \\left|${colorize(latexNumber(row.G), CURRENT_COLOR)} - ` +
            `${colorize(paren(latexNumber(row.previous_G)), PREVIOUS_COLOR)}\\right| = ${latexNumber(row.estimated_error)}`
        ),
        { kind: 'check', ok: v.ok, text: v.text },
      ],
    })
  } else {
    steps.push({ title: 'Paso 6. Error estimado', blocks: [text('En la fila 1 no hay fila anterior con qué comparar: el error estimado es «—».')] })
  }

  if (row.true_error !== null) {
    const I = result.integral.value
    const reference = result.integral.kind === 'reference'
    const blocks = [
      text(`Diferencia entre el valor ${reference ? 'de referencia' : 'exacto'} I y Gₘ.`),
      math(`E_t = I - G_{${row.m}} = ${latexNumber(I)} - ${paren(latexNumber(row.G))} = ${latexNumber(row.true_error)}`),
    ]
    if (row.relative_error !== null) {
      blocks.push(
        math(
          `\\varepsilon_t = \\frac{|E_t|}{|I|} \\cdot 100\\,\\% = \\frac{${latexNumber(Math.abs(row.true_error))}}{${latexNumber(Math.abs(I))}} \\cdot 100\\,\\% = ${latexNumber(row.relative_error)}\\,\\%`
        )
      )
    } else blocks.push(note('|I| ≈ 0: el error relativo no se calcula.'))
    if (formatNumber(row.true_error) === '0') blocks.push(text('Eₜ se ve 0: con 6 decimales Gₘ coincide con I.'))
    else if (row.true_error < 0) blocks.push(text('Eₜ es negativo: la aproximación se pasó (sobreestima).'))
    else blocks.push(text('Eₜ es positivo: la aproximación se quedó corta (subestima).'))
    const tiny = tinyErrorNote(row, reference)
    if (tiny) blocks.push(note(tiny))
    steps.push({ title: `Paso 7. Eₜ y εₜ${reference ? ' (respecto al valor de referencia)' : ''}`, blocks })
  }
  return [...steps, ...boundSteps(result, row)]
}

// --- Resumen y comprobación -----------------------------------------------------------

/** Frase final de la comprobación. */
export function gaussConclusion(result, final) {
  if (!final || final.true_error === null || final.true_error === undefined) return null
  const target = result.integral?.kind === 'reference' ? 'el valor de referencia' : 'la integral exacta'
  const last = result.iterations.at(-1).extra
  const who = `Con m = ${last.m} puntos${result.subintervals > 1 ? ` en N = ${result.subintervals} subintervalos` : ''} (${last.evaluations} evaluaciones de f)`
  if (formatNumber(final.G) === formatNumber(final.I)) return `${who} el resultado coincide con ${target} en 6 decimales.`
  return `${who} el resultado difiere de ${target} en Eₜ = ${formatNumber(final.true_error)} (εₜ = ${percent(final.relative_error)}).`
}

/** Filas de momentos a mostrar: con m grande, k = 0..3, «…», los 3 últimos exactos y la fila 2m. */
export function visibleMoments(rows) {
  if (rows.length <= 9) return rows
  return [...rows.slice(0, 4), null, ...rows.slice(-4)]
}

export { shownLatex, shownText }
