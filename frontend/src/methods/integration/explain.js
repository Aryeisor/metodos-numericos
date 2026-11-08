// Paso a paso explicado de cada fila (y de cada segmento en modo tabla), como
// datos: [{ title, blocks }] con bloques
//   { kind: 'text', text }              una o dos frases
//   { kind: 'math', latex }             la fórmula con los valores sustituidos
//   { kind: 'note', text }              nota en letra pequeña
//   { kind: 'points' }                  la tabla de puntos de la fila
//   { kind: 'check', latex, ok, text }  comparación con su marca
// La vista (TrapezoidStepDetail) y el PDF recorren la misma lista. Todos los
// números vienen del backend; aquí sólo se escriben.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
import { substitutionLatex } from '../differentiation/formulas'
import {
  approxErrorLatex,
  boundLatex,
  estimatedErrorLatex,
  meanSecondLatex,
  percent,
  ratioLatex,
  recurrenceLatex,
  relativeErrorLatex,
  stepSizeLatex,
  trueErrorLatex,
} from './formulas'

const SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'
/** 12 → «₁₂». */
export const sub = (n) => String(n).replace(/\d/g, (d) => SUBSCRIPTS[d])

const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
const shownLatex = (d) => (d.exact ? d.latex : d.approx)
const inlineH = (h) => (h.exact ? h.latex : `\\left(${h.latex}\\right)`)
const text = (t) => ({ kind: 'text', text: t })
const math = (latex) => ({ kind: 'math', latex })
const note = (t) => ({ kind: 'note', text: t })

/** f(xᵢ) sustituida término a término (las plantillas llegan una vez en result.function). */
export function pointSubstitution(result, point) {
  return {
    x: point.x,
    x_display: point.x_display,
    terms: result.function.substitution_terms.map((t, i) => ({ ...t, value: point.terms[i] })),
    value: point.f,
    all_zero: false,
  }
}

/** xᵢ = a + i·h = 0 + 1·2 = 2. */
export function divisionPointLatex(result, row, point) {
  const x = point.x_display.exact ? `= ${point.x_display.latex}` : `\\approx ${point.x_display.approx}`
  return `x_{${point.i}} = a + ${point.i} \\cdot h = ${paren(result.a_display.latex)} + ${point.i} \\cdot ${inlineH(row.h)} ${x}`
}

/** Nota cuando |Eₜ| se ve 0 a 6 decimales pero εₜ no. */
export function tinyErrorNote(item, reference = false) {
  if (!item || item.true_error === null || item.true_error === undefined) return null
  if (item.true_error === 0 || formatNumber(item.true_error) !== '0') return null
  if (item.relative_error === null || item.relative_error === undefined || formatNumber(item.relative_error) === '0') return null
  return (
    `Eₜ es menor que 0.0000005 y con 6 decimales se ve 0; en porcentaje del valor ${reference ? 'de referencia' : 'exacto'} ` +
    `es ${percent(item.relative_error)}.`
  )
}

/** Puntos que se ven por defecto: todos, o los 8 primeros y los 8 últimos («…» entre ellos). */
export function foldedPoints(step, showAll = false) {
  const points = step.points
  const limit = step.fold ?? 16
  if (showAll || points.length <= limit) return points
  return [...points.slice(0, 8), null, ...points.slice(-8)]
}

/** Todos los puntos llegaron del backend (≤ 1024) y se pueden mostrar. */
export const canShowAll = (step) => step.points.length === step.count && step.count > (step.fold ?? 16)

// --- Fila 1 ---------------------------------------------------------------------

