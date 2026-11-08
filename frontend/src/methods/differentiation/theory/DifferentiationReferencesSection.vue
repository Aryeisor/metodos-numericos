<script setup>
// Referencias bibliográficas de la diferenciación numérica, en el mismo
// formato APA (y las mismas ediciones) que las demás categorías. La obra es la
// misma para todos los métodos; la nota indica qué cubre la sección 4.1 para
// el método de la página.
defineProps({
  method: { type: String, required: true },
})
</script>

<template>
  <div class="card">
    <h2>Referencias</h2>
    <ul class="references">
      <li v-if="method === 'cinco-puntos'">
        Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
        <em>Numerical analysis</em> (10.ª ed.). Cengage Learning. (Capítulo 4: diferenciación e
        integración numéricas. La sección 4.1 presenta las fórmulas de cinco puntos, de punto medio y
        de extremo, con su error de truncamiento O(h⁴) y el ejemplo de x·eˣ en x₀ = 2; la sección 4.2,
        la extrapolación de Richardson, que también lleva a la integración de Romberg.)
      </li>
      <li v-else-if="method === 'tres-puntos'">
        Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
        <em>Numerical analysis</em> (10.ª ed.). Cengage Learning. (Capítulo 4: diferenciación e
        integración numéricas. La sección 4.1 deriva las fórmulas de tres puntos, de punto medio y
        de extremo, del polinomio de Lagrange, con su error de truncamiento O(h²), el ejemplo de
        x·eˣ en x₀ = 2 con la tabla de datos y el efecto del redondeo.)
      </li>
      <li v-else>
        Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
        <em>Numerical analysis</em> (10.ª ed.). Cengage Learning. (Capítulo 4: diferenciación e
        integración numéricas. La sección 4.1 presenta la fórmula
        <em>[f(x₀ + h) − f(x₀)]/h</em>, progresiva si h &gt; 0 y regresiva si h &lt; 0, con su error
        de truncamiento, el ejemplo de ln x en x₀ = 1.8 y el efecto del redondeo.)
      </li>
      <li>
        Chapra, S. C., &amp; Canale, R. P. (2015).
        <em>Métodos numéricos para ingenieros</em> (7.ª ed.). McGraw-Hill.
      </li>
      <li>
        Mathews, J. H., &amp; Fink, K. D. (2000). <em>Métodos numéricos con MATLAB</em> (3.ª ed.).
        Prentice Hall.
      </li>
    </ul>
  </div>
</template>
