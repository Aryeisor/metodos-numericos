<script setup>
// Teoría propia del método del trapecio, en el mismo orden que las páginas de
// diferenciación: definición formal (simple, compuesta y segmentos
// desiguales), interpretación geométrica (figura con selector de n y signo del
// error), derivación (regla simple, su error, el error compuesto,
// Euler-Maclaurin, la recurrencia y el puente a Simpson y Romberg por
// Richardson), error y convergencia, restricciones, algoritmo, el ejemplo de
// Chapra con datos reales del solver y la tabla comparativa de la categoría.
// El fundamento común y las referencias los pone la página.
import GlossaryBlock from '../../../components/GlossaryBlock.vue'
import MathFormula from '../../../components/MathFormula.vue'
import TrapezoidChart from '../../../components/TrapezoidChart.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName } from '../../routeNames'
import IntegrationRefinementTable from '../IntegrationRefinementTable.vue'
import IntegrationVerification from '../IntegrationVerification.vue'
import SegmentsTable from '../SegmentsTable.vue'
import TrapezoidStepDetail from '../TrapezoidStepDetail.vue'
import { cell, percent } from '../formulas'
import TrapezoidFigure from './TrapezoidFigure.vue'
import {
  ALGORITHM_STEPS,
  APPROX_GLOSSARY,
  BOUND_GLOSSARY,
  CHAPRA_EXACT,
  COMPOSITE_GLOSSARY,
  FUNCTION_EXAMPLE,
  GLOSSARIES,
  PRECAUTIONS,
  TABLE_EXAMPLE,
  approxCheck,
  chapra,
  convergenceRows,
  eulerCheck,
  example,
  periodic,
  recurrenceCheck,
  richardsonRows,
  simpsonN2,
  square,
  tableExample,
  tex,
} from './trapezoidContent'

const WEIGHTS_GLOSSARY = [...COMPOSITE_GLOSSARY.items, ...GLOSSARIES.weights]
const CHAPRA_TICKS = [0, 0.2, 0.4, 0.6, 0.8].map((x) => ({ x, label: String(x) }))
const SIN_TICKS = [
  { x: 0, label: '0' },
  { x: Math.PI / 2, label: 'π/2' },
  { x: Math.PI, label: 'π' },
]
const SQUARE_TICKS = [0, 1, 2].map((x) => ({ x, label: String(x) }))
</script>

