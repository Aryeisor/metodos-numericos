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

// Fórmula de 5 puntos: un glosario por fórmula.
const FIVE_COEFFICIENTS_TEXT =
  'Coeficientes: salen de exigir que la fórmula sea exacta para todos los polinomios de hasta grado 4. Suman 0, así ' +
  'que si f es constante la derivada da 0.'
const FIVE_POINT_GLOSSARY = {
  punto_medio_5: {
    items: [
      { symbol: 'D^{\\text{med},5}(h)', text: 'La aproximación de la derivada con el punto medio de 5 puntos, usando un paso h.' },
      {
        symbol: 'x_0 \\pm h,\\ x_0 \\pm 2h',
        text: 'Los 4 puntos: dos a cada lado de x₀, a distancias h y 2h.',
      },
      {
        symbol: '1,\\ -8,\\ 8,\\ -1',
        text:
          'Coeficientes: los vecinos cercanos pesan 8 y los lejanos, 1; los de la izquierda llevan signo contrario a los ' +
          'de la derecha. Suman 0, así que si f es constante la derivada da 0.',
      },
      { symbol: '12h', text: 'El denominador que hace que el resultado sea una pendiente.' },
      { symbol: 'f(x_0)', text: 'Por qué no aparece: su coeficiente es 0.' },
    ],
    summary:
      'Idea clave: se pasa un polinomio de grado 4 por 5 puntos y se toma su pendiente en x₀. También se obtiene ' +
      'combinando dos fórmulas de 3 puntos (Richardson).',
  },
  extremo_adelante_5: {
    items: [
      { symbol: 'D^{\\text{ad},5}(h)', text: 'La aproximación de la derivada con el extremo hacia adelante de 5 puntos.' },
      { symbol: 'x_0,\\ x_0 + h,\\ \\dots,\\ x_0 + 4h', text: '5 puntos hacia la derecha: x₀ y cuatro vecinos.' },
      { symbol: '-25,\\ 48,\\ -36,\\ 16,\\ -3', text: FIVE_COEFFICIENTS_TEXT },
      { symbol: '12h', text: 'El denominador común.' },
    ],
    summary: 'Cuándo se usa: en los dos primeros datos de una tabla, donde no hay dos datos a la izquierda.',
  },
  extremo_atras_5: {
    items: [
      { symbol: 'D^{\\text{at},5}(h)', text: 'La aproximación de la derivada con el extremo hacia atrás de 5 puntos.' },
      { symbol: 'x_0,\\ x_0 - h,\\ \\dots,\\ x_0 - 4h', text: '5 puntos hacia la izquierda: x₀ y cuatro vecinos.' },
      { symbol: '25,\\ -48,\\ 36,\\ -16,\\ 3', text: FIVE_COEFFICIENTS_TEXT },
      { symbol: '12h', text: 'El denominador común.' },
    ],
    summary: 'Cuándo se usa: en los dos últimos datos de una tabla, donde no hay dos datos a la derecha.',
  },
}

