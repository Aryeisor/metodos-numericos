// Vista previa en vivo de una lista de ecuaciones: para cada fila consulta
// POST /api/expressions/preview (con debounce) y expone su LaTeX o su error.
// No depende de ningún método; lo usa cualquier formulario de ecuaciones.
//
// - Debounce por fila: sólo se consulta cuando el usuario deja de escribir.
// - Caché por contenido (texto + variables): volver a un texto ya visto, o
//   quitar una fila (las demás se corren de posición), no repite peticiones.
// - Carreras: cada fila recuerda qué texto está esperando; una respuesta que
//   llega cuando el texto ya cambió se guarda en la caché pero no se muestra,
//   y la petición anterior se cancela al programar una nueva.
// - Sin parpadeo: mientras llega la respuesta nueva se sigue mostrando la
//   anterior (marcada como `stale`), en vez de vaciar la fila en cada tecla.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { previewExpression } from '../api/client'

export const PREVIEW_DEBOUNCE_MS = 450
const CACHE_LIMIT = 200
const NETWORK_ERROR = 'No fue posible verificar la ecuación: sin conexión con el servidor.'

function firstMessage(data) {
  if (Array.isArray(data?.equation) && data.equation.length) return data.equation[0]
  if (Array.isArray(data?.variables) && data.variables.length) {
    return `Variables: ${data.variables[0]}`
  }
  if (typeof data?.detail === 'string') return data.detail
  return 'La ecuación no es válida.'
}

/**
 * @param {() => string[]} getTexts      texto de cada fila
 * @param {() => string[]} getVariables  variables del sistema (válidas en todas las filas)
 * @returns {{ previews: import('vue').ComputedRef<Array<{
 *   status: 'empty' | 'pending' | 'valid' | 'invalid', latex: string | null,
 *   error: string | null, stale: boolean }>> }}
 */
export function useExpressionPreviews(getTexts, getVariables) {
  const cache = new Map() // clave -> { latex } | { error }
  const shown = ref([]) // por fila: { key, latex?, error? } | null
  const pending = ref([]) // por fila: hay una consulta programada o en curso
  let timers = []
  let controllers = []
  let awaiting = [] // por fila: clave que se está esperando

  const keyOf = (text, variables) => JSON.stringify([text, variables])

  function remember(key, value) {
    cache.set(key, value)
    if (cache.size > CACHE_LIMIT) cache.delete(cache.keys().next().value)
  }

  function cancel(i) {
    clearTimeout(timers[i])
    controllers[i]?.abort()
    timers[i] = null
    controllers[i] = null
    awaiting[i] = null
  }

  function show(i, value, isPending) {
    shown.value[i] = value
    pending.value[i] = isPending
  }

  async function request(i, key, text, variables) {
    const controller = new AbortController()
    controllers[i] = controller
    let value
    try {
      value = { latex: await previewExpression(text, variables, { signal: controller.signal }) }
      remember(key, value)
    } catch (err) {
      if (controller.signal.aborted) return
      if (err.response?.status === 400) {
        value = { error: firstMessage(err.response.data) }
        remember(key, value)
      } else {
        // Error de red: no se guarda, se reintenta en el próximo cambio.
        value = { error: NETWORK_ERROR }
      }
    }
    if (awaiting[i] !== key) return // llegó tarde: el texto de la fila ya cambió
    controllers[i] = null
    awaiting[i] = null
    show(i, { key, ...value }, false)
  }

  function update() {
    const texts = getTexts()
    const variables = [...getVariables()]

    // Se agregó o quitó una fila: las posiciones cambiaron, así que se
    // reinicia el estado por fila (lo ya consultado sale de la caché).
    if (texts.length !== shown.value.length) {
      timers.forEach((_, i) => cancel(i))
      timers = []
      controllers = []
      awaiting = []
      shown.value = texts.map(() => null)
      pending.value = texts.map(() => false)
    }

    texts.forEach((raw, i) => {
      const text = (raw ?? '').trim()
      if (!text) {
        cancel(i)
        show(i, null, false)
        return
      }
      const key = keyOf(text, variables)
      if (cache.has(key)) {
        cancel(i)
        show(i, { key, ...cache.get(key) }, false)
        return
      }
      if (awaiting[i] === key || shown.value[i]?.key === key) return
      cancel(i)
      awaiting[i] = key
      pending.value[i] = true
      timers[i] = setTimeout(() => request(i, key, text, variables), PREVIEW_DEBOUNCE_MS)
    })
  }

  watch(() => JSON.stringify([getTexts(), getVariables()]), update, { immediate: true })
  onBeforeUnmount(() => timers.forEach((_, i) => cancel(i)))

  const previews = computed(() =>
    shown.value.map((row, i) => {
      const isPending = Boolean(pending.value[i])
      if (!row) {
        return { status: isPending ? 'pending' : 'empty', latex: null, error: null, stale: false }
      }
      return {
        status: row.error ? 'invalid' : 'valid',
        latex: row.latex ?? null,
        error: row.error ?? null,
        stale: isPending,
      }
    })
  )

  return { previews }
}
