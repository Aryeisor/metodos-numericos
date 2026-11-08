// Paso a paso explicado del método de Simpson, con el mismo formato de
// bloques que el del trapecio (explain.js): [{ title, blocks }] con
//   text, math, note, check, { kind: 'division' } y { kind: 'points' }.
// La vista (TrapezoidStepDetail) y el PDF recorren la misma lista. Todos los
// números vienen del backend; aquí sólo se escriben.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
import { substitutionLatex } from '../differentiation/formulas'
import { criterionCheck, tinyErrorNote } from './explain'
import { percent, relativeErrorLatex, stepSizeLatex } from './formulas'

const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
const shownLatex = (d) => (d.exact ? d.latex : d.approx)
const inlineH = (h) => (h.exact ? h.latex : `\\left(${h.latex}\\right)`)
const text = (t) => ({ kind: 'text', text: t })
const math = (latex) => ({ kind: 'math', latex })
const note = (t) => ({ kind: 'note', text: t })

const is38 = (rule) => rule.key === 'simpson38'
/** «1/3» o «3/8». */
export const ruleShort = (key) => (key === 'simpson38' ? '3/8' : '1/3')
/** Factor de la regla en LaTeX y en texto: h/3 o 3h/8. */
export const factorText = (rule) => (is38(rule) ? '3h/8' : 'h/3')

/** Por qué el punto i pesa lo que pesa (columna «Peso» del paso a paso). */
export function weightReason(rule, i, n) {
  if (i === 0 || i === n) return 'extremo → 1'
  if (is38(rule)) return i % 3 === 0 ? 'múltiplo de 3 → 2' : 'no múltiplo de 3 → 3'
  return i % 2 === 1 ? 'impar → 4' : 'par interior → 2'
}

/** S = factor·h·suma, con h exacto o en su forma \frac{b − a}{n}. */
export function ruleValueLatex(rule, h, bracket, value, name = 'S') {
  const factor = is38(rule) ? `\\frac{3}{8} \\cdot ${inlineH(h)}` : `\\frac{${inlineH(h)}}{3}`
  const symbolic = is38(rule) ? '\\frac{3h}{8}' : '\\frac{h}{3}'
  return `${name} = ${symbolic} \\cdot \\text{suma} = ${factor} \\cdot ${paren(bracket)} = \\mathbf{${latexNumber(value)}}`
}

/** Suma ponderada: todos los productos (con pocos puntos) o agrupada por peso. */
export function weightedSumLatex(rule, row) {
  const step = row.step
  if (step.points.length === step.count && step.count <= step.fold) {
    const symbolic = step.points.map((p) => `${p.weight} \\cdot f(x_{${p.i}})`).join(' + ')
    const values = step.points.map((p) => `${p.weight} \\cdot ${paren(p.f_display)}`).join(' + ')
    const products = step.points
      .map((p, i) => (i === 0 ? p.product : p.product.startsWith('-') ? `- ${p.product.slice(1)}` : `+ ${p.product}`))
      .join(' ')
    return `${symbolic} = ${values} = ${products} = ${step.bracket}`
  }
  const [first, last] = step.ends.map(paren)
  const sums = step.sums.map((s) => `${s.weight}\\left(${s.display}\\right)`)
  const groups = is38(rule)
    ? '3\\sum_{i\\ \\text{no múlt. de 3}} f(x_i) + 2\\sum_{i\\ \\text{múlt. de 3}} f(x_i)'
    : '4\\sum_{i\\ \\text{impar}} f(x_i) + 2\\sum_{i\\ \\text{par}} f(x_i)'
  return `f(x_0) + ${groups} + f(x_{${row.n}}) = ${[first, ...sums, last].join(' + ')} = ${step.bracket}`
}

function estimatedLatex(row, k) {
  return (
    `\\left|S_{${k}} - S_{${k - 1}}\\right| = ` +
    `\\left|${colorize(latexNumber(row.S), CURRENT_COLOR)} - ${colorize(paren(latexNumber(row.previous_S)), PREVIOUS_COLOR)}\\right|` +
    ` = ${latexNumber(row.estimated_error)}`
  )
}

/** (b − a)·h⁴/C con la h de la fila, y luego con (b − a)·h⁴ ya multiplicado. */
function coefficientLatex(width, h, numerator, divisor, factor, sign = '') {
  const relation = numerator.exact ? '=' : '\\approx'
  return (
    `${sign}\\frac{(${width})\\left(${h.latex}\\right)^{4}}{${divisor}} \\cdot ${factor} ${relation} ` +
    `${sign}\\frac{${numerator.exact ? numerator.latex : numerator.approx}}{${divisor}} \\cdot ${factor}`
  )
}

