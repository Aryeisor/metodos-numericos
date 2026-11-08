// LaTeX (vista) y texto (PDF) del resultado de diferenciación numérica. Aquí
// no se calcula nada del método: D, los errores, la cota, M, los decimales del
// paso a paso y los textos exactos de h y de los puntos vienen del backend;
// sólo se les da formato. Todo depende de la fórmula que llega en
// result.formulas (nodos, pesos, orden, cota), no de una fórmula fija.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
import { shownExactly } from '../linear/verification'
import { fillTemplate } from '../nonlinear/formulas'
import { termLatex, termText } from '../nonlinear/verification'
import { CHECK_TEXT_STYLE, LATEX_STYLE, signedSum, signedValue } from '../polynomial/formulas'

const isLatex = (style) => style === LATEX_STYLE
const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)

/** f(x₀) en azul (valor de partida) y los demás nodos en verde. */
export const nodeColor = (offset) => (offset === 0 ? PREVIOUS_COLOR : CURRENT_COLOR)

/** Nombre de la derivada de orden n: f', f'', f''', f^{(4)}. */
export function derivativeName(n, style = LATEX_STYLE) {
  if (n <= 3) return `f${"'".repeat(n)}`
  return isLatex(style) ? `f^{(${n})}` : `f^(${n})`
}

const SUPERSCRIPTS = '⁰¹²³⁴⁵⁶⁷⁸⁹'
/** Nombre de f⁽ⁿ⁾ en un texto: f′, f′′, f′′′, f⁽⁴⁾, f⁽⁵⁾. */
export function derivativeText(n) {
  if (n <= 3) return `f${'′'.repeat(n)}`
  return `f⁽${[...String(n)].map((d) => SUPERSCRIPTS[d]).join('')}⁾`
}

/** Símbolo de la fórmula en la fila k: D^{+}_{3}. */
export const symbolAt = (formula, k) => `${formula.symbol_latex}_{${k}}`

// --- h y los puntos (excepción 1: exactos) -----------------------------------
/** h en una línea: «0.05», o «0.1/2^{14} ≈ 0.000006». */
export function stepLatex(h) {
  return h.exact ? h.latex : `${h.latex} \\approx ${h.approx}`
}

/** h dentro de una fórmula (sin «≈»). */
const stepInline = (h) => h.latex

/** Texto de una tabla o del PDF: exacto, o la forma h₀/2^(k−1). */
export const stepText = (h) => h.text

export function pointLatex(point) {
  const shown = point.display
  return shown.exact ? shown.latex : `${shown.latex} \\approx ${shown.approx}`
}

// --- Paso a paso ---------------------------------------------------------------
/** h_k = h₀ / 2^(k−1) = … */
export function stepSizeLatex(k, h, h0) {
  if (k === 1) return `h_{1} = h_0 = ${stepLatex(h)}`
  const value = h.exact ? ` = ${h.latex}` : ` \\approx ${h.approx}`
  return `h_{${k}} = \\frac{h_0}{2^{${k - 1}}} = \\frac{${h0.latex}}{2^{${k - 1}}}${value}`
}

/** Nodos con x₀ primero (el numerador los trae en el orden de la fórmula). */
export const byDistance = (points) => [...points].sort((a, b) => Math.abs(a.offset) - Math.abs(b.offset))

/** «x_0 = 1.8, x_0 + h = 1.9». */
export function pointsLatex(points, name = (p) => p.role) {
  return byDistance(points).map((p) => `${name(p)} = ${pointLatex(p)}`).join(',\\quad ')
}

/** Valor de f en un nodo, con su color. */
export const nodeValueLatex = (point) => colorize(paren(point.f_display), nodeColor(point.offset))

/** f(x₀ + h) = f(1.9) = ln(1.9) = 0.6418539, con el color del nodo. */
export function evaluationLatex(point, template, name = point.role) {
  const shown = point.display
  const value = nodeValueLatex(point)
  if (!shown.exact) return `f(${name}) = f\\left(${shown.latex}\\right) = ${value}`
  const substituted = template
    ? fillTemplate(template, () => ({ latex: shown.latex, parenthesize: shown.latex.startsWith('-') }))
    : null
  const middle = substituted && substituted !== shown.latex ? ` = ${substituted}` : ''
  return `f(${name}) = f(${shown.latex})${middle} = ${value}`
}

function numeratorParts(points, color) {
  return points.map((p) => {
    const weight = Math.abs(p.weight)
    // −3(14.778112): el coeficiente multiplica al valor entre paréntesis.
    const body = weight === 1 ? paren(p.f_display) : `${weight}\\left(${p.f_display}\\right)`
    return { negative: p.weight < 0, body: color ? colorize(body, nodeColor(p.offset)) : body }
  })
}

/** Productos cᵢ·f(xᵢ) ya calculados por el backend: «−44.334336 + 68.595828». */
const productParts = (item) =>
  item.products_display.map((text, i) => ({
    negative: text.startsWith('-'),
    body: colorize(text.replace(/^-/, ''), nodeColor(item.points[i].offset)),
  }))

