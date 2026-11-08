// Glosarios de la integración de Romberg: símbolos de las fórmulas, cómo se lee
// la tabla triangular y qué significa cada columna de las tablas. Los usan la
// vista (GlossaryBlock e InfoTip) y el PDF. `symbol` es LaTeX; `text`, una
// línea en palabras.

export const RECURRENCE_GLOSSARY = {
  items: [
    { symbol: 'R_{i,1}', text: 'El trapecio de la fila i, con n = 2^(i−1) segmentos (1, 2, 4, 8, …).' },
    { symbol: 'h_i', text: 'El ancho de cada segmento en la fila i: (b − a)/n. Se reduce a la mitad en cada fila.' },
    {
      symbol: '\\tfrac{R_{i-1,1}}{2}',
      text: 'El trapecio de la fila anterior a la mitad: aprovecha todos los puntos ya evaluados.',
    },
    {
      symbol: '\\sum_{\\text{nuevos}} f(x_j)',
      text: 'La suma de las alturas en los puntos nuevos: los que quedan en la mitad de cada segmento anterior.',
    },
  ],
  summary: 'En resumen: cada fila duplica los segmentos y sólo evalúa f en los puntos nuevos.',
}

export const RICHARDSON_GLOSSARY = {
  items: [
    { symbol: 'i', text: 'La fila: la fila i usa n = 2^(i−1) segmentos.' },
    { symbol: 'k', text: 'La columna: cada columna elimina un término más del error.' },
    { symbol: 'R_{i,k-1}', text: 'El valor a la izquierda, en la misma fila (el más preciso de los dos).' },
    { symbol: 'R_{i-1,k-1}', text: 'El valor de la fila anterior, en la misma columna que el de la izquierda.' },
    { symbol: '4^{k-1}', text: 'Los factores 4, 16, 64, … (k = 2, 3, 4, …).' },
    {
      symbol: '\\text{Por qué 4, 16, 64}',
      text:
        'Al reducir h a la mitad, h² se divide entre 4, h⁴ entre 16 y h⁶ entre 64. Con esos factores, el término ' +
        'del error que se quiere eliminar se cancela al restar las dos aproximaciones.',
    },
  ],
  summary: 'En resumen: dos aproximaciones con el mismo error dominante se combinan para cancelarlo.',
}

export const TABLE_LEGEND = [
  { symbol: '\\text{Filas}', text: 'Cada fila duplica el número de segmentos (n = 1, 2, 4, 8, …) y reduce h a la mitad.' },
  {
    symbol: '\\text{Columnas}',
    text:
      'Cada columna elimina un término del error: la 1 es el trapecio, O(h²); la 2, Simpson 1/3, O(h⁴); la 3, ' +
      'Boole, O(h⁶), y así sucesivamente.',
  },
  {
    symbol: 'R_{i,i}',
    text: 'El mejor valor de cada fila es el último, en la diagonal (resaltada): es el que tiene el error de orden más alto.',
  },
  {
    symbol: '\\text{Celdas}',
    text: 'Toca o pasa el cursor sobre una celda de la columna 2 en adelante para ver las dos celdas de las que sale.',
  },
]

/** Tooltip del encabezado de la columna k. */
export function columnTip(col) {
  const base =
    col.k === 1
      ? 'Columna 1: la regla del trapecio con n = 2^(i−1) segmentos.'
      : `Columna ${col.k}: combina dos valores de la columna ${col.k - 1} para eliminar su término de error.`
  const name = col.k <= 3 ? ` Coincide con ${col.k === 3 ? 'la regla de Boole' : col.name}.` : ''
  return `${base}${name} Error ${col.order_text}: exacta para polinomios de grado ≤ ${col.degree}.`
}

const REFERENCE = ' (aquí respecto al valor de referencia, que no es exacto)'

