<!--  -->
<script setup>

import { useRouter } from 'vue-router';
import { onMounted, ref, reactive, defineProps, defineEmits, defineAsyncComponent } from 'vue';
import {
  ElMessage,
  ElLoading,
  ElMessageBox
} from 'element-plus'
const props = defineProps(["data"])
const data = ref({ ...props.data })
const emits = defineEmits(['confirm']);
import axios from 'axios';
// 绑定表格标签
const formRef = ref(null);
//获取路由器对象
let router = useRouter();
const rules = {
  sortname: [
    { required: true, message: '板块分类名称不能为空', trigger: 'blur' }
  ],
  sortdesc: [
    { required: true, message: '板块描述信息不能为空', trigger: 'blur' }
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
        axios.put('/api/sorts/' + data.value.id, data.value).then((res) => {
          console.log(res)
          if (res.data.code == 0) {
            ElMessage.success('修改成功')
            emits('confirm')
          }
          loadingInstance.close()
        }).catch((err) => {
          loadingInstance.close()
        })
      } else {
        // 添加
        axios.post('/api/sorts', data.value).then((res) => {
          console.log(res)
          if (res.data.code == 0) {
            ElMessage.success('提交成功')
            router.push('/sort/list')
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
  <div class='container'>
    <!-- 添加和编辑template -->
    <div class='container'>
      <el-form :model="data" :rules="rules"
               ref="formRef" label-width="120px"
               status-icon>
        <!-- 板块分类名称 -->
        <el-form-item prop="sortname"
                      label="板块分类名称" required>
          <el-input v-model="data.sortname" />
        </el-form-item>
        <!-- 板块描述信息 -->
        <el-form-item prop="sortdesc"
                      label="板块描述信息" required>
          <el-input v-model="data.sortdesc" />
        </el-form-item>
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