/**
 * D = (f(a) − f(b)) / h = numerador / h = D, con los colores de los nodos.
 * Si el backend manda los productos (fórmulas con coeficientes ≠ ±1), se
 * muestran como paso intermedio y el denominador ya multiplicado (0.2).
 */
export function quotientLatex(formula, item, h, k) {
  const denominator =
    item.denominator_display ?? (formula.divisor === 1 ? stepInline(h) : `${formula.divisor} \\cdot ${stepInline(h)}`)
  const numerator = signedSum(numeratorParts(item.points, true))
  const products = item.products_display ? `\\dfrac{${signedSum(productParts(item))}}{${denominator}} = ` : ''
  return (
    `${symbolAt(formula, k)} = \\dfrac{${numerator}}{${denominator}} = ${products}` +
    `\\dfrac{${item.numerator_display}}{${denominator}} = \\mathbf{${latexNumber(item.D)}}`
  )
}

/** |D_k − D_(k−1)|, con D_(k−1) en azul y D_k en verde. */
export function estimatedErrorLatex(formula, item, k) {
  const symbol = formula.symbol_latex
  return (
    `\\left|${symbol}_{${k}} - ${symbol}_{${k - 1}}\\right| = ` +
    `\\left|${colorize(latexNumber(item.D), CURRENT_COLOR)} - ${colorize(paren(latexNumber(item.previous_D)), PREVIOUS_COLOR)}\\right| = ` +
    `${latexNumber(item.estimated_error)}`
  )
}

/** |D − f'(x)| = |0.547979 − 0.555556| = 0.007576. */
export function realErrorLatex(formula, item, exact, k, at = 'x_0') {
  return (
    `\\left|${symbolAt(formula, k)} - f'(${at})\\right| = ` +
    `\\left|${latexNumber(item.D)} - ${paren(latexNumber(exact))}\\right| = ${latexNumber(item.real_error)}`
  )
}

/** c·h^p con la h de la fila: «\frac{h}{2}» y «\frac{0.05}{2}». */
function coefficientLatex(formula, hLatex) {
  const [num, den] = formula.bound_coefficient
  const power = formula.order > 1 ? `^{${formula.order}}` : ''
  const top = `${num === 1 ? '' : `${num} \\cdot `}${hLatex}${power}`
  return den === 1 ? top : `\\frac{${top}}{${den}}`
}

/** Cota c·h^p·M = … y su comprobación «error real ≤ cota». */
export function boundLatex(formula, item, h) {
  if (item.bound === null) return null
  return (
    `${coefficientLatex(formula, 'h')} \\cdot M = ` +
    `${coefficientLatex(formula, h.exact ? h.latex : `\\left(${h.latex}\\right)`)} \\cdot ${latexNumber(item.M)} = ` +
    `${latexNumber(item.bound)}`
  )
}

/** «M = máx |f''(x)| en [a, b]», en LaTeX. */
export function maxLatex(formula, interval) {
  const [a, b] = interval
  return `M = \\max_{x \\in [${a},\\, ${b}]} \\left|${derivativeName(formula.bound_derivative)}(x)\\right|`
}

/** error real ≤ cota (+ R): «0.007576 ≤ 0.007716 ✔». */
export function criterionLatex(item) {
  if (item.within_bound === null) return null
  const relation = item.within_bound ? '\\le' : '>'
  const right = item.by_rounding
    ? `${latexNumber(item.bound)} + R \\quad (R = ${latexNumber(item.rounding)})`
    : latexNumber(item.bound)
  return `${latexNumber(item.real_error)} ${relation} ${right}`
}

/** Razón E_k / E_(k−1). */
export function ratioLatex(item, previous) {
  return (
    `\\frac{E_{k}}{E_{k-1}} = \\frac{${latexNumber(item.real_error)}}{${latexNumber(previous.real_error)}} = ` +
    `${latexNumber(item.ratio)}`
  )
}

/** Intervalo de una fila, con los textos exactos del backend. */
export const intervalLatex = (item) => item.interval_display.map((p) => (p.exact ? p.latex : p.approx))

// --- Comprobación ---------------------------------------------------------------
/**
 * f'(x) con x sustituido término a término (los términos y sus valores vienen
 * del backend): f'(2) = 3(2)² − 4(2) + 1 = 12 − 8 + 1 = 5.
 */
