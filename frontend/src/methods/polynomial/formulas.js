// Formato y LaTeX del paso a paso de Bairstow. No se calcula nada del
// método: todos los valores (tablas b y c, D, D_r, D_s, Δr, Δs, errores)
// vienen del backend en iteration.extra; aquí sólo se les da formato.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
// El desglose de los determinantes (ad − bc con valores sustituidos) es el
// mismo que en el detalle de Newton.
import { determinantStepsLatex } from '../nonlinear/newtonFormulas'

export { CURRENT_COLOR, PREVIOUS_COLOR, determinantStepsLatex }

const paren = (latex) => `\\left(${latex}\\right)`
// Un número negativo dentro de una operación va entre paréntesis.
const term = (value) => (value < 0 ? paren(latexNumber(value)) : latexNumber(value))

/** "1 + 0.5i", "1 − 0.5i", "0.5i", "2" (texto, para tablas). */
export function formatComplex(re, im) {
  if (im === 0) return formatNumber(re)
  const imaginary = `${formatNumber(Math.abs(im))}i`
  if (re === 0) return im < 0 ? `−${imaginary}` : imaginary
  return `${formatNumber(re)} ${im < 0 ? '−' : '+'} ${imaginary}`
}

/** |f(x)| de la comprobación: notación científica para valores pequeños. */
export function checkLatex(value) {
  if (value === null || value === undefined) return '\\text{---}'
  if (value === 0) return '0'
  if (value >= 1e-3 && value < 1e7) return latexNumber(value)
  const [mantissa, exponent] = value.toExponential(2).split('e')
  return `${mantissa} \\times 10^{${Number(exponent)}}`
}

// --- Comprobación: sustitución de cada raíz en el polinomio original ------
// Los valores (xᵏ, aₖ·xᵏ, f(x) y si se considera ≈ 0) vienen del backend en
// root.verification; aquí sólo se escriben. Dos estilos: LaTeX para la vista
// y texto ASCII para el PDF.
const LATEX_STYLE = {
  number: latexNumber,
  power: (base, k) => `${base}^{${k}}`,
  constant: 'a_0',
}
export const CHECK_TEXT_STYLE = {
  number: formatNumber,
  power: (base, k) => `${base}^${k}`,
  constant: 'a0',
}

/** Suma de partes con signo ya resuelto: "1 - 2 - 5 + 6". */
function signedSum(parts) {
  return parts
    .map(({ negative, body }, i) => (i === 0 ? `${negative ? '-' : ''}${body}` : `${negative ? '-' : '+'} ${body}`))
    .join(' ')
}

/** Valor real redondeado como parte de una suma: signo aparte y |valor|. */
function signedValue(value, style) {
  const text = style.number(Math.abs(value))
  return { negative: value < 0 && text !== '0', body: text }
}

/**
 * Línea de comprobación de una raíz real, en cuatro partes alineables:
 *   f(−2) | = (−2)^3 − 2(−2)^2 − 5(−2) + 6 | = −8 − 8 + 10 + 6 | = 0
 * `result` es la parte final ('0', '≈ 0' o el residuo) y `ok` si es ≈ 0.
 * La raíz nula (paso previo) queda f(0) = a₀ = 0.
 */
export function realCheckParts(root, style = LATEX_STYLE) {
  const check = root.verification
  const x = style.number(root.re)
  const isZeroRoot = root.re === 0
  const base = `(${x})`
  const substitution = isZeroRoot
    ? style.constant
    : signedSum(
        check.terms.map(({ power, coefficient }) => {
          const coef = style.number(Math.abs(coefficient))
          const variable = power === 0 ? '' : power === 1 ? base : style.power(base, power)
          const body = !variable ? coef : coef === '1' ? variable : `${coef}${variable}`
          return { negative: coefficient < 0, body }
        })
      )
  const evaluated = isZeroRoot ? null : signedSum(check.terms.map((t) => signedValue(t.value.re, style)))
  return {
    lhs: `f(${x})`,
    substitution,
    evaluated,
    result: checkResult(check, style),
    ok: check.is_zero,
  }
}

/** Parte final: 0 exacto, ≈ 0 o el residuo con su valor. */
function checkResult(check, style) {
  if (check.is_zero) return check.abs === 0 ? '= 0' : style === LATEX_STYLE ? '\\approx 0' : '~ 0'
  const { re, im } = check.value
  return `= ${im === 0 ? style.number(re) : complexIn(re, im, style)}`
}

