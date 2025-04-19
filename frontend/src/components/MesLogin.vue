<template>
  <div class="login-container">
    <h2>登录</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <input v-model="username" placeholder="用户名" required />
      </div>
      <div>
        <input v-model="password" type="password" placeholder="密码" required />
      </div>
      <div>
        <button type="submit">登录</button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </form>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const getCSRFToken = async () => {
  // 通过 /api/csrf/ 获取 token
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
    router.push('/welcome')
  } catch (e: any) {
    error.value = e.response?.data?.error || '登录失败'
  }
}
</script>
<style scoped>
.login-container {
  max-width: 300px;
  margin: 100px auto;
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
}
.error {
  color: red;
  margin-top: 10px;
}
</style>
