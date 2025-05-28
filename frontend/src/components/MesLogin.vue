<template>
  <div class="login-bg">
    <div class="login-panel">
      <div class="login-title">
        <img src="/logo.svg" class="login-logo" />
        <span>XMes 智能制造执行系统</span>
      </div>
      <el-form @submit.prevent="handleLogin" class="login-form">
        <el-form-item>
          <el-input v-model="username" placeholder="用户名" size="large" prefix-icon="User" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="密码" size="large" prefix-icon="Lock" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" native-type="submit">登 录</el-button>
        </el-form-item>
        <div v-if="error" class="error">{{ error }}</div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const getCSRFToken = async () => {
  const res = await axios.get('/api/csrf/', { withCredentials: true })
  return res.data.csrftoken
}
const handleLogin = async () => {
  error.value = ''
  try {
    const csrftoken = await getCSRFToken()
    await axios.post('/api/login/', {
      username: username.value,
      password: password.value
    }, {
      withCredentials: true,
      headers: { 'X-CSRFToken': csrftoken }
    })
    ElMessage.success('登录成功')
    router.push('/welcome')
  } catch (e: unknown) {
    error.value = (typeof e === 'object' && e && 'response' in e) ? (e as any).response?.data?.error || '登录失败' : '登录失败'
  }
}
</script>

<style scoped>
.login-bg {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  min-width: 0;
  min-height: 0;
  background: url('../assets/background.png') no-repeat center center fixed;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  z-index: 10;
}
.login-panel {
  background: rgba(80, 140, 230, 0.72); /* 更淡的蓝色半透明 */
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14);
  padding: 48px 36px 32px 36px;
  min-width: 320px;
  max-width: 360px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.login-title {
  display: flex;
  align-items: center;
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 32px;
  color: #f7faff; /* 更浅的白蓝色 */
}
.login-logo {
  width: 40px;
  height: 40px;
  margin-right: 12px;
}
.login-form {
  width: 260px;
}
:deep(.el-input__wrapper),
:deep(.el-input__inner),
:deep(.el-input input) {
  color: #fff !important;           /* 输入文字为白色 */
  background: transparent !important;
  caret-color: #fff !important;
}
:deep(.el-input__inner::placeholder),
:deep(.el-input input::placeholder) {
  color: #e0eaff !important;        /* placeholder 也为浅蓝白色 */
  opacity: 1 !important;
}
.el-button--primary {
  background: linear-gradient(90deg, #4f8cff 0%, #3578e5 100%);
  border: none;
  color: #fff;
}
.el-button--primary:hover {
  background: linear-gradient(90deg, #3578e5 0%, #4f8cff 100%);
}
.error {
  color: #f56c6c;
  margin-top: 10px;
  text-align: center;
}
</style>