/** 1·f(x₀) + 2·f(x₁) + 1·f(x₂) = 1·0.2 + 2·(2.456) + 1·0.232 = 0.2 + 4.912 + 0.232 = 5.344. */
function weightedSumLatex(row) {
  const step = row.step
  if (step.points.length === step.count && step.count <= step.fold) {
    const symbolic = step.points.map((p) => `${p.weight} \\cdot f(x_{${p.i}})`).join(' + ')
    const values = step.points.map((p) => `${p.weight} \\cdot ${paren(p.f_display)}`).join(' + ')
    const products = step.points.map((p, i) => (i === 0 ? p.product : p.product.startsWith('-') ? `- ${p.product.slice(1)}` : `+ ${p.product}`)).join(' ')
    const middle = step.points.length > 1 ? ` = ${products}` : ''
    return `${symbolic} = ${values}${middle} = ${step.bracket}`
  }
  const [first, last] = step.ends.map(paren)
  const sums = step.sums.map((s) => `${s.weight}\\left(${s.display}\\right)`)
  return (
    `f(x_0) + 2\\sum_{i=1}^{${row.n - 1}} f(x_i) + f(x_{${row.n}}) = ` +
    `${[first, ...sums, last].join(' + ')} = ${step.bracket}`
  )
}

function areaLatex(row) {
  const step = row.step
  const h = row.h.exact ? row.h.latex : row.h.approx
  const half = step.factor_h.exact ? step.factor_h.latex : step.factor_h.approx
  return (
    `T_{1} = \\frac{h}{2} \\cdot \\text{suma} = \\frac{${h}}{2} \\cdot ${paren(step.bracket)} = ` +
    `${half} \\cdot ${paren(step.bracket)} = \\mathbf{${latexNumber(row.T)}}`
  )
}

function firstRowSteps(result, row) {
  const many = row.n === 1 ? 'Con un solo trapecio' : `Con ${row.n} trapecios`
  return [
    {
      title: 'Paso 1. Ancho de cada trapecio',
      blocks: [text('Se divide el intervalo [a, b] en n partes iguales.'), math(stepSizeLatex(result, row, 1))],
    },
    {
      title: 'Paso 2. Puntos de división',
      blocks: [text('Cada punto se obtiene sumando i veces el ancho h al límite a: xᵢ = a + i·h.'), { kind: 'division' }],
    },
    {
      title: 'Paso 3. Altura de la curva en cada punto',
      blocks: [
        text('Se reemplaza cada xᵢ en f(x). El peso es 1 en los extremos y 2 en los puntos interiores (se cuentan dos veces).'),
        { kind: 'points' },
      ],
    },
    {
      title: 'Paso 4. Suma ponderada',
      blocks: [text('Se multiplica cada altura por su peso y se suman los resultados.'), math(weightedSumLatex(row))],
    },
    {
      title: 'Paso 5. Área total',
      blocks: [
        text('Se multiplica la suma por h/2.'),
        math(areaLatex(row)),
        text(`${many} el área es ${formatNumber(row.T)}.`),
      ],
    },
  ]
}

// --- Filas siguientes (recurrencia) -----------------------------------------------

/** Σ de los puntos nuevos: f(0.5) + f(1.5) = 0.25 + 2.25 = 2.5 (en verde). */
function newSumLatex(row) {
  const step = row.step
  const sum = colorize(paren(step.sum), CURRENT_COLOR)
  if (step.points.length !== step.count || step.count > step.fold) return `\\sum_{\\text{nuevos}} f(x_i) = ${sum}`
  const at = (p) => `f(${shownLatex(p.x_display)})`
  const symbolic = step.points.map(at).join(' + ')
  const values = step.points.map((p, i) => {
    const v = colorize(p.f_display.startsWith('-') ? p.f_display.slice(1) : p.f_display, CURRENT_COLOR)
    if (i === 0) return p.f_display.startsWith('-') ? `-${v}` : v
    return `${p.f_display.startsWith('-') ? '-' : '+'} ${v}`
  })
  const middle = step.points.length > 1 ? ` = ${values.join(' ')}` : ''
  return `\\sum_{\\text{nuevos}} f(x_i) = ${symbolic}${middle} = ${sum}`
}