/** Columnas de la tabla de convergencia de la diagonal. */
export function convergenceColumns({ showTrue, reference, isTable }) {
  const columns = [
    { key: 'i', label: 'i', symbol: 'i', text: 'La fila de la tabla triangular.' },
    { key: 'n', label: 'n', symbol: 'n', text: 'Los segmentos del trapecio de esa fila: n = 2^(i−1).' },
    {
      key: 'evaluations',
      label: isTable ? 'Datos usados' : 'Evaluaciones',
      symbol: isTable ? '\\text{Datos usados}' : '\\text{Evaluaciones}',
      text: isTable
        ? 'Cuántos datos de la tabla usa la fila: n + 1.'
        : 'Cuántas veces se evaluó f hasta esa fila (acumuladas): n + 1, porque cada fila reutiliza los puntos anteriores.',
    },
    { key: 'trapezoid', label: 'Rᵢ,₁', symbol: 'R_{i,1}', text: 'El trapecio de esa fila (columna 1).' },
    { key: 'best', label: 'Rᵢ,ᵢ', symbol: 'R_{i,i}', text: 'La diagonal: el mejor valor de esa fila.' },
    {
      key: 'estimated',
      label: 'Error estimado',
      symbol: '\\text{Error estimado}',
      text:
        'Cuánto cambió la diagonal respecto a la fila anterior, |Rᵢ,ᵢ − Rᵢ₋₁,ᵢ₋₁|. ' +
        (isTable ? 'En el modo tabla sólo informa: las filas las fija la cantidad de datos.' : 'Decide cuándo parar.'),
    },
    {
      key: 'approx',
      label: 'εₐ',
      symbol: '\\varepsilon_a',
      text: 'El error aproximado de Chapra: el error estimado en porcentaje de Rᵢ,ᵢ. Sólo informa.',
    },
  ]
  if (showTrue) {
    columns.push(
      {
        key: 'true',
        label: 'Eₜ',
        symbol: 'E_t',
        text: `Error verdadero de la diagonal, I − Rᵢ,ᵢ${reference ? REFERENCE : ''}. Sólo se puede calcular porque el sistema conoce la integral.`,
      },
      {
        key: 'relative',
        label: 'εₜ',
        symbol: '\\varepsilon_t',
        text: `El error verdadero en porcentaje del valor ${reference ? 'de referencia' : 'exacto'}, |Eₜ|/|I|·100.`,
      }
    )
  }
  return columns
}

/** Columnas de la tabla de comparación de la comprobación. */
export function rombergComparisonColumns(reference) {
  return [
    { key: 'R', label: 'R', symbol: 'R', text: 'El mejor valor de Romberg: la diagonal de la última fila.' },
    {
      key: 'I',
      label: 'I',
      symbol: 'I',
      text: reference ? 'Valor de referencia: la integral calculada numéricamente con 30 dígitos.' : 'Valor exacto, calculado con la antiderivada.',
    },
    { key: 'true', label: 'Eₜ = I − R', symbol: 'E_t = I - R', text: `Error verdadero${reference ? REFERENCE : ''}.` },
    { key: 'relative', label: 'εₜ', symbol: '\\varepsilon_t', text: 'El error en porcentaje del valor de I.' },
  ]
}

/** Columnas de la tabla de identidades. */
export const IDENTITY_COLUMNS = [
  { symbol: 'i', text: 'La fila; n = 2^(i−1) segmentos.' },
  { symbol: 'R_{i,1}', text: 'La columna 1 de Romberg.' },
  { symbol: 'T(n)', text: 'El trapecio con n segmentos, calculado aparte con la fórmula de pesos (h/2)[f₀ + 2f₁ + … + fₙ].' },
  { symbol: 'R_{i,2}', text: 'La columna 2 de Romberg.' },
  { symbol: 'S(n)', text: 'Simpson 1/3 con n segmentos, calculado aparte con el motor de Simpson (pesos 1, 4, 2, …, 4, 1).' },
  { symbol: '\\checkmark', text: '✔ si la diferencia es ≤ 10⁻¹²·máx(1, |valor|): son el mismo número salvo el redondeo.' },
]
