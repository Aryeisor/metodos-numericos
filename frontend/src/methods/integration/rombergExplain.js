// Paso a paso explicado de cada fila de Romberg, como datos con los mismos
// bloques que el trapecio (explain.js): { kind: 'text' | 'math' | 'note' |
// 'points' | 'division' | 'check' }. Cada fila se agrupa en partes plegables
// [{ title, steps: [{ title, blocks }] }]:
//   1. el trapecio nuevo R_i,1 (el paso a paso del trapecio, reutilizado);
//   2. cada extrapolación R_i,k (Richardson);
//   3. el error estimado de la diagonal frente a la tolerancia;
//   4. Eₜ y εₜ de la diagonal.
// La vista (RombergRowSteps) y el PDF recorren la misma lista. Todos los
// números vienen del backend; aquí sólo se escriben.
import { formatNumber } from '../../utils/iterationSteps'
import { CURRENT_COLOR, PREVIOUS_COLOR, colorize, latexNumber } from '../../utils/latexFormulas'
import { firstRowSteps, recurrenceSteps, sub, tinyErrorNote } from './explain'
import { percent, recurrenceLatex, stepSizeLatex } from './formulas'

const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
const shownText = (d) => (d.exact ? d.text : d.approx)
const text = (t) => ({ kind: 'text', text: t })
const math = (latex) => ({ kind: 'math', latex })
const note = (t) => ({ kind: 'note', text: t })
const SUPERSCRIPTS = { 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }
const power = (p) => `h${String(p).replace(/\d/g, (d) => SUPERSCRIPTS[d])}`

/** R_{i,k} en LaTeX y en texto («R₃,₂»). */
export const cellLatex = (i, k) => `R_{${i},${k}}`
export const cellText = (i, k) => `R${sub(i)},${sub(k)}`

// El paso a paso del trapecio con los nombres de Romberg: R_{i,1} en lugar de T_i.
const NAMES = { latex: (j) => cellLatex(j, 1), text: (j) => cellText(j, 1) }

/** «combina … para eliminar el término h² del error (pasa a O(h⁴))». */
export function eliminationText(k) {
  return (
    `Combina dos aproximaciones de la columna anterior para eliminar el término ${power(2 * (k - 1))} del error ` +
    `(pasa a O(${power(2 * k)})).`
  )
}

/** R_3,3 = (16·R_3,2 − R_2,2)/15 = (16(1.62346667) − 1.36746667)/15 = … ≈ 1.640533. */
export function extrapolationLatex(i, e) {
  const k = e.k
  const same = colorize(paren(e.same), CURRENT_COLOR)
  const previous = colorize(paren(e.previous), PREVIOUS_COLOR)
  const end = e.decimals === 6 && e.coherent ? `\\mathbf{${latexNumber(e.value)}}` : `${e.quotient} \\approx \\mathbf{${latexNumber(e.value)}}`
  return (
    `${cellLatex(i, k)} = \\frac{${e.factor}\\,${cellLatex(i, k - 1)} - ${cellLatex(i - 1, k - 1)}}{${e.divisor}} = ` +
    `\\frac{${e.factor}\\left(${same}\\right) - ${previous}}{${e.divisor}} = ` +
    `\\frac{${e.product} - ${paren(e.previous)}}{${e.divisor}} = \\frac{${paren(e.numerator)}}{${e.divisor}} = ${end}`
  )
}

// --- 1. El trapecio nuevo -------------------------------------------------------------

