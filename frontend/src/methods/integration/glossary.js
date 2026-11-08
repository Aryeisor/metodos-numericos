// Glosarios del método del trapecio: qué significa cada símbolo de las tres
// fórmulas y cada columna de las tablas. Los usan la vista (GlossaryBlock e
// InfoTip) y el PDF. `symbol` es LaTeX; `text`, una línea en palabras.
// Simpson, Romberg y Gauss pueden reutilizar las entradas comunes.

export const COMPOSITE_GLOSSARY = {
  items: [
    { symbol: 'I', text: 'El valor de la integral, es decir, el área bajo la curva entre a y b.' },
    { symbol: '\\approx', text: '«Aproximadamente igual»: el trapecio da una aproximación, no el valor exacto.' },
    { symbol: 'a,\\ b', text: 'Los límites de integración (dónde empieza y dónde termina el área).' },
    { symbol: 'n', text: 'El número de trapecios (segmentos) en que se divide [a, b].' },
    { symbol: 'h', text: 'El ancho de cada trapecio: h = (b − a)/n.' },
    { symbol: 'x_i', text: 'Los puntos de división, xᵢ = a + i·h, con i = 0, 1, …, n. x₀ = a y xₙ = b.' },
    { symbol: 'f(x_i)', text: 'La altura de la curva en el punto xᵢ (la función evaluada ahí).' },
    {
      symbol: '\\sum',
      text: '«Suma de». Σᵢ₌₁ⁿ⁻¹ f(xᵢ) es la suma de las alturas de los puntos interiores (sin los extremos).',
    },
    {
      symbol: '2',
      text: 'Los puntos interiores se cuentan dos veces: cada uno es el lado derecho de un trapecio y el lado izquierdo del siguiente.',
    },
    { symbol: '\\tfrac{h}{2}', text: 'El área de un trapecio es ancho × (altura izquierda + altura derecha)/2.' },
  ],
  summary: 'En resumen: se suman las áreas de los n trapecios.',
}

export const APPROX_GLOSSARY = {
  items: [
    {
      symbol: 'E_a',
      text: 'Una estimación del error que se puede calcular sin conocer la integral exacta (es la fórmula de Chapra).',
    },
    { symbol: "\\bar{f''}", text: "El promedio de la segunda derivada en [a, b]: f̄'' = [f'(b) − f'(a)]/(b − a)." },
    {
      symbol: '-',
      text: "El signo menos: si la curva es convexa (f'' > 0), el trapecio queda por encima de la curva, así que el error I − T es negativo.",
    },
    { symbol: '12', text: 'Sale de integrar el error de reemplazar la curva por una recta. Se explica en la Teoría.' },
  ],
}

export const BOUND_GLOSSARY = {
  items: [
    { symbol: '|E_t|', text: 'El tamaño del error verdadero, sin signo.' },
    { symbol: '\\le', text: '«Menor o igual que». La cota es el peor caso: el error nunca puede ser mayor.' },
    { symbol: 'M_2', text: "El valor más grande de |f''(x)| en [a, b], es decir, la máxima curvatura." },
    {
      symbol: 'h^{2}',
      text: 'Si se duplica n, h se reduce a la mitad y h² se divide entre 4. Por eso el error se divide entre unas 4 veces en cada fila.',
    },
  ],
}

const REFERENCE = ' (aquí respecto al valor de referencia, que no es exacto)'

// Palabras que cambian de una regla a otra en las leyendas de las tablas.
const TRAPEZOID_WORDS = {
  value: 'T',
  units: 'trapecios',
  unit: 'trapecio',
  area: 'los trapecios',
  subject: 'el trapecio',
  derivative: "f''",
  ratio: '0.25',
  divisor: '4',
}

/** Palabras de Simpson para la regla `rule` («simpson13» o «simpson38»). */
export const simpsonWords = (rule) => ({
  value: 'S',
  units: 'segmentos',
  unit: 'segmento',
  area: rule === 'simpson38' ? 'las cúbicas' : 'las parábolas',
  subject: 'Simpson',
  derivative: 'f⁽⁴⁾',
  ratio: '0.0625',
  divisor: '16',
})

