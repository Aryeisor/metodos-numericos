<script setup>
// Teoría propia de la integración de Romberg, en el mismo orden que la del
// trapecio y la de Simpson: introducción, definición formal (notación de
// Chapra, índices desde 1), interpretación (la tabla triangular y el gráfico
// de segmentos del Resolver), derivación (Euler-Maclaurin, los escalones de
// Richardson, la regla general y los pesos), error y convergencia (con el
// caso lento de √x), restricciones, algoritmo, el ejemplo de Chapra con datos
// reales del solver y la tabla comparativa compartida. El fundamento común y
// las referencias los pone la página.
import { ref } from 'vue'
import GlossaryBlock from '../../../components/GlossaryBlock.vue'
import MathFormula from '../../../components/MathFormula.vue'
import TrapezoidChart from '../../../components/TrapezoidChart.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName, theoryRouteName } from '../../routeNames'
import RombergConvergenceTable from '../RombergConvergenceTable.vue'
import RombergTable from '../RombergTable.vue'
import RombergVerification from '../RombergVerification.vue'
import TrapezoidStepDetail from '../TrapezoidStepDetail.vue'
import { RECURRENCE_LATEX, rombergRowGroups } from '../rombergExplain'
import { RECURRENCE_GLOSSARY } from '../rombergGlossary'
import IntegrationComparisonSection from './IntegrationComparisonSection.vue'
import TrapezoidFigure from './TrapezoidFigure.vue'
import {
  ALGORITHM_STEPS,
  CHART_COLUMNS,
  CHART_ROW,
  COLUMN_ROWS,
  COST_ROWS,
  FUNCTION_EXAMPLE,
  GLOSSARIES,
  PRECAUTIONS,
  chartArea,
  chartCurveLabel,
  columnRatios,
  errorTable,
  example,
  gaussReference,
  numericSteps,
  row4,
  sqrt,
  tex,
} from './rombergContent'

// El Resolver carga el ejemplo con ?ejemplo=<id> y lo resuelve.
const RESOLVE_EXAMPLE = { name: solveRouteName('romberg'), query: { ejemplo: 'romb-chapra' } }
const EULER_LINK = { name: theoryRouteName('trapecio'), hash: '#euler-maclaurin' }
const RICHARDSON_LINK = { name: theoryRouteName('trapecio'), hash: '#richardson-trapecio' }
const SIMPSON_LINK = { name: theoryRouteName('simpson'), hash: '#simpson-richardson' }
const SQRT_TICKS = [0, 0.5, 1].map((x) => ({ x, label: String(x) }))

// Gráfico de segmentos: la fila n = 4 con la columna elegida.
const chartK = ref(1)
const chartRow = (k) => ({ ...CHART_ROW, pieces: CHART_ROW.columns[k - 1] })

const groups = (item) => rombergRowGroups(FUNCTION_EXAMPLE, item.row, item.previous)
</script>

