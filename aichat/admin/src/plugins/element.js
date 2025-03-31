import ElementPlus from 'element-plus'
// import { createI18n } from 'vue-i18n'
// import 'element-plus/lib/theme-chalk/index.css'
import localeZH from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
/* 引入自定义主题 */
import './../theme/index.css'
export default (app) => {
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }
  /* 全局注册吐司弹框 */
  app.config.globalProperties.$message = ElMessage
  app.use(ElementPlus, { locale: localeZH })
  // app.use(i18n)
}
