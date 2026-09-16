<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { formatNumber } from '../utils/iterationSteps'
import { INPUT_ERROR_MESSAGES, parseNumericInput } from '../utils/numberInput'

const props = defineProps({
  n: { type: Number, required: true },
  a: { type: Array, required: true },
  b: { type: Array, required: true },
  x0: { type: Array, required: true },
})
const emit = defineEmits(['update:a', 'update:b', 'update:x0'])

// El componente es dueño del TEXTO que se está editando; al padre sólo se le
// emiten valores numéricos exactos. Así el redondeo a 6 decimales que se
// muestra al salir del campo nunca llega al modelo ni al backend.
const texts = reactive({ a: [], b: [], x0: [] })
const errors = reactive({})
const editingKey = ref(null)

function displayText(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return ''
  return formatNumber(value)
}

function syncTexts() {
  texts.a = props.a.map((row, i) =>
    row.map((value, j) => (editingKey.value === `a-${i}-${j}` ? texts.a[i]?.[j] : displayText(value)))
  )
  texts.b = props.b.map((value, i) =>
    editingKey.value === `b-${i}` ? texts.b[i] : displayText(value)
  )
  texts.x0 = props.x0.map((value, i) =>
    editingKey.value === `x0-${i}` ? texts.x0[i] : displayText(value)
  )
}

syncTexts()
watch(() => [props.a, props.b, props.x0, props.n], syncTexts)

// El valor se emite en cada tecla (NaN si aún no es válido, lo que impide
// enviar el formulario), pero el error sólo se MUESTRA al salir del campo:
// escribiendo "6/7" el estado intermedio "6/" no debe pintarse en rojo.
function commit(key, text, apply) {
  delete errors[key]
  apply(parseNumericInput(text).value)
}

function onCellInput(i, j, text) {
  texts.a[i][j] = text
  commit(`a-${i}-${j}`, text, (value) => {
    const next = props.a.map((row) => [...row])
    next[i][j] = value
    emit('update:a', next)
  })
}

function onBInput(i, text) {
  texts.b[i] = text
  commit(`b-${i}`, text, (value) => {
    const next = [...props.b]
    next[i] = value
    emit('update:b', next)
  })
}

function onX0Input(i, text) {
  texts.x0[i] = text
  commit(`x0-${i}`, text, (value) => {
    const next = [...props.x0]
    next[i] = value
    emit('update:x0', next)
  })
}

function errorLabel(key) {
  const [group, i, j] = key.split('-')
  if (group === 'a') return `a${Number(i) + 1}${Number(j) + 1}`
  if (group === 'b') return `b${Number(i) + 1}`
  return `x${Number(i) + 1} inicial`
}

const errorList = computed(() =>
  Object.keys(errors).map((key) => ({ key, label: errorLabel(key), message: errors[key] }))
)

function onFocus(key) {
  editingKey.value = key
}

/* Al salir del campo el texto pasa a la versión redondeada a 6 decimales (el
   mismo criterio de las tablas de resultados). El valor del modelo no cambia:
   sigue siendo el de precisión completa. */
function onBlur(key, currentValue) {
  editingKey.value = null
  const [group, ...rest] = key.split('-')
  const current = group === 'a' ? texts.a[Number(rest[0])][Number(rest[1])] : texts[group][Number(rest[0])]

  const { error } = parseNumericInput(current)
  if (error) {
    errors[key] = INPUT_ERROR_MESSAGES[error]
    return
  }

  delete errors[key]
  const text = displayText(currentValue)
  if (group === 'a') texts.a[Number(rest[0])][Number(rest[1])] = text
  else texts[group][Number(rest[0])] = text
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
                type="text"
                inputmode="decimal"
                :value="texts.a[i - 1]?.[j - 1]"
                :class="{ 'is-invalid': errors[`a-${i - 1}-${j - 1}`] }"
                :aria-invalid="Boolean(errors[`a-${i - 1}-${j - 1}`])"
                :title="errors[`a-${i - 1}-${j - 1}`]"
                @input="onCellInput(i - 1, j - 1, $event.target.value)"
                @focus="onFocus(`a-${i - 1}-${j - 1}`)"
                @blur="onBlur(`a-${i - 1}-${j - 1}`, a[i - 1][j - 1])"
              />
            </td>
            <td class="eq-sign">=</td>
            <td>
              <input
                type="text"
                inputmode="decimal"
                :value="texts.b[i - 1]"
                :class="{ 'is-invalid': errors[`b-${i - 1}`] }"
                :aria-invalid="Boolean(errors[`b-${i - 1}`])"
                :title="errors[`b-${i - 1}`]"
                @input="onBInput(i - 1, $event.target.value)"
                @focus="onFocus(`b-${i - 1}`)"
                @blur="onBlur(`b-${i - 1}`, b[i - 1])"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="input-hint">
      Puedes escribir fracciones, por ejemplo <strong>6/7</strong>. Al salir del campo se
      muestra redondeado a 6 decimales, pero el cálculo usa el valor exacto.
    </p>

    <div class="x0-row">
      <label>Vector inicial x0 (opcional, por defecto ceros)</label>
      <div class="x0-inputs">
        <div v-for="i in n" :key="'x0-' + i" class="x0-item">
          <span class="x0-label">x{{ i }}⁽⁰⁾</span>
          <input
            type="text"
            inputmode="decimal"
            :value="texts.x0[i - 1]"
            :class="{ 'is-invalid': errors[`x0-${i - 1}`] }"
            :aria-invalid="Boolean(errors[`x0-${i - 1}`])"
            :title="errors[`x0-${i - 1}`]"
            @input="onX0Input(i - 1, $event.target.value)"
            @focus="onFocus(`x0-${i - 1}`)"
            @blur="onBlur(`x0-${i - 1}`, x0[i - 1])"
          />
        </div>
      </div>
    </div>

    <ul v-if="errorList.length" class="input-errors">
      <li v-for="item in errorList" :key="item.key">{{ item.label }}: {{ item.message }}</li>
    </ul>
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

.input-hint {
  margin: var(--space-3) 0 0;
  font-size: var(--text-small);
  color: var(--color-ink-muted);
}

.is-invalid {
  border-color: var(--color-danger);
}

.is-invalid:focus {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px var(--color-danger-bg);
}

.input-errors {
  margin: var(--space-4) 0 0;
  padding-left: var(--space-5);
  font-size: var(--text-small);
  color: var(--color-danger);
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
