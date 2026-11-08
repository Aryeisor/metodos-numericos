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
import { substitutionText } from '../differentiation/formulas'

const TABLE = {
  theme: 'striped',
  margin: { left: MARGIN, right: MARGIN },
  styles: { fontSize: 8, halign: 'right', cellPadding: 1.5 },
  headStyles: { fillColor: [37, 99, 235], halign: 'center' },
  columnStyles: { 0: { halign: 'center' } },
}

const REPLACEMENTS = {
  '₀': '0', '₁': '1', '₂': '2', 'ᵢ': 'i', 'ₜ': 't', 'ₐ': 'a', 'ε': 'e', '−': '-', '≈': '~', '≤': '<=',
  '≥': '>=', '′': "'", '✔': 'OK', '⚠': '(!)', '…': '...', '·': '·', '²': '^2', '³': '^3',
}
const pdfSafe = (text) => String(text).replace(/Σ/g, 'Suma').replace(/[₀₁₂ᵢₜₐε−≈≤≥′✔⚠…²³]/g, (c) => REPLACEMENTS[c] ?? c)
const num = (value) => (value === null || value === undefined ? '-' : formatNumber(value))
const pct = (value) => (value === null || value === undefined ? '-' : `${formatNumber(value)} %`)
const mark = (item) =>
  !item || item.within_bound === null || item.within_bound === undefined
    ? '-'
    : item.within_bound ? (item.by_rounding ? 'OK (R)' : 'OK') : '(!)'
const shown = (d) => (d.exact ? d.text : d.approx)

function addImage(doc, y, title, image) {
  if (!image?.dataUrl || !(image.width > 0)) return y
  const height = (CONTENT_WIDTH * image.height) / image.width
  y = sectionTitle(doc, y + 2, title)
  y = ensureSpace(doc, y, height)
  doc.addImage(image.dataUrl, 'PNG', MARGIN, y, CONTENT_WIDTH, height)
  return y + height + 6
}

export function exportIntegrationPdf({ result, methodName, trapezoidImage, trapezoidRow, convergenceImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const isTable = result.mode === 'table'
  const fn = result.function
  const integral = result.integral
  const check = result.verification
  const write = (y, text) => paragraph(doc, y, pdfSafe(text))

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
    y = write(y, `Integral: de a = ${shown(result.a_display)} a b = ${shown(result.b_display)} de f(x) = ${fn.text} dx`)
    y = write(
      y,
      `Segmentos iniciales n0 = ${result.n0}    ·    Tolerancia del error estimado: ${formatNumber(result.tolerance)}` +
        `    ·    Máximo de refinamientos: ${result.max_iterations}`
    )
    y = write(y, `Regla: ${result.rule.formula_text}`)
  }
  if (fn) {
    y = write(y, `f'(x) = ${fn.first.text}    ·    f''(x) = ${fn.second.text}`)
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
    y = write(y, 'Paso a paso: Ai = hi·(yi + yi+1)/2.')
    for (const step of result.iterations) {
      const s = step.extra
      y = write(y, `A${s.i} = ${shown(s.width)}·(${shown(s.y_display[0])} + ${shown(s.y_display[1])})/2 = ${shown(s.width)}·${s.pair_sum}/2 = ${s.area_display}`)
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
    if (result.mean_second) {
      y = write(y, `Ea = -(b - a)h²/12 · f'' promedio, con f'' promedio = (f'(b) - f'(a))/(b - a) = ` +
        `(${num(result.mean_second.fb)} - ${num(result.mean_second.fa)})/${shown(result.width_display)} = ${num(result.mean_second.value)}.`)
    }
    if (result.M2) {
      y = write(y, `Cota = (b - a)h²/12 · M2, con M2 = máx |f''(x)| ~ ${num(result.M2.value)} en x ~ ${shown(result.M2.x_display)} ` +
        `(muestreo con ${result.sampling_points} puntos). "OK (R)": |Et| supera la cota sólo por el redondeo R.`)
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
  if (integral?.kind === 'exact' && check.upper) {
    y = write(y, `Antiderivada: F(x) = ${integral.antiderivative.text}`)
    y = write(y, substitutionText(check.upper).replace(/^f'/, 'F'))
    y = write(y, check.lower.all_zero
      ? `F(${shown(result.a_display)}) = 0 (todos sus términos se anulan)`
      : substitutionText(check.lower).replace(/^f'/, 'F'))
    y = write(y, `I = F(b) - F(a) = ${num(check.upper.value)} - ${num(check.lower.value)} = ${num(integral.value)}`)
  } else if (integral?.kind === 'reference') {
    y = write(y, `No hay una antiderivada elemental: se compara con el ${integral.label}, I ~ ${num(integral.value)}.`)
  }
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
  }
  if (!isTable && integral.value !== null && result.M2) {
    y = check.all_within
      ? write(y, 'En todas las filas |Et| quedó por debajo de la cota teórica OK')
      : write(y, `(!) |Et| supera la cota en las filas ${check.failed_rows.join(', ')}.`)
  }

  doc.save(`trapecio-${isTable ? 'tabla' : 'funcion'}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
