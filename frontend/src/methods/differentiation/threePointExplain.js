// Paso a paso explicado de las fórmulas de 3 y 5 puntos (punto medio y
// extremos), con los mismos bloques que el de diferencias (differenceExplain.js),
// del que reutiliza los pasos comunes: h, alturas, error estimado, error real y
// el criterio de la cota. Lo que cambia entre 3 y 5 puntos (h² o h⁴, f''' o
// f⁽⁵⁾, 2h o 12h) sale del orden de la fórmula. Todos los números vienen del
// backend; aquí sólo se escriben. Sirve para una fila (modo función) y para un
// punto (modo tabla).
import { formatNumber } from '../../utils/iterationSteps'
import { colorize, latexNumber } from '../../utils/latexFormulas'
import { signedSum } from '../polynomial/formulas'
import {
  boundCheck,
  changeLatex,
  differenceSteps,
  estimatedStep,
  heightsStep,
  realErrorStep,
  stepSizeStep,
} from './differenceExplain'
import { derivativeName, derivativeText, nodeColor, ratioLatex, substitutionLatex } from './formulas'

const text = (t) => ({ kind: 'text', text: t })
const math = (latex) => ({ kind: 'math', latex })
const note = (t) => ({ kind: 'note', text: t })
const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
const shown = (d) => (d.exact ? d.latex : d.approx)
const shownText = (d) => (d.exact ? d.text : d.approx)
const isMidpoint = (formula) => formula.key === 'punto_medio'
const byX = (points) => [...points].sort((a, b) => a.x - b.x)

export const isThreePoint = (result) => result.method === 'tres-puntos'
export const isFivePoint = (result) => result.method === 'cinco-puntos'

/** Paso a paso explicado del método del resultado (diferencias, 3 o 5 puntos). */
export function explainSteps(result, formula, item, ctx, previous = null) {
  const steps = result.method === 'diferencias-finitas' ? differenceSteps : threePointSteps
  return steps(result, formula, item, ctx, previous)
}

// Lo que depende del orden de la fórmula: O(h²) (3 puntos) u O(h⁴) (5 puntos).
const DERIVATIVE_KEYS = { 3: 'third_derivative', 5: 'fifth_derivative' }
const POWER_KEYS = { 2: 'h_squared', 4: 'h_fourth' }
const isHigh = (formula) => formula.order === 4
/** «de la parábola» (3 puntos) o «del polinomio» de grado 4 (5 puntos). */
const curve = (formula) => (isHigh(formula) ? 'del polinomio' : 'de la parábola')

/** f'''(x) o f⁽⁵⁾(x) en el punto (signo y valor), para explicar el signo del error. */
const derivativeAt = (result, ctx, n) =>
  (ctx.table ? result.iterations[ctx.label - 1].extra : result)[DERIVATIVE_KEYS[n]]

// --- Pasos ------------------------------------------------------------------------

/** Modo tabla: h es la distancia entre dos datos seguidos (con el nodo +1, o el −1). */
function tableStepSize(result, item, ctx) {
  const here = { index: ctx.label - 1, display: result.iterations[ctx.label - 1].extra.x_display }
  const node = item.points.find((p) => p.offset === 1) ?? item.points.find((p) => p.offset === -1)
  const [right, left] = node.offset > 0 ? [node, here] : [here, node]
  const h = item.h.exact ? `= ${item.h.latex}` : `\\approx ${item.h.approx}`
  return {
    title: 'El paso h',
    blocks: [
      text('Distancia entre dos datos seguidos; en esta tabla es la misma entre todos los datos.'),
      math(`h = x_{${right.index + 1}} - x_{${left.index + 1}} = ${right.display.latex} - ${paren(left.display.latex)} ${h}`),
    ],
  }
}

const POINTS_TEXT = {
  punto_medio: (at) => `El punto medio usa un vecino a cada lado de ${at}, a la misma distancia.`,
  extremo_adelante: (at) => `El extremo hacia adelante usa ${at} y dos vecinos a la derecha.`,
  extremo_atras: (at) => `El extremo hacia atrás usa ${at} y dos vecinos a la izquierda.`,
  punto_medio_5: (at) => `El punto medio usa dos vecinos a cada lado de ${at}, a distancias h y 2h.`,
  extremo_adelante_5: (at) => `El extremo hacia adelante usa ${at} y cuatro vecinos hacia la derecha.`,
  extremo_atras_5: (at) => `El extremo hacia atrás usa ${at} y cuatro vecinos hacia la izquierda.`,
}

