import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sort',
      name: 'sort',
      component: () => import('../views/sort.vue'),
    },
    {
      path: '/user',
      name: 'user',
      component: () => import('../views/user.vue'),
    },
    {
      path: '/detail/:id',
      name: 'detail',
      component: () => import('../views/detail.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/login.vue'),
    },
  ],
})

export default router
