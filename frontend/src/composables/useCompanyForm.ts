import { reactive } from 'vue'
import type { CompanyForm } from '../types/index'

/**
 * 公司表单处理逻辑组合式函数
 */
export function useCompanyForm() {
  // 表单对象
  const form = reactive<CompanyForm>({
    id: null,
    name: '',
    code: '',
    address: '',
    contact: '',
    phone: ''
  })

  // 表单验证规则
  const rules = {
    name: [
      { required: true, message: '请输入客户名称', trigger: 'blur' },
      { min: 1, max: 50, message: '长度在1到50个字符', trigger: 'blur' }
    ],
    code: [
      { required: true, message: '请输入客户代码', trigger: 'blur' },
      { min: 1, max: 20, message: '长度在1到20个字符', trigger: 'blur' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.name = ''
    form.code = ''
    form.address = ''
    form.contact = ''
    form.phone = ''
  }

  // 从对象加载表单数据
  const loadFormData = (data: any) => {
    form.id = data?.id || null
    form.name = data?.name || ''
    form.code = data?.code || ''
    form.address = data?.address || ''
    form.contact = data?.contact || ''
    form.phone = data?.phone || ''
  }

  return {
    form,
    rules,
    resetForm,
    loadFormData
  }
}
