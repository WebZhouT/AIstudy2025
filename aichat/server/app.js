// https://socket.io/zh-CN/docs/v4/server-initialization/
const createError = require('http-errors');
const express = require('express');
const { createServer } = require("node:http");
const { join } = require("node:path");
const { Server } = require("socket.io");
const userDao = require("./dao/chatsdao.js");
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const cors = require('cors');
const OpenAI = require("openai");
const axios = require('axios');
// 谷歌搜索
const { getJson } = require("serpapi");
const openai = new OpenAI({
  baseURL: 'https://api.deepseek.com',
  apiKey: 'sk-0b30386ca8f34b8eb46efc70d460c681'
});
var chatDao = require("./dao/chatsdao");
// 中间件，接口请求，设置登录状态
const { getUserState } = require('./middles/jwt');
const indexRouter = require('./routes/index');
/* AI表 */
const usersRouter = require('./routes/users');
/* 聊天表 */
const chatsRouter = require('./routes/chats');
var chatDao = require("./dao/chatsdao");
const app = express();
const httpServer = createServer(app);
// 监听在线人
let sum = [];
const io = new Server(httpServer, {
  cors: {
    origin: ["http://localhost:8080", "http://localhost:3888"]
    // origin: ["20250218case2admin.zt919.com", "20250218case2client.zt919.com"]
  }
});
// let message = [{ role: "system", content: "您正在与加密货币数据分析助手对话。我的核心能力包括：\n1. 解析链上数据（TVL/持币地址/流动性）\n2. 追踪多链生态进展（Ton/Solana/BNB Chain）\n3. 提供数据工具操作指南（DefiLlama/DappRadar/BscScan）\n4. 制定代币监控模板（含TVL/DApp/链上活跃度多维指标）\n注：对于未收录数据（如BANANAS31），我会提供手动验证路径与工具组合方案。" }];
let message = [{ role: "system", content: "你是一个专业的市场分析师" }];

