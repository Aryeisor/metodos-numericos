// Construye las representaciones en LaTeX de las fórmulas y sustituciones.
// Consume exactamente los mismos datos que ya produce `buildIterationDetail`:
// aquí no se calcula nada, sólo se da formato.

import { formatNumber } from './iterationSteps'

// Valores tomados de la iteración anterior vs. valores ya recalculados en la
// iteración actual (sólo ocurre en Gauss-Seidel).
export const PREVIOUS_COLOR = '#2563eb'
export const CURRENT_COLOR = '#15803d'

/** Pasa el número ya formateado a LaTeX (notación científica incluida). */
function latexNumber(value) {
  const text = formatNumber(value)
  if (text === '∞') return '\\infty'
  if (text === '—') return '\\text{---}'

  const scientific = text.match(/^(-?\d+(?:\.\d+)?)e([+-])(\d+)$/)
  if (scientific) {
    const [, mantissa, sign, exponent] = scientific
    return `${mantissa} \\times 10^{${sign === '-' ? '-' : ''}${Number(exponent)}}`
  }

  return text
}

function colorize(latex, color) {
  return `\\textcolor{${color}}{${latex}}`
}

export function generalFormulaLatex(method) {
  if (method === 'gauss-seidel') {
    return (
      'x_i^{(k+1)} = \\frac{b_i - \\displaystyle\\sum_{j < i} a_{ij}\\, ' +
      colorize('x_j^{(k+1)}', CURRENT_COLOR) +
      ' - \\displaystyle\\sum_{j > i} a_{ij}\\, ' +
      colorize('x_j^{(k)}', PREVIOUS_COLOR) +
      '}{a_{ii}}'
    )
  }

  return (
    'x_i^{(k+1)} = \\frac{b_i - \\displaystyle\\sum_{j \\neq i} a_{ij}\\, ' +
    colorize('x_j^{(k)}', PREVIOUS_COLOR) +
    '}{a_{ii}}'
  )
}

/** Sustitución numérica de una variable, como fracción real. */
export function substitutionLatex(variable, iteration) {
  const terms = variable.terms
    .map((term) => {
      const coefficient = latexNumber(term.coefficient)
      const value = colorize(
        latexNumber(term.value),
        term.fromCurrent ? CURRENT_COLOR : PREVIOUS_COLOR
      )
      return `- (${coefficient})(${value})`
    })
    .join(' ')

  const numerator = `${latexNumber(variable.independent)} ${terms}`.trim()

  return (
    `x_{${variable.index + 1}}^{(${iteration})} = ` +
    `\\frac{${numerator}}{${latexNumber(variable.diagonal)}} = ` +
    `\\mathbf{${latexNumber(variable.result)}}`
  )
}

export function errorFormulaLatex() {
  return '\\text{error} = \\max_{i} \\left| x_i^{(k+1)} - x_i^{(k)} \\right|'
}

/** Sustitución numérica del error: |nuevo − anterior| para cada variable. */
export function errorSubstitutionLatex(detail) {
  const absolutes = detail.error.diffs
    .map(
      (d) =>
        `\\left| ${latexNumber(d.current)} - ${colorize(
          latexNumber(d.previous),
          PREVIOUS_COLOR
        )} \\right|`
    )
    .join(',\\; ')

  return `\\max\\left( ${absolutes} \\right)`
}

export function errorResultLatex(detail) {
  const values = detail.error.diffs.map((d) => latexNumber(d.diff)).join(',\\; ')
  const result =
    detail.error.value === null ? '\\text{---}' : latexNumber(detail.error.value)
  return `\\max\\left( ${values} \\right) = \\mathbf{${result}}`
}
