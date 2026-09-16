<script setup>
import MathFormula from '../components/MathFormula.vue'
import { buildIterationDetail, formatNumber } from '../utils/iterationSteps'
import {
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  errorFormulaLatex,
  generalFormulaLatex,
  substitutionLatex,
} from '../utils/latexFormulas'

// Las fórmulas de iteración y de error vienen de las mismas funciones que usa
// el paso a paso de Resolver, para que ambas vistas compartan la notación exacta.
const tex = {
  system: 'A \\cdot x = b',
  nByN: 'n \\times n',
  nMin: 'n \\geq 3',
  x0: 'x^{(0)}',
  sequence: 'x^{(1)},\\ x^{(2)},\\ \\dots',
  aii: 'a_{ii}',
  xi: 'x_i',
  dominance: '\\left| a_{ii} \\right| > \\sum_{j \\neq i} \\left| a_{ij} \\right|',
  decomposition: 'A = D + R',
  jacobi: `${generalFormulaLatex('jacobi')}, \\qquad i = 1, \\dots, n`,
  gaussSeidel: generalFormulaLatex('gauss-seidel'),
  error: errorFormulaLatex(),
  xNext: 'x^{(k+1)}',
  xCurrent: 'x^{(k)}',
  xiNext: 'x_i^{(k+1)}',
  kRange: 'k = 1, 2, \\dots',
  iRange: 'i = 1, \\dots, n',
  before: 'x_1, \\dots, x_{i-1}',
  after: 'x_{i+1}, \\dots, x_n',
  jBefore: 'j < i',
  eps: '\\varepsilon',

  // Radio espectral
  recurrence: 'x^{(k+1)} = T\\, x^{(k)} + c',
  splitting: 'A = D + L + U',
  jacobiMatrix: 'T_J = -D^{-1} (L + U)',
  gaussSeidelMatrix: 'T_{GS} = -(D + L)^{-1} U',
  spectralRadius: '\\rho(T) = \\max_i \\left| \\lambda_i \\right| < 1',
  rho: '\\rho(T)',
  exampleSize: '3 \\times 3',
  rhoJacobi: '\\rho(T_J) = 0.3',
  rhoGaussSeidel: '\\rho(T_{GS}) \\approx 0.089443',

  // Ejemplo resuelto
  exampleSystem:
    '\\begin{cases} 10x_1 + 2x_2 + x_3 = 17 \\\\ x_1 + 10x_2 + 2x_3 = 27 \\\\ 2x_1 + x_2 + 10x_3 = 34 \\end{cases}',
  exampleSolution: 'x = (1,\\ 2,\\ 3)',
  exampleStart: 'x^{(0)} = (0,\\ 0,\\ 0)',
}

/* Ejemplo trabajado a mano. Los vectores de cada iteración son datos ya
   verificados contra los solvers del backend; las sustituciones numéricas se
   generan con las mismas utilidades que el paso a paso de Resolver, así que
   la notación y la aritmética mostrada son idénticas en toda la app. */
const EXAMPLE = {
  A: [
    [10, 2, 1],
    [1, 10, 2],
    [2, 1, 10],
  ],
  b: [17, 27, 34],
  x0: [0, 0, 0],
}

const EXAMPLE_ITERATIONS = {
  jacobi: [
    [1.7, 2.7, 3.4],
    [0.82, 1.85, 2.79],
    [1.051, 2.06, 3.0509999999999997],
  ],
  'gauss-seidel': [
    [1.7, 2.5300000000000002, 2.807],
    [0.9132999999999999, 2.04727, 3.012613],
    [0.9892847, 1.9985489300000001, 3.002288167],
  ],
}

function workedSteps(method) {
  const iterations = EXAMPLE_ITERATIONS[method].map((x, i) => ({
    iteration: i + 1,
    x,
    error: null,
  }))

  return iterations.map((row, index) => {
    const detail = buildIterationDetail({ ...EXAMPLE, method, iterations, index })
    return {
      iteration: row.iteration,
      x: row.x,
      substitutions: detail.variables.map((variable) => substitutionLatex(variable, row.iteration)),
    }
  })
}

