<!-- 登录模块 -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive } from 'vue';
//获取路由器对象
let router = useRouter();
//组件挂载完毕
onMounted(() => {
});
</script>
<template>
  <div class='con'>
    <RouterView />
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
.con {
  padding: 30px;
}
</style>