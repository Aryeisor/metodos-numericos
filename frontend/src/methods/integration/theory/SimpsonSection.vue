<script setup>
// Teoría propia del método de Simpson, en el mismo orden que la del trapecio:
// definición formal (1/3 y 3/8, simples y compuestas, y la combinación para n
// impar), interpretación geométrica (figura con selector de regla y de n),
// derivación (pesos por Lagrange, punto medio + trapecio, exactitud para
// cúbicas, el error, 1/3 frente a 3/8 y Richardson), error y convergencia,
// restricciones, algoritmo, el ejemplo de Chapra con datos reales del solver
// y la tabla comparativa de la categoría. El fundamento común y las
// referencias los pone la página.
import GlossaryBlock from '../../../components/GlossaryBlock.vue'
import MathFormula from '../../../components/MathFormula.vue'
import TrapezoidChart from '../../../components/TrapezoidChart.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { solveRouteName } from '../../routeNames'
import IntegrationRefinementTable from '../IntegrationRefinementTable.vue'
import SimpsonPointsTable from '../SimpsonPointsTable.vue'
import SimpsonVerification from '../SimpsonVerification.vue'
import TrapezoidStepDetail from '../TrapezoidStepDetail.vue'
import { cell } from '../formulas'
import { simpsonRowSteps, weightReason } from '../simpsonExplain'
import { SIMPSON_GLOSSARIES } from '../simpsonGlossary'
import TrapezoidFigure from './TrapezoidFigure.vue'
import { chapra } from './trapezoidContent'
import {
  ALGORITHM_STEPS,
  APPROX_GLOSSARY,
  BLOCK_13,
  BLOCK_38,
  BOUND_GLOSSARY_13,
  CHAPRA_EXACT,
  FUNCTION_EXAMPLE,
  GLOSSARIES,
  PRECAUTIONS,
  TABLE_EXAMPLE,
  combination,
  convergenceRows,
  example,
  tex,
} from './simpsonContent'

const CHAPRA_TICKS = [0, 0.2, 0.4, 0.6, 0.8].map((x) => ({ x, label: String(x) }))
const FIGURE_RULES = [
  { key: 'trapecio', nValues: [2, 4, 8, 16] },
  { key: 'simpson13', nValues: [2, 4, 8, 16] },
  { key: 'simpson38', nValues: [3, 6, 12] },
]
// El Resolver carga el ejemplo con ?ejemplo=<id> y lo resuelve.
const RESOLVE_EXAMPLE = { name: solveRouteName('simpson'), query: { ejemplo: 'simp-chapra' } }

const steps = (block, item) => simpsonRowSteps(FUNCTION_EXAMPLE, block.rule, item.row, item.k, item.previous)
const reason13 = (i, count) => weightReason(BLOCK_13.rule, i, count)
const reason38 = (i, count) => weightReason(BLOCK_38.rule, i, count)
</script>

