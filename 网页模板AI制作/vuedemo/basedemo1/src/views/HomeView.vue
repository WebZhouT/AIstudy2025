

<template>
  <div class="container">
    <!-- Banner -->
    <div class="banner">
      <img src="https://ai-public.mastergo.com/ai/img_res/5ab7ce9e2c71c306d646e96016ba4778.jpg"
           class="banner-image" />
      <div class="banner-text">
        <h1 class="banner-title">致敬劳动者</h1>
        <p class="banner-subtitle">五一劳动节快乐</p>
      </div>
    </div>

    <!-- 活动卡片 -->
    <div class="activity-grid">
      <div v-for="(item, index) in activities"
           :key="index" class="activity-card"
           @click="goToDetail(item)">
        <img :src="item.image"
             class="card-image" />
        <div class="card-content">
          <h3 class="card-title">{{ item.title }}
          </h3>
          <p class="card-time">{{ item.time }}</p>
          <p class="card-desc">{{ item.desc }}</p>
        </div>
      </div>
    </div>
    <footers />
  </div>
</template>

<script  setup>
import { onMounted, ref, reactive } from 'vue';
import footers from "@/components/footers.vue";
import { useRouter } from 'vue-router';
//获取路由器对象
let router = useRouter();
// 活动数据
const activities = ref([
  {
    id: 1,
    title: '五一劳动技能大赛',
    time: '5月1日 09:00-17:00',
    location: '市民广场',
    desc: '展示你的劳动技能，赢取丰厚奖品',
    image: 'https://ai-public.mastergo.com/ai/img_res/e514989a385c81a2a74ed5b5c559526c.jpg',
    detail: '本次活动设有多个劳动技能比赛项目，包括木工、电工、园艺等。参赛者将有机会展示自己的专业技能，并获得专家点评。比赛设有一、二、三等奖及优秀奖若干。',
    joinMethod: '现场报名或提前通过微信公众号预约',
    notice: '请参赛者自备基本工具，注意安全操作',
    participants: 120
  },
  {
    id: 2,
    title: '劳动者文艺汇演',
    time: '5月1日 19:00-21:00',
    location: '文化宫大剧院',
    desc: '精彩纷呈的文艺表演，展现劳动者风采',
    image: 'https://ai-public.mastergo.com/ai/img_res/7bf5031e796cb9274e99b5dc405cfea8.jpg',
    detail: '由各行业劳动者组成的文艺团队将为大家带来歌舞、小品、戏曲等丰富多彩的节目。演出内容包括歌颂劳动精神、展现行业特色等主题。',
    joinMethod: '凭邀请函入场或现场购票',
    notice: '请提前15分钟入场，演出期间请保持安静',
    participants: 80
  },
  {
    id: 3,
    title: '劳动模范事迹展',
    time: '5月1日-5月3日 08:30-17:30',
    location: '工人文化宫',
    desc: '学习劳动模范先进事迹，弘扬劳模精神',
    image: 'https://ai-public.mastergo.com/ai/img_res/83a68e6b560e1c9d9daced11f1e4f037.jpg',
    detail: '展览通过图片、文字、视频等形式，全面展示近年来各行业劳动模范的先进事迹和工作成果。展览分为工业、农业、服务业等多个板块。',
    joinMethod: '免费参观，无需预约',
    notice: '请文明参观，勿触摸展品',
    participants: 200
  },
  {
    id: 4,
    title: '亲子劳动体验营',
    time: '5月2日 10:00-16:00',
    location: '青少年活动中心',
    desc: '家长与孩子一起体验劳动的快乐',
    image: 'https://ai-public.mastergo.com/ai/img_res/898c2cd2535e5959fcca2e6bc1bf485f.jpg',
    detail: '活动设置多个劳动体验项目，包括种植、手工制作、简单维修等。通过亲子共同劳动，培养孩子的动手能力和劳动意识。',
    joinMethod: '提前通过微信公众号预约',
    notice: '建议穿着舒适服装，自备饮用水',
    participants: 50
  }
]);
const goToDetail = (item) => {
  router.push('/detail/' + item.id)
}
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

