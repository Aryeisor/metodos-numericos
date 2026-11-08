<script setup>
// Fundamento común de la integración numérica: el problema, por qué no usar
// siempre la antiderivada, aplicaciones, la idea central (Newton-Cotes y
// Gauss), la forma general de una cuadratura, reglas simples y compuestas, el
// orden del error y el contraste con la diferenciación. Lo comparten el
// trapecio, Simpson, Romberg y la cuadratura gaussiana.
import GlossaryBlock from '../../../components/GlossaryBlock.vue'
import MathFormula from '../../../components/MathFormula.vue'
import AlgorithmSteps from '../../../components/theory/AlgorithmSteps.vue'
import { GLOSSARIES, tex } from './trapezoidContent'

// Dibujo del área con signo: una curva que cruza el eje entre a y b.
const W = 320
const H = 150
const AXIS = 96
const curveY = (t) => AXIS - 58 * Math.sin(Math.PI * 1.35 * t) - 10 * t
const SAMPLES = 80
const pts = Array.from({ length: SAMPLES + 1 }, (_, i) => {
  const t = i / SAMPLES
  return [20 + t * (W - 40), curveY(t)]
})
const curve = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')
// Parte de arriba y parte de abajo del eje, cada una cerrada con el eje.
const clamp = (fn) => pts.map(([x, y]) => `${x.toFixed(1)},${fn(y, AXIS).toFixed(1)}`)
const ends = [`${(W - 20).toFixed(1)},${AXIS}`, `20.0,${AXIS}`]
const above = [...clamp(Math.min), ...ends].join(' ')
const below = [...clamp(Math.max), ...ends].join(' ')

const CONTRAST = [
  {
    title: 'Diferenciación: amplifica el error',
    body: [
      'Divide entre ',
      { m: 'h' },
      ': un error ',
      { m: '\\delta' },
      ' en los datos se convierte en un error del orden de ',
      { m: '\\delta / h' },
      ', que crece al reducir ',
      { m: 'h' },
      '.',
    ],
  },
  {
    title: 'Integración: suaviza el error',
    body: [
      'Multiplica por ',
      { m: 'h' },
      ' y promedia. Con datos que tienen un error de hasta ',
      { m: '\\delta' },
      ', el trapecio se equivoca como mucho en ',
      { m: '\\delta\\,(b - a)' },
      ', porque los pesos suman ',
      { m: 'b - a' },
      '. Con ',
      { m: '\\delta = 0.001' },
      ' en ',
      { m: '[0, 0.8]' },
      ': como mucho 0.0008, sin importar cuántos segmentos se usen.',
    ],
  },
]
</script>

