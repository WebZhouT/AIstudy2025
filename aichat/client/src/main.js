import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
// 引入vant
import installVant from './plugins/vant'
const app = createApp(App)
installVant(app)// 引入vant
app.use(createPinia())
app.use(router)

app.mount('#app')
