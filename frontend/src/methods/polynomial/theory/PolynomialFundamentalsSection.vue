<script setup>
// Fundamento común de los métodos para raíces de polinomios: el teorema
// fundamental del álgebra, los pares complejos conjugados como factores
// cuadráticos reales, la idea de buscar factores en lugar de raíces y la
// deflación.
import MathFormula from '../../../components/MathFormula.vue'
import { tex } from './content'
</script>

<template>
  <div class="card">
    <h2>Fundamento común: raíces de polinomios</h2>
    <p>Un polinomio de grado <MathFormula expression="n" /> con coeficientes reales tiene la forma</p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.polynomial" display-mode />
    </div>
    <p>
      y sus <strong>raíces</strong> son los valores de <MathFormula expression="x" /> que cumplen
      <MathFormula expression="f(x) = 0" />. A diferencia de una ecuación no lineal cualquiera, de
      un polinomio se sabe de antemano cuántas raíces tiene y qué forma pueden tomar.
    </p>

    <h3>Teorema fundamental del álgebra</h3>
    <p>
      Un polinomio de grado <MathFormula expression="n" /> tiene <strong>exactamente
      <MathFormula expression="n" /> raíces</strong>, contando su multiplicidad, que pueden ser
      reales o complejas. Equivalentemente, se descompone en <MathFormula expression="n" />
      factores lineales:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.fundamentalTheorem" display-mode />
    </div>

    <h3>Coeficientes reales: pares conjugados y factores cuadráticos</h3>
    <p>
      Si los coeficientes son reales, las raíces complejas aparecen siempre en <strong>pares
      conjugados</strong> <MathFormula expression="a \pm bi" />. Al multiplicar los dos factores
      lineales de un par, la parte imaginaria se cancela y queda un <strong>factor cuadrático con
      coeficientes reales</strong>:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.conjugatePair" display-mode />
    </div>
    <p>
      En consecuencia, todo polinomio real se factoriza en factores lineales y cuadráticos,
      <strong>todos reales</strong>:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.realFactorization" display-mode />
    </div>

    <h3>La idea de Bairstow: buscar factores, no raíces</h3>
    <p>
      Un método que busque las raíces una a una, como Newton-Raphson en una variable, necesita
      aritmética compleja para llegar a las raíces complejas. Bairstow evita ese problema:
      busca directamente un <strong>factor cuadrático</strong> con <MathFormula expression="r" /> y
      <MathFormula expression="s" /> reales,
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.factor" display-mode />
    </div>
    <p>
      con la misma notación de la vista Resolver. Todo el cálculo se hace con números reales, y
      las dos raíces del factor, reales o complejas, salen al final de la fórmula cuadrática:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.factorRoots" display-mode />
    </div>

    <h3>Deflación</h3>
    <p>
      Una vez encontrado un factor, se divide el polinomio entre él. Queda un
      <strong>cociente</strong> de dos grados menos, que tiene las raíces restantes:
    </p>
    <div class="formula-box theory-formula">
      <MathFormula :expression="tex.deflation" display-mode />
    </div>
    <p>
      Sobre el cociente se repite el proceso hasta que queda un polinomio de grado 2 o 1, que se
      resuelve directamente. Así, un polinomio de grado <MathFormula expression="n" /> se resuelve
      con unos <MathFormula expression="n/2" /> factores cuadráticos.
    </p>
  </div>
</template>
