<template>
  <div class="login-bg">
    <div class="login-panel">
      <div class="login-title">
        <img src="/vite.svg" class="login-logo" />
        <span>xMes 智能制造执行系统</span>
      </div>
      <el-form @submit.prevent="handleLogin" class="login-form">
        <el-form-item>
          <el-input v-model="username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="密码" size="large" prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" @click="handleLogin">登 录</el-button>
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
  background: linear-gradient(120deg, #4f8cff 0%, #6ed0f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  z-index: 10;
}
.login-panel {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
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
  color: #4f8cff;
}
.login-logo {
  width: 40px;
  height: 40px;
  margin-right: 12px;
}
.login-form {
  width: 260px;
}
.error {
  color: #f56c6c;
  margin-top: 10px;
  text-align: center;
}
</style>
