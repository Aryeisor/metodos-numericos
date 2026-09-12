<template>
  <div>
    <div class="card">
      <h2>Fundamento común: sistemas A·x = b</h2>
      <p>
        Ambos métodos resuelven sistemas de <code>n</code> ecuaciones lineales con
        <code>n</code> incógnitas, expresados en forma matricial <code>A·x = b</code>, donde
        <code>A</code> es la matriz de coeficientes (n×n), <code>x</code> el vector de incógnitas
        y <code>b</code> el vector de términos independientes. En lugar de resolver el sistema de
        forma directa (por ejemplo, con eliminación gaussiana), los métodos <strong>iterativos</strong>
        parten de una aproximación inicial <code>x⁽⁰⁾</code> y generan una sucesión de
        aproximaciones <code>x⁽¹⁾, x⁽²⁾, ...</code> que, bajo ciertas condiciones, converge a la
        solución exacta.
      </p>
      <h3>Restricciones de aplicabilidad</h3>
      <ul>
        <li>La matriz <code>A</code> debe ser cuadrada (n × n), con n ≥ 3.</li>
        <li>
          Ningún elemento de la diagonal principal (<code>a_ii</code>) puede ser cero, ya que se
          necesita para despejar cada variable <code>x_i</code>.
        </li>
        <li>
          <strong>Dominancia diagonal</strong> (condición suficiente, no necesaria, de convergencia):
          se dice que <code>A</code> es diagonalmente dominante por filas si, para cada fila i,
          <code>|a_ii| &gt; Σ_{j≠i} |a_ij|</code>. Si se cumple para todas las filas, ambos métodos
          convergen para cualquier vector inicial. Si no se cumple, el método puede converger o no;
          la aplicación lo advierte pero permite continuar.
        </li>
      </ul>
    </div>

    <div class="card">
      <h2>Método de Jacobi</h2>
      <p><strong>Definición formal:</strong></p>
      <p>
        Se descompone <code>A = D + R</code>, donde <code>D</code> es la diagonal de <code>A</code>
        y <code>R</code> contiene el resto de los elementos. La fórmula de iteración, componente a
        componente, es:
      </p>
      <pre class="formula">x_i^(k+1) = ( b_i − Σ_{j≠i} a_ij · x_j^(k) ) / a_ii ,   i = 1, ..., n</pre>
      <p>
        La característica distintiva de Jacobi es que <strong>todas</strong> las componentes de la
        nueva iteración <code>x^(k+1)</code> se calculan usando únicamente los valores de la
        iteración anterior completa <code>x^(k)</code>; ningún valor recién calculado se reutiliza
        dentro de la misma iteración.
      </p>
      <p><strong>Algoritmo de aplicación:</strong></p>
      <ol>
        <li>Elegir un vector inicial <code>x⁽⁰⁾</code> (por defecto, ceros) y una tolerancia ε.</li>
        <li>
          Para cada iteración k = 1, 2, ..., calcular <code>x_i^(k+1)</code> para todo i usando la
          fórmula anterior, a partir de <code>x^(k)</code>.
        </li>
        <li>
          Calcular el error como la norma infinito entre iteraciones sucesivas:
          <code>max_i |x_i^(k+1) − x_i^(k)|</code>.
        </li>
        <li>
          Detener el proceso cuando el error sea menor que ε <em>y</em> se hayan ejecutado al menos
          6 iteraciones, o al alcanzar el número máximo de iteraciones configurado.
        </li>
      </ol>
    </div>

    <div class="card">
      <h2>Método de Gauss-Seidel</h2>
      <p><strong>Definición formal:</strong></p>
      <p>
        Es una variante de Jacobi que acelera la convergencia reutilizando, dentro de la misma
        iteración, los valores de <code>x</code> que ya fueron actualizados:
      </p>
      <pre class="formula">x_i^(k+1) = ( b_i − Σ_{j&lt;i} a_ij · x_j^(k+1) − Σ_{j&gt;i} a_ij · x_j^(k) ) / a_ii</pre>
      <p>
        Es decir, para calcular <code>x_i</code> se usan los valores <code>x_1, ..., x_{i-1}</code>
        ya recalculados en la iteración actual, y los valores <code>x_{i+1}, ..., x_n</code> aún de
        la iteración anterior. Esto normalmente reduce el número de iteraciones necesarias respecto
        a Jacobi.
      </p>
      <p><strong>Algoritmo de aplicación:</strong></p>
      <ol>
        <li>Elegir un vector inicial <code>x⁽⁰⁾</code> (por defecto, ceros) y una tolerancia ε.</li>
        <li>
          Para cada iteración k, recorrer i = 1, ..., n actualizando <code>x_i</code>
          <em>in situ</em>, usando los valores ya actualizados de la propia iteración para j &lt; i.
        </li>
        <li>Calcular el error como la norma infinito entre <code>x^(k+1)</code> y <code>x^(k)</code>.</li>
        <li>
          Detener el proceso cuando el error sea menor que ε <em>y</em> se hayan ejecutado al menos
          6 iteraciones, o al alcanzar el número máximo de iteraciones configurado.
        </li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
h3 {
  margin-top: 18px;
}

.formula {
  background: #f1f5f9;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 14px;
  overflow-x: auto;
  font-size: 0.9rem;
}

code {
  background: #f1f5f9;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.9em;
}

ul,
ol {
  padding-left: 22px;
}

li {
  margin-bottom: 6px;
}
</style>
