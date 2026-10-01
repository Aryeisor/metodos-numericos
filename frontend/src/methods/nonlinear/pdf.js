// Partes del PDF propias de un sistema no lineal: la sección "Datos del
// sistema" (ecuaciones ingresadas, despejes obtenidos, x0 y parámetros).
// jsPDF no dibuja LaTeX: se usan las ecuaciones tal como se escribieron y el
// despeje en texto plano que entrega el backend (g_text).
import autoTable from 'jspdf-autotable'

import { formatNumber } from '../../utils/iterationSteps'
import { MARGIN, paragraph, sectionTitle } from '../../utils/exportPdf'

export function nonlinearPdfReport({ result, system }) {
  const n = result.variables.length

  function writeInputSection(doc, startY) {
    let y = sectionTitle(doc, startY, 'Datos del sistema')

    autoTable(doc, {
      startY: y,
      head: [['#', 'Ecuación ingresada', 'Función de iteración']],
      body: result.equations.map((equation, i) => [
        String(i + 1),
        system.equations[i],
        `${equation.variable} = ${equation.g_text}`,
      ]),
      theme: 'grid',
      margin: { left: MARGIN, right: MARGIN },
      styles: { fontSize: 9, cellPadding: 2, font: 'courier' },
      columnStyles: { 0: { halign: 'center', cellWidth: 10, font: 'helvetica' } },
      headStyles: { fillColor: [37, 99, 235], halign: 'center', font: 'helvetica' },
    })
    y = doc.lastAutoTable.finalY + 6

    y = paragraph(
      doc,
      y,
      `Número de ecuaciones (n): ${n}    ·    Punto inicial x0: [${result.x0
        .map((v) => formatNumber(v))
        .join(', ')}]`
    )
    y = paragraph(
      doc,
      y,
      `Tolerancia: ${system.tolerance}    ·    Máximo de iteraciones: ${system.max_iterations}`
    )
    y = paragraph(
      doc,
      y,
      'Cada ecuación se despejó automáticamente para su variable; la actualización es ' +
        'secuencial: cada x_i usa los valores ya recalculados en la misma iteración.'
    )

    return y
  }

  return {
    title: 'Sistemas de ecuaciones no lineales — Punto Fijo',
    writeInputSection,
    statusExtras: [],
    fileStem: `${result.method}-${n}x${n}`,
  }
}
