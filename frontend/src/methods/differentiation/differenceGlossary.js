// Glosarios de las diferencias progresiva y regresiva: qué significa cada
// símbolo de las fórmulas y cada columna de las tablas. Los usan la vista
// (GlossaryBlock e InfoTip, los mismos de integración) y el PDF. `symbol` es
// LaTeX; `text`, una línea en palabras. Las fórmulas de 3 y 5 puntos pueden
// agregar sus propias entradas con la misma forma.

const SIDE = {
  forward: { symbol: 'D^{+}(h)', word: 'progresiva', direction: '«hacia adelante»', where: 'a la derecha', node: 'x_0 + h' },
  backward: { symbol: 'D^{-}(h)', word: 'regresiva', direction: '«hacia atrás»', where: 'a la izquierda', node: 'x_0 - h' },
}

// Fórmula de 3 puntos: un glosario por fórmula.
const COEFFICIENTS_TEXT =
  'Coeficientes: salen de derivar la parábola que pasa por los 3 puntos. Suman 0, así que si f es constante la ' +
  'derivada da 0.'
const THREE_POINT_GLOSSARY = {
  punto_medio: {
    items: [
      { symbol: 'D^{\\text{med}}(h)', text: 'La aproximación de la derivada con el punto medio, usando un paso h.' },
      { symbol: 'x_0 - h,\\ x_0 + h', text: 'Un punto a cada lado de x₀, a la misma distancia.' },
      { symbol: 'f(x_0 + h) - f(x_0 - h)', text: 'El numerador: cuánto cambia la función de un lado al otro.' },
      { symbol: '2h', text: 'La distancia total entre los dos puntos.' },
      {
        symbol: 'f(x_0)',
        text: 'Por qué no aparece: la parábola pasa por los 3 puntos, pero en esta fórmula el coeficiente de f(x₀) es 0.',
      },
    ],
    summary:
      'Idea clave: se pasa una parábola por los 3 puntos y se toma su pendiente en x₀; es mucho más precisa que la ' +
      'recta de las diferencias. También es el promedio de la progresiva y la regresiva.',
  },
  extremo_adelante: {
    items: [
      { symbol: 'D^{\\text{ad}}(h)', text: 'La aproximación de la derivada con el extremo hacia adelante.' },
      { symbol: 'x_0,\\ x_0 + h,\\ x_0 + 2h', text: 'Tres puntos hacia la derecha: x₀ y dos vecinos.' },
      { symbol: '-3,\\ 4,\\ -1', text: COEFFICIENTS_TEXT },
      { symbol: '2h', text: 'El denominador común.' },
    ],
    summary: 'Cuándo se usa: cuando no hay datos a la izquierda, por ejemplo en el primer dato de una tabla.',
  },
  extremo_atras: {
    items: [
      { symbol: 'D^{\\text{at}}(h)', text: 'La aproximación de la derivada con el extremo hacia atrás.' },
      { symbol: 'x_0,\\ x_0 - h,\\ x_0 - 2h', text: 'Tres puntos hacia la izquierda: x₀ y dos vecinos.' },
      { symbol: '3,\\ -4,\\ 1', text: COEFFICIENTS_TEXT },
      { symbol: '2h', text: 'El denominador común.' },
    ],
    summary: 'Cuándo se usa: cuando no hay datos a la derecha, por ejemplo en el último dato de una tabla.',
  },
}

/** Símbolos de una fórmula: progresiva, regresiva o una de 3 puntos. */
export function formulaGlossary(key) {
  if (THREE_POINT_GLOSSARY[key]) return THREE_POINT_GLOSSARY[key]
  const s = SIDE[key]
  const numerator = key === 'forward' ? 'f(x_0 + h) - f(x_0)' : 'f(x_0) - f(x_0 - h)'
  return {
    items: [
      { symbol: s.symbol, text: `La aproximación de la derivada con la diferencia ${s.word} (${s.direction}), usando un paso h.` },
      { symbol: 'x_0', text: 'El punto donde se quiere la derivada.' },
      {
        symbol: 'h',
        text: 'El paso, es decir, la distancia al punto vecino. Mientras más pequeño, mejor la aproximación (hasta cierto límite).',
      },
      { symbol: s.node, text: `El punto vecino ${s.where} de x₀.` },
      {
        symbol: key === 'forward' ? 'f(x_0),\\ f(x_0 + h)' : 'f(x_0),\\ f(x_0 - h)',
        text: 'La altura de la curva en cada punto.',
      },
      { symbol: numerator, text: 'El numerador: cuánto sube o baja la función al avanzar h.' },
      { symbol: '\\tfrac{\\text{cambio}}{h}', text: 'Dividir entre h convierte ese cambio en una pendiente: «subida entre avance».' },
    ],
    summary:
      'Idea clave: la derivada es la pendiente de la recta tangente; esta fórmula la aproxima con la pendiente de la ' +
      'recta secante que une los dos puntos.',
  }
}

