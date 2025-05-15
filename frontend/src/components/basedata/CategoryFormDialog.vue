<template>
  <el-dialog :model-value="visible" :title="title" width="760px" destroy-on-close @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="产品类编码" prop="code">
            <el-input v-model="form.code" maxlength="20" show-word-limit />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="产品类名称" prop="display_name">
            <el-input v-model="form.display_name" maxlength="40" show-word-limit />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="所属公司" prop="company">
            <el-select v-model="form.company" filterable placeholder="选择公司" class="full-width">
              <el-option v-for="item in companies" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="默认单位" prop="unit">
            <el-select v-model="form.unit" filterable placeholder="选择单位" class="full-width">
              <el-option v-for="item in units" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="图纸PDF">
        <!-- 显示当前文件 -->
        <div v-if="form.drawing_pdf_url && !drawingFile" class="current-file">
          <span>当前文件：</span>
          <el-link :href="'/native-pdf-viewer?url=' + encodeURIComponent(form.drawing_pdf_url)" target="_blank"
            type="primary">
            <el-icon>
              <Document />
            </el-icon> 查看PDF
          </el-link>
        </div>

        <!-- 使用基本文件输入代替el-upload -->
        <div class="file-input-container">
          <el-button type="primary" @click="triggerDrawingFileInput">选择文件</el-button>
          <input ref="drawingFileInputRef" type="file" accept=".pdf,.jpg,.jpeg,.png,.bmp" class="hidden-file-input"
            @change="handleDrawingFileSelect" />
          <div class="upload-tip">支持PDF或图片格式（JPG、PNG、BMP），图片将自动转换为PDF</div>
          <div v-if="drawingFile" class="selected-file">
            已选择: {{ drawingFile.name }}
            <el-button type="danger" size="small" @click="clearDrawingFile">清除</el-button>
          </div>
        </div>

        <improved-pdf-preview v-if="drawingFile" :file="drawingFile" :file-key="drawingFileKey" />
      </el-form-item>

      <el-form-item label="工艺PDF">
        <!-- 显示当前文件 -->
        <div v-if="form.process_pdf_url && !processFile" class="current-file">
          <span>当前文件：</span>
          <el-link :href="'/native-pdf-viewer?url=' + encodeURIComponent(form.process_pdf_url)" target="_blank"
            type="primary">
            <el-icon>
              <Document />
            </el-icon> 查看PDF
          </el-link>
        </div>

        <!-- 使用基本文件输入代替el-upload -->
        <div class="file-input-container">
          <el-button type="primary" @click="triggerProcessFileInput">选择文件</el-button>
          <input ref="processFileInputRef" type="file" accept=".pdf,.jpg,.jpeg,.png,.bmp" class="hidden-file-input"
            @change="handleProcessFileSelect" />
          <div class="upload-tip">支持PDF或图片格式（JPG、PNG、BMP），图片将自动转换为PDF</div>
          <div v-if="processFile" class="selected-file">
            已选择: {{ processFile.name }}
            <el-button type="danger" size="small" @click="clearProcessFile">清除</el-button>
          </div>
        </div>

        <improved-pdf-preview v-if="processFile" :file="processFile" :file-key="processFileKey" />
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
import type { FormInstance } from 'element-plus'
import type { Company, ProductCategoryForm, Unit } from '../../types/common'
import ImprovedPdfPreview from '../common/ImprovedPdfPreview.vue'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  companies: Company[]
  units: Unit[]
  form: ProductCategoryForm
  rules: Record<string, any>
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
}>()

// 表单引用
const formRef = ref<FormInstance>()

// 文件输入引用
const drawingFileInputRef = ref<HTMLInputElement | null>(null)
const processFileInputRef = ref<HTMLInputElement | null>(null)

// 文件管理
const drawingFile = ref<File | null>(null)
const processFile = ref<File | null>(null)
const drawingFileKey = ref(Date.now().toString())
const processFileKey = ref(Date.now().toString())

// 触发文件选择对话框
const triggerDrawingFileInput = () => {
  if (drawingFileInputRef.value) {
    drawingFileInputRef.value.click()
  }
}

const triggerProcessFileInput = () => {
  if (processFileInputRef.value) {
    processFileInputRef.value.click()
  }
}

// 处理文件选择
const handleDrawingFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    const file = input.files[0]
    drawingFile.value = file
    props.form.drawing_pdf = file
    drawingFileKey.value = Date.now().toString()
  }
}

const handleProcessFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    const file = input.files[0]
    processFile.value = file
    props.form.process_pdf = file
    processFileKey.value = Date.now().toString()
  }
}

// 清除选择的文件
const clearDrawingFile = () => {
  drawingFile.value = null
  if (drawingFileInputRef.value) {
    drawingFileInputRef.value.value = ''
  }
  props.form.drawing_pdf = undefined
}

const clearProcessFile = () => {
  processFile.value = null
  if (processFileInputRef.value) {
    processFileInputRef.value.value = ''
  }
  props.form.process_pdf = undefined
}

// Methods
const handleClose = () => {
  // 清空文件选择
  clearDrawingFile()
  clearProcessFile()

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
.full-width {
  width: 100%;
}

.current-file {
  margin-bottom: 12px;
}

.file-input-container {
  margin-bottom: 16px;
}

.hidden-file-input {
  display: none;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.selected-file {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
