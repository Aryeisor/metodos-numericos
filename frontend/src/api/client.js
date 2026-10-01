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

export default apiClient
