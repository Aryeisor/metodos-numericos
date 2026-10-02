<script setup>
// Teoría propia del método de Jacobi.
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import WorkedIterations from '../../../components/theory/WorkedIterations.vue'
import { ALGORITHM_STEPS, PREVIOUS_COLOR, jacobiSteps, tex, vectorLatex } from './content'
</script>

<template>
  <div id="metodo-jacobi" class="card">
    <h2>Método de Jacobi</h2>
    <h3 class="first-heading">Definición formal</h3>
    <p>
      Se descompone <MathFormula :expression="tex.decomposition" />, donde
      <MathFormula expression="D" /> es la diagonal de <MathFormula expression="A" /> y
      <MathFormula expression="R" /> contiene el resto de los elementos. La fórmula de iteración,
      componente a componente, es:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.jacobi" display-mode />
    </div>
    <p class="formula-legend">
      <span :style="{ color: PREVIOUS_COLOR }">■</span> valores de la iteración anterior
    </p>
    <p>
      La característica distintiva de Jacobi es que <strong>todas</strong> las componentes de la
      nueva iteración <MathFormula :expression="tex.xNext" /> se calculan usando únicamente los
      valores de la iteración anterior completa <MathFormula :expression="tex.xCurrent" />; ningún
      valor recién calculado se reutiliza dentro de la misma iteración.
    </p>
    <h3>Algoritmo de aplicación</h3>
    <AlgorithmSteps :steps="ALGORITHM_STEPS.jacobi" />

    <h3 id="ejemplo-jacobi">Ejemplo resuelto: tres iteraciones de Jacobi</h3>
    <p>
      Tomemos este sistema, cuya solución exacta es
      <MathFormula :expression="tex.exampleSolution" />, partiendo de
      <MathFormula :expression="tex.exampleStart" />:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.exampleSystem" display-mode />
    </div>
    <p>
      En cada paso, <strong>las tres</strong> componentes se calculan con los valores de la
      iteración anterior (en <span class="legend-prev">azul</span>):
    </p>

    <WorkedIterations :steps="jacobiSteps" />

    <p>
      Tras tres iteraciones vamos por
      <MathFormula :expression="vectorLatex('x^{(3)}', jacobiSteps[2].x)" />, todavía a cierta
      distancia de <MathFormula :expression="tex.exampleSolution" />.
    </p>
  </div>
</template>
