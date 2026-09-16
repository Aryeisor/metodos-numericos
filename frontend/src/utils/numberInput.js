// Parseo de los campos del sistema (A, b, x0), que aceptan tanto un decimal
// como una fracción ("6/7").
//
// Precisión: la división se evalúa en punto flotante de doble precisión y el
// valor se guarda tal cual, sin redondear. El redondeo a 6 decimales es
// exclusivamente de presentación (ver `formatNumber`), nunca del dato que se
// envía al backend.

const FRACTION_PATTERN = /^([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))\s*\/\s*([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))$/

export const INPUT_ERRORS = {
  ZERO_DENOMINATOR: 'zero-denominator',
  NOT_A_NUMBER: 'not-a-number',
}

export const INPUT_ERROR_MESSAGES = {
  [INPUT_ERRORS.ZERO_DENOMINATOR]: 'El denominador de una fracción no puede ser cero.',
  [INPUT_ERRORS.NOT_A_NUMBER]: 'Escribe un número (2.5) o una fracción (6/7).',
}

// Se admite la coma como separador decimal: es lo que muestra el navegador en
// español en los demás campos numéricos.
function toDecimal(text) {
  return Number(text.replace(',', '.'))
}

/**
 * Convierte el texto de un campo en su valor numérico.
 * Devuelve { value, error }: `value` es NaN cuando hay error, y un campo vacío
 * equivale a 0 (mismo comportamiento que antes).
 */
export function parseNumericInput(text) {
  const raw = String(text ?? '').trim()
  if (raw === '') return { value: 0, error: null }

  const fraction = raw.match(FRACTION_PATTERN)
  if (fraction) {
    const denominator = toDecimal(fraction[2])
    if (denominator === 0) {
      return { value: NaN, error: INPUT_ERRORS.ZERO_DENOMINATOR }
    }
    // Sin redondeo: se conserva toda la precisión de doble precisión.
    return { value: toDecimal(fraction[1]) / denominator, error: null }
  }

  const value = toDecimal(raw)
  if (!Number.isFinite(value)) {
    return { value: NaN, error: INPUT_ERRORS.NOT_A_NUMBER }
  }
  return { value, error: null }
}

export function isFractionInput(text) {
  return FRACTION_PATTERN.test(String(text ?? '').trim())
}
