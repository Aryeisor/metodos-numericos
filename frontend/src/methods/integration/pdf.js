// PDF del resultado de integración numérica, con el mismo estilo que el de
// diferenciación (utils/exportPdf.js), siempre en tema claro: datos, resumen y
// advertencias, gráfico de trapecios, gráfico de convergencia, tablas
// completas (no sólo la página visible) y comprobación. La fuente estándar
// de jsPDF (WinAnsi) no tiene subíndices ni letras griegas: se escriben
// "x0", "Et", "<=".
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { CONTENT_WIDTH, MARGIN, ensureSpace, paragraph, sectionTitle } from '../../utils/exportPdf'
import { formatNumber } from '../../utils/iterationSteps'
import { latexToText } from '../../utils/latexText'
import { substitutionText } from '../differentiation/formulas'
import { conclusionText, pointSubstitution, referenceExplanation, rowSteps, segmentSteps, tinyErrorNote } from './explain'
import {
  APPROX_GLOSSARY,
  BOUND_GLOSSARY,
  COMPOSITE_GLOSSARY,
  comparisonColumns,
  refinementColumns,
  segmentColumns,
} from './glossary'

export const TABLE = {
  theme: 'striped',
  margin: { left: MARGIN, right: MARGIN },
  styles: { fontSize: 8, halign: 'right', cellPadding: 1.5 },
  headStyles: { fillColor: [37, 99, 235], halign: 'center' },
  columnStyles: { 0: { halign: 'center' } },
}

const REPLACEMENTS = {
  '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9', '₊': '+',
  'ᵢ': 'i', 'ₜ': 't', 'ₐ': 'a', 'ₖ': 'k', 'ₙ': 'n', 'ε': 'e', '−': '-', '≈': '~', '≤': '<=', '≥': '>=', '≠': '!=',
  '′': "'", '✔': 'OK', '⚠': '(!)', '…': '...', '²': '^2', '³': '^3', 'ⁿ': '^n', '⁻': '-', '⁺': '+', '¹': '1',
  '⁹': '9', 'ˣ': '^x', '∫': 'Integral ', '̄': '', 'Σ': 'Suma', '₌': '=', '⁽': '(', '⁾': ')', '⁴': '4', '→': '->',
}
// Un carácter fuera de WinAnsi hace que jsPDF escriba toda la línea mal: se reemplaza.
export const pdfSafe = (text) =>
  String(text).replace(/[₀-₌ᵢₜₐₖₙε−≈≤≥≠′✔⚠…²³ⁿ⁻⁺¹⁹ˣ∫̄Σ⁽⁾⁴→]/g, (c) => REPLACEMENTS[c] ?? '')
export const num = (value) => (value === null || value === undefined ? '-' : formatNumber(value))
export const pct = (value) => (value === null || value === undefined ? '-' : `${formatNumber(value)} %`)
export const mark = (item) =>
  !item || item.within_bound === null || item.within_bound === undefined
    ? '-'
    : item.within_bound ? (item.by_rounding ? 'OK (R)' : 'OK') : '(!)'
export const shown = (d) => (d.exact ? d.text : d.approx)

export function addImage(doc, y, title, image) {
  if (!image?.dataUrl || !(image.width > 0)) return y
  const height = (CONTENT_WIDTH * image.height) / image.width
  y = sectionTitle(doc, y + 2, title)
  y = ensureSpace(doc, y, height)
  doc.addImage(image.dataUrl, 'PNG', MARGIN, y, CONTENT_WIDTH, height)
  return y + height + 6
}

/**
 * Utilidades de escritura del PDF de integración, ligadas a un documento y a
 * un resultado (las usa también el PDF de Simpson). `weightReason(i, n)`
 * agrega la columna «Por qué» del peso en la tabla de puntos.
 */
