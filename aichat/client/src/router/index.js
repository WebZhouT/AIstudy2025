import { createRouter, createWebHistory,createWebHashHistory } from 'vue-router'

const router = createRouter({
  // import.meta.env.BASE_URL
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home',
    }, {
      path: '/home',
      name: 'home',
      component: () => import('../views/home.vue')
    }, {
      path: '/user',
      name: 'user',
      component: () => import('../views/user.vue')
    }, {
      path: '/list',
      name: 'list',
      component: () => import('../views/list.vue')
    },
    {
      path: '/account',
      name: 'account',
      component: () => import('../views/account.vue'),
      redirect: '/account/login',
      children: [
        {
          path: '/login',
          name: 'login',
          component: () => import('../views/login.vue')
        }, {
          path: '/register',
          name: 'register',
          component: () => import('../views/register.vue')
        }
      ]
    }
  ],
})
/* 路由拦截跳转登录页面 */
router.beforeEach((to, from, next) => {
  var localdata = localStorage.getItem('user');
  if (to.meta.requireAuth) { // 判断该路由是否需要登录权限
    console.log(localdata)
    if (localdata != null) { //判断本地存储数据是否存在
      next();
    } else {
      next({
        path: '/user/login'
      })
    }
  } else {
    next();
  }
})
export default router
