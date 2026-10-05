<script setup>
// Teoría propia del método de Bairstow: definición formal (división entre
// x² − r·x − s, recurrencias de los b y los c, sistema 2×2 por Cramer),
// derivación de las fórmulas (las derivadas parciales son los c), convergencia,
// restricciones, algoritmo, el ejemplo de Chapra resuelto con datos reales del
// solver y la comparación con Newton-Raphson y con Newton para sistemas.
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName, theoryRouteName } from '../../routeNames'
import SyntheticTable from '../SyntheticTable.vue'
import {
  ALGORITHM_STEPS,
  FIRST_FACTOR,
  SECOND_FACTOR,
  example,
  factorization,
  firstClosure,
  firstIteration,
  firstMetIteration,
  iterationRows,
  rootRows,
  secondClosure,
  tex,
  thirdClosure,
} from './content'
</script>

<template>
  <div id="metodo-bairstow" class="card">
    <h2>Método de Bairstow</h2>

    <!-- 2. Definición formal -->
    <h3 class="first-heading">Definición formal</h3>
    <p>Dado el polinomio</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.polynomial" display-mode />
    </div>
    <p>
      al dividirlo entre el factor cuadrático <MathFormula :expression="tex.factor" /> se obtiene
      un cociente de grado <MathFormula expression="n - 2" />, con coeficientes
      <MathFormula expression="b_n, \dots, b_2" />, y un residuo de grado a lo sumo 1, que se
      escribe en la forma <MathFormula :expression="tex.residue" />:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.division" display-mode />
    </div>
    <p>El residuo se anula sólo si sus dos coeficientes son cero, así que</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exactFactor" display-mode />
    </div>
    <p>
      Cada <MathFormula expression="b_i" /> depende de <MathFormula expression="r" /> y
      <MathFormula expression="s" />. El objetivo del método es encontrar los
      <MathFormula expression="r" /> y <MathFormula expression="s" /> que cumplen
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.goal" display-mode />
    </div>
    <p>
      un <strong>sistema no lineal de dos ecuaciones con dos incógnitas</strong>, que se resuelve
      con el
      <RouterLink :to="{ name: theoryRouteName('newton') }">método de Newton</RouterLink>. El método
      se apoya en tres grupos de fórmulas, con el índice de cada coeficiente igual a la potencia
      de <MathFormula expression="x" /> que acompaña.
    </p>

    <p><strong>Coeficientes b</strong> (división del polinomio entre el factor):</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.bRecurrence" display-mode />
    </div>
    <p>
      <strong>Coeficientes c</strong> (la misma división, aplicada ahora a los
      <MathFormula expression="b" />):
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.cRecurrence" display-mode />
    </div>

    <p>
      <strong>Sistema, solución, actualización y error.</strong> En cada iteración se plantea el
      sistema lineal
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.system" display-mode />
    </div>
    <p>y se resuelve por la <strong>regla de Cramer</strong>, igual que en Resolver:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.determinant" display-mode />
    </div>
    <div class="formula-pair">
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.determinantR" display-mode />
      </div>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.determinantS" display-mode />
      </div>
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.increments" display-mode />
    </div>
    <p>Después se actualizan los valores y se mide el error relativo porcentual de cada uno:</p>
    <div class="formula-pair">
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.update" display-mode />
      </div>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.errors" display-mode />
      </div>
    </div>
    <p class="formula-legend">
      Los errores se calculan con los valores <strong>ya actualizados</strong> de
      <MathFormula expression="r" /> y <MathFormula expression="s" />. La tolerancia, también en %,
      se escribe <MathFormula expression="\varepsilon_{\text{s}}" /> (con «s» de
      <em>stopping</em>, como en Chapra): no debe confundirse con
      <MathFormula expression="\varepsilon_s" />, el error de <MathFormula expression="s" />.
    </p>

    <p>
      <strong>Raíces del factor.</strong> Cuando <MathFormula expression="r" /> y
      <MathFormula expression="s" /> convergen, las dos raíces del factor salen de
      <MathFormula :expression="tex.factor + ' = 0'" />:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.factorRoots" display-mode />
    </div>
    <p>y el discriminante <MathFormula :expression="tex.discriminant" /> decide su tipo:</p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Caso</th>
            <th>Raíces</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row"><MathFormula expression="\Delta > 0" /></th>
            <td>
              Dos raíces reales distintas,
              <MathFormula expression="x = \frac{r \pm \sqrt{\Delta}}{2}" />.
            </td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="\Delta = 0" /></th>
            <td>Una raíz real doble, <MathFormula expression="x = \frac{r}{2}" />.</td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="\Delta < 0" /></th>
            <td>
              Un par complejo conjugado, con parte real
              <MathFormula expression="\frac{r}{2}" /> y parte imaginaria
              <MathFormula expression="\pm\frac{\sqrt{-\Delta}}{2}" />. Las dos partes se calculan
              por separado, con números reales: no hace falta aritmética compleja.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 3. Derivación -->
    <h3>Derivación: de dónde salen las fórmulas</h3>

    <p>
      <strong>a) La recurrencia de los b.</strong> Al desarrollar el lado derecho de la división
      e igualar el coeficiente de cada potencia de <MathFormula expression="x" /> con el de
      <MathFormula expression="f(x)" />, empezando por la más alta:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.matching" display-mode />
    </div>
    <p>y, en general, despejando <MathFormula expression="b_i" />:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.matchI" display-mode />
    </div>
    <p>
      Escribir el residuo como <MathFormula :expression="tex.residue" />, y no como
      <MathFormula expression="b_1 x + b_0" />, es lo que hace que la misma recurrencia valga
      también para <MathFormula expression="b_1" /> y <MathFormula expression="b_0" />, sin casos
      especiales al final.
    </p>

    <p>
      <strong>b) División sintética y fórmulas son lo mismo.</strong> La recurrencia de los
      <MathFormula expression="b" /> es exactamente la <strong>división sintética por un factor
      cuadrático</strong>, que se organiza en una tabla de cuatro filas, con una columna por
      potencia:
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Fila</th>
            <th>Contenido</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">1</th>
            <td>Los coeficientes <MathFormula expression="a_i" /> del polinomio.</td>
          </tr>
          <tr>
            <th scope="row">2</th>
            <td>
              <MathFormula expression="r\, b_{i+1}" />: <MathFormula expression="r" /> por el
              resultado de la columna anterior.
            </td>
          </tr>
          <tr>
            <th scope="row">3</th>
            <td>
              <MathFormula expression="s\, b_{i+2}" />: <MathFormula expression="s" /> por el
              resultado de dos columnas atrás.
            </td>
          </tr>
          <tr>
            <th scope="row">4</th>
            <td>
              <MathFormula expression="b_i" />: la suma de la columna.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="alert alert-info theory-note">
      <p>
        Las fórmulas y la tabla dan <strong>exactamente los mismos números</strong> y, por lo
        tanto, las mismas iteraciones: la tabla es sólo la forma cómoda de hacer la cuenta a
        mano. Los <MathFormula expression="c" /> se obtienen con una segunda tabla igual, que
        tiene los <MathFormula expression="b" /> en la primera fila.
      </p>
      <p>
        <strong>Cuidado:</strong> la división de Ruffini por un solo número (una sola fila de
        productos, para dividir entre <MathFormula expression="x - a" />) <strong>no</strong> es la
        división de Bairstow. Dividir entre <MathFormula :expression="tex.factor" /> lleva siempre
        las dos filas, la de <MathFormula expression="r" /> y la de <MathFormula expression="s" />.
      </p>
    </div>

    <p>
      <strong>c) Newton sobre (r, s).</strong> Para resolver
      <MathFormula expression="b_1(r, s) = 0" />, <MathFormula expression="b_0(r, s) = 0" />, se
      linealizan <MathFormula expression="b_1" /> y <MathFormula expression="b_0" /> alrededor
      del punto actual y se busca el incremento <MathFormula expression="(\Delta r, \Delta s)" />
      que anula esa aproximación lineal:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.linearization" display-mode />
    </div>

    <p>
      <strong>d) El resultado de Bairstow: las derivadas parciales son los c.</strong> Hacen falta
      las derivadas de <MathFormula expression="b_1" /> y <MathFormula expression="b_0" />, pero
      cada <MathFormula expression="b_i" /> depende de los anteriores. Derivando la recurrencia
      de los <MathFormula expression="b" /> respecto de <MathFormula expression="r" />:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.partialR" display-mode />
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.partialRStart" display-mode />
    </div>
    <p>
      Es la misma recurrencia de los <MathFormula expression="c" />, desplazada un lugar. Por lo
      tanto <MathFormula :expression="tex.partialRResult" />. Respecto de
      <MathFormula expression="s" /> ocurre lo mismo, con un desplazamiento de dos lugares:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.partialS" display-mode />
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.partialSStart" display-mode />
    </div>
    <p>de modo que <MathFormula :expression="tex.partialSResult" />. Para el sistema:</p>
    <div class="table-scroll">
      <table class="comparison-table derivatives-table">
        <thead>
          <tr>
            <th>Derivada</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row"><MathFormula expression="\partial b_0 / \partial r" /></th>
            <td><MathFormula expression="c_1" /></td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="\partial b_0 / \partial s" /></th>
            <td><MathFormula expression="c_2" /></td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="\partial b_1 / \partial r" /></th>
            <td><MathFormula expression="c_2" /></td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="\partial b_1 / \partial s" /></th>
            <td><MathFormula expression="c_3" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p>
      Sustituyendo estos valores en la linealización se obtiene el sistema de la definición,
      <MathFormula expression="c_2 \Delta r + c_3 \Delta s = -b_1" />,
      <MathFormula expression="c_1 \Delta r + c_2 \Delta s = -b_0" />. El subíndice más pequeño
      que aparece es <MathFormula expression="c_1" />: por eso <strong><MathFormula
      expression="c_0" /> no se calcula</strong>, ni aquí ni en Resolver.
    </p>

    <p><strong>e) Relación con Newton para sistemas.</strong> La matriz de coeficientes es la</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.jacobian" display-mode />
    </div>
    <p>
      <strong>Jacobiana</strong> del sistema <MathFormula expression="(b_1, b_0)" /> respecto de
      <MathFormula expression="(r, s)" />, y el sistema de cada iteración es exactamente
      <MathFormula :expression="tex.newtonForm" />, el paso del
      <RouterLink :to="{ name: theoryRouteName('newton') }">método de Newton para sistemas</RouterLink>
      con dos variables. La ventaja de Bairstow es que la Jacobiana sale de una
      <strong>segunda división sintética</strong>, sin derivar simbólicamente nada.
    </p>

    <!-- 4. Convergencia -->
    <h3>Condición de convergencia</h3>
    <ul>
      <li>
        <strong>Convergencia cuadrática cerca de un factor exacto con raíces simples.</strong> Como
        es el método de Newton, el error nuevo es proporcional al cuadrado del anterior,
        <MathFormula :expression="tex.quadratic" />, y el número de cifras correctas
        aproximadamente se duplica en cada iteración. En el ejemplo resuelto,
        <MathFormula expression="\varepsilon_r" /> pasa de 2.29 % a 0.063 %, a
        <MathFormula expression="1.3 \times 10^{-5}" /> % y a
        <MathFormula expression="2.2 \times 10^{-12}" /> %.
      </li>
      <li>
        <strong>Depende de <MathFormula expression="r_0" /> y <MathFormula expression="s_0" />.</strong>
        La convergencia es local: si los valores iniciales están lejos de un factor, el método puede
        tardar muchas iteraciones, oscilar o divergir, y el factor que encuentra depende del punto
        de partida.
      </li>
      <li>
        <strong>Sistema singular.</strong> Si <MathFormula expression="D = c_2^2 - c_1 c_3 \approx 0" />,
        el sistema no tiene solución única y el método falla en esa iteración. Un caso real de
        Resolver: para <MathFormula :expression="tex.singularStart" />, desde
        <MathFormula expression="r_0 = s_0 = -1" /> la primera iteración lleva a
        <MathFormula expression="r = s = 0" />, y ahí
        <MathFormula :expression="tex.singularStep" />. Por eso su ejemplo en Resolver usa
        <MathFormula expression="r_0 = 0.5" /> y <MathFormula expression="s_0 = -0.5" />.
      </li>
      <li>
        <strong>Raíces múltiples o muy cercanas.</strong> La Jacobiana tiende a ser singular en la
        solución y la convergencia se vuelve lenta (lineal).
      </li>
      <li>
        <strong>Criterio de parada.</strong> Un factor se da por encontrado cuando
        <MathFormula :expression="tex.stop" />, con un <strong>mínimo de 6 iteraciones</strong> por
        factor y un máximo configurable, igual que en Resolver. Si se alcanza el máximo sin cumplir
        la tolerancia, el método se reporta como no convergente.
      </li>
    </ul>

    <!-- 5. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <ul>
      <li>
        <strong>Aplicabilidad:</strong> sólo polinomios con coeficientes reales y con coeficiente
        principal <MathFormula expression="a_n \neq 0" />. En esta aplicación, de grado 3 a 10 (los
        de grado 1 y 2 se resuelven directamente).
      </li>
      <li>
        <strong>Coeficientes faltantes.</strong> Las potencias que no aparecen deben escribirse con
        coeficiente 0, por ejemplo <MathFormula :expression="tex.missingCoefficients" />. Olvidarlo
        corre las columnas de la tabla y es el error más común al hacerlo a mano. En el modo texto,
        la aplicación completa los ceros sola.
      </li>
      <li>
        <strong>Raíces nulas.</strong> Si <MathFormula expression="a_0 = 0" />, primero se
        factoriza <MathFormula :expression="tex.zeroRoots" />. La aplicación lo hace como paso
        previo, antes de iterar.
      </li>
      <li>
        <strong>Valores iniciales.</strong> Sin información previa se suele usar
        <MathFormula expression="r_0 = s_0 = -1" />, el valor por defecto de Resolver. Si el
        método no converge, se prueban otros valores.
      </li>
      <li>
        <strong>Error relativo con r o s cercanos a 0.</strong> Si el valor nuevo es prácticamente
        cero, el error relativo no está definido y se usa el error absoluto
        <MathFormula expression="|\Delta r|" /> o <MathFormula expression="|\Delta s|" />, como hace
        Resolver con una advertencia. Ocurre, por ejemplo, con el factor
        <MathFormula expression="x^2 + 1" />, que tiene <MathFormula expression="r = 0" />.
      </li>
      <li>
        <strong>Propagación de errores en la deflación.</strong> Cada cociente se calcula con
        <MathFormula expression="r" /> y <MathFormula expression="s" /> aproximados, así que el error
        se acumula en los factores siguientes. Ante la duda, las raíces se verifican en el
        polinomio original: la aplicación muestra <MathFormula expression="|f(x)|" /> para cada una.
      </li>
      <li>
        <strong>Cierres directos.</strong> Cuando el cociente queda de grado 2 se usa la fórmula
        cuadrática, y cuando queda de grado 1 se despeja <MathFormula expression="x" />. En esos
        casos no se itera.
      </li>
    </ul>

    <!-- 6. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS.bairstow" />

    <!-- 7. Ejemplo resuelto -->
    <h3 id="ejemplo-bairstow">Ejemplo resuelto: el ejemplo clásico de Chapra y Canale</h3>
    <p>Hallemos todas las raíces de</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="example.polynomial" display-mode />
    </div>
    <p>
      con <MathFormula :expression="example.start" />. Todos los valores que siguen son los que
      calcula la aplicación. Los valores
      <span class="legend-prev">de la iteración anterior</span> van en azul y la
      <span class="legend-current">columna reemplazada por los términos independientes</span>, en
      verde.
    </p>

    <div class="worked-step">
      <p class="worked-step-title">Factor 1 · Iteración 1</p>

      <div class="worked-group">
        <p class="worked-group-title">Valores actuales</p>
        <div class="formula-box theory-formula">
          <MathFormula :expression="firstIteration.current" display-mode />
        </div>
      </div>

      <div class="worked-group">
        <p class="worked-group-title">
          División sintética: coeficientes b, con <MathFormula :expression="tex.bRecurrenceShort" />
        </p>
        <div class="formula-box">
          <SyntheticTable :table="firstIteration.extra.b_table" input="a" output="b" />
        </div>
      </div>

      <div class="worked-group">
        <p class="worked-group-title">
          Segunda división sintética, sobre los b: coeficientes c, con
          <MathFormula :expression="tex.cRecurrenceShort" />
        </p>
        <div class="formula-box">
          <SyntheticTable :table="firstIteration.extra.c_table" input="b" output="c" />
        </div>
      </div>

      <div class="worked-group">
        <p class="worked-group-title">Sistema 2×2 planteado</p>
        <div class="formula-box theory-formula">
          <MathFormula :expression="firstIteration.system" display-mode />
        </div>
      </div>

      <div class="worked-group">
        <p class="worked-group-title">Regla de Cramer</p>
        <div class="formula-box theory-formula">
          <MathFormula :expression="firstIteration.D" display-mode />
        </div>
        <div class="formula-pair cramer-pair">
          <div class="formula-box theory-formula">
            <MathFormula :expression="firstIteration.Dr" display-mode />
          </div>
          <div class="formula-box theory-formula">
            <MathFormula :expression="firstIteration.Ds" display-mode />
          </div>
        </div>
      </div>

      <div class="worked-group">
        <p class="worked-group-title">Incrementos y actualización</p>
        <div class="formula-pair">
          <div v-for="(latex, i) in [...firstIteration.increments, ...firstIteration.updates]" :key="i" class="formula-box theory-formula">
            <MathFormula :expression="latex" display-mode />
          </div>
        </div>
      </div>

      <div class="worked-group">
        <p class="worked-group-title">Errores relativos</p>
        <div class="formula-pair">
          <div v-for="(latex, i) in firstIteration.errors" :key="i" class="formula-box theory-formula">
            <MathFormula :expression="latex" display-mode />
          </div>
        </div>
      </div>
      <p class="table-note">
        Los dos errores superan <MathFormula :expression="`\\varepsilon_{\\text{s}} = ${example.tolerance}`" />:
        se sigue iterando, ahora desde los <MathFormula expression="r" /> y
        <MathFormula expression="s" /> nuevos.
      </p>
    </div>

    <h4 class="table-caption">Factor 1: iteración a iteración</h4>
    <div class="table-scroll">
      <table class="comparison-table numeric-table bairstow-table">
        <thead>
          <tr>
            <th>Iteración</th>
            <th><MathFormula expression="r" /></th>
            <th><MathFormula expression="s" /></th>
            <th><MathFormula expression="\Delta r" /></th>
            <th><MathFormula expression="\Delta s" /></th>
            <th><MathFormula expression="\varepsilon_r\ (\%)" /></th>
            <th><MathFormula expression="\varepsilon_s\ (\%)" /></th>
            <th>¿Cumple?</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in iterationRows"
            :key="row.iteration"
            :class="{ 'first-met': row.firstMet }"
          >
            <td>{{ row.iteration }}</td>
            <td>{{ row.r }}</td>
            <td>{{ row.s }}</td>
            <td><MathFormula :expression="row.deltaR" /></td>
            <td><MathFormula :expression="row.deltaS" /></td>
            <td><MathFormula :expression="row.epsR" /></td>
            <td><MathFormula :expression="row.epsS" /></td>
            <td>{{ row.meets ? 'Sí' : 'No' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Los dos errores quedan por debajo del <MathFormula :expression="example.tolerance" /> en la
      <strong>iteración {{ firstMetIteration }}</strong> (resaltada), pero el método continúa hasta
      la iteración {{ FIRST_FACTOR.iterations_used }} por la regla del <strong>mínimo de 6
      iteraciones</strong>. En esas iteraciones extra se ve la convergencia cuadrática: el error
      cae de <MathFormula expression="10^{-2}" /> a <MathFormula expression="10^{-5}" /> y a
      <MathFormula expression="10^{-12}" />.
    </p>

    <div class="worked-step">
      <p class="worked-step-title">Cierre del factor 1</p>
      <div class="formula-pair">
        <div class="formula-box theory-formula">
          <MathFormula :expression="firstClosure.factor" display-mode />
        </div>
        <div class="formula-box theory-formula">
          <MathFormula :expression="firstClosure.discriminant" display-mode />
        </div>
      </div>
      <div class="formula-box theory-formula closure-roots">
        <MathFormula v-for="(latex, i) in firstClosure.roots" :key="i" :expression="latex" display-mode />
      </div>
      <div class="worked-group">
        <p class="worked-group-title">
          Deflación: la división sintética se repite con los <MathFormula expression="r" /> y
          <MathFormula expression="s" /> finales
        </p>
        <div class="formula-box">
          <SyntheticTable :table="FIRST_FACTOR.final_b" input="a" output="b" />
        </div>
      </div>
      <p class="table-note">
        Cociente: <MathFormula :expression="firstClosure.quotient" />. Residuo:
        <MathFormula :expression="firstClosure.residue" />, prácticamente cero (es el error de
        redondeo de la máquina): el factor es exacto.
      </p>
    </div>

    <div class="worked-step">
      <p class="worked-step-title">Factor 2 (resumido)</p>
      <p>
        Se repite el proceso sobre el cociente <MathFormula :expression="secondClosure.dividend" />,
        otra vez desde <MathFormula expression="r_0 = s_0 = -1" />. Tras
        <strong>{{ SECOND_FACTOR.iterations_used }} iteraciones</strong>:
      </p>
      <div class="formula-pair">
        <div class="formula-box theory-formula">
          <MathFormula :expression="secondClosure.factor" display-mode />
        </div>
        <div class="formula-box theory-formula">
          <MathFormula :expression="secondClosure.discriminant" display-mode />
        </div>
      </div>
      <div class="formula-box theory-formula closure-roots">
        <MathFormula v-for="(latex, i) in secondClosure.roots" :key="i" :expression="latex" display-mode />
      </div>
      <p class="table-note">
        El discriminante es negativo: las raíces son un par complejo conjugado, calculado sin
        aritmética compleja. El cociente que queda es <MathFormula :expression="secondClosure.quotient" />.
      </p>
    </div>

    <div class="worked-step">
      <p class="worked-step-title">Factor 3: cierre directo</p>
      <p>El cociente es de grado 1, así que no se itera: se despeja.</p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="thirdClosure.root" display-mode />
      </div>
    </div>

    <h4 class="table-caption">Resultado final</h4>
    <div class="table-scroll">
      <table class="comparison-table numeric-table roots-summary">
        <thead>
          <tr>
            <th>Raíz</th>
            <th>Valor</th>
            <th>Tipo</th>
            <th>Factor</th>
            <th>Comprobación <MathFormula expression="|f(x)|" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rootRows" :key="row.name">
            <td><MathFormula :expression="row.name" /></td>
            <td>{{ row.value }}</td>
            <td>{{ row.kind }}</td>
            <td>{{ row.factor }}</td>
            <td><MathFormula :expression="row.check" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="factorization" display-mode />
    </div>
    <p class="table-note">
      Las comprobaciones del factor 1 están en el orden del redondeo de la máquina; las de los
      factores 2 y 3, alrededor de <MathFormula expression="10^{-7}" />, porque con
      <MathFormula :expression="`\\varepsilon_{\\text{s}} = ${example.tolerance}`" /> el factor 2 se
      aceptó con menos cifras exactas y ese error pasa al cociente. Es el ejemplo
      <strong>Clásico de Chapra y Canale</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('bairstow') }"><strong>Resolver</strong></RouterLink>:
      puedes cargarlo y desplegar cada iteración para ver el mismo paso a paso.
    </p>
  </div>

  <!-- 8. Tablas comparativas -->
  <div class="card">
    <h2>Bairstow frente a Newton</h2>
    <p>
      Bairstow es un método de Newton, pero aplicado a un problema distinto. Conviene compararlo
      con las dos variantes de Newton que se ven en el curso.
    </p>

    <h4 class="table-caption">Bairstow frente a Newton-Raphson (una variable) en polinomios</h4>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Criterio</th>
            <th>Bairstow</th>
            <th>Newton-Raphson</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Qué busca</th>
            <td>Un factor cuadrático <MathFormula :expression="tex.factor" />.</td>
            <td>Una raíz <MathFormula expression="x^{*}" /> de <MathFormula expression="f(x) = 0" />.</td>
          </tr>
          <tr>
            <th scope="row">Raíces complejas</th>
            <td>
              Sin aritmética compleja: <MathFormula expression="r" /> y <MathFormula expression="s" />
              son reales y el par complejo sale de la fórmula cuadrática.
            </td>
            <td>
              Necesita aritmética compleja: desde un <MathFormula expression="x_0" /> real, con
              coeficientes reales, las iteraciones nunca salen de los reales.
            </td>
          </tr>
          <tr>
            <th scope="row">Raíces por ciclo</th>
            <td>Dos (las del factor).</td>
            <td>Una.</td>
          </tr>
          <tr>
            <th scope="row">Derivadas</th>
            <td>
              Las parciales <MathFormula expression="\partial b / \partial r" />,
              <MathFormula expression="\partial b / \partial s" /> son los
              <MathFormula expression="c" /> de una segunda división sintética.
            </td>
            <td>
              <MathFormula expression="f'(x)" />, que en un polinomio también puede evaluarse con
              una segunda división sintética (Horner).
            </td>
          </tr>
          <tr>
            <th scope="row">Orden de convergencia</th>
            <td>Cuadrático cerca de un factor con raíces simples; lineal con raíces múltiples.</td>
            <td>Cuadrático cerca de una raíz simple; lineal con raíces múltiples.</td>
          </tr>
          <tr>
            <th scope="row">Deflación</th>
            <td>Entre el factor cuadrático: el grado baja de 2 en 2.</td>
            <td>Entre <MathFormula expression="x - x^{*}" />: el grado baja de 1 en 1.</td>
          </tr>
          <tr>
            <th scope="row">Valores iniciales</th>
            <td>
              Dos (<MathFormula expression="r_0" />, <MathFormula expression="s_0" />). Puede tardar,
              oscilar o caer en un sistema singular (<MathFormula expression="D \approx 0" />).
            </td>
            <td>
              Uno (<MathFormula expression="x_0" />). Puede oscilar o divergir, y falla si
              <MathFormula expression="f'(x) \approx 0" />.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <h4 class="table-caption">
      Bairstow frente a
      <RouterLink :to="{ name: theoryRouteName('newton') }">Newton para sistemas</RouterLink> (en esta
      aplicación)
    </h4>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Criterio</th>
            <th>Bairstow</th>
            <th>Newton para sistemas</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Variables</th>
            <td>Siempre dos, <MathFormula expression="r" /> y <MathFormula expression="s" />, por cada factor.</td>
            <td>De 2 a 6, tantas como ecuaciones.</td>
          </tr>
          <tr>
            <th scope="row">Jacobiana</th>
            <td>
              <MathFormula expression="\begin{pmatrix} c_2 & c_3 \\ c_1 & c_2 \end{pmatrix}" />, con
              los <MathFormula expression="c" /> de la segunda división sintética. No se deriva.
            </td>
            <td>
              Derivando simbólicamente cada <MathFormula expression="f_i" /> una sola vez, y
              evaluándola en el punto de cada iteración.
            </td>
          </tr>
          <tr>
            <th scope="row">Sistema lineal</th>
            <td>Regla de Cramer 2×2: <MathFormula expression="D" />, <MathFormula expression="D_r" />, <MathFormula expression="D_s" />.</td>
            <td>
              Regla de Cramer <MathFormula expression="n \times n" />: <MathFormula expression="D" />
              y un <MathFormula expression="D_i" /> por variable.
            </td>
          </tr>
          <tr>
            <th scope="row">Error y parada</th>
            <td>
              Relativo porcentual por variable: <MathFormula :expression="tex.stop" />, con la
              tolerancia en % (absoluto si <MathFormula expression="r" /> o
              <MathFormula expression="s" /> es casi 0).
            </td>
            <td>
              Absoluto, en norma infinito del incremento:
              <MathFormula expression="\max_i |\Delta x_i| < \varepsilon" />.
            </td>
          </tr>
          <tr>
            <th scope="row">Iteraciones</th>
            <td>Mínimo 6 y máximo configurable, por cada factor.</td>
            <td>Mínimo 6 y máximo configurable, para todo el sistema.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      En resumen: para hallar <strong>todas</strong> las raíces de un polinomio real, Bairstow
      evita la aritmética compleja y obtiene las raíces de dos en dos; Newton-Raphson es más simple
      de plantear cuando sólo interesa una raíz real y se tiene una buena aproximación de ella.
      Ambos dependen de los valores iniciales y ambos pierden la convergencia cuadrática con
      raíces múltiples.
    </p>
  </div>
</template>

<style scoped>
/* La segunda columna (r) también es numérica: numeric-table sólo alinea a la
   derecha desde la tercera. La última (¿Cumple?) es texto. */
.bairstow-table.numeric-table td:nth-child(2),
.bairstow-table.numeric-table th:nth-child(2) {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.bairstow-table.numeric-table td:last-child,
.bairstow-table.numeric-table th:last-child {
  text-align: center;
}

/* Los valores en notación científica no se parten en dos líneas: en móvil
   la tabla se desplaza dentro de su contenedor. */
.bairstow-table td,
.roots-summary td {
  white-space: nowrap;
}

/* Primera iteración en que se cumple la tolerancia. */
.bairstow-table .first-met td {
  background: var(--color-accent-soft);
  font-weight: var(--weight-semibold);
}

/* Resumen de raíces: valor y tipo son texto. */
.roots-summary.numeric-table td:nth-child(2),
.roots-summary.numeric-table th:nth-child(2) {
  text-align: right;
}

.roots-summary.numeric-table td:nth-child(3),
.roots-summary.numeric-table th:nth-child(3),
.roots-summary.numeric-table td:nth-child(4),
.roots-summary.numeric-table th:nth-child(4) {
  text-align: center;
}

.derivatives-table {
  width: auto;
  min-width: min(100%, 320px);
  margin-bottom: var(--space-3);
}

.theory-note {
  margin: var(--space-3) 0 var(--space-4);
}

.theory-note p {
  margin: 0;
}

.theory-note p + p {
  margin-top: var(--space-2);
}

.worked-group .formula-box + .formula-pair,
.formula-pair + .formula-box {
  margin-top: var(--space-3);
}

.worked-step .formula-pair + .closure-roots {
  margin-top: var(--space-3);
}

.worked-step p:not([class]) {
  margin-top: 0;
}
</style>
