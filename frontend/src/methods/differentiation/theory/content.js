// Contenido teórico de la categoría «Diferenciación numérica»: fórmulas en
// LaTeX, el ejemplo resuelto y los pasos del algoritmo.
//
// La notación es la del Resolver (D⁺, D⁻, h_k = h₀/2^(k−1), cota (h/2)·M) y el
// paso a paso del ejemplo se dibuja con los mismos componentes
// (DifferenceStepDetail, RefinementTable, DataPointsTable,
// DifferentiationVerification), así que se ve igual en ambas vistas.
import { formatNumber } from '../../../utils/iterationSteps'
import { latexNumber } from '../../../utils/latexFormulas'
import { stepSizeLatex } from '../formulas'
// Respuestas reales del backend (POST /api/solve/diferencias-finitas/), sin
// recortar: «function» es el ejemplo «ln(x) en x₀ = 1.8 (Burden y Faires)» y
// «table», «Posición de un carro (tabla + función)». El test
// test_differentiation.TheoryExampleTests comprueba que siguen coincidiendo
// con el solver.
import EXAMPLES from './finiteDifferencesExample.json'

export { formatNumber }

export const tex = {
  // Fundamento común
  limit: "f'(x_0) = \\lim_{h \\to 0} \\frac{f(x_0 + h) - f(x_0)}{h}",
  taylor:
    "f(x_0 + h) = f(x_0) + h\\,f'(x_0) + \\frac{h^2}{2!} f''(x_0) + \\dots + \\frac{h^n}{n!} f^{(n)}(x_0) + " +
    '\\underbrace{\\frac{h^{n+1}}{(n+1)!} f^{(n+1)}(\\xi)}_{\\text{residuo de Lagrange}}',
  taylorXi: '\\xi \\text{ entre } x_0 \\text{ y } x_0 + h',

  // Definición formal
  forward: '{D^{+}f(x_0) = \\frac{f(x_0 + h) - f(x_0)}{h}} \\qquad \\text{(progresiva o hacia adelante)}',
  backward: '{D^{-}f(x_0) = \\frac{f(x_0) - f(x_0 - h)}{h}} \\qquad \\text{(regresiva o hacia atrás)}',
  burden: '\\frac{f(x_0 + h) - f(x_0)}{h}',

  // Derivación
  taylorForward:
    "f(x_0 + h) = f(x_0) + h\\,f'(x_0) + \\frac{h^2}{2} f''(\\xi_1), \\quad \\xi_1 \\in (x_0,\\, x_0 + h)",
  isolatedForward:
    "f'(x_0) = \\frac{f(x_0 + h) - f(x_0)}{h} - \\underbrace{\\frac{h}{2} f''(\\xi_1)}_{\\text{error de truncamiento}}",
  taylorBackward:
    "f(x_0 - h) = f(x_0) - h\\,f'(x_0) + \\frac{h^2}{2} f''(\\xi_2), \\quad \\xi_2 \\in (x_0 - h,\\, x_0)",
  isolatedBackward: "f'(x_0) = \\frac{f(x_0) - f(x_0 - h)}{h} + \\frac{h}{2} f''(\\xi_2)",
  leadingErrors:
    "D^{+} - f'(x_0) \\approx +\\frac{h}{2} f''(x_0) + \\frac{h^2}{6} f'''(x_0), \\qquad " +
    "D^{-} - f'(x_0) \\approx -\\frac{h}{2} f''(x_0) + \\frac{h^2}{6} f'''(x_0)",
  average: '\\frac{D^{+} + D^{-}}{2} = \\frac{f(x_0 + h) - f(x_0 - h)}{2h}',

  // Error y convergencia
  bound: "|D^{\\pm} - f'(x_0)| \\le \\frac{h}{2}\\, M, \\qquad M = \\max |f''(x)| \\ \\text{en el intervalo usado}",
  totalError: 'E(h) \\approx \\frac{h}{2} M + \\frac{2\\varepsilon\\,|f(x_0)|}{h}',
  optimalH: 'h^{*} = 2\\sqrt{\\frac{\\varepsilon\\,|f(x_0)|}{M}}',
}

// --- Ejemplo de la función (ejemplo 1 del Resolver) ------------------------------

export const FUNCTION_EXAMPLE = EXAMPLES.function
export const TABLE_EXAMPLE = EXAMPLES.table

const rows = FUNCTION_EXAMPLE.iterations
const h0 = rows[0].extra.h
const [forwardFormula, backwardFormula] = FUNCTION_EXAMPLE.formulas
export { backwardFormula, forwardFormula }

const fn = FUNCTION_EXAMPLE.function
export const example = {
  function: `f(x) = ${fn.latex}`,
  derivative: `f'(x) = ${fn.derivative.latex}`,
  exact: `f'(${FUNCTION_EXAMPLE.x0_display.latex}) = ${latexNumber(FUNCTION_EXAMPLE.exact)}`,
  data:
    `x_0 = ${FUNCTION_EXAMPLE.x0_display.latex}, \\quad h_0 = ${h0.latex}, \\quad ` +
    `\\text{tolerancia} = ${latexNumber(FUNCTION_EXAMPLE.tolerance)}`,
  tolerance: formatNumber(FUNCTION_EXAMPLE.tolerance),
  rowsUsed: FUNCTION_EXAMPLE.iterations_used,
  last: rows.at(-1).extra,
}

