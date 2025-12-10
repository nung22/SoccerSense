import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
const GoalsView = () => import('../views/GoalsView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/goals',
      name: 'goals',
      component: GoalsView
    },
  ],
})

export default router
