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
  // axios.get("/api/list/" + router.currentRoute.value.params.id).then((res) => {
  //   detail.value = res.data
  // })
});
const onClickLeft = () => {
  router.push('/list')
}
</script>
<template>
  <div class=''>
    <van-nav-bar title="详情" left-text="返回"
                 left-arrow
                 @click-left="onClickLeft" />
    <!-- <img class="png" src="" alt=""> -->
    <van-field label="新闻标题">
      <template #input>
        <b>{{ detail.tit }}</b>
      </template>
    </van-field>
    <van-action-bar>
      <van-action-bar-icon icon="chat-o" text="客服"
                           color="#ee0a24" />
      <van-action-bar-icon icon="cart-o"
                           text="购物车" />
      <van-action-bar-icon icon="star" text="已收藏"
                           color="#ff5000" />
      <van-action-bar-button type="warning"
                             text="加入购物车" />
      <van-action-bar-button type="danger"
                             text="立即购买" />
    </van-action-bar>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
.png {
  display: block;
  width: 100%;
}
</style>