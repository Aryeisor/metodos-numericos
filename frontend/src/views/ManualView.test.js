import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'
import App from '../App.vue'
import router from '../router'
import ManualView from './ManualView.vue'

const PDF = '/manuales/manual-de-usuario.pdf'

function setWidth(width) {
  window.happyDOM.setViewport({ width, height: 900 })
}

afterEach(() => setWidth(1280))

describe('Manual de usuario', () => {
  it('la ruta /manual existe y monta la página', async () => {
    await router.push('/manual')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('manual')
    const app = mount(App, { global: { plugins: [router] } })
    expect(app.findComponent(ManualView).exists()).toBe(true)
    app.unmount()
  })

  it('el visor apunta al PDF y el botón de descarga lleva download', () => {
    setWidth(1280)
    const page = mount(ManualView)
    expect(page.get('iframe').attributes('src').split('#')[0]).toBe(PDF)
    expect(page.get('iframe').attributes('title')).toBe('Manual de usuario')
    const download = page.findAll('a').find((a) => a.text() === 'Descargar PDF')
    expect(download.attributes('href')).toBe(PDF)
    expect(download.attributes()).toHaveProperty('download')
    page.unmount()
  })

  it('la barra superior tiene el enlace accesible a /manual', async () => {
    await router.push('/manual')
    const app = mount(App, { global: { plugins: [router] } })
    const link = app.get('header a[aria-label="Manual de usuario"]')
    expect(link.attributes('href')).toBe('/manual')
    expect(link.attributes('title')).toBe('Manual de usuario')
    expect(link.classes()).toContain('is-active')
    app.unmount()
  })

  it('en celular muestra la tarjeta y no el iframe; en escritorio al revés', () => {
    setWidth(390)
    const mobile = mount(ManualView)
    expect(mobile.find('iframe').exists()).toBe(false)
    expect(mobile.text()).toContain('Abrir el manual')
    mobile.unmount()

    setWidth(1440)
    const desktop = mount(ManualView)
    expect(desktop.find('iframe').exists()).toBe(true)
    expect(desktop.text()).not.toContain('Abrir el manual')
    desktop.unmount()
  })
})
