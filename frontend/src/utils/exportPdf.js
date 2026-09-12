import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { formatNumber } from './iterationSteps'

const MARGIN = 14
const CONTENT_WIDTH = 210 - MARGIN * 2 // A4 vertical
const PAGE_HEIGHT = 297

function methodLabel(method) {
  return method === 'gauss-seidel' ? 'Gauss-Seidel' : 'Jacobi'
}

function ensureSpace(doc, y, needed) {
  if (y + needed <= PAGE_HEIGHT - MARGIN) return y
  doc.addPage()
  return MARGIN
}

function sectionTitle(doc, y, text) {
  const nextY = ensureSpace(doc, y, 12)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.setTextColor(31, 41, 55)
  doc.text(text, MARGIN, nextY)
  return nextY + 6
}

function paragraph(doc, y, text) {
  const lines = doc.splitTextToSize(text, CONTENT_WIDTH)
  const nextY = ensureSpace(doc, y, lines.length * 5)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(55, 65, 81)
  doc.text(lines, MARGIN, nextY)
  return nextY + lines.length * 5 + 2
}

/**
 * Genera y descarga un PDF con el sistema resuelto, el resultado final, el
 * gráfico de convergencia y la tabla completa de iteraciones (sin paginar).
 */
export function exportResultToPdf({ result, system, chartImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const n = result.solution.length
  const label = methodLabel(result.method)

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.setTextColor(31, 41, 55)
  doc.text('Sistemas de ecuaciones lineales — Métodos iterativos', MARGIN, MARGIN + 4)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(107, 114, 128)
  doc.text(
    `Método de ${label}  ·  Generado el ${new Date().toLocaleString('es-CO')}`,
    MARGIN,
    MARGIN + 11
  )

  let y = MARGIN + 20

  // --- Datos del sistema -------------------------------------------------
  y = sectionTitle(doc, y, 'Datos del sistema')

  const variableHeaders = Array.from({ length: n }, (_, i) => `x${i + 1}`)
  autoTable(doc, {
    startY: y,
    head: [[...variableHeaders, 'b']],
    body: system.A.map((row, i) => [
      ...row.map((value) => formatNumber(value)),
      formatNumber(system.b[i]),
    ]),
    theme: 'grid',
    margin: { left: MARGIN, right: MARGIN },
    styles: { fontSize: 9, halign: 'right', cellPadding: 2 },
    headStyles: { fillColor: [37, 99, 235], halign: 'center' },
  })
  y = doc.lastAutoTable.finalY + 6

  y = paragraph(
    doc,
    y,
    `Número de variables (n): ${n}    ·    Vector inicial x0: [${system.x0
      .map((v) => formatNumber(v))
      .join(', ')}]`
  )
  y = paragraph(
    doc,
    y,
    `Tolerancia: ${system.tolerance}    ·    Máximo de iteraciones: ${system.max_iterations}`
  )

  // --- Resultado ---------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Resultado')
  y = paragraph(
    doc,
    y,
    `Estado: ${result.converged ? 'CONVERGIÓ' : 'NO CONVERGIÓ'}    ·    ` +
      `Iteraciones ejecutadas: ${result.iterations_used}    ·    ` +
      `Matriz diagonalmente dominante: ${result.is_diagonally_dominant ? 'sí' : 'no'}`
  )

  autoTable(doc, {
    startY: y,
    head: [variableHeaders],
    body: [result.solution.map((value) => formatNumber(value))],
    theme: 'grid',
    margin: { left: MARGIN, right: MARGIN },
    styles: { fontSize: 9, halign: 'right', cellPadding: 2 },
    headStyles: { fillColor: [21, 128, 61], halign: 'center' },
  })
  y = doc.lastAutoTable.finalY + 6

  if (result.warnings?.length) {
    for (const warning of result.warnings) {
      y = paragraph(doc, y, `Advertencia: ${warning}`)
    }
  }

  // --- Gráfico de convergencia -------------------------------------------
  if (chartImage?.dataUrl) {
    const imgHeight = (CONTENT_WIDTH * chartImage.height) / chartImage.width
    y = sectionTitle(doc, y + 2, 'Convergencia del error (escala logarítmica)')
    y = ensureSpace(doc, y, imgHeight)
    doc.addImage(chartImage.dataUrl, 'PNG', MARGIN, y, CONTENT_WIDTH, imgHeight)
    y += imgHeight + 8
  }

  // --- Tabla completa de iteraciones -------------------------------------
  y = sectionTitle(doc, y, 'Detalle completo de iteraciones')
  autoTable(doc, {
    startY: y,
    head: [['Iter.', ...variableHeaders, 'Error']],
    body: result.iterations.map((row) => [
      row.iteration,
      ...row.x.map((value) => formatNumber(value)),
      row.error === null ? '—' : formatNumber(row.error),
    ]),
    theme: 'striped',
    margin: { left: MARGIN, right: MARGIN },
    styles: { fontSize: 8, halign: 'right', cellPadding: 1.5 },
    headStyles: { fillColor: [37, 99, 235], halign: 'center' },
    columnStyles: { 0: { halign: 'center' } },
  })

  const fileName = `${result.method}-${n}x${n}-${new Date()
    .toISOString()
    .slice(0, 10)}.pdf`
  doc.save(fileName)
}