export function pdfTools(doc, result, { weightReason = null } = {}) {
  const write = (y, text) => paragraph(doc, y, pdfSafe(text))
  const writeMath = (y, latex) => write(y, `   ${latexToText(latex)}`)
  const label = (y, text) => {
    y = ensureSpace(doc, y, 10)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.setTextColor(31, 41, 55)
    doc.text(pdfSafe(text), MARGIN, y)
    return y + 5
  }
  const derivation = (y, steps, result) => {
    for (const term of steps.terms) y = write(y, `   ${latexToText(term.latex)}   (${term.rule})`)
    const last = steps.sum_latex || result
    return last ? writeMath(y, last) : y
  }
  const glossary = (y, title, items, summary) => {
    y = label(y, title)
    for (const item of items) y = write(y, `- ${latexToText(item.symbol)}: ${item.text}`)
    return summary ? write(y, summary) : y
  }
  const pointsTable = (y, row) => {
    const first = row.step.kind === 'formula'
    const head = first
      ? ['i', 'xi', 'Sustitución', 'f(xi)', 'Peso', ...(weightReason ? ['Por qué'] : []), 'Peso x f(xi)']
      : ['i', 'xi', 'Sustitución', 'f(xi)']
    const points = row.step.points.length > 16 ? [...row.step.points.slice(0, 8), ...row.step.points.slice(-8)] : row.step.points
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [head],
      body: points.map((p) => {
        const line = [p.i, shown(p.x_display), pdfSafe(substitutionText(pointSubstitution(result, p)).replace(/^f'/, 'f')), p.f_display]
        const reason = weightReason ? [pdfSafe(weightReason(p.i, row.n))] : []
        return first ? [...line, p.weight, ...reason, p.product] : line
      }),
    })
    y = doc.lastAutoTable.finalY + 4
    if (row.step.count > points.length) {
      y = write(y, `Se muestran ${points.length} de ${row.step.count} puntos; la suma usa todos.`)
    }
    return y
  }
  const steps = (y, list, row) => {
    for (const s of list) {
      y = label(y + 1, s.title)
      for (const block of s.blocks) {
        if (block.kind === 'text' || block.kind === 'note') y = write(y, block.text)
        else if (block.kind === 'math') y = writeMath(y, block.latex)
        else if (block.kind === 'check') {
          const markText = block.ok === true ? ' OK' : block.ok === false ? ' (!)' : ''
          if (block.latex) y = writeMath(y, `${block.latex}${markText ? ` \\text{${markText}}` : ''}`)
          y = write(y, block.text)
        } else if (block.kind === 'points') y = pointsTable(y, row)
        else if (block.kind === 'division') {
          const points = row.step.points.length > 16 ? [...row.step.points.slice(0, 8), ...row.step.points.slice(-8)] : row.step.points
          for (const p of points) {
            const x = p.x_display.exact ? p.x_display.text : `~ ${p.x_display.approx}`
            y = write(y, `   x${p.i} = ${shown(result.a_display)} + ${p.i}·${row.h.exact ? row.h.text : row.h.approx} = ${x}`)
          }
        }
      }
    }
    return y
  }

  // Integral por otro camino: antiderivada paso a paso, F' = f y F(b) − F(a), o la referencia.
  const integralCheck = (y) => {
    const integral = result.integral
    const check = result.verification
    if (integral?.kind === 'exact' && check.upper) {
      const anti = integral.antiderivative
      y = label(y + 1, 'Antiderivada F(x): una función cuya derivada es f')
      if (anti.steps.detailed) {
        y = write(y, 'Se integra f término a término, con la regla de cada término:')
        y = derivation(y, anti.steps, `F(x) = ${anti.latex}`)
      } else {
        y = write(y, `F(x) = ${anti.text}`)
        y = write(y, 'Antiderivada obtenida con integración simbólica; la técnica no se detalla aquí.')
      }
      y = label(y + 1, 'Verificación de la antiderivada: al derivar F debe salir f')
      y = derivation(y, { terms: anti.check.terms }, null)
      y = writeMath(y, `${anti.check.sum_latex} ${anti.check.ok ? '= f(x) \\text{ OK}' : '\\ne f(x) \\text{ (!)}'}`)
      y = label(y + 1, 'Teorema fundamental del cálculo: la integral de a a b es F(b) - F(a)')
      y = write(y, substitutionText(check.upper).replace(/^f'/, 'F'))
      y = write(y, check.lower.all_zero
        ? `F(${shown(result.a_display)}) = 0 (todos sus términos se anulan)`
        : substitutionText(check.lower).replace(/^f'/, 'F'))
      y = write(y, `I = F(b) - F(a) = ${num(check.upper.value)} - ${num(check.lower.value)} = ${num(integral.value)}`)
    } else if (integral?.kind === 'reference') {
      y = write(y, `${referenceExplanation(integral)} Se compara con el ${integral.label}, I ~ ${num(integral.value)}.`)
    }
    return y
  }
  return { write, writeMath, label, derivation, glossary, pointsTable, steps, integralCheck }
}

export function exportIntegrationPdf({ result, methodName, trapezoidImage, trapezoidRow, convergenceImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const isTable = result.mode === 'table'
  const fn = result.function
  const integral = result.integral
  const check = result.verification
  const { write, writeMath, label, derivation, glossary, steps, integralCheck } = pdfTools(doc, result)

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
    y = write(y, 'Modo: tabla de datos (espaciado ' + (result.uniform ? 'uniforme' : 'no uniforme') + ')')
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
      `Segmentos iniciales n0 = ${result.n0}    ·    Tolerancia del error estimado: ${formatNumber(result.tolerance)}` +
        `    ·    Máximo de refinamientos: ${result.max_iterations}`
    )
    y = write(y, `Regla: ${result.rule.formula_text}`)
  }
  if (fn) {
    y = label(y + 1, 'Derivadas de f(x)')
    y = write(
      y,
      "f'(x) se usa en el error aproximado de Chapra (el promedio de f''); f''(x) en la cota del error, porque mide " +
        'qué tan curva es la función: mientras más curva, más se separan los trapecios de la curva.'
    )
    y = write(y, 'Primera derivada, término a término:')
    y = derivation(y, fn.first.steps, `f'(x) = ${fn.first.latex}`)
    y = write(y, "Segunda derivada: se deriva f'(x) con el mismo desglose:")
    y = derivation(y, fn.second.steps, `f''(x) = ${fn.second.latex}`)
    if (fn.uses_trigonometry) y = write(y, 'Las funciones trigonométricas se evalúan en radianes.')
  }

  // --- Resultado ----------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Resultado')
  const last = result.iterations.at(-1).extra
  if (isTable) {
    y = write(y, `Suma de los trapecios: I ~ T = ${num(result.total)}    ·    Segmentos: ${result.iterations_used}`)
  } else {
    y = write(
      y,
      `Estado: ${result.converged ? 'ALCANZÓ LA TOLERANCIA' : 'NO ALCANZÓ LA TOLERANCIA'}    ·    ` +
        `Filas usadas: ${result.iterations_used}    ·    I ~ T = ${num(last.T)} (n = ${last.n})`
    )
  }
  if (integral && integral.value !== null) {
    y = write(y, `I = ${num(integral.value)} (${integral.label})`)
    const errors = isTable ? check.final : last
    if (errors?.true_error !== null && errors?.true_error !== undefined) {
      const about = integral.kind === 'reference' ? ' (respecto al valor de referencia)' : ''
      y = write(y, `Error verdadero${about}: Et = ${num(errors.true_error)}    ·    et = ${pct(errors.relative_error)}`)
    }
  }
  for (const note of result.notes ?? []) y = write(y, `Nota: ${note}`)
  for (const warning of result.warnings ?? []) y = write(y, `Advertencia: ${warning}`)

  // --- Gráficos ----------------------------------------------------------------
  const rowTitle = trapezoidRow ? ` (n = ${trapezoidRow.n})` : ''
  y = addImage(doc, y, `Gráfico de los trapecios${rowTitle}`, trapezoidImage)
  y = addImage(doc, y, 'Convergencia del error (escala logarítmica)', convergenceImage)

  // --- Tablas completas --------------------------------------------------------------
  if (isTable) {
    y = sectionTitle(doc, y + 2, 'Tabla de segmentos')
    const head = ['i', '[xi, xi+1]', 'hi', 'yi', 'yi+1', 'Área', 'Acumulada']
    if (fn) head.push('Cota')
    autoTable(doc, {
      ...TABLE,
      startY: y,
      head: [head],
      body: result.iterations.map((step) => {
        const s = step.extra
        const row = [s.i, `[${shown(s.x_display[0])}, ${shown(s.x_display[1])}]`, shown(s.width), num(s.y[0]),
          num(s.y[1]), s.area_display, num(s.cumulative)]
        if (fn) row.push(s.bound === null ? 'no disp.' : num(s.bound))
        return row
      }),
    })
    y = doc.lastAutoTable.finalY + 4
    y = glossary(y, '¿Qué significa cada columna?', segmentColumns(Boolean(fn)))
    y = label(y + 2, 'Paso a paso de cada segmento')
    const segments = result.iterations.map((step) => step.extra)
    for (const s of segments) {
      y = label(y + 1, `Segmento ${s.i}`)
      for (const st of segmentSteps(s, s.i > 0 ? segments[s.i - 1] : null)) {
        y = write(y, `${st.title}: ${st.blocks.filter((b) => b.kind === 'text').map((b) => b.text).join(' ')}`)
        for (const b of st.blocks) if (b.kind === 'math') y = writeMath(y, b.latex)
      }
    }
  } else {
    y = sectionTitle(doc, y + 2, 'Tabla de refinamiento')
    const showTrue = integral.value !== null
    const head = ['k', 'n', 'h', 'T', 'Error estimado']
    if (showTrue) head.push('Et', 'et')
    if (result.mean_second) head.push('Ea')
    head.push('Cota')
    if (showTrue) head.push('Razón', '<= cota')
    autoTable(doc, {
      ...TABLE,
      startY: y,
      head: [head],
      body: result.iterations.map((step) => {
        const e = step.extra
        const row = [step.iteration, e.n, e.h.exact ? e.h.text : `${e.h.text} ~ ${e.h.approx}`, num(e.T), num(e.estimated_error)]
        if (showTrue) row.push(num(e.true_error), pct(e.relative_error))
        if (result.mean_second) row.push(num(e.approx_error))
        row.push(e.bound === null ? 'no disp.' : num(e.bound))
        if (showTrue) row.push(num(e.ratio), mark(e))
        return row
      }),
    })
    y = doc.lastAutoTable.finalY + 4
    const reference = integral.kind === 'reference'
    const tinyRows = result.iterations.filter((s) => tinyErrorNote(s.extra, reference))
    if (tinyRows.length) {
      y = write(y, `Filas ${tinyRows.map((s) => s.iteration).join(', ')}: ${tinyErrorNote(tinyRows[0].extra, reference)}`)
    }
    if (result.iterations.some((s) => s.extra.by_rounding)) {
      y = write(y, '"OK (R)": |Et| supera la cota (más de 10^-9 relativo) y se cumple sólo con el margen de redondeo R.')
    }

    y = sectionTitle(doc, y + 2, 'Glosario de las fórmulas y de las columnas')
    y = write(y, `Regla compuesta: ${latexToText(result.rule.formula_latex)}`)
    y = glossary(y, '¿Qué significa cada símbolo?', COMPOSITE_GLOSSARY.items, COMPOSITE_GLOSSARY.summary)
    if (result.mean_second) {
      y = write(y + 1, "Error aproximado: Ea = -[(b - a)h^2/12]·f'' promedio, f'' promedio = [f'(b) - f'(a)]/(b - a)")
      y = glossary(y, '¿Qué significa cada símbolo?', APPROX_GLOSSARY.items)
    }
    y = write(y + 1, `Cota: ${latexToText(result.rule.bound_latex)}`)
    y = glossary(y, '¿Qué significa cada símbolo?', BOUND_GLOSSARY.items)
    y = glossary(
      y + 1,
      '¿Qué significa cada columna?',
      refinementColumns({ showTrue, showApprox: Boolean(result.mean_second), reference })
    )

    // Paso a paso explicado: filas 1, 2 y la última.
    const all = result.iterations
    const chosen = [...new Set([0, 1, all.length - 1])].filter((i) => i < all.length)
    y = sectionTitle(doc, y + 2, 'Paso a paso explicado')
    for (const i of chosen) {
      if (i === all.length - 1 && i > 2) y = write(y, 'El resto de las filas sigue el mismo procedimiento.')
      const row = all[i].extra
      y = label(y + 2, `Fila ${all[i].iteration} (n = ${row.n})`)
      y = steps(y, rowSteps(result, row, all[i].iteration, i > 0 ? all[i - 1].extra : null), row)
    }
  }

  // --- Comprobación --------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Comprobación')
  if (isTable) {
    const relation = check.areas_sum === check.total_display ? '=' : '~'
    y = write(y, `Suma de las áreas: ${check.areas.join(' + ')} ${relation} ${check.total_display} OK`)
    if (result.composite) {
      const c = result.composite
      y = write(y, `Fórmula compuesta con h = ${c.h.text}: (h/2)[y0 + 2(${c.interior_sum}) + yn] = ${c.half_h}·${c.bracket} = ` +
        `${num(c.value)} ${c.equal ? '= suma de los trapecios OK' : '(!) distinto de la suma'}`)
    }
    if (check.data) {
      y = write(y + 2, 'Datos contra la función: |yi - f(xi)| <= 10^-6 · máx(1, |f(xi)|).')
      autoTable(doc, {
        ...TABLE,
        theme: 'grid',
        startY: y,
        head: [['i', 'yi', 'f(xi)', '|yi - f(xi)|', '']],
        body: check.data.map((row) => [row.i, num(row.y), num(row.f), num(row.difference),
          row.ok ? 'OK' : '(!) el dato no coincide con la función']),
      })
      y = doc.lastAutoTable.finalY + 6
    }
  }
  if (!isTable) {
    y = write(
      y,
      'La comprobación calcula la integral por otro camino' +
        (integral?.kind === 'exact' ? ' (con la antiderivada)' : '') +
        ' y la compara con el resultado del trapecio.'
    )
  } else {
    y = write(y, 'Con datos, el área total es la suma de las áreas de los trapecios de cada segmento.')
  }
  y = integralCheck(y)
  const final = isTable ? check.final : { ...check.final, I: integral.value }
  if (final && final.true_error !== null && final.true_error !== undefined) {
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['T', 'I', 'Et = I - T', 'et', 'Cota', '|Et| <= cota']],
      body: [[num(final.T), num(final.I), num(final.true_error), pct(final.relative_error),
        final.bound === null ? 'no disp.' : num(final.bound), mark(final)]],
    })
    y = doc.lastAutoTable.finalY + 6
    const tiny = tinyErrorNote(final, integral?.kind === 'reference')
    if (tiny) y = write(y, tiny)
    y = glossary(y, '¿Qué significa cada columna?', comparisonColumns({ reference: integral?.kind === 'reference', isTable }))
    const conclusion = conclusionText(result, final)
    if (conclusion) y = write(y + 1, conclusion)
  }
  if (!isTable && integral.value !== null && result.M2) {
    y = check.all_within
      ? write(y, 'En todas las filas |Et| quedó por debajo de la cota teórica OK')
      : write(y, `(!) |Et| supera la cota en las filas ${check.failed_rows.join(', ')}.`)
  }

  doc.save(`trapecio-${isTable ? 'tabla' : 'funcion'}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
