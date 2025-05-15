<template>
  <el-dialog :model-value="visible" :title="title" width="500px" destroy-on-close @close="handleClose"
    @opened="$emit('opened')">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="left"
      class="form-container">
      <el-form-item label="工序代码" prop="code">
        <el-input v-model="form.code" maxlength="20" show-word-limit class="form-input" />
      </el-form-item>

      <el-form-item label="工序名称" prop="name">
        <el-input v-model="form.name" maxlength="50" show-word-limit class="form-input" />
      </el-form-item>

      <el-form-item label="工序描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit
          class="form-input" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSave">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ProcessForm } from '../../types/common'

// Props
defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: ProcessForm
  rules: Record<string, any>
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'opened'): void
}>()

// Form ref
const formRef = ref<FormInstance>()

// Methods
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return
    emit('save')
  })
}
</script>

<style lang="scss" scoped>
.form-container {
  max-height: 60vh;
  width: 100%;
  overflow-y: auto;
  padding-right: 16px;
}

.form-input {
  width: 100%;
}
</style>
