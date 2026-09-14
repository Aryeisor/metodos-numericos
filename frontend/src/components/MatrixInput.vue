<script setup>
const props = defineProps({
  n: { type: Number, required: true },
  a: { type: Array, required: true },
  b: { type: Array, required: true },
  x0: { type: Array, required: true },
})
const emit = defineEmits(['update:a', 'update:b', 'update:x0'])

// Se guarda el valor tal cual lo escribe el usuario (sin convertir a Number
// en cada tecla): mientras se escribe "-" o "-1." el navegador reporta un
// valor numérico vacío, y forzar la conversión aquí reescribía el campo a
// "0" en cada pulsación, impidiendo escribir números negativos o con punto
// decimal. La conversión final a número ocurre al resolver el sistema.
function onCellInput(i, j, value) {
  const newA = props.a.map((row) => [...row])
  newA[i][j] = value
  emit('update:a', newA)
}

function onBInput(i, value) {
  const newB = [...props.b]
  newB[i] = value
  emit('update:b', newB)
}

function onX0Input(i, value) {
  const newX0 = [...props.x0]
  newX0[i] = value
  emit('update:x0', newX0)
}
</script>

<template>
  <div>
    <div class="table-scroll">
      <table class="matrix-table">
        <thead>
          <tr>
            <th v-for="j in n" :key="'h-' + j">x{{ j }}</th>
            <th></th>
            <th>b</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in n" :key="'row-' + i">
            <td v-for="j in n" :key="'cell-' + i + '-' + j">
              <input
                type="number"
                step="any"
                :value="a[i - 1][j - 1]"
                @input="onCellInput(i - 1, j - 1, $event.target.value)"
              />
            </td>
            <td class="eq-sign">=</td>
            <td>
              <input
                type="number"
                step="any"
                :value="b[i - 1]"
                @input="onBInput(i - 1, $event.target.value)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="x0-row">
      <label>Vector inicial x0 (opcional, por defecto ceros)</label>
      <div class="x0-inputs">
        <div v-for="i in n" :key="'x0-' + i" class="x0-item">
          <span class="x0-label">x{{ i }}⁽⁰⁾</span>
          <input
            type="number"
            step="any"
            :value="x0[i - 1]"
            @input="onX0Input(i - 1, $event.target.value)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Encabezados e inputs centrados en su columna, para que cada coeficiente
   quede alineado bajo su variable. */
.matrix-table th,
.matrix-table td {
  text-align: center;
  padding: var(--space-2);
}

.matrix-table th {
  font-style: italic;
}

.matrix-table tbody tr:nth-child(even) {
  background: transparent;
}

.matrix-table input {
  width: 84px;
  text-align: right;
}

.eq-sign {
  border: none;
  text-align: center;
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  padding: 0 var(--space-1);
}

.x0-row {
  margin-top: var(--space-5);
}

.x0-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.x0-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.x0-label {
  font-size: var(--text-small);
  color: var(--color-ink-muted);
  font-weight: var(--weight-medium);
}

.x0-item input {
  width: 92px;
  text-align: right;
}

/* En móvil un sistema 3x3 completo (con b) cabe sin desplazamiento; con más
   variables la tabla sigue siendo desplazable dentro de su contenedor. */
@media (max-width: 480px) {
  .matrix-table th,
  .matrix-table td {
    padding: var(--space-1);
  }

  .matrix-table input,
  .x0-item input {
    width: 64px;
    padding-left: var(--space-2);
    padding-right: var(--space-2);
  }
}
</style>