const jacobiSteps = workedSteps('jacobi')
const gaussSeidelSteps = workedSteps('gauss-seidel')

/* Pasos del algoritmo como datos: cada descripción es una lista de fragmentos
   donde las cadenas son texto y los objetos { m } son fórmulas que se
   renderizan con MathFormula en línea. Así los dos métodos comparten los tres
   pasos que son idénticos y sólo cambia el segundo. */
const STEP_START = {
  title: 'Vector inicial',
  body: [
    'Se parte de una aproximación inicial ',
    { m: tex.x0 },
    ' (por defecto, ceros) y se fija una tolerancia ',
    { m: tex.eps },
    '.',
  ],
}

const STEP_ERROR = {
  title: 'Medir el error',
  body: [
    'Se calcula la norma infinito entre dos iteraciones sucesivas: ',
    { m: tex.error },
    '.',
  ],
}

const STEP_STOP = {
  title: 'Criterio de parada',
  body: [
    'El proceso se detiene cuando el error es menor que ',
    { m: tex.eps },
    ' y se han ejecutado al menos 6 iteraciones, o al alcanzar el número máximo de iteraciones configurado.',
  ],
}

const ALGORITHM_STEPS = {
  jacobi: [
    STEP_START,
    {
      title: 'Calcular la nueva iteración',
      body: [
        'En cada iteración ',
        { m: tex.kRange },
        ' se calcula ',
        { m: tex.xiNext },
        ' para todo ',
        { m: 'i' },
        ' con la fórmula anterior, usando únicamente los valores de ',
        { m: tex.xCurrent },
        '.',
      ],
    },
    STEP_ERROR,
    STEP_STOP,
  ],
  'gauss-seidel': [
    STEP_START,
    {
      title: 'Actualizar componente a componente',
      body: [
        'En cada iteración se recorre ',
        { m: tex.iRange },
        ' actualizando ',
        { m: tex.xi },
        ' in situ, de modo que para ',
        { m: tex.jBefore },
        ' ya se usan los valores recalculados en esa misma iteración.',
      ],
    },
    STEP_ERROR,
    STEP_STOP,
  ],
}

function vectorLatex(name, x) {
  const values = x.map((value) => formatNumber(value)).join(',\\ ')
  return `${name ? `${name} = ` : ''}(${values})`
}

// Filas de la tabla comparativa: las dos trayectorias intercaladas por iteración.
const comparisonRows = jacobiSteps.flatMap((step, i) => [
  { key: `j${i}`, iteration: step.iteration, method: 'Jacobi', x: step.x, first: true },
  { key: `g${i}`, iteration: step.iteration, method: 'Gauss-Seidel', x: gaussSeidelSteps[i].x },
])
</script>

