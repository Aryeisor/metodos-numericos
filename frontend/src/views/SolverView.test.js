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

describe('marca y título de la pestaña', () => {
  it('la marca va dentro del enlace al inicio, sin una segunda parada de tabulación', async () => {
    const app = await open('/resolver/jacobi')
    const brand = app.get('header a.brand')
    expect(brand.attributes('href')).toBe('/')
    const mark = brand.get('svg.brand-mark')
    expect(mark.attributes('aria-hidden')).toBe('true')
    expect(mark.attributes('focusable')).toBe('false')
    expect(brand.text()).toBe('Métodos Iterativos')
    expect(brand.findAll('a, button, [tabindex]')).toHaveLength(0)
    app.unmount()
  })

  it('cambia al navegar entre métodos y entre Resolver y Teoría', async () => {
    const app = await open('/resolver/jacobi')
    expect(document.title).toBe('Jacobi · Resolver · Métodos Iterativos')
    await router.push('/resolver/newton')
    expect(document.title).toBe('Newton · Resolver · Métodos Iterativos')
    await router.push('/teoria/newton')
    expect(document.title).toBe('Newton · Teoría · Métodos Iterativos')
    await router.push('/manual')
    expect(document.title).toBe('Manual de usuario · Métodos Iterativos')
    app.unmount()
  }, 20_000)
})

describe('mientras calcula', () => {
  const button = (app) => app.get('.solve-actions .btn-primary')
  const status = (app) => app.get('.solve-actions [role="status"]')

  afterEach(() => {
    vi.useRealTimers()
    solveSystem.mockImplementation(() => new Promise(() => {}))
  })

  async function startSolving(outcome) {
    solveSystem.mockClear()
    solveSystem.mockImplementation(outcome)
    const app = await open('/resolver/jacobi', { ResultsTable: true })
    await app.get('.example-btn').trigger('click')
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    await button(app).trigger('click')
    return app
  }

  it('pasa a ocupado tras 300 ms y no se puede reenviar', async () => {
    const app = await startSolving(() => new Promise(() => {}))
    // Antes del umbral no cambia nada a la vista, pero un segundo clic no envía.
    expect(button(app).text()).toBe('Resolver')
    await button(app).trigger('click')
    expect(solveSystem).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(300)
    await flushPromises()
    expect(button(app).text()).toBe('Resolviendo…')
    expect(button(app).attributes('disabled')).toBeDefined()
    expect(button(app).find('.solve-spinner').exists()).toBe(true)
    expect(status(app).attributes('aria-live')).toBe('polite')
    expect(status(app).text()).toBe('Resolviendo…')
    app.unmount()
  })

  it('con un cálculo rápido el indicador no llega a mostrarse', async () => {
    const app = await startSolving(() => Promise.resolve({
      method: 'jacobi', category: 'linear_system', converged: true, iterations_used: 1,
      iterations: [{ iteration: 1, x: [1, 1, 1], error: 0 }], solution: [1, 1, 1],
      variables: ['x1', 'x2', 'x3'], warnings: [],
    }))
    await flushPromises()
    vi.advanceTimersByTime(1000)
    await flushPromises()
    expect(app.find('.solve-spinner').exists()).toBe(false)
    expect(button(app).text()).toBe('Resolver')
    expect(status(app).text()).toBe('')
    app.unmount()
  })
})

describe('lo que no existe', () => {
  it.each(['/resolver/no-existe', '/cualquier-cosa'])('%s muestra la página de «no encontrado»', async (path) => {
    const app = await open(path)
    expect(router.currentRoute.value.name).toBe('not-found')
    expect(app.get('h1').text()).toBe('Esta página no existe')
    expect(app.get('.not-found').text()).toContain(`Ver los ${CATALOG.length} métodos`)
    expect(app.get('.not-found a[href="/"]').text()).toBe('Ir al inicio')
    expect(document.title).toBe('Página no encontrada · Métodos Iterativos')
    app.unmount()
  })

  it('el buscador sin coincidencias lo dice dentro del panel', async () => {
    const app = await open('/resolver/jacobi')
    await app.get('.nav-link').trigger('click')
    await app.get('.nav-search input').setValue('zzzz')
    expect(app.get('.nav-status').text()).toBe(
      'No hay métodos que coincidan con «zzzz». Prueba con «integral», «derivada» o «sistema».'
    )
    app.unmount()
  })
})
