
// 数据库操作 - user
// 对应表名：user

const pool = require("../db/pool"); // 导入数据库连接池对象
// 定义五个函数

// 查找所有用户表
async function getAllUsers (page, limit) {
  try {
    let sql = 'SELECT * FROM users';
    let values = [];

    // 如果提供了分页参数，则添加LIMIT和OFFSET到查询语句
    if (page && limit) {
      const offset = (page - 1) * limit;
      sql += ' LIMIT ? OFFSET ?';
      values = [limit, offset];
    }

    // 执行查询
    const [results] = await pool.query(sql, values);

    // 如果进行了分页，可以在这里添加获取总记录数的逻辑并返回分页结果
    // 如果没有分页，直接返回所有结果
    const [resultsTotal] = await pool.query('SELECT COUNT(*) AS count FROM users'); // 获取用户表总数，用于分页
    // 检查结果是否存在并获取总数
    const total = resultsTotal.length > 0 ? resultsTotal[0].count : 0;
    // 这里可以根据需要返回结果和分页信息
    return {
      data: results,
      page: page || 1, // 如果没有提供page参数，默认为1
      limit: limit || total, // 如果没有提供limit参数，默认为全部条数
      total: total // 假设这里可以获取到总记录数
    };
  } catch (e) {
    throw e;
  }
}
// 增加一个用户表记录
async function insertUser (user) {
  try {
    const columns = ["username", "password", "email", "head"];
    // 构造列名字符串
    const columnsString = columns.join(', ');
    // 构造值的占位符字符串，例如："('?', '?', '?', '?', '?')"
    const placeholders = columns.map(() => '?').join(', ');
    const values = [user.username, user.password, user.email, user.head];
    const sql = "INSERT INTO user (" + columnsString + ") VALUES (" + placeholders + ")";
    await pool.query(sql, values);
  } catch (e) {
    throw e; // 抛出错误
  }
}
// 获取指定id的一个用户表记录
async function getUserById (id) {
  try {
    // 使用参数化查询来防止SQL注入
    const result = await pool.query('SELECT * FROM ?? WHERE id = ?', ['users', id]);

    // 检查查询结果是否存在
    if (result.length === 0) {
      return null; // 或者抛出一个错误，取决于您的错误处理策略
    }

    // 返回查询到的用户信息
    return result[0];
  } catch (e) {
    // 打印错误信息
    console.error(e);
    // 抛出错误，让调用者处理
    throw e;
  }
}

// 删除一个用户表记录
async function deleteUserById (id) {
  try {
    const deleteUser = await pool.query('DELETE FROM ?? WHERE id = ?', ['users', id]);
    return deleteUser
  } catch (e) {
    throw e; // 抛出错误
  }
}

// 更新一个用户表记录
async function updateUser (id, user) {
  try {
    // 初始化一个空数组来保存需要更新的字段和值
    let updates = [];
    const params = []; // 参数数组，用于参数化查询
    // 手动指定要更新的字段和检查用户对象的属性
    const fieldsToUpdate = ["username", "password", "email", "head"];
    fieldsToUpdate.forEach(field => {
      if (user[field] !== undefined && user[field] !== null) {
        // 如果 user 对象包含该字段并且值不是 undefined 或 null，则添加到更新列表
        updates.push(field + "= ?");
        params.push(user[field]);
      }
    });
    // 构造 SET 子句
    let setClause = '';
    if (updates.length > 0) {
      setClause = 'SET ' + updates.join(', ');
    }

    // 构造 SQL 更新语句
    let sql = 'UPDATE user ' + setClause + ' WHERE id = ?';

    // 执行 SQL 更新语句，将params数组和id添加到查询参数中
    let userResult = await pool.query(sql, [...params, id]);
    return userResult


  } catch (e) {
    // 打印错误信息
    console.error(e);
    // 抛出错误，让调用者处理
    throw e;
  }
}
// 导出所有CRUD操作函数
module.exports = {
  getAllUsers,
  insertUser,
  getUserById,
  deleteUserById,
  updateUser
  // 如果有其他函数，也可以在这里添加
};