/** Modo tabla: R_i,1 con un subconjunto de los datos. */
function tableTrapezoidSteps(result, row, previous) {
  const trap = row.trapezoid
  const step = trap.step
  const used = `Fila ${row.i}: puntos ${listText(row.data_points)} de la tabla`
  if (row.i === 1) {
    const [y0, y1] = step.ends.map(paren)
    const last = row.data_points.at(-1)
    const h = trap.h.exact ? trap.h.latex : trap.h.approx
    const half = step.factor_h.exact ? step.factor_h.latex : step.factor_h.approx
    return [
      {
        title: 'Datos que usa',
        blocks: [text(`${used} (los extremos): un solo trapecio de ancho h = b − a.`)],
      },
      {
        title: 'Área del trapecio',
        blocks: [
          text('Ancho por el promedio de las dos alturas.'),
          math(stepSizeLatex(result, trap, 1)),
          math(
            `${cellLatex(1, 1)} = \\frac{h}{2}\\left[y_{0} + y_{${last}}\\right] = \\frac{${h}}{2}\\left[${y0} + ${y1}\\right] = ` +
              `${half} \\cdot ${paren(step.bracket)} = \\mathbf{${latexNumber(trap.T)}}`
          ),
        ],
      },
    ]
  }
  const newSum = step.points
    .map((p, idx) => {
      const v = colorize(p.f_display.startsWith('-') ? p.f_display.slice(1) : p.f_display, CURRENT_COLOR)
      return idx === 0 ? (p.f_display.startsWith('-') ? `-${v}` : v) : `${p.f_display.startsWith('-') ? '-' : '+'} ${v}`
    })
    .join(' ')
  const symbolic = step.points.map((p) => `y_{${p.i}}`).join(' + ')
  return [
    {
      title: 'Datos que usa',
      blocks: [
        text(
          `${used}. Los de la fila ${row.i - 1} ya están en ${cellText(row.i - 1, 1)}; los nuevos son ` +
            `${listText(row.new_points)} (en la mitad de cada segmento anterior).`
        ),
      ],
    },
    {
      title: 'Nuevo ancho',
      blocks: [
        text('Se duplica el número de segmentos y el ancho queda a la mitad.'),
        math(`n_{${row.i}} = 2 \\cdot n_{${row.i - 1}} = 2 \\cdot ${previous.n} = ${row.n}`),
        math(stepSizeLatex(result, trap, row.i)),
      ],
    },
    {
      title: 'Suma de los datos nuevos',
      blocks: [math(`\\sum_{\\text{nuevos}} y_j = ${symbolic}${step.points.length > 1 ? ` = ${newSum}` : ''} = ${colorize(paren(step.sum), CURRENT_COLOR)}`)],
    },
    {
      title: 'Nuevo valor',
      blocks: [
        math(recurrenceLatex(trap, row.i, NAMES.latex, 'y_j')),
        text(`${cellText(row.i - 1, 1)}/2 aprovecha lo ya calculado; h${sub(row.i)}·Σ agrega los datos nuevos.`),
      ],
    },
  ]
}

function listText(indices) {
  if (indices.length === 1) return String(indices[0])
  if (indices.length > 9) return `${indices.slice(0, 4).join(', ')}, …, ${indices.at(-1)}`
  return `${indices.slice(0, -1).join(', ')} y ${indices.at(-1)}`
}

function trapezoidSteps(result, row, previous) {
  if (result.mode === 'table') return tableTrapezoidSteps(result, row, previous)
  return row.i === 1
    ? firstRowSteps(result, row.trapezoid, NAMES)
    : recurrenceSteps(result, row.trapezoid, row.i, previous.trapezoid, NAMES)
}

// --- 2. Extrapolaciones ---------------------------------------------------------------

function extrapolationSteps(result, row, e) {
  const col = result.columns[e.k - 1]
  const blocks = [
    text(eliminationText(e.k)),
    text(
      `${cellText(row.i, e.k)} es la columna ${e.k} (${col.name}, ${col.order_text}). En verde, ${cellText(row.i, e.k - 1)} ` +
        `(misma fila, recién calculado); en azul, ${cellText(row.i - 1, e.k - 1)} (fila anterior).`
    ),
    math(extrapolationLatex(row.i, e)),
  ]
  if (e.decimals > 6) {
    blocks.push(
      note(
        `Con ${e.decimals} decimales: con 6, el resultado de los valores que se ven no coincidiría con el valor ` +
          `guardado (${formatNumber(e.value)}).`
      )
    )
  }
  return [{ title: `Extrapolación ${cellText(row.i, e.k)}`, blocks }]
}

