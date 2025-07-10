<!--  -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive } from 'vue';
//获取路由器对象
let router = useRouter();
//组件挂载完毕
onMounted(() => {
});
const toHome = () => {
  router.push('/');
};
</script>
<template>
  <div class=''> <!-- 顶部标志 -->
    <div class="login-logo">
      <!-- <img src="https://ai-public.mastergo.com/ai/img_res/b1ca4a4919b992c34ff51c6a81052a95.jpg"
           class="logo-image" /> -->
      <h1 class="logo-text">五一劳动节</h1>
    </div>

    <!-- 登录表单 -->
    <div class="login-form">
      <div class="form-item">
        <i class="fas fa-user"></i>
        <input type="text" placeholder="手机号/账号"
               class="form-input" />
      </div>
      <div class="form-item">
        <i class="fas fa-solid fa-lock"></i>
        <input type="password" placeholder="密码"
               class="form-input" />
      </div>
      <div class="form-item">
        <i class="fas fa-key"></i>
        <input type="text" placeholder="验证码"
               class="form-input code-input" />
        <span class="code-btn">获取验证码</span>
      </div>
    </div>

    <!-- 登录按钮 -->
    <button class="login-btn"
            @click="toHome()">登录</button>

    <!-- 快捷登录 -->
    <div class="quick-login">
      <h3 class="quick-title">快捷登录</h3>
      <div class="quick-icons">
        <i class="fab fa-weixin"></i>
        <i class="fab fa-qq"></i>
        <i class="fab fa-weibo"></i>
      </div>
    </div>

    <!-- 底部链接 -->
    <div class="login-footer">
      <span>还没有账号？</span>
      <span class="register-link">立即注册</span>
      <span>|</span>
      <span class="help-link">帮助中心</span>
    </div>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>