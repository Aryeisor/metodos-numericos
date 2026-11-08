<script setup>
// Teoría propia de la fórmula de 3 puntos: introducción, definición formal,
// interpretación geométrica (parábola con selector de fórmula y deslizador de
// h), derivación con Lagrange y con Taylor, conexión con las diferencias
// (Richardson), error y convergencia (tabla de razones y la «V» del
// redondeo), restricciones, algoritmo, el ejemplo de Burden y Faires resuelto
// con datos reales del solver (mismos componentes que Resolver) y la tabla
// comparativa. El fundamento común y las referencias los pone la página.
import ConvergenceChart from '../../../components/ConvergenceChart.vue'
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName } from '../../routeNames'
import DataPointsTable from '../DataPointsTable.vue'
import DifferenceStepDetail from '../DifferenceStepDetail.vue'
import DifferentiationVerification from '../DifferentiationVerification.vue'
import RefinementTable from '../RefinementTable.vue'
import { cell } from '../formulas'
import ParabolaFigure from './ParabolaFigure.vue'
import {
  AHEAD,
  ALGORITHM_STEPS,
  BEHIND,
  ERROR_EXPANSION,
  FORMULAS,
  FUNCTION_EXAMPLE,
  MID,
  PRECAUTIONS,
  TABLE_EXAMPLE,
  comparisonRows,
  convergenceRows,
  differences,
  efficiency,
  evaluations,
  example,
  identities,
  roundingCurve,
  roundingTable,
  rowSummary,
  secondRow,
  stepDetail,
  tex,
} from './threePointContent'

const GROUPS = [MID, AHEAD, BEHIND]
const firstRow = rowSummary(1)
</script>

