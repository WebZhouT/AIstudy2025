<!--  -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive, onBeforeUnmount } from 'vue';
import footers from "@/components/footers.vue";
import { io } from "socket.io-client";
import { showLoadingToast, showConfirmDialog, showToast, closeToast, showDialog } from 'vant';
import axios from 'axios';
//获取路由器对象
let router = useRouter();
import {
  getAllChats,/* 获取全部聊天表的信息 */
  getChatById,/* 获取单个聊天表的详细信息 */
  addChat,/* 创建聊天表记录 */
  updateChat,/* 更新聊天表记录 */
  deleteChatById,/* 删除聊天表记录 */
} from '@/api/chat.js';
// 存储websocket链接对象
let sockets = ref(null);
// 连接的人数
let sum = ref(0);
// 上传图片
let files = ref(null);
const messages = ref([]);
// 聊天的盒子内容
let chatbox = ref(null);
// 输入的文本信息
let inputtxt = ref('');
let userdata = ref(localStorage.getItem('usersockets') == null ? '' : localStorage.getItem('usersockets'))
//组件挂载完毕
onMounted(() => {
  sockets.value = io("http://47.121.179.65:3009");
  // 如果存在用户信息，就显示之前的对话信息
  if (userdata.value != '') {
    axios.get('/api/chats/' + userdata.value).then((res) => {
      console.log(res.data.data)
      messages.value = res.data.data;
    }).catch((err) => {
      console.log(err)
    })
  }
  // client-side
  sockets.value.on("connect", (data) => {
    console.log(data)
    // console.log(sockets.value.id); // x8WIv7-mJelg7on_ALbx
    if (userdata.value == '') {
      localStorage.setItem('usersockets', sockets.value.id)
      userdata.value = sockets.value.id
      sockets.value.on("getcustomer" + sockets.value.id, (val) => {
        console.log('val', val)
        messages.value = [...messages.value, val]
        // 滚动到底部
        chatbox.value.scrollTop = chatbox.value.scrollHeight
      });
      // 调用消息撤回方法
      sockets.value.on("getremovecustomer" + sockets.value.id, (val) => {
        console.log('val', val)
        messages.value = messages.value.filter((ele) => {
          return ele.id != val.id
        })
        // 滚动到底部
        chatbox.value.scrollTop = chatbox.value.scrollHeight
      });
    } else {
      sockets.value.on("getcustomer" + userdata.value, (val) => {
        console.log('val', val)
        messages.value = [...messages.value, val]
        // 滚动到底部
        chatbox.value.scrollTop = chatbox.value.scrollHeight
      });
      // 调用消息撤回方法
      sockets.value.on("getremovecustomer" + userdata.value, (val) => {
        console.log('val', val)
        console.log('我删除了')
        messages.value = messages.value.filter((ele) => {
          return ele.id != val.id
        })
        // 滚动到底部
        chatbox.value.scrollTop = chatbox.value.scrollHeight
      });
    }

    // console.log(sockets.value.connected); // true
  });

});



