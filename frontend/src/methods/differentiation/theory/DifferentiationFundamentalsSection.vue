<script setup>
// Fundamento común de la diferenciación numérica: el problema, sus
// aplicaciones, la derivada como límite, la serie de Taylor con residuo, las
// dos fuentes de error y el orden O(hⁿ). Lo comparten las diferencias
// progresiva y regresiva y las fórmulas de 3 y 5 puntos.
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { ERROR_SOURCES, tex } from './content'
</script>

<template>
  <div class="card">
    <h2>Fundamento común: diferenciación numérica</h2>

    <h3 class="first-heading">El problema</h3>
    <p>
      Se quiere calcular <MathFormula expression="f'(x_0)" /> cuando derivar a mano no es posible o
      no conviene. Hay dos casos:
    </p>
    <ol>
      <li>Sólo se tienen <strong>datos</strong> medidos: una tabla de valores, sin fórmula.</li>
      <li>La función tiene una fórmula, pero es <strong>muy complicada</strong> de derivar.</li>
    </ol>

    <h3>Aplicaciones</h3>
    <ul>
      <li>Velocidad y aceleración a partir de posiciones medidas.</li>
      <li>Tasas de cambio en ingeniería: flujo de calor, corriente eléctrica, caudal.</li>
      <li>
        La base de los métodos para ecuaciones diferenciales: el método de Euler usa la diferencia
        progresiva.
      </li>
    </ul>

    <h3>Idea central</h3>
    <p>La derivada se define como un límite:</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.limit" display-mode />
    </div>
    <p>
      Los métodos numéricos <strong>no toman el límite</strong>: usan un
      <MathFormula expression="h" /> pequeño y finito, y aceptan un error a cambio.
    </p>

    <h3>Herramienta: la serie de Taylor</h3>
    <p>
      Todas las fórmulas de la categoría, y sus errores, salen del desarrollo de
      <MathFormula expression="f(x_0 + h)" /> con el residuo de Lagrange:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.taylor" display-mode />
    </div>
    <p class="formula-legend">
      con <MathFormula :expression="tex.taylorXi" />. El residuo es exacto: dice cuánto se pierde al
      cortar la serie en el término <MathFormula expression="n" />.
    </p>

    <h3>Dos fuentes de error</h3>
    <AlgorithmSteps :steps="ERROR_SOURCES" />

    <h3>Orden del error <MathFormula expression="O(h^n)" /></h3>
    <p>
      Decir que el error es <MathFormula expression="O(h^n)" /> significa que, para
      <MathFormula expression="h" /> pequeño, se comporta como una constante por
      <MathFormula expression="h^n" />. En la práctica, dice cuánto mejora la aproximación al
      dividir <MathFormula expression="h" /> entre 2:
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Orden</th>
            <th>Al dividir <MathFormula expression="h" /> entre 2, el error…</th>
            <th>Fórmulas</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row"><MathFormula expression="O(h)" /></th>
            <td>se divide entre 2</td>
            <td>Progresiva y regresiva</td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="O(h^2)" /></th>
            <td>se divide entre 4</td>
            <td>Fórmula de 3 puntos (próxima sección)</td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="O(h^4)" /></th>
            <td>se divide entre 16</td>
            <td>Fórmula de 5 puntos (próxima sección)</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
