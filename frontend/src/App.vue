<template>
  <el-config-provider :locale="zhCn">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </transition>
    </router-view>

    <!-- 全局加载组件 -->
    <div v-if="loading" class="global-loading">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <div class="loading-text">加载中...</div>
    </div>
  </el-config-provider>
</template>

<script lang="ts" setup>
import { provide, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { Loading } from '@element-plus/icons-vue'
import { useUserStore } from './stores/user'

// 全局加载状态
const loading = ref(false)

// 提供全局加载状态控制
provide('showLoading', () => {
  loading.value = true
})

provide('hideLoading', () => {
  loading.value = false
})

// 获取store和router
const userStore = useUserStore()
const router = useRouter()

// 应用初始化
onMounted(async () => {
  // 从本地存储初始化用户
  userStore.initFromStorage()
  
  // 如果有token但没有用户信息，尝试获取用户信息
  if (userStore.isAuthenticated && !userStore.user) {
    const success = await userStore.getLoginStatus()
    if (!success) {
      // 获取用户信息失败，可能是token过期
      userStore.logout()
      router.push('/login')
    }
  }
  
  // 添加全局错误处理
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    // 可以在这里添加全局错误处理逻辑，比如显示全局错误提示
  })
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', SimSun, sans-serif;
}

#app {
  height: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-icon {
  font-size: 40px;
  color: var(--el-color-primary);
  animation: rotate 1.5s linear infinite;
}

.loading-text {
  margin-top: 16px;
  color: var(--el-color-primary);
  font-size: 16px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