/** f̄⁽⁴⁾ = [f'''(b) − f'''(a)]/(b − a). */
export function meanFourthLatex(mean, width) {
  return (
    `\\bar{f}^{(4)} = \\frac{f'''(b) - f'''(a)}{b - a} = \\frac{${latexNumber(mean.fb)} - ${paren(latexNumber(mean.fa))}}` +
    `{${width}} = ${latexNumber(mean.value)}`
  )
}

/** Pasos de f''' en los límites, f̄⁽⁴⁾ y Eₐ (modo función o una parte del modo tabla). */
export function approxBlocks(fn, mean, width, h, numerator, divisor, approx) {
  return [
    text('Primero se evalúa la tercera derivada en los límites:'),
    math(`f'''(x) = ${fn.third.latex}`),
    math(substitutionLatex(mean.fb_substitution, "f'''")),
    math(substitutionLatex(mean.fa_substitution, "f'''")),
    text('Con esos valores se obtiene el promedio de la cuarta derivada:'),
    math(meanFourthLatex(mean, width)),
    note(
      "Este promedio sale de que la integral de f⁽⁴⁾ entre a y b es f'''(b) − f'''(a); al dividir entre el ancho del " +
        'intervalo se obtiene su valor medio.'
    ),
    text('Se sustituye en la fórmula de Chapra:'),
    math(
      `E_a = -\\frac{(b - a)\\,h^{4}}{${divisor}}\\,\\bar{f}^{(4)} = ` +
        `${coefficientLatex(width, h, numerator, divisor, paren(latexNumber(mean.value)), '-')} = ${latexNumber(approx)}`
    ),
  ]
}

/** Pasos de f⁽⁴⁾, M₄ y la cota. */
export function boundBlocks(fn, M4, samplingPoints, width, h, numerator, divisor, bound) {
  const blocks = [text('La cota usa la cuarta derivada:'), math(`f^{(4)}(x) = ${fn.fourth.latex}`)]
  const search =
    `M₄ es el mayor valor de |f⁽⁴⁾(x)| en el intervalo; se busca evaluando f⁽⁴⁾ en ${samplingPoints} puntos.`
  if (!M4.substitution) {
    blocks.push(text(`${search} Aquí f⁽⁴⁾ = ${formatNumber(M4.value)} en todo el intervalo, así que M₄ = ${formatNumber(M4.value)}.`))
  } else {
    blocks.push(text(`${search} El mayor valor se alcanzó en x = ${M4.x_display.exact ? M4.x_display.text : M4.x_display.approx}:`))
    blocks.push(math(substitutionLatex(M4.substitution, 'f^{(4)}')))
    blocks.push(math(`M_4 = \\left|f^{(4)}(${shownLatex(M4.x_display)})\\right| = ${latexNumber(M4.value)}`))
  }
  blocks.push(
    text('Se sustituye en la fórmula de la cota:'),
    math(
      `\\frac{(b - a)\\,h^{4}}{${divisor}}\\,M_4 = ${coefficientLatex(width, h, numerator, divisor, latexNumber(M4.value))}` +
        ` = ${latexNumber(bound)}`
    )
  )
  return blocks
}

// --- Modo función: una fila de una regla ---------------------------------------------

function mainSteps(result, rule, row, k, previous) {
  const shape = is38(rule) ? 'cúbica' : 'parábola'
  const size = is38(rule) ? 3 : 2
  const width = [math(stepSizeLatex(result, row, k))]
  if (previous) width.unshift(math(`n_{${k}} = 2 \\cdot n_{${k - 1}} = 2 \\cdot ${previous.n} = ${row.n}`))
  const reuse = previous
    ? ` Los puntos de la fila anterior siguen siendo puntos de división (los de i par), así que su altura ya estaba ` +
      `calculada; sólo se evalúan los ${row.n / 2} puntos nuevos.`
    : ''
  const weights = is38(rule)
    ? 'El peso es 1 en los extremos, 2 donde se tocan dos cúbicas (i múltiplo de 3) y 3 en los demás.'
    : 'El peso es 1 en los extremos, 4 en los puntos impares (el medio de cada parábola) y 2 en los pares interiores (donde se tocan dos parábolas).'
  const steps = [
    {
      title: 'Paso 1. Ancho de cada segmento',
      blocks: [
        text(
          `Se divide [a, b] en n partes iguales. n ${is38(rule) ? 'es múltiplo de 3' : 'es par'}: cada ${shape} ocupa ` +
            `${size} segmentos, así que hay ${row.n / size} ${is38(rule) ? 'cúbicas' : 'parábolas'}.`
        ),
        ...width,
      ],
    },
    {
      title: 'Paso 2. Puntos de división',
      blocks: [text('Cada punto se obtiene sumando i veces el ancho h al límite a: xᵢ = a + i·h.'), { kind: 'division' }],
    },
    {
      title: 'Paso 3. Altura de la curva en cada punto y su peso',
      blocks: [text(`Se reemplaza cada xᵢ en f(x). ${weights}${reuse}`), { kind: 'points' }],
    },
    {
      title: 'Paso 4. Suma ponderada',
      blocks: [text('Se multiplica cada altura por su peso y se suman los resultados.'), math(weightedSumLatex(rule, row))],
    },
    {
      title: 'Paso 5. Resultado',
      blocks: [
        text(`Se multiplica la suma por ${factorText(rule)}.`),
        math(ruleValueLatex(rule, row.h, row.step.bracket, row.S, `S_{${k}}`)),
      ],
    },
  ]
  if (row.estimated_error !== null) {
    const tolerance = formatNumber(result.tolerance)
    const value = formatNumber(row.estimated_error)
    const stops = row.below_tolerance && k >= result.min_rows
    let verdict
    if (!row.below_tolerance) verdict = `${value} > ${tolerance}: se sigue refinando.`
    else if (k < result.min_rows) verdict = `${value} ≤ ${tolerance}, pero todavía no hay ${result.min_rows} filas: se sigue refinando.`
    else verdict = `${value} ≤ ${tolerance}: esta regla ya cumple la tolerancia (el método para cuando todas las reglas pedidas la cumplen en la misma fila).`
    steps.push({
      title: 'Paso 6. Error estimado',
      blocks: [
        text('Cuánto cambió el resultado respecto a la fila anterior.'),
        math(estimatedLatex(row, k)),
        { kind: 'check', ok: stops ? true : null, text: verdict },
      ],
    })
  }
  return steps
}

