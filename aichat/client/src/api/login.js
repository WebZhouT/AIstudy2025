/* 登录 */
import http from './index.js'
/* 获取图形验证码 */
export const getImgCode = (data) => {
  return http({
    url: '/h5/register/get_img_code',
    method: 'get',
    data: data
  })
}
/* 发送验证码 */
export const getSendCode = (data) => {
  return http({
    url: '/h5/register/send_code',
    method: 'post',
    data: data
  })
}
/* 注册/登录 */
export const getRegister = (data) => {
  return http({
    url: '/h5/register/register',
    method: 'post',
    data: data
  })
}
/* 更新用户openid */
export const getUpdate_open_id = (data) => {
  return http({
    url: '/h5/user/update_open_id',
    method: 'post',
    data: data
  })
}