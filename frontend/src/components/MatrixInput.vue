<script setup>
const props = defineProps({
  n: { type: Number, required: true },
  a: { type: Array, required: true },
  b: { type: Array, required: true },
  x0: { type: Array, required: true },
})
const emit = defineEmits(['update:a', 'update:b', 'update:x0'])

function onCellInput(i, j, value) {
  const newA = props.a.map((row) => [...row])
  newA[i][j] = value === '' ? 0 : Number(value)
  emit('update:a', newA)
}

function onBInput(i, value) {
  const newB = [...props.b]
  newB[i] = value === '' ? 0 : Number(value)
  emit('update:b', newB)
}

function onX0Input(i, value) {
  const newX0 = [...props.x0]
  newX0[i] = value === '' ? 0 : Number(value)
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
.matrix-table input {
  width: 80px;
}

.eq-sign {
  border: none;
  text-align: center;
  font-weight: 700;
  padding: 0 4px;
}

.x0-row {
  margin-top: 16px;
}

.x0-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.x0-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.x0-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.x0-item input {
  width: 90px;
}
</style>
