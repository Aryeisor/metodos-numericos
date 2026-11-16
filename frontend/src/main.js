import { createApp } from 'vue'
// Fuentes autoalojadas (subconjunto latino: cubre ñ, tildes, ¿ y ¡): la
// interfaz funciona sin conexión. Sólo los pesos que se usan.
import '@fontsource/ibm-plex-sans/latin-400.css'
import '@fontsource/ibm-plex-sans/latin-400-italic.css'
import '@fontsource/ibm-plex-sans/latin-500.css'
import '@fontsource/ibm-plex-sans/latin-600.css'
import '@fontsource/ibm-plex-sans/latin-700.css'
import '@fontsource/ibm-plex-mono/latin-400.css'
import 'katex/dist/katex.min.css'
import './assets/theme.css'
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