<template>
  <div id="metodo-trapecio" class="card">
    <h2>Método del trapecio</h2>

    <!-- 1. Introducción (el fundamento común va arriba, en la página) -->
    <p>
      Es la regla de Newton-Cotes más sencilla: reemplaza la curva por <strong>rectas</strong> (polinomios
      de grado 1) y suma las áreas de los trapecios que quedan debajo. Su error es
      <MathFormula expression="O(h^2)" />, funciona con datos de espaciado desigual y es la base de
      Simpson y Romberg.
    </p>

    <!-- 2. Definición formal -->
    <h3>Definición formal</h3>
    <p><strong>Regla simple</strong> (un solo trapecio en todo el intervalo):</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.simple" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.simple" :summary="GLOSSARIES.simpleSummary" />

    <p>
      <strong>Regla compuesta</strong> (<MathFormula expression="n" /> segmentos,
      <MathFormula expression="h = (b - a)/n" />, <MathFormula expression="x_i = a + i\,h" />):
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.composite" display-mode /></div>
    <GlossaryBlock :items="WEIGHTS_GLOSSARY" :summary="COMPOSITE_GLOSSARY.summary" />
    <p>En la forma general de una cuadratura, los pesos son:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.weights" display-mode /></div>

    <p><strong>Segmentos desiguales</strong> (datos con espaciado no uniforme):</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.unequal" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.unequal" />
    <p>
      Esta flexibilidad es una ventaja del trapecio: cada segmento usa su propio ancho. Simpson, en
      cambio, necesita espaciado uniforme.
    </p>

    <!-- 3. Interpretación geométrica -->
    <h3>Interpretación geométrica</h3>
    <p>
      La regla une los puntos <MathFormula expression="(x_i, f(x_i))" /> con rectas y calcula el área de
      los trapecios. Con la función de Chapra,
      <MathFormula expression="f(x) = 0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5" /> en
      <MathFormula expression="[0, 0.8]" />, elige el número de segmentos:
    </p>
    <TrapezoidFigure
      :f="chapra"
      :a="0"
      :b="0.8"
      :exact="CHAPRA_EXACT"
      :n-values="[1, 2, 4, 8, 16]"
      :ticks="CHAPRA_TICKS"
      label="f(x) de Chapra"
    />
    <p class="table-note">
      Calculado en el navegador, sólo como ilustración. Al duplicar <MathFormula expression="n" />, las
      zonas de color (lo que se pierde y lo que se agrega) se hacen cada vez más delgadas.
    </p>

    <p><strong>Lectura del signo del error</strong> (<MathFormula expression="E_t = I - T" />):</p>
    <div class="sign-grid">
      <div>
        <p>
          Si <MathFormula expression="f'' < 0" /> (cóncava, como <MathFormula expression="\sin x" /> en
          <MathFormula expression="[0, \pi]" />), las rectas quedan <strong>por debajo</strong> de la curva
          y el trapecio <strong>subestima</strong>: con <MathFormula expression="n = 1, 2, 4" /> da 0,
          1.570796 y 1.896119, frente a la exacta 2.
        </p>
        <TrapezoidFigure
          :f="Math.sin"
          :a="0"
          :b="Math.PI"
          :exact="2"
          :n-values="[1, 2, 4]"
          :ticks="SIN_TICKS"
          label="sin x"
          compact
        />
      </div>
      <div>
        <p>
          Si <MathFormula expression="f'' > 0" /> (convexa, como <MathFormula expression="x^2" /> en
          <MathFormula expression="[0, 2]" />), las rectas quedan <strong>por encima</strong> y el trapecio
          <strong>sobreestima</strong>: con <MathFormula expression="n = 1, 2, 4" /> da 4, 3 y 2.75,
          frente a la exacta 2.666667.
        </p>
        <TrapezoidFigure
          :f="square"
          :a="0"
          :b="2"
          :exact="8 / 3"
          :n-values="[1, 2, 4]"
          :ticks="SQUARE_TICKS"
          label="x²"
          compact
        />
      </div>
    </div>
    <p>
      Si <MathFormula expression="f''" /> cambia de signo (como en la función de Chapra), hay partes donde
      se pierde y partes donde se agrega, y se <strong>compensan</strong> en parte.
    </p>

    <!-- 4. Derivación -->
    <h3>Derivación</h3>

    <h4 class="table-caption">De dónde sale la regla simple</h4>
    <ol>
      <li>
        Se reemplaza <MathFormula expression="f" /> por la recta que pasa por
        <MathFormula expression="(a, f(a))" /> y <MathFormula expression="(b, f(b))" />, que es el polinomio
        de interpolación de grado 1:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.line" display-mode /></div>
      </li>
      <li>
        Se integra la recta. En palabras, línea por línea: se separa la integral en dos partes; la primera
        es el ancho por <MathFormula expression="f(a)" /> y la segunda es la integral de
        <MathFormula expression="x - a" />, que vale <MathFormula expression="(b - a)^2/2" />; al final se
        saca <MathFormula expression="b - a" /> como factor común:
        <div class="formula-box theory-formula">
          <MathFormula v-for="(line, i) in tex.integrateLine" :key="i" :expression="line" display-mode />
        </div>
      </li>
      <li>
        Es exactamente el área de un trapecio con bases <MathFormula expression="f(a)" /> y
        <MathFormula expression="f(b)" /> y altura <MathFormula expression="b - a" />.
      </li>
    </ol>

    <h4 class="table-caption">El error de la regla simple</h4>
    <ol>
      <li>
        El error de interpolar con una recta es (fórmula del error de interpolación, con algún
        <MathFormula expression="\xi_x" /> entre <MathFormula expression="a" /> y
        <MathFormula expression="b" />):
        <div class="formula-box theory-formula"><MathFormula :expression="tex.interpolationError" display-mode /></div>
      </li>
      <li>
        El error de la integral es la integral de ese error:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.errorIntegral" display-mode /></div>
      </li>
      <li>
        El factor <MathFormula expression="(x - a)(x - b)" /> no cambia de signo en
        <MathFormula expression="[a, b]" /> (es negativo o cero), así que el teorema del valor medio para
        integrales permite sacar <MathFormula expression="f''" /> evaluada en un solo punto
        <MathFormula expression="\xi" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.meanValue" display-mode /></div>
      </li>
      <li>
        Queda integrar un polinomio de grado 2; da negativo porque el factor es negativo dentro del
        intervalo:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.productIntegral" display-mode /></div>
      </li>
      <li>
        Se multiplica <MathFormula expression="\frac{1}{2}" /> por
        <MathFormula expression="-\frac{(b - a)^3}{6}" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.simpleError" display-mode /></div>
        <GlossaryBlock :items="GLOSSARIES.simpleError" />
      </li>
    </ol>
    <p>
      <strong>Comprobación con números:</strong> con <MathFormula expression="x^2" /> en
      <MathFormula expression="[0, 2]" />, <MathFormula expression="T = 4" /> e
      <MathFormula expression="I = 8/3" />:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.squareCheck" display-mode /></div>
    <p class="formula-legend">
      Es una igualdad exacta porque <MathFormula expression="f'' = 2" /> es constante: no importa dónde
      esté <MathFormula expression="\xi" />.
    </p>

    <h4 class="table-caption">El error de la regla compuesta</h4>
    <p>
      Se suman los <MathFormula expression="n" /> errores, cada uno de un segmento de ancho
      <MathFormula expression="h" />:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.compositeError" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.compositeError" />
    <p>
      El paso del medio: como <MathFormula expression="b - a = n\,h" />, se reescribe
      <MathFormula expression="h^3" /> por <MathFormula expression="n" /> y la suma dividida entre
      <MathFormula expression="n" /> es un promedio de <MathFormula expression="f''" />:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.nh" display-mode /></div>
    <p>De aquí salen dos fórmulas que usa el Resolver:</p>
    <ul>
      <li>
        La <strong>cota</strong>: se reemplaza el promedio por el máximo
        <MathFormula expression="M_2" /> (el peor caso; ver «Error y convergencia»).
      </li>
      <li>
        El <strong>error aproximado de Chapra</strong>: se usa el promedio exacto de
        <MathFormula expression="f''" /> en <MathFormula expression="[a, b]" />. Como la integral de
        <MathFormula expression="f''" /> es <MathFormula expression="f'" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.meanSecond" display-mode /></div>
        <div class="formula-box theory-formula"><MathFormula :expression="tex.approx" display-mode /></div>
        <GlossaryBlock :items="APPROX_GLOSSARY.items" />
      </li>
    </ul>
    <p>
      <strong>Ejemplo de Chapra</strong> (valores del solver):
      <MathFormula :expression="`f'(0) = ${example.fa}`" /> y
      <MathFormula :expression="`f'(0.8) = ${example.fb}`" />, así que
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="approxCheck.mean" display-mode />
      <MathFormula :expression="`n = 1:\\quad ${approxCheck.n1}`" display-mode />
      <MathFormula :expression="`n = 2:\\quad ${approxCheck.n2}`" display-mode />
    </div>
    <p>
      Con un solo segmento, <MathFormula expression="E_a" /> y <MathFormula expression="E_t" /> difieren
      bastante: <MathFormula expression="f''" /> varía muchísimo dentro del segmento (de −400 a casi 64), y
      el promedio no la representa bien. Con 2 segmentos ya se parecen más.
    </p>

    <div class="more-card">
      <p class="more-title">Para saber más: fórmula de Euler-Maclaurin (por qué Romberg funciona)</p>
      <p>Con sus primeros términos, el error del trapecio compuesto es</p>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.eulerMaclaurin" display-mode /></div>
      <GlossaryBlock :items="GLOSSARIES.eulerMaclaurin" />
      <ul>
        <li>
          El error del trapecio sólo tiene potencias <strong>pares</strong> de
          <MathFormula expression="h" /> (<MathFormula expression="h^2, h^4, h^6, \dots" />).
        </li>
        <li>
          El primer término es exactamente el <MathFormula expression="E_a" /> de Chapra con el signo
          cambiado (recuerda que <MathFormula expression="E_a" /> estima <MathFormula expression="I - T" />).
          Por eso <MathFormula expression="E_a" /> es tan buena estimación cuando
          <MathFormula expression="h" /> es pequeño.
        </li>
      </ul>
      <p>Comprobación con Chapra, <MathFormula expression="n = 8" /> (<MathFormula expression="h = 0.1" />):</p>
      <div class="formula-box theory-formula">
        <MathFormula :expression="eulerCheck.derivatives" display-mode />
        <MathFormula :expression="eulerCheck.terms" display-mode />
        <MathFormula :expression="`${eulerCheck.solver}\\ \\checkmark`" display-mode />
      </div>
      <p class="formula-legend">
        Los dos términos dan el valor exacto porque <MathFormula expression="f^{(5)}" /> es constante (el
        polinomio es de grado 5), así que el término siguiente, que usa
        <MathFormula expression="f^{(5)}(b) - f^{(5)}(a)" />, es 0.
      </p>
    </div>

    <h4 class="table-caption">Recurrencia al duplicar n</h4>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.recurrence" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.recurrence" />
    <p>
      En palabras: los puntos viejos siguen siendo puntos de división, así que sólo se evalúan los del
      centro de cada segmento anterior. Con los valores del solver:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="recurrenceCheck" display-mode /></div>

    <h4 class="table-caption">Puente a Simpson y Romberg (Richardson)</h4>
    <p>
      Como el error es aproximadamente <MathFormula expression="c\,h^2" />, combinar dos resultados
      elimina ese término. Línea por línea: el error con <MathFormula expression="n" />; el error con
      <MathFormula expression="2n" />, que es 4 veces menor; y al restar, el término
      <MathFormula expression="c\,h^2" /> se cancela:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula v-for="(line, i) in tex.richardsonWhy" :key="i" :expression="line" display-mode />
    </div>
    <p>de donde</p>
    <div class="formula-box theory-formula"><MathFormula :expression="`I \\approx ${tex.richardson}`" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.richardson" />
    <p>Con los <MathFormula expression="T" /> del solver (Chapra):</p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>De n a 2n</th>
            <th><MathFormula :expression="tex.richardson" /></th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in richardsonRows" :key="r.label">
            <th scope="row">{{ r.label }}</th>
            <td>{{ cell(r.value) }}</td>
            <td>{{ cell(r.error) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <ul class="table-note">
      <li>
        El primer valor ({{ simpsonN2 }}) es exactamente lo que da la <strong>regla de Simpson 1/3</strong>
        de Chapra con <MathFormula expression="n = 2" />: Simpson es, en el fondo, un trapecio mejorado con
        Richardson. Se verá en la próxima página.
      </li>
      <li>
        Repetir esta combinación en escalera es la <strong>integración de Romberg</strong>, igual a la
        escalera de Richardson de la teoría de la fórmula de 5 puntos.
      </li>
    </ul>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p><strong>Cota</strong> que usa el sistema:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.bound" display-mode /></div>
    <GlossaryBlock :items="BOUND_GLOSSARY.items" />
    <p>
      Filas 1 a 6 del ejemplo de Chapra, tal como las calcula el solver (exacta
      {{ cell(CHAPRA_EXACT) }}):
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table convergence-table">
        <thead>
          <tr>
            <th>k</th>
            <th>n</th>
            <th>h</th>
            <th>T</th>
            <th><MathFormula expression="E_t" /></th>
            <th><MathFormula expression="\varepsilon_t" /></th>
            <th>Razón</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in convergenceRows" :key="r.k">
            <td>{{ r.k }}</td>
            <td>{{ r.n }}</td>
            <td>{{ r.h }}</td>
            <td>{{ cell(r.T) }}</td>
            <td>{{ cell(r.Et) }}</td>
            <td>{{ percent(r.relative) }}</td>
            <td>{{ cell(r.ratio) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      La razón tarda en llegar a 0.25: con <MathFormula expression="h" /> grande, el término en
      <MathFormula expression="h^4" /> de Euler-Maclaurin todavía pesa. Al reducir
      <MathFormula expression="h" />, el término <MathFormula expression="h^2" /> domina y la razón se
      acerca a 0.25.
    </p>
    <ul>
      <li>
        <strong>Exactitud:</strong> la regla es exacta para polinomios de grado
        <MathFormula expression="\le 1" />, porque entonces <MathFormula expression="f'' = 0" />. Ejemplo
        del Resolver: <MathFormula expression="2x + 1" /> en <MathFormula expression="[1, 3]" /> da 10 con
        cualquier <MathFormula expression="n" />.
      </li>
      <li>
        <strong>Redondeo:</strong> a diferencia de la diferenciación, no hay un
        <MathFormula expression="h" /> óptimo a partir del cual reducirlo empeore el resultado. El trapecio
        suma valores con pesos positivos, sin restar números casi iguales, así que el redondeo sólo influye
        cuando <MathFormula expression="n" /> es enorme.
      </li>
    </ul>

    <div class="more-card">
      <p class="more-title">Para saber más: funciones periódicas</p>
      <p>
        Para una función periódica integrada sobre un período completo, los términos de Euler-Maclaurin se
        anulan (las derivadas valen lo mismo en <MathFormula expression="a" /> y en
        <MathFormula expression="b" />) y el trapecio converge rapidísimo. Ejemplo:
        <MathFormula :expression="`\\int_0^{2\\pi} e^{\\cos x}\\,dx = ${periodic.exact}`" />.
      </p>
      <ul>
        <li v-for="p in periodic.errors" :key="p.n">
          Con <MathFormula :expression="`n = ${p.n}`" />, el error es {{ p.error }}<template v-if="p.error === '0'">
            (se ve 0 con 6 decimales)</template>.
        </li>
      </ul>
    </div>

    <!-- 6. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 7. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS" />
    <p class="table-note">
      En el modo <strong>Tabla de datos</strong> no hay refinamiento: cada segmento es su propio trapecio,
      el espaciado puede ser desigual y la comprobación es la suma de las áreas.
    </p>

    <!-- 8. Ejemplo resuelto -->
    <h3 id="ejemplo-trapecio">Ejemplo resuelto: polinomio de Chapra en [0, 0.8]</h3>
    <p>Integremos</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.fn" display-mode /></div>
    <p>
      en <MathFormula expression="[0, 0.8]" />, con <MathFormula expression="n_0 = 1" /> y tolerancia
      {{ example.tolerance }}. La integral exacta es
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.integral" display-mode /></div>
    <p>
      Además, <MathFormula :expression="`\\bar{f''} = ${example.meanSecond}`" /> y
      <MathFormula :expression="`M_2 = ${example.M2}`" />. Todos los valores que siguen son los que calcula
      la aplicación, con los mismos componentes del paso a paso del Resolver. En la recurrencia,
      <span class="legend-prev">la fila anterior</span> va en azul y
      <span class="legend-current">los valores nuevos</span>, en verde.
    </p>

    <div v-for="item in example.rows" :key="item.k" class="worked-step">
      <p class="worked-step-title">
        Fila {{ item.k }} (<MathFormula :expression="`n = ${item.row.n},\\ h = ${item.row.h.latex}`" />):
        <MathFormula :expression="`T = ${example.T(item.k)}`" />
      </p>
      <div class="resolver-detail">
        <TrapezoidStepDetail :result="FUNCTION_EXAMPLE" :row="item.row" :k="item.k" :previous="item.previous" />
      </div>
    </div>
    <p>
      Resumen de la fila 1: <MathFormula :expression="`T = ${example.T(1)}`" />,
      <MathFormula :expression="`E_t = ${example.Et(1)}`" />,
      <MathFormula expression="\varepsilon_t" /> = {{ example.relative(1) }},
      <MathFormula :expression="`E_a = ${example.Ea(1)}`" /> y cota {{ example.bound(1) }}
      (<MathFormula :expression="`M_2 = ${example.M2}`" />).
    </p>

    <p>
      <strong>Resto de las filas.</strong> La tabla completa, como la devuelve el solver; despliega
      cualquier fila para ver su cálculo. Se detiene en la <strong>fila {{ example.rowsUsed }}</strong>
      (<MathFormula :expression="`n = ${example.lastN}`" />), la primera en que el error estimado es
      <MathFormula :expression="`\\le ${example.tolerance}`" /> y hay al menos 6 filas. La comprobación
      integra <MathFormula expression="f" /> término a término y evalúa
      <MathFormula expression="F(0.8) - F(0)" />.
    </p>
    <div class="resolver-detail">
      <IntegrationRefinementTable :result="FUNCTION_EXAMPLE" />
      <IntegrationVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>Polinomio de Chapra en [0, 0.8]</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('trapecio') }"><strong>Resolver</strong></RouterLink>: puedes
      cargarlo y desplegar cada fila para ver el mismo paso a paso.
    </p>

    <h4 class="table-caption">Mini-ejemplo con segmentos desiguales</h4>
    <p>
      {{ tableExample.segments + 1 }} datos del mismo polinomio, con anchos distintos: los
      {{ tableExample.segments }} trapecios suman <strong>{{ tableExample.total }}</strong>, con
      <MathFormula :expression="`E_t = ${tableExample.Et}`" /> ({{ tableExample.relative }}).
    </p>
    <div class="resolver-detail">
      <TrapezoidChart
        :curve="TABLE_EXAMPLE.curve"
        :row="tableExample.row"
        title="Trapecios de segmentos desiguales"
        :area-label="tableExample.label"
        :curve-label="tableExample.curveLabel"
      />
      <SegmentsTable :result="TABLE_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>Tabla de Chapra con segmentos desiguales</strong> de Resolver.
    </p>
  </div>

  <!-- 9. Tabla comparativa -->
  <div class="card">
    <h2>Integración numérica: comparación de la categoría</h2>
    <p>
      Por ahora, el trapecio frente a lo que vendrá. Cada método se detalla en su página; cuando estén sus
      teorías, esta tabla se completará.
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Aspecto</th>
            <th>Trapecio</th>
            <th>Simpson 1/3</th>
            <th>Romberg</th>
            <th>Gauss</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Aproxima f con</th>
            <td>Rectas (grado 1)</td>
            <td>Parábolas (grado 2)</td>
            <td>Trapecios + Richardson</td>
            <td>Polinomio en nodos óptimos</td>
          </tr>
          <tr>
            <th scope="row">Orden del error (compuesta)</th>
            <td><MathFormula expression="O(h^2)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
            <td>Sube en cada nivel</td>
            <td>Muy alto con pocos puntos</td>
          </tr>
          <tr>
            <th scope="row">Exacta para grado</th>
            <td><MathFormula expression="\le 1" /></td>
            <td><MathFormula expression="\le 3" /></td>
            <td>Aumenta por nivel</td>
            <td><MathFormula expression="\le 2m - 1" /> con <MathFormula expression="m" /> puntos</td>
          </tr>
          <tr>
            <th scope="row">Espaciado desigual</th>
            <td>Sí</td>
            <td>No</td>
            <td>No</td>
            <td>No (nodos fijos)</td>
          </tr>
          <tr>
            <th scope="row">Sirve con datos tabulados</th>
            <td>Sí</td>
            <td>Sí, si es uniforme y <MathFormula expression="n" /> es par</td>
            <td>Sólo si hay <MathFormula expression="n" /> en potencias de 2</td>
            <td>No</td>
          </tr>
          <tr>
            <th scope="row">Resultado en Chapra (<MathFormula expression="n = 2" />)</th>
            <td>{{ example.T(2) }}</td>
            <td>{{ simpsonN2 }}</td>
            <td>—</td>
            <td>—</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      La próxima página (Simpson) mejora el orden a <MathFormula expression="O(h^4)" /> usando parábolas.
      Los detalles de Simpson, Romberg y Gauss se desarrollan en su página.
    </p>
  </div>
</template>

<style scoped>
.convergence-table.numeric-table td:nth-child(2),
.convergence-table.numeric-table th:nth-child(2) {
  text-align: right;
}

.convergence-table td {
  white-space: nowrap;
}

.table-scroll + p {
  margin-top: var(--space-4);
}

.sign-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr));
  gap: var(--space-4);
}

.sign-grid > div {
  min-width: 0;
}

.more-card {
  margin: var(--space-4) 0;
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-left: 3px solid var(--color-accent);
  border-radius: var(--radius-nested);
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
</style>