<template>
  <div id="metodo-simpson" class="card">
    <h2>Método de Simpson</h2>

    <!-- 1. Introducción (el fundamento común va arriba, en la página) -->
    <p>
      El trapecio une los puntos con <strong>rectas</strong> y su error es <MathFormula expression="O(h^2)" />.
      Simpson los une con <strong>parábolas</strong> (regla 1/3) o con <strong>curvas de grado 3</strong>
      (regla 3/8). Con los mismos puntos, el error baja a <MathFormula expression="O(h^4)" />. Es la regla más
      usada en la práctica cuando los datos están igualmente espaciados.
    </p>

    <!-- 2. Definición formal -->
    <h3>Definición formal</h3>
    <p>
      <strong>Simpson 1/3 simple</strong> (3 puntos, <MathFormula expression="h = (b - a)/2" />):
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.simple13" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.simple13" :summary="GLOSSARIES.simple13Summary" />

    <p>
      <strong>Simpson 1/3 compuesta</strong> (<MathFormula expression="n" /> par,
      <MathFormula expression="h = (b - a)/n" />, <MathFormula expression="x_i = a + i\,h" />):
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.composite13" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.composite13" :summary="GLOSSARIES.composite13Summary" />

    <p>
      <strong>Simpson 3/8 simple</strong> (4 puntos, <MathFormula expression="h = (b - a)/3" />):
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.simple38" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.simple38" />

    <p>
      <strong>Simpson 3/8 compuesta</strong> (<MathFormula expression="n" /> múltiplo de 3): los pesos son
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.weights38" display-mode /></div>
    <p>es decir,</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.composite38" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.composite38" :summary="SIMPSON_GLOSSARIES.simpson38.summary" />

    <p>
      <strong>Combinación para <MathFormula expression="n" /> impar</strong> (Chapra): con un número impar de
      segmentos no se puede usar sólo 1/3 ni, en general, sólo 3/8. Se usa Simpson 1/3 en los primeros
      <MathFormula expression="n - 3" /> segmentos (que es par) y 3/8 en los últimos 3:
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.combination" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.combination" />

    <!-- 3. Interpretación geométrica -->
    <h3>Interpretación geométrica</h3>
    <p>
      Cada regla reemplaza la curva por piezas fáciles de integrar: rectas (trapecio), parábolas de 3 puntos
      (1/3) o cúbicas de 4 puntos (3/8). Con la función de Chapra,
      <MathFormula expression="f(x) = 0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5" /> en
      <MathFormula expression="[0, 0.8]" />, elige la regla y el número de segmentos:
    </p>
    <TrapezoidFigure
      :f="chapra"
      :a="0"
      :b="0.8"
      :exact="CHAPRA_EXACT"
      :rules="FIGURE_RULES"
      :ticks="CHAPRA_TICKS"
      label="f(x) de Chapra"
    />
    <p class="table-note">
      Calculado en el navegador, sólo como ilustración. Las piezas alternan dos tonos para que se vea dónde
      empieza y termina cada una.
    </p>
    <p>
      <strong>Lectura:</strong> con <MathFormula expression="n = 2" />, las dos rectas del trapecio se pierden
      casi todo el «lomo» de la curva (error 0.571733). Una sola parábola por los mismos 3 puntos lo sigue mucho
      mejor (error 0.273067). Con <MathFormula expression="n = 4" /> la diferencia ya es enorme: 0.155733
      frente a 0.017067.
    </p>

    <!-- 4. Derivación -->
    <h3>Derivación</h3>

    <h4 class="table-caption">De dónde salen los pesos 1, 4, 1</h4>
    <ol>
      <li>
        Para simplificar, se ponen los tres puntos en <MathFormula expression="-h" />,
        <MathFormula expression="0" /> y <MathFormula expression="h" />: mover el eje a la izquierda o a la
        derecha no cambia el área.
      </li>
      <li>
        Se escribe la parábola que pasa por los tres puntos con el polinomio de Lagrange:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrange" display-mode /></div>
        <GlossaryBlock :items="GLOSSARIES.lagrange" />
      </li>
      <li>
        Se integra cada fracción entre <MathFormula expression="-h" /> y <MathFormula expression="h" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrangeIntegrals" display-mode /></div>
        Por ejemplo, la primera, línea por línea: se saca la constante <MathFormula expression="1/(2h^2)" /> y
        se desarrolla el producto; se integra cada potencia y se evalúa entre <MathFormula expression="-h" /> y
        <MathFormula expression="h" /> (el término <MathFormula expression="h\,x^2/2" /> se cancela porque vale lo
        mismo en los dos extremos):
        <div class="formula-box theory-formula">
          <MathFormula v-for="(line, i) in tex.lagrangeFirst" :key="i" :expression="line" display-mode />
        </div>
      </li>
      <li>
        Se suman los tres resultados, cada uno multiplicado por su altura:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrangeResult" display-mode /></div>
        Con <MathFormula expression="h = 1" />, los pesos verificados son:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrangeCheck" display-mode /></div>
      </li>
    </ol>
    <p>
      En una línea: con 4 puntos y una cúbica, el mismo procedimiento da los pesos (verificados con
      <MathFormula expression="h = 1" />)
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.lagrange38" display-mode /></div>

    <div class="more-card">
      <p class="more-title">Para saber más: Simpson como promedio de dos reglas</p>
      <p>La regla del <strong>punto medio</strong> usa un solo rectángulo con la altura del centro:</p>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.midpoint" display-mode /></div>
      <p>
        Su error tiene el signo opuesto al del trapecio y es más o menos la mitad. Línea por línea: el error de
        <MathFormula expression="M" /> es <MathFormula expression="-1/2" /> del de <MathFormula expression="T" />;
        así que, al sumar dos veces el error de <MathFormula expression="M" /> y una vez el de
        <MathFormula expression="T" />, se cancelan:
      </p>
      <div class="formula-box theory-formula">
        <MathFormula v-for="(line, i) in tex.midTrapWhy" :key="i" :expression="line" display-mode />
      </div>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.midTrap" display-mode /></div>
      <GlossaryBlock :items="GLOSSARIES.midTrap" />
      <p>Ejemplo verificado (Chapra):</p>
      <div class="formula-box theory-formula"><MathFormula :expression="tex.midTrapCheck" display-mode /></div>
      <p class="formula-legend">Es exactamente el resultado de Simpson 1/3 con <MathFormula expression="n = 2" />.</p>
    </div>

    <h4 class="table-caption">La sorpresa: Simpson es exacta para cúbicas</h4>
    <ul>
      <li>
        La parábola es de grado 2, pero Simpson 1/3 integra <strong>exactamente</strong> cualquier polinomio de
        grado 3.
      </li>
      <li>
        <strong>Por simetría:</strong> sobre <MathFormula expression="[-h, h]" />, la integral de
        <MathFormula expression="x^3" /> es 0 (las áreas a cada lado se cancelan), y la regla también da 0:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.cubicSymmetry" display-mode /></div>
        El término cúbico «se cancela gratis»: la regla acierta en él sin haberlo buscado.
      </li>
      <li>
        Ejemplo verificado, con <MathFormula expression="n = 2" /> (<MathFormula expression="h = 1" />):
        <div class="formula-box theory-formula"><MathFormula :expression="tex.cubicCheck" display-mode /></div>
      </li>
      <li>
        Por eso el error depende de <MathFormula expression="f^{(4)}" /> y no de
        <MathFormula expression="f'''" />: el primer término que la regla no reproduce es el de
        <MathFormula expression="x^4" />.
      </li>
    </ul>

    <h4 class="table-caption">El error</h4>
    <p><strong>Regla simple</strong> (una parábola o una cúbica en todo <MathFormula expression="[a, b]" />):</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.simpleErrors" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.simpleErrors" />
    <p>
      <strong>Regla compuesta:</strong> igual que en el trapecio, se suman los errores de cada pieza. Para 1/3,
      línea por línea: cada parábola tiene ancho <MathFormula expression="2h" />, así que su error lleva
      <MathFormula expression="(2h)^5/2880" />; hay <MathFormula expression="n/2" /> parábolas, y como
      <MathFormula expression="n\,h = b - a" />:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula v-for="(line, i) in tex.compositeSteps13" :key="i" :expression="line" display-mode />
    </div>
    <p>Para 3/8, lo mismo con cúbicas de ancho <MathFormula expression="3h" />:</p>
    <div class="formula-box theory-formula">
      <MathFormula v-for="(line, i) in tex.compositeSteps38" :key="i" :expression="line" display-mode />
    </div>
    <p>Con el promedio de <MathFormula expression="f^{(4)}" /> en las piezas queda:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.compositeErrors" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.compositeErrors" />
    <p>De aquí salen dos fórmulas que usa el Resolver:</p>
    <ul>
      <li>
        La <strong>cota</strong>: se reemplaza el promedio por el máximo <MathFormula expression="M_4" /> (el
        peor caso; ver «Error y convergencia»).
      </li>
      <li>
        El <strong>error aproximado de Chapra</strong>: se usa el promedio exacto de
        <MathFormula expression="f^{(4)}" /> en <MathFormula expression="[a, b]" />. Como la integral de
        <MathFormula expression="f^{(4)}" /> es <MathFormula expression="f'''" />:
        <div class="formula-box theory-formula"><MathFormula :expression="tex.meanFourth" display-mode /></div>
        <div class="formula-box theory-formula"><MathFormula :expression="tex.approx13" display-mode /></div>
        <GlossaryBlock :items="APPROX_GLOSSARY.items" />
      </li>
    </ul>
    <p>
      <strong>Comprobación con números</strong> (igualdad exacta, porque
      <MathFormula expression="f^{(4)} = 24" /> es constante):
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="`x^4 \\text{ en } [-1, 1]\\ (1/3):\\quad ${tex.quarticCheck13}`" display-mode />
      <MathFormula :expression="`x^4 \\text{ en } [0, 3]\\ (3/8):\\quad ${tex.quarticCheck38}`" display-mode />
    </div>
    <p>
      <strong>Ejemplo de Chapra</strong> (valores del solver): la cuarta derivada es lineal y su promedio sale de
      <MathFormula expression="f'''" /> en los extremos:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="example.fourth" display-mode />
      <MathFormula :expression="example.meanFourth" display-mode />
      <MathFormula :expression="`n = 2:\\quad ${example.approxN2}`" display-mode />
    </div>
    <p class="formula-legend">
      <MathFormula expression="E_a" /> coincide exactamente con <MathFormula expression="E_t" /> porque en este
      polinomio <MathFormula expression="f^{(5)}" /> es constante: <MathFormula expression="f^{(4)}" /> cambia en
      línea recta, y su promedio describe exactamente el error.
    </p>

    <h4 class="table-caption">¿1/3 o 3/8?</h4>
    <p>Se presta a confusión, porque la respuesta depende de qué se compara:</p>
    <ul>
      <li>
        <strong>Como regla simple sobre el mismo intervalo <MathFormula expression="[a, b]" />,</strong> la 3/8
        tiene la constante menor (<MathFormula expression="1/6480" /> frente a
        <MathFormula expression="1/2880" />), pero usa 4 puntos en vez de 3.
      </li>
      <li>
        <strong>Con los mismos puntos (mismo <MathFormula expression="h" />),</strong> la 1/3 es más precisa
        (<MathFormula expression="h^4/180" /> frente a <MathFormula expression="h^4/80" />). Ejemplo verificado
        con Chapra y <MathFormula expression="n = 6" />: 1/3 da 1.637162 (error 0.003371) y 3/8 da
        {{ cell(BLOCK_38.rows[1].S) }} (error {{ cell(BLOCK_38.rows[1].true_error) }}).
      </li>
      <li>
        <strong>Conclusión:</strong> se prefiere 1/3, y 3/8 se usa sobre todo para cubrir un número
        <strong>impar</strong> de segmentos (la combinación de Chapra).
      </li>
    </ul>

    <h4 class="table-caption">Simpson como trapecio mejorado (Richardson)</h4>
    <p>
      Es el puente que se anunció en la teoría del trapecio. Por Euler-Maclaurin, el error del trapecio es
      aproximadamente <MathFormula expression="c\,h^2" />. Línea por línea: el trapecio con
      <MathFormula expression="n/2" /> segmentos (ancho <MathFormula expression="2h" />); con
      <MathFormula expression="n" /> segmentos (ancho <MathFormula expression="h" />), con un error 4 veces menor;
      y al combinar, el término <MathFormula expression="c\,h^2" /> se cancela:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula v-for="(line, i) in tex.richardsonWhy" :key="i" :expression="line" display-mode />
    </div>
    <p>de donde</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.richardson" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.richardson" />
    <p>
      Lo que queda es <MathFormula expression="O(h^4)" />. Ejemplo verificado con los valores del solver:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="`${tex.richardsonCheck} = S_2\\ \\checkmark`" display-mode />
    </div>
    <p>
      Si se repite la combinación con los resultados de Simpson se obtiene <MathFormula expression="O(h^6)" />, y
      así sucesivamente: eso es la <strong>integración de Romberg</strong>, la próxima página.
    </p>

    <!-- 5. Error y convergencia -->
    <h3>Error y convergencia</h3>
    <p><strong>Cotas</strong> que usa el sistema:</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.bounds" display-mode /></div>
    <GlossaryBlock :items="BOUND_GLOSSARY_13.items" />
    <p>
      Trapecio y Simpson 1/3 con los mismos <MathFormula expression="n" />, tal como los calcula el solver
      (ejemplo de Chapra, exacta {{ cell(CHAPRA_EXACT) }}):
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table convergence-table">
        <thead>
          <tr>
            <th>n</th>
            <th>Trapecio</th>
            <th><MathFormula expression="E_t" /></th>
            <th>Simpson 1/3</th>
            <th><MathFormula expression="E_t" /></th>
            <th>Razón</th>
            <th>Veces menor que el trapecio</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in convergenceRows" :key="r.n">
            <td>{{ r.n }}</td>
            <td>{{ cell(r.T) }}</td>
            <td>{{ cell(r.Et_T) }}</td>
            <td>{{ cell(r.S) }}</td>
            <td>{{ cell(r.Et_S) }}</td>
            <td>{{ cell(r.ratio) }}</td>
            <td>{{ r.times }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <ul class="table-note">
      <li>
        Aquí la razón es exactamente <MathFormula expression="1/16 = 0.0625" /> desde la primera fila: el
        polinomio es de grado 5, así que el error de Simpson sólo tiene el término en
        <MathFormula expression="h^4" />. En general, la razón <strong>tiende</strong> a 0.0625.
      </li>
      <li>
        Ejemplo 2 del Resolver (<MathFormula expression="e^{-x^2}" /> en <MathFormula expression="[0, 1]" />):
        Simpson 1/3 con <MathFormula expression="n = 2, 4, 8" /> tiene errores de unos 0.000356, 0.000031 y
        0.000002; el trapecio, 0.015454, 0.00384 y 0.000959.
      </li>
    </ul>
    <ul>
      <li>
        <strong>Eficiencia</strong> (Chapra): para un error verdadero
        <MathFormula expression="\le 0.000001" />, el trapecio necesita <MathFormula expression="n = 1600" />
        (1601 evaluaciones de <MathFormula expression="f" />), Simpson 1/3 necesita
        <MathFormula expression="n = 46" /> (47 evaluaciones) y Simpson 3/8, <MathFormula expression="n = 57" />
        (58 evaluaciones). Simpson logra lo mismo con unas <strong>34 veces menos</strong> evaluaciones.
      </li>
      <li>
        <strong>Exactitud:</strong> las dos reglas son exactas para polinomios de grado
        <MathFormula expression="\le 3" />, porque entonces <MathFormula expression="f^{(4)} = 0" />. Ejemplo del
        Resolver: <MathFormula expression="x^3" /> en <MathFormula expression="[0, 2]" /> da 4 con las dos reglas
        y cualquier <MathFormula expression="n" />.
      </li>
      <li>
        <strong>Signo del error:</strong> <MathFormula expression="E_t" /> tiene el signo contrario al de
        <MathFormula expression="f^{(4)}" />. Si <MathFormula expression="f^{(4)} > 0" />, Simpson
        <strong>sobreestima</strong>: <MathFormula expression="\sin x" /> en <MathFormula expression="[0, \pi]" />
        (donde <MathFormula expression="f^{(4)} = \sin x > 0" />) da 2.094395, 2.00456 y 2.000269 con
        <MathFormula expression="n = 2, 4, 8" />, frente a 2. Si <MathFormula expression="f^{(4)} < 0" />,
        subestima.
      </li>
    </ul>

    <!-- 6. Restricciones -->
    <h3>Restricciones y precauciones</h3>
    <AlgorithmSteps :steps="PRECAUTIONS" />

    <!-- 7. Algoritmo -->
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS" />
    <p class="table-note">
      En el modo <strong>Tabla de datos</strong> no hay refinamiento: el espaciado debe ser uniforme y, con
      <MathFormula expression="n" /> impar, se usa la combinación 1/3 + 3/8.
    </p>

    <!-- 8. Ejemplo resuelto -->
    <h3 id="ejemplo-simpson">Ejemplo resuelto: polinomio de Chapra en [0, 0.8]</h3>
    <p>Integremos</p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.fn" display-mode /></div>
    <p>
      en <MathFormula expression="[0, 0.8]" /> con las dos reglas (<MathFormula expression="n_0 = 2" /> para 1/3
      y <MathFormula expression="n_0 = 3" /> para 3/8) y tolerancia {{ example.tolerance }}. La integral exacta es
    </p>
    <div class="formula-box theory-formula"><MathFormula :expression="example.integral" display-mode /></div>
    <p>
      Además, <MathFormula expression="\bar{f}^{(4)} = -2400" /> y
      <MathFormula :expression="`M_4 = ${example.M4}`" /> (en <MathFormula :expression="`x = ${example.M4x}`" />).
      Todos los valores que siguen son los que calcula la aplicación, con los mismos componentes del paso a paso
      del Resolver. Al refinar, <span class="legend-prev">la fila anterior</span> va en azul y
      <span class="legend-current">los valores nuevos</span>, en verde.
    </p>
    <p>
      <RouterLink :to="RESOLVE_EXAMPLE" class="btn btn-primary">Resolver este ejemplo</RouterLink>
    </p>

    <h4 class="table-caption">Simpson 1/3</h4>
    <div v-for="item in example.steps13" :key="`s13-${item.k}`" class="worked-step">
      <p class="worked-step-title">
        Fila {{ item.k }} (<MathFormula :expression="`n = ${item.row.n},\\ h = ${item.row.h.latex}`" />):
        <MathFormula :expression="`S = ${example.S13(item.k)}`" />
      </p>
      <div class="resolver-detail">
        <TrapezoidStepDetail
          :result="FUNCTION_EXAMPLE"
          :row="item.row"
          :k="item.k"
          :previous="item.previous"
          :custom-steps="steps(BLOCK_13, item)"
          :weight-reason="reason13"
        />
      </div>
    </div>
    <p>
      Resumen de la fila 1: <MathFormula :expression="`S = (0.4/3) \\cdot 10.256 = ${example.S13(1)}`" />,
      <MathFormula :expression="`E_t = ${example.Et13}`" /> ({{ example.rel13 }}),
      <MathFormula :expression="`E_a = ${example.Ea13}`" /> y cota {{ example.bound13 }}
      (<MathFormula :expression="`M_4 = ${example.M4}`" /> en <MathFormula :expression="`x = ${example.M4x}`" />).
      La identidad con el trapecio:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="`${example.identity}\\ \\checkmark`" display-mode />
    </div>

    <h4 class="table-caption">Simpson 3/8</h4>
    <div class="worked-step">
      <p class="worked-step-title">
        Fila 1 (<MathFormula :expression="`n = ${example.step38.row.n},\\ h = ${example.step38.row.h.latex}`" />):
        <MathFormula :expression="`S = ${example.S38(1)}`" />
      </p>
      <div class="resolver-detail">
        <TrapezoidStepDetail
          :result="FUNCTION_EXAMPLE"
          :row="example.step38.row"
          :k="1"
          :custom-steps="steps(BLOCK_38, example.step38)"
          :weight-reason="reason38"
        />
      </div>
    </div>
    <p>
      Resumen: <MathFormula :expression="`S = ${example.S38(1)}`" />,
      <MathFormula :expression="`E_t = ${example.Et38}`" /> ({{ example.rel38 }}).
    </p>

    <p>
      <strong>Resto de las filas.</strong> Las dos tablas completas, como las devuelve el solver; despliega
      cualquier fila para ver su cálculo. El método se detiene en la <strong>fila {{ example.rowsUsed }}</strong>
      (<MathFormula :expression="`n = ${example.lastN13}`" /> para 1/3 y
      <MathFormula :expression="`n = ${example.lastN38}`" /> para 3/8): la primera en que las dos reglas tienen
      el error estimado <MathFormula :expression="`\\le ${example.tolerance}`" /> y hay al menos 6 filas. La
      comprobación integra <MathFormula expression="f" /> término a término y evalúa
      <MathFormula expression="F(0.8) - F(0)" />.
    </p>
    <div class="resolver-detail">
      <p class="table-caption">Simpson 1/3</p>
      <IntegrationRefinementTable :result="FUNCTION_EXAMPLE" :block="BLOCK_13" />
      <p class="table-caption">Simpson 3/8</p>
      <IntegrationRefinementTable :result="FUNCTION_EXAMPLE" :block="BLOCK_38" />
      <SimpsonVerification :result="FUNCTION_EXAMPLE" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>Polinomio de Chapra en [0, 0.8]</strong> de la vista
      <RouterLink :to="{ name: solveRouteName('simpson') }"><strong>Resolver</strong></RouterLink>: el botón
      «Resolver este ejemplo» lo carga y lo resuelve.
    </p>

    <h4 class="table-caption">Mini-ejemplo de la combinación (n impar)</h4>
    <p>
      {{ combination.n + 1 }} datos del mismo polinomio, con <MathFormula :expression="`h = ${combination.h}`" />:
      <MathFormula :expression="`n = ${combination.n}`" /> segmentos, un número impar. Simpson 1/3 en
      <MathFormula :expression="combination.interval13" /> da {{ combination.S13 }} y Simpson 3/8 en
      <MathFormula :expression="combination.interval38" /> da {{ combination.S38 }}: en total
      <strong>{{ combination.total }}</strong>, con <MathFormula :expression="`E_t = ${combination.Et}`" />
      ({{ combination.relative }}). El punto de unión <MathFormula :expression="`x = ${combination.junction}`" />
      pertenece a las dos partes: su peso es 1 + 1.
    </p>
    <div class="resolver-detail">
      <TrapezoidChart
        :curve="TABLE_EXAMPLE.curve"
        :row="combination.app.chart_row"
        title="Combinación 1/3 + 3/8"
        :area-label="combination.areaLabel"
        :curve-label="combination.curveLabel"
        :part-labels="combination.partLabels"
      />
      <SimpsonPointsTable :result="TABLE_EXAMPLE" :app="combination.app" />
    </div>
    <p class="table-note">
      Es el ejemplo <strong>Tabla de Chapra con n = 5 (combinación 1/3 + 3/8)</strong> de Resolver.
    </p>
  </div>

  <!-- 9. Tabla comparativa -->
  <div class="card">
    <h2>Integración numérica: comparación de la categoría</h2>
    <p>
      El trapecio y las dos reglas de Simpson, frente a lo que vendrá. Romberg y Gauss se detallan en su página.
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Aspecto</th>
            <th>Trapecio</th>
            <th>Simpson 1/3</th>
            <th>Simpson 3/8</th>
            <th>Romberg</th>
            <th>Gauss</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Aproxima f con</th>
            <td>Rectas</td>
            <td>Parábolas (3 puntos)</td>
            <td>Cúbicas (4 puntos)</td>
            <td>Se detalla en su página</td>
            <td>Se detalla en su página</td>
          </tr>
          <tr>
            <th scope="row">Pesos</th>
            <td><MathFormula expression="1, 2, \dots, 2, 1 \cdot \tfrac{h}{2}" /></td>
            <td><MathFormula expression="1, 4, 2, \dots, 4, 1 \cdot \tfrac{h}{3}" /></td>
            <td><MathFormula expression="1, 3, 3, 2, \dots, 3, 3, 1 \cdot \tfrac{3h}{8}" /></td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Condición sobre n</th>
            <td>Cualquiera</td>
            <td>Par</td>
            <td>Múltiplo de 3</td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Error compuesto</th>
            <td><MathFormula expression="-\frac{(b - a)h^2}{12} f''" /></td>
            <td><MathFormula expression="-\frac{(b - a)h^4}{180} f^{(4)}" /></td>
            <td><MathFormula expression="-\frac{(b - a)h^4}{80} f^{(4)}" /></td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Orden</th>
            <td><MathFormula expression="O(h^2)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Exacta para grado</th>
            <td><MathFormula expression="\le 1" /></td>
            <td><MathFormula expression="\le 3" /></td>
            <td><MathFormula expression="\le 3" /></td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Espaciado desigual</th>
            <td>Sí</td>
            <td>No</td>
            <td>No</td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">Chapra, menor n</th>
            <td>{{ example.T1 }} (<MathFormula expression="n = 1" />)</td>
            <td>{{ example.S13(1) }} (<MathFormula expression="n = 2" />)</td>
            <td>{{ example.S38(1) }} (<MathFormula expression="n = 3" />)</td>
            <td>—</td>
            <td>—</td>
          </tr>
          <tr>
            <th scope="row">
              Evaluaciones para <MathFormula expression="|E_t| \le 0.000001" /> en Chapra
            </th>
            <td>1601</td>
            <td>47</td>
            <td>58</td>
            <td>—</td>
            <td>—</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      La próxima página (Romberg) repite la combinación de Richardson en escalera, a partir de los trapecios.
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

.table-scroll + p,
.table-scroll + ul {
  margin-top: var(--space-4);
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
