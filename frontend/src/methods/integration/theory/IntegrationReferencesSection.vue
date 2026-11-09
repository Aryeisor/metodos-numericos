<script setup>
// Referencias bibliográficas de la integración numérica, en el mismo formato
// APA y las mismas ediciones que las demás categorías. La nota de cada obra
// indica qué cubre para el método de la página.
defineProps({
  method: { type: String, required: true },
})
</script>

<template>
  <div class="card">
    <h2>Referencias</h2>
    <ul class="references">
      <li>
        Chapra, S. C., &amp; Canale, R. P. (2015).
        <em>Métodos numéricos para ingenieros</em> (7.ª ed.). McGraw-Hill.
        <template v-if="method === 'trapecio'">
          (Capítulo 21: fórmulas de integración de Newton-Cotes. Presenta la regla del trapecio simple y
          compuesta, su error y el error aproximado con el promedio de f′′, la integración con segmentos
          desiguales y el ejemplo del polinomio en [0, 0.8].)
        </template>
        <template v-else-if="method === 'simpson'">
          (Capítulo 21: reglas de Simpson. Presenta las reglas 1/3 y 3/8, simples y compuestas, su error y
          el error aproximado con el promedio de f⁽⁴⁾, la combinación para un número impar de segmentos y el
          ejemplo del polinomio en [0, 0.8].)
        </template>
        <template v-else-if="method === 'romberg'">
          (Capítulo 22: integración de Romberg. Presenta la extrapolación de Richardson aplicada al trapecio, la
          tabla triangular con la notación R<sub>i,k</sub>, el criterio de parada con εₐ y el ejemplo del
          polinomio en [0, 0.8].)
        </template>
        <template v-else-if="method === 'gauss'">
          (Capítulo 22: cuadratura de Gauss. Deduce la fórmula de 2 puntos por coeficientes indeterminados, presenta
          el cambio de variable a [a, b], la tabla de nodos y pesos de Gauss-Legendre, el error con f⁽²ᵐ⁾ y el
          ejemplo del polinomio en [0, 0.8].)
        </template>
      </li>
      <li>
        Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
        <em>Numerical analysis</em> (10.ª ed.). Cengage Learning.
        <template v-if="method === 'trapecio'">
          (Capítulo 4: diferenciación e integración numéricas. La sección 4.3 presenta la regla del
          trapecio y su error a partir del polinomio de interpolación; la sección 4.4, la integración
          compuesta y su cota de error.)
        </template>
        <template v-else-if="method === 'simpson'">
          (Capítulo 4: la sección 4.3 deduce la regla de Simpson del polinomio de interpolación, su error con
          f⁽⁴⁾ y su exactitud para cúbicas; la sección 4.4, la regla compuesta y su cota de error.)
        </template>
        <template v-else-if="method === 'romberg'">
          (Sección 4.5: integración de Romberg, con la misma fórmula escrita como R<sub>k,j</sub>; la sección
          4.2 presenta la extrapolación de Richardson.)
        </template>
        <template v-else-if="method === 'gauss'">
          (Sección 4.7: cuadratura gaussiana, con los polinomios de Legendre, sus raíces como nodos, los pesos y el
          cambio de variable a [a, b].)
        </template>
      </li>
      <li>
        Mathews, J. H., &amp; Fink, K. D. (2000). <em>Métodos numéricos con MATLAB</em> (3.ª ed.).
        Prentice Hall.
      </li>
      <li v-if="method === 'romberg'">
        Romberg, W. (1955). Vereinfachte numerische Integration.
        <em>Det Kongelige Norske Videnskabers Selskabs Forhandlinger, 28</em>(7), 30–36.
      </li>
    </ul>
  </div>
</template>
