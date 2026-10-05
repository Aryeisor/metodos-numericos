<script setup>
// Fila de campos numéricos que aceptan decimales y fracciones (6/7). Por
// defecto es el punto inicial x0 de Punto Fijo y Newton; Bairstow la usa
// también para r₀ y s₀ y para los coeficientes del polinomio (con otro título,
// sufijo y etiquetas de error).
//
// El componente es dueño del TEXTO; hacia afuera sólo emite números con su
// precisión completa (NaN mientras el texto no sea válido). Mismo criterio
// que MatrixInput: el error se muestra al salir del campo.
import { computed, reactive, ref, watch } from 'vue'
import { formatNumber } from '../utils/iterationSteps'
import { INPUT_ERROR_MESSAGES, parseNumericInput } from '../utils/numberInput'

const props = defineProps({
  values: { type: Array, required: true },
  // Nombre de la variable de cada campo (puede estar vacío mientras se escribe).
  labels: { type: Array, required: true },
  // Opcionales; los valores por defecto son los del punto inicial x0.
  title: { type: String, default: 'Punto inicial x0 (opcional, por defecto ceros)' },
  // Se agrega al nombre de cada campo (x⁽⁰⁾).
  suffix: { type: String, default: '⁽⁰⁾' },
  // Cómo se nombra cada campo en la lista de errores y para lectores de
  // pantalla; por defecto "<nombre> inicial" / "Valor inicial de <nombre>".
  errorLabels: { type: Array, default: null },
})
const emit = defineEmits(['update:values'])

const texts = ref([])
const errors = reactive({})
const editingIndex = ref(null)

function displayText(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return ''
  return formatNumber(value)
}

function syncTexts() {
  texts.value = props.values.map((value, i) =>
    editingIndex.value === i ? texts.value[i] : displayText(value)
  )
}

syncTexts()
watch(() => props.values, syncTexts)

// Los errores están indexados por posición: al cambiar el número de campos
// (se agregó o quitó una variable) dejan de corresponder y se descartan.
watch(
  () => props.values.length,
  () => {
    for (const key of Object.keys(errors)) delete errors[key]
  }
)

function onInput(index, text) {
  texts.value[index] = text
  delete errors[index]
  const { value } = parseNumericInput(text)
  emit('update:values', props.values.map((v, i) => (i === index ? value : v)))
}

function onBlur(index) {
  editingIndex.value = null
  const { error } = parseNumericInput(texts.value[index])
  if (error) {
    errors[index] = INPUT_ERROR_MESSAGES[error]
    return
  }
  texts.value[index] = displayText(props.values[index])
}

const nameOf = (i) => props.labels[i] || `variable ${i + 1}`

const errorList = computed(() =>
  Object.keys(errors).map((index) => ({
    index,
    label: props.errorLabels?.[index] ?? `${nameOf(Number(index))} inicial`,
    message: errors[index],
  }))
)
</script>

<template>
  <div class="x0-row">
    <label>{{ title }}</label>
    <div class="x0-inputs">
      <div v-for="(value, i) in values" :key="'x0-' + i" class="x0-item">
        <span class="x0-label">{{ labels[i] || '?' }}{{ suffix }}</span>
        <input
          type="text"
          inputmode="decimal"
          :value="texts[i]"
          :class="{ 'is-invalid': errors[i] }"
          :aria-invalid="Boolean(errors[i])"
          :aria-label="errorLabels?.[i] ?? `Valor inicial de ${nameOf(i)}`"
          :title="errors[i]"
          @input="onInput(i, $event.target.value)"
          @focus="editingIndex = i"
          @blur="onBlur(i)"
        />
      </div>
    </div>
    <p class="input-hint">
      Admite fracciones, por ejemplo <strong>1/3</strong>; el cálculo usa el valor exacto.
    </p>

    <ul v-if="errorList.length" class="input-errors">
      <li v-for="item in errorList" :key="item.index">{{ item.label }}: {{ item.message }}</li>
    </ul>
  </div>
</template>

<style scoped>
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

@media (max-width: 480px) {
  .x0-item input {
    width: 72px;
  }
}
</style>