// --- 3. Error estimado ----------------------------------------------------------------

function verdict(result, row) {
  if (result.mode === 'table') {
    return {
      ok: null,
      text: 'En el modo tabla no hay criterio de parada: la cantidad de filas la fija la cantidad de datos.',
    }
  }
  const tolerance = formatNumber(result.tolerance)
  const value = formatNumber(row.estimated_error)
  const last = row.i === result.iterations.length
  if (!row.below_tolerance) {
    return {
      ok: last ? false : null,
      text: last ? `${value} > ${tolerance}: se alcanzó el máximo de filas sin cumplir la tolerancia.` : `${value} > ${tolerance}: se agrega otra fila.`,
    }
  }
  if (row.i >= result.min_rows) return { ok: true, text: `${value} ≤ ${tolerance} y ya hay ${result.min_rows} filas: el método se detiene.` }
  return { ok: null, text: `${value} ≤ ${tolerance}, pero todavía no hay ${result.min_rows} filas: se agrega otra fila.` }
}

export function estimatedErrorLatex(row) {
  const i = row.i
  return (
    `\\left|${cellLatex(i, i)} - ${cellLatex(i - 1, i - 1)}\\right| = ` +
    `\\left|${colorize(latexNumber(row.best), CURRENT_COLOR)} - ${colorize(paren(latexNumber(row.previous_best)), PREVIOUS_COLOR)}\\right|` +
    ` = ${latexNumber(row.estimated_error)}`
  )
}

function approxErrorLatex(row) {
  const i = row.i
  return (
    `\\varepsilon_a = \\left|\\frac{${cellLatex(i, i)} - ${cellLatex(i - 1, i - 1)}}{${cellLatex(i, i)}}\\right| \\cdot 100\\,\\% = ` +
    `\\frac{${latexNumber(row.estimated_error)}}{${latexNumber(Math.abs(row.best))}} \\cdot 100\\,\\% = ${latexNumber(row.approx_error)}\\,\\%`
  )
}

function estimatedSteps(result, row) {
  if (row.estimated_error === null) {
    return [{ title: 'Error estimado', blocks: [text('En la fila 1 no hay fila anterior con qué comparar: el error estimado es «—».')] }]
  }
  const v = verdict(result, row)
  const blocks = [
    text('Cuánto cambió el mejor valor (la diagonal) respecto a la fila anterior; es el criterio de parada.'),
    math(estimatedErrorLatex(row)),
    { kind: 'check', ok: v.ok, text: v.text },
  ]
  if (row.approx_error !== null) {
    blocks.push(text('El error aproximado de Chapra es el mismo cambio en porcentaje del valor nuevo (sólo informa):'), math(approxErrorLatex(row)))
  } else {
    blocks.push(note('|Rᵢ,ᵢ| ≈ 0: el error aproximado εₐ no se calcula.'))
  }
  return [{ title: 'Error estimado', blocks }]
}

// --- 4. Error verdadero ---------------------------------------------------------------

function trueErrorSteps(result, row) {
  if (row.true_error === null) return []
  const I = result.integral.value
  const reference = result.integral.kind === 'reference'
  const i = row.i
  const blocks = [
    text(`Diferencia entre el valor ${reference ? 'de referencia' : 'exacto'} I y el mejor valor de la fila.`),
    math(`E_t = I - ${cellLatex(i, i)} = ${latexNumber(I)} - ${paren(latexNumber(row.best))} = ${latexNumber(row.true_error)}`),
  ]
  if (row.relative_error !== null) {
    blocks.push(
      math(
        `\\varepsilon_t = \\frac{|E_t|}{|I|} \\cdot 100\\,\\% = \\frac{${latexNumber(Math.abs(row.true_error))}}{${latexNumber(Math.abs(I))}}` +
          ` \\cdot 100\\,\\% = ${latexNumber(row.relative_error)}\\,\\%`
      )
    )
  } else blocks.push(note('|I| ≈ 0: el error relativo no se calcula.'))
  if (formatNumber(row.true_error) === '0') blocks.push(text('Eₜ se ve 0: con 6 decimales la diagonal coincide con I.'))
  else if (row.true_error < 0) blocks.push(text('Eₜ es negativo: la aproximación se pasó (sobreestima).'))
  else blocks.push(text('Eₜ es positivo: la aproximación se quedó corta (subestima).'))
  const tiny = tinyErrorNote(row, reference)
  if (tiny) blocks.push(note(tiny))
  return [{ title: `Error verdadero${reference ? ' (respecto al valor de referencia)' : ''}`, blocks }]
}