<template>
  <div id="metodo-romberg" class="card">
    <h2>Integración de Romberg</h2>

    <!-- 1. Introducción (el fundamento común va arriba, en la página) -->
    <ul>
      <li>
        El <RouterLink :to="{ name: theoryRouteName('trapecio') }">trapecio</RouterLink> es simple, pero converge
        lento: su error es <MathFormula expression="O(h^2)" />.
      </li>
      <li>
        <RouterLink :to="{ name: theoryRouteName('simpson') }">Simpson</RouterLink> es un trapecio mejorado
        <strong>una vez</strong> con la extrapolación de Richardson: su error es <MathFormula expression="O(h^4)" />.
      </li>
      <li>
        Romberg <strong>sigue mejorando</strong>: combina en escalera trapecios con
        <MathFormula expression="n = 1, 2, 4, 8, \dots" /> y en cada escalón elimina un término más del error.
      </li>
      <li>
        Si la función es suave, con muy pocas evaluaciones de <MathFormula expression="f" /> llega a resultados
        muy precisos.
      </li>
    </ul>
    <p class="table-note">
      Lo propuso Werner Romberg en 1955, a partir de la extrapolación de Richardson (1927).
    </p>

    <!-- 2. Definición formal -->
    <h3>Definición formal</h3>
    <p>
      Se usa la notación de Chapra, con los índices desde 1. <strong>Columna 1:</strong> trapecios.
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.column1" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.column1" />

    <p><strong>Columnas siguientes:</strong> cada celda combina dos de la columna anterior.</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.general" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.general" :summary="GLOSSARIES.generalSummary" />

    <p>Los primeros casos, escritos uno por uno:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.cases" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.cases" />

    <p>
      <strong>Columna 1 con la recurrencia del trapecio</strong> (así la calcula el Resolver: cada fila sólo
      evalúa los puntos nuevos):
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="RECURRENCE_LATEX" display-mode /></div>
    <GlossaryBlock :items="RECURRENCE_GLOSSARY.items" :summary="RECURRENCE_GLOSSARY.summary" />

    <p>
      <strong>Criterio de parada:</strong> se compara la diagonal de dos filas seguidas. El error relativo de
      Chapra, <MathFormula expression="\varepsilon_a" />, es la alternativa en porcentaje.
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.stop" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.stop" />
    <p class="table-note">
      El sistema exige además al menos 6 filas, por requisito del curso. Nota de notación: Burden y Faires
      escriben la misma fórmula con <MathFormula expression="R_{k,j}" />, y algunos textos ponen los índices al
      revés. Es el mismo cálculo.
    </p>

    <!-- 3. Interpretación -->
    <h3>Interpretación: cómo leer la tabla triangular</h3>
    <p>
      Es la tabla del Resolver con el ejemplo de Chapra. La diagonal está resaltada; toca o pasa el cursor sobre
      una celda de la columna 2 en adelante para ver las dos celdas de las que sale:
      <span class="legend-current">la de la misma fila</span> y <span class="legend-prev">la de la fila anterior</span>.
    </p>
    <div class="resolver-detail">
      <RombergTable :result="FUNCTION_EXAMPLE" />
    </div>
    <ul>
      <li>
        <strong>Por filas:</strong> cada fila agrega un trapecio con el doble de segmentos y aprovecha los puntos
        anteriores con la recurrencia del trapecio.
      </li>
      <li><strong>Por columnas:</strong> cada columna es una regla con un orden más alto.</li>
    </ul>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Columna</th>
            <th>Equivale a</th>
            <th>Une los puntos con</th>
            <th>Orden</th>
            <th>Exacta para grado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in COLUMN_ROWS" :key="c.k">
            <th scope="row"><MathFormula :expression="c.k" /></th>
            <td>{{ c.name }}</td>
            <td>{{ c.shape }}</td>
            <td><MathFormula :expression="c.order" /></td>
            <td><MathFormula :expression="c.degree" /></td>
          </tr>
        </tbody>
      </table>
    </div>

    <p>
      <strong>Gráfico de segmentos</strong> (el del Resolver): la fila 3 del ejemplo de Chapra
      (<MathFormula expression="n = 4" />). Elige la columna y mira cómo las rectas, las parábolas y las curvas de
      grado 4 se pegan cada vez más a la curva:
    </p>
    <div class="resolver-detail">
      <TrapezoidChart
        :curve="FUNCTION_EXAMPLE.curve"
        :row="chartRow(chartK)"
        :title="`Gráfico de segmentos: ${CHART_COLUMNS[chartK - 1].label}`"
        :area-label="chartArea(chartK)"
        :curve-label="chartCurveLabel"
      >
        <div class="row-picker" role="radiogroup" aria-label="Columna del gráfico">
          <span class="picker-label">Columna:</span>
          <button
            v-for="c in CHART_COLUMNS"
            :key="c.k"
            type="button"
            role="radio"
            class="row-btn"
            :class="{ 'is-active': c.k === chartK }"
            :aria-checked="c.k === chartK"
            @click="chartK = c.k"
          >
            {{ c.label }}
          </button>
        </div>
      </TrapezoidChart>
    </div>
    <p class="table-note">
      Con <MathFormula expression="n = 4" />: columna 1 = {{ example.R(3, 1) }}, columna 2 = {{ example.R(3, 2) }}
      y columna 3 = {{ example.R(3, 3) }} (exacta). Desde la columna 4 no hay dibujo: ya no equivale a unir los
      puntos con piezas de un polinomio.
    </p>

    <!-- 4. Derivación -->
    <h3>Derivación</h3>

    <h4 class="table-caption">El punto de partida: Euler-Maclaurin</h4>
    <p>
      Se explica en la tarjeta
      <RouterLink :to="EULER_LINK">«fórmula de Euler-Maclaurin»</RouterLink> de la teoría del trapecio. Aquí basta
      la idea: el trapecio con segmentos de ancho <MathFormula expression="h" /> es el valor exacto más una suma de
      potencias de <MathFormula expression="h" />.
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.euler" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.euler" />
    <ul>
      <li>
        Los <MathFormula expression="c_j" /> no dependen de <MathFormula expression="h" />: sólo dependen de
        <MathFormula expression="f" />, <MathFormula expression="a" /> y <MathFormula expression="b" />.
      </li>
      <li>Sólo aparecen potencias <strong>pares</strong>.</li>
    </ul>

    <h4 class="table-caption">Primer escalón: eliminar h²</h4>
    <p>
      Es el mismo paso del <RouterLink :to="RICHARDSON_LINK">puente a Simpson</RouterLink> del trapecio y de
      <RouterLink :to="SIMPSON_LINK">Simpson como trapecio mejorado</RouterLink>, escrito con todos los términos.
    </p>
    <ol>
      <li>
        Se escribe el trapecio con <MathFormula expression="h/2" />: cada potencia se divide entre
        <MathFormula expression="2^2 = 4" />, <MathFormula expression="2^4 = 16" />, …
        <div class="formula-box theory-formula"><MathFormula :expression="tex.step1[0]" display-mode /></div>
      </li>
      <li>
        Se multiplica por 4 y se resta <MathFormula expression="T(h)" />. El término
        <MathFormula expression="c_1h^2" /> aparece igual en los dos y desaparece:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.step1[1]" display-mode /></div>
      </li>
      <li>
        Se divide entre 3 para que quede <MathFormula expression="I" /> sola:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.step1[2]" display-mode /></div>
        Es la columna 2, con error <MathFormula expression="O(h^4)" />.
      </li>
    </ol>
    <GlossaryBlock :items="GLOSSARIES.step1" />

    <h4 class="table-caption">Segundo escalón: eliminar h⁴</h4>
    <ol>
      <li>
        La columna 2 tiene la misma forma, pero empieza en <MathFormula expression="h^4" />; con
        <MathFormula expression="h/2" />, ese término se divide entre 16 porque
        <MathFormula expression="(h/2)^4 = h^4/16" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.step2[0]" display-mode /></div>
      </li>
      <li>
        Se multiplica por 16 y se resta: el término <MathFormula expression="d_2h^4" /> desaparece.
        <div class="formula-box theory-formula"><MathFormula :expression="tex.step2[1]" display-mode /></div>
      </li>
      <li>
        Se divide entre 15. Es la columna 3, con error <MathFormula expression="O(h^6)" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.step2[2]" display-mode /></div>
      </li>
    </ol>
    <GlossaryBlock :items="GLOSSARIES.step2" />

    <h4 class="table-caption">Regla general</h4>
    <p>
      Al reducir <MathFormula expression="h" /> a la mitad, el término <MathFormula expression="h^{2k}" /> se
      divide entre <MathFormula expression="4^k" />:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.halving" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.halving" />
    <p>
      Por eso el escalón que elimina ese término usa el factor <MathFormula expression="4^k" />. En la notación de
      la tabla, el paso de la columna <MathFormula expression="k - 1" /> a la <MathFormula expression="k" /> elimina
      <MathFormula expression="h^{2(k-1)}" /> y usa el factor <MathFormula expression="4^{k-1}" />: es la fórmula
      de la definición.
    </p>
    <p>
      <strong>Con números</strong> (Chapra, valores del solver). En
      <span class="legend-current">verde</span> el valor de la misma fila y en
      <span class="legend-prev">azul</span> el de la fila anterior. En el último paso la sustitución va con 8
      decimales, como en el Resolver: con 6, la cuenta con los números que se ven no daría el valor guardado.
    </p>
    <div v-for="(lines, i) in numericSteps" :key="i" class="formula-box theory-formula">
      <MathFormula v-for="(line, j) in lines" :key="j" :expression="line" display-mode />
    </div>

    <div class="more-card">
      <p class="more-title">Para saber más: las columnas como reglas con pesos</p>
      <p>
        Cada celda es una suma <MathFormula expression="\sum_j w_j\,f(x_j)" />, como cualquier cuadratura. En
        <MathFormula expression="[0, 1]" />, con fracciones exactas:
      </p>
      <ul>
        <li>
          <MathFormula expression="R_{2,2}" />: pesos <MathFormula expression="1/6,\ 2/3,\ 1/6" />, es decir,
          Simpson 1/3.
          <div class="formula-box theory-formula"><MathFormula :expression="tex.weights22" display-mode /></div>
        </li>
        <li>
          <MathFormula expression="R_{3,3}" />: la <strong>regla de Boole</strong>.
          <div class="formula-box theory-formula"><MathFormula :expression="tex.weights33" display-mode /></div>
        </li>
        <li>
          <MathFormula expression="R_{4,4}" />: todos los pesos son <strong>positivos</strong> y la regla es exacta
          hasta grado 7. Los de Newton-Cotes con los mismos 9 puntos tienen pesos <strong>negativos</strong>:
          <div class="formula-box theory-formula">
            <MathFormula :expression="tex.weights44" display-mode />
            <MathFormula :expression="tex.newtonCotes9" display-mode />
          </div>
        </li>
      </ul>
      <GlossaryBlock :items="GLOSSARIES.weights" />
      <p>En palabras:</p>
      <ul>
        <li>
          Desde la columna 4, Romberg ya no es una regla de Newton-Cotes; por eso el gráfico de segmentos no la
          dibuja.
        </li>
        <li>
          Sus pesos siguen siendo positivos, y eso lo hace <strong>estable</strong>: no amplifica los errores de
          redondeo restando números grandes, como sí hacen las fórmulas de Newton-Cotes de muchos puntos.
        </li>
      </ul>
    </div>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p>
      <strong>Orden por columna:</strong> la columna <MathFormula expression="k" /> tiene error
      <MathFormula expression="O(h^{2k})" />. Al pasar a la fila siguiente, el error de la columna
      <MathFormula expression="k" /> se divide entre unas <MathFormula expression="4^k" /> veces. Razones
      observadas con <MathFormula expression="e^{-x^2}" /> en <MathFormula expression="[0, 1]" /> (ejemplo 2 del
      Resolver):
    </p>
    <ul>
      <li v-for="c in columnRatios" :key="c.k">
        Columna {{ c.k }}: {{ c.values.join(', ') }}
        <template v-if="c.k < 3">(tiende a {{ c.target }})</template>
        <template v-else>(todavía lejos de 1/64 con tan pocas filas)</template>.
      </li>
    </ul>

    <p>
      <strong>Tabla triangular de errores</strong> <MathFormula expression="E_t = I - R_{i,k}" /> (valor de
      referencia {{ gaussReference }}):
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table errors-table">
        <thead>
          <tr>
            <th>Fila</th>
            <th>n</th>
            <th v-for="k in 5" :key="k">Columna {{ k }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in errorTable" :key="r.i">
            <td>{{ r.i }}</td>
            <td>{{ r.n }}</td>
            <td v-for="(c, k) in r.cells" :key="k" :class="{ 'is-diagonal': k + 1 === r.i }">{{ c }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Excepción a la regla de 6 decimales: casi todos estos errores son menores que 0.0000005 y se verían 0, así que
      van con potencias de 10.
    </p>
    <p>
      <strong>Comentario honesto:</strong> la diagonal <strong>suele</strong> ser el mejor valor de cada fila, pero
      no siempre. En la fila 4, <MathFormula expression="R_{4,3}" /> tiene error {{ row4.r43 }}, menor que el de la
      diagonal, {{ row4.r44 }}. Por eso el criterio de parada compara diagonales seguidas en lugar de suponer que
      la diagonal es exacta.
    </p>

    <p>
      <strong>Costo:</strong> evaluaciones de <MathFormula expression="f" /> para
      <MathFormula expression="|E_t| \le 0.000001" />, con la comparación de costo del Resolver (el trapecio y
      Simpson duplican <MathFormula expression="n" />):
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Ejemplo</th>
            <th>Romberg (primera fila que lo logra)</th>
            <th>Trapecio</th>
            <th>Simpson 1/3</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, idx) in COST_ROWS" :key="idx">
            <th scope="row"><template v-if="r.label">{{ r.label }}</template><MathFormula v-else :expression="r.m" /></th>
            <td>{{ r.romberg }}</td>
            <td>{{ r.trapezoid }}</td>
            <td>{{ r.simpson }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="more-card">
      <p class="more-title">Cuándo Romberg no gana: √x en [0, 1]</p>
      <ul>
        <li>
          La derivada de <MathFormula expression="\sqrt{x}" /> no existe en <MathFormula expression="x = 0" />
          (la curva sube en vertical), así que la fórmula de Euler-Maclaurin con potencias pares <strong>no
          vale</strong>.
        </li>
        <li>
          El error del trapecio decrece como <MathFormula expression="h^{1.5}" />: desde la fila 5, la razón
          observada es {{ sqrt.ratios.join(', ') }}, cerca de <MathFormula expression="2^{-1.5} = 0.3536" /> y no de
          0.25.
        </li>
        <li>
          Las combinaciones de Richardson usan factores pensados para <MathFormula expression="h^2" />,
          <MathFormula expression="h^4" />, …, así que ya no eliminan el error y Romberg pierde su ventaja.
        </li>
        <li>Es la advertencia de «función poco suave» del Resolver.</li>
      </ul>
      <TrapezoidFigure
        :f="Math.sqrt"
        :a="0"
        :b="1"
        :exact="2 / 3"
        :n-values="[1, 2, 4, 8]"
        :ticks="SQRT_TICKS"
        label="√x"
        compact
      />
      <p class="table-note">
        Cerca de 0 la curva sube casi en vertical: las rectas del trapecio pierden siempre una parte de esa zona,
        y esa parte se achica más lento de lo que Romberg supone.
      </p>
    </div>

    <!-- 6. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 7. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS" />
    <p class="table-note">
      En el modo <strong>Tabla de datos</strong> se usan <MathFormula expression="2^m + 1" /> datos igualmente
      espaciados y la cantidad de filas la fija la cantidad de datos.
    </p>

    <!-- 8. Ejemplo resuelto -->
    <h3 id="ejemplo-romberg">Ejemplo resuelto: polinomio de Chapra en [0, 0.8]</h3>
    <p>Integremos (ejemplo 1 del Resolver, de Chapra y Canale)</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.fn" display-mode /></div>
    <p>
      en <MathFormula expression="[0, 0.8]" /> con tolerancia {{ example.tolerance }}. La integral exacta es
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.integral" display-mode /></div>
    <p>
      Todos los valores que siguen son los que calcula la aplicación, con los mismos componentes del paso a paso
      del Resolver: <span class="legend-prev">la fila anterior</span> va en azul y
      <span class="legend-current">los valores nuevos</span>, en verde.
    </p>
    <p>
      <RouterLink :to="RESOLVE_EXAMPLE" class="btn btn-primary">Resolver este ejemplo</RouterLink>
    </p>

    <div v-for="item in example.rows" :key="item.row.i" class="worked-step">
      <p class="worked-step-title">
        Fila {{ item.row.i }} (<MathFormula :expression="`n = ${item.row.n}`" />):
        <MathFormula :expression="`R_{${item.row.i},${item.row.i}} = ${example.R(item.row.i, item.row.i)}`" />
      </p>
      <div class="resolver-detail">
        <details v-for="(group, idx) in groups(item)" :key="idx" class="group-details" open>
          <summary>{{ group.title }}</summary>
          <TrapezoidStepDetail
            :result="FUNCTION_EXAMPLE"
            :row="item.row.trapezoid"
            :k="item.row.i"
            :previous="item.previous ? item.previous.trapezoid : null"
            :custom-steps="group.steps"
          />
        </details>
      </div>
    </div>
    <p>
      Resumen: <MathFormula :expression="`R_{1,1} = ${example.R(1, 1)}`" />;
      <MathFormula :expression="`R_{2,1} = ${example.R(2, 1)}`" /> y
      <MathFormula :expression="`R_{2,2} = ${example.R(2, 2)}`" /> (error estimado {{ example.estimated(2) }});
      <MathFormula :expression="`R_{3,1} = ${example.R(3, 1)}`" />,
      <MathFormula :expression="`R_{3,2} = ${example.R(3, 2)}`" /> y
      <MathFormula :expression="`R_{3,3} = ${example.R(3, 3)}`" /> (error estimado {{ example.estimated(3) }} y
      <MathFormula expression="\varepsilon_a" /> = {{ example.approx(3) }}).
    </p>
    <p>
      <strong><MathFormula expression="R_{3,3}" /> ya es el valor exacto</strong>, porque la columna 3 (Boole)
      integra sin error los polinomios de grado 5, y <MathFormula expression="f" /> es de grado 5.
    </p>

    <p>
      <strong>Resto de las filas.</strong> La tabla completa, como la devuelve el solver. El método se detiene en la
      <strong>fila {{ example.rowsUsed }}</strong> ({{ example.evaluations }} evaluaciones), la primera con el error
      estimado <MathFormula :expression="`\\le ${example.tolerance}`" /> y al menos 6 filas.
    </p>
    <div class="resolver-detail">
      <p class="table-caption">Tabla triangular</p>
      <RombergTable :result="FUNCTION_EXAMPLE" />
      <p class="table-caption">Tabla de errores <MathFormula expression="E_t = I - R_{i,k}" /></p>
      <RombergTable :result="FUNCTION_EXAMPLE" field="errors" />
      <p class="table-caption">Convergencia de la diagonal</p>
      <RombergConvergenceTable :result="FUNCTION_EXAMPLE" />
      <RombergVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>Polinomio de Chapra en [0, 0.8]</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('romberg') }"><strong>Resolver</strong></RouterLink>: el botón
      «Resolver este ejemplo» lo carga y lo resuelve. En la comparación de costo, la fila 3 usa 5 evaluaciones.
    </p>

    <h4 class="table-caption">Mini-ejemplo del caso lento: √x en [0, 1]</h4>
    <p>
      Ejemplo 5 del Resolver (exacta <MathFormula expression="2/3" />). La diagonal avanza despacio:
      {{ sqrt.diagonal.join(', ') }}, … y el método necesita {{ sqrt.rows }} filas.
    </p>
    <div class="alert alert-warning">⚠ {{ sqrt.warning }}</div>
    <p class="table-note">{{ sqrt.cost }}</p>
  </div>

  <!-- 9. Tabla comparativa (compartida por la categoría) -->
  <IntegrationComparisonSection />
</template>

<style scoped>
.table-scroll + p,
.table-scroll + ul {
  margin-top: var(--space-4);
}

.errors-table td {
  white-space: nowrap;
}

.errors-table td.is-diagonal {
  background: var(--color-cell-diagonal);
  font-weight: var(--weight-semibold);
}

.more-card {
  margin: var(--space-4) 0;
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-left: 3px solid var(--color-accent);
  border-radius: var(--radius-nested);
  min-width: 0;
}

.more-title {
  margin: 0 0 var(--space-2);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
}

.resolver-detail {
  margin-top: var(--space-3);
  min-width: 0;
}

.worked-step .resolver-detail {
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
}

.group-details {
  border-left: 3px solid var(--color-line);
  padding-left: var(--space-3);
  margin-bottom: var(--space-2);
  min-width: 0;
}

.group-details > summary {
  padding: var(--space-1) 0;
  font-size: var(--text-small);
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
  cursor: pointer;
}

.group-details > summary:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

/* Los componentes de Resolver traen su propia lista .steps (ver la página de
   5 puntos): aquí recupera el aspecto que tiene en Resolver. */
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

/* Selector de columna del gráfico (mismo aspecto que en Resolver). */
.row-picker {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.picker-label {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.row-btn {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-line-strong);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  color: var(--color-ink);
  font-size: var(--text-small);
  cursor: pointer;
}

.row-btn:hover {
  background: var(--color-accent-soft);
}

.row-btn.is-active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
  font-weight: var(--weight-semibold);
}

.row-btn:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
</style>
