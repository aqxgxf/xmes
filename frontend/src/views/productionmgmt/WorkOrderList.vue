<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工单管理</span>
      <el-button type="primary" @click="openAddWorkOrder">新增工单</el-button>
    </div>
    <el-table :data="workorders" style="width:100%;margin-top:16px;" @row-click="editWorkOrder">
      <el-table-column prop="workorder_no" label="工单号" />
      <el-table-column prop="order" label="订单号" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column prop="updated_at" label="更新时间" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click.stop="editWorkOrder(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click.stop="deleteWorkOrder(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showWorkOrderDialog" :title="workOrderForm.id ? '编辑工单' : '新增工单'" width="90vw" top="2vh" fullscreen @close="cancelWorkOrderEdit">
      <div>
        <el-form :model="workOrderForm" :rules="workOrderFormRules" ref="workOrderFormRef" label-width="100px" style="display:flex;flex-wrap:wrap;gap:16px;max-width:100%;">
          <el-form-item label="工单号" style="flex:1;min-width:220px;max-width:280px;"><el-input v-model="workOrderForm.workorder_no" /></el-form-item>
          <el-form-item label="订单号" style="flex:1;min-width:160px;max-width:220px;" required>
            <el-select v-model="workOrderForm.order" filterable placeholder="请选择订单号" style="width:100%">
              <el-option v-for="o in orders" :key="o.id" :label="o.order_no" :value="o.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" style="flex:1;min-width:180px;max-width:220px;">
            <el-select v-model="workOrderForm.status" style="width:100%">
              <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注" style="flex:2;min-width:220px;max-width:400px;">
            <el-input v-model="workOrderForm.remark" type="text" />
          </el-form-item>
        </el-form>
        <h3 style="margin-top:12px;">工单明细</h3>
        <el-table
          :data="workOrderDetails"
          border
          style="width:100%;margin-top:8px;"
          :header-cell-style="{textAlign:'center'}"
          :cell-style="{textAlign:'center'}"
          :table-layout="'auto'"
        >
          <el-table-column prop="product" label="产品" width="260" align="center">
            <template #default="scope">
              <el-select v-model="scope.row.product" size="small" filterable placeholder="请选择产品" style="width:220px">
                <el-option v-for="p in orderProducts" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" align="center">
            <template #default="scope">
              <el-input-number v-model="scope.row.quantity" :min="0" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="process_code" label="工艺流程代码" width="220" align="center">
            <template #default="scope">
              <el-input v-model="scope.row.process_code" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="plan_start" label="计划开始" width="100" align="center">
            <template #default="scope">
              <el-date-picker v-model="scope.row.plan_start" type="datetime" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="plan_end" label="计划结束" width="100" align="center">
            <template #default="scope">
              <el-date-picker v-model="scope.row.plan_end" type="datetime" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="scope">
              <el-select v-model="scope.row.status" size="small" style="width:90px">
                <el-option v-for="item in detailStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" align="center">
            <template #default="scope">
              <div style="display:flex;gap:4px;justify-content:center;align-items:center;">
                <el-button size="small" type="primary" @click="saveSingleDetail(scope.row)">保存</el-button>
                <el-button size="small" type="danger" @click="removeDetail(scope.$index)">删除</el-button>
                <el-button size="small" type="success" @click="addDetailAfter(scope.$index)">增加</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top:12px;">
          <el-button type="primary" @click="addDetail">新增明细行</el-button>
          <el-button type="success" @click="saveAllDetails" :disabled="!workOrderForm.id">保存所有明细</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelWorkOrderEdit">取消</el-button>
        <el-button type="primary" @click="saveOrUpdateWorkOrder">保存工单</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const workorders = ref([])
interface Product { id: number; name: string }
interface WorkOrderDetail {
  id?: number;
  workorder: number | null;
  product: string;
  quantity: number;
  process_code: string;
  plan_start: string;
  plan_end: string;
  status: string;
  remark: string;
}
const products = ref<Product[]>([])
const orderProducts = ref<Product[]>([])
const workOrderDetails = ref<WorkOrderDetail[]>([])
const showWorkOrderDialog = ref(false)
const workOrderForm = ref({ id: null, workorder_no: '', order: '', status: '', remark: '' })
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]
const detailStatusOptions = [
  { value: 'pending', label: '待生产' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]
const orders = ref<{id:number,order_no:string}[]>([])

function fetchWorkOrders() {
  axios.get('/api/workorders/').then(res => {
    workorders.value = res.data
  })
}
function openAddWorkOrder() {
  workOrderForm.value = { id: null, workorder_no: '', order: '', status: '', remark: '' }
  workOrderDetails.value = []
  showWorkOrderDialog.value = true
}
async function editWorkOrder(row: any) {
  workOrderForm.value = { ...row }
  showWorkOrderDialog.value = true
  await nextTick()
  // 获取工单明细
  const res = await axios.get('/api/workorder-details/', { params: { workorder: row.id } })
  workOrderDetails.value = res.data.map((item: any) => ({ ...item }))
  // 获取订单明细的产品
  if (row.order) {
    const orderItemRes = await axios.get('/api/order-items/', { params: { order: row.order } })
    orderProducts.value = (orderItemRes.data || []).map((item: any) => ({ id: item.product, name: item.product_name || item.product }))
  } else {
    orderProducts.value = []
  }
}
function cancelWorkOrderEdit() {
  showWorkOrderDialog.value = false
  workOrderForm.value = { id: null, workorder_no: '', order: '', status: '', remark: '' }
  workOrderDetails.value = []
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
  const workorderId = res?.data?.id || workOrderForm.value.id
  workOrderForm.value.id = workorderId
  // 批量保存明细
  for (const item of workOrderDetails.value) {
    item.workorder = workorderId
    if (item.id) {
      await axios.put(`/api/workorder-details/${item.id}/`, item)
    } else {
      await axios.post('/api/workorder-details/', item)
    }
  }
  fetchWorkOrders()
  // 刷新明细
  const detailRes = await axios.get('/api/workorder-details/', { params: { workorder: workorderId } })
  workOrderDetails.value = detailRes.data.map((item: any) => ({ ...item }))
}
function addDetail() {
  if (!workOrderForm.value.id) {
    ElMessage.warning('请先保存工单再新增明细！')
    return
  }
  workOrderDetails.value.push({
    workorder: workOrderForm.value.id,
    product: '',
    quantity: 0,
    process_code: '',
    plan_start: '',
    plan_end: '',
    status: '',
    remark: ''
  })
}
function addDetailAfter(idx: number) {
  if (!workOrderForm.value.id) {
    ElMessage.warning('请先保存工单再新增明细！')
    return
  }
  workOrderDetails.value.splice(idx + 1, 0, {
    workorder: workOrderForm.value.id,
    product: '',
    quantity: 0,
    process_code: '',
    plan_start: '',
    plan_end: '',
    status: '',
    remark: ''
  })
}
async function removeDetail(idx: number) {
  const item = workOrderDetails.value[idx]
  if (item.id) {
    await axios.delete(`/api/workorder-details/${item.id}/`)
    ElMessage.success('明细已删除')
    const res = await axios.get('/api/workorder-details/', { params: { workorder: workOrderForm.value.id } })
    workOrderDetails.value = res.data.map((item: any) => ({ ...item }))
  } else {
    workOrderDetails.value.splice(idx, 1)
  }
}
async function saveSingleDetail(item: any) {
  item.workorder = workOrderForm.value.id
  if (item.id) {
    await axios.put(`/api/workorder-details/${item.id}/`, item)
  } else {
    await axios.post('/api/workorder-details/', item)
  }
  ElMessage.success('明细已保存')
  const res = await axios.get('/api/workorder-details/', { params: { workorder: workOrderForm.value.id } })
  workOrderDetails.value = res.data.map((item: any) => ({ ...item }))
}
async function saveAllDetails() {
  for (const item of workOrderDetails.value) {
    item.workorder = workOrderForm.value.id
    if (item.id) {
      await axios.put(`/api/workorder-details/${item.id}/`, item)
    } else {
      await axios.post('/api/workorder-details/', item)
    }
  }
  ElMessage.success('所有明细已保存')
  const res = await axios.get('/api/workorder-details/', { params: { workorder: workOrderForm.value.id } })
  workOrderDetails.value = res.data.map((item: any) => ({ ...item }))
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
  axios.get('/api/orders/').then(res => {
    orders.value = res.data
  })
})
const workOrderFormRules = {
  workorder_no: [{ required: true, message: '工单号必填', trigger: 'blur' }],
  order: [{ required: true, message: '订单号必选', trigger: 'change' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}
</script>
<style>
@import '/src/style.css';
</style>