<template>
  <div class="theory">
    <div class="card">
      <h2>Fundamento común: sistemas <MathFormula :expression="tex.system" /></h2>
      <p>
        Ambos métodos resuelven sistemas de <MathFormula expression="n" /> ecuaciones lineales con
        <MathFormula expression="n" /> incógnitas, expresados en forma matricial
        <MathFormula :expression="tex.system" />, donde <MathFormula expression="A" /> es la matriz
        de coeficientes (<MathFormula :expression="tex.nByN" />), <MathFormula expression="x" /> el
        vector de incógnitas y <MathFormula expression="b" /> el vector de términos independientes.
        En lugar de resolver el sistema de forma directa (por ejemplo, con eliminación gaussiana),
        los métodos <strong>iterativos</strong> parten de una aproximación inicial
        <MathFormula :expression="tex.x0" /> y generan una sucesión de aproximaciones
        <MathFormula :expression="tex.sequence" /> que, bajo ciertas condiciones, converge a la
        solución exacta.
      </p>
      <h3>Restricciones de aplicabilidad</h3>
      <ul>
        <li>
          La matriz <MathFormula expression="A" /> debe ser cuadrada
          (<MathFormula :expression="tex.nByN" />), con <MathFormula :expression="tex.nMin" />.
        </li>
        <li>
          Ningún elemento de la diagonal principal (<MathFormula :expression="tex.aii" />) puede ser
          cero, ya que se necesita para despejar cada variable <MathFormula :expression="tex.xi" />.
        </li>
        <li>
          <strong>Dominancia diagonal</strong> (condición suficiente, no necesaria, de convergencia):
          se dice que <MathFormula expression="A" /> es diagonalmente dominante por filas si, para
          cada fila <MathFormula expression="i" />,
          <div class="formula-box theory-formula">
            <MathFormula :expression="tex.dominance" display-mode />
          </div>
          Si se cumple para todas las filas, ambos métodos convergen para cualquier vector inicial.
          Si no se cumple, el método puede converger o no; la aplicación lo advierte pero permite
          continuar.
        </li>
      </ul>

      <h3>La condición real de convergencia: el radio espectral</h3>
      <p>
        La dominancia diagonal es cómoda de verificar, pero no es la condición que realmente
        gobierna la convergencia. Ambos métodos pueden escribirse como una única recurrencia
        matricial:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.recurrence" display-mode />
      </div>
      <p>
        donde <MathFormula expression="T" /> es la <strong>matriz de iteración</strong>, que resulta
        de despejar la recurrencia a partir de la descomposición
        <MathFormula :expression="tex.splitting" /> (con <MathFormula expression="D" /> la diagonal,
        <MathFormula expression="L" /> la parte triangular inferior y
        <MathFormula expression="U" /> la superior; en la notación de más abajo,
        <MathFormula expression="R = L + U" />). Cada método tiene la suya:
      </p>
      <div class="formula-pair">
        <div class="formula-box theory-formula">
          <MathFormula :expression="tex.jacobiMatrix" display-mode />
        </div>
        <div class="formula-box theory-formula">
          <MathFormula :expression="tex.gaussSeidelMatrix" display-mode />
        </div>
      </div>
      <p>
        La condición <strong>necesaria y suficiente</strong> de convergencia es que el
        <strong>radio espectral</strong> de esa matriz —el mayor de los módulos de sus valores
        propios <MathFormula expression="\lambda_i" />— sea menor que 1:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.spectralRadius" display-mode />
      </div>
      <p>
        Si se cumple, el método converge para <em>cualquier</em> vector inicial, y cuanto más
        pequeño sea <MathFormula :expression="tex.rho" />, más rápido lo hace. En el sistema
        <MathFormula :expression="tex.exampleSize" /> que se resuelve más abajo, los radios
        espectrales son <MathFormula :expression="tex.rhoJacobi" /> y
        <MathFormula :expression="tex.rhoGaussSeidel" />: ambos bastante menores que 1, y el de
        Gauss-Seidel es más de tres veces más pequeño, lo que explica que converja más rápido.
      </p>
      <p>
        Calcular <MathFormula :expression="tex.rho" /> exige resolver un problema de valores
        propios, más costoso que el propio sistema. Por eso en la práctica se usa la dominancia
        diagonal como <strong>atajo</strong>: se comprueba con una simple suma por filas y
        <em>garantiza</em> <MathFormula :expression="tex.rho" /> &lt; 1. Pero es sólo una condición
        suficiente, y de ahí las dos situaciones que se ven en la aplicación:
      </p>
      <ul>
        <li>
          Una matriz diagonalmente dominante <strong>siempre</strong> converge: el atajo nunca falla
          cuando se cumple.
        </li>
        <li>
          Una matriz que no lo es <strong>puede converger igualmente</strong>, porque lo que
          importa es <MathFormula :expression="tex.rho" />. Es el caso de los sistemas que la
          aplicación arregla reordenando filas: el sistema original ya tenía solución, sólo estaba
          escrito en un orden que ocultaba la dominancia.
        </li>
      </ul>
    </div>

    <div class="card">
      <h2>Método de Jacobi</h2>
      <h3 class="first-heading">Definición formal</h3>
      <p>
        Se descompone <MathFormula :expression="tex.decomposition" />, donde
        <MathFormula expression="D" /> es la diagonal de <MathFormula expression="A" /> y
        <MathFormula expression="R" /> contiene el resto de los elementos. La fórmula de iteración,
        componente a componente, es:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.jacobi" display-mode />
      </div>
      <p class="formula-legend">
        <span :style="{ color: PREVIOUS_COLOR }">■</span> valores de la iteración anterior
      </p>
      <p>
        La característica distintiva de Jacobi es que <strong>todas</strong> las componentes de la
        nueva iteración <MathFormula :expression="tex.xNext" /> se calculan usando únicamente los
        valores de la iteración anterior completa <MathFormula :expression="tex.xCurrent" />; ningún
        valor recién calculado se reutiliza dentro de la misma iteración.
      </p>
      <h3>Algoritmo de aplicación</h3>
      <ol class="steps">
        <li v-for="(step, i) in ALGORITHM_STEPS.jacobi" :key="i" class="step">
          <span class="step-number" aria-hidden="true">{{ i + 1 }}</span>
          <h4 class="step-title">{{ step.title }}</h4>
          <p class="step-text">
            <template v-for="(part, j) in step.body" :key="j">
              <MathFormula v-if="part.m" :expression="part.m" /><template v-else>{{
                part
              }}</template>
            </template>
          </p>
        </li>
      </ol>

      <h3>Ejemplo resuelto: tres iteraciones de Jacobi</h3>
      <p>
        Tomemos este sistema, cuya solución exacta es
        <MathFormula :expression="tex.exampleSolution" />, partiendo de
        <MathFormula :expression="tex.exampleStart" />:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.exampleSystem" display-mode />
      </div>
      <p>
        En cada paso, <strong>las tres</strong> componentes se calculan con los valores de la
        iteración anterior (en <span class="legend-prev">azul</span>):
      </p>

      <div v-for="step in jacobiSteps" :key="step.iteration" class="worked-step">
        <p class="worked-step-title">Iteración {{ step.iteration }}</p>
        <div class="formula-pair">
          <div
            v-for="(latex, i) in step.substitutions"
            :key="i"
            class="formula-box theory-formula"
          >
            <MathFormula :expression="latex" display-mode />
          </div>
        </div>
      </div>

      <p>
        Tras tres iteraciones vamos por
        <MathFormula :expression="vectorLatex('x^{(3)}', jacobiSteps[2].x)" />, todavía a cierta
        distancia de <MathFormula :expression="tex.exampleSolution" />.
      </p>
    </div>

    <div class="card">
      <h2>Método de Gauss-Seidel</h2>
      <h3 class="first-heading">Definición formal</h3>
      <p>
        Es una variante de Jacobi que acelera la convergencia reutilizando, dentro de la misma
        iteración, los valores de <MathFormula expression="x" /> que ya fueron actualizados:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.gaussSeidel" display-mode />
      </div>
      <p class="formula-legend">
        <span :style="{ color: PREVIOUS_COLOR }">■</span> valores de la iteración anterior ·
        <span :style="{ color: CURRENT_COLOR }">■</span> valores ya recalculados en esta misma
        iteración
      </p>
      <p>
        Es decir, para calcular <MathFormula :expression="tex.xi" /> se usan los valores
        <MathFormula :expression="tex.before" /> ya recalculados en la iteración actual, y los valores
        <MathFormula :expression="tex.after" /> aún de la iteración anterior. Esto normalmente reduce
        el número de iteraciones necesarias respecto a Jacobi.
      </p>
      <h3>Algoritmo de aplicación</h3>
      <ol class="steps">
        <li v-for="(step, i) in ALGORITHM_STEPS['gauss-seidel']" :key="i" class="step">
          <span class="step-number" aria-hidden="true">{{ i + 1 }}</span>
          <h4 class="step-title">{{ step.title }}</h4>
          <p class="step-text">
            <template v-for="(part, j) in step.body" :key="j">
              <MathFormula v-if="part.m" :expression="part.m" /><template v-else>{{
                part
              }}</template>
            </template>
          </p>
        </li>
      </ol>

      <h3>Ejemplo resuelto: el mismo sistema con Gauss-Seidel</h3>
      <p>
        Resolvamos el mismo sistema y desde el mismo punto de partida, para poder comparar. La
        diferencia aparece a partir de la segunda ecuación: en cuanto una componente se recalcula,
        las siguientes ya usan ese valor <span class="legend-current">recién calculado</span> en
        lugar del de la iteración anterior.
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.exampleSystem" display-mode />
      </div>

      <div v-for="step in gaussSeidelSteps" :key="step.iteration" class="worked-step">
        <p class="worked-step-title">Iteración {{ step.iteration }}</p>
        <div class="formula-pair">
          <div
            v-for="(latex, i) in step.substitutions"
            :key="i"
            class="formula-box theory-formula"
          >
            <MathFormula :expression="latex" display-mode />
          </div>
        </div>
      </div>

      <p>
        Con el mismo número de iteraciones, Gauss-Seidel llega a
        <MathFormula :expression="vectorLatex('x^{(3)}', gaussSeidelSteps[2].x)" />, muy cerca ya de
        <MathFormula :expression="tex.exampleSolution" />, mientras que Jacobi seguía en
        <MathFormula :expression="vectorLatex('', jacobiSteps[2].x)" />. Reutilizar los valores
        nuevos dentro de la misma iteración acelera la convergencia.
      </p>

      <h4 class="table-caption">Comparación iteración a iteración</h4>
      <div class="table-scroll">
        <table class="comparison-table numeric-table">
          <thead>
            <tr>
              <th>Iteración</th>
              <th>Método</th>
              <th><MathFormula expression="x_1" /></th>
              <th><MathFormula expression="x_2" /></th>
              <th><MathFormula expression="x_3" /></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in comparisonRows" :key="row.key" :class="{ 'group-start': row.first }">
              <td>{{ row.first ? row.iteration : '' }}</td>
              <td>{{ row.method }}</td>
              <td v-for="(value, i) in row.x" :key="i">{{ formatNumber(value) }}</td>
            </tr>
            <tr class="exact-row group-start">
              <td></td>
              <td>Solución exacta</td>
              <td>1</td>
              <td>2</td>
              <td>3</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="table-note">
        Puedes cargar este mismo sistema en la vista <strong>Resolver</strong> para verlo converger
        hasta el final.
      </p>
    </div>

    <div class="card">
      <h2>Jacobi frente a Gauss-Seidel</h2>
      <p>
        Ambos métodos resuelven el mismo problema y comparten las mismas condiciones de
        convergencia, pero se comportan de forma distinta en tres aspectos prácticos:
      </p>
      <div class="table-scroll">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Criterio</th>
              <th>Jacobi</th>
              <th>Gauss-Seidel</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Velocidad de convergencia</th>
              <td>
                Más lenta. Cada iteración usa sólo información de la anterior, así que la mejora por
                paso es menor.
              </td>
              <td>
                Generalmente converge en menos iteraciones para el mismo sistema, porque aprovecha
                los valores actualizados de inmediato. En el ejemplo de arriba,
                <MathFormula :expression="tex.rho" /> pasa de 0.3 a 0.089443.
              </td>
            </tr>
            <tr>
              <th scope="row">Uso de memoria</th>
              <td>
                Necesita dos vectores: <MathFormula :expression="tex.xCurrent" /> completo se
                conserva mientras se construye <MathFormula :expression="tex.xNext" />.
              </td>
              <td>
                Actualiza el vector <em>in situ</em>: no hace falta conservar la iteración anterior
                completa, sólo el valor previo de la componente que se está sustituyendo.
              </td>
            </tr>
            <tr>
              <th scope="row">Paralelización</th>
              <td>
                Trivialmente paralelizable: dentro de una iteración, cada componente de
                <MathFormula :expression="tex.xNext" /> es independiente de las demás y puede
                calcularse a la vez.
              </td>
              <td>
                No es directamente paralelizable: cada componente depende de las que acaban de
                actualizarse en esa misma iteración, lo que impone un orden secuencial.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="table-note">
        En resumen: Gauss-Seidel suele ser preferible en un cálculo secuencial, mientras que Jacobi
        resulta atractivo cuando se dispone de varios procesadores.
      </p>
    </div>

    <div class="card">
      <h2>Referencias</h2>
      <ul class="references">
        <li>
          Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
          <em>Numerical analysis</em> (10.ª ed.). Cengage Learning. (Capítulo 7: técnicas iterativas
          en álgebra matricial, donde se presentan los métodos de Jacobi y Gauss-Seidel con esta
          misma notación, junto con el teorema de convergencia basado en el radio espectral.)
        </li>
        <li>
          Chapra, S. C., &amp; Canale, R. P. (2015).
          <em>Métodos numéricos para ingenieros</em> (7.ª ed.). McGraw-Hill.
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
h3 {
  margin-top: var(--space-5);
}

