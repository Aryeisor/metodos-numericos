// Glosarios del método de Simpson (reglas 1/3 y 3/8): qué significa cada
// símbolo de la regla compuesta, del Eₐ de Chapra y de la cota, y cada columna
// de la tabla de puntos del modo tabla. Reutiliza las entradas comunes del
// trapecio (glossary.js). `symbol` es LaTeX; `text`, una línea en palabras.
import { APPROX_GLOSSARY, BOUND_GLOSSARY, COMPOSITE_GLOSSARY } from './glossary'

const common = (symbol) => COMPOSITE_GLOSSARY.items.find((item) => item.symbol === symbol)
const APPROX = { symbol: '\\approx', text: '«Aproximadamente igual»: Simpson da una aproximación, no el valor exacto.' }
const WIDTH = { symbol: 'h', text: 'El ancho de cada segmento: h = (b − a)/n.' }

export const SIMPSON_GLOSSARIES = {
  simpson13: {
    items: [
      common('I'),
      APPROX,
      common('a,\\ b'),
      { symbol: 'n', text: 'El número de segmentos; debe ser par porque cada parábola ocupa 2 segmentos.' },
      WIDTH,
      common('x_i'),
      common('f(x_i)'),
      { symbol: '1,\\ 4,\\ 1', text: 'Cada parábola usa 3 puntos seguidos y les da pesos 1, 4, 1.' },
      { symbol: '4', text: 'El punto del medio pesa 4 porque representa mejor a todo el tramo.' },
      { symbol: '2', text: 'Donde dos parábolas se tocan, el punto se cuenta en las dos: 1 + 1 = 2.' },
      {
        symbol: '\\tfrac{h}{3}',
        text: 'Es el área exacta bajo una parábola que pasa por 3 puntos separados h: (h/3)·(f₀ + 4f₁ + f₂). El detalle va en la Teoría.',
      },
    ],
    summary: 'En resumen: se suman las áreas bajo las n/2 parábolas.',
  },
  simpson38: {
    items: [
      common('I'),
      APPROX,
      common('a,\\ b'),
      { symbol: 'n', text: 'El número de segmentos; debe ser múltiplo de 3 porque cada cúbica ocupa 3 segmentos.' },
      WIDTH,
      common('x_i'),
      common('f(x_i)'),
      { symbol: '1,\\ 3,\\ 3,\\ 1', text: 'Cada cúbica (curva de grado 3) usa 4 puntos seguidos y les da pesos 1, 3, 3, 1.' },
      { symbol: '3', text: 'Los dos puntos del medio pesan 3 porque representan mejor a todo el tramo.' },
      { symbol: '2', text: 'Donde dos cúbicas se tocan, el punto se cuenta en las dos: 1 + 1 = 2.' },
      {
        symbol: '\\tfrac{3h}{8}',
        text: 'Es el área exacta bajo una cúbica que pasa por 4 puntos separados h: (3h/8)·(f₀ + 3f₁ + 3f₂ + f₃). El detalle va en la Teoría.',
      },
    ],
    summary: 'En resumen: se suman las áreas bajo las n/3 cúbicas.',
  },
}

const divisorItem = (divisor) => ({
  symbol: String(divisor),
  text: `Sale de integrar el error de reemplazar la curva por ${divisor === 180 ? 'parábolas' : 'cúbicas'}. Se explica en la Teoría.`,
})

/** Glosario del Eₐ de Chapra con el divisor de la regla (180 o 80). */
export const simpsonApproxGlossary = (divisor) => ({
  items: [
    APPROX_GLOSSARY.items[0],
    { symbol: '\\bar{f}^{(4)}', text: "El promedio de la cuarta derivada en [a, b]: f̄⁽⁴⁾ = [f'''(b) − f'''(a)]/(b − a)." },
    {
      symbol: '-',
      text: 'El signo menos: si f⁽⁴⁾ > 0, Simpson se pasa del área verdadera, así que el error I − S es negativo.',
    },
    divisorItem(divisor),
  ],
})

/** Glosario de la cota con el divisor de la regla. */
export const simpsonBoundGlossary = (divisor) => ({
  items: [
    ...BOUND_GLOSSARY.items.slice(0, 2),
    {
      symbol: 'M_4',
      text:
        'El valor más grande de |f⁽⁴⁾(x)| en [a, b]. Mide qué tanto se aleja la función de un polinomio de grado 3 ' +
        '(para esos f⁽⁴⁾ = 0 y Simpson es exacto).',
    },
    {
      symbol: 'h^{4}',
      text: 'Al duplicar n, h se reduce a la mitad y h⁴ se divide entre 16: el error se divide entre unas 16 veces en cada fila.',
    },
    divisorItem(divisor),
  ],
})

/** Columnas de la tabla de puntos del modo tabla. */
export const SIMPSON_POINT_COLUMNS = [
  { key: 'i', label: 'i', symbol: 'i', text: 'Número del punto.' },
  { key: 'x', label: 'xᵢ', symbol: 'x_i', text: 'Dónde está el punto (los datos deben estar igualmente espaciados).' },
  { key: 'y', label: 'yᵢ', symbol: 'y_i', text: 'El dato: la altura de la curva en xᵢ.' },
  {
    key: 'weight',
    label: 'Peso',
    symbol: '\\text{Peso}',
    text: 'Cuántas veces cuenta el dato: 1 en los extremos; 4 y 2 en Simpson 1/3; 3 y 2 en Simpson 3/8.',
  },
  { key: 'product', label: 'Peso × yᵢ', symbol: '\\text{Peso} \\times y_i', text: 'El dato multiplicado por su peso; luego se suman.' },
  { key: 'rule', label: 'Regla', symbol: '\\text{Regla}', text: 'La regla (1/3 o 3/8) a la que pertenece el punto.' },
]
