// LaTeX (vista) y texto (PDF) del resultado de integración numérica. Aquí no
// se calcula nada del método: T, los errores, la cota, M₂, los decimales del
// paso a paso y los textos exactos de h y de los puntos vienen del backend;
// sólo se les da formato.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'

const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
/** h dentro de una fórmula: exacto, o la forma \frac{b − a}{n} entre paréntesis. */
const inline = (h) => (h.exact ? h.latex : `\\left(${h.latex}\\right)`)

/** Número de 6 decimales o «—» (tablas y PDF). */
export const cell = (value) => (value === null || value === undefined ? '—' : formatNumber(value))

/** εₜ con su signo de porcentaje. */
export const percent = (value) => (value === null || value === undefined ? '—' : `${formatNumber(value)} %`)

/** Marca de «|Eₜ| ≤ cota». */
export function boundMark(item) {
  if (!item || item.within_bound === null || item.within_bound === undefined) return '—'
  return item.within_bound ? '✔' : '⚠'
}

/** ∫_a^b f(x) dx; el integrando va entre paréntesis sólo si es una suma o resta. */
export function integralLatex(result) {
  const f = result.function
  const body = f.is_sum ? `\\left(${f.latex}\\right)` : f.latex
  return `\\int_{${result.a_display.latex}}^{${result.b_display.latex}} ${body}\\,dx`
}

/** h_k = (b − a)/n_k = … */
export function stepSizeLatex(result, row, k) {
  const a = paren(result.a_display.latex)
  const b = result.b_display.latex
  const h = row.h
  const value = h.exact ? ` = ${h.latex}` : ` \\approx ${h.approx}`
  return `h_{${k}} = \\frac{b - a}{n_{${k}}} = \\frac{${b} - ${a}}{${row.n}}${value}`
}

/** xᵢ exacto, o «≈ aproximado». */
export const pointLatex = (shown) => (shown.exact ? shown.latex : `\\approx ${shown.approx}`)

/**
 * T_k = T_(k−1)/2 + h_k·Σ nuevos, con T_(k−1) en azul y los nuevos en verde.
 * `name(j)` es el LaTeX del valor de la fila j (Romberg: R_{j,1}); `term`, el de la suma.
 */
export function recurrenceLatex(row, k, name = (j) => `T_{${j}}`, term = 'f(x_i)') {
  const step = row.step
  const previous = colorize(step.previous, PREVIOUS_COLOR)
  const sum = colorize(paren(step.sum), CURRENT_COLOR)
  return (
    `${name(k)} = \\frac{${name(k - 1)}}{2} + h_{${k}} \\sum_{\\text{nuevos}} ${term} = ` +
    `\\frac{${previous}}{2} + ${inline(row.h)} \\cdot ${sum} =${step.half} + ${paren(step.product)}` +
    ` = \\mathbf{${latexNumber(row.T)}}`
  )
}

/** |T_k − T_(k−1)|, con T_(k−1) en azul y T_k en verde. */
export function estimatedErrorLatex(row, k) {
  return (
    `\\left|T_{${k}} - T_{${k - 1}}\\right| = ` +
    `\\left|${colorize(latexNumber(row.T), CURRENT_COLOR)} - ${colorize(paren(latexNumber(row.previous_T)), PREVIOUS_COLOR)}\\right|` +
    ` = ${latexNumber(row.estimated_error)}`
  )
}

/** Eₜ = I − T. */
export function trueErrorLatex(row, I, k) {
  return `E_t = I - T_{${k}} = ${latexNumber(I)} - ${paren(latexNumber(row.T))} = ${latexNumber(row.true_error)}`
}

/** εₜ = |Eₜ|/|I|·100. */
export function relativeErrorLatex(row, I) {
  return (
    `\\varepsilon_t = \\frac{|E_t|}{|I|} \\cdot 100\\,\\% = \\frac{${latexNumber(Math.abs(row.true_error))}}` +
    `{${latexNumber(Math.abs(I))}} \\cdot 100\\,\\% = ${latexNumber(row.relative_error)}\\,\\%`
  )
}

/** f̄'' = (f'(b) − f'(a))/(b − a). */
export function meanSecondLatex(result) {
  const m = result.mean_second
  return (
    `\\bar{f''} = \\frac{f'(b) - f'(a)}{b - a} = \\frac{${latexNumber(m.fb)} - ${paren(latexNumber(m.fa))}}` +
    `{${result.width_display.latex}} = ${latexNumber(m.value)}`
  )
}

/** (b − a)·h²/12 con la h de la fila y luego con (b − a)·h² ya multiplicado: «(2)(2)²/12 = 8/12». */
function coefficientLatex(result, row, factor, sign = '') {
  const product = row.coefficient_numerator
  const relation = product.exact ? '=' : '\\approx'
  return (
    `${sign}\\frac{(${result.width_display.latex})\\left(${row.h.latex}\\right)^{2}}{12} \\cdot ${factor} ${relation} ` +
    `${sign}\\frac{${product.exact ? product.latex : product.approx}}{12} \\cdot ${factor}`
  )
}

/** Eₐ = −(b − a)h²/12 · f̄''. */
export function approxErrorLatex(result, row) {
  return (
    `E_a = -\\frac{(b - a)\\,h^{2}}{12}\\,\\bar{f''} = ` +
    `${coefficientLatex(result, row, paren(latexNumber(result.mean_second.value)), '-')} = ${latexNumber(row.approx_error)}`
  )
}

/** Cota (b − a)h²/12 · M₂. */
export function boundLatex(result, row) {
  return (
    `\\frac{(b - a)\\,h^{2}}{12}\\,M_2 = ${coefficientLatex(result, row, latexNumber(result.M2.value))}` +
    ` = ${latexNumber(row.bound)}`
  )
}

/** Eₜ,k / Eₜ,(k−1). */
export function ratioLatex(row, previous, k) {
  return (
    `\\frac{E_{t,${k}}}{E_{t,${k - 1}}} = \\frac{${latexNumber(row.true_error)}}{${latexNumber(previous.true_error)}}` +
    ` = ${latexNumber(row.ratio)}`
  )
}

/** Suma de las áreas = total (o ≈ si las áreas a 6 decimales no suman exacto). */
export function areasSumLatex(check) {
  const terms = check.areas.map((a, i) => (i === 0 ? a : a.startsWith('-') ? `- ${a.slice(1)}` : `+ ${a}`)).join(' ')
  const relation = check.areas_sum === check.total_display ? '=' : '\\approx'
  return `${terms} ${relation} ${check.total_display}`
}

/** Fórmula compuesta con h (tabla uniforme) = suma de los trapecios. */
export function compositeLatex(result) {
  const c = result.composite
  const n = result.points.length - 1
  return (
    `\\frac{h}{2}\\Big[y_0 + 2\\sum_{i=1}^{${n - 1}} y_i + y_{${n}}\\Big] = ` +
    `${c.half_h}\\,\\Big[${paren(latexNumber(result.points[0][1]))} + 2\\left(${c.interior_sum}\\right) + ` +
    `${paren(latexNumber(result.points[n][1]))}\\Big] = ${c.half_h} \\cdot ${paren(c.bracket)} = ${latexNumber(c.value)}`
  )
}
