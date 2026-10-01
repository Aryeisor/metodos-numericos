import { createApp } from 'vue'
import 'katex/dist/katex.min.css'
import './style.css'
import App from './App.vue'
import router, { addMethodRoutes } from './router'
import { loadMethodRegistry, methodRegistry } from './methods/registry'

// Las rutas de resolución salen del catálogo de métodos, así que se carga
// antes de la primera navegación. Si falla, la app arranca igual y la vista
// Resolver muestra el error.
await loadMethodRegistry()
addMethodRoutes(methodRegistry.methods)

createApp(App).use(router).mount('#app')
