<template>
  <div class="pdf-preview">
    <div v-if="isLoading" class="pdf-loading">
      <el-icon class="loading-icon">
        <Loading />
      </el-icon> 正在加载PDF...
    </div>
    <div v-if="error" class="pdf-error">
      <el-icon>
        <WarningFilled />
      </el-icon> PDF加载失败: {{ error }}
    </div>
    <div v-if="previewImage" class="pdf-image-container">
      <img :src="previewImage" class="pdf-image" alt="PDF预览" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  file?: File
  url?: string
  fileKey?: string // 用于强制重新渲染预览
}>()

const isLoading = ref(false)
const error = ref('')
const previewImage = ref('')

// 加载 PDF.js
function loadPdfJs() {
  return new Promise<void>((resolve, reject) => {
    if (window.pdfjsLib) {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js'
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = '/pdfjs/pdf.js'
    script.onload = () => {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js'
      resolve()
    }
    script.onerror = () => {
      reject(new Error('无法加载PDF.js库'))
    }
    document.head.appendChild(script)
  })
}

// 处理PDF预览
async function previewPdf(source: string | ArrayBuffer) {
  isLoading.value = true
  previewImage.value = ''
  error.value = ''

  try {
    await loadPdfJs()

    const loadingTaskOptions: any = {
      cMapUrl: '/pdfjs/cmaps/',
      cMapPacked: true,
      disableRange: true,
      disableStream: true,
      isEvalSupported: false
    }

    // 创建PDF加载任务
    const loadingTask = window.pdfjsLib.getDocument({
      ...loadingTaskOptions,
      ...(typeof source === 'string' ? { url: source } : { data: source })
    })

    // 加载PDF
    const pdf = await loadingTask.promise
    const page = await pdf.getPage(1) // 只预览第一页

    // 设置合适的缩放比例
    const viewport = page.getViewport({ scale: 1.5 })

    // 创建Canvas
    const canvas = document.createElement('canvas')
    canvas.width = viewport.width
    canvas.height = viewport.height

    // 渲染PDF到Canvas
    const context = canvas.getContext('2d')
    if (!context) {
      throw new Error('无法获取Canvas 2D上下文')
    }

    await page.render({
      canvasContext: context,
      viewport
    }).promise

    // 将Canvas转换为图片
    previewImage.value = canvas.toDataURL()
  } catch (e: any) {
    console.error('PDF预览失败', e)
    error.value = e.message || '无法预览PDF文件'
  } finally {
    isLoading.value = false
  }
}

// 从文件创建预览
async function createPreviewFromFile(file: File) {
  if (!file) {
    previewImage.value = ''
    error.value = ''
    return
  }

  try {
    // 将文件读取为ArrayBuffer
    const arrayBuffer = await new Promise<ArrayBuffer>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        if (reader.result instanceof ArrayBuffer) {
          resolve(reader.result)
        } else {
          reject(new Error('读取文件失败'))
        }
      }
      reader.onerror = () => reject(reader.error || new Error('读取文件失败'))
      reader.readAsArrayBuffer(file)
    })

    // 预览PDF
    await previewPdf(arrayBuffer)
  } catch (e: any) {
    console.error('文件读取失败', e)
    error.value = e.message || '无法读取文件'
    previewImage.value = ''
  }
}

// 监听文件和URL变化，使用fileKey强制重新渲染
watch(
  () => [props.file, props.url, props.fileKey],
  async () => {
    if (props.file) {
      await createPreviewFromFile(props.file)
    } else if (props.url) {
      await previewPdf(props.url)
    } else {
      previewImage.value = ''
      error.value = ''
    }
  },
  { immediate: true }
)

// 组件挂载时初始化
onMounted(async () => {
  if (props.file) {
    await createPreviewFromFile(props.file)
  } else if (props.url) {
    await previewPdf(props.url)
  }
})
</script>


<style scoped>
.pdf-preview {
  margin-top: 10px;
  max-width: 100%;
  overflow: hidden;
}

.pdf-loading,
.pdf-error {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  margin-bottom: 10px;
}

.pdf-error {
  color: #f56c6c;
}

.loading-icon {
  animation: rotating 2s linear infinite;
  margin-right: 8px;
}

.pdf-image-container {
  margin-top: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
  padding: 10px;
  max-height: 300px;
  overflow: auto;
}

.pdf-image {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
