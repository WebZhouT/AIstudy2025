<!-- 用户管理添加 -->
<template>
  <div class=''>
    <h1>用户管理添加</h1>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive } from 'vue';
//获取路由器对象
let router = useRouter();
//调用
const goDetail = () => { };
//组件挂载完毕
onMounted(() => {
  goDetail();
});
</script>
<style lang='scss' scoped>
//@import url(); 引入公共css类
</style>