// LaTeX del paso a paso de Newton. No se calcula nada: los valores de cada
// iteración (F, J, D, D_i con sus matrices, Δx) vienen del backend en
// iteration.extra, y aquí sólo se les da formato, en el mismo orden en que se
// resuelve a mano: J(x) → evaluación → sistema lineal → D → D_i → Δx_i →
// actualización → error.
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'

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

/** F(x) = [f_1; f_2; ...] y J(x) = [∂f_i/∂x_j], simbólicos. */
export function symbolicSystemLatex(result) {
  const functions = column(result.equations.map((e) => e.function_latex))
  return `F(x) = ${functions}, \\qquad J(x) = ${bmatrix(result.jacobian.latex)}`
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

/** Paso 4: D = |J| = valor. */
export function determinantLatex(row) {
  return `D = \\det J = ${vmatrix(numbers(row.extra.J))} = \\mathbf{${latexNumber(row.extra.D)}}`
}

/** Paso 5: D_i con la columna i (reemplazada por −F) resaltada. */
export function columnDeterminantLatex(result, row, j) {
  const matrix = row.extra.matrices[j].map((r) =>
    r.map((value, c) => (c === j ? colorize(latexNumber(value), CURRENT_COLOR) : latexNumber(value)))
  )
  return `${subscriptD(result, j)} = ${vmatrix(matrix)} = \\mathbf{${latexNumber(row.extra.D_i[j])}}`
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
