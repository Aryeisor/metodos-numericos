// Comprobación de un sistema lineal: la solución reemplazada en cada ecuación
// del sistema original. Los valores (aᵢⱼ·xⱼ, lado izquierdo, residuo y si se
// considera ≈ bᵢ) vienen del backend en result.verification; aquí sólo se
// escriben, con las mismas convenciones que la comprobación de Bairstow: LaTeX
// para la vista y texto ASCII para el PDF.
import { formatNumber } from '../../utils/iterationSteps'
import { CHECK_TEXT_STYLE, LATEX_STYLE, signedSum, signedValue } from '../polynomial/formulas'

const isLatex = (style) => style === LATEX_STYLE

// El valor se ve tal cual es (sin redondeo) en la línea de la comprobación.
const shownExactly = (value) => value !== null && Number(formatNumber(value)) === value

/** Residuo con signo: notación científica (1 decimal) para valores pequeños. */
function residue(value, style) {
  if (value === null) return isLatex(style) ? '\\text{---}' : '-'
  const magnitude = Math.abs(value)
  if (magnitude === 0 || (magnitude >= 1e-3 && magnitude < 1e7)) return style.number(value)
  const [mantissa, exponent] = value.toExponential(1).split('e')
  return isLatex(style) ? `${mantissa} \\times 10^{${Number(exponent)}}` : `${mantissa}e${Number(exponent)}`
}

export const residueLatex = (value) => residue(value, LATEX_STYLE)
export const residueText = (value) => residue(value, CHECK_TEXT_STYLE)

/** "x_{1} = -3, \; x_{2} = -2" (o "x1 = -3, x2 = -2" en texto). */
export function solutionLine(variables, solution, style = LATEX_STYLE) {
  return solution
    .map((value, i) => {
      const name = isLatex(style) ? variables[i].replace(/^x(\d+)$/, 'x_{$1}') : variables[i]
      return `${name} = ${style.number(value)}`
    })
    .join(isLatex(style) ? ',\\; ' : ', ')
}

/**
 * Línea de comprobación de una ecuación, en partes alineables:
 *   4(−3) + 2(−2) | = −12 − 4 | = −16  (b₁ = −16)
 * Coeficientes 0 omitidos (no vienen en `terms`), coeficiente 1 sin escribir,
 * el valor de cada variable entre paréntesis y los términos calculados con
 * su signo ya resuelto. Si la solución no es exacta (residuo ≠ 0 o algún
 * valor redondeado), las igualdades se escriben «≈».
 */
export function equationCheckParts(equation, style = LATEX_STYLE) {
  const { terms, lhs, b, residual } = equation
  const exact = residual === 0 && terms.every((t) => [t.coefficient, t.value, t.term].every(shownExactly))
  const relation = exact ? '=' : isLatex(style) ? '\\approx' : '~'
  const substitution = signedSum(
    terms.map(({ coefficient, value }) => {
      const coef = style.number(Math.abs(coefficient))
      const variable = `(${style.number(value)})`
      return { negative: coefficient < 0, body: coef === '1' ? variable : `${coef}${variable}` }
    })
  )
  const evaluated = signedSum(terms.map((t) => signedValue(t.term, style)))
  const n = equation.row + 1
  return {
    label: n,
    substitution,
    evaluated: `${relation} ${evaluated}`,
    result: `${relation} ${style.number(lhs)}`,
    comparison: `(${isLatex(style) ? `b_{${n}}` : `b${n}`} = ${style.number(b)})`,
    residue: residual === 0 ? null : residue(residual, style),
    ok: equation.is_zero,
  }
}

/** Línea de texto (PDF): "Ec. 1: 4(-3) + 2(-2) = -12 - 4 = -16 (b1 = -16) OK". */
export function equationCheckText(equation) {
  const { label, substitution, evaluated, result, comparison, residue, ok } = equationCheckParts(
    equation,
    CHECK_TEXT_STYLE
  )
  const small = residue ? ` (residuo ${residue})` : ''
  return `Ec. ${label}: ${substitution} ${evaluated} ${result} ${comparison} ${ok ? 'OK' : '(!)'}${small}`
}
