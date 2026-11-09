// PDF del resultado de la integración de Romberg, siempre en tema claro, con el
// mismo estilo y las mismas utilidades que el trapecio y Simpson (pdf.js):
// datos, resumen y advertencias, tabla triangular (diagonal resaltada) y la de
// errores, tabla de convergencia de la diagonal, gráfico, paso a paso
// explicado de las filas 1, 2, 3 y la última, comprobación (identidades y
// comparación de costo) y los glosarios como texto.
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { MARGIN, sectionTitle } from '../../utils/exportPdf'
import { formatNumber } from '../../utils/iterationSteps'
import { latexToText } from '../../utils/latexText'
import { tinyErrorNote } from './explain'
import { TABLE, addImage, num, pct, pdfSafe, pdfTools, shown } from './pdf'
import {
  COST_NOTE,
  IDENTITY_SENTENCE,
  RECURRENCE_LATEX,
  RICHARDSON_LATEX,
  STOP_LATEX,
  dataPointsText,
  rombergConclusion,
  rombergRowGroups,
} from './rombergExplain'
import {
  CHART_GLOSSARY,
  CHART_UNDRAWABLE,
  IDENTITY_COLUMNS,
  RECURRENCE_GLOSSARY,
  RICHARDSON_GLOSSARY,
  TABLE_LEGEND,
  convergenceColumns,
  rombergComparisonColumns,
} from './rombergGlossary'

// Con más de 8 columnas k la tabla no cabe: se muestran las 4 primeras y las 3 últimas.
const MAX_COLUMNS = 8
const DIAGONAL_FILL = [253, 240, 196]

// pdfSafe (compartido con el trapecio y Simpson) no traduce ⁵–⁸: aquí cada
// grupo de superíndices se escribe «^…» (h⁶ → h^6, 10⁻¹² → 10^-12).
const SUP = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-' }
const sup = (text) => String(text).replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+/g, (m) => `^${[...m].map((c) => SUP[c]).join('')}`)
const supItems = (items) => items.map((item) => ({ ...item, text: sup(item.text) }))
const supSteps = (steps) =>
  steps.map((s) => ({ ...s, title: sup(s.title), blocks: s.blocks.map((b) => (b.text ? { ...b, text: sup(b.text) } : b)) }))

function visibleColumns(count) {
  const all = Array.from({ length: count }, (_, i) => i + 1)
  return count > MAX_COLUMNS ? [...all.slice(0, 4), null, ...all.slice(-3)] : all
}

