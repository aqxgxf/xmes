<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">订单管理</span>
      <el-button type="primary" @click="openAddOrder">新增订单</el-button>
    </div>
    <el-table :data="orders" style="width:100%;margin-top:16px;" @row-click="selectOrder">
      <el-table-column prop="order_no" label="订单号" />
      <el-table-column prop="company_name" label="公司" />
      <el-table-column prop="order_date" label="下单日期" />
      <el-table-column prop="total_amount" label="订单金额合计" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click.stop="editOrder(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAddOrder" title="新增订单">
      <el-form :model="orderForm">
        <el-form-item label="订单号"><el-input v-model="orderForm.order_no" /></el-form-item>
        <el-form-item label="公司">
          <el-select v-model="orderForm.company">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="下单日期"><el-date-picker v-model="orderForm.order_date" type="date" /></el-form-item>
        <el-form-item label="订单金额合计"><el-input v-model="orderForm.total_amount" type="number" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddOrder=false">取消</el-button>
        <el-button type="primary" @click="saveOrder">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEditOrder" title="编辑订单">
      <el-form :model="orderForm">
        <el-form-item label="订单号"><el-input v-model="orderForm.order_no" /></el-form-item>
        <el-form-item label="公司">
          <el-select v-model="orderForm.company">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="下单日期"><el-date-picker v-model="orderForm.order_date" type="date" /></el-form-item>
        <el-form-item label="订单金额合计"><el-input v-model="orderForm.total_amount" type="number" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditOrder=false">取消</el-button>
        <el-button type="primary" @click="updateOrder">保存</el-button>
      </template>
    </el-dialog>
    <div v-if="selectedOrder" style="margin-top:32px;">
      <h3>订单明细（{{ selectedOrder.order_no }}）</h3>
      <el-button type="primary" @click="openAddItem">新增明细</el-button>
      <el-table :data="orderItems" style="width:100%;margin-top:8px;">
        <el-table-column prop="item_no" label="订单项" />
        <el-table-column prop="product_name" label="产品" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="unit_price" label="单价" />
        <el-table-column prop="amount" label="金额小计" />
        <el-table-column prop="plan_delivery" label="计划交货期" />
        <el-table-column prop="actual_delivery" label="实际交货期" />
        <el-table-column prop="actual_quantity" label="实际交货数量" />
        <el-table-column prop="actual_amount" label="实际交货金额" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="editItem(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-dialog v-model="showAddItem" title="新增明细">
        <el-form :model="itemForm">
          <el-form-item label="订单项"><el-input v-model="itemForm.item_no" type="number" /></el-form-item>
          <el-form-item label="产品">
            <el-select v-model="itemForm.product">
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="数量"><el-input v-model="itemForm.quantity" type="number" /></el-form-item>
          <el-form-item label="单价"><el-input v-model="itemForm.unit_price" type="number" /></el-form-item>
          <el-form-item label="金额小计"><el-input v-model="itemForm.amount" type="number" /></el-form-item>
          <el-form-item label="计划交货期"><el-date-picker v-model="itemForm.plan_delivery" type="date" /></el-form-item>
          <el-form-item label="实际交货期"><el-date-picker v-model="itemForm.actual_delivery" type="date" /></el-form-item>
          <el-form-item label="实际交货数量"><el-input v-model="itemForm.actual_quantity" type="number" /></el-form-item>
          <el-form-item label="实际交货金额"><el-input v-model="itemForm.actual_amount" type="number" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddItem=false">取消</el-button>
          <el-button type="primary" @click="saveItem">保存</el-button>
        </template>
      </el-dialog>
      <el-dialog v-model="showEditItem" title="编辑明细">
        <el-form :model="itemForm">
          <el-form-item label="订单项"><el-input v-model="itemForm.item_no" type="number" /></el-form-item>
          <el-form-item label="产品">
            <el-select v-model="itemForm.product">
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="数量"><el-input v-model="itemForm.quantity" type="number" /></el-form-item>
          <el-form-item label="单价"><el-input v-model="itemForm.unit_price" type="number" /></el-form-item>
          <el-form-item label="金额小计"><el-input v-model="itemForm.amount" type="number" /></el-form-item>
          <el-form-item label="计划交货期"><el-date-picker v-model="itemForm.plan_delivery" type="date" /></el-form-item>
          <el-form-item label="实际交货期"><el-date-picker v-model="itemForm.actual_delivery" type="date" /></el-form-item>
          <el-form-item label="实际交货数量"><el-input v-model="itemForm.actual_quantity" type="number" /></el-form-item>
          <el-form-item label="实际交货金额"><el-input v-model="itemForm.actual_amount" type="number" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showEditItem=false">取消</el-button>
          <el-button type="primary" @click="updateItem">保存</el-button>
        </template>
      </el-dialog>
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const orders = ref([])
const companies = ref([])
const products = ref([])
const orderItems = ref([])
const selectedOrder = ref<any>(null)
const showAddOrder = ref(false)
const showEditOrder = ref(false)
const showAddItem = ref(false)
const showEditItem = ref(false)
const orderForm = ref({ order_no: '', company: '', order_date: '', total_amount: '' })
const itemForm = ref({ order: '', item_no: '', product: '', quantity: '', unit_price: '', amount: '', plan_delivery: '', actual_delivery: '', actual_quantity: '', actual_amount: '' })
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
const selectOrder = (row: any) => {
  selectedOrder.value = row
  fetchOrderItems(row.id)
}
const fetchOrderItems = async (orderId: number) => {
  const res = await axios.get('/api/order-items/', { params: { order: orderId } })
  orderItems.value = res.data
}
const openAddOrder = () => {
  orderForm.value = { order_no: '', company: '', order_date: '', total_amount: '' }
  showAddOrder.value = true
}
const saveOrder = async () => {
  await axios.post('/api/orders/', orderForm.value)
  showAddOrder.value = false
  ElMessage.success('新增订单成功')
  fetchOrders()
}
const editOrder = (row: any) => {
  orderForm.value = { ...row }
  showEditOrder.value = true
}
const updateOrder = async () => {
  await axios.put(`/api/orders/${orderForm.value.id}/`, orderForm.value)
  showEditOrder.value = false
  ElMessage.success('编辑订单成功')
  fetchOrders()
}
const openAddItem = () => {
  itemForm.value = { order: selectedOrder.value.id, item_no: '', product: '', quantity: '', unit_price: '', amount: '', plan_delivery: '', actual_delivery: '', actual_quantity: '', actual_amount: '' }
  showAddItem.value = true
}
const saveItem = async () => {
  await axios.post('/api/order-items/', itemForm.value)
  showAddItem.value = false
  ElMessage.success('新增明细成功')
  fetchOrderItems(selectedOrder.value.id)
}
const editItem = (row: any) => {
  itemForm.value = { ...row, order: selectedOrder.value.id }
  showEditItem.value = true
}
const updateItem = async () => {
  await axios.put(`/api/order-items/${itemForm.value.id}/`, itemForm.value)
  showEditItem.value = false
  ElMessage.success('编辑明细成功')
  fetchOrderItems(selectedOrder.value.id)
}
onMounted(() => {
  fetchOrders()
  fetchCompanies()
  fetchProducts()
})
</script>
<style scoped>
.el-card { width: 100%; box-sizing: border-box; }
</style>
