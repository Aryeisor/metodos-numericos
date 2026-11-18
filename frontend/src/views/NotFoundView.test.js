import { flushPromises, mount } from '@vue/test-utils'
import { beforeAll, describe, expect, it, vi } from 'vitest'

// Los 12 métodos reales (registry.py), con sus keywords, más uno de prueba
// que no se parece a nada: el botón tiene que contarlo.
const CATALOG = [
  ['jacobi', 'Jacobi', 'linear_system', 'Sistemas lineales', ['sistema', 'ecuaciones lineales', 'matriz', 'iterativo']],
  ['gauss-seidel', 'Gauss-Seidel', 'linear_system', 'Sistemas lineales', ['sistema', 'ecuaciones lineales', 'matriz', 'iterativo']],
  ['punto-fijo', 'Punto Fijo (Iterativo Secuencial)', 'nonlinear_system', 'Ecuaciones no lineales', ['sistema', 'no lineal', 'despeje', 'iterativo']],
  ['newton', 'Newton', 'nonlinear_system', 'Ecuaciones no lineales', ['sistema', 'no lineal', 'jacobiano', 'raphson']],
  ['bairstow', 'Bairstow', 'polynomial', 'Polinomios', ['raices', 'raíz', 'ecuación polinómica', 'factor cuadrático']],
  ['diferencias-finitas', 'Diferencias progresiva y regresiva', 'differentiation', 'Diferenciación numérica', ['derivada', 'diferencia progresiva', 'diferencia regresiva', 'secante']],
  ['tres-puntos', 'Fórmula de 3 puntos', 'differentiation', 'Diferenciación numérica', ['derivada', 'diferencia centrada', 'tres puntos']],
  ['cinco-puntos', 'Fórmula de 5 puntos', 'differentiation', 'Diferenciación numérica', ['derivada', 'diferencia centrada', 'cinco puntos']],
  ['trapecio', 'Método del trapecio', 'integration', 'Integración numérica', ['integral', 'área', 'trapecio compuesto']],
  ['simpson', 'Método de Simpson', 'integration', 'Integración numérica', ['integral', 'área', '1/3', '3/8']],
  ['romberg', 'Integración de Romberg', 'integration', 'Integración numérica', ['integral', 'área', 'extrapolación', 'richardson']],
  ['gauss', 'Cuadratura gaussiana', 'integration', 'Integración numérica', ['integral', 'área', 'legendre', 'gauss-legendre']],
  ['zz-prueba', 'Zz de prueba', 'integration', 'Integración numérica', []],
].map(([slug, name, category, category_label, keywords]) => ({
  slug, name, category, category_label, keywords, summary: `Resumen de ${name}`,
}))

vi.mock('../api/client', () => ({
  fetchMethods: () => Promise.resolve(CATALOG),
  fetchExamples: () => Promise.resolve([]),
  solveSystem: () => new Promise(() => {}),
  previewExpression: () => Promise.resolve(''),
}))

const { default: App } = await import('../App.vue')
const { default: router, addMethodRoutes } = await import('../router')
const { loadMethodRegistry, methodRegistry } = await import('../methods/registry')
const { parseMissingPath, suggestMethods } = await import('../methods/suggest')

beforeAll(async () => {
  await loadMethodRegistry()
  addMethodRoutes(methodRegistry.methods)
})

async function open(path) {
  await router.push(path)
  const app = mount(App, { global: { plugins: [router] }, attachTo: document.body })
  await flushPromises()
  return app
}

const cards = (app) => app.findAll('.suggestion')
const INTEGRATION = ['Método del trapecio', 'Método de Simpson', 'Integración de Romberg', 'Cuadratura gaussiana']

