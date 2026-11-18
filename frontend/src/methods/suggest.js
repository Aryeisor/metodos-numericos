// Sugerencias para una dirección que no existe: a partir del último segmento
// del camino, qué métodos buscaba probablemente el usuario.
import { fold } from '../utils/text'

const SECTIONS = { resolver: 'resolver', teoria: 'teoria' }
const MAX_SUGGESTIONS = 4

/** Minúsculas, sin tildes, guiones y guiones bajos como espacios. */
export const normalize = (text) => fold(text).replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim()

/** Distancia de Levenshtein (inserciones, borrados y sustituciones). */
export function editDistance(a, b) {
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j)
  for (let i = 1; i <= a.length; i++) {
    const row = [i]
    for (let j = 1; j <= b.length; j++) {
      row[j] = Math.min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1))
    }
    prev = row
  }
  return prev[b.length]
}

/**
 * Separa el camino (segmentos ya decodificados) en sección reconocida y el
 * texto que se compara: el último segmento después de la sección.
 */
export function parseMissingPath(segments) {
  const parts = segments.filter(Boolean)
  const section = SECTIONS[fold(parts[0] ?? '')] ?? null
  const rest = section ? parts.slice(1) : parts
  const raw = rest.at(-1) ?? ''
  return { section, raw, text: normalize(raw) }
}

/**
 * Métodos que probablemente buscaba quien escribió `text`, ya normalizado.
 * (a) error de escritura: hasta 2 ediciones contra el slug o el nombre (1 si
 *     el texto es corto, para que «abc» no se parezca a todo); van primero,
 *     el más cercano antes.
 * (b) palabra del método: alguna palabra del texto coincide (o empieza) con
 *     una de sus keywords, de su nombre o de su categoría.
 * Sin repetidos y como mucho cuatro; sin nada que se reconozca, lista vacía.
 */
export function suggestMethods(text, methods) {
  if (!/[a-z0-9]/.test(text)) return []
  const maxEdits = Math.min(2, Math.floor(text.length / 3))

  const typos = methods
    .map((method) => ({
      method,
      distance: Math.min(editDistance(text, normalize(method.slug)), editDistance(text, normalize(method.name))),
    }))
    .filter((m) => m.distance <= maxEdits)
    .sort((a, b) => a.distance - b.distance)
    .map((m) => m.method)

  // Palabras de menos de 3 letras («de», «no») coincidirían con medio catálogo.
  const tokens = text.split(' ').filter((t) => t.length >= 3)
  const related = methods
    .map((method) => {
      const words = normalize([method.name, method.categoryLabel, ...method.keywords].join(' ')).split(' ')
      const hits = tokens.filter((t) => words.some((w) => w === t || (t.length >= 4 && w.startsWith(t)))).length
      return { method, hits }
    })
    .filter((m) => m.hits > 0)
    .sort((a, b) => b.hits - a.hits) // estable: a igual coincidencia, orden del registro
    .map((m) => m.method)

  return [...new Set([...typos, ...related])].slice(0, MAX_SUGGESTIONS)
}
