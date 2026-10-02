<script setup>
// Teoría propia del método de Gauss-Seidel.
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import WorkedIterations from '../../../components/theory/WorkedIterations.vue'
import { theoryRouteName } from '../../routeNames'
import {
  ALGORITHM_STEPS,
  CURRENT_COLOR,
  PREVIOUS_COLOR,
  comparisonRows,
  formatNumber,
  gaussSeidelSteps,
  jacobiSteps,
  tex,
  vectorLatex,
} from './content'
</script>

<template>
  <div id="metodo-gauss-seidel" class="card">
    <h2>Método de Gauss-Seidel</h2>
    <h3 class="first-heading">Definición formal</h3>
    <p>
      Es una variante de Jacobi que acelera la convergencia reutilizando, dentro de la misma
      iteración, los valores de <MathFormula expression="x" /> que ya fueron actualizados:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.gaussSeidel" display-mode />
    </div>
    <p class="formula-legend">
      <span :style="{ color: PREVIOUS_COLOR }">■</span> valores de la iteración anterior ·
      <span :style="{ color: CURRENT_COLOR }">■</span> valores ya recalculados en esta misma
      iteración
    </p>
    <p>
      Es decir, para calcular <MathFormula :expression="tex.xi" /> se usan los valores
      <MathFormula :expression="tex.before" /> ya recalculados en la iteración actual, y los valores
      <MathFormula :expression="tex.after" /> aún de la iteración anterior. Esto normalmente reduce
      el número de iteraciones necesarias respecto a Jacobi.
    </p>
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS['gauss-seidel']" />

    <h3>Ejemplo resuelto: el mismo sistema con Gauss-Seidel</h3>
    <p>
      Resolvamos
      <RouterLink :to="{ name: theoryRouteName('jacobi'), hash: '#ejemplo-jacobi' }"
        >el mismo sistema</RouterLink
      >
      y desde el mismo punto de partida, para poder comparar. La
      diferencia aparece a partir de la segunda ecuación: en cuanto una componente se recalcula,
      las siguientes ya usan ese valor <span class="legend-current">recién calculado</span> en
      lugar del de la iteración anterior.
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleSystem" display-mode />
    </div>

    <WorkedIterations :steps="gaussSeidelSteps" />

    <p>
      Con el mismo número de iteraciones, Gauss-Seidel llega a
      <MathFormula :expression="vectorLatex('x^{(3)}', gaussSeidelSteps[2].x)" />, muy cerca ya de
      <MathFormula :expression="tex.exampleSolution" />, mientras que Jacobi seguía en
      <MathFormula :expression="vectorLatex('', jacobiSteps[2].x)" />. Reutilizar los valores
      nuevos dentro de la misma iteración acelera la convergencia.
    </p>

    <h4 class="table-caption">Comparación iteración a iteración</h4>
    <div class="table-scroll">
      <table class="comparison-table numeric-table">
        <thead>
          <tr>
            <th>Iteración</th>
            <th>Método</th>
            <th><MathFormula expression="x_1" /></th>
            <th><MathFormula expression="x_2" /></th>
            <th><MathFormula expression="x_3" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in comparisonRows" :key="row.key" :class="{ 'group-start': row.first }">
            <td>{{ row.first ? row.iteration : '' }}</td>
            <td>{{ row.method }}</td>
            <td v-for="(value, i) in row.x" :key="i">{{ formatNumber(value) }}</td>
          </tr>
          <tr class="exact-row group-start">
            <td></td>
            <td>Solución exacta</td>
            <td>1</td>
            <td>2</td>
            <td>3</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      Puedes cargar este mismo sistema en la vista <strong>Resolver</strong> para verlo converger
      hasta el final.
    </p>
  </div>
</template>