/** x₀ + 2h = 2 + 2(0.1) = 2.2 (el valor exacto viene del backend). */
function pointLine(p, ctx) {
  if (p.offset === 0) return `x_0 = ${shown(p.display)}`
  const factor = Math.abs(p.offset)
  const h = factor === 1 ? ctx.h.latex : `${factor}\\left(${ctx.h.latex}\\right)`
  const value = p.display.exact ? `= ${p.display.latex}` : `\\approx ${p.display.approx}`
  return `${p.role} = ${shown(ctx.x0)} ${p.offset > 0 ? '+' : '-'} ${h} ${value}`
}

function pointsStep(formula, item, ctx) {
  const lines = ctx.table
    ? byX(item.points).map((p) => `${ctx.name(p)} = ${p.display.latex}`)
    : byX(item.points).map((p) => pointLine(p, ctx))
  return {
    title: 'Puntos',
    blocks: [text(POINTS_TEXT[formula.key](ctx.atText)), ...lines.map(math)],
  }
}

/** Producto cᵢ·f(xᵢ) del backend, con el color del nodo. */
const productBody = (item, i) => colorize(item.products_display[i].replace(/^-/, ''), nodeColor(item.points[i].offset))

function productsStep(formula, item, ctx) {
  const weights = item.points.map((p) => p.weight)
  return {
    title: 'Multiplicar por los coeficientes',
    blocks: [
      text(
        `Cada altura se multiplica por su coeficiente (${weights.join(', ')}), que dice cuánto pesa ese punto en la ` +
          `pendiente ${curve(formula)}.`
      ),
      ...item.points.map((p, i) =>
        math(
          `${p.weight} \\cdot f(${ctx.name(p)}) = ${p.weight}\\left(${colorize(p.f_display, nodeColor(p.offset))}\\right) = ` +
            `${item.products_display[i].startsWith('-') ? '-' : ''}${productBody(item, i)}`
        )
      ),
    ],
  }
}

function sumStep(item) {
  const parts = item.products_display.map((t, i) => ({ negative: t.startsWith('-'), body: productBody(item, i) }))
  return {
    title: 'Sumar',
    blocks: [text('Se suman los productos, cada uno con su signo.'), math(`${signedSum(parts)} = ${item.numerator_display}`)],
  }
}

function changeStep(item, ctx) {
  return {
    title: 'Cambio de un lado al otro',
    blocks: [text(`Cuánto cambia la altura de la curva de un lado al otro de ${ctx.atText}.`), math(changeLatex(item, ctx))],
  }
}

function divideStep(formula, item, ctx) {
  const h = ctx.table ? item.h : ctx.h
  const d = formula.divisor
  const scaled = item.denominator_display
    ? `${d}h = ${d}\\left(${h.latex}\\right) = ${item.denominator_display}`
    : `${d}h = ${d} \\cdot ${h.latex}`
  const denominator = item.denominator_display ?? `${d} \\cdot ${h.latex}`
  return {
    title: `Dividir entre ${d}h`,
    blocks: [
      text(`Se divide entre ${d}h para obtener la pendiente ${curve(formula)} en ${ctx.atText}, que aproxima la derivada.`),
      math(scaled),
      math(`${ctx.symbol(formula)} = \\dfrac{${item.numerator_display}}{${denominator}} = \\mathbf{${latexNumber(item.D)}}`),
    ],
  }
}

/** Lado de la aproximación y, si f''' lo explica, por qué (signo del término del error). */
export function threePointSideTexts(result, formula, item, ctx) {
  if (item.side === 'equal') return ['La aproximación coincide exactamente con la derivada exacta.']
  const out = []
  if (item.side === 'over') out.push('La aproximación quedó por encima de la derivada exacta (la sobreestima).')
  else if (item.side === 'under') out.push('La aproximación quedó por debajo de la derivada exacta (la subestima).')
  const sign = derivativeAt(result, ctx, formula.bound_derivative)?.sign
  if (sign && item.predicted_side === item.side && isHigh(formula)) {
    const fifth = sign > 0 ? 'f⁽⁵⁾ > 0' : 'f⁽⁵⁾ < 0'
    out.push(
      `Esto pasa porque ${fifth} cerca de ${ctx.atText}. El error de las fórmulas de 5 puntos es aproximadamente ` +
        '−(h⁴/30)·f⁽⁵⁾ (punto medio) o −(h⁴/5)·f⁽⁵⁾ (extremos): los tres tienen el mismo signo. Por eso, con ' +
        `${fifth}, las tres quedan por ${sign > 0 ? 'debajo (subestiman)' : 'encima (sobreestiman)'}. Es lo contrario ` +
        `del punto medio de 3 puntos, que ${sign > 0 ? 'sobreestima' : 'subestima'}.`
    )
  } else if (sign && item.predicted_side === item.side) {
    const third = sign > 0 ? "f''' > 0" : "f''' < 0"
    out.push(
      `Esto pasa porque ${third} cerca de ${ctx.atText}. El error del punto medio es aproximadamente +(h²/6)·f''' y el ` +
        "de los extremos, −(h²/3)·f''': tienen signos contrarios. Por eso, con " +
        `${third}, el punto medio ${sign > 0 ? 'sobreestima' : 'subestima'} y los extremos ` +
        `${sign > 0 ? 'subestiman' : 'sobreestiman'}.`
    )
  }
  return out
}

