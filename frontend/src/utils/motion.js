/** 'smooth', o 'auto' (salto sin animación) si el sistema pide menos movimiento. */
export const scrollBehavior = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