/** Props de DifferenceStepDetail para la fila k y una fórmula, como en RefinementTable. */
export function stepDetail(k, formula) {
  const step = rows[k - 1]
  return {
    formula,
    item: step.extra[formula.key],
    label: k,
    stepLine: stepSizeLatex(k, step.extra.h, h0),
    h: step.extra.h,
    template: fn.template,
    exact: FUNCTION_EXAMPLE.exact,
    exactSource: FUNCTION_EXAMPLE.verification.substitution,
    derivativeLatex: fn.derivative.latex,
    boundDerivativeLatex: fn.higher_derivatives[formula.bound_derivative]?.latex ?? null,
    previous: k > 1 ? rows[k - 2].extra[formula.key] : null,
    samples: FUNCTION_EXAMPLE.sampling_points,
  }
}

// Fila 1: lo que se lee en la figura (concavidad) y el promedio de las dos.
const first = rows[0].extra
const exact = FUNCTION_EXAMPLE.exact
const x0 = FUNCTION_EXAMPLE.x0
const averageValue = (first.forward.D + first.backward.D) / 2
const averageError = Math.abs(averageValue - exact)
// f'''(x) = 2/x³ para ln x: predicción (h²/6)·f'''(x₀) del error del promedio.
const predicted = (first.h.value ** 2 / 6) * (2 / x0 ** 3)

export const concavity = `${latexNumber(first.forward.D)} < ${latexNumber(exact)} < ${latexNumber(first.backward.D)}`

export const averageExample = {
  value:
    `\\frac{${latexNumber(first.forward.D)} + ${latexNumber(first.backward.D)}}{2} = ${latexNumber(averageValue)}`,
  error: `\\left|${latexNumber(averageValue)} - ${latexNumber(exact)}\\right| \\approx ${latexNumber(averageError)}`,
  predicted: `\\frac{h^2}{6} f'''(${latexNumber(x0)}) = \\frac{${first.h.latex}^2}{6} \\cdot \\frac{2}{${latexNumber(x0)}^3} \\approx ${latexNumber(predicted)}`,
  times: Math.round(Math.min(first.forward.real_error, first.backward.real_error) / averageError),
}

/* Tabla de convergencia: las 6 primeras filas del solver, sin el paso a paso. */
export const convergenceRows = rows.slice(0, 6).map((step) => ({
  k: step.iteration,
  h: step.extra.h.text,
  forward: step.extra.forward,
  backward: step.extra.backward,
}))

/* La «V» del error total: diferencia progresiva de ln x en x₀ = 1.8 con
   h = 10⁻¹ … 10⁻¹⁵, calculada aquí con Math.log (doble precisión, como el
   backend). Es sólo ilustrativa. */
const V_POWERS = Array.from({ length: 15 }, (_, i) => i + 1)
const SUPERSCRIPT = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }
const power10 = (n) => `10${String(n).replace(/./g, (c) => SUPERSCRIPT[c])}`
export const roundingCurve = {
  iterations: V_POWERS.map((p) => ({ iteration: p })),
  labels: V_POWERS.map((p) => power10(-p)),
  series: [
    {
      label: 'Error real de la progresiva',
      values: V_POWERS.map((p) => {
        const h = 10 ** -p
        return Math.abs((Math.log(x0 + h) - Math.log(x0)) / h - exact)
      }),
      color: '--color-series-1',
    },
  ],
}

/* Orden de magnitud del error real (los mismos cálculos, de dos en dos). */
export const roundingTable = [
  ['10^{-2}', '10^{-3}'],
  ['10^{-4}', '10^{-5}'],
  ['10^{-6}', '10^{-7}'],
  ['10^{-8}', '10^{-8}'],
  ['10^{-10}', '10^{-8}'],
  ['10^{-12}', '10^{-8}'],
  ['10^{-14}', '10^{-4}'],
]

// --- Mini-ejemplo de datos (ejemplo 7 del Resolver) ------------------------------

const tableRows = TABLE_EXAMPLE.iterations
const velocities = (key) =>
  tableRows.filter((s) => s.extra[key]).map((s) => ({ t: s.extra.x_display.text, v: formatNumber(s.extra[key].D) }))

export const carExample = {
  times: tableRows.map((s) => s.extra.x_display.text).join(', '),
  positions: tableRows.map((s) => formatNumber(s.extra.y)).join(', '),
  forward: velocities('forward'),
  backward: velocities('backward'),
  error: formatNumber(tableRows[0].extra.forward.real_error),
  bound: formatNumber(tableRows[0].extra.forward.bound),
}

// --- Algoritmo ------------------------------------------------------------------