/** p + qi con el redondeo del resto del resultado (sólo la parte que no es 0). */
function complexIn(re, im, style) {
  const real = style.number(re)
  const imaginaryAbs = style.number(Math.abs(im))
  if (imaginaryAbs === '0') return real
  const imaginary = imaginaryAbs === '1' ? 'i' : `${imaginaryAbs}${style === LATEX_STYLE ? '\\,' : ''}i`
  if (real === '0') return im < 0 ? `-${imaginary}` : imaginary
  return `${real} ${im < 0 ? '-' : '+'} ${imaginary}`
}

/** p + qi redondeado, en LaTeX o en texto ASCII (PDF). */
export const complexLatex = (re, im) => complexIn(re, im, LATEX_STYLE)
export const complexCheckText = (re, im) => complexIn(re, im, CHECK_TEXT_STYLE)

/**
 * Comprobación de una raíz compleja (la de parte imaginaria positiva), como
 * filas de tabla: término aₖxᵏ, xᵏ = (a + bi)ᵏ y aₖ·xᵏ, más la suma.
 */
export function complexCheckRows(root, style = LATEX_STYLE) {
  const check = root.verification
  const z = complexIn(root.re, root.im, style)
  const rows = check.terms.map(({ power, coefficient, x_power: xp, value }) => {
    const variable = power === 0 ? '' : power === 1 ? 'x' : style.power('x', power)
    const coef = style.number(Math.abs(coefficient))
    const body = !variable ? coef : coef === '1' ? variable : `${coef}${style === LATEX_STYLE ? '\\,' : ''}${variable}`
    return {
      term: `${coefficient < 0 ? '-' : ''}${body}`,
      power:
        power === 0 ? null : power === 1 ? z : `${style.power(`(${z})`, power)} = ${complexIn(xp.re, xp.im, style)}`,
      value: complexIn(value.re, value.im, style),
    }
  })
  return {
    lhs: `f(${z})`,
    rows,
    sum: complexIn(check.value.re, check.value.im, style),
    result: checkResult(check, style),
    ok: check.is_zero,
  }
}

/** Línea de texto (PDF) de una raíz real: "f(-2) = (-2)^3 - ... = -8 - 8 + 10 + 6 = 0 OK". */
export function realCheckText(root) {
  const { lhs, substitution, evaluated, result, ok } = realCheckParts(root, CHECK_TEXT_STYLE)
  const exact = ok && root.verification.abs !== 0 ? ` (${root.verification.abs.toExponential(1)})` : ''
  return [lhs, `= ${substitution}`, evaluated && `= ${evaluated}`, result].filter(Boolean).join(' ') + (ok ? ` OK${exact}` : ' (!)')
}

/** Polinomio en texto plano (para el PDF), desde coeficientes descendentes. */
export function polynomialText(coefficients) {
  const degree = coefficients.length - 1
  const parts = []
  coefficients.forEach((value, p) => {
    const text = formatNumber(Math.abs(value))
    if (text === '0') return
    const power = degree - p
    const variable = power === 0 ? '' : power === 1 ? 'x' : `x^${power}`
    const body = variable && text === '1' ? variable : `${text}${variable}`
    if (!parts.length) parts.push(value < 0 ? `-${body}` : body)
    else parts.push(`${value < 0 ? '-' : '+'} ${body}`)
  })
  return parts.join(' ') || '0'
}

/** Paso 1: valores con los que empieza la iteración. */
export function currentValuesLatex(extra) {
  return `r = ${latexNumber(extra.r)}, \\qquad s = ${latexNumber(extra.s)}`
}

export const B_FORMULA = 'b_i = a_i + r\\, b_{i+1} + s\\, b_{i+2}'
export const C_FORMULA = 'c_i = b_i + r\\, c_{i+1} + s\\, c_{i+2}'
export const FACTOR_FORMULA = 'x^2 - r\\,x - s'

