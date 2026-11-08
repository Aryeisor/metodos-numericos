// PDF del resultado del método de Simpson, siempre en tema claro, con el mismo
// estilo y las mismas utilidades que el del trapecio (pdf.js): datos,
// derivadas paso a paso, resumen y comparación con el trapecio, gráfico de
// parábolas o cúbicas, gráfico de convergencia, glosarios, tablas completas,
// paso a paso explicado de las filas 1, 2 y la última de cada regla, y la
// comprobación con la identidad con el trapecio.
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import { MARGIN, sectionTitle } from '../../utils/exportPdf'
import { formatNumber } from '../../utils/iterationSteps'
import { latexToText } from '../../utils/latexText'
import { tinyErrorNote } from './explain'
import { comparisonColumns, refinementColumns, simpsonWords } from './glossary'
import { TABLE, addImage, mark, num, pct, pdfSafe, pdfTools, shown } from './pdf'
import {
  IDENTITY_SENTENCE,
  NO_IDENTITY_38,
  approxBlocks,
  boundBlocks,
  identityLatex,
  partSumLatex,
  partValueLatex,
  partsTotalLatex,
  pointProduct,
  pointRule,
  pointWeight,
  ruleShort,
  simpsonConclusion,
  simpsonRowSteps,
  trapezoidComparisonText,
  weightReason,
} from './simpsonExplain'
import { SIMPSON_GLOSSARIES, SIMPSON_POINT_COLUMNS, simpsonApproxGlossary, simpsonBoundGlossary } from './simpsonGlossary'