function recurrenceSteps(result, row, k, previous) {
  const estimated = []
  if (row.estimated_error !== null) {
    const tolerance = formatNumber(result.tolerance)
    const value = formatNumber(row.estimated_error)
    const stops = row.below_tolerance && k >= result.min_rows
    let verdict
    if (!row.below_tolerance) verdict = `${value} > ${tolerance}: se sigue refinando.`
    else if (stops) verdict = `${value} ≤ ${tolerance} y ya hay ${result.min_rows} filas: el método se detiene.`
    else verdict = `${value} ≤ ${tolerance}, pero todavía no hay ${result.min_rows} filas: se sigue refinando.`
    estimated.push({
      title: 'Paso 6. Error estimado',
      blocks: [
        text(
          `Cuánto cambió el resultado respecto a la fila anterior; si es menor que la tolerancia (y ya hay ` +
            `${result.min_rows} filas), el método se detiene.`
        ),
        math(estimatedErrorLatex(row, k)),
        { kind: 'check', ok: stops ? true : null, text: verdict },
      ],
    })
  }
  return [
    {
      title: 'Paso 1. Nuevo ancho',
      blocks: [
        text('Se duplica el número de trapecios y el ancho queda a la mitad.'),
        math(`n_{${k}} = 2 \\cdot n_{${k - 1}} = 2 \\cdot ${previous.n} = ${row.n}`),
        math(stepSizeLatex(result, row, k)),
      ],
    },
    {
      title: 'Paso 2. Por qué sólo se evalúan los puntos nuevos',
      blocks: [
        text(
          `Los puntos de la fila anterior siguen siendo puntos de división, así que su suma ya está incluida en T${sub(k - 1)}. ` +
            'Sólo aparecen puntos nuevos en la mitad de cada trapecio anterior.'
        ),
      ],
    },
    {
      title: 'Paso 3. Puntos nuevos y su altura',
      blocks: [
        text('Cada punto nuevo es xᵢ = a + i·h con i impar (la mitad de un trapecio anterior); se reemplaza en f(x).'),
        { kind: 'points' },
      ],
    },
    { title: 'Paso 4. Suma de los puntos nuevos', blocks: [math(newSumLatex(row))] },
    {
      title: 'Paso 5. Nuevo valor',
      blocks: [
        math(recurrenceLatex(row, k)),
        text(
          `T${sub(k - 1)}/2 aprovecha todo lo ya calculado; h${sub(k)}·Σ agrega la contribución de los puntos nuevos.`
        ),
      ],
    },
    ...estimated,
  ]
}

// --- Errores (todas las filas) ----------------------------------------------------

/**
 * Comparación |Eₜ| con la cota. `derivative` es la derivada de la cota y
 * `constant` si es constante (la igualdad se explica por eso); `factor`, el
 * factor de R (h/2 en el trapecio, h/3 o 3h/8 en Simpson).
 */
function criterionCheck(result, item, { derivative = "f''", constant = result.function?.second.constant, factor = 'h/2' } = {}) {
  if (item.within_bound === null || item.within_bound === undefined) return null
  const size = latexNumber(Math.abs(item.true_error))
  const bound = latexNumber(item.bound)
  if (!item.within_bound) {
    return {
      kind: 'check',
      ok: false,
      latex: `|E_t| = ${size} > ${bound} = \\text{cota}`,
      text: '|Eₜ| supera la cota: revisa los datos (la teoría dice que no debería pasar).',
    }
  }
  if (item.equals_bound) {
    return {
      kind: 'check',
      ok: true,
      latex: `|E_t| = ${size} = ${bound} = \\text{cota}`,
      text: constant ? `|Eₜ| = cota ✔ (la igualdad ocurre porque ${derivative} es constante).` : '|Eₜ| = cota ✔.',
    }
  }
  if (item.by_rounding) {
    return {
      kind: 'check',
      ok: true,
      latex: `|E_t| = ${size} \\le ${bound} + R \\quad (R = ${latexNumber(item.rounding)})`,
      text:
        `|Eₜ| supera la cota sólo por el redondeo de la computadora, R = 2ε·Σ|wᵢ·f(xᵢ)|·${factor}: dentro de ese margen se cumple.`,
    }
  }
  return {
    kind: 'check',
    ok: true,
    latex: `|E_t| = ${size} \\le ${bound} = \\text{cota}`,
    text: 'El error verdadero quedó por debajo de la cota, como predice la teoría.',
  }
}