/** Símbolos de una fórmula: progresiva, regresiva o una de 3 o 5 puntos. */
export function formulaGlossary(key) {
  if (FIVE_POINT_GLOSSARY[key]) return FIVE_POINT_GLOSSARY[key]
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

export const FIVE_POINT_ERRORS_LATEX =
  "|D_k - D_{k-1}|,\\qquad |D - f'(x_0)|,\\qquad \\text{cota} = \\frac{h^{4}}{30}\\,M \\text{ o } \\frac{h^{4}}{5}\\,M," +
  '\\quad M = \\max |f^{(5)}(x)|'

/** Errores, cota y razón de la fórmula de 5 puntos. */
export const FIVE_POINT_ERRORS_GLOSSARY = {
  items: [
    ERRORS_GLOSSARY.items[0],
    ERRORS_GLOSSARY.items[1],
    { symbol: '\\frac{h^{4}}{30}\\,M', text: 'Cota del punto medio: el error máximo que predice la teoría.' },
    { symbol: '\\frac{h^{4}}{5}\\,M', text: 'Cota de los extremos hacia adelante y hacia atrás.' },
    {
      symbol: 'M = \\max |f^{(5)}(x)|',
      text:
        'El valor más grande de |f⁽⁵⁾(x)| en el intervalo que usa cada fórmula: mide qué tanto se aleja f de un ' +
        'polinomio de grado 4.',
    },
    {
      symbol: 'h^{4}',
      text: 'Por qué h⁴: el error es proporcional a h⁴, así que al dividir h entre 2 el error se divide entre unas 16 veces.',
    },
    {
      symbol: '5 \\text{ en vez de } 30',
      text: 'Por qué el extremo tiene 5 en vez de 30: su error es 6 veces mayor, porque x₀ está en el borde y no al centro.',
    },
    {
      symbol: '\\text{Razón}',
      text: 'El error real de una fila dividido entre el de la anterior. Debe acercarse a 0.0625 (1/16), porque el error es O(h⁴).',
    },
    {
      symbol: '\\text{Redondeo}',
      text:
        'Como esta fórmula es tan precisa, el error de redondeo de la computadora aparece antes: en las últimas filas la ' +
        'razón puede alejarse de 0.0625.',
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
  punto_medio_5:
    'Punto medio de 5 puntos, con dos datos a cada lado: (yᵢ₋₂ − 8yᵢ₋₁ + 8yᵢ₊₁ − yᵢ₊₂)/(12h). No existe en los dos ' +
    'primeros ni en los dos últimos puntos.',
  extremo_adelante_5:
    'Extremo hacia adelante de 5 puntos, con los cuatro datos de la derecha. No existe en los cuatro últimos puntos.',
  extremo_atras_5:
    'Extremo hacia atrás de 5 puntos, con los cuatro datos de la izquierda. No existe en los cuatro primeros puntos.',
}
// Tabla de 5 puntos: el punto medio de 3 puntos va como referencia.
const REFERENCE_TEXT = 'La fórmula de 3 puntos (punto medio), como referencia, para comparar.'

const RECOMMENDED_TEXT =
  'El punto medio cuando hay datos a los dos lados (es el más preciso); en el primer dato, el extremo hacia adelante; ' +
  'en el último, el extremo hacia atrás.'
const FIVE_POINT_RECOMMENDED_TEXT =
  'El punto medio de 5 puntos cuando hay dos datos a cada lado; si no, el extremo de 5 puntos; y el de 3 puntos sólo ' +
  'cuando no cabe ninguna de 5 (por ejemplo, en una tabla de 5 datos).'

const isReference = (f) => f.name === 'Punto medio de 3 puntos'

/** Columnas del modo tabla de datos. `formulas`: las pedidas; `recommended`: columna «Recomendada» (3 y 5 puntos). */
export function tableColumns(formulas, hasFunction, recommended = false) {
  const fivePoint = formulas.some((f) => f.bound_derivative === 5)
  const columns = [
    { key: 'i', label: 'i', symbol: 'i', text: 'Número del dato.' },
    { key: 'x', label: 'xᵢ', symbol: 'x_i', text: 'El punto donde se calcula la derivada.' },
    { key: 'y', label: 'f(xᵢ)', symbol: 'f(x_i)', text: 'El dato: la altura de la curva en xᵢ.' },
    ...formulas.map((f) => ({
      key: f.key,
      label: f.name,
      symbol: f.symbol_latex,
      text: isReference(f) ? REFERENCE_TEXT : TABLE_FORMULA_TEXT[f.key],
    })),
  ]
  if (recommended) {
    columns.push({
      key: 'recommended',
      label: 'Recomendada',
      symbol: '\\text{Recomendada}',
      text: fivePoint ? FIVE_POINT_RECOMMENDED_TEXT : RECOMMENDED_TEXT,
    })
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
          f.bound_derivative === 5
            ? `El error máximo que predice la teoría: (h⁴/${f.bound_coefficient[1]})·M, con M el máximo de |f⁽⁵⁾| en los datos que usa la fórmula.`
            : f.bound_derivative === 3
              ? `El error máximo que predice la teoría: (h²/${f.bound_coefficient[1]})·M, con M el máximo de |f'''| en los datos que usa la fórmula.`
              : "El error máximo que predice la teoría: (h/2)·M, con M el máximo de |f''| entre los dos datos.",
      })),
      { key: 'within', label: '≤ cota', symbol: '\\le \\text{cota}', text: '✔ si el error real quedó por debajo de la cota.' }
    )
  }
  return columns
}

/** Columnas de la tabla de comparación (3 y 5 puntos: otra descripción de «Fórmula»). */
export const comparisonColumns = (points) =>
  points
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
