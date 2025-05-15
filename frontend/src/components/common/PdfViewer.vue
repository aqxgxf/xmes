<template>
  <div class="pdf-viewer-container">
    <pdf-preview :url="pdfUrl" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PdfPreview from './PdfPreview.vue'

// Analyze the URL parameters to get the PDF URL
const pdfUrl = ref('')

onMounted(() => {
  // Get URL from query parameters
  const urlParams = new URLSearchParams(window.location.search)
  const encodedUrl = urlParams.get('url')

  if (encodedUrl) {
    try {
      const decodedUrl = decodeURIComponent(encodedUrl)
      // 添加时间戳参数以避免浏览器缓存
      pdfUrl.value = decodedUrl.includes('?')
        ? `${decodedUrl}&_t=${Date.now()}`
        : `${decodedUrl}?_t=${Date.now()}`

      console.log('Loading PDF from URL:', pdfUrl.value)

      // 设置文档标题
      const pathSegments = decodedUrl.split('/')
      const fileName = pathSegments[pathSegments.length - 1].split('?')[0] // 移除URL参数

      // 尝试设置更友好的页面标题
      if (fileName.includes('-图纸.pdf')) {
        const parts = fileName.split('-图纸.pdf')[0].split('-')
        if (parts.length >= 2) {
          const code = parts[0]
          const company = parts.slice(1, parts.length).join('-')
          document.title = `${code}-${company}-图纸.pdf`
        } else {
          document.title = fileName
        }
      } else if (fileName.includes('-工艺.pdf')) {
        const parts = fileName.split('-工艺.pdf')[0].split('-')
        if (parts.length >= 2) {
          const code = parts[0]
          const company = parts.slice(1, parts.length).join('-')
          document.title = `${code}-${company}-工艺.pdf`
        } else {
          document.title = fileName
        }
      } else {
        document.title = fileName
      }
    } catch (e) {
      console.error('Failed to decode PDF URL', e)
    }
  } else {
    console.error('No PDF URL provided')
  }
})
</script>

<style scoped>
.pdf-viewer-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: auto;
  padding: 0;
  margin: 0;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
