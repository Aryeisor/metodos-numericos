// PDF del resultado de Bairstow, con el mismo estilo que el de los demás
// métodos (utils/exportPdf.js): datos de entrada, tabla de coeficientes, por
// cada factor su tabla de iteraciones y su gráfico, tabla de raíces y
// factorización y comprobación de cada raíz. La fuente estándar de jsPDF (WinAnsi) no tiene letras
// griegas ni superíndices como ⁴: se escriben "Dr", "er", "x^4".
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { CONTENT_WIDTH, MARGIN, ensureSpace, paragraph, sectionTitle } from '../../utils/exportPdf'
import { formatNumber } from '../../utils/iterationSteps'
import { CHECK_TEXT_STYLE, complexCheckRows, complexCheckText, polynomialText, realCheckText } from './formulas'

const HEAD = { fillColor: [37, 99, 235], halign: 'center' }

// Caracteres de los mensajes del backend que la fuente WinAnsi no tiene.
const PDF_REPLACEMENTS = { '₀': '0', ε: 'e', Δ: 'D', '×': 'x', '≈': '~', '−': '-', 'ᵏ': '^k', '≥': '>=', '≤': '<=' }
const pdfSafe = (text) => text.replace(/[₀εΔ×≈−ᵏ≥≤]/g, (c) => PDF_REPLACEMENTS[c])

function complexText(re, im) {
  if (im === 0) return formatNumber(re)
  const imaginary = `${formatNumber(Math.abs(im))}i`
  if (re === 0) return im < 0 ? `-${imaginary}` : imaginary
  return `${formatNumber(re)} ${im < 0 ? '-' : '+'} ${imaginary}`
}

function factorText(factor) {
  if (factor.method === 'lineal_directa') return polynomialText([1, -factor.roots[0].re])
  return polynomialText([1, -factor.r, -factor.s])
}

const METHOD_TEXT = {
  bairstow: 'Bairstow',
  cuadratica_directa: 'cierre directo (formula cuadratica)',
  lineal_directa: 'cierre directo (despeje)',
}

