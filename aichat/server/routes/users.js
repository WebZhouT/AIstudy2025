
const express = require('express');
const router = express.Router();
const userDao = require("../dao/usersdao");

// 获取用户表列表
router.get('/', async function (req, res, next) {
  try {
    const page = parseInt(req.query.page) || undefined; // 如果没有提供page参数，则为undefined
    const limit = parseInt(req.query.limit) || undefined; // 如果没有提供limit参数，则为undefined
    const users = await userDao.getAllUsers(page, limit);
    res.status(200).json({ "code": "000", message: "获取成功", data: users });
  } catch (e) {
    res.status(500).send({ "code": "400", "message": "获取用户表列表失败" + e.message, data: null });
  }
});

// 添加用户表
router.post('/', async function (req, res, next) {
  try {
    const user = req.body;
    const userData = await userDao.insertUser(user);
    res.status(201).json({ "code": "000", message: "添加用户表成功", data: userData });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "添加用户表失败" + e, error: e.message });
  }
});

// 获取单个用户表的详细信息
router.get('/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const user = await userDao.getUserById(id);
    if (!user) {
      return res.status(404).json({ "code": "400", message: "未找到用户表" });
    }
    res.status(200).json({ "code": "000", message: "获取成功用户表成功", data: user[0] });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "获取用户表详细信息失败" + e.message, data: null });
  }
});

// 更新用户表
router.put('/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const updatedUser = req.body;
    const result = await userDao.updateUser(id, updatedUser);
    if (result.affectedRows === 0) {
      return res.status(500).json({ "code": "400", message: "更新用户表失败，未找到对应记录" });
    }
    res.status(200).json({ "code": "000", message: "更新用户表成功", data: updatedUser });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "更新用户表失败" + e.message, data: null });
  }
});

// 删除用户表
router.delete('/:id', async function (req, res, next) {
  try {
    const id = req.params.id;
    const result = await userDao.deleteUserById(id);
    if (result.affectedRows === 0) {
      return res.status(500).json({ "code": "400", message: "删除用户表失败，未找到对应记录" });
    }
    res.status(200).json({ "code": "000", message: "删除用户表成功" });
  } catch (e) {
    res.status(500).json({ "code": "400", message: "删除用户表失败" + e.message, data: null });
  }
});

// 导出router模块
module.exports = router;