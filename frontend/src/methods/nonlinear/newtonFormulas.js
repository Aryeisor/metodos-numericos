// LaTeX del paso a paso de Newton, en el mismo orden en que se resuelve a
// mano: J(x) → evaluación → sistema lineal → D → D_i → Δx_i → actualización →
// error. Los valores de cada iteración (F y sus términos, J, D, D_i con sus
// matrices, Δx) y el desglose de las derivadas vienen del backend; aquí se les
// da formato. Lo único que se calcula es lo intermedio de cada determinante
// (productos ad y bc, menores), sólo para mostrarlo: el valor final de D y de
// cada D_i sigue siendo el del backend.
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
import { fillTemplate } from './formulas'

export { CURRENT_COLOR, PREVIOUS_COLOR }

const bmatrix = (rows) => `\\begin{bmatrix} ${rows.map((r) => r.join(' & ')).join(' \\\\ ')} \\end{bmatrix}`
const vmatrix = (rows) => `\\begin{vmatrix} ${rows.map((r) => r.join(' & ')).join(' \\\\ ')} \\end{vmatrix}`
const column = (items) => bmatrix(items.map((item) => [item]))
const numbers = (matrix) => matrix.map((row) => row.map(latexNumber))

// Un número negativo dentro de una suma o una fracción va entre paréntesis.
const term = (value) => (value < 0 ? `\\left(${latexNumber(value)}\\right)` : latexNumber(value))

/** Nombre de la variable con superíndice de iteración, ej. x_{1}^{(2)}. */
function variableAt(result, j, k) {
  const name = result.variables_latex[j]
  return `${name.includes('^') ? `{${name}}` : name}^{(${k})}`
}

const delta = (result, j) => `\\Delta ${result.variables_latex[j]}`
const subscriptD = (result, j) => `D_{${result.variables_latex[j]}}`

/** x^{(k)} = (a, b, ...) */
function pointLatex(values, k) {
  return `x^{(${k})} = \\left(${values.map(latexNumber).join(',\\ ')}\\right)`
}

export function generalStepLatex() {
  return (
    `J\\left(${colorize('x^{(k)}', PREVIOUS_COLOR)}\\right)\\, \\Delta x = ` +
    `-F\\left(${colorize('x^{(k)}', PREVIOUS_COLOR)}\\right), \\qquad ` +
    `x^{(k+1)} = ${colorize('x^{(k)}', PREVIOUS_COLOR)} + \\Delta x`
  )
}

/** Paso 2: el punto y F, J evaluados en él. */
export function evaluationLatex(row) {
  const k = row.iteration - 1
  const { point, F, J } = row.extra
  const at = `\\left(x^{(${k})}\\right)`
  return {
    point: pointLatex(point, k),
    F: F ? `F${at} = ${column(F.map(latexNumber))}` : null,
    J: J ? `J${at} = ${bmatrix(numbers(J))}` : null,
  }
}

/** Paso 3: J(x^(k)) · Δx = −F(x^(k)), con números. */
export function linearSystemLatex(result, row) {
  const { J, minus_F: minusF } = row.extra
  const unknowns = column(result.variables_latex.map((_, j) => delta(result, j)))
  return `${bmatrix(numbers(J))} ${unknowns} = ${column(minusF.map(latexNumber))}`
}

/** Paso 6: Δx_i = D_i / D. */
export function incrementLatex(result, row, j) {
  const { D, D_i: Di, delta: deltas } = row.extra
  return (
    `${delta(result, j)} = \\frac{${subscriptD(result, j)}}{D} = ` +
    `\\frac{${latexNumber(Di[j])}}{${latexNumber(D)}} = \\mathbf{${latexNumber(deltas[j])}}`
  )
}

/** Paso 7: x_i^(k+1) = x_i^(k) + Δx_i. */
export function updateLatex(result, row, j) {
  const k = row.iteration
  const previous = row.extra.point[j]
  return (
    `${variableAt(result, j, k)} = ${variableAt(result, j, k - 1)} + ${delta(result, j)} = ` +
    `${colorize(latexNumber(previous), PREVIOUS_COLOR)} + ${term(row.extra.delta[j])} = ` +
    `\\mathbf{${latexNumber(row.x[j])}}`
  )
}

/** Paso 8: ‖Δx‖∞ = max |Δx_i|. */
export function errorLatex(result, row) {
  const parts = row.extra.delta.map((d) => `\\left| ${latexNumber(d)} \\right|`).join(',\\; ')
  return (
    `\\text{error} = \\max_{i} \\left| \\Delta x_i \\right| = \\max\\left( ${parts} \\right) = ` +
    `\\mathbf{${latexNumber(row.error)}}`
  )
}

// ---------------------------------------------------------------------------
// Sub-pasos: derivadas parciales, sustitución en F y cálculo de determinantes.
// ---------------------------------------------------------------------------

/** Título de una entrada del Jacobiano: ∂f_i/∂x_j. */
export function partialTitleLatex(result, i, j) {
  return `\\frac{\\partial f_{${i + 1}}}{\\partial ${result.variables_latex[j]}}`
}

/** Desglose de ∂f_i/∂x_j que calcula el backend (una vez): {terms, sum_latex}. */
export function partialSteps(result, i, j) {
  return result.jacobian.steps[i][j]
}

