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
          <el-form-item label="所属客户" prop="company">
            <el-select v-model="form.company" filterable placeholder="选择客户" class="full-width">
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

      <el-form-item label="材质" prop="material_type">
        <el-select v-model="form.material_type" placeholder="请选择材质" filterable style="width: 100%" @change="handleMaterialChange">
          <el-option v-for="mat in materials" :key="mat.id" :label="mat.name + (mat.code ? ' (' + mat.code + ')' : '')" :value="mat.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="图纸PDF">
        <!-- 显示当前文件 -->
        <div v-if="form.drawing_pdf_url && !drawingFile" class="current-file">
          <span>当前文件：</span>
          <el-link :href="getCorrectPdfViewerUrl(form.drawing_pdf_url)" target="_blank"
            type="primary" :disabled="!form.drawing_pdf_url">
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

        <div v-if="drawingFile" ref="drawingPdfContainerRef" class="pdf-preview-container">
          <img v-if="drawingPreviewType === 'image'" :src="drawingPreviewUrl" style="max-width:100%;max-height:400px;" />
          <div v-else-if="drawingPreviewType === 'pdf'" class="pdf-canvas-wrapper">
            <div class="pdf-toolbar">
              <el-button size="small" @click="prevDrawingPdfPage" :disabled="drawingPdfPage <= 1">上一页</el-button>
              <span>第 {{ drawingPdfPage }} / {{ drawingPdfPageCount }} 页</span>
              <el-button size="small" @click="nextDrawingPdfPage" :disabled="drawingPdfPage >= drawingPdfPageCount">下一页</el-button>
            </div>
            <div class="pdf-canvas-bg">
              <img v-if="drawingPdfCanvasUrl" :src="drawingPdfCanvasUrl" style="box-shadow:0 2px 8px #ccc;border-radius:4px;background:#fff;" />
            </div>
          </div>
          <div v-else-if="drawingPreviewType === 'none' && drawingPreviewUrl">
            <span style="color:red;">不支持的文件类型</span>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="工艺PDF">
        <!-- 显示当前文件 -->
        <div v-if="form.process_pdf_url && !processFile" class="current-file">
          <span>当前文件：</span>
          <el-link :href="getCorrectPdfViewerUrl(form.process_pdf_url)" target="_blank"
            type="primary" :disabled="!form.process_pdf_url">
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

        <div v-if="processFile" ref="processPdfContainerRef" class="pdf-preview-container">
          <img v-if="processPreviewType === 'image'" :src="processPreviewUrl" style="max-width:100%;max-height:400px;" />
          <div v-else-if="processPreviewType === 'pdf'" class="pdf-canvas-wrapper">
            <div class="pdf-toolbar">
              <el-button size="small" @click="prevProcessPdfPage" :disabled="processPdfPage <= 1">上一页</el-button>
              <span>第 {{ processPdfPage }} / {{ processPdfPageCount }} 页</span>
              <el-button size="small" @click="nextProcessPdfPage" :disabled="processPdfPage >= processPdfPageCount">下一页</el-button>
            </div>
            <div class="pdf-canvas-bg">
              <img v-if="processPdfCanvasUrl" :src="processPdfCanvasUrl" style="box-shadow:0 2px 8px #ccc;border-radius:4px;background:#fff;" />
            </div>
          </div>
          <div v-else-if="processPreviewType === 'none' && processPreviewUrl">
            <span style="color:red;">不支持的文件类型</span>
          </div>
        </div>
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
import { ref, onMounted, nextTick, watch } from 'vue'
import { Document } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { Company, ProductCategoryForm, Unit, MaterialType } from '../../types/common'
import ImprovedPdfPreview from '../common/ImprovedPdfPreview.vue'
import { getCorrectPdfViewerUrl } from '../../utils/pdfHelpers'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  companies: Company[]
  units: Unit[]
  materials: MaterialType[]
  form: ProductCategoryForm
  rules: Record<string, any>
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'material-change', materialId: number): void
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

// 本地预览
const drawingPreviewUrl = ref<string>()
const drawingPreviewType = ref<'image' | 'pdf' | 'none'>('none')
const processPreviewUrl = ref<string>()
const processPreviewType = ref<'image' | 'pdf' | 'none'>('none')

// 容器引用
const drawingPdfContainerRef = ref<HTMLDivElement>()
const processPdfContainerRef = ref<HTMLDivElement>()
const drawingPdfHeight = ref(600)
const processPdfHeight = ref(600)

const drawingPdfPage = ref(1)
const drawingPdfPageCount = ref(1)
const drawingPdfCanvasUrl = ref<string>()
const drawingPdfFile = ref<File | null>(null)

const processPdfPage = ref(1)
const processPdfPageCount = ref(1)
const processPdfCanvasUrl = ref<string>()
const processPdfFile = ref<File | null>(null)

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

// 动态PDF高宽比检测
async function getPdfAspectRatio(file: File): Promise<number> {
  // 依赖public/pdfjs/pdf.js和pdf.worker.js
  if (!(window as any).pdfjsLib) {
    await new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = '/pdfjs/pdf.js'
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }
  if (!(window as any).pdfjsWorker) {
    await new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = '/pdfjs/pdf.worker.js'
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }
  const pdfjsLib = (window as any).pdfjsLib
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js'
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  const page = await pdf.getPage(1)
  const viewport = page.getViewport({ scale: 1 })
  return viewport.height / viewport.width
}

