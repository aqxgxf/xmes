<template>
  <div v-if="loading" class="loading-overlay">
    <el-icon class="loading-icon"><Loading /></el-icon>
    <div v-if="text" class="loading-text">{{ text }}</div>
  </div>
</template>

<script lang="ts" setup>
import { Loading } from '@element-plus/icons-vue'

defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: '加载中...'
  }
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
}

.loading-icon {
  font-size: 32px;
  color: var(--el-color-primary);
  animation: rotate 1.5s linear infinite;
}

.loading-text {
  margin-top: 12px;
  color: var(--el-color-primary);
  font-size: 14px;
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