export function exportBairstowPdf({ result, system, methodName, chartImages }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const { polynomial } = result

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.setTextColor(31, 41, 55)
  doc.text('Raíces de polinomios — Bairstow', MARGIN, MARGIN + 4)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(107, 114, 128)
  doc.text(
    `Método de ${methodName}  ·  Generado el ${new Date().toLocaleString('es-CO')}`,
    MARGIN,
    MARGIN + 11
  )
  let y = MARGIN + 20

  // --- Datos de entrada ---------------------------------------------------
  y = sectionTitle(doc, y, 'Datos del polinomio')
  y = paragraph(doc, y, `f(x) = ${polynomialText(polynomial.coefficients)}`)
  y = paragraph(
    doc,
    y,
    `Entrada: ${polynomial.input_mode === 'text' ? `texto "${polynomial.text}"` : 'coeficientes'}    ·    ` +
      `Grado: ${polynomial.degree}`
  )
  y = paragraph(
    doc,
    y,
    `Valores iniciales: r0 = ${formatNumber(result.r0)}, s0 = ${formatNumber(result.s0)}    ·    ` +
      `Tolerancia es: ${formatNumber(result.tolerance_percent)} %    ·    ` +
      `Máximo de iteraciones por factor: ${system.max_iterations}`
  )
  y = paragraph(doc, y, 'Factor cuadrático: x^2 - r x - s.')

  autoTable(doc, {
    startY: y,
    head: [['Potencia', ...polynomial.coefficients.map((_, p) => `x^${polynomial.degree - p}`)]],
    body: [['Coeficiente', ...polynomial.coefficients.map((value) => formatNumber(value))]],
    theme: 'grid',
    margin: { left: MARGIN, right: MARGIN },
    styles: { fontSize: 9, halign: 'right', cellPadding: 2 },
    headStyles: HEAD,
    columnStyles: { 0: { halign: 'left' } },
  })
  y = doc.lastAutoTable.finalY + 6

  // --- Estado ---------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Resultado')
  y = paragraph(
    doc,
    y,
    `Estado: ${result.converged ? 'CONVERGIÓ' : 'NO CONVERGIÓ'}    ·    ` +
      `Raíces encontradas: ${result.roots.length} de ${polynomial.degree}`
  )
  for (const warning of result.warnings ?? []) y = paragraph(doc, y, pdfSafe(`Advertencia: ${warning}`))
  for (const note of result.notes ?? []) y = paragraph(doc, y, pdfSafe(`Nota: ${note}`))
  if (result.zero_roots) {
    y = paragraph(
      doc,
      y,
      `Paso previo: se extrajo el factor x^${result.zero_roots} (${result.zero_roots} raíz/raíces x = 0).`
    )
  }

  // --- Factores -------------------------------------------------------------
  result.factors.forEach((factor, i) => {
    y = sectionTitle(doc, y + 2, `Factor ${i + 1}: ${factor.factor_latex ? factorText(factor) : 'sin cerrar'}`)
    y = paragraph(
      doc,
      y,
      `Polinomio que se divide: ${polynomialText(factor.dividend.coefficients)}    ·    ` +
        `Obtenido por: ${METHOD_TEXT[factor.method]}` +
        (factor.method === 'bairstow'
          ? `    ·    Iteraciones: ${factor.iterations_used}    ·    ${factor.converged ? 'convergió' : 'no convergió'}`
          : '')
    )
    if (factor.discriminant !== undefined && factor.factor_latex) {
      y = paragraph(
        doc,
        y,
        `Discriminante r^2 + 4s = ${formatNumber(factor.discriminant)}    ·    Raíces: ` +
          factor.roots.map((root) => complexText(root.re, root.im)).join(' ; ')
      )
    } else if (factor.method === 'lineal_directa') {
      y = paragraph(doc, y, `Raíz: ${complexText(factor.roots[0].re, 0)}`)
    }
    if (factor.quotient) {
      y = paragraph(
        doc,
        y,
        `Cociente: ${polynomialText(factor.quotient.coefficients)}    ·    ` +
          `Residuo: b1 = ${formatNumber(factor.residue.b1)}, b0 = ${formatNumber(factor.residue.b0)}`
      )
    }

    if (factor.method === 'bairstow') {
      const rows = factor.iteration_indices.map((index) => result.iterations[index])
      autoTable(doc, {
        startY: y,
        head: [['k', 'r', 's', 'Dr', 'Ds', 'er (%)', 'es (%)']],
        body: rows.map((row) => [
          row.iteration,
          formatNumber(row.x[0]),
          formatNumber(row.x[1]),
          formatNumber(row.extra.delta_r ?? null),
          formatNumber(row.extra.delta_s ?? null),
          formatNumber(row.extra.eps_r ?? null),
          formatNumber(row.extra.eps_s ?? null),
        ]),
        theme: 'striped',
        margin: { left: MARGIN, right: MARGIN },
        styles: { fontSize: 8, halign: 'right', cellPadding: 1.5 },
        headStyles: HEAD,
        columnStyles: { 0: { halign: 'center' } },
      })
      y = doc.lastAutoTable.finalY + 4

      const image = chartImages?.[i]
      if (image?.dataUrl && image.width > 0) {
        const height = (CONTENT_WIDTH * image.height) / image.width
        y = ensureSpace(doc, y, height)
        doc.addImage(image.dataUrl, 'PNG', MARGIN, y, CONTENT_WIDTH, height)
        y += height + 6
      }
    }
  })

  // --- Raíces y factorización ------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Raíces')
  autoTable(doc, {
    startY: y,
    head: [['Raíz', 'Valor', 'Parte real', 'Parte imaginaria', 'Tipo', 'Comprobación |f(x)|']],
    body: result.roots.map((root, i) => [
      `x${i + 1}`,
      complexText(root.re, root.im),
      formatNumber(root.re),
      formatNumber(root.im),
      root.im === 0 ? 'real' : 'compleja',
      root.check === 0 ? '0' : root.check.toExponential(2),
    ]),
    theme: 'grid',
    margin: { left: MARGIN, right: MARGIN },
    styles: { fontSize: 9, halign: 'right', cellPadding: 2 },
    headStyles: HEAD,
    columnStyles: { 0: { halign: 'center' }, 4: { halign: 'left' } },
  })
  y = doc.lastAutoTable.finalY + 6

  if (result.factorization) {
    const leading = polynomial.coefficients[0]
    const parts = []
    if (formatNumber(leading) !== '1') parts.push(formatNumber(leading))
    if (result.zero_roots) parts.push(result.zero_roots === 1 ? 'x' : `x^${result.zero_roots}`)
    for (const factor of result.factors) if (factor.factor_latex) parts.push(`(${factorText(factor)})`)
    y = paragraph(doc, y, `Factorización: f(x) = ${parts.join(' · ')}`)
  }

  // --- Comprobación ---------------------------------------------------------
  const realRoots = result.roots.filter((root) => root.im === 0 && root.verification)
  const complexRoots = result.roots.filter((root) => root.im > 0 && root.verification)
  if (realRoots.length || complexRoots.length) {
    y = sectionTitle(doc, y + 2, 'Comprobación')
    y = paragraph(doc, y, 'Cada raíz se reemplaza en el polinomio original; el resultado debe dar 0.')
    // Las raíces nulas son todas iguales: una sola línea.
    const zeros = realRoots.filter((root) => root.re === 0).length
    realRoots
      .filter((root, i) => root.re !== 0 || realRoots.findIndex((other) => other.re === 0) === i)
      .forEach((root) => {
        const multiplicity = root.re === 0 && zeros > 1 ? ` (raíz de multiplicidad ${zeros})` : ''
        y = paragraph(doc, y, realCheckText(root) + multiplicity)
      })

    for (const root of complexRoots) {
      const { lhs, rows, sum, result: final, ok } = complexCheckRows(root, CHECK_TEXT_STYLE)
      const exact = root.verification.abs === 0 ? '' : ` (|f| = ${root.verification.abs.toExponential(1)})`
      y = paragraph(doc, y + 2, `${lhs}:`)
      autoTable(doc, {
        startY: y,
        head: [['Término', 'Potencia de x', 'Coeficiente · potencia']],
        body: rows.map((row) => [row.term, row.power ?? '-', row.value]),
        foot: [['Suma', '', `${sum}  ${ok ? `${final} OK` : '(!)'}${exact}`]],
        theme: 'grid',
        margin: { left: MARGIN, right: MARGIN },
        styles: { fontSize: 9, cellPadding: 2 },
        headStyles: HEAD,
        footStyles: { fillColor: [243, 244, 246], textColor: [31, 41, 55] },
        columnStyles: { 2: { halign: 'right' } },
      })
      y = doc.lastAutoTable.finalY + 4
      y = paragraph(
        doc,
        y,
        `La raíz conjugada ${complexCheckText(root.re, -root.im)} ` +
          (ok ? 'también cumple f = 0' : 'da el valor conjugado (el mismo residuo)') +
          ', porque los coeficientes del polinomio son reales.'
      )
    }

    const residue = [...realRoots, ...complexRoots].some((root) => !root.verification.is_zero)
    if (residue) y = paragraph(doc, y, '(!) La raíz es aproximada; el residuo depende de la tolerancia usada.')
  }

  doc.save(`bairstow-grado${polynomial.degree}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
