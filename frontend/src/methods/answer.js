// «La respuesta» de un resultado: lo que el usuario vino a buscar, para la
// tarjeta de respuesta y la franja fija (components/ResultAnswer.vue). Sólo lee
// lo que ya trae la respuesta del backend; no calcula nada.
//
//   Sistemas lineales y no lineales   el vector solución
//   Bairstow                          las raíces
//   Diferenciación (función)          D, una por fórmula
//   Diferenciación (tabla)            la derivada en cada punto
//   Integración                       la integral, una por regla
import { formatNumber } from '../utils/iterationSteps'
import { formatComplex } from './polynomial/formulas'

// Cómo llama cada categoría a sus iteraciones (las tablas de refinamiento
// hablan de «filas»).
const ROW_UNITS = { differentiation: ['fila', 'filas'], integration: ['fila', 'filas'] }
const count = (n, [one, many]) => `${n} ${n === 1 ? one : many}`

// Un error menor que 0.000001 se vería como «0» con formatNumber.
const formatError = (error) =>
  error !== 0 && Math.abs(error) < 1e-6 ? error.toExponential(2) : formatNumber(error)

function answerValues(result) {
  const solution = (label) =>
    result.solution.map((value, i) => ({
      label: label(result.variables?.[i] ?? `x${i + 1}`),
      value: formatNumber(value),
    }))

  switch (result.category) {
    case 'polynomial':
      return {
        noun: 'raíces',
        values: result.roots.map((root, i) => ({ label: `x${i + 1}`, value: formatComplex(root.re, root.im) })),
      }
    case 'differentiation': {
      if (result.mode !== 'table') {
        const names = Object.fromEntries(result.formulas.map((f) => [f.key, f.name]))
        return { noun: 'fórmulas', values: solution((key) => names[key] ?? key) }
      }
      // Tabla de datos: la fórmula recomendada en cada punto si el backend la
      // da; si no, cada fórmula que tenga los vecinos que necesita.
      const values = result.iterations.flatMap(({ extra }) => {
        const at = `f′(${extra.x_display.text})`
        if (extra.recommended) return [{ label: at, value: formatNumber(extra.recommended.D) }]
        return result.formulas
          .filter((f) => extra[f.key])
          .map((f) => ({ label: `${at} · ${f.name}`, value: formatNumber(extra[f.key].D) }))
      })
      return { noun: 'derivadas', values }
    }
    case 'integration':
      // «T», «R» o «G» son símbolos; «Simpson 1/3» ya es un nombre.
      return { noun: 'reglas', values: solution((name) => (name.length === 1 ? `I ≈ ${name}` : name)) }
    default:
      return { noun: 'incógnitas', values: solution((name) => name) }
  }
}

function answerStatus(result) {
  if (result.mode === 'table') return { ok: true, status: 'Calculado directamente con los datos de la tabla.' }
  const used = count(result.iterations_used, ROW_UNITS[result.category] ?? ['iteración', 'iteraciones'])
  const error = result.iterations.at(-1)?.error
  const unit = result.category === 'polynomial' ? ' %' : ''
  const finalError = error === null || error === undefined ? '' : ` Error final: ${formatError(error)}${unit}.`
  return result.converged
    ? { ok: true, status: `Alcanzó la tolerancia en ${used}.${finalError}` }
    : { ok: false, status: `No alcanzó la tolerancia: se detuvo tras ${used}.${finalError}` }
}

/** { values: [{ label, value }], noun, ok, status } */
export function resultAnswer(result) {
  return { ...answerValues(result), ...answerStatus(result) }
}
