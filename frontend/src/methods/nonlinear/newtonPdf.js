// Partes del PDF propias de Newton: la sección "Datos del sistema"
// (ecuaciones, variables en orden, Jacobiano simbólico, x0 y parámetros).
// jsPDF no dibuja LaTeX: se usan las ecuaciones tal como se escribieron y las
// versiones en texto plano que entrega el backend.
import autoTable from 'jspdf-autotable'

import { formatNumber } from '../../utils/iterationSteps'
import { MARGIN, paragraph, sectionTitle } from '../../utils/exportPdf'

const TABLE_HEAD = { fillColor: [37, 99, 235], halign: 'center', font: 'helvetica' }

export function newtonPdfReport({ result, system }) {
  const n = result.variables.length

  function writeInputSection(doc, startY) {
    let y = sectionTitle(doc, startY, 'Datos del sistema')

    autoTable(doc, {
      startY: y,
      head: [['#', 'Ecuación ingresada', 'f_i(x) = 0']],
      body: result.equations.map((equation, i) => [
        String(i + 1),
        system.equations[i],
        equation.function_text,
      ]),
      theme: 'grid',
      margin: { left: MARGIN, right: MARGIN },
      styles: { fontSize: 9, cellPadding: 2, font: 'courier' },
      columnStyles: { 0: { halign: 'center', cellWidth: 10, font: 'helvetica' } },
      headStyles: TABLE_HEAD,
    })
    y = doc.lastAutoTable.finalY + 6

    y = paragraph(doc, y, `Variables, en orden: ${result.variables.join(', ')}`)

    // Jacobiano simbólico: fila i = f_i, columna j = derivada respecto de la variable j.
    autoTable(doc, {
      startY: y,
      head: [['J(x)', ...result.variables.map((v) => `d/d${v}`)]],
      body: result.jacobian.text.map((row, i) => [`f${i + 1}`, ...row]),
      theme: 'grid',
      margin: { left: MARGIN, right: MARGIN },
      styles: { fontSize: 9, cellPadding: 2, font: 'courier' },
      columnStyles: { 0: { halign: 'center', cellWidth: 14, font: 'helvetica' } },
      headStyles: TABLE_HEAD,
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
      'En cada iteración se resuelve J(x) · Dx = -F(x) por la regla de Cramer ' +
        '(Dx_i = D_i / D) y se actualiza x = x + Dx.'
    )

    return y
  }

  return {
    title: 'Sistemas de ecuaciones no lineales — Newton',
    writeInputSection,
    statusExtras: [],
    fileStem: `${result.method}-${n}x${n}`,
  }
}
