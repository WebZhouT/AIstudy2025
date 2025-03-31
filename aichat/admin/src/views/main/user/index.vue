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

import {
  getAllUsers,/* 获取全部用户表的信息 */
  getUserById,/* 获取单个用户表的详细信息 */
  addUser,/* 增加一个用户表记录 */
  updateUser,/* 更新一个用户表记录 */
  deleteUserById,/* 删除一个用户表记录 */
} from '@/api/user.js';

//获取路由器对象
let router = useRouter();
// 弹框显示和隐藏
const _show = ref({
  create: false,/* 弹窗显示和隐藏 */
  type: '',/* add 代表添加 edit 代表编辑 */
})
/* 搜索的表单信息 */
const searchform = reactive({

})
/* 修改和添加的表单信息 */
const form = ref()
//组件挂载完毕
onMounted(() => {
  getList();
});
/* 存储数据列表 */
const list = ref([])
/* 分页数据 */
const page = reactive({
  limit: 10,/* 每页显示条数 */
  total: 0,/* 总条数 */
  page: 1,/* 当前页数 */
})
/* 获取用户登录的token */
let userdata = ref(localStorage.getItem('userdata'))
/* 初始化表单 */
const initForm = () => {
  form.value = {
    username: '',/*用户名*/
    password: '',/*密码*/
    sex: '',/*性别*/
    email: '',/*邮箱*/
    mobile: '',/*手机号*/
    intro: ''/*个人介绍*/
  }
}
//调用
const getList = () => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: 'Loading',
    background: 'rgba(0, 0, 0, 0.7)'
  });
  getAllUsers({ ...searchform, ...page }).then((res) => {
    console.log(res);
    list.value = res.data.data;
    page.total = res.data.total;
    loadingInstance.close()
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
      deleteUserById(row.id).then((res) => {
        console.log(res);
        if (res.code == '000') {
          loadingInstance.close()
          ElMessage.success('删除成功')
          getList();
        }
      })
    })
}
// 重置表单
const resetSearchForm = () => {
  Object.keys(searchform).forEach(key => {
    searchform[key] = '';
  });
  // 重置分页参数
  page.value.page = 1;
  page.value.limit = 10;

  searchform.limit = 10;
  // 重新获取列表数据
  getList();
};
// 编辑
const edit = (item) => {
  getUserById(item).then((res) => {
    console.log(res)
    form.value = res.data;
    _show.value.create = true;
    _show.value.type = 'edit'
  })
};
/* 页数变更 */
const handleCurrentChange = (val) => {
  page.page = val;
  getList();
}


</script>
<template>
  <div class='container'>

    <el-table :data="list" stripe>
      <el-table-column label="Id" prop="id"
                       width="55"
                       align="center"></el-table-column>
      <el-table-column label="用户名"
                       prop="username">
      </el-table-column>
      <el-table-column label="性别" prop="sex">
        <template #default="row">
          {{row.row.sex==1?'男':'女'}}
        </template>
      </el-table-column>
      <el-table-column label="邮箱" prop="email">
      </el-table-column>
      <el-table-column label="手机号" prop="mobile">
      </el-table-column>
      <el-table-column label="操作" align="center"
                       fixed="right" width="180">
        <template #default="row">
          <el-button type="primary" size="small"
                     @click="edit(row.row)">修改</el-button>
          <el-button type="danger" size="small"
                     @click="remove(row.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination background
                   layout="prev, pager, next"
                   :total="page.total"
                   :default-page-size="page.limit"
                   page-size="10"
                   hide-on-single-page="false"
                   @current-change="handleCurrentChange" />

    <!-- 弹框修改 -->
    <el-dialog :title="_show.type=='add'?'添加':_show.type=='detail'?'详情':'修改'"
               width="600px" destroy-on-close
               lock-scroll v-model="_show.create"
               align-center="true">
      <ListTable :data="form"
                 @confirm="_show.create = false; getList()"
                 @cancel="_show.create = false" />
    </el-dialog>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>