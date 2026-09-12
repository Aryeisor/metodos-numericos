import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export function fetchExamples() {
  return apiClient.get('/examples/').then((res) => res.data)
}

export function solveSystem(method, payload) {
  const path = method === 'gauss-seidel' ? '/solve/gauss-seidel/' : '/solve/jacobi/'
  return apiClient.post(path, payload).then((res) => res.data)
}

export default apiClient
