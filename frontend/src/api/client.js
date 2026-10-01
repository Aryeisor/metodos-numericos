import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

/** Catálogo de métodos registrados en el backend: [{slug, name, category, category_label}]. */
export function fetchMethods() {
  return apiClient.get('/methods/').then((res) => res.data)
}

export function fetchExamples(method) {
  return apiClient.get('/examples/', { params: { method } }).then((res) => res.data)
}

export function solveSystem(method, payload) {
  return apiClient
    .post(`/solve/${encodeURIComponent(method)}/`, payload)
    .then((res) => res.data)
}

/**
 * LaTeX de una ecuación tal como la interpreta el parser del backend (sin
 * resolver nada). Rechaza con la respuesta 400 si no es válida. `signal`
 * permite cancelar la petición si el usuario sigue escribiendo.
 */
export function previewExpression(equation, variables, { signal } = {}) {
  return apiClient
    .post('/expressions/preview', { equation, variables }, { signal })
    .then((res) => res.data.latex)
}

export default apiClient
