// Registro de métodos del frontend.
//
// El catálogo (qué métodos existen, su nombre y su categoría) viene del
// backend en GET /api/methods/, que es la única fuente de verdad. Aquí sólo se
// asocia cada categoría con su interfaz (formulario, detalle del resultado,
// PDF, teoría). Agregar un método a una categoría existente no requiere tocar
// el frontend; una categoría nueva sólo requiere registrar su interfaz abajo.
import { markRaw, reactive, readonly } from 'vue'
import { fetchMethods } from '../api/client'
import linearSystem from './linear'

// markRaw: contienen componentes, que no deben volverse objetos reactivos.
const CATEGORY_UI = {
  linear_system: markRaw(linearSystem),
}

const state = reactive({
  status: 'idle', // idle | loading | ready | error
  methods: [], // [{ slug, name, category, categoryLabel, ui }]
})

let loading = null

/** Carga el catálogo una sola vez. Nunca rechaza: los errores quedan en `status`. */
export function loadMethodRegistry() {
  if (!loading) {
    state.status = 'loading'
    loading = fetchMethods()
      .then((catalog) => {
        state.methods = catalog
          .filter((method) => {
            if (CATEGORY_UI[method.category]) return true
            console.warn(
              `Método "${method.slug}" ignorado: la categoría "${method.category}" no tiene interfaz registrada.`
            )
            return false
          })
          .map((method) => ({
            slug: method.slug,
            name: method.name,
            category: method.category,
            categoryLabel: method.category_label,
            ui: CATEGORY_UI[method.category],
          }))
        state.status = 'ready'
      })
      .catch(() => {
        state.status = 'error'
      })
  }
  return loading
}

export const methodRegistry = readonly(state)

export function getMethod(slug) {
  return state.methods.find((method) => method.slug === slug) ?? null
}

/** True si la categoría del método tiene teoría escrita para él. */
export function hasTheory(method) {
  return Boolean(method.ui.theorySections?.[method.slug])
}

/**
 * Métodos agrupados por categoría, en el orden en que los entrega el backend.
 * Con `filter`, sólo los que lo cumplen; una categoría que se queda sin
 * métodos no aparece.
 */
export function methodsByCategory(filter = () => true) {
  const groups = []
  for (const method of state.methods.filter(filter)) {
    let group = groups.find((g) => g.category === method.category)
    if (!group) {
      group = { category: method.category, label: method.categoryLabel, methods: [] }
      groups.push(group)
    }
    group.methods.push(method)
  }
  return groups
}

/** Métodos de la misma categoría (comparten formulario y datos de entrada). */
export function siblingMethods(slug) {
  const method = getMethod(slug)
  return method ? state.methods.filter((m) => m.category === method.category) : []
}

export { solveRouteName, theoryRouteName } from './routeNames'
