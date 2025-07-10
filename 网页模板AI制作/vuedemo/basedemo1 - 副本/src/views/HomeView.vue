

<template>
  <div class="container">
    <!-- 顶部搜索区 -->
    <div class="header">
      <div class="logo">商城</div>
      <div class="search-box">
        <i
           class="iconfont icon-sousuo search-icon"></i>
        <input type="text" placeholder="搜索商品"
               class="search-input" />
      </div>
      <div class="cart-box">
        <i class="iconfont  icon-gouwuche"></i>
      </div>
    </div>

    <!-- 分类标签栏 -->
    <div class="category-scroll">
      <div class="category-list">
        <div class="category-item active">推荐</div>
        <div class="category-item">数码</div>
        <div class="category-item">服装</div>
        <div class="category-item">美食</div>
        <div class="category-item">家居</div>
        <div class="category-item">母婴</div>
        <div class="category-item">美妆</div>
      </div>
    </div>

    <div class="content">
      <!-- 轮播图 -->
      <div class="banner">
        <img src="https://ai-public.mastergo.com/ai/img_res/ea83fea3951cae24f35c86819e94fd0e.jpg"
             alt="banner" />
      </div>

      <!-- 功能分类区 -->
      <div class="function-grid">
        <div class="function-item"
             v-for="(item, index) in functionList"
             :key="index">
          <img :src="item.icon"
               :alt="item.name" />
          <span>{{ item.name }}</span>
        </div>
      </div>

      <!-- 特惠专区 -->
      <div class="special-section">
        <div class="section-title">
          <span class="title">特惠专区</span>
          <span class="more">更多</span>
        </div>
        <div class="special-scroll">
          <div class="special-list">
            <div class="special-item"
                 v-for="(item, index) in specialList"
                 :key="index">
              <img :src="item.image"
                   :alt="item.name" />
              <span
                    class="name">{{ item.name }}</span>
              <span
                    class="price">¥{{ item.price }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 商品列表 -->
      <div class="goods-section">
        <div class="filter-bar">
          <span
                class="filter-item active">综合</span>
          <span class="filter-item">销量</span>
          <span class="filter-item">价格</span>
        </div>
        <div class="goods-list">
          <div class="goods-item"
               v-for="(item, index) in goodsList"
               :key="index">
            <img :src="item.image"
                 :alt="item.name" />
            <div class="info">
              <span
                    class="name">{{ item.name }}</span>
              <span
                    class="price">¥{{ item.price }}</span>
              <button
                      class="!rounded-button">购买</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <footers />
  </div>
</template>

<script  setup>
import { ref } from "vue";
import footers from "@/components/footers.vue";
const functionList = ref([
  {
    name: "超市",
    icon: "https://ai-public.mastergo.com/ai/img_res/d8cd9a412e323315bd8ab440b489374d.jpg",
  },
  {
    name: "数码",
    icon: "https://ai-public.mastergo.com/ai/img_res/32e61b0cdfb026ce9d007472044b481a.jpg",
  },
  {
    name: "服装",
    icon: "https://ai-public.mastergo.com/ai/img_res/fc2023aa83f16ff62f7dfe3e1b65b0d9.jpg",
  },
  {
    name: "美食",
    icon: "https://ai-public.mastergo.com/ai/img_res/d4d47324ece67fd14b563d58a3a49cf0.jpg",
  },
]);

const specialList = ref([
  {
    name: "限时特惠手机",
    price: "2999",
    image:
      "https://ai-public.mastergo.com/ai/img_res/ebe3edb35367d5aa543f1fad00f30c5c.jpg",
  },
  {
    name: "新款休闲运动鞋",
    price: "399",
    image:
      "https://ai-public.mastergo.com/ai/img_res/3474982808944a9eae7cf818a4f9504d.jpg",
  },
  {
    name: "时尚双肩包",
    price: "199",
    image:
      "https://ai-public.mastergo.com/ai/img_res/cfca622fd74bc841b35871f0adbd01c4.jpg",
  },
]);

const goodsList = ref([
  {
    name: "2023新款智能手表",
    price: "899",
    image:
      "https://ai-public.mastergo.com/ai/img_res/d57ed32ee0e0defd86ee44dcd935f15a.jpg",
  },
  {
    name: "无线蓝牙耳机",
    price: "299",
    image:
      "https://ai-public.mastergo.com/ai/img_res/df20e60e89c66d3ba639b55922525e5b.jpg",
  },
  {
    name: "轻薄笔记本电脑",
    price: "5999",
    image:
      "https://ai-public.mastergo.com/ai/img_res/76f0faa59c5e6617099e2be4669d9d01.jpg",
  },
  {
    name: "高清投影仪",
    price: "2499",
    image:
      "https://ai-public.mastergo.com/ai/img_res/bd4560377f3c2e4291c93a9a94290858.jpg",
  },
]);
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
  position: relative;
  max-width: 375px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background-color: #ffffff;
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 100;
  max-width: 375px;
}

