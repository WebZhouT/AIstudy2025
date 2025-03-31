<!--  -->
<script setup>

import { useRouter } from 'vue-router';
import { onMounted, ref, reactive, defineProps, defineEmits, defineAsyncComponent } from 'vue';
const UploadWord = defineAsyncComponent(() => import("@/components/UploadWord.vue"))
import {
  ElMessage,
  ElLoading,
  ElMessageBox
} from 'element-plus'

import {
  getAllUsers,/* 获取全部用户表的信息 */
  getUserById,/* 获取单个用户表的详细信息 */
  addUser,/* 增加一个用户表记录 */
  updateUser,/* 更新一个用户表记录 */
  deleteUserById,/* 删除一个用户表记录 */
} from '@/api/user.js';

const props = defineProps(["data"])
const data = ref({ ...props.data })
const emits = defineEmits(['confirm']);
// 绑定表格标签
const formRef = ref(null);
//获取路由器对象
let router = useRouter();
const rules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' }
  ],
  sex: [
    { required: true, message: '性别不能为空', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' }
  ],
  mobile: [
    { required: true, message: '手机号不能为空', trigger: 'blur' }
  ],
  intro: [
    { required: true, message: '个人介绍不能为空', trigger: 'blur' }
  ]
};
// 渲染分类下拉列表
const classifyList = ref([])
//组件挂载完毕
onMounted(() => {
});
const define = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      const loadingInstance = ElLoading.service({
        lock: true,
        text: 'Loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      console.log(data.value)
      if (data.value.id > 0) {
        // 编辑
        updateUser(data.value).then((res) => {
          console.log(res)
          if (res.code == '000') {
            ElMessage.success('修改成功')
            emits('confirm')
          }
          loadingInstance.close()
        }).catch((err) => {
          loadingInstance.close()
        })
      } else {
        // 添加
        addUser(data.value).then((res) => {
          console.log(res)
          if (res.code == '000') {
            ElMessage.success('提交成功')
            router.push('/user/list')
          }
          loadingInstance.close()
        }).catch((err) => {
          loadingInstance.close()
        })
      }
    }
  });

}

</script>
<template>
  <div class=''>
    <!-- 添加和编辑template -->
    <div class=''>
      <el-form :model="data" :rules="rules"
               ref="formRef" label-width="120px"
               status-icon>
        <!-- 用户名 -->
        <el-form-item prop="username" label="用户名"
                      required><el-input
                    v-model="data.username" /></el-form-item>
        <!-- 密码 -->
        <el-form-item prop="password" label="密码"
                      required><el-input
                    type="password"
                    v-model="data.password" /></el-form-item>
        <!-- 性别 -->
        <el-form-item prop="sex" label="性别"
                      required>
          <el-select name="" id=""
                     v-model="data.sex">
            <el-option :value="1"
                       label="男"></el-option>
            <el-option :value="2"
                       label="女"></el-option>
          </el-select>
        </el-form-item>
        <!-- 邮箱 -->
        <el-form-item prop="email" label="邮箱"
                      required><el-input
                    v-model="data.email" /></el-form-item>

        <!-- 手机号 -->
        <el-form-item prop="mobile" label="手机号"
                      required><el-input
                    v-model="data.mobile" /></el-form-item>
        <!-- 个人介绍 -->
        <el-form-item prop="intro" label="个人介绍"
                      required><el-input
                    v-model="data.intro"
                    type="textarea"
                    rows="10" /></el-form-item>
        <el-form-item label=""
                      class="right_postion">
          <el-button type="primary"
                     @click="define">确定</el-button>
          <el-button
                     @click="$emit('cancel')">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style lang='less' scoped>
//@import url(); 引入公共css类
</style>