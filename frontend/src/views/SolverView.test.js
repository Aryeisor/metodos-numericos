import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

// Forma de GET /api/methods/. Los cinco primeros, uno por categoría, son los
// que se prueban; el resto existe porque la teoría enlaza a sus rutas.
const CATALOG = [
  ['jacobi', 'Jacobi', 'linear_system', 'Sistemas lineales', 'Actualiza todas las variables a la vez'],
  ['newton', 'Newton', 'nonlinear_system', 'Ecuaciones no lineales', 'Usa la matriz Jacobiana'],
  ['bairstow', 'Bairstow', 'polynomial', 'Polinomios', 'Extrae factores cuadráticos'],
  ['tres-puntos', 'Fórmula de 3 puntos', 'differentiation', 'Diferenciación numérica', 'Pendiente de una parábola'],
  ['simpson', 'Método de Simpson', 'integration', 'Integración numérica', 'Une los puntos con parábolas'],
  ['gauss-seidel', 'Gauss-Seidel', 'linear_system', 'Sistemas lineales', ''],
  ['punto-fijo', 'Punto Fijo', 'nonlinear_system', 'Ecuaciones no lineales', ''],
  ['diferencias-finitas', 'Diferencias', 'differentiation', 'Diferenciación numérica', ''],
  ['cinco-puntos', 'Fórmula de 5 puntos', 'differentiation', 'Diferenciación numérica', ''],
  ['trapecio', 'Método del trapecio', 'integration', 'Integración numérica', ''],
  ['romberg', 'Integración de Romberg', 'integration', 'Integración numérica', ''],
  ['gauss', 'Cuadratura gaussiana', 'integration', 'Integración numérica', ''],
].map(([slug, name, category, category_label, summary]) => ({ slug, name, category, category_label, summary }))

const EXAMPLES = [
  {
    id: 'basico-3x3',
    name: 'Sistema básico 3x3',
    description: 'Sistema diagonalmente dominante sencillo.',
    n: 3,
    A: [[4, 1, 1], [2, 5, 2], [1, 2, 4]],
    b: [6, 9, 7],
    x0: [0, 0, 0],
    tolerance: 1e-6,
    max_iterations: 100,
  },
  { id: 'otro', name: 'Otro', description: '', n: 3, A: [[4, 1, 1], [2, 5, 2], [1, 2, 4]], b: [1, 2, 3], x0: [0, 0, 0], tolerance: 1e-6, max_iterations: 100 },
]

// Por defecto la petición de resolver no termina; los tests del resultado la
// resuelven o la rechazan.
const solveSystem = vi.hoisted(() => vi.fn(() => new Promise(() => {})))

vi.mock('../api/client', () => ({
  fetchMethods: () => Promise.resolve(CATALOG),
  fetchExamples: () => Promise.resolve(EXAMPLES),
  solveSystem,
  previewExpression: () => Promise.resolve(''),
}))

const { default: App } = await import('../App.vue')
const { default: router, addMethodRoutes } = await import('../router')
const { loadMethodRegistry, methodRegistry } = await import('../methods/registry')

beforeAll(async () => {
  await loadMethodRegistry()
  addMethodRoutes(methodRegistry.methods)
})

async function open(path, stubs = {}) {
  await router.push(path)
  await router.isReady()
  const app = mount(App, { global: { plugins: [router], stubs }, attachTo: document.body })
  await flushPromises()
  return app
}

