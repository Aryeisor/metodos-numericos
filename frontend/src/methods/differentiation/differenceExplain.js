// Paso a paso explicado de las diferencias progresiva y regresiva, como datos
// [{ title, blocks }] con los mismos bloques que integración (explain.js):
//   { kind: 'text', text }  { kind: 'math', latex }  { kind: 'note', text }
//   { kind: 'check', latex, ok, text }
// La vista (TrapezoidStepDetail con `customSteps`) y el PDF recorren la misma
// lista. Todos los números vienen del backend; aquí sólo se escriben.
// Sirve para una fila (modo función) y para un punto (modo tabla).
import { formatNumber } from '../../utils/iterationSteps'
import { latexNumber } from '../../utils/latexFormulas'
import { signedSum } from '../polynomial/formulas'
import {
  estimatedErrorLatex,
  evaluationLatex,
  nodeValueLatex,
  ratioLatex,
  stepSizeLatex,
  substitutionLatex,
} from './formulas'

const text = (t) => ({ kind: 'text', text: t })
const math = (latex) => ({ kind: 'math', latex })
const note = (t) => ({ kind: 'note', text: t })
const paren = (latex) => (latex.startsWith('-') ? `\\left(${latex}\\right)` : latex)
const shown = (d) => (d.exact ? d.latex : d.approx)
const shownText = (d) => (d.exact ? d.text : d.approx)
const isForward = (formula) => formula.key === 'forward'
const byDistance = (points) => [...points].sort((a, b) => Math.abs(a.offset) - Math.abs(b.offset))

const SUPERSCRIPTS = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }
/** 1.2e-8 → «1.2×10⁻⁸». */
export function scientific(value) {
  const [mantissa, exponent] = value.toExponential(1).split('e')
  return `${mantissa}×10${String(Number(exponent)).replace(/[-\d]/g, (c) => SUPERSCRIPTS[c])}`
}

/** Nota cuando el error real se ve 0 a 6 decimales sin serlo. */
export function tinyRealErrorNote(item) {
  const error = item?.real_error
  if (error === null || error === undefined || error === 0 || formatNumber(error) !== '0') return null
  return `El error real es menor que 0.0000005 y con 6 decimales se ve 0; su valor es ${scientific(error)}.`
}

/** f'' constante (su expresión no tiene x): M es ese valor en todo el intervalo. */
const isConstant = (latex) => !/x/.test(latex)

// --- Contexto de cada modo ------------------------------------------------------
// Lo que cambia entre una fila (modo función) y un punto (modo tabla).

/** Fila k del modo función. */
export function functionContext(result, k) {
  const step = result.iterations[k - 1]
  return {
    table: false,
    label: k,
    h: step.extra.h,
    h0: result.iterations[0].extra.h,
    at: 'x_0',
    atText: 'x₀',
    name: (p) => p.role,
    symbol: (formula) => `${formula.symbol_latex}_{${k}}`,
    template: result.function.template,
    exact: result.exact,
    exactSource: result.verification.substitution,
    curvature: result.curvature,
  }
}

/** Punto i del modo tabla. */
export function tableContext(result, formula, i) {
  const extra = result.iterations[i - 1].extra
  return {
    table: true,
    label: i,
    h: extra[formula.key].h,
    at: `x_{${i}}`,
    atText: `x${i}`,
    name: (p) => `x_{${p.index + 1}}`,
    symbol: (f) => `${f.symbol_latex}(x_{${i}})`,
    template: null,
    exact: extra.exact,
    exactSource: result.verification.substitutions?.[i - 1] ?? null,
    curvature: extra.curvature ?? null,
  }
}

// --- Pasos ------------------------------------------------------------------------

function stepSizeStep(formula, item, ctx) {
  if (!ctx.table) {
    const blocks = [
      text('Distancia entre x₀ y el punto vecino. En cada fila se divide entre 2 para acercar el punto vecino.'),
      math(stepSizeLatex(ctx.label, ctx.h, ctx.h0)),
    ]
    if (ctx.label === 1) blocks.push(text('Es el paso inicial que escribiste.'))
    return { title: 'El paso h', blocks }
  }
  // Modo tabla: h es la distancia entre los dos datos.
  const [here, neighbor] = byDistance(item.points)
  const [right, left] = neighbor.offset > 0 ? [neighbor, here] : [here, neighbor]
  const h = item.h.exact ? item.h.latex : `\\approx ${item.h.approx}`
  return {
    title: 'El paso h',
    blocks: [
      text('Distancia entre los dos datos que usa la fórmula.'),
      math(`h = ${ctx.name(right)} - ${ctx.name(left)} = ${right.display.latex} - ${paren(left.display.latex)} ${item.h.exact ? '=' : ''} ${h}`),
    ],
  }
}