export function exportSimpsonPdf({ result, methodName, chartImage, chartTitle, convergenceImage }) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const isTable = result.mode === 'table'
  const fn = result.function
  const integral = result.integral
  const reference = integral?.kind === 'reference'
  const { write, writeMath, label, derivation, glossary, integralCheck } = pdfTools(doc, result)
  const blocks = (y, list) => {
    for (const block of list) {
      if (block.kind === 'math') y = writeMath(y, block.latex)
      else y = write(y, block.text)
    }
    return y
  }

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
    y = write(y, `Modo: tabla de datos igualmente espaciados (n = ${result.n} segmentos, h = ${shown(result.h)})`)
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
      `Reglas: ${result.rules.map((b) => `${b.rule.name} (n0 = ${b.n0})`).join(', ')}    ·    ` +
        `Tolerancia del error estimado: ${formatNumber(result.tolerance)}    ·    Máximo de refinamientos: ${result.max_iterations}`
    )
  }
  if (fn) {
    y = label(y + 1, 'Derivadas de f(x)')
    y = write(
      y,
      "f'''(x) se usa en el error aproximado de Chapra (el promedio de f⁽⁴⁾); f⁽⁴⁾(x) en la cota del error: mide qué " +
        'tanto se aleja la función de un polinomio de grado 3. f′ y f′′ sólo son pasos intermedios para llegar a f′′′.'
    )
    y = write(y, 'Primera derivada, término a término:')
    y = derivation(y, fn.first.steps, `f'(x) = ${fn.first.latex}`)
    y = write(y, "Segunda derivada: se deriva f'(x):")
    y = derivation(y, fn.second.steps, `f''(x) = ${fn.second.latex}`)
    y = write(y, "Tercera derivada: se deriva f''(x):")
    y = derivation(y, fn.third.steps, `f'''(x) = ${fn.third.latex}`)
    y = write(y, "Cuarta derivada: se deriva f'''(x):")
    y = derivation(y, fn.fourth.steps, `f^{(4)}(x) = ${fn.fourth.latex}`)
    if (fn.uses_trigonometry) y = write(y, 'Las funciones trigonométricas se evalúan en radianes.')
  }

  // --- Resultado ----------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Resultado')
  if (isTable) {
    for (const app of result.applications) {
      const errors = app.final ? `    ·    Et = ${num(app.final.true_error)}    ·    et = ${pct(app.final.relative_error)}` : ''
      y = write(y, `${app.name}: I ~ S = ${num(app.total)}${errors}`)
    }
  } else {
    y = write(
      y,
      `Estado: ${result.converged ? 'ALCANZÓ LA TOLERANCIA' : 'NO ALCANZÓ LA TOLERANCIA'}    ·    Filas usadas: ${result.iterations_used}`
    )
    for (const b of result.rules) {
      const last = b.rows.at(-1)
      const errors = last.true_error === null ? '' : `    ·    Et = ${num(last.true_error)}    ·    et = ${pct(last.relative_error)}`
      y = write(y, `${b.rule.name}: I ~ S = ${num(last.S)} (n = ${last.n})${errors}`)
    }
  }
  if (integral && integral.value !== null) y = write(y, `I = ${num(integral.value)} (${integral.label})`)
  if (!isTable) {
    y = label(y + 1, 'Comparación con el trapecio (mismo n)')
    for (const b of result.rules) {
      const rows = b.rows.length > 1 ? [b.rows[0], b.rows.at(-1)] : [b.rows[0]]
      for (const row of rows) y = write(y, `- ${trapezoidComparisonText(b.rule, row)}`)
    }
  }
  for (const note of result.notes ?? []) y = write(y, `Nota: ${note}`)
  for (const warning of result.warnings ?? []) y = write(y, `Advertencia: ${warning}`)

  // --- Gráficos ----------------------------------------------------------------
  y = addImage(doc, y, pdfSafe(chartTitle ?? 'Gráfico'), chartImage)
  y = addImage(doc, y, 'Convergencia del error (escala logarítmica)', convergenceImage)

  // --- Tablas, glosarios y paso a paso -------------------------------------------------
  if (isTable) {
    for (const app of result.applications) {
      y = sectionTitle(doc, y + 2, `${app.name}: tabla de puntos`)
      autoTable(doc, {
        ...TABLE,
        startY: y,
        head: [SIMPSON_POINT_COLUMNS.map((c) => pdfSafe(c.label))],
        body: app.points.map((p) => [p.i, shown(p.x_display), shown(p.y_display), pointWeight(p), pointProduct(p), pointRule(p)]),
      })
      y = doc.lastAutoTable.finalY + 4
      const junction = app.points.find((p) => p.weights.length > 1)
      if (junction) {
        y = write(
          y,
          `El punto ${junction.i} es el final de la parte 1/3 y el inicio de la parte 3/8: entra en las dos sumas con ` +
            'peso 1 en cada una (1 + 1); cada suma se multiplica por el factor de su regla.'
        )
      }
      y = glossary(y, '¿Qué significa cada columna?', SIMPSON_POINT_COLUMNS)
      for (const part of app.parts) {
        y = label(y + 1, app.key === 'combined' ? `Parte ${ruleShort(part.rule)} (segmentos ${part.start + 1} a ${part.end})` : `Simpson ${ruleShort(part.rule)}`)
        y = writeMath(y, partSumLatex(part, app.points))
        y = writeMath(y, partValueLatex(part, result.h))
        if (fn && app.final) {
          const width = part.width_display.latex
          if (part.approx_error !== null && part.mean_fourth) {
            y = blocks(y, approxBlocks(fn, part.mean_fourth, width, result.h, part.coefficient_numerator, part.divisor, part.approx_error))
          }
          if (part.bound !== null && part.M4) {
            y = blocks(y, boundBlocks(fn, part.M4, result.sampling_points, width, result.h, part.coefficient_numerator, part.divisor, part.bound))
          }
        }
      }
      if (app.key === 'combined') y = writeMath(y, partsTotalLatex(app))
    }
  } else {
    const showTrue = integral.value !== null
    const showApprox = Boolean(result.mean_fourth)
    for (const b of result.rules) {
      const rule = b.rule
      const tools = pdfTools(doc, result, { weightReason: (i, n) => weightReason(rule, i, n) })
      y = sectionTitle(doc, y + 2, `${rule.name}: tabla de refinamiento`)
      const head = ['k', 'n', 'h', 'S', 'Error estimado']
      if (showTrue) head.push('Et', 'et')
      if (showApprox) head.push('Ea')
      head.push('Cota')
      if (showTrue) head.push('Razón', '<= cota')
      autoTable(doc, {
        ...TABLE,
        startY: y,
        head: [head],
        body: b.rows.map((e) => {
          const row = [e.k, e.n, e.h.exact ? e.h.text : `${e.h.text} ~ ${e.h.approx}`, num(e.S), num(e.estimated_error)]
          if (showTrue) row.push(num(e.true_error), pct(e.relative_error))
          if (showApprox) row.push(num(e.approx_error))
          row.push(e.bound === null ? 'no disp.' : num(e.bound))
          if (showTrue) row.push(num(e.ratio), mark(e))
          return row
        }),
      })
      y = doc.lastAutoTable.finalY + 4
      const tinyRows = b.rows.filter((r) => tinyErrorNote(r, reference))
      if (tinyRows.length) y = write(y, `Filas ${tinyRows.map((r) => r.k).join(', ')}: ${tinyErrorNote(tinyRows[0], reference)}`)
      if (b.rows.some((r) => r.by_rounding)) {
        y = write(y, '"OK (R)": |Et| supera la cota (más de 10^-9 relativo) y se cumple sólo con el margen de redondeo R.')
      }

      y = label(y + 2, 'Glosario de las fórmulas y de las columnas')
      y = write(y, `Regla compuesta: ${latexToText(rule.formula_latex)}`)
      y = glossary(y, '¿Qué significa cada símbolo?', SIMPSON_GLOSSARIES[rule.key].items, SIMPSON_GLOSSARIES[rule.key].summary)
      y = write(y + 1, `Error de la regla: ${latexToText(rule.simple_error_latex)};  ${latexToText(rule.error_latex)}`)
      if (showApprox) {
        y = write(y + 1, `Error aproximado: ${latexToText(rule.approx_latex)}`)
        y = glossary(y, '¿Qué significa cada símbolo?', simpsonApproxGlossary(rule.divisor).items)
      }
      y = write(y + 1, `Cota: ${latexToText(rule.bound_latex)}`)
      y = glossary(y, '¿Qué significa cada símbolo?', simpsonBoundGlossary(rule.divisor).items)
      y = glossary(y + 1, '¿Qué significa cada columna?', refinementColumns({ showTrue, showApprox, reference, words: simpsonWords(rule.key) }))

      // Paso a paso explicado: filas 1, 2 y la última.
      const rows = b.rows
      const chosen = [...new Set([0, 1, rows.length - 1])].filter((i) => i < rows.length)
      y = label(y + 2, `Paso a paso explicado (${rule.name})`)
      for (const i of chosen) {
        if (i === rows.length - 1 && i > 2) y = write(y, 'El resto de las filas sigue el mismo procedimiento.')
        const row = rows[i]
        y = label(y + 2, `Fila ${row.k} (n = ${row.n})`)
        y = tools.steps(y, simpsonRowSteps(result, rule, row, row.k, i > 0 ? rows[i - 1] : null), row)
      }
    }
  }

  // --- Comprobación --------------------------------------------------------------
  y = sectionTitle(doc, y + 2, 'Comprobación')
  if (isTable && result.verification.data) {
    y = write(y, 'Datos contra la función: |yi - f(xi)| <= 10^-6 · máx(1, |f(xi)|).')
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['i', 'yi', 'f(xi)', '|yi - f(xi)|', '']],
      body: result.verification.data.map((row) => [row.i, num(row.y), num(row.f), num(row.difference),
        row.ok ? 'OK' : '(!) el dato no coincide con la función']),
    })
    y = doc.lastAutoTable.finalY + 6
  }
  y = write(
    y,
    'La comprobación calcula la integral por otro camino' + (integral?.kind === 'exact' ? ' (con la antiderivada)' : '') +
      ' y la compara con el resultado de Simpson.'
  )
  y = integralCheck(y)

  const entries = isTable
    ? result.applications.map((app) => ({ name: app.name, n: result.n, final: app.final }))
    : result.rules.map((b) => ({ name: b.rule.name, n: b.rows.at(-1).n, final: { ...b.verification.final, I: integral.value }, verification: b.verification }))
  for (const e of entries) {
    const final = e.final
    if (!final || final.true_error === null || final.true_error === undefined) continue
    y = label(y + 1, e.name)
    autoTable(doc, {
      ...TABLE,
      theme: 'grid',
      startY: y,
      head: [['S', 'I', 'Et = I - S', 'et', 'Cota', '|Et| <= cota']],
      body: [[num(final.S), num(final.I), num(final.true_error), pct(final.relative_error),
        final.bound === null ? 'no disp.' : num(final.bound), mark(final)]],
    })
    y = doc.lastAutoTable.finalY + 6
    const tiny = tinyErrorNote(final, reference)
    if (tiny) y = write(y, tiny)
    const conclusion = simpsonConclusion(result, e.name, e.n, final)
    if (conclusion) y = write(y, conclusion)
    if (e.verification && result.M4) {
      y = e.verification.all_within
        ? write(y, `En todas las filas de ${e.name} |Et| quedó por debajo de la cota teórica OK`)
        : write(y, `(!) ${e.name}: |Et| supera la cota en las filas ${e.verification.failed_rows.join(', ')}.`)
    }
  }
  if (entries.some((e) => e.final && e.final.true_error !== null && e.final.true_error !== undefined)) {
    y = glossary(y, '¿Qué significa cada columna?', comparisonColumns({ reference, isTable, words: simpsonWords('simpson13') }))
  }

  // Identidad con el trapecio.
  const identities = isTable
    ? result.applications.filter((a) => a.identity).map((a) => ({ k: null, identity: a.identity }))
    : result.rules
        .filter((b) => b.rule.key === 'simpson13')
        .flatMap((b) => (b.rows.length > 1 ? [b.rows[0], b.rows.at(-1)] : [b.rows[0]]).map((r) => ({ k: r.k, identity: r.identity })))
  const has38 = isTable ? result.applications.some((a) => a.key !== 'simpson13') : result.rules.some((b) => b.rule.key === 'simpson38')
  if (identities.length || has38) {
    y = label(y + 2, 'Identidad con el trapecio')
    if (identities.length) {
      y = write(y, IDENTITY_SENTENCE)
      y = writeMath(y, 'S_{n} = \\frac{4\\,T_{n} - T_{n/2}}{3}')
      for (const { k, identity } of identities) {
        y = write(y, `${k ? `Fila ${k}: ` : ''}T${identity.n} = ${identity.T_n_display}, T${identity.n / 2} = ${identity.T_half_display}`)
        y = writeMath(y, `${identityLatex(identity)} \\text{ ${identity.ok ? 'OK' : '(!)'}}`)
      }
    }
    if (has38) y = write(y, NO_IDENTITY_38)
  }

  doc.save(`simpson-${isTable ? 'tabla' : 'funcion'}-${new Date().toISOString().slice(0, 10)}.pdf`)
}