// 处理文件选择
const handleDrawingFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    const file = input.files[0]
    drawingFile.value = file
    props.form.drawing_pdf = file
    drawingFileKey.value = Date.now().toString()
    // 本地预览类型判断
    if (file.type.startsWith('image/')) {
      drawingPreviewUrl.value = URL.createObjectURL(file)
      drawingPreviewType.value = 'image'
      updateDrawingPdfHeight()
    } else if (file.type === 'application/pdf') {
      drawingPreviewUrl.value = URL.createObjectURL(file)
      drawingPreviewType.value = 'pdf'
      drawingPdfFile.value = file
      drawingPdfPage.value = 1
      await updateDrawingPdfCanvas()
    } else {
      drawingPreviewUrl.value = undefined
      drawingPreviewType.value = 'none'
      updateDrawingPdfHeight()
    }
  }
}

const handleProcessFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    const file = input.files[0]
    processFile.value = file
    props.form.process_pdf = file
    processFileKey.value = Date.now().toString()
    // 本地预览类型判断
    if (file.type.startsWith('image/')) {
      processPreviewUrl.value = URL.createObjectURL(file)
      processPreviewType.value = 'image'
      updateProcessPdfHeight()
    } else if (file.type === 'application/pdf') {
      processPreviewUrl.value = URL.createObjectURL(file)
      processPreviewType.value = 'pdf'
      processPdfFile.value = file
      processPdfPage.value = 1
      await updateProcessPdfCanvas()
    } else {
      processPreviewUrl.value = undefined
      processPreviewType.value = 'none'
      updateProcessPdfHeight()
    }
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

const handleMaterialChange = (materialId: number) => {
  emit('material-change', materialId)
}

function updateDrawingPdfHeight() {
  nextTick(() => {
    if (drawingPdfContainerRef.value) {
      const width = drawingPdfContainerRef.value.offsetWidth
      drawingPdfHeight.value = Math.round(width * 1.414)
    }
  })
}

function updateProcessPdfHeight() {
  nextTick(() => {
    if (processPdfContainerRef.value) {
      const width = processPdfContainerRef.value.offsetWidth
      processPdfHeight.value = Math.round(width * 1.414)
    }
  })
}

async function renderPdfPage(file: File, pageNum: number, containerWidth: number) {
  if (!(window as any).pdfjsLib) {
    await new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = '/pdfjs/pdf.js'
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }
  const pdfjsLib = (window as any).pdfjsLib
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js'
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  drawingPdfPageCount.value = pdf.numPages
  const page = await pdf.getPage(pageNum)
  const viewport = page.getViewport({ scale: 1 })
  const scale = (containerWidth - 32) / viewport.width
  const scaledViewport = page.getViewport({ scale })
  const canvas = document.createElement('canvas')
  canvas.width = scaledViewport.width
  canvas.height = scaledViewport.height
  const ctx = canvas.getContext('2d')
  await page.render({ canvasContext: ctx, viewport: scaledViewport }).promise
  drawingPdfCanvasUrl.value = canvas.toDataURL()
}

function prevDrawingPdfPage() {
  if (drawingPdfPage.value > 1) {
    drawingPdfPage.value--
    updateDrawingPdfCanvas()
  }
}
function nextDrawingPdfPage() {
  if (drawingPdfPage.value < drawingPdfPageCount.value) {
    drawingPdfPage.value++
    updateDrawingPdfCanvas()
  }
}
async function updateDrawingPdfCanvas() {
  if (drawingPdfFile.value && drawingPreviewType.value === 'pdf') {
    await renderPdfPage(drawingPdfFile.value, drawingPdfPage.value, drawingPdfContainerRef.value?.offsetWidth || 600)
  }
}

async function renderProcessPdfPage(file: File, pageNum: number, containerWidth: number) {
  if (!(window as any).pdfjsLib) {
    await new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = '/pdfjs/pdf.js'
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }
  const pdfjsLib = (window as any).pdfjsLib
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js'
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  processPdfPageCount.value = pdf.numPages
  const page = await pdf.getPage(pageNum)
  const viewport = page.getViewport({ scale: 1 })
  const scale = (containerWidth - 32) / viewport.width
  const scaledViewport = page.getViewport({ scale })
  const canvas = document.createElement('canvas')
  canvas.width = scaledViewport.width
  canvas.height = scaledViewport.height
  const ctx = canvas.getContext('2d')
  await page.render({ canvasContext: ctx, viewport: scaledViewport }).promise
  processPdfCanvasUrl.value = canvas.toDataURL()
}

function prevProcessPdfPage() {
  if (processPdfPage.value > 1) {
    processPdfPage.value--
    updateProcessPdfCanvas()
  }
}
function nextProcessPdfPage() {
  if (processPdfPage.value < processPdfPageCount.value) {
    processPdfPage.value++
    updateProcessPdfCanvas()
  }
}
async function updateProcessPdfCanvas() {
  if (processPdfFile.value && processPreviewType.value === 'pdf') {
    await renderProcessPdfPage(processPdfFile.value, processPdfPage.value, processPdfContainerRef.value?.offsetWidth || 600)
  }
}

onMounted(() => {
  updateDrawingPdfHeight()
  updateProcessPdfHeight()
})

watch([drawingPreviewUrl, drawingPreviewType], updateDrawingPdfHeight)
watch([processPreviewUrl, processPreviewType], updateProcessPdfHeight)
watch([drawingPdfPage, () => drawingPdfContainerRef.value?.offsetWidth], updateDrawingPdfCanvas)
watch([processPdfPage, () => processPdfContainerRef.value?.offsetWidth], updateProcessPdfCanvas)

window.addEventListener('resize', () => {
  updateDrawingPdfHeight()
  updateProcessPdfHeight()
  updateDrawingPdfCanvas()
  updateProcessPdfCanvas()
})
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

.pdf-preview-container {
  padding: 16px 0;
}
.pdf-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.pdf-canvas-bg {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border-radius: 8px;
  min-height: 200px;
}
</style>
