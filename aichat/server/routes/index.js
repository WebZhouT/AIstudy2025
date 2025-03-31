const express = require('express');
const router = express.Router();
/* 文件上传 */
const { uploadFile } = require('../middles/uploadFile');
const userDao = require("../dao/indexdao");
/* 设置当前token */
const { Token } = require('../utils/token');
/* 密码加密和解密方法 */
const { genPassword, exportPassword } = require('../utils/cryp');
/* GET home page. */
router.get('/', function (req, res, next) {
  res.render('index', { title: 'Express' });
});
// 图片上传路由
router.post('/upLoad', uploadFile, (req, res) => {
  if (!req.file) {
    res.status(400).json({ code: 400, message: '上传失败，文件未找到' });
  } else {
    // 构建图片的URL
    const imageUrl = `${req.protocol}://${req.get('host')}/uploads/${req.file.filename}`;
    // 返回成功响应
    res.status(200).json({
      code: "000",
      message: '图片上传成功',
      data: {
        filename: req.file.filename,
        url: imageUrl
      }
    });
  }
});
// 用户注册
router.post('/register', async (req, res) => {
  try {
    const { username, password, email, mobile, intro, head } = req.body;
    const existingUser = await userDao.getUserByUsername(username);
    if (existingUser) {
      return res.status(400).json({ code: '400', message: '用户名已存在' });
    }
    const user = await userDao.addUser({ username, password, email, mobile, intro, head });
    res.json({ code: '000', data: { id: user }, message: '注册成功' });
  } catch (error) {
    res.status(400).json({ code: '400', message: error.message });
  }
});

// 用户登录
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await userDao.getUserByUsername(username);
    if (user && user.password === genPassword(password)) {
      // 设置请求token
      const tokenStr = Token.encrypt(user);
      delete user.password;
      // 登录成功逻辑，可能需要创建一个token等
      res.status(200).json({ code: '000', data: { ...user, token: tokenStr }, message: '登录成功' });
    } else {
      res.status(200).json({ code: '401', message: '用户名或密码错误' });
    }
  } catch (error) {
    res.status(400).json({ code: '400', message: error.message });
  }
});
module.exports = router;
