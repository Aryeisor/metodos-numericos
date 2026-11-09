<script setup>
// Teoría propia de la cuadratura gaussiana, en el mismo orden que las otras
// teorías de integración: introducción, definición formal (con el cambio de
// variable y la tabla de nodos y pesos del Resolver), interpretación (gráfico
// de rectángulos y comparación con Simpson), derivación (2 puntos por
// coeficientes indeterminados, por qué 2m − 1, Legendre y el error), error y
// convergencia, funciones singulares, restricciones, algoritmo, el ejemplo de
// Chapra con datos reales del solver, la tabla comparativa compartida y la
// guía de la categoría. El fundamento común y las referencias los pone la página.
import { ref } from 'vue'
import GlossaryBlock from '../../../components/GlossaryBlock.vue'
import InfoTip from '../../../components/InfoTip.vue'
import MathFormula from '../../../components/MathFormula.vue'
import TrapezoidChart from '../../../components/TrapezoidChart.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName, theoryRouteName } from '../../routeNames'
import GaussStepDetail from '../GaussStepDetail.vue'
import GaussVerification from '../GaussVerification.vue'
import { boundMark, cell, percent } from '../formulas'
import { BOUND_GLOSSARY, BOUND_LATEX, COMPOSITE_GLOSSARY, COMPOSITE_LATEX, NODES_GLOSSARY, NODES_LATEX, gaussColumns } from '../gaussExplain'
import GaussNodesFigure from './GaussNodesFigure.vue'
import IntegrationComparisonSection from './IntegrationComparisonSection.vue'
import {
  ALGORITHM_STEPS,
  CHAPRA_EXACT,
  CHART_ROWS,
  COMPOSITE_EXAMPLE,
  COST_ROWS,
  ERROR_CONSTANTS,
  FUNCTION_EXAMPLE,
  GLOSSARIES,
  NODE_TABLE,
  PRECAUTIONS,
  ROOT_CHART_MS,
  ROOT_COMPOSITE,
  ROOT_EXAMPLE,
  THREE_EVALUATIONS,
  chartArea,
  chartCurveLabel,
  chartLive,
  composite,
  errorRows,
  example,
  gaussReference,
  moments3,
  root,
  sixth,
  tex,
} from './gaussContent'

// El Resolver carga el ejemplo con ?ejemplo=<id> y lo resuelve.
const RESOLVE_EXAMPLE = { name: solveRouteName('gauss'), query: { ejemplo: 'gauss-chapra' } }
const TRAPEZOID = { name: theoryRouteName('trapecio') }
const SIMPSON = { name: theoryRouteName('simpson') }
const ROMBERG = { name: theoryRouteName('romberg') }

// Gráfico de rectángulos del ejemplo 1 (m = 1 a 4) y el de 1/√x.
const chartM = ref(3)
const chartRow = (m) => CHART_ROWS.find((r) => r.m === m)
const rootM = ref(4)
const rootRow = (m) => ROOT_EXAMPLE.chart_rows.find((r) => r.m === m)

const HEADERS = gaussColumns({ showTrue: true, reference: false })
</script>

