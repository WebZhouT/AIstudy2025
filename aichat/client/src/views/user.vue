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
  <div class=''>
    <van-nav-bar title="我的" />
    <van-card desc="用户名："
              thumb="https://fastly.jsdelivr.net/npm/@vant/assets/icon-demo.png">
      <template #tags>
        <van-button>前往登录</van-button>
      </template>
    </van-card>
    <!-- <van-cell-group title="分组2">
  <van-cell title="单元格" value="内容" is-link icon="location-o"/>
</van-cell-group> -->
    <van-cell-group inset>
      <van-cell title="购物车" is-link />
      <van-cell title="订单管理" is-link />
      <van-cell title="退出登录" is-link />
    </van-cell-group>
    <footers active="/user" />
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>