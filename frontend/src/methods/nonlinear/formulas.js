// LaTeX del paso a paso de Punto Fijo. Aquí no se evalúa nada: los valores
// con los que se evaluó cada g_i vienen del backend (iteration.extra.inputs)
// y sólo se les da formato.
//
// Cada g_i llega como plantilla LaTeX con marcadores @@j@@ en lugar de la
// variable j (ver `g_template` en solvers/nonlinear/fixed_point.py). La misma
// plantilla se rellena dos veces: con las variables y su superíndice de
// iteración, y con los valores numéricos.
import {
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  colorize,
  latexNumber,
} from '../../utils/latexFormulas'

const PLACEHOLDER = /@@(\d+)@@(\^)?/g
const FAILURE_COLOR = '#b91c1c'

/** Variable j con superíndice de iteración, ej. x_{1}^{(3)}. */
export function variableLatex(result, j, iteration) {
  const name = result.variables_latex[j]
  // Si el nombre ya trae superíndice (variable "x__2" -> x^{2}) se agrupa.
  const base = name.includes('^') ? `{${name}}` : name
  return `${base}^{(${iteration})}`
}

// True si el marcador es todo el contenido de un grupo: el argumento de una
// función, \left( @@0@@ \right), o un grupo {@@0@@} (exponente, fracción).
function isWholeGroup(template, offset, length) {
  const before = template.slice(0, offset).trimEnd()
  const after = template.slice(offset + length).trimStart()
  return (
    (before.endsWith('\\left(') && after.startsWith('\\right)')) ||
    (before.endsWith('{') && after.startsWith('}'))
  )
}

// Un valor que es base de una potencia, o negativo en medio de una
// operación, se escribe entre paréntesis: (-0.5)^{2}, 3 - (-0.5); pero
// sin(-0.5), no sin((-0.5)).
function fillTemplate(template, render) {
  return template.replace(PLACEHOLDER, (match, j, caret, offset) => {
    const { latex, color, parenthesize } = render(Number(j))
    const wrap = caret || (parenthesize && !isWholeGroup(template, offset, match.length))
    const body = wrap ? `\\left(${latex}\\right)` : latex
    return colorize(body, color) + (caret ?? '')
  })
}

export function generalFormulaLatex() {
  return (
    'x_i^{(k+1)} = g_i\\left(' +
    colorize('x_1^{(k+1)}, \\ldots, x_{i-1}^{(k+1)}', CURRENT_COLOR) +
    ',\\ ' +
    colorize('x_{i+1}^{(k)}, \\ldots, x_n^{(k)}', PREVIOUS_COLOR) +
    '\\right)'
  )
}

/** Despeje de la ecuación i: x_i = g_i(...). */
export function isolationLatex(result, i) {
  return `${result.variables_latex[i]} = ${result.equations[i].g_latex}`
}

/**
 * Sustitución de la variable i en la fila `index` de la tabla:
 *   x_i^{(k)} = g_i con las variables (nuevas en verde, anteriores en azul)
 *             = g_i con los valores = resultado
 */
export function substitutionLatex(result, index, i) {
  const row = result.iterations[index]
  const k = row.iteration
  const equation = result.equations[i]
  const inputs = row.extra.inputs[i]
  const position = new Map(equation.dependencies.map((j, d) => [j, d]))

  // j < i ya se recalculó en esta iteración; j > i viene de la anterior.
  const isNew = (j) => j < i
  const color = (j) => (isNew(j) ? CURRENT_COLOR : PREVIOUS_COLOR)

  const symbolic = fillTemplate(equation.g_template, (j) => ({
    latex: variableLatex(result, j, isNew(j) ? k : k - 1),
    color: color(j),
    parenthesize: false,
  }))
  const numeric = fillTemplate(equation.g_template, (j) => {
    const value = inputs[position.get(j)]
    const latex = latexNumber(value)
    return { latex, color: color(j), parenthesize: value < 0 || latex.includes('\\times') }
  })

  const value = row.x[i]
  const outcome =
    value === null
      ? colorize('\\text{no es un número real finito}', FAILURE_COLOR)
      : `\\mathbf{${latexNumber(value)}}`
  const lhs = variableLatex(result, i, k)

  if (!equation.dependencies.length) return `${lhs} = ${numeric} = ${outcome}`
  return `\\begin{aligned} ${lhs} &= ${symbolic} \\\\ &= ${numeric} = ${outcome} \\end{aligned}`
}

/**
 * Datos del error de la fila `index` con la forma que esperan
 * errorSubstitutionLatex / errorResultLatex de utils/latexFormulas.
 */
export function errorDetail(result, index) {
  const row = result.iterations[index]
  const previous = index > 0 ? result.iterations[index - 1].x : result.x0
  return {
    error: {
      diffs: row.x.map((current, i) => ({
        current,
        previous: previous[i],
        diff: Math.abs(current - previous[i]),
      })),
      value: row.error,
    },
  }
}
