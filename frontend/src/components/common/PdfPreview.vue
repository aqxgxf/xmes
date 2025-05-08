<template>
  <div class="pdf-preview">
    <div v-if="isLoading" class="pdf-loading">
      <el-icon class="loading-icon"><Loading /></el-icon> 正在加载PDF...
    </div>
    <div v-if="error" class="pdf-error">
      <el-icon><WarningFilled /></el-icon> PDF加载失败: {{ error }}
    </div>
    <div v-if="previewImage" class="pdf-image-container">
      <img :src="previewImage" class="pdf-image" alt="PDF预览" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  file?: File
  url?: string
}>()

const isLoading = ref(false)
const error = ref('')
const previewImage = ref('')

// PDF.js路径
const PDFJS_CDN = '/pdfjs/pdf.js'
const PDFJS_WORKER_CDN = '/pdfjs/pdf.worker.js'

// 加载PDF.js
function loadPdfJs() {
  return new Promise<void>((resolve, reject) => {
    if (window.pdfjsLib) {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_WORKER_CDN
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = PDFJS_CDN
    script.onload = () => {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_WORKER_CDN
      resolve()
    }
    script.onerror = () => {
      reject(new Error('无法加载PDF.js库'))
    }
    document.head.appendChild(script)
  })
}

// 渲染PDF到Canvas，然后转换为图片
async function renderPdf(source: string | ArrayBuffer) {
  isLoading.value = true
  previewImage.value = ''
  error.value = ''

  try {
    await loadPdfJs()
    
    const loadingTask = window.pdfjsLib.getDocument(source)
    const pdf = await loadingTask.promise
    const page = await pdf.getPage(1) // 只预览第一页
    
    // 设置合适的缩放比例
    const viewport = page.getViewport({ scale: 1.5 })
    
    // 创建Canvas
    const canvas = document.createElement('canvas')
    canvas.width = viewport.width
    canvas.height = viewport.height
    
    // 渲染到Canvas
    const context = canvas.getContext('2d')
    if (!context) {
      throw new Error('无法获取canvas上下文')
    }
    
    await page.render({
      canvasContext: context,
      viewport: viewport
    }).promise
    
    // 转换为图片
    previewImage.value = canvas.toDataURL('image/png')
  } catch (err) {
    console.error('PDF预览失败', err)
    error.value = err instanceof Error ? err.message : '预览失败'
  } finally {
    isLoading.value = false
  }
}

// 从文件加载PDF
function loadPdfFromFile(file: File) {
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    if (e.target?.result) {
      renderPdf(e.target.result as ArrayBuffer)
    }
  }
  reader.onerror = () => {
    error.value = '读取文件失败'
  }
  reader.readAsArrayBuffer(file)
}

// 从URL加载PDF
function loadPdfFromUrl(url: string) {
  if (!url) return
  renderPdf(url)
}

// 监听props变化，重新加载PDF
watch(() => props.file, (newFile) => {
  if (newFile) {
    loadPdfFromFile(newFile)
  }
}, { immediate: true })

watch(() => props.url, (newUrl) => {
  if (newUrl && !props.file) {
    loadPdfFromUrl(newUrl)
  }
}, { immediate: true })

// 初始加载
onMounted(() => {
  if (props.file) {
    loadPdfFromFile(props.file)
  } else if (props.url) {
    loadPdfFromUrl(props.url)
  }
})
</script>

<style scoped>
.pdf-preview {
  margin-top: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  width: 100%;
}

.pdf-loading, .pdf-error {
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.pdf-error {
  color: var(--el-color-danger);
}

.loading-icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pdf-image-container {
  display: flex;
  justify-content: center;
  padding: 16px;
  background-color: #f5f7fa;
}

.pdf-image {
  max-width: 100%;
  border: 1px solid #dcdfe6;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>

<script lang="ts">
// 添加全局类型声明，用于PDF.js
declare global {
  interface Window {
    pdfjsLib: any
  }
}
</script> 