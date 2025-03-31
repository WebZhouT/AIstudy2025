<!--  -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive, nextTick } from 'vue';
import { io } from "socket.io-client";
import { ElMessage } from 'element-plus'
import { marked } from 'marked'; // 使用 marked
import axios from 'axios';
//获取路由器对象
let router = useRouter();
let inputtxt = ref('');
// 存储websocket链接对象
let sockets = ref(null);
// 默认头像
let head = ref(null);
// 总的数据
let userlist = ref([]);
// 切换的聊天列表
let chatlist = ref([]);
// 激活的选项卡
let active = ref(null);
// 聊天的盒子内容
let chatbox = ref(null);
//组件挂载完毕
onMounted(() => {
  sockets.value = io("http://127.0.0.1:3009");
  getData();
  // client-side
  sockets.value.on("connect", (data) => {
    console.log(data)
    // console.log(sockets.value.id); // x8WIv7-mJelg7on_ALbx
    // console.log(sockets.value.connected); // true
  });
  // 管理员监听数据变化
  sockets.value.on("getAllAdmin", (val) => {
    console.log('getAllAdmin', val)
    // 总的数据列表
    let list = userlist.value;
    let exit = list.findIndex((ele) => {
      return ele.sendid == val.sendid
    });
    console.log('exit', exit);
    if (exit != -1) {
      console.log('list[exit].data1', list[exit].data);
      // 如果存在
      list[exit].data.push(val)
      console.log('list[exit].data', list[exit].data);
      userlist.value = [...list]
      if (active.value == val.sendid) {
        // 如果选择的刚好是当前的用户
        chatlist.value = userlist.value[exit]
        console.log('chatlist', chatlist.value)
      } else {

      }

    } else {
      list.push({
        sendid: val.sendid,
        data: [val]
      })
      userlist.value = list;
    }
  });
});
// 上传图片
let files = ref(null);
// 获取基础数据
const getData = () => {
  axios.get('/api/chats').then(res => {
    console.log(JSON.stringify(res.data.data.data))
    console.log(mergeArray(res.data.data.data))
    userlist.value = mergeArray(res.data.data.data)
    // 默认选择的用户名
    active.value = userlist.value[0].sendid;
    chatlist.value = userlist.value[0]
    nextTick(() => {
      // 滚动到页面底部
      chatbox.value.scrollTop = chatbox.value.scrollHeight
    })
    axios.post('/api/getData', chatlist.value.data, {
      headers: {
        'Content-Type': 'application/json' // 明确指定请求头（Axios 默认会自动设置，但显式声明更安全）
      }
    })
      .then((res) => {
        console.log('响应数据:', res.data); // 注意：Axios 的响应数据在 res.data 中
      })
      .catch((error) => {
        console.error('请求失败:', error.response?.data || error.message);
      });
  })

}
// 发送
const send = () => {
  let txt = inputtxt.value;
  if (txt) {
    let submitdata = { 'sendid': chatlist.value.sendid, 'role': 'user', 'type': 'txt', 'comments': txt };
    console.log(submitdata)
    sockets.value.emit("getUser", submitdata, (response) => {
      console.log('response', response); // ok
      let resultId = response.data[0].insertId;
      let maindata = userlist.value;
      userlist.value = maindata.map((ele) => {
        if (ele.name == active.value) {
          ele.data = [...ele.data, { id: resultId, ...submitdata }]
        }
        return ele;
      })
      let chatdata = userlist.value.filter((ele) => {
        return ele.name == active.value;
      })
      console.log('chatlist', chatdata);
      console.log('userlist', userlist.value);
      chatlist.value = { ...chatdata[0] };
      // 滚动到底部
      chatbox.value.scrollTop = chatbox.value.scrollHeight
    });
  } else {
    // 请填充内容
    ElMessage({
      message: '请填写内容',
      type: 'warning',
      duration: 2000,
      onClose: () => {
        // 输入框获取焦点
        inputtxt.value.focus();
      }
    });
  }

}
// 编写函数合并数组中对象同个sendid的数据
const mergeArray = (arr) => {
  // 使用 Map 来按 sendid 分组，提高查找效率
  const groupedMap = new Map();

  arr.forEach(item => {
    const { sendid, ...rest } = item; // 提取 sendid 和其他属性
    if (groupedMap.has(sendid)) {
      // 如果 Map 中已有该 sendid，将当前项的其他数据添加到 data 数组中
      groupedMap.get(sendid).data.push(rest);
    } else {
      // 如果没有，则创建一个新的对象并加入 Map
      groupedMap.set(sendid, { sendid: sendid, data: [rest] });
    }
  });

  // 将 Map 转换为数组形式
  return Array.from(groupedMap.values());
};
/* 切换聊天用户 */
const changeName = (val) => {
  chatlist.value = val;
  active.value = val.sendid
  console.log(chatbox.value)
  // 滚动到底部
  // chatbox.value.scrollIntoView({ behavior: "smooth", block: "end" });
  chatbox.value.scrollTop = chatbox.value.scrollHeight
  axios.post('/api/getData', chatlist.value.data, {
    headers: {
      'Content-Type': 'application/json' // 明确指定请求头（Axios 默认会自动设置，但显式声明更安全）
    }
  })
    .then((res) => {
      console.log('响应数据:', res.data); // 注意：Axios 的响应数据在 res.data 中
    })
    .catch((error) => {
      console.error('请求失败:', error.response?.data || error.message);
    });
}
const upload = () => {
  files.value.click()
}
// 切换文件
const changeFile = ($event) => {
  console.log($event.target.files[0])
  let formdata = new FormData();
  formdata.append("file", $event.target.files[0]);
  // 图片上传
  axios.post("/api/upload", formdata).then((res) => {
    console.log(res.data.data.url)
    if (res.data.code == '000') {
      // 重置files中的文件内容为空
      files.value.value = ''
      // 点击后发送数据给客户端
      let submitdata = { 'sendid': chatlist.value.sendid, 'role': 'system', 'type': 'img', 'comments': res.data.data.filename };
      sockets.value.emit("getUser", submitdata, (response) => {
        console.log('response', response); // ok
        let resultId = response.data[0].insertId;
        let maindata = userlist.value;
        userlist.value = maindata.map((ele) => {
          if (ele.sendid == active.value) {
            ele.data = [...ele.data, { id: resultId, ...submitdata }]
          }
          return ele;
        })
        let chatdata = userlist.value.filter((ele) => {
          return ele.name == active.value;
        })
        console.log('chatlist', chatdata);
        console.log('userlist', userlist.value);
        chatlist.value = { ...chatdata[0] };
        // 滚动到底部
        chatbox.value.scrollTop = chatbox.value.scrollHeight
      });
    } else {
      // 发送有误请重新上传

    }
  });
}
// 删除
const deleted = (datas) => {
  axios.delete('/api/chats/name/' + datas.name, datas.id).then((res) => {
    // 删除成功
    if (res.data.code == '000') {
      // 弹框删除成功提示关闭后调用todatas方法
      ElMessage({
        message: '删除成功',
        type: 'success',
        // 延迟1秒
        duration: 1000,
        // 关闭后调用getData方法
        onClose: () => {
          getData()
        }
      })

    }
  })
}
// 移除指定id的数据
const remove = (item) => {
  axios.delete('/api/chats/' + item.id).then((res) => {
    // 删除成功
    if (res.data.code == '000') {
      // 弹框删除成功提示关闭后调用todatas方法
      ElMessage({
        message: '删除成功',
        type: 'success',
        // 延迟1秒
        duration: 1000,
        // 关闭后调用getData方法
        onClose: () => {
          chatlist.value.data = chatlist.value.data.filter((ele) => {
            return ele.id != item.id;
          });
          // 滚动到底部
          chatbox.value.scrollTop = chatbox.value.scrollHeight
        }
      })
      sockets.value.emit("removeData", { id: item.id, sendid: active.value }, (response) => {
        console.log(response)
      })
    }
  })
}
// 创建聊天
const addChat = () => {
  let addData = {
    /* 随机时间戳 */
    name: new Date().getTime(),
    data: []
  }
  userlist.value = [...userlist.value, addData]
  // 默认选择的用户名
  active.value = addData.name;
  chatlist.value = addData
  axios.post('/api/getData', chatlist.value.data, {
    headers: {
      'Content-Type': 'application/json' // 明确指定请求头（Axios 默认会自动设置，但显式声明更安全）
    }
  })
    .then((res) => {
      console.log('响应数据:', res.data); // 注意：Axios 的响应数据在 res.data 中
    })
    .catch((error) => {
      console.error('请求失败:', error.response?.data || error.message);
    });
}
</script>
<template>
  <div class='content'>
    <el-container>
      <el-aside width="300px" class="leftbar">
        <ul>
          <li v-for="(item,i) in userlist"
              class="fn-clear" :key="i"
              @click="changeName(item)">
            <el-button class="leftbox"
                       :type="item.sendid==active?'primary':''">
              {{item.sendid}}
            </el-button>
            <el-icon class="del"
                     @click="deleted(item)">
              <CircleClose />
            </el-icon>
          </li>
          <li><el-button
                       @click="addChat()">创建聊天</el-button>
          </li>
        </ul>

      </el-aside>

      <UploadWord models="certificate"
                  :imgurl="'/api/uploads/'+head"
                  :img="'/api/uploads/'+head"
                  @success="(item)=>{
            console.log(item)
              head = item.filename;/* 存储的图片上传地址 */
            }" />
      <el-container>
        <el-main> <!-- 聊天记录盒子 -->
          <div class="chatbox" ref="chatbox">
            <div class="txtbox">
              <div v-for="(item,i) in chatlist.data"
                   :key="i">
                <el-row :gutter="20"
                        class="line leftbox"
                        v-if="item.role=='system'||item.role=='assistant'">

                  <el-col :span="20">
                    <el-card class="box-card">
                      <!--  <template #header>
                        <div class="card-header">
                          <span>用户名：{{chatlist.name}}</span>
                           <el-button class="button times"
                                     text>时间：{{item.subtime}}</el-button> 
                        </div>
                      </template>-->
                      <div class="text item">
                        <div
                             v-if="item.type=='txt'">
                          <div
                               v-html="marked.parse(item.comments)">
                          </div>
                        </div>
                        <div
                             v-if="item.type=='img'">
                          <img :src="'/api/uploads/'+item.comments"
                               alt=""
                               style="width:120px">
                        </div>
                        <el-button type="danger"
                                   size="small"
                                   @click="remove(item)">删除</el-button>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="4">
                    <!-- 用户头像 -->
                    <img src="/avatar-admin2.png"
                         alt=""
                         style="width:50px">

                  </el-col>
                </el-row>
                <el-row :gutter="20"
                        class="line rightbox"
                        v-if="item.role=='user'">
                  <el-col :span="4">
                    <!-- logo等 -->
                    <img src="/userhead.jpeg"
                         alt=""
                         style="width:50px">
                  </el-col>
                  <el-col :span="20">
                    <el-card class="box-card">
                      <!--<template #header>
                        <div class="card-header">
                          <span>管理员</span>
                           <el-button class="button times"
                                     text>时间：{{item.subtime}}</el-button> 
                        </div>
                      </template>-->
                      <div class="text item">
                        <div
                             v-if="item.type=='txt'">
                          <div
                               v-html="marked.parse(item.comments)">
                          </div>
                        </div>
                        <div
                             v-if="item.type=='img'">
                          <img :src="'/api/uploads/'+item.comments"
                               alt=""
                               style="width:120px">
                        </div>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>
        </el-main>
        <el-footer>
          <input type="file" hidden ref="files"
                 @change="changeFile($event)">
          <el-input v-model="inputtxt"
                    style="max-width: 600px"
                    placeholder="输入内容">
            <template #prepend>
              <el-button
                         @click="upload">选择图片</el-button>
            </template>
            <template #append>
              <el-button
                         @click="send">发送</el-button>
            </template>
          </el-input>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
