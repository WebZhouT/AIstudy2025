
var express = require('express');
var router = express.Router();
var chatDao = require("../dao/chatsdao");

// 获取聊天表列表
router.get('/', async function (req, res, next) {
  try {
    const page = parseInt(req.query.page) || undefined; // 如果没有提供page参数，则为undefined
    const limit = parseInt(req.query.limit) || undefined; // 如果没有提供limit参数，则为undefined
    const users = await chatDao.getAllChats(page, limit);
    res.status(200).json({ "code": "000", message: "获取成功", data: users });
  } catch (e) {
    res.status(500).send({ "code": "400", "message": "获取聊天表列表失败" + e.message, data: null });
  }
});

// 添加聊天表
router.post('/', async function (req, res, next) {
  try {
    const chat = req.body;
    const chatData = await chatDao.insertChat(chat);
    res.status(201).json({ "code": "000", message: "添加聊天表成功", data: chatData });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "添加聊天表失败" + e, error: e.message });
  }
});

// 获取单个聊天表的详细信息
router.get('/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const chat = await chatDao.getChatById(id);
    if (!chat) {
      return res.status(404).json({ "code": "400", message: "未找到聊天表" });
    }
    res.status(200).json({ "code": "000", message: "获取成功聊天表成功", data: chat[0] });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "获取聊天表详细信息失败" + e.message, data: null });
  }
});

// 更新聊天表
router.put('/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const updatedUser = req.body;
    const result = await chatDao.updateChat(id, updatedUser);
    if (result.affectedRows === 0) {
      return res.status(500).json({ "code": "400", message: "更新聊天表失败，未找到对应记录" });
    }
    res.status(200).json({ "code": "000", message: "更新聊天表成功", data: updatedUser });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "更新聊天表失败" + e.message, data: null });
  }
});

// 删除聊天表
router.delete('/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const result = await chatDao.deleteChatById(id);
    if (result.affectedRows === 0) {
      return res.status(500).json({ "code": "400", message: "删除聊天表失败，未找到对应记录" });
    }
    res.status(200).json({ "code": "000", message: "删除聊天表成功" });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "删除聊天表失败" + e.message, data: null });
  }
});
// 删除指定用户的聊天表
router.delete('/name/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const result = await chatDao.deleteChatNameById(id);
    if (result.affectedRows === 0) {
      return res.status(500).json({ "code": "400", message: "删除聊天表失败，未找到对应记录" });
    }
    res.status(200).json({ "code": "000", message: "删除聊天表成功" });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "删除聊天表失败" + e.message, data: null });
  }
});

// 导出router模块
module.exports = router;