<script setup>
// Referencia rápida de cómo se escribe cada operación en un campo de
// ecuación. Complementa la barra de símbolos para quien prefiere teclear.
// Coincide con lo que acepta el parser del backend (expressions/parser.py).
const ROWS = [
  { name: 'Raíz cuadrada', syntax: ['sqrt(x)'] },
  { name: 'Potencia', syntax: ['x^2', 'x**2'] },
  { name: 'Logaritmo base 10', syntax: ['log(x)'] },
  { name: 'Logaritmo natural', syntax: ['ln(x)'] },
  { name: 'Valor absoluto', syntax: ['abs(x)'] },
  { name: 'Exponencial', syntax: ['exp(x)', 'e^x'] },
  { name: 'Trigonométricas', syntax: ['sin(x)', 'cos(x)', 'tan(x)'] },
  { name: 'Constantes', syntax: ['pi', 'e'] },
  { name: 'Producto', syntax: ['3*x', '3x'] },
  { name: 'División', syntax: ['(x + 1)/2'] },
]
</script>

<template>
  <dl class="syntax-help">
    <div v-for="row in ROWS" :key="row.name" class="syntax-row">
      <dt>{{ row.name }}</dt>
      <dd>
        <template v-for="(code, k) in row.syntax" :key="code">
          <span v-if="k" class="syntax-or">o</span>
          <code>{{ code }}</code>
        </template>
      </dd>
    </div>
  </dl>
</template>

<style scoped>
.syntax-help {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(250px, 100%), 1fr));
  gap: var(--space-1) var(--space-5);
  margin: 0;
  font-size: var(--text-small);
}

.syntax-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
  padding: 2px 0;
  border-bottom: 1px dashed var(--color-line);
}

dt {
  color: var(--color-ink-muted);
}

dd {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: baseline;
  gap: var(--space-1);
}

code {
  font-family: 'Consolas', 'Courier New', monospace;
  color: var(--color-ink);
  background: var(--color-sunken);
  border-radius: 4px;
  padding: 0 4px;
}

.syntax-or {
  color: var(--color-ink-muted);
}
</style>
