<template>
  <div class="welcome-menu-container">
    <!-- <h2>欢迎，{{ username }}</h2> -->
    <div class="menu-grid">
      <el-card
        v-for="item in menuCards"
        :key="item.path"
        class="menu-card"
        shadow="hover"
        @click="goPage(item.path)"
      >
        <div class="menu-card-title">{{ item.name }}</div>
        <div class="menu-card-path">{{ item.path }}</div>
      </el-card>
    </div>
    <el-button type="danger" @click="logout" style="margin-top:32px">退出登录</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
const username = ref('')
const menuCards = ref<{ name: string; path: string }[]>([])
const router = useRouter()

const fetchMenus = async () => {
  const res = await axios.get('/api/menus/', { withCredentials: true })
  // 扁平化所有有path的菜单
  function flatMenus(tree: any[]): { name: string; path: string }[] {
    let arr: { name: string; path: string }[] = []
    for (const m of tree) {
      if (m.path) arr.push({ name: m.name, path: m.path })
      if (m.children && m.children.length) arr = arr.concat(flatMenus(m.children))
    }
    return arr
  }
  menuCards.value = flatMenus(res.data.menus)
}

onMounted(async () => {
  const res = await axios.get('/api/userinfo/', { withCredentials: true })
  username.value = res.data.username
  await fetchMenus()
})
const goPage = (path: string) => {
  router.push(path)
}
const logout = () => {
  document.cookie = 'sessionid=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/'
  router.push('/login')
}
</script>

<style scoped>
.welcome-menu-container {
  min-height: 0;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  background: #f5f6fa;
  padding: 12px 0 0 0;
  box-sizing: border-box;
}
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  justify-content: center;
  margin-top: 32px;
  width: 100%;
  max-width: 90vw;
}
.menu-card {
  width: 220px;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  cursor: pointer;
  transition: box-shadow 0.2s;
  border-radius: 12px;
  font-size: 18px;
  box-sizing: border-box;
}
.menu-card-title {
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 8px;
}
.menu-card-path {
  color: #888;
  font-size: 14px;
}
</style>
