import axios from 'axios'
const http = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json;charset=UTF-8',
    // 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
  },
  data: {},
  timeout: 5000,
  responseType: 'json',
  // withCredentials: true,//跨域携带cookie
})

// 添加一个请求拦截器
http.interceptors.request.use((config) => {
  return config
}, (error) => {
  // Do something with request error
  return Promise.reject(error)
})

// 添加一个响应拦截器
http.interceptors.response.use((response) => {
  console.log(response.data);
  // if (response.data || response.data.code == '0') {
  return response.data
  // if (response.data) {

  // } else {
  //   return Promise.reject(response.data)
  // }
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
  return Promise.reject(error)
})

export default http