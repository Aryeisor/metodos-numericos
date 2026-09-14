<script setup>
import MathFormula from '../components/MathFormula.vue'
import {
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  errorFormulaLatex,
  generalFormulaLatex,
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
}
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
    </div>

    <div class="card">
      <h2>Método de Jacobi</h2>
      <p><strong>Definición formal:</strong></p>
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
      <p><strong>Algoritmo de aplicación:</strong></p>
      <ol>
        <li>
          Elegir un vector inicial <MathFormula :expression="tex.x0" /> (por defecto, ceros) y una
          tolerancia <MathFormula :expression="tex.eps" />.
        </li>
        <li>
          Para cada iteración <MathFormula :expression="tex.kRange" />, calcular
          <MathFormula :expression="tex.xiNext" /> para todo <MathFormula expression="i" /> usando la
          fórmula anterior, a partir de <MathFormula :expression="tex.xCurrent" />.
        </li>
        <li>
          Calcular el error como la norma infinito entre iteraciones sucesivas:
          <div class="formula-box theory-formula">
            <MathFormula :expression="tex.error" display-mode />
          </div>
        </li>
        <li>
          Detener el proceso cuando el error sea menor que
          <MathFormula :expression="tex.eps" /> <em>y</em> se hayan ejecutado al menos 6
          iteraciones, o al alcanzar el número máximo de iteraciones configurado.
        </li>
      </ol>
    </div>

    <div class="card">
      <h2>Método de Gauss-Seidel</h2>
      <p><strong>Definición formal:</strong></p>
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
      <p><strong>Algoritmo de aplicación:</strong></p>
      <ol>
        <li>
          Elegir un vector inicial <MathFormula :expression="tex.x0" /> (por defecto, ceros) y una
          tolerancia <MathFormula :expression="tex.eps" />.
        </li>
        <li>
          Para cada iteración <MathFormula expression="k" />, recorrer
          <MathFormula :expression="tex.iRange" /> actualizando
          <MathFormula :expression="tex.xi" /> <em>in situ</em>, usando los valores ya actualizados de la propia iteración para
          <MathFormula :expression="tex.jBefore" />.
        </li>
        <li>
          Calcular el error como la norma infinito entre <MathFormula :expression="tex.xNext" /> y
          <MathFormula :expression="tex.xCurrent" />.
        </li>
        <li>
          Detener el proceso cuando el error sea menor que
          <MathFormula :expression="tex.eps" /> <em>y</em> se hayan ejecutado al menos 6
          iteraciones, o al alcanzar el número máximo de iteraciones configurado.
        </li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
h3 {
  margin-top: 18px;
}

ul,
ol {
  padding-left: 22px;
}

li {
  margin-bottom: 6px;
}

.theory-formula {
  margin: 10px 0;
}

.formula-legend {
  margin: -2px 0 12px;
  font-size: 0.78rem;
  color: var(--color-text-muted);
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
    font-size: 0.85em;
  }
}
</style>
