import { reactive } from 'vue'
import type { ProcessForm } from '../types/common'

/**
 * 工序表单处理逻辑组合式函数
 */
export function useProcessForm() {
  // 表单对象
  const form = reactive<ProcessForm>({
    id: null,
    code: '',
    name: '',
    description: ''
  })

  // 表单验证规则
  const rules = {
    code: [
      { required: true, message: '请输入工序代码', trigger: 'blur' },
      { max: 20, message: '最大长度不能超过20个字符', trigger: 'blur' }
    ],
    name: [
      { required: true, message: '请输入工序名称', trigger: 'blur' },
      { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
    ],
    description: [
      { max: 200, message: '最大长度不能超过200个字符', trigger: 'blur' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.code = ''
    form.name = ''
    form.description = ''
  }

  return {
    form,
    rules,
    resetForm
  }
}
