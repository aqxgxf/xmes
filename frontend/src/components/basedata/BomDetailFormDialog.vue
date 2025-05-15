<template>
  <el-dialog :model-value="visible" :title="title" width="800px" destroy-on-close @close="handleClose">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" label-position="left">
      <el-form-item label="BOM" prop="bom">
        <el-select v-model="form.bom" filterable placeholder="请选择BOM" class="form-input">
          <el-option v-for="item in boms" :key="item.id"
            :label="`${item.name} (v${item.version}) ${item.product_name || ''}`" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="物料" prop="material">
        <el-select v-model="form.material" filterable placeholder="请选择物料" class="form-input">
          <el-option v-for="item in materials" :key="item.id" :label="`${item.name} (${item.code || ''})`"
            :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="用量" prop="quantity">
        <el-input-number v-model="form.quantity" :min="0" :step="1" class="form-input" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="3" class="form-input" />
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
import type { BomDetailForm, Bom, Product } from '../../types/common'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: BomDetailForm
  rules: Record<string, any>
  boms: Bom[]
  materials: Product[]
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
