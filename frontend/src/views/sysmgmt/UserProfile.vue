<template>
  <div class="user-profile-container">
    <el-card>
      <template #header>
        <div class="profile-header">
          <el-avatar :size="64" :src="form.avatar || ''" />
          <div class="profile-title">个人资料</div>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" class="profile-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            action="#"
          >
            <img v-if="form.avatar" :src="form.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            <div class="upload-text">点击上传头像</div>
          </el-upload>
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" autocomplete="off" placeholder="如需修改请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" autocomplete="off" placeholder="再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="loading">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'
import axios from 'axios'
import { Plus } from '@element-plus/icons-vue'

const userStore = useUserStore()
const user = userStore.user as Partial<{username: string; phone: string; email: string; avatar: string}> || {}
const loading = ref(false)
const formRef = ref()

const form = reactive<Record<string, any>>({
  username: user.username || '',
  phone: user.phone || '',
  email: user.email || '',
  avatar: user.avatar || '',
  password: '',
  confirmPassword: ''
})

let avatarFile: File | null = null

const rules = {
  phone: [
    { required: false, pattern: /^1[3-9]\d{9}$/, message: '请输入有效手机号', trigger: 'blur' }
  ],
  email: [
    { required: false, type: 'email', message: '请输入有效邮箱', trigger: 'blur' }
  ],
  password: [
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: (rule: any, value: string, callback: any) => {
      if (value && value !== form.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ]
}

const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('只能上传图片格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB!')
    return false
  }
  avatarFile = file
  // 预览
  const reader = new FileReader()
  reader.onload = (e) => {
    form.avatar = e.target?.result as string
  }
  reader.readAsDataURL(file)
  return false // 阻止 el-upload 默认上传
}

const onSubmit = async () => {
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('phone', form.phone || '')
      formData.append('email', form.email || '')
      if (form.password) formData.append('password', form.password)
      if (avatarFile) formData.append('avatar', avatarFile)
      // 不要手动设置 Content-Type，让 axios 自动生成
      const res = await axios.post('/api/user/profile/', formData, {
        withCredentials: true
      })
      ElMessage.success('资料修改成功')
      form.avatar = res.data.avatar || ''
      await userStore.getLoginStatus()
      await refreshProfile()
      form.password = ''
      form.confirmPassword = ''
      avatarFile = null
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.error || '保存失败')
    } finally {
      loading.value = false
    }
  })
}

async function refreshProfile() {
  const res = await axios.get('/api/user/profile/', { withCredentials: true })
  form.username = res.data.username
  form.phone = res.data.phone
  form.email = res.data.email
  form.avatar = res.data.avatar
}

onMounted(() => {
  refreshProfile()
})
</script>

<style scoped>
.user-profile-container {
  max-width: 480px;
  margin: 32px auto;
}
.profile-header {
  display: flex;
  align-items: center;
  gap: 18px;
}
.profile-title {
  font-size: 22px;
  font-weight: bold;
}
.profile-form {
  margin-top: 18px;
}
.avatar-uploader {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  width: 96px;
  height: 96px;
  justify-content: center;
  margin-bottom: 8px;
}
.avatar-uploader-icon {
  font-size: 32px;
  color: #8c939d;
}
.upload-text {
  font-size: 14px;
  color: #888;
  margin-top: 4px;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: block;
}
</style> 