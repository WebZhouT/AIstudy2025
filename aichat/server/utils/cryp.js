const crypto = require('crypto');
const { Buffer } = require('buffer');
// ase-128-cbc 加密算法要求key和iv长度都为16
// 密匙
const SECRET_KEY = 'Wn3L7EDzjqWjcaY2';
const key = Buffer.from(SECRET_KEY.slice(0, 16), 'utf8');
const iv = Buffer.from(SECRET_KEY.slice(0, 16), 'utf8');
// 加密函数
function genPassword (password) {
  let sign = '';
  const cipher = crypto.createCipheriv('aes-128-cbc', key, iv);
  sign += cipher.update(password, 'utf8', 'base64');
  // 原先hex的改成base64 使java适用
  sign += cipher.final('base64');
  return sign;
}
// 解密函数
function exportPassword (password) {
  let src = '';
  const cipher = crypto.createDecipheriv('aes-128-cbc', key, iv);
  src += cipher.update(password, 'base64', 'utf8');
  // 原先hex的改成base64 使java适用
  src += cipher.final('utf8');
  return src;
}
module.exports = {
  genPassword,
  exportPassword
}