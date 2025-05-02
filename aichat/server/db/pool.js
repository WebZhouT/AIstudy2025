// 导入mysql2模块
const mysql = require('mysql2');
// 创建数据库连接池
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  database: 'aichat',
  password: '123456',
  connectionLimit: 10,
  charset: 'utf8mb4', // 关键配置
});
// const pool = mysql.createPool({
//   host: '47.121.179.65',
//   user: '0218case2',
//   database: '0218case2',
//   password: 'MZRb8aWHbPdaKZsh',
//   connectionLimit: 10
// });
// 获得连接池的promise对象
const promisePool = pool.promise();
module.exports = promisePool;