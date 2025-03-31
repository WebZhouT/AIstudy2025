
/**
 * @description 所有人可使用的参数配置列表
 * @params hideMenu: 是否隐藏当前路由结点不在导航中展示
 * @params alwayShow: 只有一个子路由时是否总是展示菜单，默认false
 */
import Layout from '@/layout/index.vue'
import { reactive } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import store from '@/store'
import NProgress from '@/utils/system/nprogress'
import { changeTitle } from '@/utils/system/title'
import { createNameComponent } from './createNode'
NProgress.configure({ showSpinner: false })


/** 
 * @name 初始化必须要的路由
 * @description 使用reactive属性使得modules可以在路由菜单里面实时响应，搞定菜单回显的问题
 * @detail 针对modules的任何修改，均会同步至菜单级别，记住，是针对变量名为：moduels的修改
 **/

const routes = [
  // {
  //   path: '/',
  //   hideMenu: true,
  //   redirect: '/system'
  // },
  {
    path: '/',
    component: Layout,
    redirect: '/chat',
    meta: { title: 'dashboard', icon: 'sfont system-home' },
    children: [
      {
        path: 'dashboard',
        component: createNameComponent(() => import('@/views/main/dashboard/index.vue')),
        meta: { title: '首页', icon: 'sfont system-home', hideClose: true }
      },

    ]
  },
  {
    path: '/system',
    component: Layout,
    redirect: '/404',
    hideMenu: true,
    meta: { title: '系统目录' },
    children: [
      {
        path: '/404',
        component: createNameComponent(() => import('@/views/system/404.vue')),
        meta: { title: '404', hideTabs: true }
      },
      {
        path: '/401',
        component: createNameComponent(() => import('@/views/system/401.vue')),
        meta: { title: '401', hideTabs: true }
      },
      {
        path: '/redirect/:path(.*)',
        component: createNameComponent(() => import('@/views/system/redirect.vue')),
        meta: { title: '重定向页面', hideTabs: true }
      }
    ]
  },
  // {
  //   path: '/user',
  //   component: Layout,
  //   redirect: '/user/list',
  //   meta: { title: '用户管理', icon: 'sfont system-home' },
  //   children: [
  //     {
  //       path: 'list',
  //       component: createNameComponent(() => import('@/views/main/user/index.vue')),
  //       meta: { title: '用户管理列表', icon: 'sfont system-home' }
  //     },
  //     {
  //       path: 'add',
  //       component: createNameComponent(() => import('@/views/main/user/userEdit.vue')),
  //       meta: { title: '用户管理添加', icon: 'sfont system-home' }
  //     },
  //   ]
  // }, 
  {
    path: '/chat',
    component: Layout,
    redirect: '/chat/chat',
    meta: { title: '用户管理', icon: 'sfont system-home' },
    children: [
      {
        path: 'chat',
        component: createNameComponent(() => import('@/views/main/chat/index.vue')),
        meta: { title: '在线聊天系统', icon: 'sfont system-home' }
      },
    ]
  },
  // {
  //   path: '/sort',
  //   component: Layout,
  //   redirect: '/sort/list',
  //   meta: { title: '分类管理', icon: 'sfont system-home' },
  //   children: [
  //     {
  //       path: 'list',
  //       component: createNameComponent(() => import('@/views/main/sortlist/index.vue')),
  //       meta: { title: '分类管理列表', icon: 'sfont system-home' }
  //     },
  //     {
  //       path: 'add',
  //       component: createNameComponent(() => import('@/views/main/sortlist/userEdit.vue')),
  //       meta: { title: '分类管理添加', icon: 'sfont system-home' }
  //     },
  //   ]
  // },
  {
    path: "/login",
    name: "Login",
    hideMenu: true,
    meta: {
      title: '登录'
    },
    component: () => import("@/views/system/login.vue")
  },

];
const router = createRouter({
  history: createWebHashHistory(),
  routes: routes
})
// 路由拦截
router.beforeEach((to, from, next) => {
  const role = localStorage.getItem('admintoken');
  if (!role && to.path !== '/login') {
    next('/login');
  } else if (role && to.path == '/login') {
    // 如果用户登录了，但是访问的是登录页面，就跳转回首页
    next('/');
  } else {

    next();
  }
});


export default router