// chat发送消息
async function main () {
  const completion = await openai.chat.completions.create({
    messages: message,
    model: "deepseek-reasoner",
    prefix_mode: true, // 允许以 assistant 消息结尾
    max_tokens: 8000
  });
  console.log(completion)
  message.push({ role: "system", content: completion.choices[0].message.content });
  console.log(completion.choices[0].message.content);
  return completion

}
// ---------------------- 新增函数：提取【】内关键字 ----------------------
function extractKeywords (text) {
  const regex = /【(.*?)】/g; // 匹配【】内的内容
  const matches = [...text.matchAll(regex)];
  return matches.map(match => match[1]); // 返回关键词数组
}
// 提示词构建函数
function buildPrompt ({ userQuestion, keywords, knowledge, maxSources }) {
  return `
【用户问题】${userQuestion}

【背景知识】根据关键词 ${keywords.join(', ')} 检索到以下最新信息：
${knowledge.slice(0, maxSources).map((k, i) =>
    `${i + 1}. [来源：${k.source}] ${k.title}\n   摘要：${k.snippet}`
  ).join('\n')}

【回答要求】
1. 优先使用知识库中2025年数据
2. 标注数据来源（如：据Coindesk 2025-03报道）
3. 不确定内容需注明“可能存在时效偏差”
  `;
}
io.on("connection", (socket) => {
  console.log(socket.id)
  // 服务器端，发送给客户端的数据
  socket.emit("hello", "world");
  // AI发给管理员
  socket.on("send", async (data, callback) => {
    console.log(data);
    const chatData = await chatDao.insertChat(data);
    // 服务器端，返回给客户端的数据
    callback({ "code": "000", message: "添加聊天表成功", data: chatData })
    // 广播给管理员链接的AI推广信息
    io.emit("getAllAdmin", { id: chatData[0].insertId, ...data });
  });
  // 管理员发给AI
  socket.on("getUser", async (data, callback) => {
    console.log('data', data);
    const chatData = await chatDao.insertChat(data);
    // 服务器端，返回给客户端的数据
    callback({ "code": "000", message: "添加聊天表成功", data: chatData })
    // io.emit("getAllAdmin", {
    //   id: data.insertId,
    //   sendid: data.sendid,
    //   role: 'assistant',
    //   comments: '666',
    //   type: "txt",
    //   source: ''
    // });
    // 广播给管理员链接的AI推广信息
    if (data.type == 'txt') {
      // 如果是文本
      console.log('cccc', data.comments)
      // // 新增代码：提取【】内的关键词
      const keywords = extractKeywords(data.comments);
      let searchResults = [];
      console.log(keywords)
      if (keywords.length > 0) {
        try {
          //     // 合并多个关键词为搜索语句（例如：【AI】【医疗】→ "AI 医疗"）
          const searchQuery = keywords.join(' ');
          getJson({
            engine: "google_light",
            q: "Trump tariffs Digital currency bubble burst",
            location: "Austin, Texas, United States",
            google_domain: "google.com",
            hl: "en",
            gl: "us",
            api_key: "373c486154696f277d65af08d933deac5c4b00b6a6e1f229834d537707e57237"
          }, async (json) => {
            try {
              const aiPrompt = `
                  用户问题：${data.comments}
                  用户标注的关键词：${keywords.join(', ')}
                  【背景知识】根据关键词 ${keywords.join(', ')} 检索到以下最新信息：${JSON.stringify(json["organic_results"])}
                  【回答要求】
                  1. 优先使用知识库中2025年数据
                  2. 标注数据来源（如：据Coindesk 2025-03报道）
                  3. 不确定内容需注明“可能存在时效偏差”
                `;

              message.push({ role: "user", content: JSON.stringify(json["organic_results"]) + aiPrompt });
              console.log(message);

              let result = await main(); // 现在可以正常使用 await

              let saveData = {
                sendid: data.sendid,
                role: 'assistant',
                comments: result.choices[0].message.content,
                type: "txt",
                source: JSON.stringify(json["organic_results"])
              };

              const chatData = await chatDao.insertChat(saveData);
              io.emit("getAllAdmin", { id: chatData[0].insertId, ...saveData });
            } catch (innerError) {
              console.error('内部处理失败:', innerError);
            }
          });


        } catch (searchError) {
          console.error('搜索处理失败:', searchError);
        }
      } else {

        console.log(message);
        (async () => {
          message.push({ role: "user", content: data.comments });
          let result = await main(); // 现在可以正常使用 await
          let saveData = {
            sendid: data.sendid,
            role: 'assistant',
            comments: result.choices[0].message.content,
            type: "txt",
            source: JSON.stringify(json["organic_results"])
          };

          const chatData = chatDao.insertChat(saveData);
          io.emit("getAllAdmin", { id: chatData[0].insertId, ...saveData });
        })
      }
    }
  });
  // 管理员删除信息
  socket.on("removeData", async (data, callback) => {
    console.log('管理员删除了数据', data);
    // 更新指定AI收到的信息
    io.emit("getremovecustomer" + data.sendid, { id: data.id });
    callback({ "code": "000", message: "删除成功", data: data })

  });
  // 当有人连接进来，人数+1
  sum = sum + 1;
  // 新的人数数据推送给客户端
  io.emit("count", sum);
  // 当断开链接，人数减1
  socket.on("disconnect", () => {
    sum--;
    console.log("sum", sum);
    io.emit("count", sum);
  });
});

httpServer.listen(3009);
// 允许所有跨域请求
app.use(cors());

app.use(logger('dev'));/* 默认的错误日志输出目录 */
app.use(express.json());/* 解析post方法下的json参数 */
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());/* 获取web浏览器发送的cookie中的内容 */
app.use(express.static(path.join(__dirname, 'public')));/* 静态文件目录 */
// 创建聊天的post请求
app.post('/getData', (req, res) => {
  console.log('接收到的数据:', req.body); // 直接访问 req.body，无需 .data
  let result = req.body.map((ele) => {
    return {
      role: ele.role,
      content: ele.comments,
    }
  })
  // 初始化循环对话的数据
  message = result.map((ele) => {
    ele.content = ele.content + ele.source;
    return ele;
  });
  res.json({ status: 'success', receivedData: result });
});
app.use('/', indexRouter);
app.use('/users', getUserState, usersRouter);
app.use('/chats', chatsRouter);
// catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});


// 创建服务 错误处理显示
app.use(function (err, req, res, next) {

  // 呈现错误页
  res.status(err.status || 500).json({
    code: '400',
    message: err.message || '未知错误'
  });
});

module.exports = app;