function pointsStep(formula, item, ctx) {
  const [here, neighbor] = byDistance(item.points)
  const forward = isForward(formula)
  if (ctx.table) {
    return {
      title: forward ? 'Vecino de la derecha' : 'Vecino de la izquierda',
      blocks: [
        text(
          forward
            ? `La progresiva usa el dato siguiente, a la derecha de ${ctx.atText}.`
            : `La regresiva usa el dato anterior, a la izquierda de ${ctx.atText}.`
        ),
        math(`${ctx.name(here)} = ${here.display.latex},\\quad ${ctx.name(neighbor)} = ${neighbor.display.latex}`),
      ],
    }
  }
  const sign = forward ? '+' : '-'
  const value = neighbor.display.exact
    ? `${here.display.latex} ${sign} ${ctx.h.latex} = ${neighbor.display.latex}`
    : `${neighbor.display.latex} \\approx ${neighbor.display.approx}`
  return {
    title: 'Puntos',
    blocks: [
      text(forward ? 'La progresiva usa el punto a la derecha de x₀.' : 'La regresiva usa el punto a la izquierda de x₀.'),
      math(`x_0 = ${shown(here.display)},\\quad ${neighbor.role} = ${value}`),
    ],
  }
}

function heightsStep(item, ctx) {
  const blocks = []
  if (ctx.table) {
    blocks.push(text('Las alturas son los datos de la tabla.'))
    for (const p of byDistance(item.points)) blocks.push(math(`f(${ctx.name(p)}) = y_{${p.index + 1}} = ${nodeValueLatex(p)}`))
  } else {
    blocks.push(text('Se reemplaza cada punto en f(x).'))
    for (const p of byDistance(item.points)) blocks.push(math(evaluationLatex(p, ctx.template, p.role)))
  }
  if (item.decimals > 6) {
    blocks.push(
      note(
        `Se muestran ${item.decimals} decimales porque al restar dos valores muy parecidos y dividir entre h, con 6 ` +
          'decimales el resultado no coincidiría con el que se ve.'
      )
    )
  }
  return { title: 'Altura de la curva en cada punto', blocks }
}

/** f(x₀) − f(x₀ − h) en el orden del numerador, con los colores de los nodos. */
function changeLatex(item, ctx) {
  const symbolic = signedSum(item.points.map((p) => ({ negative: p.weight < 0, body: `f(${ctx.name(p)})` })))
  const values = signedSum(item.points.map((p) => ({ negative: p.weight < 0, body: nodeValueLatex(p) })))
  return `${symbolic} = ${values} = ${item.numerator_display}`
}

function slopeStep(formula, item, ctx) {
  const h = ctx.table ? (item.h.exact ? item.h.latex : item.h.approx) : ctx.h.latex
  return {
    title: 'Pendiente de la secante (la aproximación)',
    blocks: [
      text(
        'Se divide el cambio de la función entre el avance h: eso es la pendiente de la recta que une los dos puntos, ' +
          'y aproxima la derivada.'
      ),
      math(`${ctx.symbol(formula)} = \\dfrac{${item.numerator_display}}{${h}} = \\mathbf{${latexNumber(item.D)}}`),
    ],
  }
}

function estimatedStep(result, formula, item, ctx) {
  const k = ctx.label
  const tolerance = formatNumber(result.tolerance)
  const value = formatNumber(item.estimated_error)
  const min = result.min_rows
  const last = result.iterations.at(-1).iteration
  const stops = result.converged && k === last
  let verdict
  if (!item.below_tolerance) verdict = `${value} > ${tolerance}: se sigue refinando.`
  else if (stops) verdict = `${value} ≤ ${tolerance} y ya hay ${k} filas: el método se detiene.`
  else if (k < min) verdict = `${value} ≤ ${tolerance}, pero todavía no hay ${min} filas: se sigue refinando.`
  else verdict = `${value} ≤ ${tolerance}, pero la otra fórmula todavía no llega a la tolerancia: se sigue refinando.`
  return {
    title: 'Error estimado',
    blocks: [
      text(
        `Cuánto cambió la aproximación respecto a la fila anterior (en azul la anterior, en verde la nueva). Si es menor ` +
          `que la tolerancia, y ya hay ${min} filas, el método se detiene.`
      ),
      math(estimatedErrorLatex(formula, item, k)),
      { kind: 'check', ok: stops ? true : null, text: verdict },
    ],
  }
}

