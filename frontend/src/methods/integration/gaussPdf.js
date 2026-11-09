// PDF del resultado de la cuadratura gaussiana, siempre en tema claro, con el
// mismo estilo y las mismas utilidades que los otros métodos de integración
// (pdf.js): datos y cambio de variable, resumen y notas, gráfico de rectángulos,
// gráfico de convergencia, tabla de refinamiento, paso a paso explicado de las
// filas 1, 2, 3 y la última, comprobación (momentos y costo) y los glosarios.
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { MARGIN, sectionTitle } from '../../utils/exportPdf'
import { formatNumber } from '../../utils/iterationSteps'
import { latexToText } from '../../utils/latexText'
import { substitutionText } from '../differentiation/formulas'
import { tinyErrorNote } from './explain'
import {
  BOUND_GLOSSARY,
  BOUND_LATEX,
  CHANGE_GLOSSARY,
  CHART_GLOSSARY,
  COMPOSITE_GLOSSARY,
  COMPOSITE_LATEX,
  GAUSS_GLOSSARY,
  GAUSS_LATEX,
  MOMENT_COLUMNS,
  MOMENT_SENTENCE,
  NODES_GLOSSARY,
  NODES_LATEX,
  STOP_LATEX,
  TABLE_LEGEND,
  centersLatex,
  changeOfVariable,
  comparisonColumns,
  gaussColumns,
  gaussConclusion,
  gaussRowSteps,
  gaussSubstitution,
  mappingLatex,
  visibleMoments,
} from './gaussExplain'
import { TABLE, addImage, mark, num, pct, pdfSafe, pdfTools, shown } from './pdf'

// La fuente estándar de jsPDF (WinAnsi) no tiene ⁵–⁸ ni los subíndices ₘ, ⱼ…:
// los superíndices se escriben «^…» y los subíndices como letras normales;
// cualquier otro carácter fuera de Latin-1 se quita (dañaría toda la línea).
const SUP = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-', 'ᵐ': 'm', 'ᵏ': 'k', 'ⁿ': 'n' }
const SUB = { 'ₘ': 'm', 'ⱼ': 'j', 'ᵢ': 'i', 'ₖ': 'k', 'ₜ': 't', 'ₐ': 'a', 'ₙ': 'n', '₋': '-', '₁': '1', '₂': '2', '₀': '0' }
const KEEP = new Set(['—', '–', '…', '“', '”', '•', '≤', '≥', '≈', '≠', '−', '✔', '⚠', 'Σ', '∫', 'ε', '→'])
function clean(value) {
  const text = String(value)
    .replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻ᵐᵏⁿ]+/g, (m) => `^${[...m].map((c) => SUP[c]).join('')}`)
    .replace(/[ₘⱼᵢₖₜₐₙ₋₀₁₂]/g, (c) => SUB[c])
    .replace(/⁽/g, '(')
    .replace(/⁾/g, ')')
  return pdfSafe([...text].filter((c) => c.charCodeAt(0) <= 0xff || KEEP.has(c)).join(''))
}
const cleanItems = (items) => items.map((item) => ({ ...item, symbol: item.symbol, text: clean(item.text) }))

