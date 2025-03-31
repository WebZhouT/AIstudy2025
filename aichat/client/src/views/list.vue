<!--  -->
<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref, reactive } from 'vue';
import footers from "@/components/footers.vue";
import axios from 'axios';
//获取路由器对象
let router = useRouter();
//组件挂载完毕
onMounted(() => {
  // axios.get('http://localhost:3000/goods').then((res) => {
  //   list.value = res.data
  // })
});
</script>
<template>
  <div class=''>
    <van-nav-bar title="列表" />
    <van-card num="2" price="2.00" desc="描述信息"
              title="商品标题"
              thumb="https://fastly.jsdelivr.net/npm/@vant/assets/icon-demo.png">
      <template #tags>
        <van-tag plain type="primary">标签</van-tag>
        <van-tag plain type="primary">标签</van-tag>
      </template>
      <template #footer>
        <van-button size="mini">查看详情</van-button>
      </template>
    </van-card>
    <footers active="/list" />
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>