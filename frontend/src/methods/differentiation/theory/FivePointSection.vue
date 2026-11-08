<script setup>
// Teoría propia de la fórmula de 5 puntos, en el mismo orden que la de 3
// puntos: introducción, definición formal, interpretación geométrica
// (polinomio de grado 4 con selector de fórmula), derivación por Richardson y
// por coeficientes indeterminados, la escalera de Richardson (puente a
// Romberg), error y convergencia, restricciones, algoritmo, el ejemplo de
// Burden y Faires con datos reales del solver y la tabla comparativa que
// cierra la categoría. El fundamento común y las referencias los pone la página.
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
  categoryErrors as err,
  comparisonRows,
  convergenceRows,
  differences,
  efficiency,
  evaluations,
  example,
  identities,
  ladder,
  ladderMagnitude,
  roundingCurve,
  roundingTable,
  rowSummary,
  secondRow,
  stepDetail,
  tableHighlights,
  tex,
} from './fivePointContent'

const GROUPS = [MID, AHEAD, BEHIND]
const firstRow = rowSummary(1)
</script>

<template>
  <div id="metodo-cinco-puntos" class="card">
    <h2>Fórmula de 5 puntos</h2>

    <!-- 1. Introducción (el fundamento común va arriba, en la página) -->
    <p>
      La progresiva usa 2 puntos (una recta) y tiene error <MathFormula expression="O(h)" />. La
      fórmula de 3 puntos usa una parábola y tiene error <MathFormula expression="O(h^2)" />. La
      fórmula de 5 puntos usa un <strong>polinomio de grado 4</strong> y tiene error
      <MathFormula expression="O(h^4)" />. Es la opción cuando los datos son precisos y se necesitan
      muchas cifras correctas sin usar un <MathFormula expression="h" /> muy pequeño.
    </p>

    <!-- 2. Definición formal -->
    <h3>Definición formal</h3>
    <p>
      Para <MathFormula expression="h > 0" /> (notación de Burden y Faires), con el término exacto
      del error:
    </p>
    <p><strong>Punto medio:</strong></p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.mid" display-mode /></div>
    <p><strong>Extremo hacia adelante:</strong></p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.ahead" display-mode /></div>
    <p><strong>Extremo hacia atrás</strong> (los mismos coeficientes con el signo cambiado):</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.behind" display-mode /></div>
    <ul>
      <li>
        Burden presenta una sola fórmula de extremo y obtiene la de atrás con
        <MathFormula expression="h < 0" />. En esta aplicación, <MathFormula expression="h" /> siempre
        es positivo y las dos fórmulas de extremo se presentan por separado.
      </li>
      <li>
        El punto medio usa <strong>5 puntos</strong>, aunque el coeficiente de
        <MathFormula expression="f(x_0)" /> es 0 y no aparece en la fórmula.
      </li>
      <li>Los coeficientes de cada fórmula suman 0, igual que en las fórmulas anteriores.</li>
    </ul>

    <!-- 3. Interpretación geométrica -->
    <h3>Interpretación geométrica</h3>
    <p>
      La aproximación es la pendiente en <MathFormula expression="x_0" /> del
      <strong>polinomio de grado 4</strong> que pasa por los 5 puntos. Elige la fórmula para ver dónde
      quedan sus puntos; la parábola de 3 puntos y la secante de la progresiva quedan de referencia:
    </p>
    <ParabolaFigure :points="5" />
    <p><strong>Lectura del signo del error:</strong></p>
    <ul>
      <li>En el <strong>punto medio</strong>, <MathFormula :expression="tex.midSign" />.</li>
      <li>En los <strong>extremos</strong>, <MathFormula :expression="tex.endSign" />.</li>
      <li>
        Con <MathFormula expression="f(x) = x e^{x}" /> (<MathFormula expression="f^{(5)} > 0" />), las
        tres fórmulas <strong>subestiman</strong>: <MathFormula :expression="example.order" />.
      </li>
      <li>
        En la fórmula de 3 puntos, el punto medio sobreestimaba: el signo del término principal cambia
        de una familia a otra.
      </li>
    </ul>

    <!-- 4. Derivación -->
    <h3>Derivación</h3>
    <h4 class="table-caption">Por extrapolación de Richardson (punto medio)</h4>
    <p>Es la derivación más corta y conecta con las páginas anteriores:</p>
    <ol>
      <li>
        Por la página de 3 puntos, el error del punto medio de 3 puntos sólo tiene potencias pares:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.d3h" display-mode /></div>
      </li>
      <li>
        Con <MathFormula expression="2h" /> en lugar de <MathFormula expression="h" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.d32h" display-mode /></div>
      </li>
      <li>
        Se multiplica la primera por 4, se le resta la segunda y se divide entre 3. El término en
        <MathFormula expression="h^2" /> se cancela:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.combination" display-mode /></div>
      </li>
      <li>
        Al escribir <MathFormula expression="D_3(h)" /> y <MathFormula expression="D_3(2h)" /> con sus
        puntos y simplificar (común denominador <MathFormula expression="4h" />):
        <div class="formula-box theory-formula">
          <MathFormula v-for="(line, i) in tex.algebra" :key="i" :expression="line" display-mode />
        </div>
        que es la fórmula del punto medio de 5 puntos.
      </li>
    </ol>
    <p>
      <strong>Coherencia del coeficiente del error:</strong>
      <MathFormula :expression="tex.coefficient" />. Coincide con el término
      <MathFormula expression="+\frac{h^4}{30} f^{(5)}" /> de la definición formal, que está escrito
      del lado de <MathFormula expression="f'(x_0)" />.
    </p>

    <h4 class="table-caption">Por coeficientes indeterminados (extremo)</h4>
    <p>
      Para el extremo no hay una combinación tan simple. En lugar de derivar el polinomio de Lagrange
      de grado 4, que es largo, se usa el método de <strong>coeficientes indeterminados</strong>:
    </p>
    <ol>
      <li>
        Se busca
        <div class="formula-box theory-formula"><MathFormula :expression="tex.ansatz" display-mode /></div>
      </li>
      <li>
        Se desarrolla cada <MathFormula expression="f_j" /> con Taylor y se exige que el resultado sea
        <MathFormula expression="f'(x_0)" /> exacto para <MathFormula expression="1, x, x^2, x^3, x^4" />.
        Eso da 5 ecuaciones:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.conditions" display-mode /></div>
      </li>
      <li>
        La solución es <MathFormula :expression="tex.solution" />. Verificación de cada ecuación:
        <ul>
          <li v-for="(line, i) in tex.checks" :key="i"><MathFormula :expression="line" /></li>
        </ul>
      </li>
      <li>
        El error sale de la siguiente potencia: <MathFormula :expression="tex.fifth" />. El término de
        error es <MathFormula :expression="tex.endError" />.
      </li>
    </ol>
    <p>
      Con los puntos <MathFormula expression="-2, -1, 0, 1, 2" /> el mismo procedimiento da
      <MathFormula expression="(1, -8, 0, 8, -1)" /> y
      <MathFormula expression="\sum c_j\,j^5 = -48" />, de donde sale
      <MathFormula expression="-48/1440 = -1/30" />: es el punto medio, y coincide con la derivación
      por Richardson.
    </p>

    <h4 class="table-caption">Desarrollo del error</h4>
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
        El punto medio sólo tiene potencias <strong>pares</strong>
        (<MathFormula expression="h^4" />, <MathFormula expression="h^6" />, …), así que su razón es
        casi exactamente <MathFormula expression="0.0625" /> desde la fila 2.
      </li>
      <li>
        Los extremos tienen el término principal <strong>6 veces mayor</strong>
        (<MathFormula expression="\frac{h^4}{5}" /> frente a <MathFormula expression="\frac{h^4}{30}" />)
        y un término en <MathFormula expression="h^5" />. Por eso su razón se acerca a
        <MathFormula expression="0.0625" /> desde abajo (adelante) y desde arriba (atrás), igual que
        pasaba en 3 puntos.
      </li>
      <li>
        <strong>Exactitud para polinomios:</strong> son exactas para grado
        <MathFormula expression="\le 4" />. Con <MathFormula expression="x^5" />,
        <MathFormula expression="x_0 = 1" /> y <MathFormula expression="h = 0.5" />, el punto medio da
        4.75 (error <MathFormula expression="0.25 = \frac{h^4}{30} \cdot 120" />) y los extremos dan
        3.5 (error <MathFormula expression="1.5 = \frac{h^4}{5} \cdot 120" />). El error coincide
        exactamente con la cota porque <MathFormula expression="f^{(5)} = 120" /> es constante.
      </li>
    </ul>

    <h4 class="table-caption">La escalera de Richardson (puente hacia Romberg)</h4>
    <p>
      Con <MathFormula expression="x e^{x}" /> y <MathFormula expression="x_0 = 2" />, cada nivel
      combina dos valores del nivel anterior:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table ladder-table">
        <thead>
          <tr>
            <th><MathFormula expression="h" /></th>
            <th>Nivel 1: <MathFormula expression="D_3(h)" />, <MathFormula expression="O(h^2)" /></th>
            <th>
              Nivel 2: <MathFormula expression="\frac{4D_3(h) - D_3(2h)}{3}" />,
              <MathFormula expression="O(h^4)" />
            </th>
            <th>
              Nivel 3: <MathFormula expression="\frac{16D_5(h) - D_5(2h)}{15}" />,
              <MathFormula expression="O(h^6)" />
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in ladder" :key="row.h">
            <td>{{ row.h }}</td>
            <td v-for="i in 3" :key="i">
              <template v-if="row.levels[i - 1]">
                {{ cell(row.levels[i - 1].D) }}
                <span class="ladder-error">
                  (error
                  <template v-if="row.levels[i - 1].small">≈ <MathFormula :expression="ladderMagnitude" /></template>
                  <template v-else>{{ cell(row.levels[i - 1].error) }}</template>)
                </span>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Con sólo tres valores de la fórmula de 3 puntos se llega a un error del orden de
      <MathFormula expression="10^{-8}" />. Repetir esta escalera es exactamente lo que hace la
      <strong>integración de Romberg</strong>, aplicada a la regla del trapecio en lugar de a las
      derivadas; se verá en la próxima categoría. El nivel 3 es sólo ilustrativo: <strong>no</strong>
      es parte del Resolver (su error se escribe en potencias de 10 porque a 6 decimales se vería 0).
    </p>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p><strong>Cotas</strong> que usa el sistema:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.bounds" display-mode /></div>
    <p>
      donde el máximo se toma en el intervalo que usa cada fórmula. Orden
      <MathFormula expression="O(h^4)" />: al dividir <MathFormula expression="h" /> entre 2, el error
      se divide entre aproximadamente <strong>16</strong>. Filas 1 a 6 del ejemplo
      (<MathFormula expression="x e^{x}" />, <MathFormula expression="x_0 = 2" />,
      <MathFormula expression="h_0 = 0.1" />, exacta {{ cell(FUNCTION_EXAMPLE.exact) }}), tal como las
      calcula el solver:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table convergence-table">
        <thead>
          <tr>
            <th rowspan="2">k</th>
            <th rowspan="2">h</th>
            <th v-for="f in GROUPS" :key="f.key" colspan="4" class="group-head">{{ f.name }}</th>
          </tr>
          <tr>
            <template v-for="f in GROUPS" :key="f.key">
              <th><MathFormula :expression="f.symbol_latex" /></th>
              <th>Error</th>
              <th>Error (orden de magnitud)</th>
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
              <td><MathFormula :expression="item.magnitude" /></td>
              <td>{{ cell(item.ratio) }}</td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Los errores se muestran como en el Resolver, a 6 decimales: lo que redondea a 0 se ve 0. La
      columna «orden de magnitud» es la <strong>única excepción</strong> de la página a la regla de no
      usar notación científica (junto con las tablas de orden de magnitud y la escalera), porque los
      errores son menores que 0.0000005. En la fila 6 la razón se aleja de 0.0625 porque el redondeo ya
      empieza a influir.
    </p>

    <p>
      <strong>Comparación de toda la categoría</strong> (mismo ejemplo,
      <MathFormula expression="h = 0.1" />):
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Fórmula</th>
            <th>Puntos</th>
            <th>Aproximación</th>
            <th>Error real</th>
            <th>Veces menor que el error de la progresiva</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in comparisonRows" :key="row.name" :class="{ 'best-row': row.best }">
            <th scope="row">{{ row.name }}</th>
            <td>{{ row.count }}</td>
            <td>{{ cell(row.D) }}</td>
            <td>{{ cell(row.real_error) }}</td>
            <td>{{ row.times }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p>
      <strong>Eficiencia:</strong> el <MathFormula expression="h" /> necesario para tener cierto error
      real en este ejemplo, refinando <MathFormula expression="h_0 = 0.1" /> entre 2:
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Error objetivo</th>
            <th>Progresiva</th>
            <th>Punto medio de 3 puntos</th>
            <th>Punto medio de 5 puntos</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in efficiency" :key="row.target">
            <th scope="row"><MathFormula :expression="row.target" /></th>
            <td v-for="col in [row.forward, row.mid3, row.mid5]" :key="col[0]">
              fila {{ col[0] }} (<MathFormula :expression="col[1]" />)
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Por aproximación, la de 5 puntos evalúa <MathFormula expression="f" /> en 4 puntos, contra 2 de
      las otras. A cambio, trabaja con un <MathFormula expression="h" /> cientos o miles de veces mayor,
      lo que la aleja del problema de redondeo.
    </p>

    <p>
      <strong>Redondeo y <MathFormula expression="h" /> óptimo.</strong> El error total del punto medio
      es aproximadamente
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.totalError" display-mode /></div>
    <p>que tiene su mínimo en</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.optimalH" display-mode /></div>
    <p>
      En el ejemplo, <MathFormula expression="h^{*} \approx 0.0009" />. Orden de magnitud del error real
      con las tres fórmulas (<MathFormula expression="x e^{x}" />, <MathFormula expression="x_0 = 2" />):
    </p>
    <div class="table-scroll">
      <table class="comparison-table rounding-table">
        <tbody>
          <tr>
            <th scope="row"><MathFormula expression="h" /></th>
            <td v-for="h in roundingTable.h" :key="h"><MathFormula :expression="h" /></td>
          </tr>
          <tr v-for="row in roundingTable.rows" :key="row.name">
            <th scope="row">{{ row.name }}</th>
            <td v-for="(o, i) in row.values" :key="i"><MathFormula :expression="o" /></td>
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
      Cuanto mayor es el orden de la fórmula, menor es el error mínimo alcanzable
      (<MathFormula expression="10^{-7}" />, <MathFormula expression="10^{-10}" /> y
      <MathFormula expression="10^{-12}" />) y mayor es el <MathFormula expression="h" /> donde se
      logra. Con <MathFormula expression="h" /> muy pequeño, todas terminan dominadas por el redondeo.
    </p>

    <!-- 6. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 7. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS" />
    <p class="table-note">
      En el modo <strong>Tabla de datos</strong> no hay refinamiento: los datos deben tener espaciado
      uniforme, la columna «Recomendada» elige la fórmula con la regla de la restricción 4 y el punto
      medio de 3 puntos se muestra como columna de referencia.
    </p>

    <!-- 8. Ejemplo resuelto -->
    <h3 id="ejemplo-cinco-puntos">Ejemplo resuelto: x·eˣ en x₀ = 2 (Burden y Faires)</h3>
    <p>Aproximemos la derivada de</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.function" display-mode /></div>
    <p>
      con <MathFormula :expression="example.data" /> y las tres fórmulas («Todas»). La derivada exacta
      es <MathFormula :expression="example.derivative" />, así que
      <MathFormula :expression="example.exact" />. Además,
      <MathFormula :expression="example.fifth" />. Todos los valores que siguen son los que calcula la
      aplicación. En las evaluaciones, <span class="legend-prev">f(x₀)</span> va en azul y
      <span class="legend-current">los demás puntos</span>, en verde.
    </p>

    <div class="worked-step">
      <p class="worked-step-title">Fila 1 (<MathFormula expression="h = 0.1" />)</p>
      <p>Evaluaciones de <MathFormula expression="f" /> en los 9 puntos que usan las tres fórmulas:</p>
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
      <p><strong>Identidad de Richardson</strong>, tal como la calcula el solver:</p>
      <div class="formula-box identity-box">
        <div v-for="line in identities" :key="line.key" class="identity-line">
          <MathFormula :expression="line.latex" /> <span class="mark mark-ok">✔</span>
        </div>
      </div>
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
      <MathFormula :expression="`\\le ${example.tolerance}`" /> y hay al menos 6 filas.
    </p>
    <div class="comparison-box">
      <p class="comparison-title">{{ FUNCTION_EXAMPLE.comparison_title }}</p>
      <p v-for="(line, i) in differences.lines" :key="i" class="comparison-line">{{ line }}</p>
    </div>
    <div class="resolver-detail">
      <RefinementTable v-for="f in FORMULAS" :key="f.key" :result="FUNCTION_EXAMPLE" :formula="f" />
      <DifferentiationVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>x·eˣ en x₀ = 2 (Burden y Faires)</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('cinco-puntos') }"><strong>Resolver</strong></RouterLink>:
      puedes cargarlo y desplegar cada fila para ver el mismo paso a paso.
    </p>

    <h4 class="table-caption">Mini-ejemplo con datos: la tabla del libro</h4>
    <p>
      Los 9 valores de <MathFormula expression="x e^{x}" /> entre 1.6 y 2.4 de la fila 1, redondeados a
      6 decimales, como tabla de datos:
    </p>
    <div class="resolver-detail">
      <DataPointsTable :result="TABLE_EXAMPLE" />
      <DifferentiationVerification :result="TABLE_EXAMPLE" />
    </div>
    <ul class="table-note">
      <li>
        En <MathFormula expression="x = 2" /> el punto medio da {{ tableHighlights.book }}, el valor del
        libro (con la función exacta, {{ cell(firstRow[0].D) }}: el redondeo de los datos cambia el sexto
        decimal).
      </li>
      <li>
        En <MathFormula expression="x = 1.7" /> no hay punto medio de 5 puntos: la recomendada es el
        {{ tableHighlights.recommended17 }} (error {{ tableHighlights.ahead17 }}, frente a
        {{ tableHighlights.mid3_17 }} del punto medio de 3 puntos).
      </li>
      <li v-if="tableHighlights.rounding22">
        En <MathFormula expression="x = 2.2" />, la identidad de Richardson con los valores mostrados da
        {{ tableHighlights.rounding22.value_display }} frente a {{ tableHighlights.rounding22.D_display }}:
        la comprobación lo marca como diferencia por redondeo.
      </li>
    </ul>
    <p class="table-note">
      Es el ejemplo <strong>Tabla de x·eˣ (Burden y Faires, tabla + función)</strong> de Resolver.
    </p>
  </div>

  <!-- 9. Tabla comparativa (cierre de la categoría) -->
  <div class="card">
    <h2>Diferenciación numérica: comparación de la categoría</h2>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Aspecto</th>
            <th>Progresiva / Regresiva</th>
            <th>Punto medio de 3 puntos</th>
            <th>Extremo de 3 puntos</th>
            <th>Punto medio de 5 puntos</th>
            <th>Extremo de 5 puntos</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Puntos</th>
            <td>2</td>
            <td>3 (<MathFormula expression="f(x_0)" /> con coeficiente 0)</td>
            <td>3</td>
            <td>5 (<MathFormula expression="f(x_0)" /> con coeficiente 0)</td>
            <td>5</td>
          </tr>
          <tr>
            <th scope="row">Denominador</th>
            <td><MathFormula expression="h" /></td>
            <td><MathFormula expression="2h" /></td>
            <td><MathFormula expression="2h" /></td>
            <td><MathFormula expression="12h" /></td>
            <td><MathFormula expression="12h" /></td>
          </tr>
          <tr>
            <th scope="row">Orden del error</th>
            <td><MathFormula expression="O(h)" /></td>
            <td><MathFormula expression="O(h^2)" /></td>
            <td><MathFormula expression="O(h^2)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
          </tr>
          <tr>
            <th scope="row">Término principal del error</th>
            <td><MathFormula expression="\pm\frac{h}{2} f''" /></td>
            <td><MathFormula expression="+\frac{h^2}{6} f'''" /></td>
            <td><MathFormula expression="-\frac{h^2}{3} f'''" /></td>
            <td><MathFormula expression="-\frac{h^4}{30} f^{(5)}" /></td>
            <td><MathFormula expression="-\frac{h^4}{5} f^{(5)}" /></td>
          </tr>
          <tr>
            <th scope="row">Exacta para polinomios de grado</th>
            <td><MathFormula expression="\le 1" /></td>
            <td><MathFormula expression="\le 2" /></td>
            <td><MathFormula expression="\le 2" /></td>
            <td><MathFormula expression="\le 4" /></td>
            <td><MathFormula expression="\le 4" /></td>
          </tr>
          <tr>
            <th scope="row">Razón al dividir <MathFormula expression="h" /> entre 2</th>
            <td><MathFormula expression="\approx 0.5" /></td>
            <td><MathFormula expression="\approx 0.25" /></td>
            <td><MathFormula expression="\approx 0.25" /></td>
            <td><MathFormula expression="\approx 0.0625" /></td>
            <td><MathFormula expression="\approx 0.0625" /></td>
          </tr>
          <tr>
            <th scope="row">Amplificación del ruido (<MathFormula expression="\delta" /> en los datos)</th>
            <td><MathFormula expression="2\delta / h" /></td>
            <td><MathFormula expression="\delta / h" /></td>
            <td><MathFormula expression="4\delta / h" /></td>
            <td><MathFormula expression="1.5\delta / h" /></td>
            <td><MathFormula expression="\approx 10.67\delta / h" /></td>
          </tr>
          <tr>
            <th scope="row">Error en el ejemplo (<MathFormula expression="h = 0.1" />)</th>
            <td>{{ cell(err.forward) }} / {{ cell(err.backward) }}</td>
            <td>{{ cell(err.mid3) }}</td>
            <td>{{ cell(err.ahead3) }} / {{ cell(err.behind3) }}</td>
            <td>{{ cell(err.mid5) }}</td>
            <td>{{ cell(err.ahead5) }} / {{ cell(err.behind5) }}</td>
          </tr>
          <tr>
            <th scope="row">Se obtiene por Richardson de</th>
            <td>—</td>
            <td>Promedio de progresiva y regresiva</td>
            <td><MathFormula expression="2D^{+}(h) - D^{+}(2h)" /></td>
            <td><MathFormula expression="\frac{4D_3(h) - D_3(2h)}{3}" /></td>
            <td>Coeficientes indeterminados</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h3>Cómo elegir</h3>
    <ul>
      <li>Datos precisos y se necesita mucha exactitud: <strong>5 puntos</strong>.</li>
      <li>Datos con ruido moderado o pocos puntos: <strong>3 puntos</strong> (punto medio).</li>
      <li>
        Sólo hay valores a un lado, o el cálculo es rápido y sencillo (por ejemplo, el método de Euler):
        <strong>progresiva o regresiva</strong>.
      </li>
    </ul>

    <h3>Puente hacia la integración</h3>
    <p>
      La diferenciación numérica <strong>amplifica</strong> el ruido de los datos; la integración lo
      <strong>suaviza</strong>. La misma herramienta (interpolar con polinomios y combinar resultados
      con Richardson) aparecerá en el trapecio, en Simpson y en Romberg.
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
.evaluations-table td,
.ladder-table td {
  white-space: nowrap;
}

.convergence-table .group-head {
  text-align: center;
}

.rounding-table td,
.evaluations-table td {
  text-align: center;
}

.ladder-error {
  color: var(--color-ink-muted);
  font-size: var(--text-small);
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

/* Paso a paso de Resolver, una fórmula debajo de la otra (la línea de
   productos coeficiente·valor no cabe en columnas). */
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

/* Los componentes de Resolver traen su propia lista .steps (ver la página de
   3 puntos): aquí recupera el aspecto que tiene en Resolver. */
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
