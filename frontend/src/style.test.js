// @vitest-environment node
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

const css = readFileSync(new URL('./style.css', import.meta.url), 'utf8')
const token = (name) => css.match(new RegExp(`--${name}:\\s*([^;]+);`))?.[1].trim()

describe('escala tipográfica', () => {
  it('define los tokens nuevos', () => {
    expect(token('text-display')).toBe('1.75rem')
    expect(token('text-micro')).toBe('0.75rem')
    expect(token('font-mono')).toBeDefined()
  })

  it('el título de tarjeta ya no mide lo mismo que el cuerpo', () => {
    expect(token('text-card-title')).not.toBe(token('text-body'))
  })
})

describe('familias', () => {
  it('se resuelven a IBM Plex con su cadena de respaldo', () => {
    expect(token('font-sans')).toBe(
      "'IBM Plex Sans', 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
    )
    expect(token('font-mono')).toBe("'IBM Plex Mono', 'Consolas', 'Courier New', monospace")
  })

  it('main.js importa las fuentes autoalojadas', () => {
    const main = readFileSync(new URL('./main.js', import.meta.url), 'utf8')
    expect(main).toContain("'@fontsource/ibm-plex-sans/latin-400.css'")
    expect(main).toContain("'@fontsource/ibm-plex-mono/latin-400.css'")
  })
})