function errorSteps(result, row, k, previous) {
  const steps = []
  const I = result.integral.value
  const reference = result.integral.kind === 'reference'
  if (row.true_error !== null) {
    const blocks = [
      text(`Diferencia entre el valor ${reference ? 'de referencia' : 'exacto'} I y el aproximado T.`),
      math(trueErrorLatex(row, I, k)),
    ]
    if (row.relative_error !== null) blocks.push(math(relativeErrorLatex(row, I)))
    else blocks.push(note('|I| ≈ 0: el error relativo no se calcula.'))
    if (formatNumber(row.true_error) === '0') blocks.push(text('Eₜ se ve 0: con 6 decimales el trapecio coincide con I.'))
    else if (row.true_error < 0) blocks.push(text('Eₜ es negativo: el trapecio sobreestimó el área.'))
    else blocks.push(text('Eₜ es positivo: el trapecio subestimó el área.'))
    const tiny = tinyErrorNote(row, reference)
    if (tiny) blocks.push(note(tiny))
    steps.push({ title: `Error verdadero${reference ? ' (respecto al valor de referencia)' : ''}`, blocks })
  }

  const fn = result.function
  const m = result.mean_second
  if (row.approx_error !== null && m) {
    const coincide = row.true_error !== null && formatNumber(row.approx_error) === formatNumber(row.true_error)
    let reading = 'Eₐ estima el error sin conocer la integral exacta.'
    if (coincide) reading += ` Aquí coincide con Eₜ${fn.second.constant ? " porque f'' es constante" : ''}.`
    else if (row.true_error !== null) {
      reading += ` Aquí Eₐ = ${formatNumber(row.approx_error)} y Eₜ = ${formatNumber(row.true_error)}: ` +
        "Eₐ usa el promedio de f'', así que sólo coincide con Eₜ cuando f'' es constante."
    }
    steps.push({
      title: 'Error aproximado (Chapra)',
      blocks: [
        text('Primero se evalúa la primera derivada en los límites a y b:'),
        math(`f'(x) = ${fn.first.latex}`),
        math(substitutionLatex(m.fb_substitution, "f'")),
        math(substitutionLatex(m.fa_substitution, "f'")),
        text('Con esos valores se obtiene el promedio de la segunda derivada:'),
        math(meanSecondLatex(result)),
        note(
          "Este promedio sale de que la integral de f'' entre a y b es f'(b) − f'(a); al dividir entre el ancho del " +
            'intervalo se obtiene su valor medio.'
        ),
        text('Se sustituye en la fórmula de Chapra:'),
        math(approxErrorLatex(result, row)),
        text(reading),
      ],
    })
  }

  const M2 = result.M2
  if (row.bound !== null && M2) {
    const blocks = [
      text('La cota usa la segunda derivada:'),
      math(`f''(x) = ${fn.second.latex}`),
    ]
    const search = `M₂ es el mayor valor de |f''(x)| en [a, b]; se busca evaluando f'' en ${result.sampling_points} puntos del intervalo.`
    if (!M2.substitution) {
      blocks.push(text(`${search} Aquí f'' = ${formatNumber(M2.value)} en todo el intervalo, así que M₂ = ${formatNumber(M2.value)}.`))
    } else {
      const x = shownLatex(M2.x_display)
      blocks.push(text(`${search} El mayor valor se alcanzó en x = ${M2.x_display.exact ? M2.x_display.text : M2.x_display.approx}:`))
      blocks.push(math(substitutionLatex(M2.substitution, "f''")))
      blocks.push(math(`M_2 = |f''(${x})| = ${latexNumber(M2.value)}`))
    }
    blocks.push(text('Se sustituye en la fórmula de la cota:'), math(boundLatex(result, row)))
    const check = criterionCheck(result, row)
    if (check) blocks.push(check)
    steps.push({ title: 'Cota del error', blocks })
  }

  if (row.ratio !== null && previous) {
    const close = Math.abs(row.ratio - result.rule.expected_ratio) < 0.02
    steps.push({
      title: 'Razón',
      blocks: [
        math(ratioLatex(row, previous, k)),
        text(
          close
            ? 'El error se dividió entre 4 al duplicar n, como predice la teoría (error proporcional a h²).'
            : `La teoría predice una razón cercana a ${formatNumber(result.rule.expected_ratio)} (error proporcional a h²); ` +
                `aquí es ${formatNumber(row.ratio)}.`
        ),
      ],
    })
  }
  return steps
}

