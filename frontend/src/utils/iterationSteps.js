// Reconstruye, en el frontend, el paso a paso de cada iteración a partir de los
// datos que ya devuelve la API (historial de iteraciones) y del sistema que se
// envió (A, b, x0). El backend no necesita calcular ni enviar nada extra.

export const MAX_DECIMALS = 6

// A partir de esta magnitud se usa notación científica, para que los casos de
// divergencia (valores de 10^40 o más) no rompan el layout de la tabla.
const SCIENTIFIC_THRESHOLD = 1e7

export function formatNumber(value) {
  if (value === null || value === undefined) return '—'
  if (!Number.isFinite(value)) return '∞'
  if (value === 0) return '0'

  if (Math.abs(value) >= SCIENTIFIC_THRESHOLD) {
    return value.toExponential(2)
  }

  return value
    .toFixed(MAX_DECIMALS)
    .replace(/0+$/, '')
    .replace(/\.$/, '')
}

export function generalFormula(method) {
  return method === 'gauss-seidel'
    ? 'xᵢ⁽ᵏ⁺¹⁾ = ( bᵢ − Σ_{j<i} aᵢⱼ · xⱼ⁽ᵏ⁺¹⁾ − Σ_{j>i} aᵢⱼ · xⱼ⁽ᵏ⁾ ) / aᵢᵢ'
    : 'xᵢ⁽ᵏ⁺¹⁾ = ( bᵢ − Σ_{j≠i} aᵢⱼ · xⱼ⁽ᵏ⁾ ) / aᵢᵢ'
}

/**
 * Devuelve el vector de x que sirvió de base para la iteración `index`
 * (0-based): la iteración 1 parte de x0, y la iteración k de la anterior.
 */
export function baseVectorFor(iterations, index, x0) {
  return index === 0 ? x0 : iterations[index - 1].x
}

/**
 * Construye el detalle completo de una iteración: la sustitución numérica de
 * cada variable y el cálculo del error.
 */
export function buildIterationDetail({ A, b, x0, method, iterations, index }) {
  const current = iterations[index]
  const previousX = baseVectorFor(iterations, index, x0)
  const currentX = current.x
  const n = currentX.length
  const isGaussSeidel = method === 'gauss-seidel'

  const variables = []
  for (let i = 0; i < n; i++) {
    const terms = []
    for (let j = 0; j < n; j++) {
      if (j === i) continue
      // En Gauss-Seidel las variables ya recalculadas en esta misma iteración
      // (j < i) usan el valor nuevo; el resto usa el de la iteración anterior.
      const fromCurrent = isGaussSeidel && j < i
      terms.push({
        j,
        coefficient: A[i][j],
        value: fromCurrent ? currentX[j] : previousX[j],
        fromCurrent,
      })
    }

    variables.push({
      index: i,
      independent: b[i],
      diagonal: A[i][i],
      terms,
      result: currentX[i],
    })
  }

  const diffs = currentX.map((value, i) => ({
    index: i,
    current: value,
    previous: previousX[i],
    diff: Math.abs(value - previousX[i]),
  }))

  let maxIndex = 0
  for (let i = 1; i < diffs.length; i++) {
    if (diffs[i].diff > diffs[maxIndex].diff) maxIndex = i
  }

  return {
    iteration: current.iteration,
    previousX,
    currentX,
    variables,
    error: {
      value: current.error,
      diffs,
      maxIndex,
    },
  }
}

/** Versión en texto plano de la sustitución de una variable (para el PDF). */
export function substitutionToText(variable) {
  const terms = variable.terms
    .map((t) => `- (${formatNumber(t.coefficient)})(${formatNumber(t.value)})`)
    .join(' ')
  return (
    `x${variable.index + 1} = (${formatNumber(variable.independent)} ${terms}) ` +
    `/ ${formatNumber(variable.diagonal)} = ${formatNumber(variable.result)}`
  )
}