function errorSteps(result, rule, row, k, previous) {
  const steps = []
  const fn = result.function
  const I = result.integral.value
  const reference = result.integral.kind === 'reference'
  if (row.true_error !== null) {
    const blocks = [
      text(`Diferencia entre el valor ${reference ? 'de referencia' : 'exacto'} I y el aproximado S.`),
      math(`E_t = I - S_{${k}} = ${latexNumber(I)} - ${paren(latexNumber(row.S))} = ${latexNumber(row.true_error)}`),
    ]
    if (row.relative_error !== null) blocks.push(math(relativeErrorLatex(row, I)))
    else blocks.push(note('|I| ≈ 0: el error relativo no se calcula.'))
    if (formatNumber(row.true_error) === '0') blocks.push(text('Eₜ se ve 0: con 6 decimales Simpson coincide con I.'))
    else if (row.true_error < 0) blocks.push(text('Eₜ es negativo: Simpson sobreestimó el área.'))
    else blocks.push(text('Eₜ es positivo: Simpson subestimó el área.'))
    const tiny = tinyErrorNote(row, reference)
    if (tiny) blocks.push(note(tiny))
    steps.push({ title: `Error verdadero${reference ? ' (respecto al valor de referencia)' : ''}`, blocks })
  }

  const divisor = rule.divisor
  const width = result.width_display.latex
  if (row.approx_error !== null && result.mean_fourth) {
    const blocks = approxBlocks(fn, result.mean_fourth, width, row.h, row.coefficient_numerator, divisor, row.approx_error)
    const coincide = row.true_error !== null && formatNumber(row.approx_error) === formatNumber(row.true_error)
    let reading = 'Eₐ estima el error sin conocer la integral exacta.'
    if (coincide) reading += ' Aquí coincide con Eₜ.'
    else if (row.true_error !== null) {
      reading +=
        ` Aquí Eₐ = ${formatNumber(row.approx_error)} y Eₜ = ${formatNumber(row.true_error)}: Eₐ usa el promedio de ` +
        'f⁽⁴⁾, así que sólo coincide con Eₜ cuando f⁽⁴⁾ cambia de forma lineal (f⁽⁵⁾ constante).'
    }
    blocks.push(text(reading))
    steps.push({ title: 'Error aproximado (Chapra)', blocks })
  }

  if (row.bound !== null && result.M4) {
    const blocks = boundBlocks(fn, result.M4, result.sampling_points, width, row.h, row.coefficient_numerator, divisor, row.bound)
    const check = criterionCheck(result, row, {
      derivative: 'f⁽⁴⁾',
      constant: fn.fourth.constant,
      factor: factorText(rule),
    })
    if (check) blocks.push(check)
    steps.push({ title: 'Cota del error', blocks })
  }

  if (row.ratio !== null && previous) {
    const close = Math.abs(row.ratio - rule.expected_ratio) < 0.005
    steps.push({
      title: 'Razón',
      blocks: [
        math(
          `\\frac{E_{t,${k}}}{E_{t,${k - 1}}} = \\frac{${latexNumber(row.true_error)}}{${latexNumber(previous.true_error)}} = ${latexNumber(row.ratio)}`
        ),
        text(
          close
            ? 'El error se dividió entre unas 16 veces al duplicar n, como predice la teoría (error proporcional a h⁴).'
            : `La teoría predice una razón cercana a ${formatNumber(rule.expected_ratio)} (error proporcional a h⁴); ` +
                `aquí es ${formatNumber(row.ratio)}.`
        ),
      ],
    })
  }
  return steps
}