describe('encabezado de la vista', () => {
  it.each(CATALOG.slice(0, 5).flatMap((method) => ['resolver', 'teoria'].map((view) => ({ view, method }))))(
    '/$view/$method.slug muestra categoría, nombre y resumen',
    async ({ view, method }) => {
      const app = await open(`/${view}/${method.slug}`)
      const header = app.get('.method-header')
      expect(header.get('.method-category').text()).toBe(method.category_label)
      expect(header.get('h1').text()).toBe(method.name)
      expect(header.get('.method-summary').text()).toBe(method.summary)
      // --text-display sólo lo usa la regla global de h1: un h1 por página.
      expect(app.findAll('h1')).toHaveLength(1)
      app.unmount()
    },
    20_000 // las páginas de teoría con muchas fórmulas pasan de 5 s en happy-dom
  )

  it('--text-display se usa una sola vez en todos los estilos', () => {
    const src = join(process.cwd(), 'src') // vitest corre desde frontend/
    const uses = readdirSync(src, { recursive: true })
      .filter((file) => /\.(vue|css)$/.test(file))
      .flatMap((file) => readFileSync(join(src, file), 'utf8').match(/var\(--text-display\)/g) ?? [])
    expect(uses).toHaveLength(1)
  })

  it('esa única regla alcanza al h1 y al valor de la tarjeta de respuesta, nada más', () => {
    const css = readFileSync(join(process.cwd(), 'src', 'style.css'), 'utf8')
    const selectors = css.match(/([^{}]+)\{[^}]*var\(--text-display\)/)[1]
    expect(selectors.replace(/\/\*[^]*?\*\//g, '').split(',').map((sel) => sel.trim())).toEqual(['h1', '.answer-value'])
  })
})

describe('ejemplos plegables', () => {
  const toggle = (app) => app.get('.examples-toggle')
  const isOpen = (app) => toggle(app).attributes('aria-expanded') === 'true'

  it('empieza abierta y se pliega al cargar un ejemplo, mostrando su nombre', async () => {
    const app = await open('/resolver/jacobi')
    expect(isOpen(app)).toBe(true)
    await app.get('.example-btn').trigger('click')
    expect(isOpen(app)).toBe(false)
    expect(toggle(app).text()).toContain('Sistema básico 3x3')
    expect(toggle(app).text()).toContain('Cambiar')
    app.unmount()
  })

  it('se pliega al escribir en el formulario y muestra cuántos ejemplos hay', async () => {
    const app = await open('/resolver/bairstow')
    expect(isOpen(app)).toBe(true)
    await app.get('.input-card input').setValue('5')
    expect(isOpen(app)).toBe(false)
    expect(toggle(app).text()).toContain(`Ejemplos precargados (${EXAMPLES.length})`)
    app.unmount()
  })

  it('se abre y se cierra a mano', async () => {
    const app = await open('/resolver/newton')
    await toggle(app).trigger('click')
    expect(isOpen(app)).toBe(false)
    await toggle(app).trigger('click')
    expect(isOpen(app)).toBe(true)
    app.unmount()
  })
})

describe('después de resolver', () => {
  // Respuesta mínima de Jacobi; el detalle (gráfico y tabla) no se monta.
  const RESULT = {
    method: 'jacobi',
    category: 'linear_system',
    converged: true,
    iterations_used: 40,
    iterations: [{ iteration: 40, x: [1, 1, 1], error: 8.04e-7 }],
    solution: [1, 1, 1],
    variables: ['x1', 'x2', 'x3'],
    warnings: [],
  }
  const stubs = { ResultsTable: true }
  // Los tamaños de --text-display en la página: el h1 y el bloque de valores.
  const displayUses = (app) => app.findAll('h1').length + app.findAll('.answer-values:not(.is-compact)').length

  afterEach(() => solveSystem.mockImplementation(() => new Promise(() => {})))

  async function solve(outcome) {
    const scrolled = vi.spyOn(HTMLElement.prototype, 'scrollIntoView').mockImplementation(() => {})
    solveSystem.mockImplementation(outcome)
    const app = await open('/resolver/jacobi', stubs)
    await app.get('.example-btn').trigger('click')
    expect(displayUses(app)).toBe(1) // sin resultado: sólo el nombre del método
    await app.get('.solve-btn').trigger('click')
    await flushPromises()
    const target = scrolled.mock.contexts.at(-1)
    scrolled.mockRestore()
    return { app, target }
  }

  it('la página se desplaza al resultado y el foco queda en su encabezado', async () => {
    const { app, target } = await solve(() => Promise.resolve(RESULT))
    const heading = app.get('.answer-card h2')
    expect(target).toBe(app.get('.answer-card').element)
    expect(document.activeElement).toBe(heading.element)
    expect(heading.text()).toBe('Resultado (Jacobi)')
    expect(heading.attributes('tabindex')).toBe('-1')
    expect(app.findAll('.answer-value').map((v) => v.text())).toEqual(['1', '1', '1'])
    expect(displayUses(app)).toBe(2) // el nombre del método y la respuesta
    app.unmount()
  })

  it('con un error de validación, el desplazamiento y el foco van al mensaje', async () => {
    const { app, target } = await solve(() => Promise.reject({ response: { data: { detail: 'La matriz es singular.' } } }))
    const alert = app.get('.alert-danger')
    expect(alert.text()).toBe('La matriz es singular.')
    expect(target).toBe(alert.element)
    expect(document.activeElement).toBe(alert.element)
    expect(app.find('.answer-card').exists()).toBe(false)
    app.unmount()
  })
})
