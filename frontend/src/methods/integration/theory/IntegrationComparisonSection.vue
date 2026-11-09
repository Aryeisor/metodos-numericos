<script setup>
// Tabla comparativa de la categoría, compartida por las teorías del trapecio,
// Simpson, Romberg y la cuadratura gaussiana. Los valores de Chapra son los de
// las respuestas del solver que muestra cada página; las evaluaciones del
// trapecio y de Simpson 1/3 se dan contando cualquier n y duplicando n (como
// la comparación de costo de Romberg y de Gauss).
import MathFormula from '../../../components/MathFormula.vue'
</script>

<template>
  <div class="card">
    <h2>Integración numérica: comparación de la categoría</h2>
    <p>El trapecio, las dos reglas de Simpson, Romberg y la cuadratura gaussiana.</p>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Aspecto</th>
            <th>Trapecio</th>
            <th>Simpson 1/3</th>
            <th>Simpson 3/8</th>
            <th>Romberg</th>
            <th>Gauss</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Aproxima f con</th>
            <td>Rectas</td>
            <td>Parábolas (3 puntos)</td>
            <td>Cúbicas (4 puntos)</td>
            <td>Trapecios + Richardson en escalera</td>
            <td>Nodos y pesos óptimos</td>
          </tr>
          <tr>
            <th scope="row">Dónde evalúa</th>
            <td>Puntos equiespaciados, con los extremos</td>
            <td>Ídem</td>
            <td>Ídem</td>
            <td>Ídem (<MathFormula expression="n = 2^k" />)</td>
            <td>Raíces de Legendre, sin los extremos</td>
          </tr>
          <tr>
            <th scope="row">Pesos</th>
            <td><MathFormula expression="1, 2, \dots, 2, 1 \cdot \tfrac{h}{2}" /></td>
            <td><MathFormula expression="1, 4, 2, \dots, 4, 1 \cdot \tfrac{h}{3}" /></td>
            <td><MathFormula expression="1, 3, 3, 2, \dots, 3, 3, 1 \cdot \tfrac{3h}{8}" /></td>
            <td>Positivos en todas las columnas</td>
            <td>
              <MathFormula expression="w_i = \tfrac{2}{(1 - t_i^2)[P_m'(t_i)]^2}" />, todos positivos
            </td>
          </tr>
          <tr>
            <th scope="row">Error compuesto</th>
            <td><MathFormula expression="-\frac{(b - a)h^2}{12} f''" /></td>
            <td><MathFormula expression="-\frac{(b - a)h^4}{180} f^{(4)}" /></td>
            <td><MathFormula expression="-\frac{(b - a)h^4}{80} f^{(4)}" /></td>
            <td>Se estima con <MathFormula expression="|R_{i,i} - R_{i-1,i-1}|" /></td>
            <td>
              <MathFormula expression="\frac{(b - a)^{2m+1}(m!)^4}{(2m + 1)[(2m)!]^3} f^{(2m)}" /> (simple)
            </td>
          </tr>
          <tr>
            <th scope="row">Orden / convergencia</th>
            <td><MathFormula expression="O(h^2)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
            <td><MathFormula expression="O(h^4)" /></td>
            <td><MathFormula expression="O(h^{2k})" /> en la columna <MathFormula expression="k" /></td>
            <td>Muy rápida con <MathFormula expression="f" /> suave (exponencial al agregar puntos)</td>
          </tr>
          <tr>
            <th scope="row">Exacta para grado</th>
            <td><MathFormula expression="\le 1" /></td>
            <td><MathFormula expression="\le 3" /></td>
            <td><MathFormula expression="\le 3" /></td>
            <td><MathFormula expression="\le 2k - 1" /> en la columna <MathFormula expression="k" /></td>
            <td><MathFormula expression="\le 2m - 1" /></td>
          </tr>
          <tr>
            <th scope="row">Espaciado desigual</th>
            <td>Sí</td>
            <td>No</td>
            <td>No</td>
            <td>No</td>
            <td>No aplica (elige sus puntos)</td>
          </tr>
          <tr>
            <th scope="row">Datos tabulados</th>
            <td>Cualquier cantidad</td>
            <td><MathFormula expression="n" /> par</td>
            <td><MathFormula expression="n" /> múltiplo de 3</td>
            <td><MathFormula expression="2^m + 1" /> puntos</td>
            <td>No (nodos irracionales)</td>
          </tr>
          <tr>
            <th scope="row"><MathFormula expression="f" /> no definida en un extremo</th>
            <td>No sirve</td>
            <td>No sirve</td>
            <td>No sirve</td>
            <td>No sirve</td>
            <td>Sí sirve (no evalúa los extremos)</td>
          </tr>
          <tr>
            <th scope="row">Reutiliza evaluaciones al refinar</th>
            <td>Sí (recurrencia)</td>
            <td>Sí</td>
            <td>Sí</td>
            <td>Sí</td>
            <td>No (los nodos cambian con <MathFormula expression="m" />)</td>
          </tr>
          <tr>
            <th scope="row">Chapra, menor n</th>
            <td>0.1728 (<MathFormula expression="n = 1" />)</td>
            <td>1.367467 (<MathFormula expression="n = 2" />)</td>
            <td>1.51917 (<MathFormula expression="n = 3" />)</td>
            <td>1.640533 (exacta, fila 3)</td>
            <td>1.9648 (<MathFormula expression="m = 1" />); 1.640533 (exacta, <MathFormula expression="m = 3" />)</td>
          </tr>
          <tr>
            <th scope="row">Chapra con 3 evaluaciones</th>
            <td>1.0688</td>
            <td>1.367467</td>
            <td>—</td>
            <td>1.367467 (<MathFormula expression="R_{2,2}" />)</td>
            <td>1.640533 (exacta)</td>
          </tr>
          <tr>
            <th scope="row">Evaluaciones para <MathFormula expression="|E_t| \le 0.000001" /> en Chapra</th>
            <td>1601 (cualquier n) / 2049 (duplicando n)</td>
            <td>47 (cualquier n) / 65 (duplicando n)</td>
            <td>58 (cualquier n múltiplo de 3)</td>
            <td>5</td>
            <td>3</td>
          </tr>
          <tr>
            <th scope="row">Funciona mal si</th>
            <td>—</td>
            <td>—</td>
            <td>—</td>
            <td>f no es suave (por ejemplo <MathFormula expression="\sqrt{x}" /> en 0)</td>
            <td>f no es suave (por ejemplo <MathFormula expression="1/\sqrt{x}" /> en 0): converge lento</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">
      «Cualquier n» es el menor n que lo logra; «duplicando n» es lo que hace la comparación de costo de Romberg y
      de Gauss (n = 1, 2, 4, … para el trapecio y 2, 4, 8, … para Simpson). Simpson 3/8 necesita al menos 4
      evaluaciones.
    </p>
  </div>
</template>
