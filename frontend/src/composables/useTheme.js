import { readonly, ref } from 'vue'

// Tema claro u oscuro de la interfaz, compartido por toda la app (estado de
// módulo). El primer valor lo pone el script en línea de index.html antes de
// pintar la página; aquí sólo se lee. Sin elección guardada se sigue la
// preferencia del sistema operativo, también si cambia con la app abierta.
export const THEME_STORAGE_KEY = 'theme'
const TRANSITION_MS = 200

const root = document.documentElement
const systemDark = window.matchMedia('(prefers-color-scheme: dark)')

function storedTheme() {
  try {
    const value = localStorage.getItem(THEME_STORAGE_KEY)
    return value === 'light' || value === 'dark' ? value : null
  } catch {
    return null
  }
}

const systemTheme = () => (systemDark.matches ? 'dark' : 'light')

const initial = root.dataset.theme
const theme = ref(initial === 'dark' || initial === 'light' ? initial : storedTheme() ?? systemTheme())
root.dataset.theme = theme.value

let transitionTimer = null

function applyTheme(next) {
  if (next === theme.value) return
  // La transición de colores sólo durante el cambio (ver theme.css).
  root.classList.add('theme-transition')
  clearTimeout(transitionTimer)
  transitionTimer = setTimeout(() => root.classList.remove('theme-transition'), TRANSITION_MS)
  root.dataset.theme = next
  theme.value = next
}

systemDark.addEventListener('change', () => {
  if (!storedTheme()) applyTheme(systemTheme())
})

function toggleTheme() {
  const next = theme.value === 'dark' ? 'light' : 'dark'
  try {
    localStorage.setItem(THEME_STORAGE_KEY, next)
  } catch {
    // Almacenamiento bloqueado: el cambio vale para esta visita.
  }
  applyTheme(next)
}

export function useTheme() {
  return { theme: readonly(theme), toggleTheme }
}
