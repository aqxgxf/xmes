<template>
  <el-dialog :model-value="visible" :title="title" width="600px" destroy-on-close @close="handleClose"
    @opened="$emit('opened')">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="left"
      class="form-container">
      <el-form-item label="产品类" prop="category">
        <el-select v-model="form.category" placeholder="请选择产品类" filterable class="form-select"
          @change="handleCategoryChange">
          <el-option
            v-for="item in categories"
            :key="typeof item.id === 'string' ? Number(item.id) : item.id"
            :label="item.display_name + '（' + item.code + '）'"
            :value="typeof item.id === 'string' ? Number(item.id) : item.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="说明" prop="description">
        <el-input v-model="form.description" class="form-input" />
      </el-form-item>

      <el-form-item label="版本" prop="version">
        <el-select v-model="form.version" placeholder="请选择版本" class="form-select" @change="handleVersionChange">
          <el-option v-for="v in ['A', 'B', 'C', 'D', 'E', 'F', 'G']" :key="v" :label="v" :value="v" />
        </el-select>
      </el-form-item>

      <el-form-item label="工艺流程代码" prop="code">
        <el-input v-model="form.code" class="form-input" />
      </el-form-item>

      <el-form-item label="工艺PDF">
        <div v-if="form.process_pdf && !localPdfFiles.length" class="current-file">
          <span>当前文件：</span>
          <el-link :href="'/native-pdf-viewer?url=' + encodeURIComponent(form.process_pdf)" target="_blank"
            type="primary">
            <el-icon>
              <Document />
            </el-icon> 查看PDF
          </el-link>
        </div>

        <el-upload class="pdf-uploader" :auto-upload="false" accept=".pdf" :limit="1" :file-list="localPdfFiles"
          @update:file-list="handleFileListUpdate">
          <template #trigger>
            <el-button type="primary">选择文件</el-button>
          </template>
          <template #tip>
            <div class="upload-tip">仅支持PDF格式文件</div>
          </template>
        </el-upload>

        <pdf-preview v-if="localPdfFiles.length > 0" :file="localPdfFiles[0].raw" />
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
import { ref, watch, onMounted } from 'vue'
import { Document } from '@element-plus/icons-vue'
import type { FormInstance, UploadUserFile } from 'element-plus'
import type { ProcessCodeForm, Product, ProductCategory } from '../../types/common'
// @ts-ignore - Vue SFC没有默认导出，但在Vue项目中可以正常使用
import PdfPreview from '../common/PdfPreview.vue'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: ProcessCodeForm
  rules: Record<string, any>
  categories?: ProductCategory[]
  pdfFiles: any[]
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'opened'): void
  (e: 'category-change', categoryId: number): void
  (e: 'version-change', version: string): void
  (e: 'update:pdfFiles', files: UploadUserFile[]): void
}>()

// 本地状态
const localPdfFiles = ref<UploadUserFile[]>([])
const formRef = ref<FormInstance>()

// 观察props.pdfFiles变化并更新本地状态
watch(() => props.pdfFiles, (newFiles) => {
  localPdfFiles.value = [...newFiles]
}, { immediate: true })

// 文件列表更新处理
const handleFileListUpdate = (files: UploadUserFile[]) => {
  localPdfFiles.value = files
  emit('update:pdfFiles', files)
}

// 组件加载时初始化
onMounted(() => {
  localPdfFiles.value = [...props.pdfFiles]
})

// Methods
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleCategoryChange = (categoryId: number) => {
  emit('category-change', categoryId)
}

const handleVersionChange = (version: string) => {
  emit('version-change', version)
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

.form-select,
.form-input {
  width: 100%;
}

.pdf-uploader {
  margin-bottom: 12px;

  .upload-tip {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    margin-top: 8px;
  }
}

.current-file {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
