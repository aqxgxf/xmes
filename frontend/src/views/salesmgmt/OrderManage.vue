<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">订单管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="orderSearch" placeholder="筛选订单号/公司" style="width:220px" clearable />
        <el-button type="primary" @click="openAddOrder">新增订单</el-button>
      </div>
    </div>
    <el-table :data="filteredOrders" style="width:100%;margin-top:16px;" @row-click="selectOrder">
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
    <el-dialog v-model="showOrderDialog" :title="orderForm.id ? '编辑订单' : '新增订单'" width="90vw" top="2vh" fullscreen @close="cancelOrderEdit" class="order-dialog">
      <div class="order-dialog-content">
        <el-form :model="orderForm" label-width="100px" style="display:flex;flex-wrap:wrap;gap:16px;max-width:100%;">
          <el-form-item label="订单号" style="flex:1;min-width:220px;max-width:280px;"><el-input v-model="orderForm.order_no" /></el-form-item>
          <el-form-item label="公司" style="flex:1;min-width:160px;max-width:220px;"><el-select v-model="orderForm.company" style="width:100%">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select></el-form-item>
          <el-form-item label="下单日期" style="flex:1;min-width:220px;max-width:220px;"><el-date-picker v-model="orderForm.order_date" type="date" style="width:100%" /></el-form-item>
          <el-form-item label="订单金额合计" style="flex:1;min-width:120px;max-width:160px;"><el-input v-model="orderForm.total_amount" type="number" readonly style="width:100%" /></el-form-item>
        </el-form>
        <h3 style="margin-top:12px;">订单明细</h3>
        <el-table
          :data="orderItems"
          border
          style="width:100%;margin-top:8px;"
          :header-cell-style="{textAlign:'center'}"
          :cell-style="{textAlign:'center'}"
          :table-layout="'auto'"
        >
          <el-table-column prop="item_no" label="订单项" width="70" align="center" />
          <el-table-column prop="product" label="产品" width="320" align="center">
            <template #default="scope">
              <el-select v-model="scope.row.product" size="small" filterable placeholder="请选择产品" @change="setProductPrice(scope.row, $event)" style="width: 280px">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" align="center">
            <template #default="scope">
              <el-input-number v-model="scope.row.quantity" :min="0" size="small" @change="() => calcAmount(scope.row)" />
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" width="80" align="center">
            <template #default="scope">
              <el-input-number v-model="scope.row.unit_price" :min="0" size="small" @change="() => calcAmount(scope.row)" />
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额小计" width="100" align="center" />
          <el-table-column prop="plan_delivery" label="计划交货期" width="120" align="center">
            <template #default="scope">
              <el-date-picker v-model="scope.row.plan_delivery" type="date" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center">
            <template #default="scope">
              <div style="display:flex;gap:4px;justify-content:center;align-items:center;">
                <el-button size="small" type="primary" @click="saveSingleOrderItem(scope.row)">保存</el-button>
                <el-button size="small" type="danger" @click="removeOrderItem(scope.$index)">删除</el-button>
                <el-button size="small" type="success" @click="addOrderItemAfter(scope.$index)">增加</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top:12px;">
          <el-button type="primary" @click="addOrderItem">新增明细行</el-button>
          <el-button type="success" @click="saveAllOrderItems" :disabled="!orderForm.id">保存所有明细</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelOrderEdit">取消</el-button>
        <el-button type="primary" @click="saveOrUpdateOrder">保存订单</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 类型声明
interface Company { id: number; name: string }
interface Product { id: number; name: string }
interface OrderItem {
  id?: number;
  order: number;
  item_no: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  amount: number;
  plan_delivery: string;
  actual_delivery?: string;
  actual_quantity?: number;
  actual_amount?: number;
}
interface Order {
  id?: number;
  order_no: string;
  company: number;
  company_name?: string;
  order_date: string;
  total_amount: number;
  creator_name?: string;
  created_at?: string;
  items?: OrderItem[];
}

