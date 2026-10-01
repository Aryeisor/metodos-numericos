<script setup>
// Comparación práctica entre Jacobi y Gauss-Seidel.
import MathFormula from '../../../components/MathFormula.vue'
import { tex } from './content'
</script>

<template>
  <div class="card">
    <h2>Jacobi frente a Gauss-Seidel</h2>
    <p>
      Ambos métodos resuelven el mismo problema y comparten las mismas condiciones de
      convergencia, pero se comportan de forma distinta en tres aspectos prácticos:
    </p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Criterio</th>
            <th>Jacobi</th>
            <th>Gauss-Seidel</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Velocidad de convergencia</th>
            <td>
              Más lenta. Cada iteración usa sólo información de la anterior, así que la mejora por
              paso es menor.
            </td>
            <td>
              Generalmente converge en menos iteraciones para el mismo sistema, porque aprovecha
              los valores actualizados de inmediato. En el ejemplo de arriba,
              <MathFormula :expression="tex.rho" /> pasa de 0.3 a 0.089443.
            </td>
          </tr>
          <tr>
            <th scope="row">Uso de memoria</th>
            <td>
              Necesita dos vectores: <MathFormula :expression="tex.xCurrent" /> completo se
              conserva mientras se construye <MathFormula :expression="tex.xNext" />.
            </td>
            <td>
              Actualiza el vector <em>in situ</em>: no hace falta conservar la iteración anterior
              completa, sólo el valor previo de la componente que se está sustituyendo.
            </td>
          </tr>
          <tr>
            <th scope="row">Paralelización</th>
            <td>
              Trivialmente paralelizable: dentro de una iteración, cada componente de
              <MathFormula :expression="tex.xNext" /> es independiente de las demás y puede
              calcularse a la vez.
            </td>
            <td>
              No es directamente paralelizable: cada componente depende de las que acaban de
              actualizarse en esa misma iteración, lo que impone un orden secuencial.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      En resumen: Gauss-Seidel suele ser preferible en un cálculo secuencial, mientras que Jacobi
      resulta atractivo cuando se dispone de varios procesadores.
    </p>
  </div>
</template>
