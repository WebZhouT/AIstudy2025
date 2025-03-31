// 引入jsonwebtoken包
const jwt = require('jsonwebtoken');
// 设定一个密钥，用来加密和解密token
const tokenKey = 'XfZEpWEn?ARD7rHBN';
// 设定默认Token过期时间，单位s
const TOKEN_EXPIRE_SENCOND = 3600 * 1000 + 's';
// 定义一个对象
const Token = {
  /**
   * Token加密方法
   * @param data 需要加密在Token中的数据
   * @returns {*} 返回一个Token
   */
  encrypt: function (data) {
    return jwt.sign({ userdata: data }, tokenKey, { expiresIn: TOKEN_EXPIRE_SENCOND })
  },
  /**
   * Token解密方法
   * @param token 加密之后的Token
   * @returns 返回对象{{token: boolean（true表示Token合法，false则不合法）, data: *（解密出来的数据或错误信息）}}
   */
  decrypt: function (token) {
    try {
      let data = jwt.verify(token, tokenKey);
      return {
        token: true,
        data: data
      };
    } catch (e) {
      return {
        token: false,
        data: e
      }
    }
  }
};

// 导出对象，方便其他模块调用
module.exports = {
  Token
}