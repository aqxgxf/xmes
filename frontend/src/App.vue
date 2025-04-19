<template>
  <el-container style="height: 100vh">
    <!-- 顶部导航栏 -->
    <el-header height="60px" class="header-bar">
      <div class="logo-area">
        <img alt="logo" class="logo" src="/logo.svg" style="height:32px;width:32px;" />
        <span class="logo-title">xMes</span>
      </div>
      <div class="collapse-btn-top" @click="isCollapse = !isCollapse">
        <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
      </div>
      <div class="user-area">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar :size="32" :src="user.avatar" style="margin-right:8px" />
            <span>{{ user.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>
                <el-avatar :size="24" :src="user.avatar" style="margin-right:8px" />
                {{ user.username }}
              </el-dropdown-item>
              <el-dropdown-item @click="editProfile">
                <el-icon><User /></el-icon> 修改个人信息
              </el-dropdown-item>
              <el-dropdown-item divided @click="logout">
                <el-icon><SwitchButton /></el-icon> 注销
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <!-- 左侧栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="aside-bar">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          :collapse="isCollapse"
          background-color="#2d3a4b"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <template v-for="item in menus" :key="item.id">
            <el-sub-menu v-if="item.children && item.children.length" :index="String(item.id)">
              <template #title>
                <span>{{ item.name }}</span>
              </template>
              <template v-for="child in item.children" :key="child.id">
                <el-menu-item v-if="!child.children || !child.children.length" :index="child.path" @click="handleMenuClick(child)">
                  {{ child.name }}
                </el-menu-item>
                <el-sub-menu v-else :index="String(child.id)">
                  <template #title>
                    <span>{{ child.name }}</span>
                  </template>
                  <template v-for="sub in child.children" :key="sub.id">
                    <el-menu-item :index="sub.path" @click="handleMenuClick(sub)">
                      {{ sub.name }}
                    </el-menu-item>
                  </template>
                </el-sub-menu>
              </template>
            </el-sub-menu>
            <el-menu-item v-else :index="item.path" @click="handleMenuClick(item)">
              {{ item.name }}
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, User, SwitchButton, Menu, Setting, Fold, Expand, ElementPlus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
const router = useRouter()
const isCollapse = ref(false)
const activeMenu = ref('1-1')
const user = ref({ username: '', avatar: '', groups: [] })

// 递归类型安全处理children
interface MenuItem {
  id: number;
  name: string;
  path: string;
  parent: number | null;
  groups: string[];
  children?: MenuItem[];
}

const menus = ref<MenuItem[]>([])

const fetchUser = async () => {
  try {
    const res = await axios.get('/api/userinfo/', { withCredentials: true })
    user.value = res.data
  } catch {
    user.value = { username: '', avatar: '', groups: [] }
  }
}

const fetchMenus = async () => {
  try {
    const res = await axios.get('/api/menus/', { withCredentials: true })
    menus.value = res.data.menus
  } catch {
    menus.value = []
  }
}

onMounted(() => {
  fetchUser()
  fetchMenus()
})

const logout = () => {
  document.cookie = 'sessionid=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/'
  user.value = { username: '', avatar: '', groups: [] }
  ElMessage.success('已注销')
  router.push('/login')
}

const editProfile = () => {
  alert('功能开发中...')
}

const handleMenuClick = (item: MenuItem) => {
  if (item.path) router.push(item.path)
}

router.afterEach(() => {
  fetchUser()
})
</script>

<style scoped>
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #2d3a4b;
  color: #fff;
  padding: 0 24px;
}
.logo-area {
  display: flex;
  align-items: center;
}
.logo-title {
  font-size: 22px;
  font-weight: bold;
  margin-left: 10px;
  letter-spacing: 2px;
}
.collapse-btn-top {
  cursor: pointer;
  color: #ffd04b;
}
.user-area {
  display: flex;
  align-items: center;
}
.el-container {
  height: 100vh;
  min-height: 0;
  min-width: 0;
  width: 100vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.el-container > .el-container {
  flex-direction: row;
  flex: 1 1 auto;
  height: 0;
  min-height: 0;
  min-width: 0;
  overflow: hidden;
}

.el-header {
  min-width: 0;
  width: 100%;
  height: 60px;
  box-sizing: border-box;
  flex-shrink: 0;
}

.aside-bar {
  background: #2d3a4b;
  color: #fff;
  position: relative;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.el-main {
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  box-sizing: border-box;
  padding: 24px;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.main-content {
  background: #f5f6fa;
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.el-menu-vertical-demo {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}
</style>