function boundStep(result, formula, item, ctx) {
  const n = formula.bound_derivative
  const high = isHigh(formula)
  // f''' (3 puntos) o f⁽⁵⁾ (5 puntos), en LaTeX y en el texto.
  const name = derivativeName(n)
  const word = high ? derivativeText(n) : "f'''"
  const title = `Cota (aquí se usa ${word})`
  const derivative = result.function.higher_derivatives[n]
  if (item.bound === null) {
    return { title, blocks: [note(`No disponible: ${word}(x) no es finita en todo el intervalo de la fórmula.`)] }
  }
  const constant = !/x/.test(derivative.latex)
  const sorted = byX(item.points)
  const [a, b] = ctx.table
    ? [sorted[0], sorted.at(-1)].map((p) => shownText(p.display))
    : item.interval_display.map(shownText)
  const blocks = [
    text(
      high
        ? `La quinta derivada mide qué tanto se aleja la función de un polinomio de grado 4 (si ${word} = 0, la fórmula es exacta):`
        : 'La tercera derivada mide qué tanto se aleja la función de una parábola:'
    ),
    math(`${name}(x) = ${derivative.latex}`),
  ]
  const search =
    `M es el mayor valor de |${word}(x)| en el intervalo [${a}, ${b}] que usa la fórmula; se busca evaluando ${word} en ` +
    `${result.sampling_points} puntos.`
  if (constant) {
    blocks.push(text(`${search} Aquí ${word} = ${formatNumber(item.M_substitution?.value ?? item.M)} en todo el intervalo, así que M = ${formatNumber(item.M)}.`))
  } else {
    blocks.push(text(`${search} El mayor está en x = ${shownText(item.M_substitution.x_display)}:`))
    blocks.push(math(substitutionLatex(item.M_substitution, name)))
    blocks.push(math(`M = \\left|${name}(${shown(item.M_substitution.x_display)})\\right| = ${latexNumber(item.M)}`))
  }
  const den = formula.bound_coefficient[1]
  const p = formula.order
  const h = ctx.table ? item.h : ctx.h
  // h^p exacto si tiene 12 decimales o menos; si no, (h)^p con la forma de h.
  const power = item[POWER_KEYS[p]]
  const hPower = power.exact ? power.latex : `\\left(${h.latex}\\right)^{${p}}`
  blocks.push(text('Se sustituye en la fórmula de la cota:'))
  if (high && power.exact) blocks.push(math(`h^{4} = ${h.latex}^{4} = ${power.latex}`))
  blocks.push(
    math(`\\dfrac{h^{${p}}}{${den}} \\cdot M = \\dfrac{${hPower}}{${den}} \\cdot ${latexNumber(item.M)} = ${latexNumber(item.bound)}`)
  )
  if (item.within_bound !== null) blocks.push(boundCheck(item, result.rounding_text, constant, word))
  return { title, blocks }
}

function ratioStep(formula, item, previous) {
  const high = isHigh(formula)
  const [expected, factor, power] = high ? [0.0625, 16, 'h⁴'] : [0.25, 4, 'h²']
  const close = Math.abs(item.ratio - expected) < (high ? 0.0075 : 0.03)
  return {
    title: 'Razón',
    blocks: [
      math(ratioLatex(item, previous)),
      text(
        close
          ? `El error se dividió entre ${factor} al dividir h entre 2, como predice la teoría (error proporcional a ${power}).`
          : `La teoría predice una razón cercana a ${expected} (error proporcional a ${power}); aquí es ${formatNumber(item.ratio)}.` +
              (high ? ' Con h tan pequeño, el redondeo de la computadora ya pesa en el error y aleja la razón.' : '')
      ),
    ],
  }
}

