<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">订单管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="orderSearch" placeholder="筛选订单号/公司" style="width:220px" clearable />
        <el-button type="primary" @click="openAddOrder">新增订单</el-button>
      </div>
    </div>
    <el-table :data="filteredOrders" style="width:100%;margin-top:16px;">
      <el-table-column prop="order_no" label="订单号" />
      <el-table-column prop="company_name" label="公司" />
      <el-table-column prop="order_date" label="下单日期" />
      <el-table-column prop="product_name" label="产品" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column prop="unit_price" label="单价" />
      <el-table-column prop="total_amount" label="订单金额" />
      <el-table-column prop="plan_delivery" label="计划交货期" />
      <el-table-column prop="actual_delivery" label="实际交货期" />
      <el-table-column prop="actual_quantity" label="已交货数量" />
      <el-table-column prop="actual_amount" label="已交货金额" />
      <el-table-column label="操作">
  <template #default="scope">
    <div style="display: flex; gap: 4px;">
      <el-button size="small" @click.stop="editOrder(scope.row)">编辑</el-button>
      <el-button size="small" type="danger" @click.stop="deleteOrder(scope.row)">删除</el-button>
    </div>
  </template>
</el-table-column>
    </el-table>
    <el-dialog v-model="showOrderDialog" :title="orderForm.id ? '编辑订单' : '新增订单'" width="80vw" @close="cancelOrderEdit" :modal-append-to-body="false" class="order-dialog-max">
      <el-form :model="orderForm" label-width="100px" style="margin-top:12px;">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="订单号"><el-input v-model="orderForm.order_no" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="公司"><el-select v-model="orderForm.company" style="width:100%">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="订单类别">
            <el-select v-model="orderForm.order_type" style="width:100%">
              <el-option v-for="opt in orderTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="产品"><el-select v-model="orderForm.product" filterable style="width:100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="下单日期"><el-date-picker v-model="orderForm.order_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="计划交货期"><el-date-picker v-model="orderForm.plan_delivery" type="date" style="width:100%" /></el-form-item></el-col>
         </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="数量"><el-input-number v-model="orderForm.quantity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="单价"><el-input-number v-model="orderForm.unit_price" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="订单金额合计"><el-input v-model="orderForm.total_amount" readonly /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="实际交货期"><el-date-picker v-model="orderForm.actual_delivery" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="已交货数量"><el-input-number v-model="orderForm.actual_quantity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="已交货金额"><el-input-number v-model="orderForm.actual_amount" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="cancelOrderEdit">取消</el-button>
        <el-button type="primary" @click="saveOrUpdateOrder">保存订单</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Company { id: number; name: string }
interface Product { id: number; name: string; price?: number } // 增加 price 字段
interface Order {
  id?: number;
  order_no: string;
  company: number;
  company_name?: string;
  order_date: string;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  amount: number;
  total_amount?: number; // Added this property
  plan_delivery: string;
  actual_delivery?: string;
  actual_quantity?: number;
  actual_amount?: number;
  order_type?: string; // 新增订单类别字段
}

const orders = ref<Order[]>([])
const companies = ref<Company[]>([])
const products = ref<Product[]>([])
const showOrderDialog = ref(false)
const orderForm = ref<Order>({ order_no: '', company: 0, order_date: '', product: 0, quantity: 0, unit_price: 0, amount: 0, total_amount: 0, plan_delivery: '' })
const orderSearch = ref('')
const filteredOrders = computed(() => {
  if (!orderSearch.value) return orders.value
  const kw = orderSearch.value.toLowerCase()
  return orders.value.filter(o =>
    (o.order_no && o.order_no.toLowerCase().includes(kw)) ||
    (o.company_name && o.company_name.toLowerCase().includes(kw))
  )
})

