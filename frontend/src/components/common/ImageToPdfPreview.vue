<template>
  <div>
    <input type="file" accept="image/*,application/pdf" @change="onFileChange" />
    <div v-if="previewType === 'image'">
      <img :src="previewUrl" style="max-width:100%;max-height:400px;" />
    </div>
    <iframe v-else-if="previewType === 'pdf'" :src="previewUrl" width="100%" height="600px" frameborder="0"></iframe>
    <div v-else-if="previewType === 'none' && previewUrl">
      <span style="color:red;">不支持的文件类型</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const previewUrl = ref<string>()
const previewType = ref<'image' | 'pdf' | 'none'>('none')

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files || input.files.length === 0) {
    previewUrl.value = undefined
    previewType.value = 'none'
    return
  }
  const file = input.files[0]
  if (file.type.startsWith('image/')) {
    previewUrl.value = URL.createObjectURL(file)
    previewType.value = 'image'
  } else if (file.type === 'application/pdf') {
    previewUrl.value = URL.createObjectURL(file)
    previewType.value = 'pdf'
  } else {
    previewUrl.value = undefined
    previewType.value = 'none'
    alert('仅支持图片或PDF文件')
  }
}
</script>

<script lang="ts">
export default {}
</script> 