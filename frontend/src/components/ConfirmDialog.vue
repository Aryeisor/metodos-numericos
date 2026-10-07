<script setup>
// Diálogo de confirmación con el estilo de la app (en lugar de window.confirm).
// Usa <dialog> nativo con showModal(): el navegador se encarga del fondo,
// de atrapar el foco dentro del diálogo y de cerrarlo con Esc (= cancelar).
// El foco inicial va a «Cancelar», la opción que no borra nada.
import { nextTick, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  message: { type: String, required: true },
  confirmLabel: { type: String, default: 'Aceptar' },
  cancelLabel: { type: String, default: 'Cancelar' },
})
const emit = defineEmits(['confirm', 'cancel'])

const dialogRef = ref(null)
const cancelRef = ref(null)

watch(
  () => props.open,
  async (open) => {
    const dialog = dialogRef.value
    if (!dialog) return
    if (open && !dialog.open) {
      dialog.showModal()
      await nextTick()
      cancelRef.value?.focus()
    } else if (!open && dialog.open) {
      dialog.close()
    }
  }
)

// Esc dispara `cancel` en el <dialog>: se trata como «Cancelar».
function onCancel(event) {
  event.preventDefault()
  emit('cancel')
}

// Un clic en el fondo (fuera de la caja) también cancela.
function onBackdropClick(event) {
  if (event.target === dialogRef.value) emit('cancel')
}
</script>

<template>
  <dialog
    ref="dialogRef"
    class="confirm-dialog"
    aria-labelledby="confirm-dialog-message"
    @cancel="onCancel"
    @click="onBackdropClick"
  >
    <div class="confirm-body">
      <p id="confirm-dialog-message" class="confirm-message">{{ message }}</p>
      <div class="confirm-actions">
        <button ref="cancelRef" type="button" class="btn btn-secondary" @click="emit('cancel')">
          {{ cancelLabel }}
        </button>
        <button type="button" class="btn btn-primary" @click="emit('confirm')">{{ confirmLabel }}</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped>
.confirm-dialog {
  padding: 0;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-nested);
  background: var(--color-surface);
  color: var(--color-ink);
  box-shadow: var(--shadow-interactive-hover);
  width: min(420px, calc(100vw - 2 * var(--space-4)));
}

.confirm-dialog::backdrop {
  background: rgba(15, 23, 42, 0.45);
}

.confirm-body {
  padding: var(--space-5);
}

.confirm-message {
  margin: 0 0 var(--space-5);
  font-size: var(--text-body);
  line-height: 1.5;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: var(--space-3);
}
</style>