/**
 * f_i(x^(k)) paso a paso: sustitución sin simplificar → valor de cada término
 * → resultado. Los términos y sus valores vienen del backend
 * (equations[i].terms, extra.F_terms); aquí sólo se les da formato.
 */
export function functionSubstitutionLatex(result, row, i) {
  const k = row.iteration - 1
  const point = row.extra.point
  const terms = result.equations[i].terms
  const values = row.extra.F_terms[i]

  const substituted = terms
    .map(({ sign, template }, t) => {
      const body = fillTemplate(template, (j) => {
        const latex = latexNumber(point[j])
        return { latex, color: PREVIOUS_COLOR, parenthesize: point[j] < 0 || latex.includes('\\times') }
      })
      if (t === 0) return sign === '-' ? `- ${body}` : body
      return `${sign} ${body}`
    })
    .join(' ')

  const evaluated = terms
    .map(({ sign }, t) => {
      // Valor de la parte sin signo del término (el signo ya está escrito).
      const magnitude = sign === '-' ? -values[t] : values[t]
      if (t === 0) return sign === '-' ? `- ${term(magnitude)}` : latexNumber(magnitude)
      return `${sign} ${term(magnitude)}`
    })
    .join(' ')

  const lines = [`f_{${i + 1}}\\left(x^{(${k})}\\right) &= ${substituted}`]
  if (terms.length > 1) lines.push(`&= ${evaluated}`)
  lines.push(`&= \\mathbf{${latexNumber(row.extra.F[i])}}`)
  return `\\begin{aligned} ${lines.join(' \\\\ ')} \\end{aligned}`
}

/** Determinante (sólo para mostrar los menores de una expansión). */
function det(matrix) {
  if (matrix.length === 1) return matrix[0][0]
  if (matrix.length === 2) return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
  return matrix[0].reduce(
    (sum, value, j) => sum + (j % 2 ? -1 : 1) * value * det(minor(matrix, j)),
    0
  )
}

const minor = (matrix, j) => matrix.slice(1).map((r) => r.filter((_, c) => c !== j))

// Entrada de la matriz, en color si pertenece a la columna reemplazada por −F.
function entry(value, column, colorColumn) {
  const latex = latexNumber(value)
  return column === colorColumn ? colorize(latex, CURRENT_COLOR) : latex
}

const paren = (latex) => `\\left(${latex}\\right)`

/**
 * Cálculo de un determinante en renglones alineados, empezando por
 * `label = |matriz|` y terminando en `value` (el valor del backend).
 *  - 2×2: ad − bc con los valores sustituidos y los dos productos.
 *  - n×n (n ≥ 3): expansión por cofactores a lo largo de la primera fila;
 *    se muestran los menores, el valor de cada uno y los productos, sin
 *    desarrollar los menores (cada uno es otro determinante más pequeño).
 * `colorColumn` resalta la columna reemplazada por −F (en los D_i).
 */
export function determinantStepsLatex(label, matrix, value, colorColumn = null) {
  const lines = [
    `${label} &= ${vmatrix(matrix.map((r) => r.map((v, c) => entry(v, c, colorColumn))))}`,
  ]

  if (matrix.length === 2) {
    const [[a, b], [c, d]] = matrix
    const show = (v, col) => paren(entry(v, col, colorColumn))
    lines.push(`&= ${show(a, 0)}${show(d, 1)} - ${show(b, 1)}${show(c, 0)}`)
    lines.push(`&= ${latexNumber(a * d)} - ${term(b * c)}`)
  } else if (matrix.length > 2) {
    const signs = matrix[0].map((_, j) => (j % 2 ? '-' : '+'))
    const join = (parts) =>
      parts.map((part, j) => (j === 0 ? (signs[j] === '-' ? `- ${part}` : part) : `${signs[j]} ${part}`)).join(' ')
    const minors = matrix[0].map((_, j) => minor(matrix, j))
    const minorValues = minors.map(det)
    const coefficient = (j) => paren(entry(matrix[0][j], j, colorColumn))

    lines.push(
      `&= ${join(
        minors.map((m, j) =>
          `${coefficient(j)} ${vmatrix(m.map((r) => r.map((v, c) => entry(v, c < j ? c : c + 1, colorColumn))))}`
        )
      )}`
    )
    lines.push(`&= ${join(minorValues.map((m, j) => `${coefficient(j)}${paren(latexNumber(m))}`))}`)
    // El primer producto va sin paréntesis aunque sea negativo (abre la línea).
    const products = minorValues.map((m, j) => matrix[0][j] * m)
    lines.push(`&= ${join(products.map((p, j) => (j === 0 ? latexNumber(p) : term(p))))}`)
  }

  lines.push(`&= \\mathbf{${latexNumber(value)}}`)
  return `\\begin{aligned} ${lines.join(' \\\\ ')} \\end{aligned}`
}

/** F(x) = [f_1; f_2; ...] simbólico. */
export function functionsLatex(result) {
  return `F(x) = ${column(result.equations.map((e) => e.function_latex))}`
}

/** J(x) = [∂f_i/∂x_j] simbólico. */
export function jacobianLatex(result) {
  return `J(x) = ${bmatrix(result.jacobian.latex)}`
}