.logo {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 16px;
  padding: 6px 12px;
}

.search-icon {
  margin-right: 8px;
  color: #999999;
  font-size: 14px;
}

.search-input {
  flex: 1;
  font-size: 14px;
  border: none;
  background: transparent;
  outline: none;
}

.cart-box {
  margin-left: 10px;
  color: #333333;
  font-size: 18px;
}

.category-scroll {
  background-color: #ffffff;
  position: fixed;
  top: 50px;
  width: 100%;
  max-width: 375px;
  z-index: 99;
  overflow-x: auto;
  white-space: nowrap;
  padding: 10px 0;
}

.category-list {
  display: inline-flex;
  padding: 0 15px;
}

.category-item {
  padding: 6px 12px;
  margin-right: 10px;
  font-size: 14px;
  color: #666666;
  display: inline-block;
}

.category-item.active {
  color: #ff6b6b;
  font-weight: bold;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding-top: 100px;
  padding-bottom: 60px;
}

.banner {
  height: 150px;
  margin-bottom: 10px;
}

.banner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 15px;
  background-color: #ffffff;
  margin-bottom: 10px;
}

.function-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.function-item img {
  width: 50px;
  height: 50px;
  margin-bottom: 8px;
  object-fit: contain;
}

.function-item span {
  font-size: 12px;
  color: #333333;
}

.special-section {
  background-color: #ffffff;
  padding: 15px;
  margin-bottom: 10px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #333333;
}

.more {
  font-size: 12px;
  color: #999999;
}

.special-scroll {
  width: 100%;
  overflow-x: auto;
}

.special-list {
  display: inline-flex;
  padding-bottom: 10px;
}

.special-item {
  margin-right: 10px;
  width: 100px;
  flex-shrink: 0;
}

.special-item img {
  width: 100px;
  height: 100px;
  border-radius: 6px;
  margin-bottom: 6px;
  object-fit: cover;
}

.special-item .name {
  font-size: 12px;
  color: #333333;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.special-item .price {
  font-size: 14px;
  color: #ff6b6b;
  font-weight: bold;
}

.goods-section {
  background-color: #ffffff;
}

.filter-bar {
  display: flex;
  padding: 10px 15px;
  border-bottom: 1px solid #f5f5f5;
}

.filter-item {
  margin-right: 20px;
  font-size: 14px;
  color: #666666;
}

.filter-item.active {
  color: #ff6b6b;
  font-weight: bold;
}

.goods-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 10px;
}

.goods-item {
  background-color: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.goods-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.goods-item .info {
  padding: 8px;
}

.goods-item .name {
  font-size: 14px;
  color: #333333;
  margin-bottom: 6px;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.goods-item .price {
  font-size: 16px;
  color: #ff6b6b;
  font-weight: bold;
  margin-bottom: 6px;
  display: block;
}
</style>

