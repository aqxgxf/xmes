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

// 处理PDF文件验证
function isPdfValid(fileOrUrl: File | string): Promise<boolean> {
  return new Promise((resolve) => {
    // 如果是文件对象，检查MIME类型
    if (fileOrUrl instanceof File) {
      // 检查文件类型
      if (fileOrUrl.type === 'application/pdf') {
        resolve(true)
      } else {
        // 如果类型不是PDF，进一步检查文件头部
        const reader = new FileReader()
        reader.onload = (e) => {
          if (e.target?.result) {
            const arr = new Uint8Array(e.target.result as ArrayBuffer).subarray(0, 5)
            const header = Array.from(arr).map(byte => String.fromCharCode(byte)).join('')
            // PDF文件头通常是 %PDF-
            resolve(header.indexOf('%PDF') === 0)
          } else {
            resolve(false)
          }
        }
        reader.onerror = () => resolve(false)
        reader.readAsArrayBuffer(fileOrUrl.slice(0, 5))
      }
    } else {
      // 如果是URL，假设它是有效的，因为我们无法轻易检查
      resolve(true)
    }
  })
}

// 判断是否为乱码字符
function isGarbledText(text: string): boolean {
  // 检查常见的乱码标志，如特殊控制字符、特殊UTF字符等
  const garbledPatterns = [
    /[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/,  // 控制字符
    /å|â|ã|à|é|è|ê|ë|í|ì|î|ï|ò|ó|ô|õ|ö|ù|ú|û|ü|ÿ/, // 常见乱码字符组合
    /[^\x00-\x7F]+/  // 非ASCII字符
  ];

  return garbledPatterns.some(pattern => pattern.test(text));
}

// 渲染PDF到Canvas，然后转换为图片
async function renderPdf(source: string | ArrayBuffer) {
  isLoading.value = true
  previewImage.value = ''
  error.value = ''

  try {
    await loadPdfJs()

    // 添加标题修复
    let loadingTaskOptions: any = {
      cMapUrl: '/pdfjs/cmaps/',
      cMapPacked: true,
      // 提高渲染质量
      disableRange: false,
      disableStream: false,
      isEvalSupported: true
    }

    // 如果是URL，从URL中提取文件名用于显示
    if (typeof source === 'string') {
      const urlParts = source.split('/')
      const fileName = urlParts[urlParts.length - 1]

      // 设置文档标题，覆盖PDF内部的标题
      loadingTaskOptions.docTitle = decodeURIComponent(fileName)
    }

    // 创建PDF加载任务
    const loadingTask = window.pdfjsLib.getDocument({
      ...loadingTaskOptions,
      ...(typeof source === 'string' ? { url: source } : { data: source })
    })

    // 添加加载失败事件处理
    loadingTask.onProgress = (progressData: any) => {
      console.log('PDF加载进度:', progressData.loaded / progressData.total)
    }

    loadingTask.onPassword = (updateCallback: Function, reason: number) => {
      console.log('PDF需要密码')
      error.value = 'PDF文件受密码保护，无法预览'
    }

    // 等待PDF加载
    const pdf = await loadingTask.promise

    // 设置文档标题
    if (typeof source === 'string') {
      // 如果前面已经设置了标题，以早期设置的为准
      if (document.title && (document.title.includes('-工艺.pdf') || document.title.includes('-图纸.pdf'))) {
        console.log('Using previously set document title:', document.title)
      } else {
        // 从URL中提取文件名
        const urlParts = source.split('/')
        let fileName = urlParts[urlParts.length - 1]

        console.log('Setting document title from URL:', source)
        console.log('Extracted filename:', fileName)

        // 解码文件名
        try {
          fileName = decodeURIComponent(fileName)
          console.log('Decoded filename:', fileName)

          // 移除URL参数部分
          if (fileName.includes('?')) {
            fileName = fileName.split('?')[0]
            console.log('Removed URL parameters:', fileName)
          }

          // 处理特殊字符显示问题
          if (fileName.includes('-图纸.pdf')) {
            const parts = fileName.split('-图纸.pdf')[0].split('-')
            if (parts.length >= 2) {
              const code = parts[0]
              const company = parts.slice(1, parts.length).join('-')
              document.title = `${code}-${company}-图纸.pdf`
              console.log('Set drawing PDF title:', document.title)
            } else {
              document.title = fileName
              console.log('Using raw filename as title:', document.title)
            }
          } else if (fileName.includes('-工艺.pdf')) {
            const parts = fileName.split('-工艺.pdf')[0].split('-')
            if (parts.length >= 2) {
              const code = parts[0]
              const company = parts.slice(1, parts.length).join('-')
              document.title = `${code}-${company}-工艺.pdf`
              console.log('Set process PDF title:', document.title)
            } else {
              document.title = fileName
              console.log('Using raw filename as title:', document.title)
            }
          } else if (fileName.includes('-process.pdf')) {
            // 处理旧格式的process命名
            const parts = fileName.split('-process.pdf')[0].split('-')
            if (parts.length >= 2) {
              const code = parts[0]
              const company = parts.slice(1, parts.length).join('-')
              document.title = `${code}-${company}-工艺.pdf`
              console.log('Set process PDF title from old format:', document.title)
            } else {
              document.title = fileName.replace('-process.pdf', '-工艺.pdf')
              console.log('Converted old process filename to title:', document.title)
            }
          } else {
            // 尝试从URL路径中查找关键词
            const urlPath = source.toLowerCase()
            if (urlPath.includes('/process/') || urlPath.includes('process_pdf') || urlPath.includes('工艺')) {
              console.log('Detected process PDF from URL path')

              // 尝试提取产品代码
              const segments = source.split('/')
              for (const segment of segments) {
                // 找到包含数字和字母的段落，可能是产品代码
                if (/[A-Z0-9]/.test(segment) && segment.length <= 10) {
                  document.title = `${segment}-工艺.pdf`
                  console.log('Set process PDF title from URL segment:', document.title)
                  break
                }
              }

              if (!document.title.includes('.pdf')) {
                document.title = '工艺文档.pdf'
              }
            } else if (urlPath.includes('/drawing/') || urlPath.includes('drawing_pdf') || urlPath.includes('图纸')) {
              console.log('Detected drawing PDF from URL path')
              document.title = fileName.includes('.pdf') ? fileName : '图纸文档.pdf'
            } else {
              // 默认情况：移除扩展名作为标题
              document.title = fileName.replace(/\.[^/.]+$/, "") || 'PDF预览'
              console.log('Using filename without extension as title:', document.title)
            }
          }
        } catch (e) {
          console.error('Failed to decode filename', e)
          document.title = 'PDF预览'
        }
      }
    }

    const page = await pdf.getPage(1) // 只预览第一页

    // 设置合适的缩放比例 - 使用更大的缩放比例以显示更多内容
    const viewport = page.getViewport({ scale: 1.8 })

    // 创建Canvas - 确保足够大以容纳整个PDF页面
    const canvas = document.createElement('canvas')
    canvas.width = viewport.width
    canvas.height = viewport.height

    // 使用完整的渲染上下文
    const context = canvas.getContext('2d')

    if (!context) {
      throw new Error('无法创建canvas上下文')
    }

    // 渲染PDF到Canvas
    const renderContext = {
      canvasContext: context,
      viewport
    }

    await page.render(renderContext).promise

    // 转换Canvas为图片URL
    previewImage.value = canvas.toDataURL('image/jpeg', 0.95)
  } catch (err: any) {
    console.error('PDF预览失败:', err)
    error.value = err.message || '无法加载PDF'
  } finally {
    isLoading.value = false
  }
}

// 从文件加载PDF
async function loadPdfFromFile(file: File) {
  if (!file) return

  // 验证文件是否是有效的PDF
  const isValid = await isPdfValid(file)
  if (!isValid) {
    error.value = '无效的PDF文件格式'
    return
  }

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

  // 添加时间戳避免缓存问题
  const timestampedUrl = url.includes('?')
    ? `${url}&_t=${Date.now()}`
    : `${url}?_t=${Date.now()}`

  renderPdf(timestampedUrl)
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
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: auto;
  background: #f0f0f0;
}

.pdf-loading,
.pdf-error {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 20px;
  color: #666;
  font-size: 16px;
  width: 100%;
  height: 100%;
}

.loading-icon {
  font-size: 32px;
  margin-bottom: 10px;
  animation: rotate 1.5s linear infinite;
}

.pdf-image-container {
  width: 100%;
  height: auto;
  overflow: auto;
  padding: 20px;
  display: flex;
  justify-content: center;
}

.pdf-image {
  max-width: 100%;
  height: auto;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  background: white;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
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
