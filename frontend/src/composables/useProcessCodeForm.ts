import { reactive, ref, watchEffect } from 'vue'
import type { UploadUserFile } from 'element-plus'
import type { ProcessCodeForm, Product, ProductCategory } from '../types/common'

/**
 * 工艺流程代码表单处理逻辑组合式函数
 */
export function useProcessCodeForm() {
  // 表单对象
  const form = reactive<ProcessCodeForm>({
    id: null,
    code: '',
    description: '',
    version: '',
    process_pdf: '',
    category: null
  })

  // 表单验证规则
  const rules = {
    code: [
      { required: true, message: '请输入工艺流程代码', trigger: 'blur' },
      { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
    ],
    version: [
      { required: true, message: '请选择版本', trigger: 'change' }
    ],
    category: [
      { required: true, message: '请选择产品类', trigger: 'change' }
    ]
  }

  // PDF文件列表
  const pdfFileList = ref<UploadUserFile[]>([])

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.code = ''
    form.description = ''
    form.version = ''
    form.process_pdf = ''
    form.category = null
    pdfFileList.value = []
  }

  // 自动更新code和description（基于产品类和版本）
  const updateCodeByProductAndVersion = (categories: ProductCategory[] = []) => {
    if (form.category && form.version) {
      // 根据产品类生成代码
      const category = categories.find(c => c.id === form.category)
      if (category) {
        form.code = category.code + '-' + form.version
        if (form.description === '' && form.code !== '') {
          form.description = category?.code + '-' + category?.display_name + '-' + form.version
        }
      }
    } else {
      form.code = ''
    }
  }

  // 根据产品类更新代码
  const updateCodeByCategory = (categoryId: number, categories: ProductCategory[], version: string = '') => {
    form.category = categoryId
    
    if (version) {
      form.version = version
    }
    
    if (form.category && form.version) {
      const category = categories.find(c => c.id === form.category)
      if (category) {
        form.code = category.code + '-' + form.version
        if (form.description === '' && form.code !== '') {
          form.description = category?.code + '-' + category?.display_name + '-' + form.version
        }
      }
    }
  }

  return {
    form,
    rules,
    pdfFileList,
    resetForm,
    updateCodeByProductAndVersion,
    updateCodeByCategory
  }
}