export function exportRombergPdf({ result, methodName, chartImage, chartTitle, convergenceImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const isTable = result.mode === 'table'
  const fn = result.function
  const integral = result.integral
  const reference = integral?.kind === 'reference'
  const hasI = integral && integral.value !== null && integral.value !== undefined
  const rows = result.iterations.map((s) => s.extra)
  const tools = pdfTools(doc, result)
  const { writeMath, integralCheck } = tools
  const write = (y, text) => tools.write(y, sup(text))
  const label = (y, text) => tools.label(y, sup(text))
  const glossary = (y, title, items, summary) => tools.glossary(y, title, supItems(items), summary && sup(summary))

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.setTextColor(31, 41, 55)
  doc.text(`Integración numérica — ${methodName}`, MARGIN, MARGIN + 4)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(107, 114, 128)
  doc.text(`Método: ${methodName}  ·  Generado el ${new Date().toLocaleString('es-CO')}`, MARGIN, MARGIN + 11)
  let y = MARGIN + 20

  // --- Datos -----------------------------------------------------------------
  y = sectionTitle(doc, y, 'Datos')
  if (isTable) {
    y = write(y, `Modo: tabla de ${result.points.length} datos igualmente espaciados (2^${rows.length - 1} + 1 puntos)`)
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['i', 'xi', 'yi']],
      body: result.points.map(([x, yValue], i) => [i, num(x), num(yValue)]),
    })
    y = doc.lastAutoTable.finalY + 6
    y = write(y, fn ? `Función para comparar: f(x) = ${fn.text}` : 'Sin función para comparar.')
  } else {
    const body = fn.is_sum ? `(${fn.text})` : fn.text
    y = write(y, `Integral: de a = ${shown(result.a_display)} a b = ${shown(result.b_display)} de ${body} dx`)
    y = write(
      y,
      `Tolerancia del error estimado: ${formatNumber(result.tolerance)}    ·    Máximo de filas: ${result.max_iterations}` +
        `    ·    Mínimo de filas: ${result.min_rows}`
    )
  }
  y = write(y, 'Romberg no usa derivadas: sólo evalúa f (o usa los datos) y combina trapecios.')
  if (fn?.uses_trigonometry) y = write(y, 'Las funciones trigonométricas se evalúan en radianes.')

  // --- Resultado --------------------------------------------------------------
  const last = rows.at(-1)
  y = sectionTitle(doc, y + 2, 'Resultado')
  y = write(
    y,
    `Estado: ${isTable ? 'CALCULADO' : result.converged ? 'ALCANZÓ LA TOLERANCIA' : 'NO ALCANZÓ LA TOLERANCIA'}    ·    ` +
      `Filas usadas: ${result.iterations_used}    ·    ${isTable ? 'Datos usados' : 'Evaluaciones de f'}: ${result.evaluations}`
  )
  const errors = last.true_error === null ? '' : `    ·    Et = ${num(last.true_error)}    ·    et = ${pct(last.relative_error)}`
  y = write(y, `Mejor valor: I ~ R${last.i},${last.i} = ${num(last.best)} (n = ${last.n})${errors}`)
  if (hasI) y = write(y, `I = ${num(integral.value)} (${integral.label})`)
  for (const note of result.notes ?? []) y = write(y, `Nota: ${note}`)
  for (const warning of result.warnings ?? []) y = write(y, `Advertencia: ${warning}`)

  // --- Gráfico de segmentos (la columna y la fila elegidas en pantalla) -------------
  if (chartImage) {
    y = addImage(doc, y, pdfSafe(sup(chartTitle ?? 'Gráfico de segmentos')), chartImage)
    y = write(y, CHART_UNDRAWABLE)
    y = glossary(y, '¿Cómo se lee este gráfico?', CHART_GLOSSARY)
  }

  // --- Tabla triangular ---------------------------------------------------------
  const columns = visibleColumns(result.columns.length)
  const triangular = (title, field) => {
    y = label(y + 2, title)
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['i', 'n', ...columns.map((k) => (k === null ? '...' : pdfSafe(sup(`${result.columns[k - 1].name} ${result.columns[k - 1].order_text}`))))]],
      body: rows.map((row) => [row.i, row.n, ...columns.map((k) => (k === null ? '...' : k <= row.i ? num(row[field][k - 1]) : ''))]),
      didParseCell: (data) => {
        if (data.section !== 'body') return
        const k = columns[data.column.index - 2]
        if (k && k === rows[data.row.index].i) {
          data.cell.styles.fillColor = DIAGONAL_FILL
          data.cell.styles.fontStyle = 'bold'
        }
      },
    })
    y = doc.lastAutoTable.finalY + 4
    if (columns.includes(null)) {
      y = write(y, `La tabla tiene ${result.columns.length} columnas: se muestran las 4 primeras y las 3 últimas ("..." son las de en medio).`)
    }
  }
  y = sectionTitle(doc, y + 2, 'Tabla triangular de Romberg')
  y = write(y, `Columna 1 (trapecios con la recurrencia): ${latexToText(RECURRENCE_LATEX)}`)
  y = glossary(y, '¿Qué significa cada símbolo?', RECURRENCE_GLOSSARY.items, RECURRENCE_GLOSSARY.summary)
  y = write(y + 1, `Columnas siguientes (Richardson): ${latexToText(RICHARDSON_LATEX)}`)
  y = glossary(y, '¿Qué significa cada símbolo?', RICHARDSON_GLOSSARY.items, RICHARDSON_GLOSSARY.summary)
  y = write(y + 1, `Criterio de parada: ${latexToText(STOP_LATEX)}`)
  y = write(
    y,
    isTable
      ? 'En el modo tabla no hay criterio de parada: las filas las fija la cantidad de datos.'
      : `Se detiene cuando el error estimado es <= ${formatNumber(result.tolerance)} y ya hay al menos ${result.min_rows} filas.`
  )
  triangular('Valores Ri,k (la diagonal, resaltada, es el mejor valor de cada fila)', 'values')
  y = glossary(y, '¿Cómo se lee esta tabla?', TABLE_LEGEND.slice(0, 3))
  if (hasI) triangular(`Tabla de errores: Et = I - Ri,k${reference ? ' (respecto al valor de referencia)' : ''}`, 'errors')

  // --- Convergencia de la diagonal ------------------------------------------------
  const headers = convergenceColumns({ showTrue: hasI, reference, isTable })
  y = sectionTitle(doc, y + 2, 'Convergencia de la diagonal')
  autoTable(doc, {
    ...TABLE,
    startY: y,
    head: [headers.map((c) => pdfSafe(c.label))],
    body: rows.map((r) => {
      const line = [r.i, r.n, r.evaluations, num(r.values[0]), num(r.best), num(r.estimated_error), pct(r.approx_error)]
      return hasI ? [...line, num(r.true_error), pct(r.relative_error)] : line
    }),
  })
  y = doc.lastAutoTable.finalY + 4
  const tinyRows = rows.filter((r) => tinyErrorNote(r, reference))
  if (tinyRows.length) y = write(y, `Filas ${tinyRows.map((r) => r.i).join(', ')}: ${tinyErrorNote(tinyRows[0], reference)}`)
  y = glossary(y, '¿Qué significa cada columna?', headers)

  y = addImage(doc, y, 'Convergencia del error (escala logarítmica)', convergenceImage)

  // --- Paso a paso: filas 1, 2, 3 y la última -------------------------------------
  y = sectionTitle(doc, y + 2, 'Paso a paso explicado')
  const chosen = [...new Set([0, 1, 2, rows.length - 1])].filter((i) => i < rows.length)
  for (const i of chosen) {
    if (i === rows.length - 1 && i > 3) y = write(y, `Las filas 4 a ${rows.length - 1} siguen el mismo procedimiento.`)
    const row = rows[i]
    const previous = i > 0 ? rows[i - 1] : null
    y = label(y + 2, `Fila ${row.i} (n = ${row.n}${isTable ? `, ${dataPointsText(row)} de la tabla` : ''})`)
    for (const group of rombergRowGroups(result, row, previous)) {
      y = label(y + 1, group.title)
      y = tools.steps(y, supSteps(group.steps), row.trapezoid)
    }
  }

  // --- Comprobación -----------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Comprobación')
  if (isTable && result.verification.data) {
    y = write(y, 'Datos contra la función: |yi - f(xi)| <= 10^-6 · máx(1, |f(xi)|).')
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['i', 'yi', 'f(xi)', '|yi - f(xi)|', '']],
      body: result.verification.data.map((row) => [row.i, num(row.y), num(row.f), num(row.difference),
        row.ok ? 'OK' : '(!) el dato no coincide con la función']),
    })
    y = doc.lastAutoTable.finalY + 6
  }
  y = integralCheck(y)
  const final = result.verification.final
  if (final) {
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [rombergComparisonColumns(reference).map((c) => pdfSafe(c.label))],
      body: [[num(final.R), num(final.I), num(final.true_error), pct(final.relative_error)]],
    })
    y = doc.lastAutoTable.finalY + 6
    const tiny = tinyErrorNote(final, reference)
    if (tiny) y = write(y, tiny)
    const conclusion = rombergConclusion(result, final)
    if (conclusion) y = write(y, conclusion)
    y = glossary(y, '¿Qué significa cada columna?', rombergComparisonColumns(reference))
  }

  y = label(y + 2, 'Identidades: columna 1 = trapecio, columna 2 = Simpson 1/3')
  const diff = (item) => (item.difference === 0 ? '0' : item.difference.toExponential(1))
  autoTable(doc, {
    ...TABLE,
    theme: 'grid',
    startY: y,
    head: [['i', 'n', 'Ri,1', 'T(n)', '|dif.|', '', 'Ri,2', 'S(n)', '|dif.|', '']],
    body: result.verification.identities.map((r) => [
      r.i, r.n, num(r.trapezoid.value), num(r.trapezoid.other), diff(r.trapezoid), r.trapezoid.ok ? 'OK' : '(!)',
      ...(r.simpson ? [num(r.simpson.value), num(r.simpson.other), diff(r.simpson), r.simpson.ok ? 'OK' : '(!)'] : ['-', '-', '-', '']),
    ]),
  })
  y = doc.lastAutoTable.finalY + 4
  y = write(y, IDENTITY_SENTENCE)
  y = glossary(y, '¿Qué significa cada columna?', IDENTITY_COLUMNS)

  if (result.cost) {
    y = label(y + 2, 'Comparación de costo')
    y = write(y, result.cost.text)
    y = write(y, COST_NOTE)
  }

  doc.save(`romberg-${isTable ? 'tabla' : 'funcion'}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
