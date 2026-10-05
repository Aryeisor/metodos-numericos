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
