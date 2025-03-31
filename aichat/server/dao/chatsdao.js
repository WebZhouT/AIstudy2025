// 数据库操作 - chat
// 对应表名：chat

const pool = require("../db/pool"); // 导入数据库连接池对象
// 定义五个函数

// 查找所有聊天表
async function getAllChats (page, limit) {
  try {
    let sql = 'SELECT * FROM chat';
    // 倒序排列
    // sql += ' ORDER BY id DESC';
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
    const [resultsTotal] = await pool.query('select count(*) as count from chat'); // 获取聊天表总数，用于分页
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
// 增加一个聊天表记录
async function insertChat (chat) {
  try {

    const sql = "insert into chat (`sendid`,`role`,`comments`,`type`,`source`) values (?, ?, ?, ?, ?)";
    let result = await pool.query(sql, [chat.sendid, chat.role, chat.comments, chat.type, chat.source | '']);
    return result;
  } catch (e) {
    throw e; // 抛出错误
  }
}
// 获取指定id的一个聊天表记录
async function getChatById (id) {
  try {
    // 使用参数化查询来防止SQL注入
    const result = await pool.query('select * from chat where sendid = ?', [id]);

    // 检查查询结果是否存在
    if (result.length === 0) {
      return null; // 或者抛出一个错误，取决于您的错误处理策略
    }

    // 返回查询到的用户信息
    return result;
  } catch (e) {
    // 打印错误信息
    console.error(e);
    // 抛出错误，让调用者处理
    throw e;
  }
}

// 删除一个聊天表记录
async function deleteChatById (id) {
  try {
    const deleteChat = await pool.query('delete from chat WHERE id = ?', [id]);
    return deleteChat
  } catch (e) {
    throw e; // 抛出错误
  }
}
// 删除一个聊天表记录
async function deleteChatNameById (id) {
  try {
    const deleteChat = await pool.query('delete from chat WHERE sendid = ?', [id]);
    return deleteChat
  } catch (e) {
    throw e; // 抛出错误
  }
}

// 更新一个聊天表记录
async function updateChat (id, chat) {
  try {
    // 初始化一个空数组来保存需要更新的字段和值
    let updates = [];
    const params = []; // 参数数组，用于参数化查询
    // 手动指定要更新的字段和检查用户对象的属性
    const fieldsToUpdate = ["sendid", "role", "comments", "type"];
    fieldsToUpdate.forEach(field => {
      if (chat[field] !== undefined && chat[field] !== null) {
        // 如果 chat 对象包含该字段并且值不是 undefined 或 null，则添加到更新列表
        updates.push(field + "= ?");
        params.push(chat[field]);
      }
    });
    // 构造 SET 子句
    let setClause = '';
    if (updates.length > 0) {
      setClause = 'SET ' + updates.join(', ');
    }

    // 构造 SQL 更新语句
    let sql = 'update chat ' + setClause + ' WHERE id = ?';

    // 执行 SQL 更新语句，将params数组和id添加到查询参数中
    let chatResult = await pool.query(sql, [...params, id]);
    return chatResult


  } catch (e) {
    // 打印错误信息
    console.error(e);
    // 抛出错误，让调用者处理
    throw e;
  }
}
// 导出所有CRUD操作函数
module.exports = {
  getAllChats,
  insertChat,
  getChatById,
  deleteChatById,
  updateChat,
  deleteChatNameById
};