<template>
  <el-dialog :model-value="visible" :title="title" width="70%" destroy-on-close @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="left"
      class="form-container">
      <el-form-item label="物料类别" prop="category">
        <el-select v-model="form.category" placeholder="请选择物料类别" filterable class="form-select"
          @change="handleCategoryChange">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.display_name + ' (' + cat.code + ')'"
            :value="cat.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="物料代码" prop="code">
        <el-input v-model="form.code" maxlength="100" show-word-limit class="form-input" />
      </el-form-item>

      <el-form-item label="物料名称" prop="name">
        <el-input v-model="form.name" maxlength="100" show-word-limit class="form-input" />
      </el-form-item>

      <el-form-item label="单价" prop="price">
        <el-input-number v-model="form.price" :precision="2" :min="0" class="form-input-number" />
      </el-form-item>

      <el-form-item label="单位" prop="unit">
        <el-select v-model="form.unit" placeholder="请选择单位" filterable clearable class="form-select">
          <el-option v-for="unit in units" :key="unit.id" :label="`${unit.name} (${unit.code})`" :value="unit.id" />
        </el-select>
      </el-form-item>

      <el-form-item v-for="param in params" :key="param.id" :label="param.name" :prop="`paramValues.${param.id}`">
        <el-input v-model="form.paramValues[param.id]" class="form-input-param" @input="handleParamValueChange" />
      </el-form-item>

      <el-form-item label="图纸PDF" prop="drawing_pdf">
        <!-- 显示当前文件（仅编辑模式） -->
        <div v-if="form.drawing_pdf_url" class="current-file">
          <span>当前文件：</span>
          <el-link :href="'/native-pdf-viewer?url=' + encodeURIComponent(form.drawing_pdf_url)" target="_blank"
            type="primary">
            <el-icon>
              <Document />
            </el-icon> 查看PDF
          </el-link>
        </div>

        <el-upload class="pdf-uploader" :auto-upload="false" accept=".pdf" :limit="1" :file-list="drawingFiles"
          @change="handleDrawingChange">
          <template #trigger>
            <el-button type="primary">选择文件</el-button>
          </template>
          <template #tip>
            <div class="upload-tip">
              {{ form.id ? '上传新文件将替换当前文件' : '仅支持PDF格式文件' }}
            </div>
          </template>
        </el-upload>
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
import { Document } from '@element-plus/icons-vue'
import type { FormInstance, UploadFile, UploadUserFile } from 'element-plus'
import type { Category, MaterialForm, Param, Unit } from '../../types/common'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  categories: Category[]
  units: Unit[]
  params: Param[]
  form: MaterialForm
  rules: Record<string, any>
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'category-change', categoryId: number): void
  (e: 'param-change'): void
}>()

// Form ref and file list
const formRef = ref<FormInstance>()
const drawingFiles = ref<UploadUserFile[]>([])

// 处理图纸变更
const handleDrawingChange = (file: UploadFile, fileList: UploadUserFile[]) => {
  drawingFiles.value = fileList
  if (file.raw) {
    props.form.drawing_pdf = file.raw
  }
}

// 处理参数值变化
const handleParamValueChange = () => {
  emit('param-change')
}

// Methods
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleCategoryChange = (categoryId: number) => {
  emit('category-change', categoryId)
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
  width: 500px;
  overflow-y: auto;
  padding-right: 16px;
}

.form-input,
.form-select {
  width: 400px;
}

.form-input-number {
  width: 140px;
}

.form-input-param {
  width: 200px;
}

.current-file {
  margin-bottom: 12px;
}

.pdf-uploader {
  margin-bottom: 16px;
}
</style>
