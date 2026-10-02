<script setup>
// Teoría propia del método de Punto Fijo (iterativo secuencial): fórmula,
// variantes simultánea y secuencial, algoritmo, ejemplo resuelto y la
// comparación entre ambas variantes.
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import WorkedIterations from '../../../components/theory/WorkedIterations.vue'
import {
  ALGORITHM_STEPS,
  CURRENT_COLOR,
  ITERATIONS_TO_CONVERGE,
  PREVIOUS_COLOR,
  comparisonRows,
  formatNumber,
  tex,
  vectorLatex,
  workedSteps,
} from './content'
</script>

<template>
  <div id="metodo-punto-fijo" class="card">
    <h2>Método de Punto Fijo (iterativo secuencial)</h2>
    <h3 class="first-heading">Definición formal</h3>
    <p>
      Una vez reescrito el sistema como <MathFormula :expression="tex.fixedPointForm" />, cada
      componente de la nueva iteración se calcula evaluando su función
      <MathFormula :expression="tex.gi" />. En la variante <strong>secuencial</strong>, que es la
      que implementa esta aplicación, se reutilizan dentro de la misma iteración los valores que
      ya fueron actualizados:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.sequential" display-mode />
    </div>
    <p class="formula-legend">
      <span :style="{ color: CURRENT_COLOR }">■</span> valores ya recalculados en esta misma
      iteración · <span :style="{ color: PREVIOUS_COLOR }">■</span> valores de la iteración
      anterior
    </p>
    <p>
      Es decir, para calcular <MathFormula :expression="tex.xiNext" /> se usan los valores
      <MathFormula :expression="tex.before" /> ya recalculados en la iteración actual, y los
      valores <MathFormula :expression="tex.after" /> aún de la iteración anterior. Cada
      <MathFormula :expression="tex.gi" /> se obtiene despejando <MathFormula :expression="tex.xi" />
      de la ecuación <MathFormula :expression="tex.fi" />; como
      <MathFormula :expression="tex.gi" /> no contiene a <MathFormula :expression="tex.xi" />, la
      fórmula nunca necesita el valor que se está calculando.
    </p>

    <h3>Esquema simultáneo y esquema secuencial</h3>
    <p>
      Existe también una variante <strong>simultánea</strong>, en la que todas las componentes se
      actualizan con los valores de la iteración anterior completa:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.simultaneous" display-mode />
    </div>
    <p>
      La relación entre ambas es la misma que entre Jacobi y Gauss-Seidel: la simultánea es el
      análogo de Jacobi y la secuencial, el de Gauss-Seidel. Cerca de la solución, el error de
      cada variante se comporta como el de una iteración lineal: la simultánea con la matriz
      <MathFormula :expression="tex.simultaneousMatrix" />, y la secuencial con
      <MathFormula :expression="tex.sequentialMatrix" />, donde
      <MathFormula :expression="tex.splitting" /> separa la jacobiana en su parte estrictamente
      triangular inferior y el resto, igual que la descomposición
      <MathFormula expression="A = D + L + U" /> de los métodos lineales. Usar los valores nuevos
      en cuanto están disponibles suele reducir el radio espectral, y con él el número de
      iteraciones; por eso esta aplicación implementa la variante secuencial.
    </p>

    <h3>Restricciones en esta aplicación</h3>
    <ul>
      <li>
        El sistema tiene entre 2 y 6 ecuaciones. La ecuación <MathFormula expression="i" /> se
        despeja automáticamente para la incógnita <MathFormula :expression="tex.xi" />, así que
        <strong>el orden de las ecuaciones importa</strong>: cambiarlo cambia la función
        <MathFormula :expression="tex.G" /> que se itera.
      </li>
      <li>
        El despeje debe ser único y real. Se rechaza la ecuación si no tiene despeje, si sólo
        tiene despejes complejos o si tiene varios despejes reales (por ejemplo,
        <MathFormula expression="x^2 = y" /> da <MathFormula expression="x = \pm\sqrt{y}" />).
        Tampoco se intenta despejar una variable que aparezca con grado mayor que 4.
      </li>
      <li>
        Si durante la iteración algún valor deja de ser un número real finito (la raíz de un
        número negativo, el logaritmo de cero, un desbordamiento), el método se detiene y se
        reporta como no convergente.
      </li>
    </ul>

    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps class="five-steps" :steps="ALGORITHM_STEPS['punto-fijo']" />

    <h3 id="ejemplo-punto-fijo">Ejemplo resuelto</h3>
    <p>
      Resolvamos el sistema
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleSystem" display-mode />
    </div>
    <p>
      partiendo de <MathFormula :expression="tex.exampleStart" />. Cada ecuación es lineal en la
      incógnita que se despeja de ella (<MathFormula expression="x" /> en la primera,
      <MathFormula expression="y" /> en la segunda), así que el despeje es directo:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleG" display-mode />
    </div>
    <p>
      En cada iteración se calcula primero <MathFormula expression="x" /> con el valor de
      <MathFormula expression="y" /> de la iteración <span class="legend-prev">anterior</span>, y
      después <MathFormula expression="y" /> con el valor de <MathFormula expression="x" />
      <span class="legend-current">recién calculado</span>:
    </p>

    <WorkedIterations :steps="workedSteps" />

    <p>
      Tras tres iteraciones se llega a
      <MathFormula :expression="vectorLatex('x^{(3)}', workedSteps[2].x)" />, con un error de
      <MathFormula :expression="formatNumber(workedSteps[2].error)" />; la solución es
      <MathFormula :expression="tex.exampleSolution" />. La convergencia está asegurada porque
      la jacobiana de <MathFormula :expression="tex.G" />,
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleJacobian" display-mode />
    </div>
    <p>
      tiene en la solución <MathFormula :expression="tex.exampleJacobianNorm" />. Los radios
      espectrales de las dos variantes son <MathFormula :expression="tex.rhoSimultaneous" /> y
      <MathFormula :expression="tex.rhoSequential" />: la secuencial reduce el error unas cuatro
      veces más por iteración, y por eso necesita {{ ITERATIONS_TO_CONVERGE.sequential }}
      iteraciones para alcanzar una tolerancia de <MathFormula expression="10^{-6}" />, frente a
      las {{ ITERATIONS_TO_CONVERGE.simultaneous }} de la simultánea.
    </p>

    <h4 class="table-caption">Comparación iteración a iteración</h4>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Iteración</th>
            <th>Esquema</th>
            <th><MathFormula expression="x" /></th>
            <th><MathFormula expression="y" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in comparisonRows" :key="row.key" :class="{ 'group-start': row.first }">
            <td>{{ row.first ? row.iteration : '' }}</td>
            <td>{{ row.scheme }}</td>
            <td v-for="(value, i) in row.x" :key="i">{{ formatNumber(value) }}</td>
          </tr>
          <tr class="exact-row group-start">
            <td></td>
            <td>Solución</td>
            <td>0.403642</td>
            <td>0.459268</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Es el ejemplo <strong>Algebraico 2x2</strong> de la vista <strong>Resolver</strong>: puedes
      cargarlo para verlo converger hasta el final y desplegar el despeje paso a paso de cada
      ecuación.
    </p>
  </div>

  <div class="card">
    <h2>Esquema simultáneo frente a secuencial</h2>
    <p>
      Ambas variantes iteran la misma función <MathFormula :expression="tex.G" /> y tienen los
      mismos puntos fijos, pero se comportan de forma distinta en tres aspectos prácticos:
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Criterio</th>
            <th>Simultáneo</th>
            <th>Secuencial</th>
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
              Generalmente converge en menos iteraciones, porque aprovecha los valores
              actualizados de inmediato. En el ejemplo de arriba, el radio espectral pasa de
              0.248583 a 0.061793 y las iteraciones, de {{ ITERATIONS_TO_CONVERGE.simultaneous }} a
              {{ ITERATIONS_TO_CONVERGE.sequential }}.
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
              completa, sólo el valor previo de la componente que se está sustituyendo (para
              medir el error).
            </td>
          </tr>
          <tr>
            <th scope="row">Paralelización</th>
            <td>
              Trivialmente paralelizable: dentro de una iteración, cada
              <MathFormula :expression="tex.gi" /> se evalúa con los mismos datos y todas pueden
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
      En resumen: la variante secuencial suele ser preferible en un cálculo secuencial, mientras
      que la simultánea resulta atractiva cuando se dispone de varios procesadores o cuando cada
      <MathFormula :expression="tex.gi" /> es costosa de evaluar.
    </p>
  </div>
</template>

<style scoped>
/* Cinco pasos (uno más que Jacobi y Gauss-Seidel): columnas algo más
   angostas para que quepan en una sola fila en escritorio en lugar de dejar
   el último solo en la segunda. En pantallas angostas siguen apilándose. */
.steps.five-steps {
  grid-template-columns: repeat(auto-fit, minmax(min(175px, 100%), 1fr));
}
</style>
