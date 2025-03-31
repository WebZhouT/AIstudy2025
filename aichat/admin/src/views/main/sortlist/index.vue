<!--  -->
<script setup>

import { useRouter } from 'vue-router';
import { onMounted, ref, reactive, defineAsyncComponent } from 'vue';
import {
  ElMessage,
  ElLoading,
  ElMessageBox
} from 'element-plus'
/* 添加的列表 */
const ListTable = defineAsyncComponent(() => import('./userEdit.vue'))
import axios from 'axios';
//获取路由器对象
let router = useRouter();
// 弹框显示和隐藏
const _show = ref({
  create: false,/* 弹窗显示和隐藏 */
  type: '',/* add 代表添加 edit 代表编辑 */
})
/* 修改和添加的表单信息 */
const form = ref()
//组件挂载完毕
onMounted(() => {
  getList();
});
/* 存储数据列表 */
const list = ref([])
/* 获取用户 */
let userdata = ref(localStorage.getItem('userdata'))
/* 初始化表单 */
const initForm = () => {
  form.value = {
    sortname: '',/*板块分类名称*/
    sortdesc: ''/*板块描述信息*/
  }
}
//调用
const getList = () => {
  axios.get('/api/sorts').then((res) => {
    console.log(res.data.data);
    list.value = res.data.data.data;
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
      axios.delete('/api/sorts', row.id).then((res) => {
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
  axios.get('/api/sorts/' + item.id).then((res) => {
    console.log(res)
    form.value = res.data.data;
    _show.value.create = true;
    _show.value.type = 'edit'
  })
}
const add = () => {
  initForm();
  _show.value.create = true;
  _show.value.type = 'add'
}
</script>
<template>
  <div class='container'>
    <div class="content">
      <el-table :data="list" stripe border>
        <el-table-column label="Id" prop="id"
                         width="55"
                         align="center"></el-table-column>
        <el-table-column label="板块分类名称"
                         prop="sortname">
        </el-table-column>
        <el-table-column label="板块描述信息"
                         prop="sortdesc">
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
    </div>

    <!-- 弹框修改 -->
    <el-dialog :title="_show.type=='add'?'添加':_show.type=='detail'?'详情':'修改'"
               width="600px" destroy-on-close
               lock-scroll v-model="_show.create"
               align-center="true">
      <ListTable :data="form"
                 @confirm="_show.create = false; getList(activeName)"
                 @cancel="_show.create = false" />
    </el-dialog>
  </div>
</template>

<style lang='less' scoped>
.content {
  width: 900px;
  margin: 30px auto;
}
</style>