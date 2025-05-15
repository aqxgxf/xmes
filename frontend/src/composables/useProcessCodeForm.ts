import { reactive, ref, watchEffect } from 'vue'
import type { UploadUserFile } from 'element-plus'
import type { ProcessCodeForm, Product } from '../types/common'

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
    product: null
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
    product: [
      { required: true, message: '请选择产品', trigger: 'change' }
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
    form.product = null
    pdfFileList.value = []
  }

  // 自动更新code和description（基于产品和版本）
  const updateCodeByProductAndVersion = (products: Product[]) => {
    const product = products.find(p => p.id === form.product)
    if (product && form.version) {
      form.code = product.code + '-' + form.version
    } else {
      form.code = ''
    }
    if (form.description === '' && form.code !== '') {
      form.description = product?.code + '-' + product?.name + '-' + form.version
    }
  }

  return {
    form,
    rules,
    pdfFileList,
    resetForm,
    updateCodeByProductAndVersion
  }
}
