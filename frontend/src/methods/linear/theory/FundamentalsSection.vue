<script setup>
// Fundamento común de Jacobi y Gauss-Seidel: restricciones, dominancia diagonal y radio espectral.
import MathFormula from '../../../components/MathFormula.vue'
import { tex } from './content'
</script>

<template>
  <div class="card">
    <h2>Fundamento común: sistemas <MathFormula :expression="tex.system" /></h2>
    <p>
      Ambos métodos resuelven sistemas de <MathFormula expression="n" /> ecuaciones lineales con
      <MathFormula expression="n" /> incógnitas, expresados en forma matricial
      <MathFormula :expression="tex.system" />, donde <MathFormula expression="A" /> es la matriz
      de coeficientes (<MathFormula :expression="tex.nByN" />), <MathFormula expression="x" /> el
      vector de incógnitas y <MathFormula expression="b" /> el vector de términos independientes.
      En lugar de resolver el sistema de forma directa (por ejemplo, con eliminación gaussiana),
      los métodos <strong>iterativos</strong> parten de una aproximación inicial
      <MathFormula :expression="tex.x0" /> y generan una sucesión de aproximaciones
      <MathFormula :expression="tex.sequence" /> que, bajo ciertas condiciones, converge a la
      solución exacta.
    </p>
    <h3>Restricciones de aplicabilidad</h3>
    <ul>
      <li>
        La matriz <MathFormula expression="A" /> debe ser cuadrada
        (<MathFormula :expression="tex.nByN" />), con <MathFormula :expression="tex.nMin" />.
      </li>
      <li>
        Ningún elemento de la diagonal principal (<MathFormula :expression="tex.aii" />) puede ser
        cero, ya que se necesita para despejar cada variable <MathFormula :expression="tex.xi" />.
      </li>
      <li>
        <strong>Dominancia diagonal</strong> (condición suficiente, no necesaria, de convergencia):
        se dice que <MathFormula expression="A" /> es diagonalmente dominante por filas si, para
        cada fila <MathFormula expression="i" />,
        <div class="formula-box theory-formula">
          <MathFormula :expression="tex.dominance" display-mode />
        </div>
        Si se cumple para todas las filas, ambos métodos convergen para cualquier vector inicial.
        Si no se cumple, el método puede converger o no; la aplicación lo advierte pero permite
        continuar.
      </li>
    </ul>

    <h3>La condición real de convergencia: el radio espectral</h3>
    <p>
      La dominancia diagonal es cómoda de verificar, pero no es la condición que realmente
      gobierna la convergencia. Ambos métodos pueden escribirse como una única recurrencia
      matricial:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.recurrence" display-mode />
    </div>
    <p>
      donde <MathFormula expression="T" /> es la <strong>matriz de iteración</strong>, que resulta
      de despejar la recurrencia a partir de la descomposición
      <MathFormula :expression="tex.splitting" /> (con <MathFormula expression="D" /> la diagonal,
      <MathFormula expression="L" /> la parte triangular inferior y
      <MathFormula expression="U" /> la superior; en la notación de más abajo,
      <MathFormula expression="R = L + U" />). Cada método tiene la suya:
    </p>
    <div class="formula-pair">
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.jacobiMatrix" display-mode />
      </div>
      <div class="formula-box theory-formula">
        <MathFormula :expression="tex.gaussSeidelMatrix" display-mode />
      </div>
    </div>
    <p>
      La condición <strong>necesaria y suficiente</strong> de convergencia es que el
      <strong>radio espectral</strong> de esa matriz —el mayor de los módulos de sus valores
      propios <MathFormula expression="\lambda_i" />— sea menor que 1:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.spectralRadius" display-mode />
    </div>
    <p>
      Si se cumple, el método converge para <em>cualquier</em> vector inicial, y cuanto más
      pequeño sea <MathFormula :expression="tex.rho" />, más rápido lo hace. En el sistema
      <MathFormula :expression="tex.exampleSize" /> que se resuelve más abajo, los radios
      espectrales son <MathFormula :expression="tex.rhoJacobi" /> y
      <MathFormula :expression="tex.rhoGaussSeidel" />: ambos bastante menores que 1, y el de
      Gauss-Seidel es más de tres veces más pequeño, lo que explica que converja más rápido.
    </p>
    <p>
      Calcular <MathFormula :expression="tex.rho" /> exige resolver un problema de valores
      propios, más costoso que el propio sistema. Por eso en la práctica se usa la dominancia
      diagonal como <strong>atajo</strong>: se comprueba con una simple suma por filas y
      <em>garantiza</em> <MathFormula :expression="tex.rho" /> &lt; 1. Pero es sólo una condición
      suficiente, y de ahí las dos situaciones que se ven en la aplicación:
    </p>
    <ul>
      <li>
        Una matriz diagonalmente dominante <strong>siempre</strong> converge: el atajo nunca falla
        cuando se cumple.
      </li>
      <li>
        Una matriz que no lo es <strong>puede converger igualmente</strong>, porque lo que
        importa es <MathFormula :expression="tex.rho" />. Es el caso de los sistemas que la
        aplicación arregla reordenando filas: el sistema original ya tenía solución, sólo estaba
        escrito en un orden que ocultaba la dominancia.
      </li>
    </ul>
  </div>
</template>