onBeforeUnmount(() => {
});
const upload = () => {
  files.value.click()
}
// 切换文件
const changeFile = ($event) => {
  console.log($event.target.files[0])
  let formdata = new FormData();
  formdata.append("file", $event.target.files[0]);
  /* 显示加载状态 */
  showLoadingToast({
    duration: 0,
    forbidClick: true,
    message: '加载中...',
  });
  // 图片上传
  axios.post("/api/upload", formdata).then((res) => {
    console.log(res)
    if (res.data.code == '000') {
      /* 关闭加载状态 */
      closeToast()
      // messages.value.push({ 'type': 'img', 'data': res.data.data.url })
      console.log(messages.value)
      // 重置files中的文件内容为空
      files.value.value = ''
      // 点击后发送数据给客户端
      let submitdata = { 'sendid': userdata.value, 'acceptid': 1, 'type': 'img', 'comments': res.data.data.filename };
      sockets.value.emit("send", submitdata, (response) => {
        console.log('response', response); // ok
        messages.value.push({ id: response.data[0].insertId, ...submitdata })
        inputtxt.value = ''
        // 滚动到底部
        chatbox.value.scrollTop = chatbox.value.scrollHeight
      });
    } else {
      /* 关闭加载状态 */
      closeToast()
    }
  }).catch((err) => {
    /* 关闭加载状态 */
    closeToast()
  })
}
const send = () => {
  let txt = inputtxt.value;
  if (txt) {
    let submitdata = { 'sendid': userdata.value, 'acceptid': 1, 'type': 'txt', 'comments': txt };
    console.log(submitdata)
    sockets.value.emit("send", submitdata, (response) => {
      console.log('response', response); // ok
      messages.value.push({ id: response.data[0].insertId, ...submitdata })
      inputtxt.value = ''
      // 滚动到底部
      chatbox.value.scrollTop = chatbox.value.scrollHeight
    });
  }
}
</script>
<template>
  <div id="mainbox">
    <van-nav-bar title="在线聊天" />
    <ul class="chatlist" ref="chatbox">
      <li v-for="(message, index) in messages"
          :key="index">
        <div class="mainbox">
          <div class="leftbox btn-group"
               v-if="message.acceptid==2">
            <div class="btn">
              <img class="head"
                   src="/avatar-admin2.png"
                   alt="">

            </div>
            <div class="contxt">
              <div v-if="message.type=='txt'"
                   class="txtbox">
                {{message.comments}}
              </div>
              <div v-if="message.type=='img'"
                   class="txtbox">
                <img :src="'/api/uploads/'+message.comments"
                     alt="" style="width:100px;">
              </div>
            </div>
          </div>
          <div class="rightbox btn-group"
               v-if="message.acceptid==1">

            <div class="contxt">
              <div v-if="message.type=='txt'"
                   class="txtbox">
                {{message.comments}}
              </div>
              <div v-if="message.type=='img'"
                   class="txtbox">
                <img :src="'/api/uploads/'+message.comments"
                     alt="" style="width:100px;">
              </div>
            </div>
            <div class="btn">
              <img class="head"
                   src="/userhead.jpeg" alt="">
            </div>
          </div>
        </div>

      </li>
    </ul>
    <input type="file" hidden ref="files"
           @change="changeFile($event)">
    <div class="footerbox btn-group">
      <van-icon name="photo-o" class="iconbox"
                @click="upload" />
      <div class="sendtxt"><input type="text"
               placeholder="输入内容"
               v-model="inputtxt">
      </div>
      <a href="javascript:;" @click="send"
         id="send">发送</a>
    </div>
  </div>
  <!-- <div class=''>
    <van-nav-bar title="京东" />
    <van-swipe class="my-swipe" :autoplay="3000"
               indicator-color="white">
      <van-swipe-item>1</van-swipe-item>
      <van-swipe-item>2</van-swipe-item>
      <van-swipe-item>3</van-swipe-item>
      <van-swipe-item>4</van-swipe-item>
    </van-swipe>
    <footers />
  </div> -->
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
.head {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
}
.contxt {
  margin: 10px;
  border-radius: 10px;
  .txtbox {
    padding: 20px;
  }
}
.leftbox {
  margin-right: 120px;
  margin-bottom: 10px;
  display: flex;
  flex-wrap: nowrap;
  .contxt {
    flex-grow: 1;
    background: #f4f4f4;
  }
}
.rightbox {
  margin-left: 120px;
  display: flex;
  flex-wrap: nowrap;
  margin-bottom: 10px;
  .contxt {
    flex-grow: 1;
    background: #f4f4f4;
  }
}
.my-swipe {
  img {
    display: block;
    width: 100%;
    height: 400px;
    object-fit: cover;
  }
}
#mainbox {
  height: 100vh;
  position: relative;
}
.footerbox {
  background: #fff;
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 120px;
  display: flex;
  z-index: 96666;
  .iconbox {
    font-size: 40px;
    line-height: 90px;
    padding: 0 20px;
    height: 90px;
  }
  .sendtxt {
    flex-grow: 1;
    input {
      width: 100%;
      line-height: 90px;
      border: none;
      font-size: 30px;
      background: #f4f4f4;
      padding: 0 30px;
    }
  }
  #send {
    height: 90px;
    width: 120px;
    line-height: 90px;
    color: #333;
    font-size: 30px;
    text-align: center;
    padding: 0 10px;
  }
}
.chatlist {
  padding-bottom: 120px;
  overflow: auto;
  height: calc(100vh - 240px);
  * {
    font-size: 30px;
    line-height: 60px;
  }
}
</style>