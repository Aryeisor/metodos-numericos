// PDF del resultado de diferenciación numérica, con el mismo estilo que el de
// los demás métodos (utils/exportPdf.js), siempre en tema claro: datos,
// derivada exacta, resultado y advertencias, gráfico, tablas completas (no
// sólo la página visible) y comprobación. La fuente estándar de jsPDF
// (WinAnsi) no tiene subíndices ni letras griegas: se escriben "x0", "e", "<=".
// h sigue la excepción 1: exacto, o la forma 0.1/2^14.
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { CONTENT_WIDTH, MARGIN, ensureSpace, paragraph, sectionTitle } from '../../utils/exportPdf'
import { formatNumber } from '../../utils/iterationSteps'
import { derivativeName, identityText, listNames, stepText, substitutionText } from './formulas'

const HEAD = { fillColor: [37, 99, 235], halign: 'center' }
const TABLE = {
  theme: 'striped',
  margin: { left: MARGIN, right: MARGIN },
  styles: { fontSize: 8, halign: 'right', cellPadding: 1.5 },
  headStyles: HEAD,
  columnStyles: { 0: { halign: 'center' } },
}

const PDF_REPLACEMENTS = {
  '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
  'ᵢ': 'i', '⁺': '+', '⁻': '-', 'ᵏ': '^k', ε: 'e', Δ: 'D', ξ: 'x', '×': 'x', '≈': '~', '−': '-',
  '≥': '>=', '≤': '<=', '′': "'", '″': "''", '✔': 'OK', '⚠': '(!)', '…': '...',
}
const SUPERSCRIPT_DIGITS = { '⁻': '-', '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9' }
const pdfSafe = (text) =>
  String(text)
    // 5.9×10⁻⁸ (comparación con diferencias) -> 5.9e-8
    .replace(/×10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g, (_, power) => `e${[...power].map((c) => SUPERSCRIPT_DIGITS[c]).join('')}`)
    .replace(/Σ/g, 'Suma')
    .replace(/[₀-₉ᵢ⁺⁻ᵏεΔξ×≈−≥≤′″✔⚠…]/g, (c) => PDF_REPLACEMENTS[c] ?? c)
const num = (value) => (value === null || value === undefined ? '-' : formatNumber(value))
const mark = (item) => (!item || item.within_bound === null ? '-' : item.within_bound ? (item.by_rounding ? 'OK (R)' : 'OK') : '(!)')
const formulaNames = (result) => listNames(result.formulas.map((f) => f.name))
// Encabezados cortos de la tabla del modo datos (las de 3 puntos no caben).
const SHORT_NAMES = { punto_medio: 'Medio', extremo_adelante: 'Adelante', extremo_atras: 'Atrás' }
const short = (formula) => SHORT_NAMES[formula.key] ?? formula.name
// Título de cada método (el de diferencias se conserva tal cual).
const TITLES = { 'diferencias-finitas': 'Diferencias finitas' }
const STEMS = { 'diferencias-finitas': 'diferencias' }

