<template>
  <el-dialog :model-value="visible" :title="title" width="580px" @update:model-value="$emit('update:visible', $event)"
    @closed="onDialogClosed" @opened="$emit('opened')" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="left">
      <el-form-item label="客户名称" prop="name">
        <el-input v-model="form.name" maxlength="50" show-word-limit />
      </el-form-item>
      <el-form-item label="客户代码" prop="code">
        <el-input v-model="form.code" maxlength="20" show-word-limit />
      </el-form-item>
      <el-form-item label="地址" prop="address">
        <el-input v-model="form.address" maxlength="200" />
      </el-form-item>
      <el-form-item label="联系人" prop="contact">
        <el-input v-model="form.contact" maxlength="50" />
      </el-form-item>
      <el-form-item label="联系电话" prop="phone">
        <el-input v-model="form.phone" maxlength="20" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSave">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type { CompanyForm } from '../../types'

// 定义属性
const props = defineProps<{
  visible: boolean
  title: string
  form: CompanyForm
  rules: Record<string, any>
  loading: boolean
}>()

// 定义事件
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'opened'): void
}>()

// 表单引用
const formRef = ref<FormInstance>()

// 保存处理
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      emit('save')
    }
  })
}

// 关闭对话框处理
const onDialogClosed = () => {
  emit('close')
}
</script>

<style lang="scss" scoped>
.el-form-item {
  margin-bottom: 20px;
}
</style>
