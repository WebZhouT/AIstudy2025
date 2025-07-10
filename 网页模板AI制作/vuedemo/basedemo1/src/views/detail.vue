<!--  -->
<script setup>
import { useRouter, useRoute } from 'vue-router';
import { watch, onMounted, ref, reactive } from 'vue';
//获取路由器对象
let router = useRouter();
const route = useRoute()
// 监听路由参数变化
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      loadData(newId)
    }
  }
)
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
  },
  {
    id: 5,
    title: '五一劳动节健康跑',
    time: '5月1日 07:00-10:00',
    location: '城市公园',
    desc: '健康跑步活动，倡导健康生活方式',
    image: 'https://ai-public.mastergo.com/ai/img_res/2dd72b7447452948f81f02f65613a6b2.jpg',
    detail: '5公里健康跑活动，路线环绕城市公园。活动旨在倡导健康生活方式，弘扬劳动精神。完赛者可获得纪念奖牌。',
    joinMethod: '提前通过运动APP报名',
    notice: '请穿着运动服装，注意安全',
    participants: 300
  },
  {
    id: 6,
    title: '劳动者摄影展',
    time: '5月1日-5月7日 09:00-18:00',
    location: '艺术馆',
    desc: '记录劳动者美丽瞬间的摄影作品展',
    image: 'https://ai-public.mastergo.com/ai/img_res/a28f0c994d2380a89a746c2d5caae1d9.jpg',
    detail: '展出由专业摄影师和业余爱好者拍摄的劳动者主题摄影作品。作品展现了各行各业劳动者的工作场景和精神风貌。',
    joinMethod: '免费参观，无需预约',
    notice: '请勿使用闪光灯拍照',
    participants: 150
  }
]);
// 当前活动详情
const currentActivity = ref(null);
// 相关活动推荐
const relatedActivities = ref([]);
//组件挂载完毕
onMounted(() => {
  // 获取地址栏id
  loadData(route.params.id)

});
const loadData = async (id) => {
  relatedActivities.value = [
    activities.value[1],
    activities.value[2],
    activities.value[3],
  ]

  console.log(id)
  currentActivity.value = activities.value.filter((ele) => {
    return ele.id == id;
  })[0];
}
const goToDetail = (item) => {

  router.push('/detail/' + item.id)
}
</script>
<template>
  <div class=''>

    <div class="detail-scroll"
         v-if="currentActivity">
      <!-- 顶部大图 -->
      <img :src="currentActivity.image"
           class="detail-image" />

      <!-- 活动信息 -->
      <div class="detail-info">
        <h1 class="detail-title">
          {{ currentActivity.title }}</h1>
        <div class="detail-meta">
          <div class="meta-item">
            <i class="fas fa-calendar"></i>
            <span>{{ currentActivity.time }}</span>
          </div>
          <div class="meta-item">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ currentActivity.location }}</span>
          </div>
        </div>

        <div class="detail-section">
          <h2 class="section-title">活动详情</h2>
          <p class="section-content">
            {{ currentActivity.detail }}</p>
        </div>

        <div class="detail-section">
          <h2 class="section-title">参与方式</h2>
          <p class="section-content">
            {{ currentActivity.joinMethod }}</p>
        </div>

        <div class="detail-section">
          <h2 class="section-title">注意事项</h2>
          <p class="section-content">
            {{ currentActivity.notice }}</p>
        </div>
      </div>

      <!-- 相关推荐 -->
      <div class="related-activities">
        <h2 class="related-title">相关推荐</h2>
        <div class="related-scroll">
          <div v-for="(item, index) in relatedActivities"
               :key="index" class="related-item"
               @click="goToDetail(item)">
            <img :src="item.image"
                 class="related-image" />
            <p class="related-name">
              {{ item.title }}</p>
          </div>
        </div>
      </div>
    </div>
    <!-- 底部按钮 -->
    <div class="detail-footer">
      <router-link to="/sort" class="share-btn">
        <i class="fas fa-share"></i>
        <span>返回</span>
      </router-link>
      <button class="join-btn">立即报名</button>
    </div>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>