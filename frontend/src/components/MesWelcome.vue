<template>
  <div class="welcome-container">
    <h2>欢迎，{{ username }}</h2>
    <button @click="logout">退出登录</button>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
const username = ref('')
const router = useRouter()
onMounted(async () => {
  const res = await axios.get('/api/userinfo/', { withCredentials: true })
  username.value = res.data.username
})
const logout = () => {
  document.cookie = 'sessionid=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/'
  router.push('/login')
}
</script>
<style scoped>
.welcome-container {
  max-width: 300px;
  margin: 100px auto;
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
  text-align: center;
}
</style>
