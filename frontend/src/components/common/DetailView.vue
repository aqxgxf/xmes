<template>
  <div class="detail-view-container">
    <!-- Header with title and actions -->
    <div class="detail-header">
      <div class="detail-title">
        <h3>{{ title }}</h3>
        <span v-if="subtitle" class="detail-subtitle">{{ subtitle }}</span>
      </div>
      <div class="detail-actions">
        <slot name="actions"></slot>
      </div>
    </div>
    
    <!-- Loading overlay -->
    <LoadingOverlay :loading="loading" :text="loadingText" />
    
    <!-- Error message -->
    <ErrorMessage :error="error" />
    
    <!-- Content section -->
    <div v-if="data" class="detail-content">
      <el-descriptions :column="column" :size="size" :border="border" :direction="direction" :label-align="labelAlign">
        <slot :data="data"></slot>
      </el-descriptions>
      
      <!-- Extra content (e.g., related tables, charts) -->
      <div v-if="$slots.extra" class="detail-extra">
        <slot name="extra" :data="data"></slot>
      </div>
    </div>
    
    <!-- Empty state -->
    <el-empty v-else-if="!loading && !error" :description="emptyText" />
  </div>
</template>

<script lang="ts" setup>
import LoadingOverlay from './LoadingOverlay.vue'
import ErrorMessage from './ErrorMessage.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  data: {
    type: Object,
    default: undefined
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: '加载中...'
  },
  error: {
    type: String,
    default: undefined
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  },
  column: {
    type: Number,
    default: 3
  },
  size: {
    type: String,
    default: 'default'
  },
  border: {
    type: Boolean,
    default: true
  },
  direction: {
    type: String,
    default: 'horizontal'
  },
  labelAlign: {
    type: String,
    default: 'right'
  }
})
</script>

<style scoped>
.detail-view-container {
  position: relative;
  padding: 24px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.detail-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.detail-subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
  display: block;
}

.detail-content {
  margin-top: 16px;
}

.detail-extra {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px dashed #ebeef5;
}
</style> 