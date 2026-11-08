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
      </li>
      <li>
        Mathews, J. H., &amp; Fink, K. D. (2000). <em>Métodos numéricos con MATLAB</em> (3.ª ed.).
        Prentice Hall.
      </li>
    </ul>
  </div>
</template>
