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
import { pdfTools } from '../integration/pdf'
import { conclusionText, functionContext, numbered, tableContext, tinyRealErrorNote } from './differenceExplain'
import {
  ERRORS_GLOSSARY,
  ERRORS_LATEX,
  FIVE_POINT_ERRORS_GLOSSARY,
  FIVE_POINT_ERRORS_LATEX,
  THREE_POINT_ERRORS_GLOSSARY,
  THREE_POINT_ERRORS_LATEX,
  comparisonColumns,
  formulaGlossary,
  refinementColumns,
  tableColumns,
} from './differenceGlossary'
import { derivativeName, derivativeText, identityText, namedSteps, listNames, stepText, substitutionText } from './formulas'
import {
  COMPARISON_LEGEND,
  ENDPOINTS_NOTE,
  FIVE_POINT_COMPARISON_LEGEND,
  IDENTITY_TEXTS,
  RICHARDSON_ROUNDING_NOTE,
  RICHARDSON_TEXT,
  UNIFORM_NOTE,
  explainSteps,
  recommendedText,
} from './threePointExplain'

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
    // f⁽⁵⁾ -> f^(5) y h⁴ -> h^4 (WinAnsi tiene ¹²³, pero no ⁴ ni ⁽⁾).
    .replace(/⁽([⁰¹²³⁴⁵⁶⁷⁸⁹]+)⁾/g, (_, n) => `^(${[...n].map((c) => SUPERSCRIPT_DIGITS[c]).join('')})`)
    .replace(/[⁰⁴⁵⁶⁷⁸⁹]/g, (c) => `^${SUPERSCRIPT_DIGITS[c]}`)
    .replace(/Σ/g, 'Suma')
    .replace(/[₀-₉ᵢ⁺⁻ᵏεΔξ×≈−≥≤′″✔⚠…]/g, (c) => PDF_REPLACEMENTS[c] ?? c)
const num = (value) => (value === null || value === undefined ? '-' : formatNumber(value))
const mark = (item) => (!item || item.within_bound === null ? '-' : item.within_bound ? (item.by_rounding ? 'OK (R)' : 'OK') : '(!)')
const formulaNames = (result) => listNames(result.formulas.map((f) => f.name))
// Encabezados cortos de la tabla del modo datos (las de 3 puntos no caben).
const SHORT_NAMES = {
  punto_medio: 'Medio',
  extremo_adelante: 'Adelante',
  extremo_atras: 'Atrás',
  punto_medio_5: 'Medio 5',
  extremo_adelante_5: 'Adelante 5',
  extremo_atras_5: 'Atrás 5',
}
// En la tabla de 5 puntos, el punto medio de 3 puntos va como referencia.
const short = (formula) =>
  formula.name === 'Punto medio de 3 puntos' ? 'Medio 3' : SHORT_NAMES[formula.key] ?? formula.name
// Título de cada método (el de diferencias se conserva tal cual).
const TITLES = { 'diferencias-finitas': 'Diferencias finitas' }
const STEMS = { 'diferencias-finitas': 'diferencias' }

