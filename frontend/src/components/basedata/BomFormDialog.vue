<template>
  <el-dialog :model-value="visible" :title="title" width="800px" destroy-on-close @close="handleClose">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" label-position="left">
      <el-form-item label="产品" prop="product">
        <div class="product-select-container">
          <el-select v-model="form.product" placeholder="请选择产品" filterable class="product-select"
            @change="(val: number) => handleProductChange(val)">
            <el-option v-for="item in products" :key="item.id" :label="`${item.name} (${item.code || ''})`"
              :value="item.id" />
          </el-select>
        </div>
      </el-form-item>

      <el-form-item label="版本" prop="version">
        <el-select v-model="form.version" placeholder="请选择版本" class="version-select"
          @change="(val: string) => handleVersionChange(val)">
          <el-option v-for="v in versionOptions" :key="v" :label="v" :value="v" />
        </el-select>
      </el-form-item>

      <el-form-item label="BOM代码" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import type { BomForm, Product } from '../../types/common'

// Props
const props = defineProps<{
  visible: boolean
  title: string
  loading: boolean
  form: BomForm
  rules: Record<string, any>
  products: Product[]
  versionOptions: string[]
  product?: number | null
  version?: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'update:product'): void
  (e: 'update:version'): void
}>()

// 表单引用
const formRef = ref<FormInstance>()

// 监听产品和版本的变化，自动生成BOM代码和描述
watch(() => props.form.product, (newVal) => {
  if (newVal && props.form.version) {
    generateBomCode()
  }
})

watch(() => props.form.version, (newVal) => {
  if (newVal && props.form.product) {
    generateBomCode()
  }
})

// 生成BOM代码和描述
const generateBomCode = () => {
  console.log('组件内直接生成BOM代码', props.form.product, props.form.version)
  // 查找产品
  const product = props.products.find(p => p.id === props.form.product)

  if (product && props.form.version) {
    // 直接设置BOM代码和描述
    console.log('找到产品:', product.code, product.name)
    props.form.name = `${product.code}-${props.form.version}`

    // 只有当描述为空时才自动生成描述
    if (!props.form.description || props.form.description === '') {
      props.form.description = `${product.name}-${props.form.version}`
    }

    console.log('已生成BOM代码和描述:', props.form.name, props.form.description)
  }
}

// Methods
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

// 处理产品变更
const handleProductChange = (val: number) => {
  console.log('组件内产品变更:', val)
  // 直接在组件内处理
  if (val) {
    setTimeout(() => {
      generateBomCode()
    }, 100)
  }
  emit('update:product')
}

// 处理版本变更
const handleVersionChange = (val: string) => {
  console.log('组件内版本变更:', val)
  // 直接在组件内处理
  if (val) {
    setTimeout(() => {
      generateBomCode()
    }, 100)
  }
  emit('update:version')
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
.product-select-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-select {
  width: 100%;
}

.version-select {
  width: 120px;
}
</style>
