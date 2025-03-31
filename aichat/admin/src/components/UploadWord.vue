<!-- 
/* 调用示例 */
<UploadWord models="certificate"
            :imgurl="data.fullPath"
            :img="data.head" @success="(item)=>{
            console.log(item)
              data.head = item.filename;/* 存储的图片上传地址 */
              data.fullPath = item.url;/* 显示的图片完整地址 */
            }" />
-->
<template>
  <div>
    <el-upload :class="size + '-uploader'"
               :action="uploadUrl + '/api/village_backend/web/file/upload'"
               :show-file-list="false"
               :data="uploadData"
               :on-success="handleAvatarSuccess"
               :before-upload="beforeAvatarUpload"
               :headers="{'token':userdata}">
      <img v-if="img" :src="imgurl"
           :class="size" />
      <el-icon v-else
               :class="size + '-uploader-icon'">
        <Plus />
      </el-icon>
    </el-upload>

    <el-dialog v-model="dialogVisible">
      <img w-full :src="dialogImageUrl"
           alt="Preview Image" />
    </el-dialog>
  </div>
</template>
<script setup>
import { ElMessage, ElLoading } from 'element-plus'
// import { fa } from "element-plus/es/locale";
import { ref, defineEmits, defineProps } from "vue";
const emits = defineEmits(['success'])
let userdata = ref(localStorage.getItem('userdata'));
import axios from 'axios';
const uploadData = ref({});
const data = {
  // ["Authorization"]: localStorage.getItem('userdata'),
  // "token": "53ff8126f048c0df695dd1c69c4ec9c4"
}
const props = defineProps({
  img: { type: String },
  size: { type: String, default: "avatar" },
  models: { type: String, default: "img" },
  imgurl: { type: String, default: '' }

})
const size = ref(props.size)
const uploadUrl = ""
const handleAvatarSuccess = (res) => {
  emits("success", res)
}
const beforeAvatarUpload = (file) => {
  var img = file.name.substring(file.name.lastIndexOf('.') + 1)
  const suffix = img === 'jpg'
  const suffix2 = img === 'png'
  const suffix3 = img === 'jpeg'
  if (!suffix && !suffix2 && !suffix3) {
    ElMessage.error('只能上传图片!')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  // 创建 FormData 对象
  const formData = new FormData();
  // 添加额外的数据到 formData 对象
  formData.append('type', props.models);
  // 添加文件对象
  formData.append('file', file);
  console.log(formData);
  // 设置 uploadData 以便 el-upload 使用 FormData 提交
  // uploadData.value = formData;
  // return isLt2M;
  const loadingInstance = ElLoading.service({
    lock: true,
    text: 'Loading',
    background: 'rgba(0, 0, 0, 0.7)'
  });
  axios({
    url: uploadUrl + '/api/upLoad',
    method: 'post',
    headers: {
      // 'token': localStorage.getItem('userdata'),
      'content-type': 'application/x-www-form-urlencoded'
    },
    data: formData
  }).then((res) => {
    console.log(res.data)
    emits("success", res.data)
    if (res.data.code == '000') {
      emits("success", res.data.data)
    } else {
      ElMessage({
        showClose: true,
        message: res.data.message,
        type: "warning",
        duration: 3000,
      });
    }
    loadingInstance.close()
  }).catch((err) => {
    console.log(err)
    ElMessage({
      showClose: true,
      message: err.response.data.message.toString(),
      type: "warning",
      duration: 5000,
    });
    loadingInstance.close()
  })
  return false;
}



</script>

<style scoped>
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

.small-uploader {
  width: 48px;
  height: 48px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}

.small-uploader:hover {
  border-color: #409eff;
}

.small-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.small-uploader .el-upload:hover {
  border-color: #409eff;
}

.small-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 48px;
  height: 48px;
  line-height: 48px;
  text-align: center;
}

.small {
  width: 48px;
  height: 48px;
  display: block;
}
</style>