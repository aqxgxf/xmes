import { ref } from 'vue'
import type { WorkOrderForm } from '../types/productionmgmt'
import { useWorkOrderStore } from '../stores/workOrderStore'
import { ElMessage } from 'element-plus'

export const useWorkOrderForm = () => {
  const store = useWorkOrderStore()
  const form = ref<WorkOrderForm>({
    workorder_no: '',
    order: 0,
    product: 0,
    quantity: 0,
    process_code: 0,
    plan_start: '',
    plan_end: '',
    status: '',
    remark: ''
  })
  const reset = () => {
    form.value = {
      workorder_no: '',
      order: 0,
      product: 0,
      quantity: 0,
      process_code: 0,
      plan_start: '',
      plan_end: '',
      status: '',
      remark: ''
    }
  }
  const save = async () => {
    try {
      if (form.value.id) {
        await store.update(form.value.id, form.value)
        ElMessage.success('工单更新成功')
      } else {
        await store.create(form.value)
        ElMessage.success('工单创建成功')
      }
      reset()
    } catch (e: any) {
      ElMessage.error(e.message || '保存失败')
    }
  }
  return { form, save, reset }
}
