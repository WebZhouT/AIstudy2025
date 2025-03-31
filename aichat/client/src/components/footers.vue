<!--  -->
<template>
  <van-tabbar v-model="active"
              active-color="#ee0a24">
    <van-tabbar-item icon="home-o" to="/home"
                     name="/home">首页</van-tabbar-item>
    <van-tabbar-item icon="search" to="/list"
                     name="/list">商品</van-tabbar-item>
    <van-tabbar-item icon="friends-o" to="/user"
                     name="/user">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup >
import { useRouter } from "vue-router";
import { onMounted, ref, reactive } from "vue";
let props = defineProps(["active"]);
//获取路由器对象
let router = useRouter();
let active = ref('');
//组件挂载完毕
onMounted(() => {
  active.value = router.currentRoute.value.path
});
</script>
<style lang='less' scoped>
</style>