// Partes del PDF propias de un sistema lineal: la sección "Datos del sistema"
// (matriz A|b, x0, tolerancia y nota de reordenamiento) y la dominancia
// diagonal en la línea de estado.
import autoTable from 'jspdf-autotable'

import { formatNumber } from '../../utils/iterationSteps'
import { MARGIN, paragraph, sectionTitle } from '../../utils/exportPdf'

export function linearPdfReport({ result, system }) {
  const n = result.solution.length
  const variableHeaders = result.variables ?? Array.from({ length: n }, (_, i) => `x${i + 1}`)

  function writeInputSection(doc, startY) {
    let y = sectionTitle(doc, startY, 'Datos del sistema')

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

    if (result.reordered && result.row_order) {
      // Flecha ASCII: la fuente estándar de jsPDF (WinAnsi) no tiene el glifo "→".
      const mapping = result.row_order
        .map((originalRow, position) => `fila ${originalRow + 1} -> posición ${position + 1}`)
        .join(', ')
      y = paragraph(
        doc,
        y,
        `Nota: las filas se reordenaron automáticamente (${mapping}) para lograr ` +
          'dominancia diagonal. La tabla anterior muestra el sistema ya reordenado; ' +
          'la solución es la misma que la del orden original.'
      )
    }

    return y
  }

  return {
    title: 'Sistemas de ecuaciones lineales — Métodos iterativos',
    writeInputSection,
    statusExtras: [
      `Matriz diagonalmente dominante: ${result.is_diagonally_dominant ? 'sí' : 'no'}`,
    ],
    fileStem: `${result.method}-${n}x${n}`,
  }
}
