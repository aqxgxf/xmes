import { reactive } from 'vue'
import type { ProductProcessCodeForm } from '../types/common'

/**
 * 产品工艺关联表单处理逻辑组合式函数
 */
export function useProductProcessCodeForm() {
  // 表单对象
  const form = reactive<ProductProcessCodeForm>({
    id: null,
    product: 0,
    process_code: 0,
    is_default: false,
    remark: ''
  })

  // 表单验证规则
  const rules = {
    product: [
      { required: true, message: '请选择产品', trigger: 'change' }
    ],
    process_code: [
      { required: true, message: '请选择工艺流程代码', trigger: 'change' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.product = 0
    form.process_code = 0
    form.is_default = false
    form.remark = ''
  }

  // 填充表单数据
  const fillForm = (item: any) => {
    form.id = item.id
    form.product = item.product
    form.process_code = item.process_code
    form.is_default = item.is_default
    form.remark = item.remark || ''
  }

  return {
    form,
    rules,
    resetForm,
    fillForm
  }
}