ul,
ol {
  padding-left: var(--space-5);
}

li {
  margin-bottom: var(--space-2);
}

/* font-size fijo: KaTeX se dimensiona en em, y así las fórmulas en bloque
   conservan exactamente el tamaño que tenían antes de la escala tipográfica. */
.theory-formula {
  margin: var(--space-3) 0;
  font-size: 1rem;
}

.formula-legend {
  margin: calc(-1 * var(--space-1)) 0 var(--space-4);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

/* Fórmulas emparejadas (las matrices de iteración, o las componentes de un
   paso del ejemplo). El ancho mínimo es el mismo que usa el paso a paso de
   Resolver: por debajo, las sustituciones con fracción quedan cortadas. */
.formula-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(430px, 100%), 1fr));
  gap: var(--space-3);
}

.formula-pair .theory-formula {
  margin: 0;
}

/* Pasos del algoritmo: tarjetas numeradas que se recorren de un vistazo, en
   lugar de una lista de párrafos. */
.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr));
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: none;
}

.step {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-4);
  margin: 0;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  margin-bottom: var(--space-2);
}

.step-title {
  margin: 0 0 var(--space-1);
  font-size: var(--text-card-title);
  color: var(--color-ink);
}

.step-text {
  margin: 0;
  font-size: var(--text-small);
  line-height: 1.55;
  color: var(--color-ink-muted);
}

