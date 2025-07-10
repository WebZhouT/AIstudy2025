<!--  -->
<template>
  <!-- 底部导航 -->
  <div class="tab-bar">
    <router-link to="/home" name="/home"
                 class="tab-item active">
      <i class="iconfont icon-shouye"></i>
      <span>首页</span>
    </router-link>
    <router-link to="/sort" name="/sort"
                 class="tab-item">
      <i class="iconfont icon-liebiao"></i>
      <span>分类</span>
    </router-link>
    <router-link to="/shopcard" name="/shopcard"
                 class="tab-item">
      <i class="iconfont icon-gouwuche"></i>
      <span>购物车</span>
    </router-link>
    <router-link to="/user" name="/user"
                 class="tab-item">
      <i class="iconfont icon-icon7"></i>
      <span>我的</span>
    </router-link>
  </div>
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
.tab-bar {
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  background-color: #ffffff;
  border-top: 1px solid #f5f5f5;
  position: fixed;
  bottom: 0;
  width: 100%;
  max-width: 375px;
  z-index: 100;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666666;
}

.tab-item i {
  font-size: 18px;
  margin-bottom: 2px;
}

.tab-item span {
  font-size: 12px;
}

.tab-item.active {
  color: #ff6b6b;
}
</style>