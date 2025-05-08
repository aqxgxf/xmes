<template>
  <div class="page-header">
    <div class="left">
      <h2 class="title">{{ title }}</h2>
      <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
    </div>
    <div class="right">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.title {
  font-size: 22px;
  font-weight: 500;
  color: #303133;
  margin: 0;
  line-height: 1.5;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style> 