export function substitutionParts(substitution, style = LATEX_STYLE, name = "f'") {
  const latex = isLatex(style)
  const x = [substitution.x]
  const values = substitution.terms.map((t) => t.value)
  const exact = [...values, substitution.value, substitution.x].every(shownExactly)
  const relation = exact ? '=' : latex ? '\\approx' : '~'
  const xShown = substitution.x_display.exact ? substitution.x_display.text : style.number(substitution.x)
  const replaced = signedSum(
    substitution.terms.map((t) => ({
      negative: t.sign === '-',
      body: latex ? termLatex(t.template, x) : termText(t.text, x),
    }))
  )
  const evaluated =
    values.length > 1 && !values.includes(null)
      ? signedSum(values.map((value) => signedValue(value, style)))
      : null
  return {
    lhs: `${name}(${xShown})`,
    replaced,
    evaluated,
    relation,
    value: substitution.value === null ? (latex ? '\\text{---}' : '-') : style.number(substitution.value),
  }
}

/** `name`: la derivada que se sustituye (f' por defecto; f'' para M). */
export function substitutionLatex(substitution, name = "f'") {
  const { lhs, replaced, evaluated, relation, value } = substitutionParts(substitution, LATEX_STYLE, name)
  return [`${lhs} = ${replaced}`, evaluated, value].filter(Boolean).join(` ${relation} `)
}

export function substitutionText(substitution) {
  const { lhs, replaced, evaluated, relation, value } = substitutionParts(substitution, CHECK_TEXT_STYLE)
  return [`${lhs} = ${replaced}`, evaluated, value].filter(Boolean).join(` ${relation} `)
}

/**
 * Identidad de la fórmula de 3 puntos (valores del backend, a 6 decimales):
 *   (D⁺ + D⁻)/2 = (23.70845 + 20.74913)/2 = 22.22879 = D^med
 *   2D⁺(h) − D⁺(2h) = 2(23.70845) − 25.38459 = 22.03231 = D^ad
 */
export function identityLatex(item, formula) {
  const n = (value) => latexNumber(value)
  const symbol = formula?.symbol_latex ?? 'D'
  if (item.kind === 'romberg') return rombergLatex(item, symbol)
  let lhs
  if (item.kind === 'average') {
    lhs =
      `\\frac{D^{+} + D^{-}}{2} = \\frac{${n(item.forward)} + ${paren(n(item.backward))}}{2}`
  } else {
    const d = `D^{${item.direction}}`
    lhs = `2${d}(h) - ${d}(2h) = 2\\left(${n(item.base)}\\right) - ${paren(n(item.double))}`
  }
  const rhs = item.ok ? `= ${symbol}` : `\\ne ${symbol} = ${n(item.D)}`
  return `${lhs} = ${n(item.value)} ${rhs}`
}

/**
 * Identidad de Richardson del punto medio de 5 puntos, con los valores que se
 * ven (el backend calcula el resultado con ellos):
 *   (4D₃(h) − D₃(2h))/3 = (4(28.958315) − 29.193778)/3 = 28.879827 ≈ D₅ = 28.879828 (diferencia por redondeo)
 */
function rombergEnd(item, symbol, approx, note) {
  if (!item.ok) return `\\ne ${symbol} = ${item.D_display}`
  if (item.value_display === item.D_display) return `= ${symbol}`
  return `${approx} ${symbol} = ${item.D_display}${item.rounding_difference ? ` ${note}` : ''}`
}

function rombergLatex(item, symbol) {
  const lhs =
    `\\frac{4D_{3}(h) - D_{3}(2h)}{3} = ` +
    `\\frac{4\\left(${item.base_display}\\right) - ${paren(item.double_display)}}{3}`
  return `${lhs} = ${item.value_display} ${rombergEnd(item, symbol, '\\approx', '\\;\\text{(diferencia por redondeo)}')}`
}

/** Identidad en texto plano (PDF). */
export function identityText(item) {
  if (item.kind === 'romberg') {
    const double = item.double_display.startsWith('-') ? `(${item.double_display})` : item.double_display
    const end = rombergEnd(item, 'D5', '~', '(diferencia por redondeo)')
    return `(4D3(h) - D3(2h))/3 = (4(${item.base_display}) - ${double})/3 = ${item.value_display} ${end}` +
      (item.ok ? ' OK' : ' (!)')
  }
  const n = (value) => formatNumber(value)
  const p = (value) => (value < 0 ? `(${n(value)})` : n(value))
  const lhs =
    item.kind === 'average'
      ? `(D+ + D-)/2 = (${n(item.forward)} + ${p(item.backward)})/2`
      : `2D${item.direction}(h) - D${item.direction}(2h) = 2(${n(item.base)}) - ${p(item.double)}`
  return `${lhs} = ${n(item.value)} ${item.ok ? 'OK' : `!= ${n(item.D)} (!)`}`
}

/** «A y B», «A, B y C». */
export const listNames = (names) =>
  names.length <= 2 ? names.join(' y ') : `${names.slice(0, -1).join(', ')} y ${names.at(-1)}`

/** Número de 6 decimales o «—» (tablas y PDF). */
export const cell = (value) => (value === null || value === undefined ? '—' : formatNumber(value))

/** Marca de la columna «error real ≤ cota». */
export function boundMark(item) {
  if (!item || item.within_bound === null) return '—'
  return item.within_bound ? '✔' : '⚠'
}
