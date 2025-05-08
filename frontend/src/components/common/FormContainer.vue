<template>
  <div class="form-container">
    <el-form
      ref="formRef"
      :model="modelValue"
      :rules="rules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      :disabled="disabled || loading"
      :validate-on-rule-change="validateOnRuleChange"
      :scroll-to-error="scrollToError"
      :status-icon="statusIcon"
      :size="size"
    >
      <slot></slot>
      
      <div v-if="showActions" class="form-actions">
        <div class="form-actions-left">
          <slot name="actions-left"></slot>
        </div>
        <div class="form-actions-right">
          <slot name="actions">
            <el-button :disabled="loading || disabled" @click="handleReset">{{ resetText }}</el-button>
            <el-button :loading="loading" type="primary" @click="handleSubmit">{{ submitText }}</el-button>
          </slot>
        </div>
      </div>
    </el-form>
    
    <div v-if="error" class="form-error">
      <el-alert :title="error" type="error" :closable="true" @close="clearError" />
    </div>
    
    <div v-if="loading" class="form-overlay">
      <el-icon class="is-loading"><Loading /></el-icon>
      <div class="loading-text">{{ loadingText }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, defineEmits, defineProps, defineExpose, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  rules: {
    type: Object as () => FormRules,
    default: () => ({})
  },
  labelWidth: {
    type: String,
    default: '100px'
  },
  labelPosition: {
    type: String,
    default: 'right'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: '提交中...'
  },
  showActions: {
    type: Boolean,
    default: true
  },
  submitText: {
    type: String,
    default: '提交'
  },
  resetText: {
    type: String,
    default: '重置'
  },
  error: {
    type: String,
    default: ''
  },
  validateOnRuleChange: {
    type: Boolean,
    default: true
  },
  scrollToError: {
    type: Boolean,
    default: true
  },
  statusIcon: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'default'
  }
})

const emit = defineEmits(['submit', 'reset', 'update:modelValue', 'clear-error'])
const formRef = ref<FormInstance>()

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate((valid, fields) => {
      if (valid) {
        emit('submit', props.modelValue)
      } else {
        console.error('Form validation failed:', fields)
        
        // 获取第一个验证失败的字段和错误信息
        if (fields) {
          const firstField = Object.keys(fields)[0]
          const firstError = fields[firstField]?.[0]?.message || '表单验证失败'
          emit('clear-error')
          setTimeout(() => {
            emit('clear-error', firstError)
          }, 0)
        }
      }
    })
  } catch (err) {
    console.error('Form validation error:', err)
  }
}

// 重置表单
const handleReset = () => {
  if (!formRef.value) return
  
  formRef.value.resetFields()
  emit('reset')
}

// 清除错误
const clearError = () => {
  emit('clear-error')
}

// 暴露方法给父组件
defineExpose({
  validate: async () => {
    if (!formRef.value) return false
    return await formRef.value.validate()
  },
  validateField: async (field: string | string[]) => {
    if (!formRef.value) return
    return await formRef.value.validateField(field)
  },
  resetFields: () => {
    if (!formRef.value) return
    formRef.value.resetFields()
  },
  scrollToField: (field: string) => {
    if (!formRef.value) return
    formRef.value.scrollToField(field)
  },
  clearValidate: (fields?: string | string[]) => {
    if (!formRef.value) return
    formRef.value.clearValidate(fields)
  }
})
</script>

<style scoped>
.form-container {
  position: relative;
}

.form-actions {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-actions-left {
  display: flex;
  align-items: center;
}

.form-actions-right {
  display: flex;
  align-items: center;
}

.form-actions .el-button {
  min-width: 90px;
}

.form-actions .el-button + .el-button {
  margin-left: 12px;
}

.form-error {
  margin-top: 16px;
}

.form-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-text {
  margin-top: 12px;
  color: var(--el-color-primary);
}
</style> 