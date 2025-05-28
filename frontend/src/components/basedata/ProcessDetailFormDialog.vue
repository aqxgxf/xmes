<template>
  <el-dialog :model-value="visible" :title="title" width="600px" destroy-on-close @close="handleClose">
    <el-form :ref="props.formRef" :model="form" :rules="rules" label-width="120px" label-position="left">
      <el-form-item label="步骤" prop="step_no">
        <el-input-number v-model="form.step_no" :min="1" class="form-input" />
      </el-form-item>
      <el-form-item label="工序" prop="step">
        <el-select v-model="form.step" filterable placeholder="请选择工序" class="form-input">
          <el-option v-for="process in processes" :key="process.id" :label="process.name" :value="process.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="工序内容" prop="process_content">
        <el-input v-model="form.process_content" type="textarea" :rows="3" placeholder="请输入工序内容" class="form-input" />
      </el-form-item>
      <el-form-item label="设备时间(分钟)" prop="machine_time">
        <el-input-number v-model="form.machine_time" :min="0" :precision="2" class="form-input" />
      </el-form-item>
      <el-form-item label="人工时间(分钟)" prop="labor_time">
        <el-input-number v-model="form.labor_time" :min="0" :precision="2" class="form-input" />
      </el-form-item>
      <el-form-item label="所需设备" prop="required_equipment">
        <el-input v-model="form.required_equipment" placeholder="请输入所需设备" class="form-input" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" class="form-input" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts">
export default {
  name: 'ProcessDetailFormDialog'
}
</script>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ProcessDetailForm, Process } from '../../types/common'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: ProcessDetailForm
  rules: Record<string, any>
  processes: Process[]
  formRef: any // 新增，Ref<FormInstance|undefined>
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
}>()

// Methods
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleSave = async () => {
  if (!props.formRef?.value) return

  await props.formRef.value.validate(async (valid: boolean) => {
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
