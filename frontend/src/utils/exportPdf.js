import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { formatNumber } from './iterationSteps'

// Primitivas de maquetación compartidas con las secciones propias de cada
// categoría de métodos (ver methods/*/pdf.js).
export const MARGIN = 14
export const CONTENT_WIDTH = 210 - MARGIN * 2 // A4 vertical
const PAGE_HEIGHT = 297

export function ensureSpace(doc, y, needed) {
  if (y + needed <= PAGE_HEIGHT - MARGIN) return y
  doc.addPage()
  return MARGIN
}

export function sectionTitle(doc, y, text) {
  const nextY = ensureSpace(doc, y, 12)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.setTextColor(31, 41, 55)
  doc.text(text, MARGIN, nextY)
  return nextY + 6
}

export function paragraph(doc, y, text) {
  const lines = doc.splitTextToSize(text, CONTENT_WIDTH)
  const nextY = ensureSpace(doc, y, lines.length * 5)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(55, 65, 81)
  doc.text(lines, MARGIN, nextY)
  return nextY + lines.length * 5 + 2
}

/**
 * Genera y descarga un PDF con los datos de entrada, el resultado final, el
 * gráfico de convergencia y la tabla completa de iteraciones (sin paginar).
 *
 * `report` lo aporta la categoría del método:
 *   title             título del documento
 *   writeInputSection(doc, y) -> y   sección con los datos de entrada
 *   statusExtras      textos adicionales para la línea de estado del resultado
 *   fileStem          nombre base del archivo (sin fecha ni extensión)
 */
export function exportResultToPdf({ result, methodName, chartImage, report }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const variables = result.variables ?? result.solution.map((_, i) => `x${i + 1}`)

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.setTextColor(31, 41, 55)
  doc.text(report.title, MARGIN, MARGIN + 4)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(107, 114, 128)
  doc.text(
    `Método de ${methodName}  ·  Generado el ${new Date().toLocaleString('es-CO')}`,
    MARGIN,
    MARGIN + 11
  )

  let y = MARGIN + 20

  // --- Datos de entrada (propios de la categoría) -------------------------
  y = report.writeInputSection(doc, y)

  // --- Resultado ---------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Resultado')
  y = paragraph(
    doc,
    y,
    [
      `Estado: ${result.converged ? 'CONVERGIÓ' : 'NO CONVERGIÓ'}`,
      `Iteraciones ejecutadas: ${result.iterations_used}`,
      ...(report.statusExtras ?? []),
    ].join('    ·    ')
  )

  autoTable(doc, {
    startY: y,
    head: [variables],
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
    head: [['Iter.', ...variables, 'Error']],
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

  const stem = report.fileStem ?? result.method
  doc.save(`${stem}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
