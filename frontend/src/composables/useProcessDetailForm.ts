import { reactive } from 'vue'
import type { ProcessDetailForm } from '../types/common'

/**
 * 工艺流程明细表单处理逻辑组合式函数
 */
export function useProcessDetailForm(processCodeId: number) {
  // 表单对象
  const form = reactive<ProcessDetailForm>({
    id: null,
    process_code: Number(processCodeId),
    step_no: 10,
    step: 0,
    machine_time: 0,
    labor_time: 0,
    required_equipment: '',
    remark: ''
  })

  // 表单验证规则
  const rules = {
    step_no: [
      { required: true, message: '请输入步骤号', trigger: 'blur' }
    ],
    step: [
      { required: true, message: '请选择工序', trigger: 'change' }
    ],
    machine_time: [
      { required: true, message: '请输入设备时间', trigger: 'blur' }
    ],
    labor_time: [
      { required: true, message: '请输入人工时间', trigger: 'blur' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.process_code = Number(processCodeId)
    form.step_no = getNextStepNo([])
    form.step = 0
    form.machine_time = 0
    form.labor_time = 0
    form.required_equipment = ''
    form.remark = ''
  }

  // 获取下一个步骤号
  const getNextStepNo = (details: any[]): number => {
    // 如果没有明细，从10开始
    if (!details || details.length === 0) {
      return 10
    }

    // 找到最大的步骤号，然后+10
    const maxStep = Math.max(...details.map(d => d.step_no))
    return maxStep + 10
  }

  // 填充表单数据
  const fillForm = (detail: any) => {
    form.id = detail.id
    form.process_code = Number(processCodeId)
    form.step_no = detail.step_no
    form.step = detail.step
    form.machine_time = detail.machine_time
    form.labor_time = detail.labor_time
    form.required_equipment = detail.required_equipment || ''
    form.remark = detail.remark || ''
  }

  return {
    form,
    rules,
    resetForm,
    getNextStepNo,
    fillForm
  }
}