export const ALGORITHM_STEPS = {
  'diferencias-finitas': [
    {
      title: 'Datos',
      body: [
        { m: 'f(x)' },
        ' (o la tabla de datos), ',
        { m: 'x_0' },
        ', ',
        { m: 'h_0' },
        ', la fórmula (progresiva, regresiva o ambas), la tolerancia y el máximo de refinamientos.',
      ],
    },
    {
      title: 'Puntos',
      body: [{ m: 'x_0 + h' }, ' (progresiva) y/o ', { m: 'x_0 - h' }, ' (regresiva).'],
    },
    {
      title: 'Evaluar',
      body: ['Se calcula ', { m: 'f' }, ' en ', { m: 'x_0' }, ' y en los puntos del paso anterior.'],
    },
    {
      title: 'Cociente',
      body: ['Se aplica la fórmula y se obtiene ', { m: 'D_k' }, ', la aproximación de la fila ', { m: 'k' }, '.'],
    },
    {
      title: 'Errores',
      body: [
        'Error estimado ',
        { m: '|D_k - D_{k-1}|' },
        '; error real ',
        { m: "|D_k - f'(x_0)|" },
        ' (si se conoce ',
        { m: "f'" },
        '); cota ',
        { m: '\\frac{h}{2} M' },
        '.',
      ],
    },
    {
      title: 'Refinar',
      body: [{ m: 'h \\leftarrow h / 2' }, ' y se repite desde el paso 2.'],
    },
    {
      title: 'Parar',
      body: [
        'Cuando el error estimado es ',
        { m: '\\le' },
        ' tolerancia y hay al menos 6 filas, o al llegar al máximo de refinamientos.',
      ],
    },
    {
      title: 'Comprobar',
      body: [
        'Se sustituye ',
        { m: 'x_0' },
        ' en ',
        { m: "f'(x)" },
        ' y se verifica que el error real quede por debajo de la cota.',
      ],
    },
  ],
}

/* Las dos fuentes de error, en tarjetas como las del algoritmo. */
export const ERROR_SOURCES = [
  {
    title: 'Truncamiento',
    body: [
      'Es el error de «cortar» la serie de Taylor: los términos que se descartan. ',
      'Disminuye cuando ',
      { m: 'h' },
      ' disminuye.',
    ],
  },
  {
    title: 'Redondeo',
    body: [
      'La computadora guarda unos 16 dígitos. Al restar dos valores casi iguales, ',
      { m: 'f(x_0 + h) - f(x_0)' },
      ' con ',
      { m: 'h' },
      ' muy pequeño, se pierden cifras, y ese error crece cuando ',
      { m: 'h' },
      ' disminuye. Es aproximadamente ',
      { m: '2\\varepsilon |f(x_0)| / h' },
      ', con ',
      { m: '\\varepsilon \\approx 2.22 \\cdot 10^{-16}' },
      '.',
    ],
  },
]

/* Restricciones y precauciones, en el mismo formato de tarjetas. */
export const PRECAUTIONS = [
  {
    title: 'Segunda derivada continua',
    body: [
      'Para que la cota valga, ',
      { m: 'f' },
      ' debe tener ',
      { m: "f''" },
      ' continua en el intervalo usado. Si no la tiene, como ',
      { m: '|x|' },
      ' en ',
      { m: 'x = 0' },
      ', la fórmula no aproxima ninguna derivada: la progresiva da 1 y la regresiva da −1.',
    ],
  },
  {
    title: 'Dominio de f',
    body: [
      'Todos los puntos deben estar en el dominio. Por ejemplo, ',
      { m: '\\ln x' },
      ' con ',
      { m: 'x_0 = 0.05' },
      ' y ',
      { m: 'h = 0.1' },
      ' necesita ',
      { m: '\\ln(-0.05)' },
      ', que no existe en los reales.',
    ],
  },
  {
    title: 'Ni muy grande ni muy pequeño',
    body: [
      { m: 'h' },
      ' grande aumenta el error de truncamiento; ',
      { m: 'h' },
      ' muy pequeño, el de redondeo.',
    ],
  },
  {
    title: 'Datos con ruido',
    body: [
      'Si cada dato tiene un error de hasta ',
      { m: '\\delta' },
      ', la fórmula puede amplificarlo hasta ',
      { m: '2\\delta / h' },
      ': con ',
      { m: '\\delta = 0.001' },
      ' y ',
      { m: 'h = 0.01' },
      ', hasta 0.2. Derivar numéricamente amplifica el ruido; integrar, en cambio, lo suaviza (se verá en la categoría de integración).',
    ],
  },
  {
    title: 'Extremos de una tabla',
    body: [
      'En el primer dato sólo existe la progresiva y en el último sólo la regresiva. Es su principal utilidad frente a las fórmulas centradas.',
    ],
  },
  {
    title: 'Espaciado no uniforme',
    body: ['Se puede usar: cada par de puntos lleva su propio ', { m: 'h' }, '.'],
  },
  {
    title: 'Radianes',
    body: ['Las funciones trigonométricas se evalúan en radianes.'],
  },
]
