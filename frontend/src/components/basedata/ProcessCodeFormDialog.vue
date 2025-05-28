<template>
  <el-dialog :model-value="visible" :title="title" width="600px" @close="handleClose"
    @opened="$emit('opened')"
    @update:model-value="(val: boolean) => $emit('update:visible', val)">
    <el-form :ref="props.formRef" :model="localForm" :rules="rules" label-width="100px" label-position="left"
      class="form-container">
      <el-form-item label="产品类" prop="category">
        <el-select v-model="localForm.category" placeholder="请选择产品类" filterable class="form-select" v-if="localForm"
          @change="handleCategoryChange">
          <el-option
            v-for="item in categories"
            :key="typeof item.id === 'string' ? Number(item.id) : item.id"
            :label="item?.display_name + '（' + item?.code + '）'"
            :value="typeof item.id === 'string' ? Number(item.id) : item.id"
          />
        </el-select>
        <span v-else>正在加载产品类...</span>
      </el-form-item>
      
      <el-form-item label="说明" prop="description">
        <el-input v-model="localForm.description" class="form-input" v-if="localForm" />
      </el-form-item>

      <el-form-item label="版本" prop="version">
        <el-select v-model="localForm.version" placeholder="请选择版本" class="form-select" v-if="localForm" @change="handleVersionChange">
          <el-option v-for="v in ['A', 'B', 'C', 'D', 'E', 'F', 'G']" :key="v" :label="v" :value="v" />
        </el-select>
      </el-form-item>

      <el-form-item label="工艺流程代码" prop="code">
        <el-input v-model="localForm.code" class="form-input" v-if="localForm" />
      </el-form-item>

      <el-form-item label="工艺PDF">
        <div v-if="localForm?.process_pdf && !localPdfFiles.length" class="current-file">
          <span>当前文件：</span>
          <el-link :href="getCorrectPdfViewerUrl(typeof localForm?.process_pdf === 'string' ? localForm?.process_pdf : null)" 
                   target="_blank" 
                   type="primary" 
                   :disabled="!localForm?.process_pdf">
            <el-icon><Document /></el-icon> 查看已上传文件
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
import { ref, watch, onMounted, toRaw, reactive, nextTick } from 'vue'
import { Document } from '@element-plus/icons-vue'
import type { FormInstance, UploadUserFile } from 'element-plus'
import type { ProcessCodeForm, ProductCategory } from '../../types/common'
// @ts-ignore - Vue SFC没有默认导出，但在Vue项目中可以正常使用
import PdfPreview from '../common/PdfPreview.vue'
import { getCorrectPdfViewerUrl } from '../../utils/pdfHelpers'

console.log('ProcessCodeFormDialog component setup');

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: ProcessCodeForm
  rules: Record<string, any>
  categories?: ProductCategory[]
  pdfFiles: UploadUserFile[] //明确类型为 UploadUserFile[]
  formRef: any // 新增，Ref<FormInstance|undefined>
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

const getDefaultForm = (): ProcessCodeForm => ({
  id: null,
  code: '',
  description: '',
  version: '',
  process_pdf: '',
  category: null,
})

// 使用 reactive 创建深层响应式对象
const localForm = reactive<ProcessCodeForm>(getDefaultForm())

// 弹窗打开时，深拷贝props.form的属性到localForm，关闭时显式重置localForm属性
watch(() => props.visible, (visible) => {
  console.log('[ProcessCodeFormDialog] Watch visible triggered. Visible:', visible)
  if (visible) {
    // 深度合并属性到现有的localForm对象
    // 先重置确保结构完整，再合并传入的数据
    Object.assign(localForm, getDefaultForm(), JSON.parse(JSON.stringify(toRaw(props.form))))
    localPdfFiles.value = Array.isArray(props.pdfFiles) ? [...props.pdfFiles] : []
    console.log('[ProcessCodeFormDialog] localForm after sync (open):', JSON.parse(JSON.stringify(toRaw(localForm))))
    console.log('[ProcessCodeFormDialog] categories prop:', props.categories)
    console.log('[ProcessCodeFormDialog] localForm.category value and type:', localForm.category, typeof localForm.category)
  } else {
    // 弹窗关闭时显式重置localForm属性
    Object.assign(localForm, getDefaultForm())
    localPdfFiles.value = []
    console.log('[ProcessCodeFormDialog] localForm reset on close:', JSON.parse(JSON.stringify(toRaw(localForm))))
  }
}, { immediate: true })

// 自动生成工艺流程代码（产品类代码-版本）- 监听localForm变化
watch(
  () => [localForm?.category, localForm?.version, props.categories],
  ([categoryId, version, categories]) => {
    console.log('[ProcessCodeFormDialog] Auto-generate watch triggered. CategoryId:', categoryId, ' Version:', version, ' localForm.id:', localForm?.id)
    console.log('[ProcessCodeFormDialog] Auto-generate watch localForm.category value and type:', localForm?.category, typeof localForm?.category)
    // 只有在新增模式下才自动生成代码和说明
    if (localForm?.id === null && categoryId && version && Array.isArray(categories) && categories.length > 0) {
      const category = categories.find((c: any) => c.id === categoryId)
      if (category) {
        // 使用找到的产品类代码和名称来生成代码和描述
        localForm.code = `P-${category.code}-${version}`
        localForm.description = `${category.display_name}-${version}`
        console.log('[ProcessCodeFormDialog] Generated code based on category:', localForm.code, ' description:', localForm.description)
      }
    } else if (localForm && (localForm.code || localForm.description)) { // 如果不是新增模式且有值，且category或version变为空，则清空
         if (!categoryId || !version) {
            localForm.code = ''
            localForm.description = ''
            console.log('[ProcessCodeFormDialog] Cleared code and description due to category/version empty')
         }
    }
  },
  { immediate: true, deep: true } // 深度监听localForm属性
)

// 文件列表更新处理 (由 el-upload 触发)
const handleFileListUpdate = (files: UploadUserFile[]) => {
  localPdfFiles.value = files;
  // 将本地文件列表的变化同步给父组件 (使用 v-model:pdf-files)
  emit('update:pdfFiles', files);
};

// 组件加载时初始化 (可以移除，因为 visible 的 watcher 带有 immediate: true)
// onMounted(() => {
//   console.log('ProcessCodeFormDialog mounted');
//   // Initial sync of pdfFiles - already handled by the immediate watcher
// });

// Methods
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
  // 关闭时显式重置localForm属性
  Object.assign(localForm, getDefaultForm())
  localPdfFiles.value = []
  console.log('[ProcessCodeFormDialog] localForm reset on handleClose:', JSON.parse(JSON.stringify(toRaw(localForm))))
}

const handleCategoryChange = (categoryId: number) => {
  emit('category-change', categoryId)
}

const handleVersionChange = (version: string) => {
  emit('version-change', version)
}

const handleSave = async () => {
  if (!props.formRef?.value) return
  await props.formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    // 保存前同步localForm的属性到props.form
    Object.assign(props.form, toRaw(localForm))
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

<script lang="ts">
export default {
  name: 'ProcessCodeFormDialog'
}
</script>
