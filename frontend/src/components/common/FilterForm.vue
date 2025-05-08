<template>
  <div class="filter-form">
    <el-form
      ref="filterFormRef"
      :model="formModel"
      :inline="true"
      class="filter-container"
      size="default"
    >
      <!-- Main slot for filter items -->
      <slot></slot>
      
      <!-- Filter action buttons -->
      <div class="filter-actions">
        <el-button
          type="primary"
          :loading="props.loading"
          @click="handleApplyFilter"
        >
          <el-icon v-if="!props.loading"><Search /></el-icon>
          <span>查询</span>
        </el-button>
        
        <el-button
          @click="handleReset"
          :disabled="props.loading"
        >
          <el-icon><Refresh /></el-icon>
          <span>重置</span>
        </el-button>
        
        <slot name="actions"></slot>
      </div>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, watch, onMounted } from 'vue';
import { Search, Refresh } from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';

interface FilterFormProps {
  initialValues?: Record<string, any>;
  loading?: boolean;
  dateFormat?: string;
  persistKey?: string; // 用于本地存储的key
}

const props = withDefaults(defineProps<FilterFormProps>(), {
  initialValues: () => ({}),
  loading: false,
  dateFormat: 'YYYY-MM-DD',
  persistKey: ''
});

const emit = defineEmits<{
  (e: 'filter', values: Record<string, any>): void;
  (e: 'reset'): void;
}>();

// 表单引用
const filterFormRef = ref<FormInstance | null>(null);

// 动态表单模型
const formModel = reactive<Record<string, any>>({
  ...props.initialValues
});

// 监听初始值变化
watch(() => props.initialValues, (newValues) => {
  Object.keys(newValues).forEach(key => {
    formModel[key] = newValues[key];
  });
}, { deep: true });

// 应用过滤器
function handleApplyFilter(): void {
  // 清理空值
  const cleanValues: Record<string, any> = {};
  
  Object.keys(formModel).forEach(key => {
    const value = formModel[key];
    if (value !== null && value !== undefined && value !== '') {
      cleanValues[key] = value;
    }
  });
  
  // 保存到本地存储
  if (props.persistKey) {
    localStorage.setItem(`filter_${props.persistKey}`, JSON.stringify(cleanValues));
  }
  
  emit('filter', cleanValues);
}

// 重置过滤器
function handleReset(): void {
  // 清空表单
  filterFormRef.value?.resetFields();
  
  // 重置为初始值
  Object.keys(formModel).forEach(key => {
    formModel[key] = props.initialValues[key] || null;
  });
  
  // 清除本地存储
  if (props.persistKey) {
    localStorage.removeItem(`filter_${props.persistKey}`);
  }
  
  emit('reset');
}

// 从本地存储中恢复过滤器状态
onMounted(() => {
  if (props.persistKey) {
    try {
      const savedFilter = localStorage.getItem(`filter_${props.persistKey}`);
      if (savedFilter) {
        const parsedFilter = JSON.parse(savedFilter);
        Object.keys(parsedFilter).forEach(key => {
          formModel[key] = parsedFilter[key];
        });
      }
    } catch (e) {
      console.error('恢复过滤器状态失败:', e);
    }
  }
});

// 暴露给父组件的方法
defineExpose({
  applyFilter: handleApplyFilter,
  resetFilter: handleReset,
  getFilterValues: () => ({ ...formModel })
});
</script>

<style scoped>
.filter-form {
  margin-bottom: 16px;
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

:deep(.el-form-item) {
  margin-bottom: 10px;
  margin-right: 16px;
}

:deep(.el-date-editor),
:deep(.el-select),
:deep(.el-input) {
  width: 220px;
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 12px;
    width: 100%;
    justify-content: flex-end;
  }
  
  :deep(.el-form-item) {
    margin-right: 0;
    width: 100%;
  }
  
  :deep(.el-date-editor),
  :deep(.el-select),
  :deep(.el-input) {
    width: 100%;
  }
}
</style> 