export const ERRORS_LATEX =
  '|D_k - D_{k-1}|,\\qquad |D - f\'(x_0)|,\\qquad \\text{cota} = \\frac{h}{2}\\,M,\\quad M = \\max |f\'\'(x)|'

/** Símbolos de los errores, la cota y la razón. */
export const ERRORS_GLOSSARY = {
  items: [
    {
      symbol: '|D_k - D_{k-1}|',
      text:
        'Error estimado: cuánto cambió la aproximación respecto a la fila anterior. Es el que decide cuándo parar, ' +
        'porque en la práctica no se conoce la derivada exacta.',
    },
    { symbol: "|D - f'(x_0)|", text: 'Error real: la distancia a la derivada exacta. El sistema la calcula para comparar.' },
    {
      symbol: '\\frac{h}{2}\\,M',
      text: 'Cota: el error máximo que predice la teoría.',
    },
    {
      symbol: "M = \\max |f''(x)|",
      text: "El valor más grande de |f''(x)| en el intervalo que usa la fórmula, es decir, la máxima curvatura.",
    },
    { symbol: '\\tfrac{h}{2}', text: 'De dónde sale h/2: de la serie de Taylor; se explica en la Teoría.' },
    {
      symbol: 'h',
      text: 'Por qué h: el error es proporcional a h, así que al dividir h entre 2 el error se divide entre 2.',
    },
    {
      symbol: '\\text{Razón}',
      text: 'El error real de una fila dividido entre el de la anterior. Debe acercarse a 0.5, porque el error es O(h).',
    },
  ],
}

export const THREE_POINT_ERRORS_LATEX =
  "|D_k - D_{k-1}|,\\qquad |D - f'(x_0)|,\\qquad \\text{cota} = \\frac{h^{2}}{6}\\,M \\text{ o } \\frac{h^{2}}{3}\\,M," +
  "\\quad M = \\max |f'''(x)|"

/** Errores, cota y razón de la fórmula de 3 puntos. */
export const THREE_POINT_ERRORS_GLOSSARY = {
  items: [
    ERRORS_GLOSSARY.items[0],
    ERRORS_GLOSSARY.items[1],
    { symbol: '\\frac{h^{2}}{6}\\,M', text: 'Cota del punto medio: el error máximo que predice la teoría.' },
    { symbol: '\\frac{h^{2}}{3}\\,M', text: 'Cota de los extremos hacia adelante y hacia atrás.' },
    {
      symbol: "M = \\max |f'''(x)|",
      text: "El valor más grande de |f'''(x)| en el intervalo que usa cada fórmula: mide qué tanto se aleja f de una parábola.",
    },
    {
      symbol: 'h^{2}',
      text: 'Por qué h²: el error es proporcional a h², así que al dividir h entre 2 el error se divide entre unas 4 veces.',
    },
    {
      symbol: '3 \\text{ en vez de } 6',
      text: 'Por qué el extremo tiene 3 en vez de 6: su error es el doble, porque x₀ está en el borde y no al centro.',
    },
    {
      symbol: '\\text{Razón}',
      text: 'El error real de una fila dividido entre el de la anterior. Debe acercarse a 0.25, porque el error es O(h²).',
    },
  ],
}

/** Columnas de la tabla de refinamiento (las que se muestran). `ratio`: la razón esperada. */
export function refinementColumns(showReal, ratio = '0.5') {
  const columns = [
    { key: 'k', label: 'k', symbol: 'k', text: 'Número de la fila de refinamiento.' },
    { key: 'h', label: 'h', symbol: 'h', text: 'El paso de esa fila; se divide entre 2 en cada fila (h_k = h₀/2^(k−1)).' },
    { key: 'D', label: 'D', symbol: 'D', text: 'La aproximación de la derivada en esa fila.' },
    {
      key: 'estimated',
      label: 'Error estimado',
      symbol: '\\text{Error estimado}',
      text: 'Cuánto cambió D respecto a la fila anterior; decide cuándo parar.',
    },
  ]
  if (showReal) columns.push({ key: 'real', label: 'Error real', symbol: '\\text{Error real}', text: 'La distancia a la derivada exacta.' })
  columns.push({ key: 'bound', label: 'Cota', symbol: '\\text{Cota}', text: 'El error máximo que predice la teoría.' })
  if (showReal) {
    columns.push(
      {
        key: 'ratio',
        label: 'Razón',
        symbol: '\\text{Razón}',
        text: `Error real de esta fila entre el de la anterior; debe acercarse a ${ratio}.`,
      },
      {
        key: 'within',
        label: '≤ cota',
        symbol: '\\le \\text{cota}',
        text: '✔ si el error real quedó por debajo de la cota, como predice la teoría.',
      }
    )
  }
  return columns
}