export function exportGaussPdf({ result, methodName, chartImage, chartTitle, chartM, convergenceImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const fn = result.function
  const integral = result.integral
  const reference = integral?.kind === 'reference'
  const hasI = integral && integral.value !== null && integral.value !== undefined
  const rows = result.iterations.map((s) => s.extra)
  const N = result.subintervals
  const tools = pdfTools(doc, result)
  const write = (y, text) => tools.write(y, clean(text))
  const writeMath = (y, latex) => write(y, `   ${latexToText(latex)}`)
  const label = (y, text) => tools.label(y, clean(text))
  const glossary = (y, title, items, summary) => tools.glossary(y, title, cleanItems(items), summary && clean(summary))
  const table = (y, head, body) => {
    autoTable(doc, { ...TABLE, theme: 'grid', startY: y, head: [head.map(clean)], body: body.map((r) => r.map((c) => clean(c))) })
    return doc.lastAutoTable.finalY + 4
  }

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.setTextColor(31, 41, 55)
  doc.text(`Integración numérica — ${methodName}`, MARGIN, MARGIN + 4)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(107, 114, 128)
  doc.text(`Método: ${methodName}  ·  Generado el ${new Date().toLocaleString('es-CO')}`, MARGIN, MARGIN + 11)
  let y = MARGIN + 20

  // --- Datos y cambio de variable ----------------------------------------------------
  y = sectionTitle(doc, y, 'Datos')
  const body = fn.is_sum ? `(${fn.text})` : fn.text
  y = write(y, `Integral: de a = ${shown(result.a_display)} a b = ${shown(result.b_display)} de ${body} dx`)
  y = write(
    y,
    `Subintervalos N = ${N}    ·    Tolerancia del error estimado: ${formatNumber(result.tolerance)}    ·    ` +
      `Máximo de puntos: ${result.max_iterations}    ·    Mínimo de filas: ${result.min_rows}`
  )
  if (fn.uses_trigonometry) y = write(y, 'Las funciones trigonométricas se evalúan en radianes.')
  y = label(y + 2, `Cambio de variable${N > 1 ? ' (en un subintervalo genérico j)' : ''}`)
  y = write(y, `Se lleva ${N === 1 ? 'el intervalo [a, b]' : 'cada subintervalo'} a [-1, 1], porque los nodos y pesos están calculados para ese intervalo.`)
  for (const line of changeOfVariable(result)) y = writeMath(y, line)
  if (N > 1) y = writeMath(y, centersLatex(result))
  y = glossary(y, '¿Qué significa cada símbolo?', CHANGE_GLOSSARY)

  // --- Resultado ------------------------------------------------------------------------
  const last = rows.at(-1)
  y = sectionTitle(doc, y + 2, 'Resultado')
  y = write(
    y,
    `Estado: ${result.converged ? 'ALCANZÓ LA TOLERANCIA' : 'NO ALCANZÓ LA TOLERANCIA'}    ·    Filas usadas: ${result.iterations_used}` +
      `    ·    Evaluaciones de f: ${result.evaluations} en total (${last.evaluations} en la última fila)`
  )
  const errors = last.true_error === null ? '' : `    ·    Et = ${num(last.true_error)}    ·    et = ${pct(last.relative_error)}`
  y = write(y, `Resultado: I ~ G${last.m} = ${num(last.G)} (m = ${last.m}, N = ${N})${errors}`)
  if (hasI) y = write(y, `I = ${num(integral.value)} (${integral.label})`)
  for (const note of result.notes ?? []) y = write(y, `Nota: ${note}`)
  for (const warning of result.warnings ?? []) y = write(y, `Advertencia: ${warning}`)

  // --- Fórmulas -------------------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Fórmula de Gauss')
  y = write(y, `Simple (N = 1): ${latexToText(GAUSS_LATEX)}`)
  y = glossary(y, '¿Qué significa cada símbolo?', GAUSS_GLOSSARY.items, GAUSS_GLOSSARY.summary)
  if (N > 1) {
    y = write(y + 1, `Compuesta: ${latexToText(COMPOSITE_LATEX)}`)
    y = glossary(y, '¿Qué significa cada símbolo?', COMPOSITE_GLOSSARY.items, COMPOSITE_GLOSSARY.summary)
  }
  y = write(y + 1, `Nodos y pesos: ${latexToText(NODES_LATEX)}`)
  y = glossary(y, '¿Qué significa cada símbolo?', NODES_GLOSSARY.items)
  y = write(y + 1, `Criterio de parada: ${latexToText(STOP_LATEX)}. Se detiene cuando es <= ${formatNumber(result.tolerance)} y ya hay al menos ${result.min_rows} filas.`)
  y = write(y + 1, `Cota (m <= ${result.max_bound_points}): ${latexToText(BOUND_LATEX)}`)
  y = glossary(y, '¿Qué significa cada símbolo?', BOUND_GLOSSARY)
  y = label(y + 2, 'Derivadas para la cota')
  for (const d of fn.derivatives) {
    if (d.order % 2) continue
    y = d.long
      ? write(y, `   f^(${d.order})(x): expresión larga (${d.text.length} caracteres); ver la vista en pantalla.`)
      : writeMath(y, `f^{(${d.order})}(x) = ${d.latex}`)
  }

  // --- Gráficos ------------------------------------------------------------------------
  if (chartImage) {
    y = addImage(doc, y, clean(chartTitle ?? `Gráfico de rectángulos (m = ${chartM})`), chartImage)
    y = glossary(y, '¿Cómo se lee este gráfico?', CHART_GLOSSARY)
  }
  y = addImage(doc, y, 'Convergencia del error (escala logarítmica)', convergenceImage)

  // --- Tabla de refinamiento ------------------------------------------------------------
  const headers = gaussColumns({ showTrue: hasI, reference })
  y = sectionTitle(doc, y + 2, 'Tabla de refinamiento')
  y = table(
    y,
    headers.map((c) => c.label),
    rows.map((r) => {
      const bound = r.bound === null ? 'no disponible' : num(r.bound)
      return hasI
        ? [r.m, r.evaluations, num(r.G), num(r.estimated_error), num(r.true_error), pct(r.relative_error), bound, mark(r)]
        : [r.m, r.evaluations, num(r.G), num(r.estimated_error), bound]
    })
  )
  const tinyRows = rows.filter((r) => tinyErrorNote(r, reference))
  if (tinyRows.length) y = write(y, `Filas ${tinyRows.map((r) => r.m).join(', ')}: ${tinyErrorNote(tinyRows[0], reference)}`)
  y = glossary(y, '¿Qué significa cada columna?', headers)
  y = glossary(y, '¿Cómo se lee esta tabla?', TABLE_LEGEND)

  // --- Paso a paso: filas 1, 2, 3 y la última ---------------------------------------------
  y = sectionTitle(doc, y + 2, 'Paso a paso explicado')
  const chosen = [...new Set([0, 1, 2, rows.length - 1])].filter((i) => i < rows.length)
  for (const i of chosen) {
    if (i === rows.length - 1 && i > 3) y = write(y, `Las filas 4 a ${rows.length - 1} siguen el mismo procedimiento.`)
    const row = rows[i]
    y = label(y + 2, `Fila ${row.m} (m = ${row.m}, ${row.evaluations} evaluaciones)`)
    const points = row.step.groups.flatMap((g) => g.points.map((p) => ({ g, p })))
    const visible = points.length > 16 ? [...points.slice(0, 8), ...points.slice(-8)] : points
    for (const s of gaussRowSteps(result, row, i > 0 ? rows[i - 1] : null)) {
      y = label(y + 1, s.title)
      for (const block of s.blocks) {
        if (block.kind === 'text' || block.kind === 'note') y = write(y, block.text)
        else if (block.kind === 'math') y = writeMath(y, block.latex)
        else if (block.kind === 'check') {
          const markText = block.ok === true ? ' OK' : block.ok === false ? ' (!)' : ''
          if (block.latex) y = writeMath(y, `${block.latex}${markText ? ` \\text{${markText}}` : ''}`)
          y = write(y, block.text)
        } else if (block.kind === 'nodes') {
          y = table(y, ['i', 'ti (forma exacta)', 'ti', 'wi (forma exacta)', 'wi'],
            row.step.nodes.map((n) => [n.i, n.t_latex ? latexToText(n.t_latex) : '-', n.t_display, n.w_latex ? latexToText(n.w_latex) : '-', n.w_display]))
        } else if (block.kind === 'mapping') {
          for (const { g, p } of visible) y = writeMath(y, mappingLatex(result, row, g, p))
        } else if (block.kind === 'evals') {
          y = table(y, [...(N > 1 ? ['j'] : []), 'i', 'xi', 'Sustitución', 'f(xi)'],
            visible.map(({ g, p }) => [...(N > 1 ? [g.j] : []), p.i, p.x_display, substitutionText(gaussSubstitution(result, p)).replace(/^f'/, 'f'), p.f_display]))
        } else if (block.kind === 'products') {
          y = table(y, [...(N > 1 ? ['j'] : []), 'i', 'wi', 'f(xi)', 'wi · f(xi)'],
            visible.map(({ g, p }) => [...(N > 1 ? [g.j] : []), p.i, row.step.nodes[p.i - 1].w_display, p.f_display, p.product]))
          if (points.length > visible.length) y = write(y, `Se muestran ${visible.length} de ${points.length} puntos; la suma usa todos.`)
        }
      }
    }
  }

  // --- Comprobación ----------------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Comprobación')
  y = tools.integralCheck(y)
  const final = result.verification.final
  if (final.I !== null) {
    y = table(y, comparisonColumns(reference).map((c) => c.label), [[num(final.G), num(final.I), num(final.true_error), pct(final.relative_error)]])
    const tiny = tinyErrorNote(final, reference)
    if (tiny) y = write(y, tiny)
    const conclusion = gaussConclusion(result, final)
    if (conclusion) y = write(y, conclusion)
    y = glossary(y, '¿Qué significa cada columna?', comparisonColumns(reference))
  }

  const moments = result.verification.moments
  y = label(y + 2, `Exactitud de la regla (m = ${moments.m}): momentos`)
  y = table(
    y,
    ['k', 'Suma wi·ti^k', 'Integral de t^k en [-1, 1]', ''],
    visibleMoments(moments.rows).map((r) =>
      r ? [r.k, num(r.value), num(r.exact), r.ok ? (r.k === 0 ? 'OK (los pesos suman 2)' : 'OK') : 'no coincide'] : ['...', '', '', '']
    )
  )
  y = write(y, MOMENT_SENTENCE)
  y = glossary(y, '¿Qué significa cada columna?', MOMENT_COLUMNS)

  if (result.cost) {
    y = label(y + 2, 'Comparación de costo')
    y = write(y, result.cost.text)
    y = write(y, 'El mínimo de 6 filas es un requisito del curso, no del método: Gauss podría detenerse antes.')
  }

  doc.save(`gauss-${new Date().toISOString().slice(0, 10)}.pdf`)
}
