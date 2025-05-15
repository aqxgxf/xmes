import { reactive } from 'vue'
import type { BomDetailForm } from '../types/common'

/**
 * BOM明细表单处理逻辑组合式函数
 */
export function useBomDetailForm(initialBomId: number | null = null) {
  // 表单对象
  const form = reactive<BomDetailForm>({
    id: null,
    bom: initialBomId,
    material: null,
    quantity: 1,
    remark: ''
  })

  // 表单验证规则
  const rules = {
    bom: [
      { required: true, message: '请选择BOM', trigger: 'change' }
    ],
    material: [
      { required: true, message: '请选择物料', trigger: 'change' }
    ],
    quantity: [
      { required: true, message: '请输入用量', trigger: 'blur' },
      { type: 'number', min: 0.01, message: '用量必须大于0', trigger: 'blur' }
    ]
  }

  // 重置表单
  const resetForm = (bomId: number | null = null) => {
    form.id = null
    form.bom = bomId || initialBomId
    form.material = null
    form.quantity = 1
    form.remark = ''
  }

  // 填充表单数据
  const fillForm = (detail: any) => {
    form.id = detail.id

    // 处理ID可能是字符串的情况
    form.bom = typeof detail.bom === 'string' ? Number(detail.bom) : detail.bom
    form.material = typeof detail.material === 'string' ? Number(detail.material) : detail.material

    form.quantity = detail.quantity
    form.remark = detail.remark || ''
  }

  return {
    form,
    rules,
    resetForm,
    fillForm
  }
}