/** Paso 4: el sistema 2×2, en símbolos y con los números sustituidos. */
export function systemLatex(extra) {
  const { c1, c2, c3, b0, b1 } = extra
  const symbolic =
    '\\begin{cases} c_2\\, \\Delta r + c_3\\, \\Delta s = -b_1 \\\\ c_1\\, \\Delta r + c_2\\, \\Delta s = -b_0 \\end{cases}'
  const numeric =
    `\\begin{cases} ${paren(latexNumber(c2))} \\Delta r + ${paren(latexNumber(c3))} \\Delta s = ${latexNumber(-b1)} \\\\ ` +
    `${paren(latexNumber(c1))} \\Delta r + ${paren(latexNumber(c2))} \\Delta s = ${latexNumber(-b0)} \\end{cases}`
  return `${symbolic} \\quad\\Longrightarrow\\quad ${numeric}`
}

/** Paso 6: Δr = D_r / D y Δs = D_s / D. */
export function incrementsLatex(extra) {
  const { D, D_r: Dr, D_s: Ds, delta_r: dr, delta_s: ds } = extra
  return [
    `\\Delta r = \\frac{D_r}{D} = \\frac{${latexNumber(Dr)}}{${latexNumber(D)}} = \\mathbf{${latexNumber(dr)}}`,
    `\\Delta s = \\frac{D_s}{D} = \\frac{${latexNumber(Ds)}}{${latexNumber(D)}} = \\mathbf{${latexNumber(ds)}}`,
  ]
}

/** Paso 7: r ← r + Δr, s ← s + Δs. */
export function updatesLatex(extra) {
  return [
    `r_{\\text{nuevo}} = ${colorize(latexNumber(extra.r), PREVIOUS_COLOR)} + ${term(extra.delta_r)} = \\mathbf{${latexNumber(extra.r_new)}}`,
    `s_{\\text{nuevo}} = ${colorize(latexNumber(extra.s), PREVIOUS_COLOR)} + ${term(extra.delta_s)} = \\mathbf{${latexNumber(extra.s_new)}}`,
  ]
}

/** Paso 8: ε_r y ε_s en %, o el error absoluto si r o s nuevo ≈ 0. */
export function errorsLatex(extra) {
  const one = (name, delta, value, error, absolute) =>
    absolute
      ? `\\varepsilon_${name} = \\left| \\Delta ${name} \\right| = \\left| ${latexNumber(delta)} \\right| = \\mathbf{${latexNumber(error)}}`
      : `\\varepsilon_${name} = \\left| \\frac{\\Delta ${name}}{${name}_{\\text{nuevo}}} \\right| \\cdot 100 = ` +
        `\\left| \\frac{${latexNumber(delta)}}{${latexNumber(value)}} \\right| \\cdot 100 = \\mathbf{${latexNumber(error)}\\,\\%}`
  return [
    one('r', extra.delta_r, extra.r_new, extra.eps_r, extra.absolute?.r),
    one('s', extra.delta_s, extra.s_new, extra.eps_s, extra.absolute?.s),
  ]
}

/** Cierre de un factor: el discriminante y las raíces explicadas. */
export function discriminantLatex(r, s, discriminant) {
  return `\\Delta = r^2 + 4s = ${term(r)}^2 + 4 \\cdot ${term(s)} = \\mathbf{${latexNumber(discriminant)}}`
}

export function rootsLatex(r, discriminant, roots) {
  if (discriminant > 0) {
    return [
      `x = \\frac{r \\pm \\sqrt{\\Delta}}{2} = \\frac{${latexNumber(r)} \\pm \\sqrt{${latexNumber(discriminant)}}}{2}`,
      `x_1 = \\mathbf{${latexNumber(roots[0].re)}}, \\qquad x_2 = \\mathbf{${latexNumber(roots[1].re)}}`,
    ]
  }
  if (discriminant === 0) {
    return [
      `\\Delta = 0 \\;\\Rightarrow\\; x = \\frac{r}{2} = \\frac{${latexNumber(r)}}{2}`,
      `x_1 = x_2 = \\mathbf{${latexNumber(roots[0].re)}} \\quad \\text{(raíz doble)}`,
    ]
  }
  const imaginary = Math.abs(roots[0].im)
  return [
    `\\Delta < 0 \\;\\Rightarrow\\; \\text{par complejo conjugado: parte real } \\frac{r}{2} = ${latexNumber(roots[0].re)}, ` +
      `\\text{ parte imaginaria } \\frac{\\sqrt{-\\Delta}}{2} = \\frac{\\sqrt{${latexNumber(-discriminant)}}}{2} = ${latexNumber(imaginary)}`,
    `x_{1,2} = \\mathbf{${latexNumber(roots[0].re)} \\pm ${latexNumber(imaginary)}\\,i}`,
  ]
}