describe('página de «no encontrado»', () => {
  it.each([
    ['/resolver/integral', INTEGRATION, '/resolver/'],
    ['/resolver/jacoby', ['Jacobi'], '/resolver/'],
    ['/teoria/simson', ['Método de Simpson'], '/teoria/'],
    ['/resolver/derivada', ['Diferencias progresiva y regresiva', 'Fórmula de 3 puntos', 'Fórmula de 5 puntos'], '/resolver/'],
    ['/resolver/trapezio', ['Método del trapecio'], '/resolver/'],
    ['/resolver/xyz123', [], null],
    ['/cualquier-cosa', [], null],
  ])('%s sugiere %j', async (path, names, prefix) => {
    const app = await open(path)
    expect(router.currentRoute.value.name).toBe('not-found')
    expect(cards(app).map((c) => c.get('.suggestion-name').text())).toEqual(names)
    for (const card of cards(app)) expect(card.attributes('href').startsWith(prefix)).toBe(true)
    if (names.length) {
      const typed = path.split('/').at(-1)
      expect(app.get('h1').text()).toBe(`No existe un método llamado «${typed}»`)
      expect(app.get('.not-found-path').text()).toBe(path)
    } else {
      // Sin coincidencias, ni siquiera el título de la sección de sugerencias.
      expect(app.find('.not-found-suggestions').exists()).toBe(false)
      expect(app.get('h1').text()).toBe('Esta página no existe')
      expect(app.get('.not-found a[href="/"]').text()).toBe('Ir al inicio')
    }
    expect(app.find('.not-found-figure[aria-hidden="true"]').exists()).toBe(true)
    expect(document.title).toBe('Página no encontrada · Métodos Iterativos')
    app.unmount()
  })

  it('las tarjetas enlazan a la ruta exacta de su sección', async () => {
    let app = await open('/teoria/simson')
    expect(cards(app).map((c) => c.attributes('href'))).toEqual(['/teoria/simpson'])
    app.unmount()
    app = await open('/resolver/integral')
    expect(cards(app).map((c) => c.attributes('href'))).toEqual(['/resolver/trapecio', '/resolver/simpson', '/resolver/romberg', '/resolver/gauss'])
    app.unmount()
  })

  it('un segmento de 200 caracteres sale recortado', async () => {
    const long = `integral${'x'.repeat(192)}`
    const app = await open(`/resolver/${long}`)
    // Sin coincidencias: versión simple, sin el texto del usuario.
    expect(app.get('h1').text()).toBe('Esta página no existe')
    app.unmount()
    const words = `integral-${'a'.repeat(191)}`
    const app2 = await open(`/resolver/${words}`)
    const h1 = app2.get('h1').text()
    expect(h1).toContain('…')
    expect(h1.length).toBeLessThan(80)
    expect(app2.get('.not-found-path').text().length).toBe(40)
    app2.unmount()
  })

  it('el texto del usuario no se interpreta como HTML', async () => {
    const app = await open('/resolver/<b>integral</b>')
    expect(app.find('h1 b').exists()).toBe(false)
    app.unmount()
  })

  it('el botón cuenta los métodos del registro, incluido el de prueba', async () => {
    const app = await open('/cualquier-cosa')
    expect(app.get('.not-found .btn-primary').text()).toBe(`Ver los ${CATALOG.length} métodos`)
    expect(CATALOG.length).toBe(13)
    app.unmount()
  })
})

describe('suggestMethods', () => {
  const text = (path) => parseMissingPath(path.split('/')).text

  it('nunca más de cuatro, ni repetidas', () => {
    // «numerica» coincide con los 8 de diferenciación e integración.
    for (const path of ['/resolver/numerica', '/resolver/integral-area-gauss', '/resolver/gaus']) {
      const slugs = suggestMethods(text(path), methodRegistry.methods).map((m) => m.slug)
      expect(slugs.length).toBeLessThanOrEqual(4)
      expect(new Set(slugs).size).toBe(slugs.length)
    }
  })

  it('el error de escritura va primero', () => {
    expect(suggestMethods(text('/resolver/gaus'), methodRegistry.methods)[0].slug).toBe('gauss')
  })

  it('vacío o sólo símbolos: sin sugerencias', () => {
    for (const path of ['/resolver', '/resolver/---', '/resolver/%20']) {
      expect(suggestMethods(text(path), methodRegistry.methods)).toEqual([])
    }
  })

  it('normaliza tildes, guiones y guiones bajos', () => {
    expect(parseMissingPath(['Teoría', 'Gauss_Seidel'])).toEqual({ section: 'teoria', raw: 'Gauss_Seidel', text: 'gauss seidel' })
  })
})
