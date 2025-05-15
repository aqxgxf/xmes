export type WorkOrder = {
  id: number
  workorder_no: string
  order: number
  product: number
  quantity: number
  process_code: number
  plan_start: string
  plan_end: string
  status: string
  remark?: string
  // 可扩展其他字段
}

export type WorkOrderForm = Omit<WorkOrder, 'id'> & { id?: number }