.del {
  color: #666;
  margin: 20px 10px;
  cursor: pointer;
}
.content {
  height: calc(100vh - 100px);
  .leftbox {
  }
}
ul,
li {
  list-style: none;
  margin: 0;
  padding: 0;
}
.chatbox {
  height: calc(100vh - 200px);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 30px;
}
.line {
  margin: 30px 0;
  .logo {
    width: 60%;
    margin: auto;
    display: block;
  }
}
.comment-input {
  display: flex;
  flex-wrap: nowrap;
  input {
    width: 100%;
  }
}
.subbox {
  margin: 30px;
  width: 100%;
  .tit {
    text-align: right;
  }
}
.times {
  float: right;
}
.txtbox {
  padding-bottom: 120px;
}
.mainbox {
  position: relative;
  width: 100%;
  height: calc(100vh - 120px);
  overflow: hidden;
  .txtbox {
    overflow: auto;
    padding-bottom: 120px;
    height: calc(100vh - 210px);
  }
}
.downtxt {
  position: absolute;
  bottom: 0;
  background: #fff;
  width: 100%;
}
.leftbox {
  .card-header {
    span {
      display: block;
      text-align: right;
    }
  }
  .el-card__body {
    .text {
      text-align: right;
    }
  }
}
.rightbox {
  .card-header {
    span {
      display: block;
      text-align: left;
    }
  }
  .el-card__body {
    .text {
      text-align: left;
    }
  }
}
.leftbar {
  overflow-x: hidden;
}
.markdown-content {
  h1 {
    font-size: 2em;
  }
  code {
    background: #f5f5f5;
    padding: 2px 4px;
  }
  pre code {
    display: block;
    padding: 1em;
  }
}
</style>