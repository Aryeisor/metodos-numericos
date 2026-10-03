<script setup>
// Teoría propia del método de Newton para sistemas no lineales: de dónde sale
// (forma escalar y relación con el punto fijo), regla de Cramer para el
// sistema lineal de cada iteración, convergencia cuadrática, restricciones,
// algoritmo, ejemplo resuelto y comparación con Punto Fijo.
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import WorkedIterations from '../../../components/theory/WorkedIterations.vue'
import { theoryRouteName } from '../../routeNames'
import {
  ALGEBRAIC_AFTER_4,
  ALGORITHM_STEPS,
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  convergenceRows,
  exampleEntries,
  formatNumber,
  scalarNewtonIterates,
  tex,
  workedSteps,
} from './newtonContent'
</script>

<template>
  <div id="metodo-newton" class="card">
    <h2>Método de Newton</h2>
    <h3 class="first-heading">De dónde sale el método</h3>
    <p>
      Para una sola ecuación <MathFormula expression="f(x) = 0" />, Newton reemplaza la curva por
      su recta tangente en el punto actual, <MathFormula :expression="tex.tangent" />, y toma como
      nueva aproximación el punto donde esa recta corta el eje:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.scalarNewton" display-mode />
    </div>
    <p>
      Visto desde el fundamento común, esto es una iteración de punto fijo
      <MathFormula expression="x = g(x)" /> con un despeje muy particular,
      <MathFormula :expression="tex.scalarAsFixedPoint" />: en lugar de una
      <MathFormula expression="g" /> fija elegida a mano, el factor de corrección
      <MathFormula expression="1/f'(x)" /> se recalcula en cada paso con la derivada. Su gracia
      está en la derivada de <MathFormula expression="g" /> en la raíz:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.scalarDerivative" display-mode />
    </div>
    <p>
      siempre que <MathFormula :expression="tex.fPrimeNonzero" />. Es el caso extremo de la
      condición de contracción: no sólo <MathFormula expression="|g'(p)| < 1" />, sino
      <MathFormula expression="g'(p) = 0" />. Aplicado a la ecuación
      <MathFormula :expression="tex.scalarEquation" /> del ejemplo escalar de más arriba, con el
      mismo punto de partida <MathFormula :expression="tex.scalarStart" />:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table newton-scalar-table">
        <thead>
          <tr>
            <th>Despeje</th>
            <th><MathFormula expression="\left| g'(2) \right|" /></th>
            <th><MathFormula expression="x^{(1)}" /></th>
            <th><MathFormula expression="x^{(2)}" /></th>
            <th><MathFormula expression="x^{(3)}" /></th>
            <th><MathFormula expression="x^{(4)}" /></th>
            <th>Resultado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><MathFormula :expression="tex.scalarNewtonExample" /></td>
            <td><MathFormula expression="0" /></td>
            <td v-for="(value, i) in scalarNewtonIterates" :key="i">{{ value }}</td>
            <td>Converge cuadráticamente</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Frente a <MathFormula expression="g_b" /> (derivada <MathFormula expression="\tfrac{1}{4}" />),
      que tras cuatro iteraciones seguía en 1.99796, el despeje de Newton ya acierta en diez
      cifras.
    </p>

    <h3>Generalización a sistemas</h3>
    <p>
      Para el sistema <MathFormula :expression="tex.system" />, con
      <MathFormula :expression="tex.vectorMap" />, la derivada
      <MathFormula expression="f'(x)" /> se convierte en la <strong>matriz Jacobiana</strong>,
      que reúne las derivadas parciales de cada función respecto a cada variable:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.jacobianDefinition" display-mode />
    </div>
    <p>y dividir entre la derivada pasa a ser multiplicar por la inversa de la Jacobiana:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.inverseForm" display-mode />
    </div>
    <p>
      Igual que en el caso escalar, es una iteración de punto fijo con
      <MathFormula :expression="tex.newtonG" />, y cuando la Jacobiana es no singular en la
      solución se cumple <MathFormula :expression="tex.newtonJG" />: el radio espectral que
      gobierna la convergencia según el fundamento común es <MathFormula :expression="tex.rhoZero" />.
    </p>
    <p>
      En la práctica <strong>no se invierte la Jacobiana</strong>: calcular una inversa cuesta
      más y es menos preciso que resolver un sistema lineal. Se plantea el sistema y se suma la
      corrección, que es exactamente lo que muestra el detalle de cada iteración en Resolver:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.practicalForm" display-mode />
    </div>
    <p class="formula-legend">
      <span :style="{ color: PREVIOUS_COLOR }">■</span> punto de la iteración anterior
    </p>

    <h3>El sistema lineal de cada iteración: regla de Cramer</h3>
    <p>
      En cada iteración hay que resolver un sistema lineal <MathFormula expression="n \times n" />.
      Muchos textos lo hacen por eliminación gaussiana; en esta aplicación, siguiendo el
      procedimiento enseñado en clase, se resuelve por la <strong>regla de Cramer</strong>.
      Con <MathFormula :expression="tex.Ji" /> la Jacobiana evaluada con su columna
      <MathFormula expression="i" /> reemplazada por <MathFormula :expression="tex.minusF" />:
    </p>
    <div class="formula-pair">
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.determinant" display-mode />
      </div>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.columnDeterminant" display-mode />
      </div>
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.increment" display-mode />
    </div>
    <p>
      La regla exige <MathFormula :expression="tex.nonSingular" />: si la Jacobiana es singular
      en el punto actual, el sistema no tiene solución única y el método no puede continuar
      desde ahí. Para los sistemas de este curso (2 a 4 incógnitas) calcular los
      <MathFormula expression="n + 1" /> determinantes es inmediato; su costo crece muy rápido
      con <MathFormula expression="n" />, por eso para sistemas grandes se prefiere la
      eliminación gaussiana.
    </p>

    <h3>Convergencia cuadrática</h3>
    <p>
      Punto Fijo converge <strong>linealmente</strong>: cada iteración reduce el error en una
      proporción aproximadamente fija <MathFormula :expression="tex.K" />,
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.linear" display-mode />
    </div>
    <p>
      y si <MathFormula :expression="tex.K" /> está cerca de 1 avanza despacio. Newton, cuando
      <MathFormula :expression="tex.jacobianAtRoot" /> es no singular, converge
      <strong>cuadráticamente</strong> cerca de la solución: el error nuevo es proporcional al
      <em>cuadrado</em> del anterior,
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.quadratic" display-mode />
    </div>
    <p>
      En la práctica, el número de cifras correctas se <strong>duplica aproximadamente en cada
      iteración</strong>: un error de <MathFormula expression="10^{-3}" /> pasa a ser del orden de
      <MathFormula expression="10^{-6}" /> y luego de <MathFormula expression="10^{-12}" />. Se
      ve en el ejemplo resuelto más abajo (tabla de convergencia).
    </p>
    <p>
      Igual que en Punto Fijo, esta rapidez es <strong>local</strong>. Si
      <MathFormula expression="x^{(0)}" /> está lejos de la raíz, las tangentes pueden alejar a
      la iteración en lugar de acercarla, llevarla hacia otra solución, o pasar por un punto
      donde la Jacobiana es singular (<MathFormula expression="D = 0" />) y el método se detiene.
    </p>

    <h3>Requisitos y restricciones en esta aplicación</h3>
    <ul>
      <li>
        <MathFormula expression="F" /> debe ser <strong>diferenciable</strong>: cada
        <MathFormula expression="f_i" /> necesita sus derivadas parciales respecto a todas las
        variables. La aplicación las calcula automáticamente, término a término.
      </li>
      <li>
        <strong>No hay que despejar nada.</strong> A diferencia de Punto Fijo, las ecuaciones se
        usan tal como se escriben (<MathFormula expression="\text{lhs} = \text{rhs}" /> equivale a
        <MathFormula expression="f = \text{lhs} - \text{rhs} = 0" />), y las variables se
        declaran aparte, en orden: ese orden fija las columnas de la Jacobiana y el de
        <MathFormula expression="x^{(0)}" />.
      </li>
      <li>
        La Jacobiana no puede ser singular en ninguna iteración. Si
        <MathFormula expression="D = 0" /> (o prácticamente cero) en algún paso, el método se
        detiene y se reporta como no convergente, con una advertencia. Por la misma razón se
        rechaza de entrada una variable que no aparece en ninguna ecuación: su columna de la
        Jacobiana sería de ceros.
      </li>
      <li>
        El sistema tiene entre 2 y 6 ecuaciones, tantas como variables. Si algún valor deja de
        ser un número real finito (la raíz de un negativo, el logaritmo de cero, un
        desbordamiento), el método también se detiene.
      </li>
    </ul>

    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS.newton" />

    <h3 id="ejemplo-newton">Ejemplo resuelto</h3>
    <p>Resolvamos, desde <MathFormula :expression="tex.exampleStart" />, el sistema</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleSystem" display-mode />
    </div>
    <p>
      cuya solución es <MathFormula :expression="tex.exampleSolution" />.
      <strong>Paso 1</strong>, una sola vez: escribir <MathFormula expression="F(x)" /> y derivar
      cada entrada de la Jacobiana término a término.
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleF" display-mode />
    </div>
    <div class="formula-pair">
      <div v-for="entry in exampleEntries" :key="entry.key" class="formula-box partial-card">
        <p class="partial-title"><MathFormula :expression="entry.title" /></p>
        <ul class="partial-terms">
          <li v-for="(term, t) in entry.terms" :key="t">
            <div class="partial-formula"><MathFormula :expression="term.latex" /></div>
            <span class="partial-rule">{{ term.rule }}</span>
          </li>
        </ul>
        <div v-if="entry.sum_latex" class="partial-sum">
          <MathFormula :expression="entry.sum_latex" />
        </div>
      </div>
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleJ" display-mode />
    </div>
    <p>
      Con la Jacobiana ya armada, cada iteración sustituye el punto actual, plantea el sistema
      lineal y lo resuelve por Cramer. Los valores
      <span class="legend-prev">de la iteración anterior</span> van en azul y la
      <span class="legend-current">columna reemplazada por −F</span>, en verde:
    </p>

    <WorkedIterations :steps="workedSteps" />

    <h4 class="table-caption">Convergencia iteración a iteración</h4>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Iteración</th>
            <th></th>
            <th><MathFormula expression="x" /></th>
            <th><MathFormula expression="y" /></th>
            <th>Distancia a <MathFormula expression="p" /></th>
            <th>Cifras correctas</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in convergenceRows" :key="row.iteration">
            <td>{{ row.iteration }}</td>
            <td></td>
            <td>{{ formatNumber(row.x) }}</td>
            <td>{{ formatNumber(row.y) }}</td>
            <td><MathFormula :expression="row.distance" /></td>
            <td>{{ row.digits }}</td>
          </tr>
          <tr class="exact-row group-start">
            <td></td>
            <td>Solución</td>
            <td>2</td>
            <td>3</td>
            <td></td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Las cifras correctas pasan de 1 a 3, a 6 y a 13: se duplican en cada iteración, que es la
      convergencia cuadrática. Es el ejemplo <strong>Clásico 2x2 (Chapra)</strong> de la vista
      <strong>Resolver</strong>: puedes cargarlo y desplegar cada iteración para ver el mismo
      paso a paso.
    </p>
  </div>

  <div class="card">
    <h2>Punto Fijo frente a Newton</h2>
    <p>
      Los dos métodos de la categoría resuelven el mismo problema
      <MathFormula :expression="tex.system" /> y comparten el fundamento común, pero difieren en
      cuatro aspectos prácticos:
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Criterio</th>
            <th>
              <RouterLink :to="{ name: theoryRouteName('punto-fijo') }">Punto Fijo</RouterLink>
            </th>
            <th>Newton</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Velocidad de convergencia</th>
            <td>
              Lineal: cada iteración reduce el error en una proporción fija, que depende del
              radio espectral de <MathFormula expression="J_G" /> en la solución.
            </td>
            <td>
              Cuadrática cerca de la solución: las cifras correctas se duplican en cada iteración.
              Con el mismo sistema algebraico y el mismo punto de partida, tras 4 iteraciones la
              distancia a la solución es <MathFormula :expression="ALGEBRAIC_AFTER_4.fixedPoint" />
              con Punto Fijo y <MathFormula :expression="ALGEBRAIC_AFTER_4.newton" /> con Newton.
            </td>
          </tr>
          <tr>
            <th scope="row">Qué necesita de entrada</th>
            <td>
              Reescribir el sistema como <MathFormula expression="x = G(x)" />. La aplicación
              despeja cada ecuación para su variable, y sólo acepta despejes únicos y reales; la
              convergencia depende de qué despeje resulte.
            </td>
            <td>
              Sólo <MathFormula :expression="tex.system" />, tal como se escribe, y el orden de las
              variables. No hay que despejar nada.
            </td>
          </tr>
          <tr>
            <th scope="row">Costo por iteración</th>
            <td>
              Bajo: evaluar las <MathFormula expression="n" /> funciones
              <MathFormula expression="g_i" />.
            </td>
            <td>
              Mayor: evaluar <MathFormula expression="F" /> (<MathFormula expression="n" />
              funciones) y <MathFormula expression="J" /> (<MathFormula expression="n^2" />
              derivadas), y resolver un sistema lineal; con Cramer,
              <MathFormula expression="n + 1" /> determinantes.
            </td>
          </tr>
          <tr>
            <th scope="row">Robustez frente al punto inicial</th>
            <td>
              Local. Converge desde cualquier punto de una región donde
              <MathFormula expression="G" /> sea contracción, pero puede no converger nunca si el
              despeje no lo es, aunque el punto inicial sea bueno.
            </td>
            <td>
              Local. Desde un punto cercano a la raíz converge muy rápido; desde uno lejano puede
              diverger, y se detiene si la Jacobiana se vuelve singular en el camino.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      En resumen: Newton suele ser preferible cuando se dispone de un punto inicial razonable,
      porque necesita muchas menos iteraciones y no exige despejar; Punto Fijo resulta atractivo
      cuando hay un despeje natural que es contracción, porque cada iteración es más barata y no
      depende de que la Jacobiana sea no singular.
    </p>
  </div>
</template>

<style scoped>
/* Despeje (fórmula) y resultado (texto) a la izquierda; los iterados, a la
   derecha, como en la tabla del ejemplo escalar del fundamento común. */
.newton-scalar-table.numeric-table td:last-child,
.newton-scalar-table.numeric-table th:last-child {
  text-align: left;
}

/* Derivación de cada entrada de la Jacobiana: misma presentación que la
   sección «Sistema y matriz Jacobiana» de Resolver. */
.partial-card {
  min-width: 0;
}

.partial-title {
  margin: 0 0 var(--space-2);
}

.partial-terms {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.partial-formula {
  overflow-x: auto;
}

.partial-rule {
  display: block;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.partial-sum {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-line);
  font-weight: var(--weight-semibold);
  overflow-x: auto;
}

.formula-pair + .formula-box {
  margin-top: var(--space-3);
}
</style>