/** Todos los pasos de una fórmula de 3 o 5 puntos en una fila (o en un punto, en modo tabla). */
export function threePointSteps(result, formula, item, ctx, previous = null) {
  const steps = [
    ctx.table ? tableStepSize(result, item, ctx) : stepSizeStep(formula, item, ctx),
    pointsStep(formula, item, ctx),
    heightsStep(item, ctx, `al combinar valores muy parecidos y dividir entre ${formula.divisor}h`),
    ...(isMidpoint(formula) ? [changeStep(item, ctx)] : [productsStep(formula, item, ctx), sumStep(item)]),
    divideStep(formula, item, ctx),
  ]
  if (!ctx.table && item.estimated_error !== null && item.estimated_error !== undefined) {
    steps.push(estimatedStep(result, formula, item, ctx))
  }
  if (result.function && ctx.exact !== null && ctx.exact !== undefined && item.real_error !== null) {
    steps.push(realErrorStep(result, formula, item, ctx, (f, i, c) => threePointSideTexts(result, f, i, c)))
  }
  if (result.function) steps.push(boundStep(result, formula, item, ctx))
  if (item.ratio !== null && item.ratio !== undefined && previous) steps.push(ratioStep(formula, item, previous))
  return steps
}

// --- Identidades y comparación ------------------------------------------------------

/** Una frase por identidad (comprobación y PDF). */
export const IDENTITY_TEXTS = {
  average:
    'El punto medio es el promedio de la progresiva y la regresiva: sus errores tienen signos contrarios y se cancelan.',
  richardson:
    'El extremo es 2·D(h) − D(2h), con la diferencia de su lado: combinar dos diferencias con distinto h elimina el ' +
    'error principal; esta idea se llama extrapolación de Richardson.',
}

export const COMPARISON_LEGEND =
  'Qué se compara: con el mismo h, la progresiva y la regresiva tendrían estos errores. El de 3 puntos es mucho menor ' +
  'porque su error es proporcional a h² y el de las diferencias, a h: con h pequeño, h² es mucho más pequeño que h.'

export const UNIFORM_NOTE =
  'Esta tabla exige espaciado uniforme porque las fórmulas suponen el mismo h a ambos lados.'

// --- Fórmula de 5 puntos ---------------------------------------------------------------

export const FIVE_POINT_COMPARISON_LEGEND =
  'Qué se compara: con el mismo h, el punto medio de 3 puntos y las diferencias progresiva y regresiva tendrían estos ' +
  'errores. El de 5 puntos es mucho menor porque su error es proporcional a h⁴; el de 3 puntos, a h², y el de las ' +
  'diferencias, a h. Cada línea dice cuántas veces menor es el error de cada fórmula de 5 puntos.'

/** Identidad de Richardson del punto medio de 5 puntos, explicada (comprobación y PDF). */
export const RICHARDSON_TEXT =
  'El punto medio de 5 puntos se obtiene combinando dos fórmulas de 3 puntos, una con h y otra con 2h: así se elimina ' +
  'su error de orden h² y queda uno de orden h⁴. La línea sustituye los valores y marca ✔ si da la misma aproximación.'

export const RICHARDSON_ROUNDING_NOTE =
  '«Diferencia por redondeo»: la sustitución usa los valores que se ven, redondeados a 6 decimales, y por eso el último ' +
  'decimal puede salir distinto en 1. Con los valores completos la identidad se cumple exactamente: por eso lleva ✔.'

export const ENDPOINTS_NOTE =
  'Los extremos de 5 puntos no tienen una identidad tan simple; en ellos se comprueba que el error quede por debajo de ' +
  'la cota.'

const MID5 = 'punto_medio_5'
const MID3 = 'punto_medio'

/**
 * Por qué en el punto i se recomendó esa fórmula (modo tabla de 5 puntos): «en
 * x = 1.7 no hay dos datos a la izquierda, así que no cabe el punto medio de 5
 * puntos; se usa el extremo hacia adelante, que es más preciso que el punto
 * medio de 3 puntos (error 0.000906 frente a 0.042907)».
 */
export function recommendedText(result, i) {
  const extra = result.iterations[i - 1].extra
  const at = `En x = ${extra.x_display.text}`
  const key = extra.recommended.key
  if (key === MID5) return `${at} hay dos datos a cada lado: se usa el punto medio de 5 puntos, el más preciso.`
  if (key === MID3) {
    return `${at} no cabe ninguna fórmula de 5 puntos (no hay cuatro datos hacia ningún lado ni dos a cada lado): se usa el punto medio de 3 puntos.`
  }
  const ahead = key === 'extremo_adelante_5'
  const missing = `no hay dos datos a la ${ahead ? 'izquierda' : 'derecha'}, así que no cabe el punto medio de 5 puntos`
  const name = `el extremo hacia ${ahead ? 'adelante' : 'atrás'}`
  const [mine, three] = [extra[key]?.real_error, extra[MID3]?.real_error]
  if (!extra[MID3]) return `${at} ${missing}; se usa ${name}.`
  const errors =
    mine !== null && mine !== undefined && three !== null && three !== undefined
      ? ` (error ${formatNumber(mine)} frente a ${formatNumber(three)})`
      : ''
  return `${at} ${missing}; se usa ${name}, que es más preciso que el punto medio de 3 puntos${errors}.`
}
