<!--  -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive } from 'vue';
import footers from "@/components/footers.vue";
//获取路由器对象
let router = useRouter();
//组件挂载完毕
onMounted(() => {
});
</script>
<template>
  <div class='container'> <!-- 用户信息 -->
    <div class="user-info">
      <img src="https://ai-public.mastergo.com/ai/img_res/6973324cf715e3f7cf1ba6bcfd93ed7c.jpg"
           class="user-avatar" />
      <h2 class="user-name">劳动者</h2>
      <div class="user-stats">
        <div class="stat-item">
          <span class="stat-number">5</span>
          <span class="stat-label">已报名</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">3</span>
          <span class="stat-label">已参加</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">7</span>
          <span class="stat-label">签到</span>
        </div>
      </div>

      <!-- 功能菜单 -->
      <div class="menu-list">
        <div class="menu-item">
          <i class="fas fa-star"></i>
          <span>我的活动</span>
          <i class="fas fa-chevron-right"></i>
        </div>
        <div class="menu-item">
          <i class="fas fa-heart"></i>
          <span>我的收藏</span>
          <i class="fas fa-chevron-right"></i>
        </div>
        <div class="menu-item">
          <i class="fas fa-bell"></i>
          <span>消息通知</span>
          <i class="fas fa-chevron-right"></i>
        </div>
        <div class="menu-item">
          <i class="fas fa-cog"></i>
          <span>设置</span>
          <i class="fas fa-chevron-right"></i>
        </div>
        <router-link to="/login"
                     class="menu-item">
          <i class="fas fa-cog"></i>
          <span>登录/注册</span>
          <i class="fas fa-chevron-right"></i>
        </router-link>
      </div>
    </div>
    <footers />
  </div>
</template>

<style lang='less' scoped>
.menu-list {
  display: block;
  width: 100%;
}
</style>