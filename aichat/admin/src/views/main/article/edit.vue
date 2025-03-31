<!--  -->
<script setup>

import { useRouter } from 'vue-router';
import { onMounted, ref, reactive, defineProps, defineEmits, defineAsyncComponent } from 'vue';
import {
  ElMessage,
  ElLoading,
  ElMessageBox
} from 'element-plus'
import axios from 'axios';
import moment from 'moment'
const props = defineProps(["data"])
const data = ref({ ...props.data })
const emits = defineEmits(['confirm']);
// 绑定表格标签
const formRef = ref(null);
const uploadData = ref({});
const rules = {
  newsname: [
    { required: true, message: '资讯标题不能为空', trigger: 'blur' }
  ],
  newsdesc: [
    { required: true, message: '资讯描述不能为空', trigger: 'blur' }
  ],
  sort_id: [
    { required: true, message: '资讯分类id不能为空', trigger: 'blur' }
  ],
  addtimes: [
    { required: true, message: '发布时间不能为空', trigger: 'blur' }
  ],
  picture: [
    { required: true, message: '图片不能为空', trigger: 'blur' }
  ]
};
// 渲染分类下拉列表
const classifyList = ref([])
//组件挂载完毕
onMounted(() => {
  axios.get('/api/sorts').then((res) => {
    console.log(res)
    classifyList.value = res.data.data.map((ele) => {
      return {
        label: ele.sortname,
        value: ele.id,
      }
    });
  })
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
        axios.put('/api/articles/' + data.value.id, data.value).then((res) => {
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
        data.value.addtimes = moment(new Date()).format('YYYY-MM-DD HH:mm:ss');
        // 添加
        axios.post('/api/articles', data.value).then((res) => {
          console.log(res)
          if (res.data.code == 0) {
            ElMessage.success('提交成功')
            emits('confirm')
          }
          loadingInstance.close()
        }).catch((err) => {
          loadingInstance.close()
        })
      }
    }
  });

}
/* 提交图片前验证 */
const beforeAvatarUpload = (rawFile) => {
  console.log(rawFile)
  if (rawFile.raw.type !== 'image/jpeg' && rawFile.raw.type !== 'image/png' && rawFile.raw.type !== 'image/webp') {
    ElMessage.error('文件格式有误请重新上传')
    return false
  } else if (rawFile.raw.size / 1024 / 1024 > 2) {
    ElMessage.error('文件大小需要小于 2MB!')
    return false
  } else {
    if (rawFile.raw) {
      // 创建 FormData 对象
      const formData = new FormData();
      // 添加文件对象
      formData.append('file', rawFile.raw);
      axios({
        url: '/api/upLoad',
        method: 'post',
        headers: {
          'content-type': 'application/x-www-form-urlencoded'
        },
        data: formData
      }).then((res) => {
        console.log(res)
        data.value.picture = res.data.data.file;
        console.log(data.value.picture)
      })
    }
  }

};

</script>
<template>
  <div class=''>
    <!-- 添加和编辑template -->
    <div class=''>
      <el-form :model="data" :rules="rules"
               ref="formRef" label-width="120px"
               status-icon>
        <!-- 资讯标题 -->
        <el-form-item prop="newsname" label="资讯标题"
                      required>
          <el-input v-model="data.newsname" />
        </el-form-item>
        <!-- 资讯描述 -->
        <el-form-item prop="newsdesc" label="资讯描述"
                      required>
          <el-input v-model="data.newsdesc"
                    type="textarea" rows="10" />
        </el-form-item>
        <!-- 资讯分类id -->
        <el-form-item prop="sort_id" label="资讯分类"
                      required>
          <el-select v-model="data.sort_id"
                     placeholder="请选择分类">
            <template v-for="(item,i) in classifyList"
                      :key="i">
              <el-option :label="item.label"
                         :value="item.value"></el-option>
            </template>
          </el-select>

        </el-form-item>
        <el-form-item label="选择主图" prop="picture"
                      required>
          <el-upload :limit="1"
                     :auto-upload="false"
                     :data="uploadData"
                     class="avatar-uploader"
                     :show-file-list="false"
                     :on-change="beforeAvatarUpload">
            <el-image v-if="data.picture"
                      style="width: 160px; height:160px;object-fit:cover;"
                      :src="'/api/uploads/'+data.picture"
                      fit="contain"
                      class="avatar" />
            <el-icon v-else
                     class="avatar-uploader-icon">
              <Plus />
            </el-icon>
          </el-upload>
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
.avatar-uploader {
  width: 148px;
  height: 148px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 148px;
  height: 148px;
  line-height: 148px;
  text-align: center;
}

.avatar {
  width: 148px;
  height: 148px;
  display: block;
}
</style>