/** Todos los pasos de la fila k de una regla (modo función). */
export function simpsonRowSteps(result, rule, row, k, previous) {
  return [...mainSteps(result, rule, row, k, previous), ...errorSteps(result, rule, row, k, previous)]
}

// --- Comparación con el trapecio e identidad ------------------------------------------

/** «Con n = 2, el trapecio da … y Simpson 1/3 da …: un error 2.1 veces menor.» */
export function trapezoidComparisonText(rule, row) {
  const t = row.trapezoid
  const head = `Con n = ${row.n}, el trapecio da T = ${formatNumber(t.T)}`
  if (t.true_error === null || row.true_error === null) {
    return `${head} y ${rule.name} da S = ${formatNumber(row.S)}.`
  }
  const both = `${head} (Eₜ = ${formatNumber(t.true_error)}) y ${rule.name} da S = ${formatNumber(row.S)} (Eₜ = ${formatNumber(row.true_error)})`
  if (t.times === null || formatNumber(row.true_error) === '0') {
    return `${both}: Simpson ya coincide con I en 6 decimales.`
  }
  return `${both}: un error ${formatNumber(Number(t.times.toFixed(1)))} veces menor.`
}

/** S_n = (4T_n − T_(n/2))/3 con los valores visibles (n es el número de segmentos). */
export function identityLatex(identity) {
  const n = identity.n
  return (
    `S_{${n}} = \\frac{4\\,T_{${n}} - T_{${n / 2}}}{3} = \\frac{4\\left(${identity.T_n_display}\\right) - ${paren(identity.T_half_display)}}{3}` +
    ` = \\frac{${identity.numerator_display}}{3} = ${identity.value_display}`
  )
}

export const IDENTITY_SENTENCE =
  'Simpson 1/3 es el trapecio mejorado con la extrapolación de Richardson: combinar dos trapecios elimina su error de orden h².'
export const NO_IDENTITY_38 = 'Para Simpson 3/8 no hay una identidad tan simple con el trapecio.'

// --- Modo tabla ----------------------------------------------------------------------------

/** Peso de un punto en la tabla: «4», o «1 + 1» en el punto de unión. */
export const pointWeight = (point) => point.weights.map((w) => w.weight).join(' + ')
export const pointRule = (point) => point.weights.map((w) => ruleShort(w.rule)).join(' y ')
export const pointProduct = (point) => point.products.join(' + ')

/** Suma ponderada de una parte: [y₀ + 4y₁ + y₂] = … */
export function partSumLatex(part, points) {
  const terms = []
  const values = []
  for (let i = part.start; i <= part.end; i++) {
    const w = points[i].weights.find((x) => x.rule === part.rule).weight
    terms.push(`${w === 1 ? '' : w}y_{${i}}`)
    values.push(`${w === 1 ? '' : `${w} \\cdot `}${paren(shownLatex(points[i].y_display))}`)
  }
  return `${terms.join(' + ')} = ${values.join(' + ')} = ${part.step.bracket}`
}

/** S de una parte: (h/3)·suma o (3h/8)·suma. */
export function partValueLatex(part, h) {
  const name = `S_{${ruleShort(part.rule)}}`
  return ruleValueLatex({ key: part.rule }, h, part.step.bracket, part.value, name)
}

/** Suma de las partes (combinación). */
export function partsTotalLatex(app) {
  const values = app.parts.map((p) => latexNumber(p.value))
  const relation = app.parts_sum_display === app.total_display ? '=' : '\\approx'
  return `S = S_{1/3} + S_{3/8} = ${values.join(' + ')} ${relation} \\mathbf{${latexNumber(app.total)}}`
}

/** Frase final de la comprobación (una regla o una aplicación del modo tabla). */
export function simpsonConclusion(result, name, n, final) {
  if (!final || final.true_error === null || final.true_error === undefined) return null
  const target = result.integral?.kind === 'reference' ? 'el valor de referencia' : 'la integral exacta'
  const who = result.mode === 'table' ? `Con ${name} y los datos (n = ${n})` : `Con ${name} y n = ${n}`
  if (formatNumber(final.S) === formatNumber(final.I)) return `${who} el resultado coincide con ${target} en 6 decimales.`
  return `${who} el resultado difiere de ${target} en Eₜ = ${formatNumber(final.true_error)} (εₜ = ${percent(final.relative_error)}).`
}
