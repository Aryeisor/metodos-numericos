// Comprobación de Punto Fijo y Newton: la solución reemplazada en cada ecuación
// original, escrita f_i = 0. Los términos de f_i, su valor y el residuo vienen
// del backend en result.verification (con la misma descomposición en términos
// que Newton); aquí sólo se escriben, con las convenciones de la comprobación
// lineal: LaTeX para la vista y texto ASCII para el PDF.
import { CHECK_TEXT_STYLE, LATEX_STYLE, signedSum, signedValue } from '../polynomial/formulas'
import { shownExactly, visibleResidue } from '../linear/verification'
import { fillTemplate } from './formulas'

const isLatex = (style) => style === LATEX_STYLE

// Un valor que multiplica a otro factor va entre paréntesis, sin el punto:
// "20 \cdot @@0@@" → "20(1)", "@@0@@ \cdot @@1@@" → "(2)(1)".
const productTemplate = (template) =>
  template
    .replace(/(@@\d+@@)(?=\s*\\cdot)/g, '\\left($1\\right)')
    .replace(/(\\cdot\s*)(@@\d+@@)(?!\^)/g, '$1\\left($2\\right)')
    .replace(/\s*\\cdot\s*(?=\\left\(|@@\d+@@\^)/g, '')

/** Término con la solución sustituida, en LaTeX. */
function termLatex(template, x) {
  const filled = fillTemplate(productTemplate(template), (j) => ({
    latex: LATEX_STYLE.number(x[j]),
    parenthesize: x[j] < 0,
  }))
  // Paréntesis simples alrededor de un número: \left( agrega espacio, "20 (1)".
  return filled.replace(/\\left\((-?[\d.]+)\\right\)/g, '($1)')
}

/** Lo mismo en texto: "20*@@0@@" → "20(1)", "@@1@@^2" → "(2)^2", "sin(@@1@@)" → "sin(0.55)". */
function termText(text, x) {
  return text
    .replace(/@@(\d+)@@/g, (match, j, offset) => {
      const value = CHECK_TEXT_STYLE.number(x[j])
      const before = text[offset - 1]
      const after = text[offset + match.length]
      const wrap = x[j] < 0 || before === '*' || after === '*' || after === '^'
      return wrap ? `(${value})` : value
    })
    .replace(/\*\(/g, '(')
    .replace(/\)\*/g, ')')
}

/** "x = 1, \; y = 2" (o "x = 1, y = 2" en texto). */
export function solutionLine(names, solution, style = LATEX_STYLE) {
  return solution.map((value, i) => `${names[i]} = ${style.number(value)}`).join(isLatex(style) ? ',\\; ' : ', ')
}

/**
 * Comprobación de la ecuación i, en partes:
 *   20x + y² − 24 = 0  |  20(1) + (2)² − 24  |  = 20 + 4 − 24  |  = 0
 * Con valores no exactos (residuo ≠ 0 o algún valor redondeado) las
 * igualdades se escriben «≈», y el resultado termina en «≈ 0» si se
 * considera nulo.
 */
export function equationCheckParts(check, i, style = LATEX_STYLE) {
  const equation = check.equations[i]
  const { terms, residual } = equation
  const latex = isLatex(style)
  const values = terms.map((t) => t.value)
  const exact = residual === 0 && [...values, ...check.solution].every(shownExactly)
  const relation = exact ? '=' : latex ? '\\approx' : '~'

  const substitution = signedSum(
    terms.map((t) => ({
      negative: t.sign === '-',
      body: latex ? termLatex(t.template, check.solution) : termText(t.text, check.solution),
    }))
  )
  const evaluated = values.includes(null)
    ? null
    : `${relation} ${signedSum(values.map((value) => signedValue(value, style)))}`

  let result
  if (residual === null) result = latex ? '= \\text{no es un número real finito}' : '= (no es un número real finito)'
  else {
    const shown = style.number(residual)
    result = `${relation} ${shown}`
    if (equation.is_zero && shown !== '0') result += ` ${relation} 0`
  }

  return {
    label: i + 1,
    equation: `${latex ? equation.function_latex : equation.function_text} = 0`,
    substitution,
    evaluated,
    result,
    residue: visibleResidue(residual, style),
    ok: equation.is_zero,
  }
}

/** Línea de texto (PDF): "Ec. 1: 20(1) + (2)^2 - 24 = 20 + 4 - 24 = 0 OK". */
export function equationCheckText(check, i) {
  const { label, substitution, evaluated, result, residue, ok } = equationCheckParts(check, i, CHECK_TEXT_STYLE)
  const small = residue ? ` (residuo ${residue})` : ''
  return `Ec. ${label}: ${[substitution, evaluated, result].filter(Boolean).join(' ')} ${ok ? 'OK' : '(!)'}${small}`
}

/**
 * Nota del residuo con los valores sin redondear: sólo si alguna variable se
 * trató como entera y ese residuo se ve distinto de 0 con 6 decimales.
 */
export function rawResidualNote(check, style = LATEX_STYLE) {
  const raw = check.raw_max_residual
  if (!check.integers.some(Boolean) || raw === check.max_residual) return null
  return visibleResidue(raw, style)
}