const TABLE_FORMULA_TEXT = {
  forward: 'Aproximación con el dato vecino de la derecha: (yᵢ₊₁ − yᵢ)/h. No existe en el último punto.',
  backward: 'Aproximación con el dato vecino de la izquierda: (yᵢ − yᵢ₋₁)/h. No existe en el primer punto.',
  punto_medio: 'Punto medio, con un dato a cada lado: (yᵢ₊₁ − yᵢ₋₁)/(2h). No existe en el primer ni en el último punto.',
  extremo_adelante:
    'Extremo hacia adelante, con los dos datos de la derecha: (−3yᵢ + 4yᵢ₊₁ − yᵢ₊₂)/(2h). No existe en los dos últimos puntos.',
  extremo_atras:
    'Extremo hacia atrás, con los dos datos de la izquierda: (3yᵢ − 4yᵢ₋₁ + yᵢ₋₂)/(2h). No existe en los dos primeros puntos.',
}

const RECOMMENDED_TEXT =
  'El punto medio cuando hay datos a los dos lados (es el más preciso); en el primer dato, el extremo hacia adelante; ' +
  'en el último, el extremo hacia atrás.'

/** Columnas del modo tabla de datos. `formulas`: las pedidas; `recommended`: columna «Recomendada» (3 puntos). */
export function tableColumns(formulas, hasFunction, recommended = false) {
  const columns = [
    { key: 'i', label: 'i', symbol: 'i', text: 'Número del dato.' },
    { key: 'x', label: 'xᵢ', symbol: 'x_i', text: 'El punto donde se calcula la derivada.' },
    { key: 'y', label: 'f(xᵢ)', symbol: 'f(x_i)', text: 'El dato: la altura de la curva en xᵢ.' },
    ...formulas.map((f) => ({
      key: f.key,
      label: f.name,
      symbol: f.symbol_latex,
      text: TABLE_FORMULA_TEXT[f.key],
    })),
  ]
  if (recommended) {
    columns.push({ key: 'recommended', label: 'Recomendada', symbol: '\\text{Recomendada}', text: RECOMMENDED_TEXT })
  }
  if (hasFunction) {
    columns.push(
      { key: 'exact', label: 'f′(xᵢ) exacta', symbol: "f'(x_i)", text: 'La derivada exacta de la función para comparar, en xᵢ.' },
      ...formulas.map((f) => ({
        key: `e-${f.key}`,
        label: `Error real ${f.name.toLowerCase()}`,
        symbol: `\\text{Error real ${f.name.toLowerCase()}}`,
        text: 'La distancia entre la aproximación y la derivada exacta.',
      })),
      ...formulas.map((f) => ({
        key: `c-${f.key}`,
        label: `Cota ${f.name.toLowerCase()}`,
        symbol: `\\text{Cota ${f.name.toLowerCase()}}`,
        text:
          f.bound_derivative === 3
            ? `El error máximo que predice la teoría: (h²/${f.bound_coefficient[1]})·M, con M el máximo de |f'''| en los datos que usa la fórmula.`
            : "El error máximo que predice la teoría: (h/2)·M, con M el máximo de |f''| entre los dos datos.",
      })),
      { key: 'within', label: '≤ cota', symbol: '\\le \\text{cota}', text: '✔ si el error real quedó por debajo de la cota.' }
    )
  }
  return columns
}

/** Columnas de la tabla de comparación (3 puntos: otra descripción de «Fórmula»). */
export const comparisonColumns = (threePoint) =>
  threePoint
    ? COMPARISON_COLUMNS.map((c) =>
        c.key === 'formula' ? { ...c, text: 'La fórmula usada: punto medio, extremo hacia adelante o hacia atrás.' } : c
      )
    : COMPARISON_COLUMNS

/** Columnas de la tabla de comparación de la comprobación. */
export const COMPARISON_COLUMNS = [
  { key: 'formula', label: 'Fórmula', symbol: '\\text{Fórmula}', text: 'La diferencia usada: progresiva o regresiva.' },
  { key: 'D', label: 'Aproximación', symbol: '\\text{Aproximación}', text: 'El valor de D en la última fila.' },
  { key: 'exact', label: 'Exacta f′(x₀)', symbol: "f'(x_0)", text: 'La derivada exacta, sustituyendo x₀ en f′(x).' },
  { key: 'real', label: 'Error real', symbol: '\\text{Error real}', text: 'La distancia entre la aproximación y la exacta.' },
  { key: 'bound', label: 'Cota', symbol: '\\text{Cota}', text: 'El error máximo que predice la teoría en esa fila.' },
  { key: 'within', label: 'Error real ≤ cota', symbol: '\\le \\text{cota}', text: '✔ si se cumple la teoría.' },
]
