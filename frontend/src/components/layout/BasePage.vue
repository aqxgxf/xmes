<template>
  <div class="base-page">
    <!-- Page header with title and actions slot -->
    <PageHeader :title="title" :subtitle="subtitle">
      <template #actions>
        <slot name="page-actions"></slot>
      </template>
    </PageHeader>

    <!-- Error messages -->
    <ErrorMessage :error="error" />

    <!-- Main content with overlay for loading state -->
    <div class="page-content" :class="{ 'has-table': hasTable }">
      <LoadingOverlay :loading="loading" :text="loadingText" />
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PageHeader from '../common/PageHeader.vue'
import ErrorMessage from '../common/ErrorMessage.vue'
import LoadingOverlay from '../common/LoadingOverlay.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
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
  hasTable: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.base-page {
  padding: 24px;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.page-content {
  flex: 1;
  position: relative;
  background-color: #fff;
  border-radius: 4px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.page-content.has-table {
  padding: 0;
  overflow: hidden;
}
</style> 