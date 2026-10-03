<script setup>
// Referencias bibliográficas de los métodos para sistemas no lineales. La
// obra es la misma para todos; la nota indica qué sección cubre el método de
// la página.
defineProps({
  method: { type: String, required: true },
})
</script>

<template>
  <div class="card">
    <h2>Referencias</h2>
    <ul class="references">
      <li v-if="method === 'newton'">
        Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
        <em>Numerical analysis</em> (10.ª ed.). Cengage Learning. (Capítulo 10: soluciones
        numéricas de sistemas de ecuaciones no lineales. La sección 10.2 presenta el método de
        Newton para sistemas, con la matriz jacobiana, su relación con la iteración de punto fijo
        y su convergencia cuadrática cuando la jacobiana es no singular en la solución.)
      </li>
      <li v-else>
        Burden, R. L., Faires, J. D., &amp; Burden, A. M. (2016).
        <em>Numerical analysis</em> (10.ª ed.). Cengage Learning. (Capítulo 10: soluciones
        numéricas de sistemas de ecuaciones no lineales. La sección 10.1 presenta los puntos fijos
        de funciones de varias variables, el teorema de convergencia para contracciones con la
        cota de error basada en las derivadas parciales, y cómo acelerar la iteración usando los
        valores ya actualizados, a la manera de Gauss-Seidel.)
      </li>
      <li>
        Chapra, S. C., &amp; Canale, R. P. (2015).
        <em>Métodos numéricos para ingenieros</em> (7.ª ed.). McGraw-Hill.
      </li>
    </ul>
  </div>
</template>
