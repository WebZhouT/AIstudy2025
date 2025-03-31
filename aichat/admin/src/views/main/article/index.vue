<!--  -->
<script setup>
import { useRouter } from 'vue-router';
/* 页面头部 */
import headers from '@/components/headers.vue'
import { onMounted, ref, reactive, defineAsyncComponent } from 'vue';
import {
  ElMessage,
  ElLoading,
  ElMessageBox
} from 'element-plus'
/* 添加的列表 */
const ListTable = defineAsyncComponent(() => import('./edit.vue'))
//获取路由器对象
let router = useRouter();
import axios from 'axios';
// 弹框显示和隐藏
const _show = ref({
  create: false,/* 弹窗显示和隐藏 */
  type: '',/* add 代表添加 edit 代表编辑 */
});
/* 修改和添加的表单信息 */
const form = ref({
  newsname: '',/*资讯标题*/
  newsdesc: '',/*资讯描述*/
  sort_id: '',/*资讯分类id*/
  addtimes: '',/*发布时间*/
  picture: ''/*图片*/
});
//组件挂载完毕
onMounted(() => {
  getList();

});
/* 存储数据列表 */
const list = ref([]);

//调用
const getList = () => {
  axios.get('/api/articles').then((res) => {
    console.log(res);
    list.value = res.data.data;
  })
}

// 删除
const remove = (row) => {
  ElMessageBox.confirm(
    '确定要删除吗？',
    '提示'
  )
    .then(() => {
      const loadingInstance = ElLoading.service({
        lock: true,
        text: 'Loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      axios.delete('/api/articles/' + row.id).then((res) => {
        console.log(res);
        if (res.data.code == 0) {
          loadingInstance.close()
          ElMessage.success('删除成功')
          getList();
        }
      }).catch((err) => {
        loadingInstance.close()
      })
    })
}

// 编辑
const edit = (item) => {
  axios.get('/api/articles/' + item.id).then((res) => {
    console.log(res)
    form.value = res.data.data;
    _show.value.create = true;
    _show.value.type = 'edit'
  })
}
const add = () => {
  _show.value.create = true;
  _show.value.type = 'add'
}
</script>
<template>
  <div class=''>
    <!-- 轮播图 -->
    <headers />
    <div class="content">
      <el-row>
        <el-col :span="24" class="text-right">
          <el-button type="success"
                     @click="add()">添加</el-button>
        </el-col>
      </el-row>
      <el-table :data="list" stripe border>
        <el-table-column label="Id" prop="id"
                         width="55"
                         align="center"></el-table-column>
        <el-table-column label="资讯标题"
                         prop="newsname">
        </el-table-column>
        <el-table-column label="资讯图片"
                         prop="pirture">
          <template #default="scope">
            <img :src="'/api/uploads/'+scope.row.picture"
                 width="120" height="120"
                 style="object-fit:contain"
                 alt="">
          </template>
        </el-table-column>
        <el-table-column label="发布时间"
                         prop="addtimes">
        </el-table-column>
        <el-table-column label="操作" align="center"
                         fixed="right"
                         width="180">
          <template #default="row">
            <el-button type="primary" size="small"
                       @click="edit(row.row)">修改</el-button>
            <el-button type="danger" size="small"
                       @click="remove(row.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 弹框修改 -->
      <el-dialog :title="_show.type=='add'?'添加':_show.type=='detail'?'详情':'修改'"
                 width="600px" destroy-on-close
                 lock-scroll
                 v-model="_show.create"
                 align-center="true">
        <ListTable :data="form"
                   @confirm="_show.create = false; getList(activeName)"
                   @cancel="_show.create = false" />
      </el-dialog>
    </div>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
.content {
  width: 900px;
  margin: 30px auto;
}
</style>