<template>
  <div id="metodo-tres-puntos" class="card">
    <h2>Fórmula de 3 puntos</h2>

    <!-- 1. Introducción (el fundamento común va arriba, en la página) -->
    <p>
      Las diferencias progresiva y regresiva usan 2 puntos: una <strong>recta secante</strong>, con
      error <MathFormula expression="O(h)" />. Las fórmulas de 3 puntos pasan una
      <strong>parábola</strong> por 3 puntos y toman su pendiente en
      <MathFormula expression="x_0" />. Con eso el error baja a
      <MathFormula expression="O(h^2)" />. En la práctica, son las fórmulas más usadas para derivar
      datos.
    </p>

    <!-- 2. Definición formal -->
    <h3>Definición formal</h3>
    <p>
      Para <MathFormula expression="h > 0" /> (notación de Burden y Faires), con el término exacto
      del error:
    </p>
    <p><strong>Punto medio (centrada):</strong></p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.mid" display-mode /></div>
    <p><strong>Extremo hacia adelante:</strong></p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.ahead" display-mode /></div>
    <p><strong>Extremo hacia atrás:</strong></p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.behind" display-mode /></div>
    <ul>
      <li>
        Burden escribe una sola fórmula de extremo y explica que con
        <MathFormula expression="h < 0" /> se obtiene la de atrás. En esta aplicación,
        <MathFormula expression="h" /> siempre es positivo y las dos fórmulas de extremo se presentan
        por separado.
      </li>
      <li>
        Las tres usan <strong>3 puntos</strong>, aunque en el punto medio el coeficiente de
        <MathFormula expression="f(x_0)" /> es 0 y no aparece en la fórmula.
      </li>
      <li>
        Los coeficientes de cada fórmula suman 0. Por eso, si <MathFormula expression="f" /> es una
        constante, la derivada que da es 0, como debe ser.
      </li>
    </ul>

    <!-- 3. Interpretación geométrica -->
    <h3>Interpretación geométrica</h3>
    <p>
      La idea es la <strong>parábola</strong> que pasa por los 3 puntos (el polinomio de Lagrange de
      grado 2). La aproximación es la pendiente de esa parábola en
      <MathFormula expression="x_0" />. Elige la fórmula para ver dónde quedan sus 3 puntos:
    </p>
    <ParabolaFigure />
    <p><strong>Lectura del signo del error:</strong></p>
    <ul>
      <li>En el <strong>punto medio</strong>, <MathFormula :expression="tex.midSign" />.</li>
      <li>En los <strong>extremos</strong>, <MathFormula :expression="tex.endSign" />.</li>
      <li>
        Con <MathFormula expression="f(x) = x e^{x}" /> (<MathFormula expression="f''' > 0" />), el
        punto medio <strong>sobreestima</strong> y los extremos <strong>subestiman</strong>:
        <MathFormula :expression="example.order" />.
      </li>
    </ul>

    <!-- 4. Derivación -->
    <h3>Derivación</h3>
    <h4 class="table-caption">Con el polinomio de Lagrange (como lo hace Burden)</h4>
    <p>Para el <strong>extremo hacia adelante</strong>:</p>
    <ol>
      <li>
        Puntos <MathFormula expression="x_0" />, <MathFormula expression="x_1 = x_0 + h" /> y
        <MathFormula expression="x_2 = x_0 + 2h" />. Se escribe el polinomio de Lagrange:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrange" display-mode /></div>
        con <MathFormula :expression="tex.lagrangeBasis" />.
      </li>
      <li>
        Se deriva cada <MathFormula expression="L_j" /> y se evalúa en
        <MathFormula expression="x_0" />, usando el espaciado uniforme:
        <div class="formula-box theory-formula">
          <MathFormula :expression="tex.l0" display-mode />
          <MathFormula :expression="tex.l1" display-mode />
          <MathFormula :expression="tex.l2" display-mode />
        </div>
      </li>
      <li>
        Se suma:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrangeSum" display-mode /></div>
      </li>
    </ol>
    <p>
      Con los puntos <MathFormula expression="x_0 - h" />, <MathFormula expression="x_0" /> y
      <MathFormula expression="x_0 + h" />, el mismo procedimiento da los coeficientes
      <MathFormula expression="-\frac{1}{2h}" />, <MathFormula expression="0" /> y
      <MathFormula expression="\frac{1}{2h}" />, que es el punto medio.
    </p>

    <h4 class="table-caption">Con la serie de Taylor (de dónde sale el error)</h4>
    <p><strong>Punto medio.</strong> Se escribe Taylor hacia los dos lados:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.taylorBoth" display-mode /></div>
    <p>
      Al restar, se cancelan <MathFormula expression="f(x_0)" />, <MathFormula expression="f''" /> y
      <MathFormula expression="f^{(4)}" />: todos los términos pares. Al dividir entre
      <MathFormula expression="2h" /> queda:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.taylorMid" display-mode /></div>
    <p>Lo mismo con cada fórmula da el desarrollo de su error:</p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Fórmula</th>
            <th><MathFormula expression="D - f'(x_0)" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="[name, latex] in ERROR_EXPANSION" :key="name">
            <th scope="row">{{ name }}</th>
            <td><MathFormula :expression="latex" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <ul class="consequences">
      <li>
        El punto medio sólo tiene potencias <strong>pares</strong> de
        <MathFormula expression="h" />, por la simetría. Por eso su razón de errores es casi
        exactamente <MathFormula expression="0.25" /> desde la fila 2.
      </li>
      <li>
        Los extremos tienen el término principal <strong>el doble de grande</strong>
        (<MathFormula expression="\frac{h^2}{3}" /> frente a <MathFormula expression="\frac{h^2}{6}" />)
        y además un término en <MathFormula expression="h^3" />. Por eso su razón se acerca a
        <MathFormula expression="0.25" /> más lentamente: desde abajo en el extremo hacia adelante y
        desde arriba en el extremo hacia atrás (ver la tabla de convergencia).
      </li>
      <li>
        <strong>Exactitud para polinomios:</strong> si <MathFormula expression="f" /> es de grado 2 o
        menor, <MathFormula expression="f''' = 0" /> y las tres fórmulas son
        <strong>exactas</strong>. Con <MathFormula expression="x^2 - 3x + 1" /> en
        <MathFormula expression="x_0 = 2" />, todas dan exactamente 1. Con
        <MathFormula expression="x^3" /> en <MathFormula expression="x_0 = 1" /> y
        <MathFormula expression="h = 0.5" /> ya no son exactas: el punto medio da 3.25 (error
        <MathFormula expression="0.25 = \frac{h^2}{6} \cdot 6" />) y el extremo hacia adelante da 2.5
        (error <MathFormula expression="0.5 = \frac{h^2}{3} \cdot 6" />). El error coincide
        exactamente con la cota porque <MathFormula expression="f''' = 6" /> es constante.
      </li>
    </ul>

    <h4 class="table-caption">Conexión con las diferencias (Richardson)</h4>
    <p>Son las dos identidades que usa la comprobación del Resolver:</p>
    <p><strong>Punto medio = promedio de la progresiva y la regresiva:</strong></p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.average" display-mode /></div>
    <p>Los términos <MathFormula expression="\pm \frac{h}{2} f''" /> se cancelan.</p>
    <p>
      <strong>Extremo hacia adelante = <MathFormula expression="2 \cdot D^{+}(h) - D^{+}(2h)" />:</strong>
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.richardson" display-mode /></div>
    <p>
      El error de <MathFormula expression="D^{+}(h)" /> es aproximadamente
      <MathFormula expression="\frac{h}{2} f''" /> y el de <MathFormula expression="D^{+}(2h)" />,
      <MathFormula expression="h\,f''" />. La combinación
      <MathFormula expression="2 \cdot \frac{h}{2} - h = 0" /> elimina el término de orden
      <MathFormula expression="h" />.
    </p>
    <p>
      Esta técnica se llama <strong>extrapolación de Richardson</strong>: combinar dos aproximaciones
      con distinto <MathFormula expression="h" /> para eliminar el término principal del error. Es la
      misma idea en la que se basa la <strong>integración de Romberg</strong>, que se verá en la
      categoría de integración.
    </p>
    <p>
      Con <MathFormula expression="x e^{x}" />, <MathFormula expression="x_0 = 2" /> y
      <MathFormula expression="h = 0.1" />, tal como lo calcula el solver:
    </p>
    <div class="formula-box identity-box">
      <div v-for="line in identities" :key="line.key" class="identity-line">
        <MathFormula :expression="line.latex" /> <span class="mark mark-ok">✔</span>
      </div>
    </div>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p><strong>Cotas</strong> que usa el sistema:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.bounds" display-mode /></div>
    <p>
      donde el máximo se toma en el intervalo que usa cada fórmula. Orden
      <MathFormula expression="O(h^2)" />: al dividir <MathFormula expression="h" /> entre 2, el error
      se divide entre aproximadamente <strong>4</strong>. Filas 1 a 6 del ejemplo
      (<MathFormula expression="x e^{x}" />, <MathFormula expression="x_0 = 2" />,
      <MathFormula expression="h_0 = 0.1" />, exacta {{ cell(FUNCTION_EXAMPLE.exact) }}), tal como
      las calcula el solver:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table convergence-table">
        <thead>
          <tr>
            <th rowspan="2">k</th>
            <th rowspan="2">h</th>
            <th v-for="f in GROUPS" :key="f.key" colspan="3" class="group-head">{{ f.name }}</th>
          </tr>
          <tr>
            <template v-for="f in GROUPS" :key="f.key">
              <th><MathFormula :expression="f.symbol_latex" /></th>
              <th>Error</th>
              <th>Razón</th>
            </template>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in convergenceRows" :key="row.k">
            <td>{{ row.k }}</td>
            <td>{{ row.h }}</td>
            <template v-for="(item, i) in row.items" :key="i">
              <td>{{ cell(item.D) }}</td>
              <td>{{ cell(item.real_error) }}</td>
              <td>{{ cell(item.ratio) }}</td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>

    <p><strong>Comparación con las diferencias</strong> (mismo ejemplo, <MathFormula expression="h = 0.1" />):</p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Fórmula</th>
            <th>Aproximación</th>
            <th>Error real</th>
            <th>Veces menor que el error de la progresiva</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in comparisonRows" :key="row.name" :class="{ 'best-row': row.best }">
            <th scope="row">{{ row.name }}</th>
            <td>{{ cell(row.D) }}</td>
            <td>{{ cell(row.real_error) }}</td>
            <td>{{ row.times }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>Eficiencia:</strong> para tener un error real
      <MathFormula expression="\le 0.0001" /> en este ejemplo, el punto medio necesita
      <MathFormula :expression="`h = ${efficiency.h}`" /> (fila {{ efficiency.k }} del refinamiento) y
      la progresiva necesita <MathFormula expression="h = 0.1/2^{14} \approx 0.000006" /> (fila 15).
      Las dos fórmulas evalúan <MathFormula expression="f" /> en 2 puntos nuevos por aproximación, así
      que el punto medio llega con un <MathFormula expression="h" /> casi 512 veces mayor por el mismo
      costo.
    </p>

    <p><strong>Redondeo y <MathFormula expression="h" /> óptimo.</strong> El error total del punto medio es aproximadamente</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.totalError" display-mode /></div>
    <p>que tiene su mínimo en</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.optimalH" display-mode /></div>
    <p>
      En el ejemplo, <MathFormula expression="h^{*} \approx 0.000006" />, mucho mayor que el de la
      progresiva, que es del orden de <MathFormula expression="10^{-8}" />. Orden de magnitud del error
      real (<MathFormula expression="x e^{x}" />, <MathFormula expression="x_0 = 2" />):
    </p>
    <div class="table-scroll">
      <table class="comparison-table rounding-table">
        <tbody>
          <tr>
            <th scope="row"><MathFormula expression="h" /></th>
            <td v-for="h in roundingTable.h" :key="h"><MathFormula :expression="h" /></td>
          </tr>
          <tr>
            <th scope="row">Progresiva</th>
            <td v-for="(o, i) in roundingTable.forward" :key="i"><MathFormula :expression="o" /></td>
          </tr>
          <tr>
            <th scope="row">Punto medio</th>
            <td v-for="(o, i) in roundingTable.mid" :key="i"><MathFormula :expression="o" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <ConvergenceChart
      :iterations="roundingCurve.iterations"
      :series="roundingCurve.series"
      :labels="roundingCurve.labels"
      title="Error real frente a h (escala log-log)"
      x-label="h"
      y-label="Error (escala log)"
    />
    <p class="table-note">
      El punto medio llega a un error más de 100 veces menor que la mejor progresiva (unas
      <MathFormula expression="6 \cdot 10^{-10}" /> frente a <MathFormula expression="1 \cdot 10^{-7}" />),
      y lo logra con un <MathFormula expression="h" /> mucho más grande. Con
      <MathFormula expression="h" /> muy pequeño, las dos fórmulas terminan con el mismo error de
      redondeo.
    </p>

    <!-- 6. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 7. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS" />
    <p class="table-note">
      En el modo <strong>Tabla de datos</strong> no hay refinamiento: los datos deben tener espaciado
      uniforme, cada punto usa las fórmulas para las que tiene vecinos, la columna «Recomendada» elige
      la mejor y la comprobación verifica las identidades en cada punto.
    </p>

    <!-- 8. Ejemplo resuelto -->
    <h3 id="ejemplo-tres-puntos">Ejemplo resuelto: x·eˣ en x₀ = 2 (Burden y Faires)</h3>
    <p>Aproximemos la derivada de</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.function" display-mode /></div>
    <p>
      con <MathFormula :expression="example.data" /> y las tres fórmulas («Todas»). La derivada exacta
      es <MathFormula :expression="example.derivative" />, así que
      <MathFormula :expression="example.exact" />. Además,
      <MathFormula :expression="example.third" />. Todos los valores que siguen son los que calcula la
      aplicación. En las evaluaciones, <span class="legend-prev">f(x₀)</span> va en azul y
      <span class="legend-current">los demás puntos</span>, en verde.
    </p>

    <div class="worked-step">
      <p class="worked-step-title">Fila 1 (<MathFormula expression="h = 0.1" />)</p>
      <p>Evaluaciones de <MathFormula expression="f" /> en los 5 puntos que usan las tres fórmulas:</p>
      <div class="table-scroll">
        <table class="comparison-table numeric-table evaluations-table">
          <tbody>
            <tr>
              <th scope="row">x</th>
              <td v-for="p in evaluations" :key="p.x">{{ p.x }}</td>
            </tr>
            <tr>
              <th scope="row">f(x)</th>
              <td v-for="p in evaluations" :key="p.x">{{ p.f }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <ul>
        <li v-for="item in firstRow" :key="item.key">
          <strong>{{ item.name }}:</strong>{{ ' ' }}
          <MathFormula :expression="`${item.symbol} = ${cell(item.D)}`" />. Error real
          {{ cell(item.real_error) }}, cota {{ cell(item.bound) }}
          <span class="mark mark-ok">{{ item.within_bound ? '✔' : '⚠' }}</span>
        </li>
      </ul>
      <p>
        El paso a paso, con los mismos componentes del Resolver (los productos y las sumas llevan más
        decimales, por la regla de <MathFormula expression="d" /> decimales):
      </p>
      <div class="detail-grid">
        <div v-for="formula in FORMULAS" :key="formula.key" class="worked-group resolver-detail">
          <p class="worked-group-title">{{ formula.name }}</p>
          <DifferenceStepDetail v-bind="stepDetail(1, formula)" />
        </div>
      </div>
    </div>

    <div class="worked-step">
      <p class="worked-step-title">Fila 2 (<MathFormula :expression="`h = ${secondRow.h}`" />)</p>
      <p>
        <template v-for="(item, i) in secondRow.items" :key="item.key">
          {{ i ? (i === secondRow.items.length - 1 ? ' y ' : ', ') : '' }}{{ item.name.toLowerCase() }}
          <MathFormula :expression="cell(item.D)" />
        </template>.
      </p>
    </div>

    <p>
      <strong>Resto de las filas.</strong> Las tablas completas, como las devuelve el solver; despliega
      cualquier fila para ver su cálculo. Se detiene en la <strong>fila {{ example.rowsUsed }}</strong>,
      la primera en que el error estimado de las tres fórmulas es
      <MathFormula :expression="`\\le ${example.tolerance}`" />.
    </p>
    <div class="comparison-box">
      <p class="comparison-title">Comparación con las diferencias progresiva y regresiva</p>
      <p v-for="(line, i) in differences.lines" :key="i" class="comparison-line">{{ line }}</p>
    </div>
    <div class="resolver-detail">
      <RefinementTable v-for="f in FORMULAS" :key="f.key" :result="FUNCTION_EXAMPLE" :formula="f" />
      <DifferentiationVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>x·eˣ en x₀ = 2 (Burden y Faires)</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('tres-puntos') }"><strong>Resolver</strong></RouterLink>:
      puedes cargarlo y desplegar cada fila para ver el mismo paso a paso.
    </p>

    <h4 class="table-caption">Mini-ejemplo con datos: la tabla del libro</h4>
    <p>
      Los mismos <MathFormula expression="x" /> y <MathFormula expression="f(x)" /> de la fila 1,
      redondeados a 6 decimales, como tabla de datos:
    </p>
    <div class="resolver-detail">
      <DataPointsTable :result="TABLE_EXAMPLE" />
      <DifferentiationVerification :result="TABLE_EXAMPLE" />
    </div>
    <p class="table-note">
      Los resultados en <MathFormula expression="x = 2" /> coinciden con los del libro (22.03231,
      22.22879 y 22.054525). Difieren en el último decimal de los del ejemplo de arriba
      ({{ cell(firstRow[1].D) }}, {{ cell(firstRow[0].D) }} y {{ cell(firstRow[2].D) }}) porque el libro
      parte de datos redondeados a 6 decimales y, al dividir entre
      <MathFormula expression="2h = 0.2" />, ese redondeo se amplifica: un ejemplo pequeño de la
      amplificación del error de los datos (restricción 5). Es el ejemplo
      <strong>Tabla de x·eˣ (Burden y Faires, tabla + función)</strong> de Resolver.
    </p>
  </div>

  <!-- 9. Tabla comparativa -->
  <div class="card">
    <h2>Diferencias y fórmulas de 3 puntos</h2>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Aspecto</th>
            <th>Progresiva / Regresiva</th>
            <th>Punto medio</th>
            <th>Extremo (adelante / atrás)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Puntos que usa</th>
            <td>2</td>
            <td>3 (<MathFormula expression="x_0 \pm h" />; <MathFormula expression="f(x_0)" /> con coeficiente 0)</td>
            <td>3, hacia un solo lado</td>
          </tr>
          <tr>
            <th scope="row">Fórmula</th>
            <td><MathFormula expression="\pm\frac{f(x_0 \pm h) - f(x_0)}{h}" /></td>
            <td><MathFormula expression="\frac{f(x_0 + h) - f(x_0 - h)}{2h}" /></td>
            <td><MathFormula expression="\frac{\mp 3f(x_0) \pm 4f(x_0 \pm h) \mp f(x_0 \pm 2h)}{2h}" /></td>
          </tr>
          <tr>
            <th scope="row">Orden del error</th>
            <td><MathFormula expression="O(h)" /></td>
            <td><MathFormula expression="O(h^2)" /></td>
            <td><MathFormula expression="O(h^2)" /></td>
          </tr>
          <tr>
            <th scope="row">Término principal del error</th>
            <td><MathFormula expression="\pm\frac{h}{2} f''" /></td>
            <td><MathFormula expression="+\frac{h^2}{6} f'''" /></td>
            <td><MathFormula expression="-\frac{h^2}{3} f'''" /></td>
          </tr>
          <tr>
            <th scope="row">Exacta para polinomios de grado</th>
            <td><MathFormula expression="\le 1" /></td>
            <td><MathFormula expression="\le 2" /></td>
            <td><MathFormula expression="\le 2" /></td>
          </tr>
          <tr>
            <th scope="row">Razón de errores al dividir <MathFormula expression="h" /> entre 2</th>
            <td><MathFormula expression="\approx 0.5" /></td>
            <td><MathFormula expression="\approx 0.25" /></td>
            <td><MathFormula expression="\approx 0.25" /></td>
          </tr>
          <tr>
            <th scope="row">Amplificación del ruido (<MathFormula expression="\delta" /> en los datos)</th>
            <td><MathFormula expression="2\delta / h" /></td>
            <td><MathFormula expression="\delta / h" /></td>
            <td><MathFormula expression="4\delta / h" /></td>
          </tr>
          <tr>
            <th scope="row">Datos necesarios</th>
            <td>A un lado</td>
            <td>A ambos lados</td>
            <td>Dos puntos a un lado</td>
          </tr>
          <tr>
            <th scope="row">Uso típico en una tabla</th>
            <td>—</td>
            <td>Puntos interiores</td>
            <td>Primer y último punto</td>
          </tr>
          <tr>
            <th scope="row">Error en el ejemplo (<MathFormula expression="h = 0.1" />)</th>
            <td>{{ cell(comparisonRows[0].real_error) }} / {{ cell(comparisonRows[1].real_error) }}</td>
            <td>{{ cell(comparisonRows[4].real_error) }}</td>
            <td>{{ cell(comparisonRows[2].real_error) }} / {{ cell(comparisonRows[3].real_error) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      La fórmula de 5 puntos sube el orden a <MathFormula expression="O(h^4)" /> con
      5 puntos.
    </p>
  </div>
</template>

<style scoped>
/* h es numérica aunque esté en la segunda columna. */
.convergence-table.numeric-table td:nth-child(2),
.convergence-table.numeric-table th:nth-child(2) {
  text-align: right;
}

.convergence-table td,
.rounding-table td,
.evaluations-table td {
  white-space: nowrap;
}

.convergence-table .group-head {
  text-align: center;
}

.rounding-table td,
.evaluations-table td {
  text-align: center;
}

.best-row th,
.best-row td {
  font-weight: var(--weight-semibold);
}

.table-scroll + p {
  margin-top: var(--space-4);
}

.consequences {
  margin-top: var(--space-3);
}

.identity-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  overflow-x: auto;
}

.comparison-box {
  margin: var(--space-3) 0;
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
}

.comparison-title {
  margin: 0 0 var(--space-2);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.comparison-line {
  margin: 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

/* Paso a paso de Resolver, una fórmula debajo de la otra: con tres columnas la
   línea de la fórmula (productos coeficiente·valor) no cabe y se parte. */
.detail-grid {
  display: grid;
  gap: var(--space-3);
}

.detail-grid .resolver-detail {
  margin: 0;
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
}

/* Los componentes de Resolver traen su propia lista .steps, que no es la de
   las tarjetas del algoritmo (TheoryLayout le da estilo a .theory .steps):
   aquí recupera el aspecto que tiene en Resolver. */
.resolver-detail :deep(.steps) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin: 0;
  padding-left: var(--space-5);
  list-style: decimal;
}

.resolver-detail :deep(.steps > li) {
  margin: 0;
}

.resolver-detail + .table-note,
.resolver-detail {
  margin-top: var(--space-3);
}
</style>
