import { createRouter, createWebHistory } from 'vue-router'
import SolverView from '../views/SolverView.vue'
import TheoryView from '../views/TheoryView.vue'
import { methodRegistry, solveRouteName } from '../methods/registry'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      // Sin método en la URL se abre el primero del registro. Si el catálogo
      // no pudo cargarse, SolverView muestra el error.
      path: '/',
      name: 'home',
      component: SolverView,
      beforeEnter: () => {
        const first = methodRegistry.methods[0]
        return first ? { name: solveRouteName(first.slug) } : true
      },
    },
    { path: '/teoria', name: 'theory', component: TheoryView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, top: 16 }
  },
})

/**
 * Una ruta /resolver/<slug> por cada método del registro. Todas usan el mismo
 * componente, así que cambiar entre métodos de una misma categoría conserva
 * los datos que el usuario ya escribió.
 */
export function addMethodRoutes(methods) {
  for (const method of methods) {
    router.addRoute({
      path: `/resolver/${method.slug}`,
      name: solveRouteName(method.slug),
      component: SolverView,
      props: { method: method.slug },
      meta: { method: method.slug },
    })
  }
}

export default router
