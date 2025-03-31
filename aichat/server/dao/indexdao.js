const pool = require("../db/pool"); // 导入数据库连接池对象
/* 密码加密和解密方法 */
const { genPassword,
  exportPassword } = require('./../utils/cryp')
// 根据用户名获取用户
async function getUserByUsername (username) {
  const [rows, fields] = await pool.execute('SELECT * FROM users WHERE username = ?', [username]);
  return rows.length ? rows[0] : null;
}
// 增加一个用户表记录
async function addUser (user) {
  try {
    const columns = ["username", "password", "email", "mobile", "intro", "head"];
    // 构造列名字符串
    const columnsString = columns.join(', ');
    const placeholders = columns.map(() => '?').join(', ');
    const values = [user.username, genPassword(user.password), user.email, user.mobile, user.intro, user.head];
    const sql = "INSERT INTO user (" + columnsString + ") VALUES (" + placeholders + ")";
    await pool.query(sql, values);
  } catch (e) {
    throw e; // 抛出错误
  }
}

// 导出所有CRUD操作函数
module.exports = {
  // 如果有其他函数，也可以在这里添加
  getUserByUsername,
  addUser
};