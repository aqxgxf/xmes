<template>
  <el-dialog :model-value="visible" :title="title" width="600px" destroy-on-close @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" label-position="left">
      <el-form-item label="产品" prop="product">
        <el-select v-model="form.product" filterable placeholder="请选择产品" class="form-input">
          <el-option v-for="product in products" :key="product.id" :label="`${product.name} (${product.code || ''})`"
            :value="product.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="工艺流程代码" prop="process_code">
        <el-select v-model="form.process_code" filterable placeholder="请选择工艺流程代码" class="form-input">
          <el-option v-for="code in processCodes" :key="code.id" :label="`${code.code} (${code.version})`"
            :value="code.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否默认" prop="is_default">
        <el-switch v-model="form.is_default" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" rows="3" placeholder="请输入备注" class="form-input" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ProductProcessCodeForm, Product, ProcessCode } from '../../types/common'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: ProductProcessCodeForm
  rules: Record<string, any>
  products: Product[]
  processCodes: ProcessCode[]
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
}>()

// 表单引用
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
.form-input {
  width: 100%;
}
</style>