export function exportDifferentiationPdf({ result, methodName, chartImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const isTable = result.mode === 'table'
  const fn = result.function
  const write = (y, text) => paragraph(doc, y, pdfSafe(text))
  // Explicaciones (diferencias, 3 y 5 puntos): las mismas utilidades del PDF de integración.
  const differences = result.method === 'diferencias-finitas'
  const threePoint = result.method === 'tres-puntos'
  const fivePoint = result.method === 'cinco-puntos'
  const tools = pdfTools(doc, result)
  const safeSteps = (list) =>
    numbered(list).map((s) => ({ ...s, blocks: s.blocks.map((b) => (b.text ? { ...b, text: pdfSafe(b.text) } : b)) }))

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
    y = write(
      y,
      fivePoint
        ? "Para qué sirve cada una: f'(x) es la derivada exacta, sólo para comparar y calcular el error real. f''(x) a " +
            'f⁽⁴⁾(x) son pasos intermedios. f⁽⁵⁾(x) se usa en la cota del error, porque mide qué tanto se aleja la ' +
            'función de un polinomio de grado 4: si f⁽⁵⁾ = 0, la fórmula es exacta.'
        : threePoint
          ? "Para qué sirve cada una: f'(x) es la derivada exacta, sólo para comparar y calcular el error real. f''(x) es " +
              "un paso intermedio para llegar a f'''(x). f'''(x) se usa en la cota del error, porque mide qué tanto se " +
              'aleja la función de una parábola.'
          : "Para qué se necesitan: f'(x) es la derivada exacta; el sistema la usa sólo para comparar y calcular el error real " +
              "(el método no la necesita para aproximar). f''(x) mide qué tan curva es la función y se usa para la cota del " +
              'error: mientras más curva, más se separa la recta secante de la tangente.'
    )
    y = write(y, 'Primera derivada, término a término:')
    y = tools.derivation(y, fn.derivative.steps, `f'(x) = ${fn.derivative.latex}`)
    const ordinals = { 2: 'Segunda', 3: 'Tercera', 4: 'Cuarta', 5: 'Quinta' }
    const latexNames = { 2: "f''", 3: "f'''", 4: 'f^{(4)}', 5: 'f^{(5)}' }
    for (const [n, d] of Object.entries(fn.higher_derivatives)) {
      const from = Number(n) <= 4 ? `f${"'".repeat(n - 1)}` : derivativeText(n - 1)
      y = write(y, `${ordinals[n]} derivada: se deriva ${from}(x) con el mismo desglose:`)
      y = tools.derivation(y, namedSteps(Number(n), d.steps), `${latexNames[n]}(x) = ${d.latex}`)
    }
    if (result.derivative_pattern) {
      y = write(y, 'Patrón: cada derivada es la anterior más el mismo término, así que el número que lo acompaña sube de 1 en 1:')
      y = tools.writeMath(y, result.derivative_pattern.latex)
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
  if (result.comparison?.length) y = write(y, fivePoint ? FIVE_POINT_COMPARISON_LEGEND : COMPARISON_LEGEND)
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
      // Con la de 5 puntos (4 fórmulas) llegan a 18.
      styles: { ...TABLE.styles, fontSize: head.length > 15 ? 5.5 : head.length > 11 ? 6.5 : TABLE.styles.fontSize },
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
    if (recommended) y = write(y, UNIFORM_NOTE)
    y = tools.glossary(y, '¿Qué significa cada columna?', tableColumns(result.formulas, Boolean(fn), recommended))
    if (fivePoint) {
      y = tools.label(y + 2, 'Por qué se recomendó cada fórmula')
      for (const step of result.iterations) y = write(y, `- ${recommendedText(result, step.iteration)}`)
    }
    y = explainedGlossaries(y)
    y = sectionTitle(doc, y + 2, 'Paso a paso explicado')
    const n = result.iterations.length
    for (const f of result.formulas) {
      const points = result.iterations.filter((s) => s.extra[f.key]).map((s) => s.iteration)
      const chosen = [...new Set([points[0], points[1], points.at(-1)])].filter(Boolean)
      for (const i of chosen) {
        if (i === points.at(-1) && points.length > 3) y = write(y, 'El resto de los puntos sigue el mismo procedimiento.')
        y = tools.label(y + 2, `${f.name} en x${i} (punto ${i} de ${n})`)
        y = tools.steps(y, safeSteps(explainSteps(result, f, result.iterations[i - 1].extra[f.key], tableContext(result, f, i))))
      }
    }
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
    const ratio = formatNumber(result.formulas[0].expected_ratio) + (fivePoint ? ' (1/16)' : '')
    y = tools.glossary(y + 1, '¿Qué significa cada columna?', refinementColumns(result.differentiable, ratio))
    y = explainedGlossaries(y)
    const all = result.iterations
    const chosen = [...new Set([0, 1, all.length - 1])].filter((i) => i < all.length)
    y = sectionTitle(doc, y + 2, 'Paso a paso explicado')
    for (const f of result.formulas) {
      for (const i of chosen) {
        if (i === all.length - 1 && i > 2) y = write(y, 'El resto de las filas sigue el mismo procedimiento.')
        const k = all[i].iteration
        y = tools.label(y + 2, `${f.name}: fila ${k} (h = ${stepText(all[i].extra.h)})`)
        const steps = explainSteps(result, f, all[i].extra[f.key], functionContext(result, k), i > 0 ? all[i - 1].extra[f.key] : null)
        y = tools.steps(y, safeSteps(steps))
      }
    }
  }

  // --- Comprobación --------------------------------------------------------------
  const check = result.verification
  y = sectionTitle(doc, y + 2, 'Comprobación')
  if (!isTable && result.differentiable) {
    y = write(
      y,
      "La comprobación calcula la derivada exacta en x0 por otro camino (sustituyendo en f'(x)) y la compara con la aproximación."
    )
  }
  if (check.identities && fivePoint) {
    if (check.identities.some((group) => (group.items ?? [group]).length)) {
      y = write(
        y,
        `Identidad de Richardson (${isTable ? 'en cada punto donde aplica el punto medio de 5 puntos, con los datos' : 'en la fila 1'}): ` +
          `${RICHARDSON_TEXT} D5(h) = (4D3(h) - D3(2h))/3, con ` +
          `${isTable ? 'D3(h) = (yi+1 - yi-1)/(2h) y D3(2h) = (yi+2 - yi-2)/(4h)' : 'D3(h) = [f(x0 + h) - f(x0 - h)]/(2h)'}.`
      )
    }
  } else if (check.identities) {
    y = write(
      y,
      `Las identidades comprueban el resultado por otro camino (${isTable ? 'en cada punto, con los datos' : 'en la fila 1, con los valores sin redondear'}):`
    )
    for (const t of Object.values(IDENTITY_TEXTS)) y = write(y, `- ${t}`)
  }
  if (check.identities) {
    const groups = isTable ? check.identities : [{ i: null, items: check.identities }]
    for (const group of groups) {
      for (const item of group.items) {
        y = write(y, `${group.i === null ? '' : `x${group.i} = ${group.x_display.text}: `}${item.name}: ${identityText(item)}`)
      }
    }
    const groupsWithItems = isTable ? check.identities : [{ items: check.identities }]
    if (groupsWithItems.some((g) => g.items.some((item) => item.rounding_difference))) y = write(y, RICHARDSON_ROUNDING_NOTE)
    y += 2
  }
  if (fivePoint) y = write(y, ENDPOINTS_NOTE) + 2
  if (isTable && check.secant) {
    y = write(
      y,
      'Secante común: la progresiva en xi y la regresiva en xi+1 usan la misma recta (la que une los dos puntos), por eso deben dar lo mismo.'
    )
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
    for (const f of result.formulas) {
      const tiny = tinyRealErrorNote(check.final[f.key])
      if (tiny) y = write(y, `${f.name}: ${tiny}`)
    }
    y = tools.glossary(y, '¿Qué significa cada columna?', comparisonColumns(!differences))
    for (const f of result.formulas) {
      const conclusion = conclusionText(result, f)
      if (conclusion) y = write(y + 1, conclusion)
    }
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

  // Glosarios de las fórmulas y de los errores.
  function explainedGlossaries(y) {
    y = sectionTitle(doc, y + 2, 'Glosario de las fórmulas')
    for (const f of result.formulas) {
      y = write(y + 1, `${f.name}: ${f.formula_text}`)
      const g = formulaGlossary(f.key)
      y = tools.glossary(y, '¿Qué significa cada símbolo?', g.items, g.summary)
    }
    if (fn) {
      const [latex, glossary] = fivePoint
        ? [FIVE_POINT_ERRORS_LATEX, FIVE_POINT_ERRORS_GLOSSARY]
        : threePoint
          ? [THREE_POINT_ERRORS_LATEX, THREE_POINT_ERRORS_GLOSSARY]
          : [ERRORS_LATEX, ERRORS_GLOSSARY]
      y = tools.writeMath(y + 1, latex)
      y = tools.glossary(y, '¿Qué significa cada símbolo?', glossary.items)
    }
    return y
  }

  const stem = `${STEMS[result.method] ?? result.method}-${isTable ? 'tabla' : 'funcion'}`
  doc.save(`${stem}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