<template>
  <div class="card">
    <h2>Fundamento común: integración numérica</h2>

    <h3 class="first-heading">El problema</h3>
    <p>Se quiere calcular</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.problem" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.problem" />
    <figure class="area-figure">
      <svg :viewBox="`0 0 ${W} ${H}`" role="img" aria-label="Área con signo bajo una curva entre a y b: la parte sobre el eje cuenta positiva y la de abajo, negativa">
        <polygon class="above" :points="above" />
        <polygon class="below" :points="below" />
        <line class="axis" x1="10" :y1="AXIS" :x2="W - 10" :y2="AXIS" />
        <polyline class="curve" :points="curve" />
        <text class="label" x="20" :y="AXIS + 22" text-anchor="middle">a</text>
        <text class="label" :x="W - 20" :y="AXIS + 22" text-anchor="middle">b</text>
        <text class="sign" x="110" :y="AXIS - 18" text-anchor="middle">+</text>
        <text class="sign" x="262" :y="AXIS + 26" text-anchor="middle">−</text>
      </svg>
      <figcaption>
        El área sobre el eje suma y la que queda debajo resta: por eso se habla de «área con signo».
      </figcaption>
    </figure>

    <h3>¿Por qué no usar siempre la antiderivada?</h3>
    <p>Por el teorema fundamental del cálculo,</p>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.ftc" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.ftc" />
    <p>pero hay tres situaciones en que no sirve:</p>
    <ol>
      <li>
        Muchas funciones <strong>no tienen antiderivada elemental</strong>: no se puede escribir con
        potencias, exponenciales, logaritmos ni funciones trigonométricas. Ejemplos:
        <MathFormula expression="e^{-x^2}" /> (su antiderivada usa la función especial erf),
        <MathFormula expression="\frac{\sin x}{x}" /> y <MathFormula expression="\sqrt{1 + x^3}" />.
      </li>
      <li>A veces sólo hay <strong>datos medidos</strong>: una tabla de valores, sin fórmula.</li>
      <li>La antiderivada puede existir y ser <strong>muy complicada</strong> de obtener o de evaluar.</li>
    </ol>

    <h3>Aplicaciones</h3>
    <ul>
      <li>Distancia recorrida a partir de velocidades medidas.</li>
      <li>Trabajo de una fuerza que cambia a lo largo del recorrido.</li>
      <li>Área de una sección transversal o volumen de un cuerpo.</li>
      <li>Valor promedio de una señal en un intervalo de tiempo.</li>
      <li>Probabilidades: el área bajo la curva normal.</li>
    </ul>

    <h3>Idea central</h3>
    <p>Se reemplaza <MathFormula expression="f" /> por algo fácil de integrar:</p>
    <ul>
      <li>
        <strong>Newton-Cotes:</strong> polinomios que pasan por puntos igualmente espaciados. El trapecio
        usa grado 1 (rectas); Simpson, grado 2 y 3 (parábolas y cúbicas).
      </li>
      <li><strong>Gauss:</strong> los puntos se eligen de forma óptima, no igualmente espaciados.</li>
    </ul>

    <h3>Forma general de una regla de integración (cuadratura)</h3>
    <div class="formula-box theory-formula"><MathFormula :expression="tex.quadrature" display-mode /></div>
    <GlossaryBlock :items="GLOSSARIES.quadrature" :summary="GLOSSARIES.quadratureSummary" />

    <h3>Simple frente a compuesta</h3>
    <ul>
      <li>
        Una regla <strong>simple</strong> usa un solo polinomio en todo
        <MathFormula expression="[a, b]" />.
      </li>
      <li>
        Una regla <strong>compuesta</strong> divide <MathFormula expression="[a, b]" /> en
        <MathFormula expression="n" /> segmentos y aplica la regla simple en cada uno.
      </li>
    </ul>

    <h3>Orden del error</h3>
    <p>
      Igual que en la diferenciación numérica: <MathFormula expression="O(h^n)" /> significa que, para
      <MathFormula expression="h" /> pequeño, el error se comporta como una constante por
      <MathFormula expression="h^n" />. Por ejemplo, <MathFormula expression="O(h^2)" /> significa
      que al duplicar <MathFormula expression="n" /> (es decir, al dividir
      <MathFormula expression="h" /> entre 2) el error se divide entre 4.
    </p>

    <h3>Integración frente a diferenciación</h3>
    <AlgorithmSteps :steps="CONTRAST" />
    <div class="formula-box theory-formula"><MathFormula :expression="tex.noise" display-mode /></div>
    <p class="formula-legend">
      <MathFormula expression="\tilde y" />: los datos con error; <MathFormula expression="y" />: los
      datos exactos. Por eso integrar datos ruidosos es seguro y derivarlos no lo es.
    </p>
  </div>
</template>

<style scoped>
.first-heading {
  margin-top: 0;
}

.area-figure {
  margin: var(--space-3) 0 var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  padding: var(--space-3) var(--space-4);
}

.area-figure svg {
  display: block;
  width: 100%;
  max-width: 360px;
  height: auto;
  margin: 0 auto;
}

.area-figure figcaption {
  margin-top: var(--space-2);
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  text-align: center;
}

.above {
  fill: var(--color-area-positive);
}

.below {
  fill: var(--color-area-negative);
}

.axis {
  stroke: var(--color-ink-muted);
  stroke-width: 1.2;
}

.curve {
  fill: none;
  stroke: var(--color-ink);
  stroke-width: 2.2;
}

.label,
.sign {
  fill: var(--color-ink-muted);
  font-size: 14px;
}

.sign {
  font-size: 20px;
  font-weight: var(--weight-bold);
  fill: var(--color-ink);
}
</style>