/** Columnas de la tabla de refinamiento (las que se muestran). */
export function refinementColumns({ showTrue, showApprox, reference, words = TRAPEZOID_WORDS }) {
  const about = reference ? REFERENCE : ''
  const w = words
  const V = w.value
  const columns = [
    { key: 'k', label: 'k', symbol: 'k', text: 'Número de la fila de refinamiento.' },
    { key: 'n', label: 'n', symbol: 'n', text: `Cuántos ${w.units} se usaron en esa fila; se duplica en cada fila.` },
    { key: 'h', label: 'h', symbol: 'h', text: `Ancho de cada ${w.unit}, (b − a)/n.` },
    { key: V, label: V, symbol: V, text: `El área calculada con ${w.area} (la aproximación de la integral).` },
    {
      key: 'estimated',
      label: 'Error estimado',
      symbol: '\\text{Error estimado}',
      text:
        `Cuánto cambió ${V} respecto a la fila anterior, |${V}_k − ${V}_(k−1)|. Decide cuándo parar: cuando ya casi no cambia ` +
        '(es menor que la tolerancia), se considera que se llegó a la precisión pedida.',
    },
  ]
  if (showTrue) {
    columns.push(
      {
        key: 'true',
        label: 'Eₜ',
        symbol: 'E_t',
        text:
          `Error verdadero, I − ${V}${about}. Positivo si ${w.subject} se quedó corto (subestima); negativo si se pasó ` +
          '(sobreestima). Sólo se puede calcular porque el sistema conoce la integral.',
      },
      {
        key: 'relative',
        label: 'εₜ',
        symbol: '\\varepsilon_t',
        text: `El error verdadero en porcentaje del valor ${reference ? 'de referencia' : 'exacto'}, |Eₜ|/|I|·100.`,
      }
    )
  }
  if (showApprox) {
    columns.push({
      key: 'approx',
      label: 'Eₐ',
      symbol: 'E_a',
      text: `El error estimado con la fórmula de Chapra (con el promedio de ${w.derivative}).`,
    })
  }
  columns.push({ key: 'bound', label: 'Cota', symbol: '\\text{Cota}', text: 'El error máximo posible según la teoría.' })
  if (showTrue) {
    columns.push(
      {
        key: 'ratio',
        label: 'Razón',
        symbol: '\\text{Razón}',
        text: `El error de esta fila dividido entre el de la anterior. Debe acercarse a ${w.ratio}: al duplicar n el error se divide entre ${w.divisor}.`,
      },
      {
        key: 'within',
        label: '≤ cota',
        symbol: '\\le \\text{cota}',
        text: '✔ si el error verdadero quedó por debajo de la cota, como predice la teoría.',
      }
    )
  }
  return columns
}

/** Columnas de la tabla de segmentos (modo tabla). */
export function segmentColumns(hasBound) {
  const columns = [
    { key: 'i', label: 'i', symbol: 'i', text: 'Número del segmento (del trapecio).' },
    { key: 'interval', label: '[xᵢ, xᵢ₊₁]', symbol: '[x_i,\\ x_{i+1}]', text: 'Dónde empieza y dónde termina el segmento.' },
    { key: 'h', label: 'hᵢ', symbol: 'h_i', text: 'Ancho del segmento, hᵢ = xᵢ₊₁ − xᵢ (puede cambiar de un segmento a otro).' },
    { key: 'y0', label: 'yᵢ', symbol: 'y_i', text: 'Altura izquierda del trapecio (el dato en xᵢ).' },
    { key: 'y1', label: 'yᵢ₊₁', symbol: 'y_{i+1}', text: 'Altura derecha del trapecio (el dato en xᵢ₊₁).' },
    { key: 'area', label: 'Área', symbol: '\\text{Área}', text: 'Área de este trapecio: hᵢ·(yᵢ + yᵢ₊₁)/2.' },
    { key: 'cumulative', label: 'Acumulada', symbol: '\\text{Acumulada}', text: 'Suma de las áreas desde el primer segmento hasta este.' },
  ]
  if (hasBound) {
    columns.push({
      key: 'bound',
      label: 'Cota hᵢ³/12·M',
      symbol: '\\text{Cota}',
      text: "Error máximo de este trapecio según la teoría; M es el máximo de |f''(x)| en el segmento.",
    })
  }
  return columns
}

/** Columnas de la tabla de comparación de la comprobación. */
export function comparisonColumns({ reference, isTable, words = TRAPEZOID_WORDS }) {
  const V = words.value
  let valueText = isTable ? 'La suma de las áreas de los trapecios.' : 'Resultado del trapecio en la última fila.'
  if (V !== 'T') valueText = isTable ? 'Resultado de Simpson con los datos.' : 'Resultado de Simpson en la última fila.'
  return [
    { key: V, label: V, symbol: V, text: valueText },
    {
      key: 'I',
      label: 'I',
      symbol: 'I',
      text: reference ? 'Valor de referencia: la integral calculada numéricamente con 30 dígitos.' : 'Valor exacto, calculado con la antiderivada.',
    },
    { key: 'true', label: `Eₜ = I − ${V}`, symbol: `E_t = I - ${V}`, text: `Error verdadero${reference ? REFERENCE : ''}.` },
    { key: 'relative', label: 'εₜ', symbol: '\\varepsilon_t', text: 'El error en porcentaje del valor de I.' },
    { key: 'bound', label: 'Cota', symbol: '\\text{Cota}', text: 'Error máximo teórico.' },
    { key: 'within', label: '|Eₜ| ≤ cota', symbol: '|E_t| \\le \\text{cota}', text: '✔ si se cumple la teoría.' },
  ]
}
