import { createApp } from 'vue';
import { PasswordInput, NumberKeyboard } from 'vant';
import { Icon } from 'vant';
/* 引入自定义主题 */
import './../theme/index.css'
// Toast
import 'vant/es/toast/style';
export default (app) => {
  /* 密码输入框 */
  app.use(PasswordInput);
  app.use(NumberKeyboard);
  app.use(Icon);
}
