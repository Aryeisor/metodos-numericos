// Comprueba el contraste de los colores de texto del tema claro (WCAG 2.x).
// Uso: node scripts/verificar-contraste.mjs   (desde frontend/)
// Sale con código 1 si algún par queda por debajo de 4.5:1; avisa si < 7:1.
import { readFileSync } from 'node:fs'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const THEME_PATH = fileURLToPath(new URL('../src/assets/theme.css', import.meta.url))

export const TEXT_TOKENS = [
  'color-ink',
  'color-ink-muted',
  'color-accent',
  'color-accent-hover',
  'color-value-old',
  'color-value-new',
  'color-success',
  'color-warning',
  'color-danger',
]
export const BACKGROUND_TOKENS = ['color-surface', 'color-stripe', 'color-sunken', 'color-page']

const MIN = 4.5
const GOOD = 7

/** Tokens `--nombre: #hex` del bloque que abre con `selector {`. */
export function readBlock(css, selector) {
  const start = css.indexOf(selector)
  if (start < 0) throw new Error(`No se encontró el bloque ${selector}`)
  const body = css.slice(css.indexOf('{', start) + 1, css.indexOf('\n}', start))
  return Object.fromEntries([...body.matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})\b/g)].map((m) => [m[1], m[2].toLowerCase()]))
}

// El CSS puede venir con CRLF desde Git en Windows.
export function readTheme() {
  return readFileSync(THEME_PATH, 'utf8').replace(/\r\n/g, '\n')
}

export function lightTokens(css = readTheme()) {
  return readBlock(css, ":root,\n[data-theme='light']")
}

function luminance(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

export function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}

function main() {
  const tokens = lightTokens()
  let failed = false
  const rows = TEXT_TOKENS.map((text) => {
    const row = { token: `--${text}`, valor: tokens[text] }
    let worst = Infinity
    for (const bg of BACKGROUND_TOKENS) {
      const ratio = contrast(tokens[text], tokens[bg])
      worst = Math.min(worst, ratio)
      row[bg.replace('color-', '')] = ratio.toFixed(2)
    }
    row['peor caso'] = worst.toFixed(2)
    row.estado = worst < MIN ? 'FALLA (< 4.5)' : worst < GOOD ? 'aviso (< 7)' : 'ok'
    if (worst < MIN) failed = true
    return row
  })
  console.log('Contraste de texto del tema claro (WCAG):')
  console.table(rows)
  if (failed) {
    console.error(`Hay colores de texto por debajo de ${MIN}:1.`)
    process.exit(1)
  }
  console.log(`Todos los pares ≥ ${MIN}:1.`)
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main()