const fetchOrders = async () => {
  const res = await axios.get('/api/orders/')
  orders.value = res.data
}
const fetchCompanies = async () => {
  const res = await axios.get('/api/companies/')
  companies.value = res.data
}
const fetchProducts = async () => {
  const res = await axios.get('/api/products/')
  products.value = res.data.results || res.data
}
const orderTypeOptions = [
  { label: '常规', value: 'normal' },
  { label: '新品', value: 'new' }
]
const openAddOrder = () => {
  const today = new Date().toISOString().slice(0, 10)
  orderForm.value = {
    order_no: '',
    company: companies.value.length > 0 ? companies.value[0].id : 0,
    order_date: today,
    product: products.value.length > 0 ? products.value[0].id : 0,
    quantity: 1,
    unit_price: 0,
    amount: 0,
    total_amount: 0,
    plan_delivery: addDays(today, 30), // 默认常规+30天
    order_type: 'normal', // 默认常规
  }
  showOrderDialog.value = true
}
// 日期加天数工具
function addDays(dateStr: string, days: number) {
  const date = new Date(dateStr)
  date.setDate(date.getDate() + days)
  return date.toISOString().slice(0, 10)
}
// 监听订单类别和下单日期变化，自动设置计划交货期
watch([
  () => orderForm.value.order_type,
  () => orderForm.value.order_date
], ([type, date]) => {
  if (!date) return
  if (type === 'new') {
    orderForm.value.plan_delivery = addDays(date, 20)
  } else {
    orderForm.value.plan_delivery = addDays(date, 30)
  }
})
const editOrder = (row: Order) => {
  orderForm.value = { ...row }
  showOrderDialog.value = true
}

const deleteOrder = async (row: Order) => {
  try {
    await ElMessageBox.confirm('确定要删除该订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await axios.delete(`/api/orders/${row.id}/`)
    ElMessage.success('订单删除成功')
    await fetchOrders()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
const cancelOrderEdit = async () => {
  showOrderDialog.value = false
  orderForm.value = { order_no: '', company: 0, order_date: '', product: 0, quantity: 0, unit_price: 0, amount: 0, total_amount: 0, plan_delivery: '' }
  await fetchOrders()
}
const saveOrUpdateOrder = async () => {
  // 自动计算订单金额合计
  orderForm.value.total_amount = Number(orderForm.value.quantity) * Number(orderForm.value.unit_price)
  try {
    if (orderForm.value.id) {
      await axios.put(`/api/orders/${orderForm.value.id}/`, orderForm.value)
      ElMessage.success('订单更新成功')
    } else {
      await axios.post('/api/orders/', orderForm.value)
      ElMessage.success('订单创建成功')
    }
    showOrderDialog.value = false
    await fetchOrders()
  } catch (e: any) {
    // 处理后端字段级错误
    const detail = e?.response?.data
    if (typeof detail === 'object' && detail !== null) {
      Object.entries(detail).forEach(([field, msg]) => {
        if (Array.isArray(msg)) {
          msg.forEach(m => ElMessage.error(`${field}: ${m}`))
        } else {
          ElMessage.error(`${field}: ${msg}`)
        }
      })
    } else {
      ElMessage.error(detail || '保存失败')
    }
  }
}
watch(() => [orderForm.value.quantity, orderForm.value.unit_price], () => {
  orderForm.value.total_amount = Number(orderForm.value.quantity) * Number(orderForm.value.unit_price)
})
// 监听产品选择，自动带入单价
watch(() => orderForm.value.product, (newProductId) => {
  const p = products.value.find(p => p.id === newProductId)
  if (p && p.price !== undefined) {
    orderForm.value.unit_price = Number(p.price)
  }
})
// 实际交货金额自动计算
watch(() => [orderForm.value.actual_quantity, orderForm.value.unit_price], () => {
  orderForm.value.actual_amount = Number(orderForm.value.actual_quantity || 0) * Number(orderForm.value.unit_price || 0)
})
onMounted(() => {
  fetchOrders()
  fetchCompanies()
  fetchProducts()
})
</script>
<style>
@import '/src/style.css';
.order-dialog-max .el-dialog__body {
  padding: 12px 24px 0 24px;
}
</style>
