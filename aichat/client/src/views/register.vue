<!--  -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive } from 'vue';
import { showToast } from "vant";
//获取路由器对象
let router = useRouter();
//组件挂载完毕
onMounted(() => {
});
const username = ref('');
const password = ref('');
const email = ref('');
const mobile = ref('');
const onSubmit = (values) => {
  console.log('submit', values);
  showToast({
    'message': "注册成功",
    "onClose": function () {
      router.push('/register')
    }
  })
};
</script>
<template>
  <div class=''>
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field v-model="username" name="用户名"
                   label="用户名" placeholder="用户名"
                   :rules="[{ required: true, message: '请填写用户名' }]" />
        <van-field v-model="password"
                   type="password" name="密码"
                   label="密码" placeholder="密码"
                   :rules="[{ required: true, message: '请填写密码' }]" />
      </van-cell-group>
      <div style="margin: 16px;">
        <van-button round block type="primary"
                    native-type="submit">
          注册
        </van-button>
      </div>
      <router-link to='/login'>返回登录</router-link>
    </van-form>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>