<script setup>
// Teoría propia de las diferencias progresiva y regresiva: definición formal,
// interpretación geométrica (figura con deslizador de h), derivación desde
// Taylor, error y convergencia (tabla de razones y la «V» del redondeo),
// restricciones, algoritmo, el ejemplo de Burden y Faires resuelto con datos
// reales del solver (mismos componentes que Resolver) y la tabla comparativa.
import ConvergenceChart from '../../../components/ConvergenceChart.vue'
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName } from '../../routeNames'
import DataPointsTable from '../DataPointsTable.vue'
import DifferenceStepDetail from '../DifferenceStepDetail.vue'
import DifferentiationVerification from '../DifferentiationVerification.vue'
import RefinementTable from '../RefinementTable.vue'
import { cell } from '../formulas'
import SecantFigure from './SecantFigure.vue'
import {
  ALGORITHM_STEPS,
  FUNCTION_EXAMPLE,
  PRECAUTIONS,
  TABLE_EXAMPLE,
  averageExample,
  backwardFormula,
  carExample,
  concavity,
  convergenceRows,
  example,
  formatNumber,
  forwardFormula,
  roundingCurve,
  roundingTable,
  stepDetail,
  tex,
} from './content'

const FORMULAS = [forwardFormula, backwardFormula]
</script>