/** Las partes plegables de la fila (ver el comentario del inicio). */
export function rombergRowGroups(result, row, previous) {
  const groups = [{ title: `1. El trapecio nuevo ${cellText(row.i, 1)} (n = ${row.n})`, steps: trapezoidSteps(result, row, previous) }]
  row.extrapolations.forEach((e, idx) => {
    groups.push({ title: `${idx + 2}. Extrapolación ${cellText(row.i, e.k)} (${result.columns[e.k - 1].name})`, steps: extrapolationSteps(result, row, e) })
  })
  if (row.i === 1) {
    groups[0].steps.push({
      title: 'Sin extrapolaciones',
      blocks: [text(`En la fila 1 no hay fila anterior: ${cellText(1, 1)} es el mejor valor de la fila.`)],
    })
  }
  let next = groups.length + 1
  groups.push({ title: `${next}. Error estimado`, steps: estimatedSteps(result, row) })
  next += 1
  const errors = trueErrorSteps(result, row)
  if (errors.length) groups.push({ title: `${next}. Eₜ y εₜ de la diagonal`, steps: errors })
  return groups
}

// --- Resumen y comprobación -----------------------------------------------------------

/** Frase final de la comprobación. */
export function rombergConclusion(result, final) {
  if (!final || final.true_error === null || final.true_error === undefined) return null
  const target = result.integral?.kind === 'reference' ? 'el valor de referencia' : 'la integral exacta'
  const rows = result.iterations.length
  const who = `Con ${rows} ${rows === 1 ? 'fila' : 'filas'} (${result.evaluations} ${result.mode === 'table' ? 'datos' : 'evaluaciones de f'})`
  if (formatNumber(final.R) === formatNumber(final.I)) return `${who} el mejor valor coincide con ${target} en 6 decimales.`
  return `${who} el mejor valor difiere de ${target} en Eₜ = ${formatNumber(final.true_error)} (εₜ = ${percent(final.relative_error)}).`
}

export const IDENTITY_SENTENCE =
  'La columna 2 es exactamente Simpson: Simpson es un trapecio mejorado una vez; Romberg sigue mejorando.'

export const COST_NOTE = 'El mínimo de 6 filas es un requisito del curso, no del método: Romberg podría detenerse antes.'

/** Datos que usa cada fila en modo tabla: «puntos 0, 4 y 8». */
export const dataPointsText = (row) => `puntos ${listText(row.data_points)}`

export { shownText }

// Fórmulas del método (vista y PDF).
export const RECURRENCE_LATEX = String.raw`R_{1,1} = \frac{h}{2}\left[f(a) + f(b)\right],\qquad R_{i,1} = \frac{R_{i-1,1}}{2} + h_i \sum_{\text{nuevos}} f(x_j)`
export const RICHARDSON_LATEX = String.raw`R_{i,k} = \frac{4^{k-1}\,R_{i,k-1} - R_{i-1,k-1}}{4^{k-1} - 1},\qquad k = 2, \dots, i`
export const STOP_LATEX = String.raw`\text{Error estimado} = \left|R_{i,i} - R_{i-1,i-1}\right|,\qquad \varepsilon_a = \left|\frac{R_{i,i} - R_{i-1,i-1}}{R_{i,i}}\right| \cdot 100\,\%`
