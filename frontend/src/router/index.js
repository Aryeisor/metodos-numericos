import { createRouter, createWebHistory } from 'vue-router'
import SolverView from '../views/SolverView.vue'
import TheoryView from '../views/TheoryView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'solver', component: SolverView },
    { path: '/teoria', name: 'theory', component: TheoryView },
  ],
})

export default router