/** «la aproximación quedó por encima…» y, si la curvatura lo explica, por qué. */
export function sideTexts(formula, item, ctx) {
  const out = []
  if (item.side === 'equal') return ['La aproximación coincide exactamente con la derivada exacta.']
  if (item.side === 'over') out.push('La aproximación quedó por encima de la derivada exacta (la sobreestima).')
  else if (item.side === 'under') out.push('La aproximación quedó por debajo de la derivada exacta (la subestima).')
  const sign = ctx.curvature?.sign
  if (sign && item.predicted_side === item.side) {
    const shape = sign < 0 ? "cóncava (f'' < 0)" : "convexa (f'' > 0)"
    const towards = isForward(formula) ? 'derecha' : 'izquierda'
    out.push(
      `Esto pasa porque f es ${shape} cerca de ${ctx.atText}: la secante hacia la ${towards} queda ` +
        `${item.side === 'over' ? 'más' : 'menos'} inclinada que la tangente.`
    )
  }
  return out
}

function realErrorStep(result, formula, item, ctx) {
  const blocks = [
    text('Se compara con la derivada exacta para ver qué tan buena es la aproximación.'),
    text('La derivada exacta (ver la sección «Derivada exacta») es:'),
    math(`f'(x) = ${result.function.derivative.latex}`),
  ]
  if (ctx.exactSource) blocks.push(math(substitutionLatex(ctx.exactSource)))
  blocks.push(
    math(
      `\\left|${ctx.symbol(formula)} - f'(${ctx.at})\\right| = ` +
        `\\left|${latexNumber(item.D)} - ${paren(latexNumber(ctx.exact))}\\right| = ${latexNumber(item.real_error)}`
    )
  )
  for (const t of sideTexts(formula, item, ctx)) blocks.push(text(t))
  const tiny = tinyRealErrorNote(item)
  if (tiny) blocks.push(note(tiny))
  return { title: 'Error real', blocks }
}

/** error real ≤ cota con el criterio de integración: «= cota» y R sólo si hace falta. */
export function boundCheck(item, roundingText, constant) {
  const real = latexNumber(item.real_error)
  const bound = latexNumber(item.bound)
  if (!item.within_bound) {
    return {
      kind: 'check',
      ok: false,
      latex: `\\text{error real} = ${real} > ${bound} = \\text{cota}`,
      text: 'El error real supera la cota: revisa los datos (la teoría dice que no debería pasar).',
    }
  }
  if (item.equals_bound) {
    return {
      kind: 'check',
      ok: true,
      latex: `\\text{error real} = ${real} = ${bound} = \\text{cota}`,
      text: constant
        ? "El error real es igual a la cota (pasa porque f'' es constante): se cumple."
        : 'El error real es igual a la cota: se cumple.',
    }
  }
  if (item.by_rounding) {
    return {
      kind: 'check',
      ok: true,
      latex: `\\text{error real} = ${real} \\le ${bound} + R \\quad (R = ${latexNumber(item.rounding)})`,
      text: `El error real supera la cota sólo por el redondeo de la computadora, ${roundingText}: dentro de ese margen se cumple.`,
    }
  }
  return {
    kind: 'check',
    ok: true,
    latex: `\\text{error real} = ${real} \\le ${bound} = \\text{cota}`,
    text: 'El error real quedó por debajo de la cota, como predice la teoría.',
  }
}