<template>
  <div id="metodo-diferencias" class="card">
    <h2>Diferencias progresiva y regresiva</h2>

    <!-- 2. Definición formal -->
    <h3 class="first-heading">Definición formal</h3>
    <p>Para una función <MathFormula expression="f" /> y un paso <MathFormula expression="h > 0" />:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.forward" display-mode />
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.backward" display-mode />
    </div>
    <ul>
      <li>
        Burden y Faires escriben una sola fórmula, <MathFormula :expression="tex.burden" />, y la
        llaman progresiva si <MathFormula expression="h > 0" /> y regresiva si
        <MathFormula expression="h < 0" />. Es lo mismo que las dos fórmulas de arriba.
      </li>
      <li>La regresiva es la progresiva aplicada «desde el otro lado».</li>
      <li>
        En esta aplicación, <MathFormula expression="h" /> siempre es positivo y se elige la
        fórmula.
      </li>
    </ul>

    <!-- 3. Interpretación geométrica -->
    <h3>Interpretación geométrica</h3>
    <p>
      La derivada es la <strong>pendiente de la recta tangente</strong> en
      <MathFormula expression="x_0" />. Las fórmulas la reemplazan por la pendiente de una
      <strong>recta secante</strong>:
    </p>
    <ul>
      <li>
        la progresiva une <MathFormula expression="(x_0,\, f(x_0))" /> con
        <MathFormula expression="(x_0 + h,\, f(x_0 + h))" />, a la derecha;
      </li>
      <li>
        la regresiva une <MathFormula expression="(x_0 - h,\, f(x_0 - h))" /> con
        <MathFormula expression="(x_0,\, f(x_0))" />, a la izquierda.
      </li>
    </ul>
    <SecantFigure />
    <p><strong>Lectura de la figura (concavidad):</strong></p>
    <ul>
      <li>
        Si <MathFormula expression="f" /> es <strong>cóncava</strong>
        (<MathFormula expression="f'' < 0" />, como <MathFormula expression="\ln x" />), la
        progresiva <strong>subestima</strong> la derivada y la regresiva la
        <strong>sobreestima</strong>.
      </li>
      <li>
        Si <MathFormula expression="f" /> es <strong>convexa</strong>
        (<MathFormula expression="f'' > 0" />), ocurre al revés.
      </li>
      <li>
        En el ejemplo, con <MathFormula expression="h = 0.1" />:
        <MathFormula :expression="concavity" />.
      </li>
    </ul>

    <!-- 4. Derivación -->
    <h3>Derivación desde Taylor</h3>
    <p><strong>Progresiva.</strong> Se corta la serie de Taylor en el término de orden 1:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.taylorForward" display-mode />
    </div>
    <p>
      Se resta <MathFormula expression="f(x_0)" /> en los dos lados y se divide entre
      <MathFormula expression="h" />:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.isolatedForward" display-mode />
    </div>
    <p>
      El último término es el <strong>error de truncamiento</strong>: lo que se pierde al usar sólo
      el cociente.
    </p>
    <p><strong>Regresiva.</strong> Lo mismo, con <MathFormula expression="f(x_0 - h)" />:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.taylorBackward" display-mode />
    </div>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.isolatedBackward" display-mode />
    </div>

    <div class="alert alert-info theory-note">
      <p>
        <strong>Observación:</strong> los términos principales del error tienen
        <strong>signos opuestos</strong>:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.leadingErrors" display-mode />
      </div>
      <p>
        Por eso, al <strong>promediarlas</strong>, el término en <MathFormula expression="h" /> se
        cancela y el error pasa a ser de orden <MathFormula expression="O(h^2)" />:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.average" display-mode />
      </div>
      <p>
        Es la idea de la fórmula de 3 puntos (punto medio), que se verá en la siguiente sección.
        Con <MathFormula expression="\ln x" />, <MathFormula expression="x_0 = 1.8" /> y
        <MathFormula expression="h = 0.1" />: <MathFormula :expression="averageExample.value" />,
        con error <MathFormula :expression="averageExample.error" />, unas
        {{ averageExample.times }} veces menor que el de cada fórmula por separado. Coincide con la
        predicción <MathFormula :expression="averageExample.predicted" />.
      </p>
    </div>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p><strong>Cota del error.</strong> Del término de truncamiento:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.bound" display-mode />
    </div>
    <p>
      El error es de orden <MathFormula expression="O(h)" />, o de <strong>primer orden</strong>.
    </p>

    <p>
      <strong>Convergencia cuando <MathFormula expression="h \to 0" />.</strong> Cada vez que
      <MathFormula expression="h" /> se divide entre 2, el error se divide aproximadamente entre 2:
      la razón entre errores consecutivos tiende a <MathFormula expression="0.5" />. Filas 1 a 6 del
      ejemplo (<MathFormula expression="\ln x" />, <MathFormula expression="x_0 = 1.8" />,
      <MathFormula expression="h_0 = 0.1" />), tal como las calcula el solver:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table convergence-table">
        <thead>
          <tr>
            <th>k</th>
            <th>h</th>
            <th><MathFormula expression="D^{+}" /></th>
            <th>Error</th>
            <th>Razón</th>
            <th><MathFormula expression="D^{-}" /></th>
            <th>Error</th>
            <th>Razón</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in convergenceRows" :key="row.k">
            <td>{{ row.k }}</td>
            <td>{{ row.h }}</td>
            <td>{{ cell(row.forward.D) }}</td>
            <td>{{ cell(row.forward.real_error) }}</td>
            <td>{{ cell(row.forward.ratio) }}</td>
            <td>{{ cell(row.backward.D) }}</td>
            <td>{{ cell(row.backward.real_error) }}</td>
            <td>{{ cell(row.backward.ratio) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p>
      <strong>¿Por qué no usar un <MathFormula expression="h" /> diminuto?</strong> Al truncamiento
      se suma el redondeo, y el error total es aproximadamente
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.totalError" display-mode />
    </div>
    <p>que tiene un mínimo en</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.optimalH" display-mode />
    </div>
    <p>
      Para el ejemplo, <MathFormula expression="h^{*} \approx 0.00000004" />. Orden de magnitud del
      error real de la diferencia progresiva (<MathFormula expression="\ln x" />,
      <MathFormula expression="x_0 = 1.8" />):
    </p>
    <div class="table-scroll">
      <table class="comparison-table rounding-table">
        <tbody>
          <tr>
            <th scope="row"><MathFormula expression="h" /></th>
            <td v-for="[h] in roundingTable" :key="h"><MathFormula :expression="h" /></td>
          </tr>
          <tr>
            <th scope="row">Orden del error</th>
            <td v-for="[h, order] in roundingTable" :key="h"><MathFormula :expression="order" /></td>
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
      Al principio, reducir <MathFormula expression="h" /> mejora la aproximación; desde cierto
      punto el redondeo domina y el error vuelve a crecer. Por eso Resolver avisa cuando el redondeo
      se vuelve comparable con el truncamiento.
    </p>

    <!-- 6. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 7. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS['diferencias-finitas']" />
    <p class="table-note">
      En el modo <strong>Tabla de datos</strong> no hay refinamiento: cada punto usa sus vecinos de
      la tabla, con el <MathFormula expression="h" /> de cada par.
    </p>

    <!-- 8. Ejemplo resuelto -->
    <h3 id="ejemplo-diferencias">Ejemplo resuelto: ln x en x₀ = 1.8 (Burden y Faires)</h3>
    <p>Aproximemos la derivada de</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="example.function" display-mode />
    </div>
    <p>
      con <MathFormula :expression="example.data" /> y las dos fórmulas («Ambas»). La derivada
      exacta es <MathFormula :expression="example.derivative" />, así que
      <MathFormula :expression="example.exact" />. Todos los valores que siguen son los que calcula
      la aplicación. En las evaluaciones, <span class="legend-prev">f(x₀)</span> va en azul y
      <span class="legend-current">los demás puntos</span>, en verde; en el error estimado,
      <span class="legend-prev">la fila anterior</span> va en azul y
      <span class="legend-current">la actual</span>, en verde.
    </p>

    <div v-for="k in [1, 2]" :key="k" class="worked-step">
      <p class="worked-step-title">Fila {{ k }}</p>
      <div class="detail-pair">
        <div v-for="formula in FORMULAS" :key="formula.key" class="worked-group resolver-detail">
          <p class="worked-group-title">{{ formula.name }}</p>
          <DifferenceStepDetail v-bind="stepDetail(k, formula)" />
        </div>
      </div>
    </div>

    <p>
      <strong>Resto de las filas.</strong> La tabla completa, como la devuelve el solver; despliega
      cualquier fila para ver su cálculo. Se detiene en la
      <strong>fila {{ example.rowsUsed }}</strong>, la primera en que el error estimado de las dos
      fórmulas es <MathFormula :expression="`\\le ${example.tolerance}`" />, con
      <MathFormula :expression="`D^{+} = ${formatNumber(example.last.forward.D)}`" /> y
      <MathFormula :expression="`D^{-} = ${formatNumber(example.last.backward.D)}`" />.
    </p>
    <div class="resolver-detail">
      <RefinementTable v-for="f in FORMULAS" :key="f.key" :result="FUNCTION_EXAMPLE" :formula="f" />
      <DifferentiationVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>ln(x) en x₀ = 1.8 (Burden y Faires)</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('diferencias-finitas') }"><strong>Resolver</strong></RouterLink>:
      puedes cargarlo y desplegar cada fila para ver el mismo paso a paso.
    </p>

    <h4 class="table-caption">Mini-ejemplo con datos: la posición de un carro</h4>
    <p>
      Se midió la posición de un carro en <MathFormula :expression="`t = ${carExample.times}`" /> s:
      <MathFormula :expression="`${carExample.positions}`" /> m. Sin refinamiento, cada punto usa su
      vecino:
    </p>
    <ul>
      <li>
        Velocidad progresiva en <MathFormula expression="t = 0, \dots, 4" />:
        {{ carExample.forward.map((p) => p.v).join(', ') }} m/s.
      </li>
      <li>
        Velocidad regresiva en <MathFormula expression="t = 1, \dots, 5" />:
        {{ carExample.backward.map((p) => p.v).join(', ') }} m/s.
      </li>
      <li>
        Los datos son <MathFormula expression="f(t) = 2t^2" />, así que la velocidad exacta es
        <MathFormula expression="4t" /> y el error es {{ carExample.error }} en todos los puntos.
        Coincide exactamente con la cota
        <MathFormula :expression="`\\frac{1}{2} \\cdot 4 = ${carExample.bound}`" />, porque
        <MathFormula expression="f'' = 4" /> es constante.
      </li>
    </ul>
    <div class="resolver-detail">
      <DataPointsTable :result="TABLE_EXAMPLE" />
      <DifferentiationVerification :result="TABLE_EXAMPLE" />
    </div>
    <p class="table-note">
      La comprobación de la secante común, <MathFormula expression="D^{+}(t_i) = D^{-}(t_{i+1})" />,
      muestra que las dos fórmulas usan la misma recta entre dos datos vecinos. Es el ejemplo
      <strong>Posición de un carro (tabla + función)</strong> de Resolver.
    </p>
  </div>

  <!-- 9. Tabla comparativa -->
  <div class="card">
    <h2>Progresiva, regresiva y derivada analítica</h2>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Aspecto</th>
            <th>Progresiva</th>
            <th>Regresiva</th>
            <th>Derivada analítica</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Fórmula</th>
            <td><MathFormula expression="\frac{f(x_0 + h) - f(x_0)}{h}" /></td>
            <td><MathFormula expression="\frac{f(x_0) - f(x_0 - h)}{h}" /></td>
            <td><MathFormula expression="f'(x)" />, derivando a mano</td>
          </tr>
          <tr>
            <th scope="row">Puntos que usa</th>
            <td><MathFormula expression="x_0,\ x_0 + h" /></td>
            <td><MathFormula expression="x_0 - h,\ x_0" /></td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Orden del error</th>
            <td><MathFormula expression="O(h)" /></td>
            <td><MathFormula expression="O(h)" /></td>
            <td>Exacta</td>
          </tr>
          <tr>
            <th scope="row">Signo del error principal</th>
            <td><MathFormula expression="+\frac{h}{2} f''" /></td>
            <td><MathFormula expression="-\frac{h}{2} f''" /></td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Funciona sólo con datos</th>
            <td>Sí</td>
            <td>Sí</td>
            <td>No</td>
          </tr>
          <tr>
            <th scope="row">Uso típico</th>
            <td>Primer punto de una tabla; método de Euler.</td>
            <td>Último punto de una tabla; datos en tiempo real (sólo hay valores pasados).</td>
            <td>Cuando la fórmula es sencilla.</td>
          </tr>
          <tr>
            <th scope="row">Evaluaciones de <MathFormula expression="f" /> por aproximación</th>
            <td>2</td>
            <td>2</td>
            <td>—</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Las fórmulas de 3 y 5 puntos mejoran el orden a
      <MathFormula expression="O(h^2)" /> y <MathFormula expression="O(h^4)" /> usando más puntos.
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
.rounding-table td {
  white-space: nowrap;
}

.rounding-table td {
  text-align: center;
}

.table-scroll + p {
  margin-top: var(--space-4);
}

.theory-note {
  margin: var(--space-3) 0 var(--space-4);
}

.theory-note p {
  margin: 0;
}

.theory-note > * + * {
  margin-top: var(--space-2);
}

/* Paso a paso de Resolver, una fórmula al lado de la otra si caben. */
.detail-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(380px, 100%), 1fr));
  gap: var(--space-3);
}

.detail-pair .resolver-detail {
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
