import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ResultAnswer from './ResultAnswer.vue'

// IntersectionObserver controlado a mano: `intersect` simula que la tarjeta
// entra o sale de la pantalla.
let intersect
beforeEach(() => {
  vi.stubGlobal(
    'IntersectionObserver',
    class {
      constructor(callback) {
        intersect = (isIntersecting, top) => callback([{ isIntersecting, boundingClientRect: { top } }])
      }
      observe() {}
      disconnect() {}
    }
  )
})
afterEach(() => {
  vi.unstubAllGlobals()
  window.happyDOM.setViewport({ width: 1024, height: 768 })
})

const values = (n) => Array.from({ length: n }, (_, i) => ({ label: `x${i + 1}`, value: String(i + 1) }))
const render = (answer = {}) =>
  mount(ResultAnswer, {
    props: {
      methodName: 'Jacobi',
      answer: { values: values(3), noun: 'incógnitas', ok: true, status: 'Alcanzó la tolerancia en 40 iteraciones.', ...answer },
    },
    attachTo: document.body,
  })

describe('tarjeta de respuesta', () => {
  it('muestra cada valor con su etiqueta, el estado y los dos botones', () => {
    const card = render()
    expect(card.get('h2').text()).toBe('Resultado (Jacobi)')
    expect(card.findAll('.answer-item').map((item) => item.text())).toEqual(['x11', 'x22', 'x33'])
    expect(card.get('.answer-status').text()).toContain('Alcanzó la tolerancia en 40 iteraciones.')
    expect(card.findAll('.answer-actions button').map((b) => b.text())).toEqual(['Descargar PDF', 'Limpiar'])
    card.unmount()
  })

  it('con más de cuatro valores usa el tamaño menor', () => {
    const four = render({ values: values(4) })
    expect(four.get('.answer-values').classes()).not.toContain('is-compact')
    four.unmount()
    const five = render({ values: values(5) })
    expect(five.get('.answer-values').classes()).toContain('is-compact')
    five.unmount()
  })

  it('si no convergió lo dice con el color de aviso y marca el valor como último calculado', () => {
    const card = render({ ok: false, status: 'No alcanzó la tolerancia: se detuvo tras 6 iteraciones.', values: values(1) })
    const status = card.get('.answer-status')
    expect(status.classes()).toContain('alert-warning')
    expect(status.text()).toContain('No alcanzó la tolerancia')
    expect(status.text()).toContain('El valor mostrado es el último calculado, no una solución.')
    expect(card.get('.answer-value').text()).toBe('1')
    card.unmount()
  })

  it('los botones avisan a la vista', async () => {
    const card = render()
    await card.get('.answer-actions button:first-child').trigger('click')
    await card.get('.answer-actions button:last-child').trigger('click')
    expect(card.emitted()).toMatchObject({ 'export-pdf': [[]], clear: [[]] })
    card.unmount()
  })
})

describe('franja fija', () => {
  it('aparece al salir la tarjeta por arriba y se oculta al volver', async () => {
    const card = render()
    expect(card.find('.result-bar').exists()).toBe(false)

    intersect(false, -400)
    await card.vm.$nextTick()
    expect(card.get('.result-bar').text()).toContain('Jacobi')
    expect(card.get('.bar-answer').text()).toBe('3 incógnitas')
    expect(card.get('.bar-top').text()).toBe('Ir arriba')
    expect(document.documentElement.classList.contains('has-result-bar')).toBe(true)

    intersect(true, 80)
    await card.vm.$nextTick()
    expect(card.find('.result-bar').exists()).toBe(false)
    expect(document.documentElement.classList.contains('has-result-bar')).toBe(false)
    card.unmount()
  })

  it('no aparece si la tarjeta queda por debajo de la pantalla', async () => {
    const card = render()
    intersect(false, 1200)
    await card.vm.$nextTick()
    expect(card.find('.result-bar').exists()).toBe(false)
    card.unmount()
  })

  it('con un solo valor lo muestra completo', async () => {
    const card = render({ values: [{ label: 'I ≈ T', value: '1.640533' }], noun: 'reglas' })
    intersect(false, -400)
    await card.vm.$nextTick()
    expect(card.get('.bar-answer').text()).toBe('I ≈ T = 1.640533')
    card.unmount()
  })

  it('no se monta por debajo de 1024 px', async () => {
    window.happyDOM.setViewport({ width: 1023, height: 768 })
    const card = render()
    intersect(false, -400)
    await card.vm.$nextTick()
    expect(card.find('.result-bar').exists()).toBe(false)
    card.unmount()
  })
})