const orders = ref<Order[]>([])
const companies = ref<Company[]>([])
const products = ref<Product[]>([])
const orderItems = ref<OrderItem[]>([])
// 删除未使用的selectedOrder、itemForm声明
// const selectedOrder = ref<Order | null>(null)
// const itemForm = ref<OrderItem>({ order: 0, item_no: 0, product: 0, quantity: 0, unit_price: 0, amount: 0, plan_delivery: '', actual_delivery: '', actual_quantity: 0, actual_amount: 0 })
const showOrderDialog = ref(false)
const orderForm = ref<Order>({ order_no: '', company: 0, order_date: '', total_amount: 0, creator_name: '', created_at: '' })
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
  if (!products.value || products.value.length === 0) {
    ElMessage.warning('产品数据为空，请先在基础数据维护产品！')
  }
}
const selectOrder = (row: Order) => {
  fetchOrderItems(row.id!)
}
const fetchOrderItems = async (orderId: number) => {
  const res = await axios.get('/api/order-items/', { params: { order: orderId } })
  // 保证所有数字字段为number类型
  orderItems.value = (res.data || []).map((item: any) => ({
    ...item,
    quantity: Number(item.quantity),
    unit_price: Number(item.unit_price),
    amount: Number(item.amount),
  }))
  calcOrderTotal()
}
const openAddOrder = () => {
  orderForm.value = {
    order_no: '',
    company: companies.value.length > 0 ? companies.value[0].id : 0,
    order_date: new Date().toISOString().slice(0, 10),
    total_amount: 0,
    creator_name: '',
    created_at: ''
  }
  orderItems.value = []
  showOrderDialog.value = true
}
const editOrder = async (row: Order) => {
  orderForm.value = { ...row }
  orderItems.value = [] // 先清空，防止显示旧数据
  showOrderDialog.value = true
  await nextTick()
  try {
    const itemsRes = await axios.get('/api/order-items/', { 
      params: { 
        order: row.id,
        order_no: row.order_no // 同时传递订单号确保数据匹配
      } 
    })
    // 验证返回的明细数据是否属于当前订单，并保证数字类型
    if (Array.isArray(itemsRes.data)) {
      orderItems.value = itemsRes.data.filter(item => 
        item.order === row.id || item.order_no === row.order_no
      ).map((item: any) => ({
        ...item,
        quantity: Number(item.quantity),
        unit_price: Number(item.unit_price),
        amount: Number(item.amount),
      }))
    } else {
      orderItems.value = []
    }
    calcOrderTotal()
  } catch (error) {
    ElMessage.error('加载订单明细失败')
    orderItems.value = []
  }
}
const cancelOrderEdit = async () => {
  showOrderDialog.value = false
  orderForm.value = { order_no: '', company: 0, order_date: '', total_amount: 0, creator_name: '', created_at: '' }
  orderItems.value = []
  await fetchOrders()
}
// 保存订单时一并保存明细，保存前校验单价与产品价格
const saveOrUpdateOrder = async () => {
  // 检查明细单价与产品价格是否一致
  let priceDiff = false
  let diffItems: OrderItem[] = []
  for (const item of orderItems.value) {
    // 明确products.value为any[]，避免TS类型报错
    const prod = (products.value as any[]).find((p: any) => p.id === item.product)
    if (prod && Number(item.unit_price) !== Number((prod as any).price)) {
      priceDiff = true
      diffItems.push({ ...item, product_name: (prod as any).name, product_price: (prod as any).price } as any)
    }
  }
  const doSave = async (updateProductPrice = false) => {
    const payload = {
      order_no: orderForm.value.order_no,
      company: orderForm.value.company,
      order_date: orderForm.value.order_date
    }
    let res
    if (orderForm.value.id) {
      res = await axios.put(`/api/orders/${orderForm.value.id}/`, payload)
      ElMessage.success('订单更新成功')
    } else {
      res = await axios.post('/api/orders/', payload)
      ElMessage.success('订单创建成功')
    }
    // 刷新id
    const orderId = res?.data?.id || orderForm.value.id
    orderForm.value.id = orderId
    // 批量保存明细
    for (const item of orderItems.value) {
      item.order = orderId
      item.amount = Number(item.quantity) * Number(item.unit_price)
      if (item.id) {
        await axios.put(`/api/order-items/${item.id}/`, item)
      } else {
        await axios.post('/api/order-items/', item)
      }
      // 如需同步更新产品价格
      if (updateProductPrice) {
        const prod = products.value.find((p: any) => p.id === item.product)
        if (prod && Number(item.unit_price) !== Number((prod as any).price)) {
          const formData = new FormData()
          if ('code' in prod) formData.append('code', String(prod.code))
          if ('name' in prod) formData.append('name', String(prod.name))
          formData.append('price', String(item.unit_price))
          formData.append('category', String(typeof (prod as any).category === 'object' && (prod as any).category.id ? (prod as any).category.id : (prod as any).category))
          formData.append('param_values', JSON.stringify((prod as any).param_values || []))
          if ((prod as any).drawing_pdf && typeof (prod as any).drawing_pdf !== 'string') {
            formData.append('drawing_pdf', (prod as any).drawing_pdf)
          }
          try {
            await axios.put(`/api/products/${item.product}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
          } catch (e: any) {
            const msg = e && typeof e === 'object' && 'response' in e && e.response && 'data' in e.response && e.response.data && 'detail' in e.response.data ? e.response.data.detail : (e?.message || e)
            ElMessage.error('产品价格更新失败: ' + msg)
          }
          await fetchProducts()
          ;(prod as any).price = item.unit_price
        }
      }
    }
    fetchOrders()
    // 只刷新本订单明细，避免带出所有明细
    await nextTick()
    const itemsRes = await axios.get('/api/order-items/', {
      params: {
        order: orderId,
        order_no: orderForm.value.order_no
      }
    })
    orderItems.value = Array.isArray(itemsRes.data) ? itemsRes.data.filter(item => item.order === orderId || item.order_no === orderForm.value.order_no).map((item: any) => ({
      ...item,
      quantity: Number(item.quantity),
      unit_price: Number(item.unit_price),
      amount: Number(item.amount),
    })) : []
    calcOrderTotal()
  }
  if (priceDiff) {
    // 构造详细差异表格
    let diffHtml = '<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;width:100%;margin:8px 0;font-size:14px;text-align:center;">'
    diffHtml += '<tr style="background:#f5f7fa;"><th>产品</th><th>订单单价</th><th>产品价格</th></tr>'
    diffItems.forEach((item: any) => {
      diffHtml += `<tr><td>${item.product_name || ''}</td><td>${item.unit_price}</td><td>${(item as any).product_price}</td></tr>`
    })
    diffHtml += '</table>'
    // 用自定义html按钮实现“更新产品价格”
    let msgHtml = `有订单明细的单价与产品价格不一致，详情如下：<br>${diffHtml}<br>是否确定保存？<br><span style='color:#888;font-size:13px;'>如需同步更新产品表价格，请点击 <a id='update-prod-price-btn' style='color:#409EFF;cursor:pointer;text-decoration:underline;'>更新产品价格</a></span>`
    ElMessageBox.confirm(
      msgHtml,
      '提示',
      {
        dangerouslyUseHTMLString: true,
        showCancelButton: true,
        showConfirmButton: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        closeOnClickModal: false,
        showClose: true,
        distinguishCancelAndClose: true,
      }
    ).then(() => {
      doSave(false)
    }).catch(() => {})
    // 挂载自定义按钮事件
    setTimeout(() => {
      const btn = document.getElementById('update-prod-price-btn')
      if (btn) {
        btn.onclick = () => {
          ElMessageBox.close()
          doSave(true)
        }
      }
    }, 100)
  } else {
    await doSave(false)
  }
}
// 新增明细行后自动计算订单合计
const addOrderItem = () => {
  if (!orderForm.value.id) {
    ElMessage.warning('请先保存订单再新增明细！')
    return
  }
  const planDate = new Date();
  planDate.setDate(planDate.getDate() + 30);
  // 自动带出产品单价
  const firstProduct = products.value.length > 0 ? products.value[0] : null
  orderItems.value.push({
    order: orderForm.value.id,
    item_no: orderItems.value.length + 1,
    product: firstProduct ? firstProduct.id : 0,
    quantity: 0,
    unit_price: firstProduct ? Number((firstProduct as any).price) : 0,
    amount: 0,
    plan_delivery: planDate.toISOString().slice(0, 10)
  })
  calcOrderTotal()
}
const addOrderItemAfter = (idx: number) => {
  if (!orderForm.value.id) {
    ElMessage.warning('请先保存订单再新增明细！')
    return
  }
  const planDate = new Date();
  planDate.setDate(planDate.getDate() + 30);
  orderItems.value.splice(idx + 1, 0, {
    order: orderForm.value.id,
    item_no: orderItems.value.length + 1,
    product: products.value.length > 0 ? products.value[0].id : 0,
    quantity: 0,
    unit_price: 0,
    amount: 0,
    plan_delivery: planDate.toISOString().slice(0, 10)
  })
  calcOrderTotal()
}
const removeOrderItem = async (idx: number) => {
  const item = orderItems.value[idx]
  if (item.id) {
    await axios.delete(`/api/order-items/${item.id}/`)
    ElMessage.success('明细已删除')
    // 删除后只刷新本订单明细，避免带出所有明细
    await nextTick()
    const itemsRes = await axios.get('/api/order-items/', {
      params: {
        order: orderForm.value.id,
        order_no: orderForm.value.order_no
      }
    })
    orderItems.value = Array.isArray(itemsRes.data) ? itemsRes.data.filter(item => item.order === orderForm.value.id || item.order_no === orderForm.value.order_no).map((item: any) => ({
      ...item,
      quantity: Number(item.quantity),
      unit_price: Number(item.unit_price),
      amount: Number(item.amount),
    })) : []
    calcOrderTotal()
  } else {
    orderItems.value.splice(idx, 1)
    calcOrderTotal()
  }
}
const saveSingleOrderItem = async (item: OrderItem) => {
  item.amount = Number(item.quantity) * Number(item.unit_price)
  if (item.id) {
    await axios.put(`/api/order-items/${item.id}/`, item)
  } else {
    await axios.post('/api/order-items/', item)
  }
  ElMessage.success('明细已保存')
  fetchOrderItems(orderForm.value.id!)
  fetchOrders()
}
const saveAllOrderItems = async () => {
  for (const item of orderItems.value) {
    item.amount = Number(item.quantity) * Number(item.unit_price)
    if (item.id) {
      await axios.put(`/api/order-items/${item.id}/`, item)
    } else {
      await axios.post('/api/order-items/', item)
    }
  }
  ElMessage.success('所有明细已保存')
  fetchOrderItems(orderForm.value.id!)
  fetchOrders()
}
// 设置产品时自动带出单价
const setProductPrice = (row: OrderItem, productId: number) => {
  const prod = products.value.find(p => p.id === productId)
  if (prod) {
    row.unit_price = Number((prod as any).price)
    calcAmount(row)
  }
}
// 数量或单价变化时自动计算金额小计并更新合计
const calcAmount = (row: OrderItem) => {
  row.amount = Number(row.quantity) * Number(row.unit_price)
  // 保证类型
  row.quantity = Number(row.quantity)
  row.unit_price = Number(row.unit_price)
  calcOrderTotal()
}
// 计算订单合计
const calcOrderTotal = () => {
  orderForm.value.total_amount = orderItems.value.reduce((sum, item) => sum + Number(item.amount || 0), 0)
}
onMounted(() => {
  fetchOrders()
  fetchCompanies()
  fetchProducts()
})
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->
