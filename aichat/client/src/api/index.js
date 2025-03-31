import axios from 'axios'
import { showLoadingToast, showConfirmDialog, showToast, closeToast, showDialog } from 'vant';
// import { ElMessage } from 'element-plus'
const http = axios.create({
  baseURL: '/api',
  // baseURL: '',
  headers: {
    // 'Content-Type': 'application/json;charset=UTF-8',
    // 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    /* 设定jwt请求头 */
    'authorization': localStorage.getItem('userdata') == null ? '' : JSON.parse(localStorage.getItem('userdata')).token
  },
  data: {},
  crossdomain: true,/* 跨域设定 */
  timeout: 5000,
  responseType: 'json',
  withCredentials: false,//表示跨域请求时是否需要使用凭证cookie
})

// 添加一个请求拦截器
http.interceptors.request.use((config) => {
  config.headers.authorization = localStorage.getItem('userdata') ? JSON.parse(localStorage.getItem('userdata')).token : '';
  // 生成一个随机数作为查询参数
  config.params = {
    ...config.params,
    timestamp: Date.now() // 或者使用 Math.random()
  };
  /* 显示加载状态 */
  showLoadingToast({
    duration: 0,
    forbidClick: true,
    message: '加载中...',
  });
  return config;
}, (error) => {
  console.log(error)
  showToast(error.msg)
  // Do something with request error
  return Promise.reject(error)
})
// 添加一个响应拦截器
http.interceptors.response.use((response) => {
  if (response.data.code == 2000
  ) {
    /* 关闭加载状态 */
    closeToast()
    return response.data
  } else {
    if (response.data.code == 3001) {
      showToast({
        'message': response.data.message,
        "onClose": function () {
          window.location.href = '/login'
        }
      })
    } else {
      if (response.data != null) {
        showToast(response.data.msg)
      }
      return Promise.reject(response.data)
    }
    /* 关闭加载状态 */
    closeToast()
    return Promise.reject(response.data)
  }

}, (error) => {
  // Do something with response error
  if (error.response) {
    switch (error.response.status) {
      case 400:
        error.message = '请求错误'
        break

      case 401:
        error.message = '未授权，请登录'
        break

      case 403:
        error.message = '拒绝访问'
        break

      case 404:
        error.message = `请求地址出错: ${error.response.config.url}`
        break

      case 408:
        error.message = '请求超时'
        break

      case 500:
        error.message = '服务器内部错误'
        break

      case 501:
        error.message = '服务未实现'
        break

      case 502:
        error.message = '网关错误'
        break

      case 503:
        error.message = '服务不可用'
        break

      case 504:
        error.message = '网关超时'
        break

      case 505:
        error.message = 'HTTP版本不受支持'
        break
      default:
        error.message = `连接出错(${error.response.status})!`
    }
  } else {
    error.message = '网络异常,连接服务器失败!'
  }
  console.log(error.response)
  if (error.response.status == 401) {
    showToast({
      'message': error.message,
      "onClose": function () {
        window.location.href = '/#/login'
      }
    })
  } else {
    showToast(error.message)
  }

  return Promise.reject(error)
})

export default http