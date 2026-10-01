// Nombres de las rutas generadas por método. Módulo sin dependencias para que
// lo puedan usar tanto el registro como el contenido de cada categoría.

export function solveRouteName(slug) {
  return `solve-${slug}`
}

export function theoryRouteName(slug) {
  return `theory-${slug}`
}