export function exportDifferentiationPdf({ result, methodName, chartImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const isTable = result.mode === 'table'
  const fn = result.function
  const write = (y, text) => paragraph(doc, y, pdfSafe(text))

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.setTextColor(31, 41, 55)
  doc.text(`Diferenciación numérica — ${TITLES[result.method] ?? methodName}`, MARGIN, MARGIN + 4)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(107, 114, 128)
  doc.text(`Método: ${methodName}  ·  Generado el ${new Date().toLocaleString('es-CO')}`, MARGIN, MARGIN + 11)
  let y = MARGIN + 20

  // --- Datos -----------------------------------------------------------------
  y = sectionTitle(doc, y, 'Datos')
  if (isTable) {
    y = write(y, `Modo: tabla de datos    ·    Fórmula: ${formulaNames(result)}`)
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['i', 'xi', 'f(xi)']],
      body: result.points.map(([x, yValue], i) => [i + 1, result.iterations[i].extra.x_display.text, num(yValue)]),
    })
    y = doc.lastAutoTable.finalY + 6
    y = write(y, fn ? `Función para comparar: f(x) = ${fn.text}` : 'Sin función para comparar.')
  } else {
    y = write(y, `Modo: función    ·    f(x) = ${fn.text}`)
    y = write(
      y,
      `x0 = ${result.x0_display.text}    ·    h0 = ${stepText(result.iterations[0].extra.h)}    ·    ` +
        `Fórmula: ${formulaNames(result)}    ·    Tolerancia del error estimado: ${formatNumber(result.tolerance)}` +
        `    ·    Máximo de refinamientos de h: ${result.max_iterations}`
    )
  }
  for (const f of result.formulas) y = write(y, `${f.name}: ${f.formula_text}`)

  // --- Derivada exacta ----------------------------------------------------------
  if (fn) {
    y = sectionTitle(doc, y + 2, 'Derivada exacta')
    y = write(y, `f'(x) = ${fn.derivative.text}`)
    for (const [n, d] of Object.entries(fn.higher_derivatives)) {
      y = write(y, `${derivativeName(Number(n), null)}(x) = ${d.text}`)
    }
    if (fn.uses_trigonometry) y = write(y, 'Las funciones trigonométricas se evalúan en radianes.')
  }

  // --- Resultado ----------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Resultado')
  if (isTable) {
    y = write(y, `Puntos: ${result.iterations_used}    ·    Espaciado: ${result.uniform ? 'uniforme' : 'no uniforme'}`)
  } else {
    const lastRow = result.iterations.at(-1).extra
    y = write(
      y,
      `Estado: ${result.converged ? 'ALCANZÓ LA TOLERANCIA' : 'NO ALCANZÓ LA TOLERANCIA'}    ·    ` +
        `Filas usadas: ${result.iterations_used}`
    )
    for (const f of result.formulas) y = write(y, `${f.name}: f'(x0) ~ ${num(lastRow[f.key].D)}`)
    y = write(y, result.differentiable ? `Valor exacto: f'(x0) = ${num(result.exact)}` : 'f no es derivable en x0.')
  }
  for (const line of result.comparison ?? []) y = write(y, line.text)
  for (const warning of result.warnings ?? []) y = write(y, `Advertencia: ${warning}`)

  // --- Gráfico ----------------------------------------------------------------
  if (chartImage?.dataUrl && chartImage.width > 0) {
    const height = (CONTENT_WIDTH * chartImage.height) / chartImage.width
    y = sectionTitle(doc, y + 2, isTable ? "Aproximaciones de f'(x) en cada punto" : 'Convergencia del error (escala logarítmica)')
    y = ensureSpace(doc, y, height)
    doc.addImage(chartImage.dataUrl, 'PNG', MARGIN, y, CONTENT_WIDTH, height)
    y += height + 6
  }

  // --- Tablas completas ----------------------------------------------------------
  if (isTable) {
    y = sectionTitle(doc, y + 2, 'Derivada en cada punto')
    const recommended = Boolean(result.iterations[0]?.extra.recommended)
    const head = ['i', 'xi', 'f(xi)', ...result.formulas.map((f) => short(f))]
    if (recommended) head.push('Recomendada')
    if (fn) {
      head.push("f'(xi)", ...result.formulas.map((f) => `Error ${short(f).toLowerCase()}`),
        ...result.formulas.map((f) => `Cota ${short(f).toLowerCase()}`), '<= cota')
    }
    autoTable(doc, {
      ...TABLE,
      // Con 3 fórmulas y función para comparar hay 14 columnas en vertical.
      styles: { ...TABLE.styles, fontSize: head.length > 11 ? 6.5 : TABLE.styles.fontSize },
      startY: y,
      head: [head],
      body: result.iterations.map((step) => {
        const e = step.extra
        const items = result.formulas.map((f) => e[f.key])
        const row = [step.iteration, e.x_display.text, num(e.y), ...items.map((item) => num(item?.D))]
        if (recommended) row.push(`${num(e.recommended.D)} (${short(e.recommended).toLowerCase()})`)
        if (fn) {
          row.push(num(e.exact), ...items.map((item) => num(item?.real_error)),
            ...items.map((item) => (item && item.bound === null ? 'no disp.' : num(item?.bound))),
            items.filter(Boolean).map(mark).join(' '))
        }
        return row
      }),
    })
    y = doc.lastAutoTable.finalY + 6
  } else {
    for (const f of result.formulas) {
      y = sectionTitle(doc, y + 2, `Tabla de refinamiento: ${f.name}`)
      const head = ['k', 'h', 'D', 'Error estimado']
      if (result.differentiable) head.push('Error real')
      head.push('Cota')
      if (result.differentiable) head.push('Razón', '<= cota')
      autoTable(doc, {
        ...TABLE,
        startY: y,
        head: [head],
        body: result.iterations.map((step) => {
          const item = step.extra[f.key]
          const row = [step.iteration, stepText(step.extra.h), num(item.D), num(item.estimated_error)]
          if (result.differentiable) row.push(num(item.real_error))
          row.push(item.bound === null ? 'no disp.' : num(item.bound))
          if (result.differentiable) row.push(num(item.ratio), mark(item))
          return row
        }),
      })
      y = doc.lastAutoTable.finalY + 4
    }
    y = write(
      y,
      `La cota usa M = máx |${derivativeName(result.formulas[0].bound_derivative, null)}(x)| en el intervalo de cada fila, estimado por muestreo con ` +
        `${result.sampling_points} puntos. "OK (R)": el error real supera la cota sólo por el redondeo ` +
        `${result.rounding_text ?? 'R = 4e·máx|f|/h'}.`
    )
  }

  // --- Comprobación --------------------------------------------------------------
  const check = result.verification
  y = sectionTitle(doc, y + 2, 'Comprobación')
  if (check.identities) {
    y = write(
      y,
      `${isTable ? 'En cada punto, con los datos' : 'En la fila 1, con los valores sin redondear'}: el punto medio ` +
        'es el promedio de la progresiva y la regresiva, y cada extremo es una extrapolación de Richardson, 2D(h) - D(2h).'
    )
    const groups = isTable ? check.identities : [{ i: null, items: check.identities }]
    for (const group of groups) {
      for (const item of group.items) {
        y = write(y, `${group.i === null ? '' : `x${group.i} = ${group.x_display.text}: `}${item.name}: ${identityText(item)}`)
      }
    }
    y += 2
  }
  if (isTable && check.secant) {
    y = write(y, 'Secante común: la progresiva en xi y la regresiva en xi+1 deben ser iguales.')
    for (const pair of check.secant) {
      y = write(y, `D+(x${pair.i}) = D-(x${pair.i + 1}) = ${num(pair.forward)} ${pair.equal ? 'OK' : `(!) (${num(pair.backward)})`}`)
    }
  }
  if (isTable) {
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
  const substitutions = isTable ? (check.substitutions ?? []).filter(Boolean) : check.substitution ? [check.substitution] : []
  if (substitutions.length) {
    y = write(y, `Sustitución en f'(x) = ${fn.derivative.text}, término a término:`)
    for (const s of substitutions) y = write(y, substitutionText(s))
  }
  if (!isTable && result.differentiable) {
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['Fórmula', 'Aproximación', "Exacta f'(x0)", 'Error real', 'Cota', '<= cota']],
      body: result.formulas.map((f) => {
        const item = check.final[f.key]
        return [f.name, num(item.D), num(result.exact), num(item.real_error),
          item.bound === null ? 'no disp.' : num(item.bound), mark(item)]
      }),
    })
    y = doc.lastAutoTable.finalY + 6
  }
  if (fn && (isTable || result.differentiable)) {
    if (check.all_within) {
      y = write(y, `En ${isTable ? 'todos los puntos' : 'todas las filas'} el error real quedó por debajo de la cota teórica OK`)
    } else {
      for (const f of result.formulas) {
        const rows = check.failed_rows?.[f.key] ?? []
        if (rows.length) y = write(y, `(!) ${f.name}: el error real supera la cota en ${isTable ? 'los puntos' : 'las filas'} ${rows.join(', ')}.`)
      }
    }
  }

  const stem = `${STEMS[result.method] ?? result.method}-${isTable ? 'tabla' : 'funcion'}`
  doc.save(`${stem}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