/** Todos los pasos de la fila k del modo función. */
export function rowSteps(result, row, k, previous) {
  const main = row.step.kind === 'formula' ? firstRowSteps(result, row) : recurrenceSteps(result, row, k, previous)
  return [...main, ...errorSteps(result, row, k, previous)]
}

export { criterionCheck }

// --- Comprobación ------------------------------------------------------------------

/** Por qué no hay antiderivada y qué es el valor de referencia. */
export function referenceExplanation(integral) {
  const what =
    'I se calcula numéricamente con 30 dígitos de precisión (mucho más que los 6 que se muestran) y se usa como ' +
    'valor de referencia en lugar del exacto.'
  if (integral.timed_out) {
    return `La integración simbólica superó el límite de tiempo, así que no se obtuvo F(x): ${what}`
  }
  const why = integral.special ? `${integral.special}.` : 'sympy no encontró una antiderivada utilizable en [a, b].'
  return (
    `No hay una antiderivada elemental: ${why} Es decir, la antiderivada de f no se puede escribir con funciones ` +
    `elementales (potencias, exponenciales, logaritmos, trigonométricas), así que I no sale de F(b) − F(a): ${what}`
  )
}

/** Frase final de la comprobación. */
export function conclusionText(result, final) {
  if (!final || final.true_error === null || final.true_error === undefined) return null
  const target = result.integral?.kind === 'reference' ? 'el valor de referencia' : 'la integral exacta'
  const who =
    result.mode === 'table'
      ? `Con los ${result.iterations.length} trapecios de los datos`
      : `Con n = ${result.iterations.at(-1).extra.n} trapecios`
  if (formatNumber(final.T) === formatNumber(final.I)) return `${who} el resultado coincide con ${target} en 6 decimales.`
  return (
    `${who} el resultado difiere de ${target} en Eₜ = ${formatNumber(final.true_error)} ` +
    `(εₜ = ${percent(final.relative_error)}).`
  )
}

// --- Modo tabla: un segmento ----------------------------------------------------------

export function segmentSteps(segment, previous) {
  const [x0, x1] = segment.x_display.map(shownLatex)
  const [y0, y1] = segment.y_display.map(shownLatex)
  const i = segment.i
  const width = shownLatex(segment.width)
  const cumulative =
    previous === null
      ? `\\text{Acumulada}_{${i}} = A_{${i}} = ${segment.area_display}`
      : `\\text{Acumulada}_{${i}} = \\text{Acumulada}_{${i - 1}} + A_{${i}} = ` +
        `${colorize(latexNumber(previous.cumulative), PREVIOUS_COLOR)} + ${colorize(paren(segment.area_display), CURRENT_COLOR)} = ` +
        `${latexNumber(segment.cumulative)}`
  return [
    {
      title: 'Ancho del segmento',
      blocks: [math(`h_{${i}} = x_{${i + 1}} - x_{${i}} = ${x1} - ${paren(x0)} = ${width}`)],
    },
    {
      title: 'Alturas',
      blocks: [text('Los dos datos del segmento son las alturas izquierda y derecha del trapecio.'), math(`y_{${i}} = ${y0},\\quad y_{${i + 1}} = ${y1}`)],
    },
    {
      title: 'Área del trapecio',
      blocks: [text('Ancho por el promedio de las dos alturas.'), math(segmentAreaLatex(segment))],
    },
    {
      title: 'Área acumulada',
      blocks: [text('Se suma el área de este trapecio a la de los anteriores.'), math(cumulative)],
    },
  ]
}

function segmentAreaLatex(segment) {
  const [y0, y1] = segment.y_display.map((y) => paren(shownLatex(y)))
  const width = shownLatex(segment.width)
  const i = segment.i
  return (
    `A_{${i}} = h_{${i}} \\cdot \\frac{y_{${i}} + y_{${i + 1}}}{2} = ${width} \\cdot \\frac{${y0} + ${y1}}{2} = ` +
    `${width} \\cdot \\frac{${paren(segment.pair_sum)}}{2} = ${segment.area_display}`
  )
}
