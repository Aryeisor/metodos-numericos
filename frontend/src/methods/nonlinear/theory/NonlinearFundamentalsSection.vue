<script setup>
// Fundamento común de los métodos para sistemas no lineales: qué es un
// sistema no lineal, el concepto de punto fijo, la condición de convergencia
// (contracción) y las limitaciones que introduce reformular F(x) = 0.
import MathFormula from '../../../components/MathFormula.vue'
import { scalarRows, tex } from './content'
</script>

<template>
  <div class="card">
    <h2>Fundamento común: sistemas <MathFormula :expression="tex.vectorForm" /></h2>
    <p>
      Un sistema de <MathFormula expression="n" /> ecuaciones <strong>no lineales</strong> con
      <MathFormula expression="n" /> incógnitas tiene la forma
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.system" display-mode />
    </div>
    <p>
      o, en forma vectorial, <MathFormula :expression="tex.vectorForm" />, con
      <MathFormula :expression="tex.vectorMap" />. Al menos una de las funciones
      <MathFormula :expression="tex.fi" /> contiene productos de incógnitas, potencias o funciones
      como <MathFormula expression="\sin" />, <MathFormula expression="e^{x}" /> o
      <MathFormula expression="\sqrt{x}" />. Esto cambia el problema respecto al caso lineal
      <MathFormula :expression="tex.linearForm" /> en dos aspectos fundamentales:
    </p>
    <ul>
      <li>
        <strong>No hay garantía de solución única.</strong> Un sistema lineal cuadrado tiene una
        única solución o ninguna (o infinitas). Uno no lineal puede tener cualquier número de
        soluciones: por ejemplo, una circunferencia y una parábola pueden cortarse en 0, 1, 2, 3 o
        4 puntos. La solución que encuentre el método depende del punto de partida.
      </li>
      <li>
        <strong>No existe un método directo.</strong> Para un sistema lineal, la eliminación
        gaussiana da la solución exacta en un número finito de pasos. Para uno no lineal no hay
        un procedimiento equivalente: siempre se resuelve de forma <strong>iterativa</strong>,
        generando una sucesión <MathFormula :expression="tex.sequence" /> a partir de una
        aproximación inicial <MathFormula :expression="tex.x0" />.
      </li>
    </ul>
    <h3>Restricciones de aplicabilidad</h3>
    <ul>
      <li>
        El sistema debe ser cuadrado: tantas ecuaciones como incógnitas, con
        <MathFormula :expression="tex.nMin" />.
      </li>
      <li>
        Las funciones <MathFormula :expression="tex.fi" /> deben ser continuas y derivables cerca
        de la solución buscada: la teoría de convergencia se apoya en sus derivadas parciales.
      </li>
      <li>
        La aproximación inicial <MathFormula :expression="tex.x0" /> debe estar
        <strong>suficientemente cerca</strong> de la solución. A diferencia de los métodos para
        sistemas lineales, aquí la convergencia es <em>local</em> (ver más abajo).
      </li>
    </ul>

    <h3>El concepto de punto fijo</h3>
    <p>
      La idea central es reescribir el sistema <MathFormula :expression="tex.vectorForm" /> de
      forma equivalente como
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.fixedPointForm" display-mode />
    </div>
    <p>
      es decir, despejar en cada ecuación una incógnita:
      <MathFormula :expression="tex.fixedPointComponents" />. Un vector
      <MathFormula :expression="tex.p" /> que cumple <MathFormula expression="p = G(p)" /> se
      llama <strong>punto fijo</strong> de <MathFormula :expression="tex.G" />, porque
      <MathFormula :expression="tex.G" /> lo deja donde está. Como la reformulación es
      equivalente,
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.fixedPoint" display-mode />
    </div>
    <p>
      así que buscar una solución del sistema es lo mismo que buscar un punto fijo de
      <MathFormula :expression="tex.G" />. La iteración más natural para encontrarlo consiste en
      aplicar <MathFormula :expression="tex.G" /> una y otra vez:
      <MathFormula :expression="tex.iterationScheme" />. Si la sucesión converge, lo hace a un
      punto fijo.
    </p>

    <h3>La condición de convergencia: contracción</h3>
    <p>
      En los métodos lineales la convergencia la gobierna el radio espectral de la matriz de
      iteración. El equivalente no lineal es que <MathFormula :expression="tex.G" /> sea una
      <strong>contracción</strong> en una región <MathFormula :expression="tex.D" /> que contiene
      la solución: que acerque cualquier par de puntos en una proporción fija
      <MathFormula :expression="tex.K" /> menor que 1.
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.contraction" display-mode />
    </div>
    <p>
      El <strong>teorema del punto fijo</strong> asegura que, si además
      <MathFormula :expression="tex.GofD" /> (las iteraciones no salen de la región), entonces
      <MathFormula :expression="tex.G" /> tiene un único punto fijo <MathFormula :expression="tex.p" />
      en <MathFormula :expression="tex.D" />, la iteración converge a él desde cualquier
      <MathFormula :expression="tex.x0" /> de la región, y el error queda acotado por
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.errorBound" display-mode />
    </div>
    <p>
      Cuanto más pequeño es <MathFormula :expression="tex.K" />, más rápido converge. En la práctica
      la contracción se comprueba con las derivadas: la <strong>matriz jacobiana</strong> de
      <MathFormula :expression="tex.G" /> reúne cómo cambia cada
      <MathFormula :expression="tex.gi" /> respecto a cada incógnita,
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.jacobian" display-mode />
    </div>
    <p>
      y si su norma infinito (la mayor suma por filas de los valores absolutos) se mantiene por
      debajo de 1 en la región, <MathFormula :expression="tex.G" /> es una contracción:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.jacobianNorm" display-mode />
    </div>
    <p>
      Es el mismo papel que juega la dominancia diagonal en los métodos lineales: una condición
      <strong>suficiente</strong> y fácil de comprobar. La condición que realmente decide la
      convergencia cerca de la solución es <MathFormula :expression="tex.localRadius" />. De hecho,
      el caso lineal es un caso particular: si <MathFormula :expression="tex.linearCase" />, y la
      condición se reduce a <MathFormula :expression="tex.rhoT" />, la misma que para Jacobi y
      Gauss-Seidel. La diferencia es que en un sistema no lineal <MathFormula expression="J_G" />
      cambia de un punto a otro, de modo que la condición sólo vale <em>cerca</em> de
      <MathFormula :expression="tex.p" />: la convergencia es local, no global.
    </p>

    <h3>Limitaciones propias de la iteración de punto fijo</h3>
    <p>
      Dos factores que no aparecen en Jacobi ni en Gauss-Seidel determinan si el método
      converge y con qué rapidez:
    </p>
    <ul>
      <li>
        <strong>La aproximación inicial.</strong> Como la contracción sólo se cumple cerca de la
        solución, un <MathFormula :expression="tex.x0" /> alejado puede hacer que la iteración
        diverja, que tienda a otra solución distinta o que llegue a valores fuera del dominio de
        alguna función (por ejemplo, la raíz de un número negativo).
      </li>
      <li>
        <strong>Cómo se despejó cada ecuación.</strong> Un mismo sistema
        <MathFormula :expression="tex.vectorForm" /> admite muchas reformulaciones
        <MathFormula :expression="tex.fixedPointForm" />. Todas tienen los mismos puntos fijos,
        pero no la misma derivada en ellos: unas convergen, otras divergen y otras convergen mucho
        más despacio.
      </li>
    </ul>
    <p>
      Un ejemplo escalar lo muestra con claridad. La ecuación
      <MathFormula :expression="tex.scalarEquation" /> tiene la raíz
      <MathFormula :expression="tex.scalarRoot" />, y se puede despejar <MathFormula expression="x" />
      de al menos tres maneras. Partiendo de <MathFormula :expression="tex.scalarStart" />:
    </p>
    <div class="table-scroll">
      <table class="comparison-table numeric-table scalar-table">
        <thead>
          <tr>
            <th>Despeje</th>
            <th><MathFormula :expression="tex.derivative" /></th>
            <th><MathFormula expression="x^{(1)}" /></th>
            <th><MathFormula expression="x^{(2)}" /></th>
            <th><MathFormula expression="x^{(3)}" /></th>
            <th><MathFormula expression="x^{(4)}" /></th>
            <th>Resultado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in scalarRows" :key="row.g">
            <td><MathFormula :expression="row.g" /></td>
            <td><MathFormula :expression="row.derivative" /></td>
            <td v-for="(value, i) in row.iterates" :key="i">{{ value }}</td>
            <td>{{ row.verdict }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Las tres son la misma ecuación. Converge el despeje cuya derivada en la raíz es menor que 1
      en valor absoluto, y lo hace más rápido cuanto más pequeña es esa derivada.
    </p>
    <p>
      La aplicación elige el despeje automáticamente: la ecuación <MathFormula expression="i" /> se
      despeja para la incógnita <MathFormula :expression="tex.xi" /> y sólo se acepta si ese
      despeje es único y real. Eso garantiza una <MathFormula :expression="tex.G" /> válida, pero
      <strong>no</strong> que sea la que converge más rápido, ni siquiera que converja. Si el
      método no converge, reescribir las ecuaciones o cambiar su orden (lo que cambia qué
      incógnita se despeja de cada una) produce una <MathFormula :expression="tex.G" /> distinta
      que puede funcionar.
    </p>
  </div>
</template>

<style scoped>
/* Primera columna con la fórmula del despeje y la última con texto: se
   alinean a la izquierda (numeric-table alinea a la derecha desde la 3.ª). */
.scalar-table.numeric-table td:last-child,
.scalar-table.numeric-table th:last-child {
  text-align: left;
}
</style>
