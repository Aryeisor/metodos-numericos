// @vitest-environment node
import { describe, expect, it } from 'vitest'
import { contrast, lightTokens, readBlock, readTheme } from '../../scripts/verificar-contraste.mjs'

const css = readTheme()
const light = lightTokens(css)
const dark = readBlock(css, "[data-theme='dark'] {")

describe('tema claro con más contraste', () => {
  it('tiene los colores de texto nuevos', () => {
    expect(light).toMatchObject({
      'color-ink': '#111827',
      'color-ink-muted': '#334155',
      'color-accent': '#0b4a5a',
      'color-accent-hover': '#083a46',
      'color-value-old': '#1e40af',
      'color-value-new': '#116029',
      'color-success': '#116029',
      'color-tolerance': '#116029',
      'color-warning': '#7c3609',
      'color-danger': '#991b1b',
    })
  })

  it('no cambia los fondos claros', () => {
    expect(light).toMatchObject({
      'color-page': '#e6ebf1',
      'color-surface': '#f8fafc',
      'color-input': '#ffffff',
      'color-sunken': '#e8edf3',
      'color-stripe': '#f0f3f7',
    })
  })

  it('deja intacto el tema oscuro', () => {
    expect(dark).toMatchObject({
      'color-page': '#0f172a',
      'color-surface': '#1c2638',
      'color-sunken': '#263247',
      'color-stripe': '#212c3f',
      'color-ink': '#e2e8f0',
      'color-ink-muted': '#a5b1c2',
      'color-accent': '#5ec4d6',
      'color-accent-hover': '#86d5e2',
      'color-success': '#6ee09a',
      'color-warning': '#f2c46b',
      'color-danger': '#f59a9a',
      'color-value-old': '#93d4ff',
      'color-value-new': '#8ef0b4',
      'color-tolerance': '#6ee09a',
    })
  })

  it('mantiene los selectores de KaTeX con los literales de latexFormulas.js', () => {
    expect(css).toContain(".katex [style*='color:#2563eb'] {\n  color: var(--color-value-old) !important;")
    expect(css).toContain(".katex [style*='color:#15803d'] {\n  color: var(--color-value-new) !important;")
    expect(css).toContain(".katex [style*='color:#b91c1c'] {\n  color: var(--color-danger) !important;")
  })

  it.each([
    ['color-ink-muted', 'color-page'],
    ['color-value-old', 'color-sunken'],
    ['color-value-old', 'color-page'],
    ['color-value-new', 'color-sunken'],
    ['color-value-new', 'color-page'],
    ['color-danger', 'color-surface'],
  ])('%s sobre %s da al menos 6:1', (text, bg) => {
    expect(contrast(light[text], light[bg])).toBeGreaterThanOrEqual(6)
  })
})
