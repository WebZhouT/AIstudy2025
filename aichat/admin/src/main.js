
import { createApp } from 'vue'
import installElementPlus from './plugins/element'
// import ElementPlus from 'element-plus'
// import 'element-plus/theme-chalk/display.css' // 引入基于断点的隐藏类
// import 'element-plus/dist/index.css'
import 'normalize.css' // css初始化
import './assets/style/common.scss' // 公共css
import './theme/modules/chinese/index.scss'
import App from './App.vue'
import store from './store'
import router from './router'
import { createPinia } from 'pinia'
if (import.meta.env.MODE !== 'development') { // 非开发环境调用
}

const app = createApp(App)
installElementPlus(app)
app
  .use(store)
  .use(createPinia())
  .use(router)
  .mount('#app')