// Glosarios de las diferencias progresiva y regresiva: qué significa cada
// símbolo de las fórmulas y cada columna de las tablas. Los usan la vista
// (GlossaryBlock e InfoTip, los mismos de integración) y el PDF. `symbol` es
// LaTeX; `text`, una línea en palabras. Las fórmulas de 3 y 5 puntos pueden
// agregar sus propias entradas con la misma forma.

const SIDE = {
  forward: { symbol: 'D^{+}(h)', word: 'progresiva', direction: '«hacia adelante»', where: 'a la derecha', node: 'x_0 + h' },
  backward: { symbol: 'D^{-}(h)', word: 'regresiva', direction: '«hacia atrás»', where: 'a la izquierda', node: 'x_0 - h' },
}

/** Símbolos de la fórmula progresiva o regresiva. */
export function formulaGlossary(key) {
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

/** Columnas de la tabla de refinamiento (las que se muestran). */
export function refinementColumns(showReal) {
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
        text: 'Error real de esta fila entre el de la anterior; debe acercarse a 0.5.',
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

/** Columnas del modo tabla de datos. `formulas`: las pedidas (progresiva, regresiva o ambas). */
export function tableColumns(formulas, hasFunction) {
  const columns = [
    { key: 'i', label: 'i', symbol: 'i', text: 'Número del dato.' },
    { key: 'x', label: 'xᵢ', symbol: 'x_i', text: 'El punto donde se calcula la derivada.' },
    { key: 'y', label: 'f(xᵢ)', symbol: 'f(x_i)', text: 'El dato: la altura de la curva en xᵢ.' },
    ...formulas.map((f) => ({
      key: f.key,
      label: f.name,
      symbol: SIDE[f.key].symbol.replace('(h)', ''),
      text:
        f.key === 'forward'
          ? 'Aproximación con el dato vecino de la derecha: (yᵢ₊₁ − yᵢ)/h. No existe en el último punto.'
          : 'Aproximación con el dato vecino de la izquierda: (yᵢ − yᵢ₋₁)/h. No existe en el primer punto.',
    })),
  ]
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
        text: "El error máximo que predice la teoría: (h/2)·M, con M el máximo de |f''| entre los dos datos.",
      })),
      { key: 'within', label: '≤ cota', symbol: '\\le \\text{cota}', text: '✔ si el error real quedó por debajo de la cota.' }
    )
  }
  return columns
}

/** Columnas de la tabla de comparación de la comprobación. */
export const COMPARISON_COLUMNS = [
  { key: 'formula', label: 'Fórmula', symbol: '\\text{Fórmula}', text: 'La diferencia usada: progresiva o regresiva.' },
  { key: 'D', label: 'Aproximación', symbol: '\\text{Aproximación}', text: 'El valor de D en la última fila.' },
  { key: 'exact', label: 'Exacta f′(x₀)', symbol: "f'(x_0)", text: 'La derivada exacta, sustituyendo x₀ en f′(x).' },
  { key: 'real', label: 'Error real', symbol: '\\text{Error real}', text: 'La distancia entre la aproximación y la exacta.' },
  { key: 'bound', label: 'Cota', symbol: '\\text{Cota}', text: 'El error máximo que predice la teoría en esa fila.' },
  { key: 'within', label: 'Error real ≤ cota', symbol: '\\le \\text{cota}', text: '✔ si se cumple la teoría.' },
]