<template>
  <div id="metodo-gauss" class="card">
    <h2>Cuadratura gaussiana</h2>

    <!-- 1. Introducción (el fundamento común va arriba, en la página) -->
    <ul>
      <li>
        El <RouterLink :to="TRAPEZOID">trapecio</RouterLink>, <RouterLink :to="SIMPSON">Simpson</RouterLink> y
        <RouterLink :to="ROMBERG">Romberg</RouterLink> evalúan <MathFormula expression="f" /> en puntos
        <strong>igualmente espaciados, fijados de antemano</strong>, y sólo eligen los pesos.
      </li>
      <li>Gauss elige <strong>también dónde evaluar</strong>: los nodos.</li>
      <li>
        Con esa libertad extra, <MathFormula expression="m" /> evaluaciones bastan para ser exacto con polinomios
        de grado <MathFormula expression="2m - 1" />.
      </li>
      <li>
        Es el máximo posible con <MathFormula expression="m" /> puntos, y es la base de los programas profesionales
        de integración.
      </li>
    </ul>
    <p class="table-note">
      Carl Friedrich Gauss la propuso en 1814; la forma con polinomios de Legendre se debe a Jacobi (1826).
    </p>

    <!-- 2. Definición formal -->
    <h3>Definición formal</h3>
    <p><strong>En <MathFormula expression="[-1, 1]" />:</strong> una suma de evaluaciones con pesos.</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.rule" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.rule" />

    <p>
      <strong>Cambio de variable a <MathFormula expression="[a, b]" />:</strong> los nodos y los pesos están
      calculados para <MathFormula expression="[-1, 1]" />, así que primero se lleva el intervalo a ese.
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.change" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.change" />
    <ul>
      <li>Con <MathFormula expression="t = -1" />, <MathFormula expression="x = a" />: el extremo izquierdo.</li>
      <li>Con <MathFormula expression="t = 1" />, <MathFormula expression="x = b" />: el extremo derecho.</li>
      <li>
        <MathFormula expression="(b - a)/2" /> es cuánto se estira el intervalo: <MathFormula expression="[-1, 1]" />
        mide 2 y <MathFormula expression="[a, b]" /> mide <MathFormula expression="b - a" />.
      </li>
    </ul>
    <p>Se reemplaza <MathFormula expression="x" /> y <MathFormula expression="dx" /> en la integral:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.mapped" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.mapped" />

    <p>
      <strong>Compuesta</strong> (<MathFormula expression="N" /> subintervalos de ancho
      <MathFormula expression="H = (b - a)/N" />, con centros <MathFormula expression="c_j" />): la misma fórmula
      aplicada en cada subintervalo, y se suman los resultados.
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="COMPOSITE_LATEX" display-mode /></div>
    <GlossaryBlock :items="COMPOSITE_GLOSSARY.items" :summary="COMPOSITE_GLOSSARY.summary" />

    <p><strong>Nodos y pesos</strong> (las formas exactas del Resolver, con sus decimales):</p>
    <div class="table-scroll">
      <table class="comparison-table nodes-table">
        <thead>
          <tr>
            <th>m</th>
            <th>Nodos <MathFormula expression="t_i" /></th>
            <th>Pesos <MathFormula expression="w_i" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in NODE_TABLE" :key="r.m">
            <th scope="row">{{ r.m }}</th>
            <td><div v-for="(t, i) in r.t" :key="i"><MathFormula :expression="t" /></div></td>
            <td><div v-for="(w, i) in r.w" :key="i"><MathFormula :expression="w" /></div></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Cada fila lista los nodos de <MathFormula expression="t \ge 0" />; los negativos son los mismos con signo
      menos y tienen el mismo peso. En cada fila los pesos suman 2.
    </p>

    <!-- 3. Interpretación geométrica -->
    <h3>Interpretación geométrica</h3>
    <p>
      <strong>Gráfico de rectángulos</strong> (el del Resolver), con el polinomio de Chapra en
      <MathFormula expression="[0, 0.8]" />. Cada rectángulo tiene la altura de la curva en un nodo y el ancho que
      le da su peso; los anchos suman <MathFormula expression="b - a" />.
    </p>
    <div class="resolver-detail">
      <TrapezoidChart
        :curve="FUNCTION_EXAMPLE.curve"
        :row="chartRow(chartM)"
        :title="`Gráfico de rectángulos (m = ${chartM})`"
        :area-label="chartArea(chartM)"
        :curve-label="chartCurveLabel"
      >
        <div class="row-picker" role="radiogroup" aria-label="Puntos del gráfico">
          <span class="picker-label">Puntos:</span>
          <button
            v-for="r in CHART_ROWS"
            :key="r.m"
            type="button"
            role="radio"
            class="row-btn"
            :class="{ 'is-active': r.m === chartM }"
            :aria-checked="r.m === chartM"
            @click="chartM = r.m"
          >
            m = {{ r.m }}
          </button>
        </div>
        <div class="live-values">
          <span><MathFormula :expression="`G_{${chartM}} = ${chartLive(chartM).G}`" /></span>
          <span><MathFormula :expression="`I = ${CHAPRA_EXACT}`" /></span>
          <span><MathFormula :expression="`E_t = I - G_{${chartM}} = ${chartLive(chartM).error}`" /></span>
        </div>
      </TrapezoidChart>
    </div>
    <p class="table-note">
      Con <MathFormula expression="m = 3" /> el área ya es la exacta: <MathFormula expression="f" /> es de grado 5
      y la regla de 3 puntos es exacta hasta grado <MathFormula expression="2 \cdot 3 - 1 = 5" />.
    </p>

    <p><strong>Simpson frente a Gauss, con 3 evaluaciones cada uno:</strong></p>
    <GaussNodesFigure />

    <ul>
      <li>
        <strong>Los nodos se agrupan hacia los extremos</strong>, pero sin tocarlos: con
        <MathFormula expression="m = 10" />, el nodo más externo está en <MathFormula expression="t = \pm 0.973907" />.
      </li>
      <li>
        <strong>Todos los pesos son positivos</strong> (el menor, con <MathFormula expression="m = 10" />, es
        0.066671). Como en Romberg, eso hace al método estable frente al redondeo.
      </li>
    </ul>

    <!-- 4. Derivación -->
    <h3>Derivación</h3>

    <h4 class="table-caption">Gauss de 2 puntos, desde cero (coeficientes indeterminados)</h4>
    <ol>
      <li>
        Se buscan <MathFormula expression="t_1,\ t_2,\ w_1,\ w_2" /> (4 incógnitas) tales que la fórmula sea exacta
        para <MathFormula expression="1,\ t,\ t^2,\ t^3" /> (4 condiciones):
        <div class="formula-box theory-formula"><MathFormula :expression="tex.conditions" display-mode /></div>
      </li>
      <li>
        Se escribe una ecuación por cada potencia; el lado derecho es la integral exacta de esa potencia:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.system" display-mode /></div>
        <GlossaryBlock :items="GLOSSARIES.system" />
      </li>
      <li>
        El intervalo es simétrico, así que los nodos también: <MathFormula expression="t_2 = -t_1" /> y
        <MathFormula expression="w_1 = w_2" />. Con eso, la segunda y la cuarta ecuación se cumplen solas, y la
        primera da los pesos:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.symmetry" display-mode /></div>
      </li>
      <li>
        Con los pesos iguales a 1, la tercera ecuación da los nodos:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.third" display-mode /></div>
      </li>
      <li>
        Resultado: exacta hasta grado 3 con <strong>sólo 2 evaluaciones</strong>. Simpson necesita 3 para lo mismo.
        <div class="formula-box theory-formula"><MathFormula :expression="tex.result2" display-mode /></div>
      </li>
    </ol>
    <p><strong>Comprobación con <MathFormula expression="t^4" /></strong> (grado 4, ya fuera del alcance de las dos):</p>
    <div class="formula-box theory-formula">
      <MathFormula v-for="(line, i) in tex.t4" :key="i" :expression="line" display-mode />
    </div>
    <p>
      Gauss de 2 puntos se equivoca <strong>menos con menos evaluaciones</strong>, y Gauss de 3 puntos ya es exacto
      (llega hasta grado 5).
    </p>

    <h4 class="table-caption">¿Por qué 2m − 1?</h4>
    <ul>
      <li>
        Con <MathFormula expression="m" /> puntos hay <MathFormula expression="2m" /> valores libres
        (<MathFormula expression="m" /> nodos y <MathFormula expression="m" /> pesos), así que se pueden cumplir
        <MathFormula expression="2m" /> condiciones: exactitud para
        <MathFormula expression="1, t, \dots, t^{2m-1}" />.
      </li>
      <li>
        Newton-Cotes fija los <MathFormula expression="m" /> nodos y sólo elige los <MathFormula expression="m" />
        pesos, así que llega a grado <MathFormula expression="m - 1" /> (o <MathFormula expression="m" /> cuando
        <MathFormula expression="m" /> es impar, como Simpson).
      </li>
    </ul>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Evaluaciones</th>
            <th>Newton-Cotes llega a grado</th>
            <th>Gauss llega a grado</th>
          </tr>
        </thead>
        <tbody>
          <tr><th scope="row">2</th><td>1 (trapecio)</td><td>3</td></tr>
          <tr><th scope="row">3</th><td>3 (Simpson 1/3)</td><td>5</td></tr>
          <tr><th scope="row">4</th><td>3 (Simpson 3/8)</td><td>7</td></tr>
        </tbody>
      </table>
    </div>

    <div class="more-card">
      <p class="more-title">Para saber más: los polinomios de Legendre (de dónde salen los nodos)</p>
      <p><strong>Definición por recurrencia:</strong> cada uno sale de los dos anteriores.</p>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.recurrence" display-mode /></div>
      <GlossaryBlock :items="GLOSSARIES.recurrence" />
      <p><strong>Primeros casos:</strong> sus raíces son justo los nodos de la tabla.</p>
      <div class="formula-box theory-formula">
        <MathFormula v-for="(line, i) in tex.firstCases" :key="i" :expression="line" display-mode />
      </div>
      <p><strong>Ortogonalidad:</strong> la integral del producto de dos distintos es 0.</p>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.orthogonality" display-mode /></div>
      <p><strong>Idea de por qué sirven</strong>, en palabras:</p>
      <ul>
        <li>
          Cualquier polinomio <MathFormula expression="p" /> de grado <MathFormula expression="\le 2m - 1" /> se
          puede dividir entre <MathFormula expression="P_m" />:
          <div class="formula-box theory-formula"><MathFormula :expression="tex.split" display-mode /></div>
        </li>
        <li>
          La parte <MathFormula expression="q\,P_m" /> integra 0 por la ortogonalidad (<MathFormula expression="q" />
          se escribe con <MathFormula expression="P_0, \dots, P_{m-1}" />), y la regla también le da 0, porque
          <MathFormula expression="P_m" /> vale 0 en los nodos.
        </li>
        <li>
          La parte <MathFormula expression="r" />, de grado <MathFormula expression="< m" />, la integra
          exactamente cualquier regla interpolatoria de <MathFormula expression="m" /> puntos.
        </li>
      </ul>
      <p>Por eso basta con poner los nodos en las raíces de <MathFormula expression="P_m" />.</p>
      <GlossaryBlock :items="GLOSSARIES.orthogonality" />
      <p><strong>Pesos:</strong> es lo que calcula el Resolver; los nodos se obtienen con el método de Newton.</p>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.weights" display-mode /></div>
      <GlossaryBlock :items="GLOSSARIES.weights" />
      <p class="table-note">En el Resolver, la misma fórmula se escribe así:</p>
      <div class="formula-box theory-formula"><MathFormula :expression="NODES_LATEX" display-mode /></div>
      <GlossaryBlock :items="NODES_GLOSSARY.items" />
    </div>

    <h4 class="table-caption">El error</h4>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.error" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.error" />
    <p>Constantes en <MathFormula expression="[-1, 1]" /> (con <MathFormula expression="(b - a)^{2m+1} = 2^{2m+1}" /> incluido):</p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table constants-table">
        <thead>
          <tr>
            <th>m</th>
            <th>Constante</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in ERROR_CONSTANTS" :key="c.m">
            <th scope="row">{{ c.m }}</th>
            <td><MathFormula :expression="c.c" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <ul>
      <li>
        Simpson simple en <MathFormula expression="[-1, 1]" /> tiene la constante
        <MathFormula expression="1/90" /> con 3 evaluaciones; Gauss de 2 puntos tiene
        <MathFormula expression="1/135" /> con 2.
      </li>
      <li>Las constantes bajan muy rápido: por eso cada punto extra reduce tanto el error.</li>
      <li>
        El Resolver da la cota sólo hasta <MathFormula expression="m = 5" />: la derivada de orden
        <MathFormula expression="2m" /> (<MathFormula expression="f^{(10)}" /> con <MathFormula expression="m = 5" />)
        se vuelve muy larga de calcular.
      </li>
    </ul>
    <p class="table-note">Así escribe la cota el Resolver (con <MathFormula expression="N = 1" />, <MathFormula expression="H = b - a" />):</p>
    <div class="formula-box theory-formula"><MathFormula :expression="BOUND_LATEX" display-mode /></div>
    <GlossaryBlock :items="BOUND_GLOSSARY" />
    <p>
      <strong>Comprobación</strong> (ejemplo 4 del Resolver): <MathFormula expression="x^6" /> en
      <MathFormula expression="[-1, 1]" /> con <MathFormula expression="m = 3" /> da {{ sixth.G }} frente a
      <MathFormula expression="2/7" />, con <MathFormula :expression="`E_t = ${sixth.error}`" />. La fórmula da
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.sixth" display-mode /></div>
    <p>
      Es una igualdad exacta (no sólo una cota) porque <MathFormula expression="f^{(6)} = 720" /> es constante: no
      importa dónde esté <MathFormula expression="\xi" />. El Resolver muestra la cota {{ sixth.bound }} y la marca
      «|Eₜ| = cota ✔».
    </p>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p>
      <strong>Cómo baja el error al agregar puntos</strong>: <MathFormula expression="e^{-x^2}" /> en
      <MathFormula expression="[0, 1]" /> (ejemplo 2 del Resolver, referencia {{ gaussReference }}).
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>m</th>
            <th><MathFormula expression="G_m" /></th>
            <th><MathFormula expression="E_t" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in errorRows" :key="r.m">
            <th scope="row">{{ r.m }}</th>
            <td>{{ r.G }}</td>
            <td class="nowrap">{{ r.error }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Excepción a la regla de 6 decimales: desde <MathFormula expression="m = 4" /> los errores son menores que
      0.0000005 y se verían 0, así que van con potencias de 10.
    </p>
    <ul>
      <li>
        No hay una razón fija entre un error y el siguiente, como el 0.25 del trapecio: cada punto nuevo divide el
        error entre un número cada vez más grande.
      </li>
      <li>
        Con funciones suaves, el error baja cada vez más rápido: se llama <strong>convergencia exponencial</strong>.
      </li>
      <li>
        <strong>Signo y tamaño:</strong> el mismo análisis que en los otros métodos, con
        <MathFormula expression="f^{(2m)}" />. Si esa derivada no cambia de signo en
        <MathFormula expression="[a, b]" />, <MathFormula expression="E_t" /> tiene su mismo signo (positivo: Gauss
        se queda corto; negativo: se pasa). Las derivadas de <MathFormula expression="e^{-x^2}" /> cambian de
        signo dentro de <MathFormula expression="[0, 1]" />, por eso el signo de <MathFormula expression="E_t" />
        no sigue un patrón simple. El tamaño lo marca la constante, que cae muy rápido.
      </li>
    </ul>

    <p>
      <strong>Costo: la tabla de la categoría.</strong> Evaluaciones de <MathFormula expression="f" /> para
      <MathFormula expression="|E_t| \le 0.000001" />, con la comparación de costo del Resolver:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Ejemplo</th>
            <th>Trapecio (duplicando n)</th>
            <th>Simpson 1/3 (duplicando n)</th>
            <th>Romberg</th>
            <th>Gauss</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, idx) in COST_ROWS" :key="idx">
            <th scope="row"><template v-if="r.label">{{ r.label }}</template><MathFormula v-else :expression="r.m" /></th>
            <td>{{ r.trapezoid }}</td>
            <td>{{ r.simpson }}</td>
            <td>{{ r.romberg }}</td>
            <td><strong>{{ r.gauss }}</strong></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 6. Funciones singulares -->
    <div class="more-card">
      <p class="more-title">Cuándo Gauss no es suficiente: funciones singulares</p>
      <p>
        <MathFormula expression="1/\sqrt{x}" /> en <MathFormula expression="[0, 1]" /> (ejemplo 5 del Resolver,
        exacta 2):
      </p>
      <ul>
        <li>
          <strong>Ventaja:</strong> Gauss <strong>no evalúa los extremos</strong>, así que puede integrarla aunque
          <MathFormula expression="f(0)" /> no exista. El trapecio, Simpson y Romberg ni siquiera pueden empezar.
        </li>
        <li>
          <strong>Limitación:</strong> converge muy lento. Con <MathFormula expression="m = 1" /> a 6 da
          {{ root.first.join(', ') }}; con <MathFormula expression="m = 12" />, {{ root.m12 }}. La función no es
          suave en 0: sus derivadas crecen sin límite.
        </li>
        <li>
          <strong>La versión compuesta ayuda poco:</strong> con <MathFormula expression="m = 4" /> y
          <MathFormula expression="N = 1, 4, 16, 64" /> da
          {{ ROOT_COMPOSITE.map((r) => r.value).join(', ') }} ({{ ROOT_COMPOSITE.at(-1).evaluations }} evaluaciones y
          todavía con error 0.024).
        </li>
      </ul>
      <div class="resolver-detail">
        <TrapezoidChart
          :curve="ROOT_EXAMPLE.curve"
          :row="rootRow(rootM)"
          :title="`1/√x en [0, 1] (m = ${rootM})`"
          :area-label="root.area(rootM)"
          :curve-label="root.curveLabel"
        >
          <div class="row-picker" role="radiogroup" aria-label="Puntos del gráfico de 1/√x">
            <span class="picker-label">Puntos:</span>
            <button
              v-for="m in ROOT_CHART_MS"
              :key="m"
              type="button"
              role="radio"
              class="row-btn"
              :class="{ 'is-active': m === rootM }"
              :aria-checked="m === rootM"
              @click="rootM = m"
            >
              m = {{ m }}
            </button>
          </div>
        </TrapezoidChart>
      </div>
      <p class="table-note">
        Cerca de 0 la curva sube sin límite: los rectángulos nunca llegan a cubrir esa zona, y por eso el área se
        queda corta.
      </p>
      <p>
        <strong>Para saber más:</strong> con el cambio de variable <MathFormula expression="x = u^2" />
        (<MathFormula expression="dx = 2u\,du" />), la integral se vuelve
        <MathFormula expression="\int_0^1 \frac{2u}{u}\,du = \int_0^1 2\,du = 2" />, que cualquier método calcula
        exacto. Cambiar la variable para quitar la singularidad es lo que hacen los programas profesionales, junto
        con métodos adaptativos como Gauss-Kronrod (los que usan <code>scipy.integrate.quad</code> y QUADPACK).
      </p>
      <p>
        <strong>Otro ejemplo del Resolver:</strong> <MathFormula expression="\frac{\sin x}{x}" /> en
        <MathFormula expression="[0, \pi]" /> no está definida en 0 (referencia 1.851937). Aquí Gauss sí converge
        rápido (<MathFormula expression="m = 4" /> ya da 1.851937), porque la función es suave aunque la fórmula no
        pueda evaluarse en 0.
      </p>
    </div>

    <!-- 7. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 8. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS" />

    <!-- 9. Ejemplo resuelto -->
    <h3 id="ejemplo-gauss">Ejemplo resuelto: polinomio de Chapra en [0, 0.8]</h3>
    <p>Integremos (ejemplo 1 del Resolver, de Chapra y Canale)</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.fn" display-mode /></div>
    <p>en <MathFormula expression="[0, 0.8]" /> con tolerancia {{ example.tolerance }}. La integral exacta es</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.integral" display-mode /></div>
    <p>
      Cambio de variable: <MathFormula expression="x = 0.4 + 0.4t" />. Todos los valores que siguen son los que
      calcula la aplicación, con los mismos componentes del paso a paso del Resolver.
    </p>
    <p>
      <RouterLink :to="RESOLVE_EXAMPLE" class="btn btn-primary">Resolver este ejemplo</RouterLink>
    </p>

    <div v-for="m in [2, 3]" :key="m" class="worked-step">
      <p class="worked-step-title">
        Gauss de {{ m }} puntos: <MathFormula :expression="`G_{${m}} = ${example.G(m)}`" />
      </p>
      <div class="resolver-detail">
        <GaussStepDetail :result="FUNCTION_EXAMPLE" :row="example.row(m)" :previous="example.row(m - 1)" />
      </div>
      <p v-if="m === 3">
        <strong>Exacto:</strong> <MathFormula expression="f" /> es de grado 5 = 2·3 − 1.
      </p>
    </div>

    <p>
      <strong>Resto de las filas.</strong> La tabla de refinamiento del Resolver. El método se detiene en la
      <strong>fila {{ example.rowsUsed }}</strong>, por el mínimo de 6 filas (el error estimado ya era 0 desde la
      fila 4).
    </p>
    <div class="table-scroll">
      <table class="iterations-table">
        <thead>
          <tr>
            <th v-for="col in HEADERS" :key="col.key">
              <InfoTip :text="col.text">{{ col.label }}</InfoTip>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in example.rows" :key="row.m">
            <td>{{ row.m }}</td>
            <td>{{ row.evaluations }}</td>
            <td>{{ cell(row.G) }}</td>
            <td>{{ cell(row.estimated_error) }}</td>
            <td>{{ cell(row.true_error) }}</td>
            <td>{{ percent(row.relative_error) }}</td>
            <td>{{ row.bound === null ? 'no disponible' : cell(row.bound) }}</td>
            <td class="mark-cell">
              <span v-if="row.within_bound !== null" :class="row.within_bound ? 'mark mark-ok' : 'mark mark-warn'">{{ boundMark(row) }}</span>
              <template v-else>—</template>
              <sup v-if="row.by_rounding" class="rounding-mark" title="Sólo dentro del margen de redondeo R">R</sup>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p>
      <strong>Momentos con <MathFormula expression="m = 3" /></strong>: la regla integra exacto
      <MathFormula expression="t^k" /> hasta <MathFormula expression="k = 5" />, y con
      <MathFormula expression="k = 6" /> ya no (0.24 frente a <MathFormula expression="2/7" />).
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>k</th>
            <th><MathFormula expression="\sum w_i t_i^k" /></th>
            <th><MathFormula expression="\int_{-1}^{1} t^k\,dt" /></th>
            <th>¿Coincide?</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in moments3" :key="r.k">
            <th scope="row">{{ r.k }}</th>
            <td>{{ r.value }}</td>
            <td><MathFormula :expression="r.exact" /></td>
            <td>
              <span :class="r.ok ? 'mark mark-ok' : 'mark mark-warn'">{{ r.ok ? '✔' : '✘' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="resolver-detail">
      <GaussVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      La comprobación del Resolver usa la última fila (<MathFormula expression="m = 6" />): sus momentos son exactos
      hasta <MathFormula expression="k = 11" />. Costo: Gauss 3 evaluaciones, Romberg 5, Simpson 65 y trapecio 2049.
    </p>

    <p><strong>Comparación con 3 evaluaciones</strong> (Chapra):</p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Método</th>
            <th>Resultado</th>
            <th>Error <MathFormula expression="\varepsilon_t" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in THREE_EVALUATIONS" :key="r.method">
            <th scope="row">{{ r.method }}</th>
            <td>{{ r.value }}</td>
            <td>{{ r.error }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p>
      Y con 2 evaluaciones: el trapecio simple da 0.1728 (89.47 %) y Gauss de 2 puntos,
      {{ example.G(2) }} ({{ percent(example.row(2).relative_error) }}).
    </p>

    <h4 class="table-caption">Mini-ejemplo de la versión compuesta (ejemplo 7, N = 2)</h4>
    <p>
      Subintervalos <MathFormula expression="[0, 0.4]" /> y <MathFormula expression="[0.4, 0.8]" />, con
      <MathFormula expression="H = 0.4" /> y centros <MathFormula expression="c_1 = 0.2" />,
      <MathFormula expression="c_2 = 0.6" />. Con <MathFormula expression="m = 2" />, los nodos son
      {{ composite.nodes.join(', ') }} y el resultado es {{ composite.G2 }}
      (<MathFormula :expression="`E_t = ${composite.E2}`" />); con <MathFormula expression="m = 3" />, exacto
      ({{ composite.G3 }}).
    </p>
    <details class="group-details">
      <summary>Paso a paso de m = 2 con N = 2</summary>
      <div class="resolver-detail">
        <GaussStepDetail :result="COMPOSITE_EXAMPLE" :row="composite.row" :previous="composite.previous" />
      </div>
    </details>
  </div>

  <!-- 10. Tabla comparativa (compartida por la categoría) -->
  <IntegrationComparisonSection />

  <!-- 11. Guía de la categoría -->
  <div class="card">
    <h2>¿Qué método de integración usar?</h2>
    <ul class="guide">
      <li><strong>Datos medidos con espaciado desigual:</strong> el trapecio.</li>
      <li>
        <strong>Datos igualmente espaciados:</strong> Simpson (con la combinación 1/3 + 3/8 si
        <MathFormula expression="n" /> es impar); Romberg, si hay <MathFormula expression="2^m + 1" /> datos y la
        función es suave.
      </li>
      <li>
        <strong>Se tiene la fórmula de <MathFormula expression="f" /> y es suave:</strong> Gauss (menos
        evaluaciones) o Romberg (si se quiere aprovechar cada evaluación al refinar).
      </li>
      <li>
        <strong><MathFormula expression="f" /> no definida en un extremo:</strong> Gauss; si converge lento,
        cambiar la variable.
      </li>
      <li><strong>Para aprender o revisar a mano:</strong> el trapecio y Simpson, por su sencillez.</li>
    </ul>
  </div>
</template>

<style scoped>
.table-scroll + p,
.table-scroll + ul {
  margin-top: var(--space-4);
}

.nodes-table td {
  white-space: nowrap;
}

.constants-table {
  max-width: 320px;
}

.nowrap {
  white-space: nowrap;
}

.live-values {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-5);
  margin-bottom: var(--space-3);
}

.iterations-table td,
.iterations-table th {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.mark-cell {
  text-align: center !important;
}

.rounding-mark {
  margin-left: 2px;
  color: var(--color-ink-muted);
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

/* Los componentes de Resolver traen su propia lista .steps: aquí recupera el
   aspecto que tiene en Resolver (igual que en Romberg). */
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
