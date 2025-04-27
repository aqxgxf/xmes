<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工单管理</span>
      <el-button type="primary" @click="openAddWorkOrder">新增工单</el-button>
      <el-button type="success" @click="openCreateByOrderDialog">通过订单新增</el-button>
    </div>
    <el-table :data="workorders" style="width:100%;margin-top:16px;">
      <el-table-column prop="workorder_no" label="工单号" />
      <el-table-column prop="order" label="订单号" />
      <el-table-column prop="product" label="产品" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column prop="process_code" label="工艺流程代码" />
      <el-table-column prop="plan_start" label="计划开始" />
      <el-table-column prop="plan_end" label="计划结束" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="remark" label="备注" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click.stop="editWorkOrder(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click.stop="deleteWorkOrder(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showWorkOrderDialog" :title="workOrderForm.id ? '编辑工单' : '新增工单'" width="600px" @close="cancelWorkOrderEdit">
      <el-form :model="workOrderForm" :rules="workOrderFormRules" ref="workOrderFormRef" label-width="100px">
        <el-form-item label="工单号" prop="workorder_no"><el-input v-model="workOrderForm.workorder_no" /></el-form-item>
        <el-form-item label="订单号" prop="order">
          <el-select v-model="workOrderForm.order" filterable placeholder="请选择订单号" style="width:100%">
            <el-option v-for="o in orders" :key="o.id" :label="o.order_no" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-select v-model="workOrderForm.product" filterable placeholder="请选择产品" style="width:100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity"><el-input-number v-model="workOrderForm.quantity" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select v-model="workOrderForm.process_code" filterable placeholder="请选择工艺流程" style="width:100%">
            <el-option v-for="c in processCodes" :key="c.id" :label="c.code + ' ' + c.version" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始" prop="plan_start"><el-date-picker v-model="workOrderForm.plan_start" type="datetime" style="width:100%" /></el-form-item>
        <el-form-item label="计划结束" prop="plan_end"><el-date-picker v-model="workOrderForm.plan_end" type="datetime" style="width:100%" /></el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="workOrderForm.status" style="width:100%">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark"><el-input v-model="workOrderForm.remark" type="text" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelWorkOrderEdit">取消</el-button>
        <el-button type="primary" @click="saveOrUpdateWorkOrder">保存工单</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showCreateByOrderDialog" title="通过订单新增工单" width="600px">
      <el-table :data="ordersWithoutWorkOrder" style="width:100%;margin-bottom:12px;" row-key="id">
        <el-table-column prop="order_no" label="订单号" />
        <el-table-column prop="company_name" label="公司" />
        <el-table-column prop="order_date" label="下单日期" />
        <el-table-column prop="total_amount" label="订单金额合计" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="primary" @click.stop="createWorkOrderByOrder(scope.row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showCreateByOrderDialog=false">关闭</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const workorders = ref([])
const products = ref<any[]>([])
const processCodes = ref<any[]>([])
const orders = ref<any[]>([])
const showWorkOrderDialog = ref(false)
const workOrderForm = ref<any>({ id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' })
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

function fetchWorkOrders() {
  axios.get('/api/workorders/').then(res => {
    workorders.value = res.data
  })
}
function openAddWorkOrder() {
  workOrderForm.value = { id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' }
  showWorkOrderDialog.value = true
}
function editWorkOrder(row: any) {
  workOrderForm.value = { ...row }
  showWorkOrderDialog.value = true
}
function cancelWorkOrderEdit() {
  showWorkOrderDialog.value = false
  workOrderForm.value = { id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' }
  fetchWorkOrders()
}
async function saveOrUpdateWorkOrder() {
  let res
  if (workOrderForm.value.id) {
    res = await axios.put(`/api/workorders/${workOrderForm.value.id}/`, workOrderForm.value)
    ElMessage.success('工单更新成功')
  } else {
    res = await axios.post('/api/workorders/', workOrderForm.value)
    ElMessage.success('工单创建成功')
  }
  fetchWorkOrders()
}
async function deleteWorkOrder(row: any) {
  await axios.delete(`/api/workorders/${row.id}/`)
  ElMessage.success('工单已删除')
  fetchWorkOrders()
}
onMounted(() => {
  fetchWorkOrders()
  axios.get('/api/products/').then(res => {
    products.value = res.data.results || res.data
  })
  axios.get('/api/process-codes/').then(res => {
    processCodes.value = res.data.results || res.data
  })
  axios.get('/api/orders/').then(res => {
    orders.value = res.data
  })
})
const workOrderFormRules = {
  workorder_no: [{ required: true, message: '工单号必填', trigger: 'blur' }],
  order: [{ required: true, message: '订单号必选', trigger: 'change' }],
  product: [{ required: true, message: '产品必选', trigger: 'change' }],
  quantity: [{ required: true, message: '数量必填', trigger: 'blur' }],
  process_code: [{ required: true, message: '工艺流程必选', trigger: 'change' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}

const showCreateByOrderDialog = ref(false)
const ordersWithoutWorkOrder = ref<any[]>([])
function openCreateByOrderDialog() {
  axios.get('/api/orders-without-workorder/').then(res => {
    ordersWithoutWorkOrder.value = res.data
    showCreateByOrderDialog.value = true
  })
}
async function createWorkOrderByOrder(order: any) {
  const loading = ElMessage({ message: '正在创建工单...', type: 'info', duration: 0 })
  try {
    const res = await axios.post('/api/workorders/create-by-order/', { order_id: order.id }, {
      headers: {
        'Content-Type': 'application/json',
      }
    })
    showCreateByOrderDialog.value = false
    await fetchWorkOrders()
    if (res.data && res.data.id) {
      editWorkOrder(res.data)
      ElMessage.success('工单已自动生成，请补充完善后保存')
    } else {
      ElMessage.success('工单已自动生成')
    }
  } catch (e: any) {
    ElMessage.error('创建失败: ' + (e?.response?.data?.detail || e.message || '未知错误'))
  } finally {
    loading.close && loading.close()
  }
}
</script>
<style>
@import '/src/style.css';
</style>