function boundStep(result, formula, item, ctx) {
  const second = result.function.higher_derivatives[2]
  if (item.bound === null) {
    return { title: "Cota (aquí se usa f'')", blocks: [note("No disponible: f''(x) no es finita en todo el intervalo de la fórmula.")] }
  }
  const constant = isConstant(second.latex)
  const [a, b] = ctx.table
    ? [...item.points].sort((p, q) => p.x - q.x).map((p) => shownText(p.display))
    : item.interval_display.map(shownText)
  const blocks = [text('La cota usa la segunda derivada:'), math(`f''(x) = ${second.latex}`)]
  const search =
    `M es el mayor valor de |f''(x)| en el intervalo [${a}, ${b}] que usa la fórmula; se busca evaluando f'' en ` +
    `${result.sampling_points} puntos.`
  if (constant) {
    blocks.push(text(`${search} Aquí f'' = ${formatNumber(item.M_substitution?.value ?? item.M)} en todo el intervalo, así que M = ${formatNumber(item.M)}.`))
  } else {
    const x = shownText(item.M_substitution.x_display)
    blocks.push(text(`${search} El mayor está en x = ${x}:`))
    blocks.push(math(substitutionLatex(item.M_substitution, "f''")))
    blocks.push(math(`M = \\left|f''(${shown(item.M_substitution.x_display)})\\right| = ${latexNumber(item.M)}`))
  }
  const h = ctx.table ? item.h : ctx.h
  const hLatex = h.exact ? h.latex : `\\left(${h.latex}\\right)`
  const half = item.half_h.exact ? `= ${item.half_h.latex}` : `\\approx ${item.half_h.approx}`
  blocks.push(
    text('Se sustituye en la fórmula de la cota:'),
    math(
      `\\frac{h}{2} \\cdot M = \\frac{${hLatex}}{2} \\cdot ${latexNumber(item.M)} ${half} \\cdot ${latexNumber(item.M)} = ` +
        `${latexNumber(item.bound)}`
    )
  )
  if (item.within_bound !== null) blocks.push(boundCheck(item, result.rounding_text ?? 'R = 4ε·máx|f|/h', constant))
  return { title: "Cota (aquí se usa f'')", blocks }
}

function ratioStep(item, previous) {
  const close = Math.abs(item.ratio - 0.5) < 0.05
  return {
    title: 'Razón',
    blocks: [
      math(ratioLatex(item, previous)),
      text(
        close
          ? 'El error se redujo a la mitad al dividir h entre 2, como predice la teoría (error proporcional a h).'
          : `La teoría predice una razón cercana a 0.5 (error proporcional a h); aquí es ${formatNumber(item.ratio)}.`
      ),
    ],
  }
}

/** Todos los pasos de una fórmula en una fila (o en un punto, en modo tabla). */
export function differenceSteps(result, formula, item, ctx, previous = null) {
  const steps = [
    stepSizeStep(formula, item, ctx),
    pointsStep(formula, item, ctx),
    heightsStep(item, ctx),
    {
      title: 'Cambio de la función («subida»)',
      blocks: [text('Cuánto cambia la altura de la curva entre los dos puntos.'), math(changeLatex(item, ctx))],
    },
    slopeStep(formula, item, ctx),
  ]
  if (!ctx.table && item.estimated_error !== null && item.estimated_error !== undefined) {
    steps.push(estimatedStep(result, formula, item, ctx))
  }
  if (result.function && ctx.exact !== null && ctx.exact !== undefined && item.real_error !== null) {
    steps.push(realErrorStep(result, formula, item, ctx))
  }
  if (result.function) steps.push(boundStep(result, formula, item, ctx))
  if (item.ratio !== null && item.ratio !== undefined && previous) steps.push(ratioStep(item, previous))
  return steps
}

/** En el PDF no hay lista numerada: «Paso 1. El paso h». */
export const numbered = (steps) => steps.map((s, i) => ({ ...s, title: `Paso ${i + 1}. ${s.title}` }))

// --- Comprobación ---------------------------------------------------------------------

/** «Con h = 0.000391 (fila 9), la progresiva coincide con la derivada exacta en 4 decimales». */
export function conclusionText(result, formula) {
  const final = result.verification.final?.[formula.key]
  if (!final || final.real_error === null || final.real_error === undefined) return null
  const last = result.iterations.at(-1)
  const h = last.extra.h
  const who = `Con h = ${h.exact ? h.text : `${h.text} ≈ ${h.approx}`} (fila ${last.iteration}), la ${formula.name.toLowerCase()}`
  const d = final.matching_decimals
  if (d === 6) return `${who} coincide con la derivada exacta en los 6 decimales que se muestran.`
  if (d === null || d === undefined || d === 0) {
    return `${who} difiere de la derivada exacta en ${formatNumber(final.real_error)}.`
  }
  return `${who} coincide con la derivada exacta en ${d} ${d === 1 ? 'decimal' : 'decimales'}.`
}
