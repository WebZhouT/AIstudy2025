const { Token } = require('../utils/token');
// 判断对应的用户信息是否存在
const userDao = require("../dao/indexdao");
function getUserState (req, res, next) {
  console.log('req', req.headers.authorization)
  if (req.headers.authorization) {
    let userinfo = Token.decrypt(req.headers.authorization);
    console.log(userinfo)
    /* 对密码解密进行返回显示用户信息 */
    // userinfo.data.userdata.password = exportPassword(userinfo.data.userdata.password);
    req.body.userdata = userinfo;
    if (userinfo.token == false) {
      // 解密失败，要求重新登录
      return res.status(401).json({ code: 401, message: '登录已过期，请重新登录' });
    } else {
      next();
    }

  } else {
    // get请求，没登录就放行
    // if (req.method != 'GET') {
    return res.status(401).json({ code: 401, message: '请重新登录' });
    // }
    next();
  }
}
module.exports = {
  getUserState: getUserState
};