/* Las fórmulas en línea dentro de un paso no deben agrandar el interlineado. */
.step-text :deep(.katex) {
  font-size: 1em;
}

.worked-step {
  margin-bottom: var(--space-4);
}

.worked-step-title {
  margin: 0 0 var(--space-2);
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
}

.legend-prev {
  color: v-bind(PREVIOUS_COLOR);
  font-weight: var(--weight-semibold);
}

.legend-current {
  color: v-bind(CURRENT_COLOR);
  font-weight: var(--weight-semibold);
}

/* Tablas de texto: a diferencia de las de resultados numéricos, se alinean a
   la izquierda y dejan respirar el contenido. */
.comparison-table th,
.comparison-table td {
  text-align: left;
  vertical-align: top;
  padding: var(--space-3);
  line-height: 1.5;
}

.comparison-table tbody th {
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
  background: var(--color-sunken);
  white-space: nowrap;
}

.comparison-table td {
  font-size: var(--text-small);
}

.exact-row td {
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
}

/* Valores numéricos alineados a la derecha; las dos primeras columnas son
   etiquetas y se quedan a la izquierda. */
.numeric-table td:nth-child(n + 3),
.numeric-table th:nth-child(n + 3) {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.numeric-table tbody tr {
  background: transparent;
}

.group-start td {
  border-top: 2px solid var(--color-line);
}

.table-caption {
  margin: var(--space-5) 0 var(--space-2);
  color: var(--color-ink-muted);
}

.table-note {
  margin-top: var(--space-3);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.references {
  padding-left: var(--space-5);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.references li {
  margin-bottom: var(--space-3);
}

/* KaTeX inline trae 1.21em por defecto: se reduce para no alterar el
   interlineado de los párrafos. Las fórmulas en bloque conservan su tamaño. */
.theory :deep(.math:not(.math-display) .katex) {
  font-size: 1.05em;
}

/* En móvil las fórmulas de iteración (fracción + sumatorias) no caben a
   tamaño completo: se reducen un poco en vez de obligar a desplazarse. */
@media (max-width: 480px) {
  .theory-formula {
    padding: 10px;
  }

  .theory-formula :deep(.katex-display > .katex) {
    font-size: 0.8em;
  }
}
</style>
