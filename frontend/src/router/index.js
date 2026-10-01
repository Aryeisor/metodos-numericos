import { createRouter, createWebHistory } from 'vue-router'
import SolverView from '../views/SolverView.vue'
import TheoryView from '../views/TheoryView.vue'
import { hasTheory, methodRegistry, solveRouteName, theoryRouteName } from '../methods/registry'

// Antes la teoría era una sola página con anclas #metodo-<slug>; esos enlaces
// se redirigen a la página nueva del método, conservando el ancla.
const LEGACY_THEORY_ANCHOR = /^#metodo-(.+)$/

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
    {
      path: '/teoria',
      name: 'theory',
      component: TheoryView,
      beforeEnter: (to) => {
        const withTheory = methodRegistry.methods.filter(hasTheory)
        const legacy = to.hash.match(LEGACY_THEORY_ANCHOR)
        const target = (legacy && withTheory.find((m) => m.slug === legacy[1])) || withTheory[0]
        if (!target) return true
        return { name: theoryRouteName(target.slug), hash: legacy ? to.hash : '' }
      },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(to, from) {
    if (to.hash) return { el: to.hash, top: 16 }
    // Al pasar a la teoría de otro método, empezar desde arriba. Entre
    // métodos de Resolver se conserva la posición (el formulario es el mismo).
    if (to.meta.theoryMethod && to.path !== from.path) return { top: 0 }
  },
})

/**
 * Por cada método del registro: /resolver/<slug> y, si su categoría tiene
 * teoría escrita para él, /teoria/<slug>. Todas las rutas de resolución usan
 * el mismo componente, así que cambiar entre métodos de una misma categoría
 * conserva los datos que el usuario ya escribió.
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
    if (hasTheory(method)) {
      router.addRoute({
        path: `/teoria/${method.slug}`,
        name: theoryRouteName(method.slug),
        component: TheoryView,
        props: { method: method.slug },
        meta: { theoryMethod: method.slug },
      })
    }
  }
}

export default router
