<template>
  <div class="order-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">订单管理</h2>
          <div class="actions">
            <el-input 
              v-model="orderSearch" 
              placeholder="筛选订单号/公司" 
              class="search-input" 
              clearable 
              @clear="fetchOrders" 
              prefix-icon="Search"
            />
            <el-button type="primary" @click="openAddOrder">
              <el-icon><Plus /></el-icon> 新增订单
            </el-button>
          </div>
        </div>
      </template>

      <!-- 订单表格 -->
      <el-table 
        :data="filteredOrders" 
        v-loading="loading" 
        border 
        stripe
        style="width:100%"
      >
        <el-table-column prop="order_no" label="订单号" min-width="120" />
        <el-table-column prop="company_name" label="公司" min-width="150" />
        <el-table-column prop="order_date" label="下单日期" min-width="120" />
        <el-table-column prop="product_name" label="产品" min-width="150" />
        <el-table-column prop="quantity" label="数量" min-width="100" />
        <el-table-column prop="unit_price" label="单价" min-width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.unit_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="订单金额" min-width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="plan_delivery" label="计划交货期" min-width="120" />
        <el-table-column prop="actual_delivery" label="实际交货期" min-width="120" />
        <el-table-column prop="actual_quantity" label="已交货数量" min-width="120" />
        <el-table-column prop="actual_amount" label="已交货金额" min-width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.actual_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="160">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="editOrder(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDeleteOrder(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 订单表单弹窗 -->
    <el-dialog 
      v-model="showOrderDialog" 
      :title="orderForm.id ? '编辑订单' : '新增订单'" 
      width="80%" 
      @close="cancelOrderEdit" 
      :modal-append-to-body="false" 
      class="order-dialog"
      destroy-on-close
    >
      <el-form 
        :model="orderForm" 
        label-width="100px" 
        :rules="orderRules"
        ref="orderFormRef"
        label-position="left"
      >
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="订单号" prop="order_no">
              <el-input v-model="orderForm.order_no" placeholder="请输入订单号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="公司" prop="company">
              <el-select v-model="orderForm.company" placeholder="请选择公司" filterable class="form-select">
                <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="订单类别" prop="order_type">
              <el-select v-model="orderForm.order_type" placeholder="请选择订单类别" class="form-select">
                <el-option v-for="opt in orderTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col >
            <el-form-item label="产品" prop="product">
              <el-select 
                v-model="orderForm.product" 
                placeholder="请选择产品" 
                filterable 
                :filter-method="filterProduct"
                class="form-select"
                :popper-append-to-body="true"
                :reserve-keyword="true"
                remote
                :remote-method="remoteSearchProducts"
              >
                <el-option 
                  v-for="p in filteredProducts" 
                  :key="p.id" 
                  :label="`${p.name}（${p.code || ''}）`" 
                  :value="p.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="下单日期" prop="order_date">
              <el-date-picker v-model="orderForm.order_date" type="date" class="form-select" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="计划交货期" prop="plan_delivery">
              <el-date-picker v-model="orderForm.plan_delivery" type="date" class="form-select" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="orderForm.quantity" :min="0" class="form-select" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="orderForm.unit_price" :min="0" :precision="2" :step="0.01" class="form-select" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="订单金额合计">
              <el-input v-model="orderForm.total_amount" readonly class="form-select">
                <template #prepend>¥</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="实际交货期" prop="actual_delivery">
              <el-date-picker v-model="orderForm.actual_delivery" type="date" class="form-select" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="已交货数量" prop="actual_quantity">
              <el-input-number v-model="orderForm.actual_quantity" :min="0" class="form-select" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="已交货金额">
              <el-input-number v-model="orderForm.actual_amount" :min="0" :precision="2" class="form-select" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="cancelOrderEdit">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="saveOrUpdateOrder">保存订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

// 类型定义
interface Company { 
  id: number; 
  name: string; 
}

interface Product { 
  id: number; 
  name: string; 
  code?: string; 
  price?: number; 
}

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
  total_amount: number;
  plan_delivery: string;
  actual_delivery?: string;
  actual_quantity?: number;
  actual_amount?: number;
  order_type?: string;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const orders = ref<Order[]>([])
const companies = ref<Company[]>([])
const products = ref<Product[]>([])
const filteredProducts = ref<Product[]>([])
const searchKeyword = ref('')
const showOrderDialog = ref(false)
const orderFormRef = ref<FormInstance>()

// 订单表单
const orderForm = ref<Order>({
  order_no: '',
  company: 0,
  order_date: '',
  product: 0,
  quantity: 0,
  unit_price: 0,
  amount: 0,
  total_amount: 0,
  plan_delivery: ''
})

// 搜索
const orderSearch = ref('')
const filteredOrders = computed(() => {
  if (!orderSearch.value) return orders.value
  const kw = orderSearch.value.toLowerCase()
  return orders.value.filter(o =>
    (o.order_no && o.order_no.toLowerCase().includes(kw)) ||
    (o.company_name && o.company_name.toLowerCase().includes(kw))
  )
})

// 订单类型选项
const orderTypeOptions = [
  { label: '常规', value: 'normal' },
  { label: '新品', value: 'new' }
]

// 表单验证规则
const orderRules = {
  order_no: [
    { required: true, message: '请输入订单号', trigger: 'blur' }
  ],
  company: [
    { required: true, message: '请选择公司', trigger: 'change' }
  ],
  product: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ],
  order_date: [
    { required: true, message: '请选择下单日期', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' }
  ],
  plan_delivery: [
    { required: true, message: '请选择计划交货期', trigger: 'change' }
  ]
}

// 格式化金额
function formatCurrency(amount: number | undefined): string {
  if (amount === undefined || amount === null) return '¥0.00'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(amount)
}

// 数据加载方法
const fetchOrders = async () => {
  loading.value = true
  
  try {
    const res = await axios.get('/api/orders/')
    console.log('Orders API response:', res.data)
    
    // 处理不同格式的API响应
    let ordersData = [];
    
    if (Array.isArray(res.data)) {
      // 直接是数组
      ordersData = res.data;
    } else if (res.data && res.data.results && Array.isArray(res.data.results)) {
      // 分页格式
      ordersData = res.data.results;
    } else if (res.data && typeof res.data === 'object') {
      // 其他对象格式，尝试找到数据数组
      if (res.data.data && Array.isArray(res.data.data)) {
        ordersData = res.data.data;
      } else {
        console.warn('Unexpected API response format:', res.data);
        ordersData = [];
      }
    } else {
      console.warn('Unexpected API response format:', res.data);
      ordersData = [];
    }
    
    // 补全 company_name 和 product_name 字段
    orders.value = ordersData.map((o: any) => {
      // 安全地查找公司名称
      let companyName = '';
      if (Array.isArray(companies.value)) {
        const company = companies.value.find(c => c && c.id === o.company);
        if (company && company.name) {
          companyName = company.name;
        }
      }
      
      // 安全地查找产品名称
      let productName = '';
      if (Array.isArray(products.value)) {
        const product = products.value.find(p => p && p.id === o.product);
        if (product && product.name) {
          productName = product.name;
        }
      }
      
      return {
        ...o,
        company_name: companyName,
        product_name: productName
      };
    })
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
    orders.value = []
  } finally {
    loading.value = false
  }
}

const fetchCompanies = async () => {
  try {
    console.log('Fetching companies data...')
    const res = await axios.get('/api/companies/')
    console.log('Companies API response:', res.data)
    
    // 处理不同格式的API响应
    if (Array.isArray(res.data)) {
      companies.value = res.data
    } else if (res.data && res.data.results && Array.isArray(res.data.results)) {
      companies.value = res.data.results
    } else if (res.data && typeof res.data === 'object') {
      if (res.data.data && Array.isArray(res.data.data)) {
        companies.value = res.data.data
      } else {
        console.warn('Unexpected companies API format:', res.data)
        companies.value = []
      }
    } else {
      console.warn('Unexpected companies API format:', res.data)
      companies.value = []
    }
  } catch (error) {
    console.error('获取公司列表失败:', error)
    ElMessage.error('获取公司列表失败')
    companies.value = []
  }
}

const fetchProducts = async () => {
  try {
    console.log('Fetching products data...')
    const res = await axios.get('/api/products/')
    console.log('Products API response:', res.data)
    
    // 处理不同格式的API响应
    if (Array.isArray(res.data)) {
      products.value = res.data
    } else if (res.data && res.data.results && Array.isArray(res.data.results)) {
      products.value = res.data.results
    } else if (res.data && typeof res.data === 'object') {
      if (res.data.data && Array.isArray(res.data.data)) {
        products.value = res.data.data
      } else {
        console.warn('Unexpected products API format:', res.data)
        products.value = []
      }
    } else {
      console.warn('Unexpected products API format:', res.data)
      products.value = []
    }
    
    // 初始时设置过滤后的产品为全部产品
    filteredProducts.value = [...products.value]
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
    products.value = []
    filteredProducts.value = []
  }
}

// 日期加天数工具
function addDays(dateStr: string, days: number): string {
  const date = new Date(dateStr)
  date.setDate(date.getDate() + days)
  return date.toISOString().slice(0, 10)
}

// 过滤产品的函数
const filterProduct = (query: string) => {
  if (query === '') {
    filteredProducts.value = products.value
  } else {
    const lowerQuery = query.toLowerCase()
    filteredProducts.value = products.value.filter(p => {
      return (p.name && p.name.toLowerCase().includes(lowerQuery)) || 
             (p.code && p.code.toLowerCase().includes(lowerQuery))
    })
  }
}

// 远程搜索产品
const remoteSearchProducts = (query: string) => {
  searchKeyword.value = query
  filterProduct(query)
}

// 订单操作方法
const openAddOrder = async () => {
  // 确保产品和公司数据已加载
  if (!Array.isArray(products.value) || products.value.length === 0) {
    const loadingMsg = ElMessage({
      message: '正在加载产品数据...',
      type: 'info',
      duration: 0
    })
    await fetchProducts()
    if (loadingMsg.close) loadingMsg.close()
  }
  
  if (!Array.isArray(companies.value) || companies.value.length === 0) {
    const loadingMsg = ElMessage({
      message: '正在加载公司数据...',
      type: 'info',
      duration: 0
    })
    await fetchCompanies()
    if (loadingMsg.close) loadingMsg.close()
  }
  
  const today = new Date().toISOString().slice(0, 10)
  
  // 安全检查：确保companies和products是数组
  const defaultCompany = Array.isArray(companies.value) && companies.value.length > 0 ? companies.value[0].id : 0;
  const defaultProduct = Array.isArray(products.value) && products.value.length > 0 ? products.value[0].id : 0;
  
  orderForm.value = {
    order_no: '',
    company: defaultCompany,
    order_date: today,
    product: defaultProduct,
    quantity: 1,
    unit_price: 0,
    amount: 0,
    total_amount: 0,
    plan_delivery: addDays(today, 30), // 默认常规+30天
    order_type: 'normal' // 默认常规
  }
  
  // 让Vue完成DOM更新后再打开对话框
  setTimeout(() => {
    // 重置过滤后的产品列表，确保显示全部产品
    filteredProducts.value = [...products.value]
    showOrderDialog.value = true
  }, 50)
}

const editOrder = async (row: Order) => {
  // 确保产品数据已加载完成
  if (!Array.isArray(products.value) || products.value.length === 0) {
    const loadingMsg = ElMessage({
      message: '正在加载产品数据...',
      type: 'info',
      duration: 0
    })
    await fetchProducts()
    if (loadingMsg.close) loadingMsg.close()
  }
  
  // 深拷贝订单数据，并确保数值字段为Number类型
  const orderData = { ...row };
  
  // 转换可能的字符串数值为数字类型
  if (typeof orderData.quantity === 'string') {
    orderData.quantity = Number(orderData.quantity);
  }
  if (typeof orderData.unit_price === 'string') {
    orderData.unit_price = Number(orderData.unit_price);
  }
  if (typeof orderData.amount === 'string') {
    orderData.amount = Number(orderData.amount);
  }
  if (typeof orderData.total_amount === 'string') {
    orderData.total_amount = Number(orderData.total_amount);
  }
  if (typeof orderData.actual_quantity === 'string') {
    orderData.actual_quantity = Number(orderData.actual_quantity);
  }
  if (typeof orderData.actual_amount === 'string') {
    orderData.actual_amount = Number(orderData.actual_amount);
  }
  
  orderForm.value = orderData;
  
  // 让Vue完成DOM更新后再打开对话框
  setTimeout(() => {
    // 重置过滤后的产品列表，确保显示全部产品
    filteredProducts.value = [...products.value]
    showOrderDialog.value = true
  }, 50)
}

const confirmDeleteOrder = (row: Order) => {
  if (!row.id) return
  
  ElMessageBox.confirm(
    `确定要删除订单 "${row.order_no}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(() => {
    deleteOrder(row)
  }).catch(() => {
    // 用户取消操作
  })
}

const deleteOrder = async (row: Order) => {
  if (!row.id) return
  
  loading.value = true
  
  try {
    await axios.delete(`/api/orders/${row.id}/`)
    ElMessage.success('订单删除成功')
    await fetchOrders()
  } catch (error: any) {
    let errorMsg = '删除失败'
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        }
      }
    }
    
    ElMessage.error(`删除失败: ${errorMsg}`)
    console.error('删除订单失败:', error)
  } finally {
    loading.value = false
  }
}

const cancelOrderEdit = () => {
  showOrderDialog.value = false
  orderForm.value = { 
    order_no: '', 
    company: 0, 
    order_date: '', 
    product: 0, 
    quantity: 0, 
    unit_price: 0, 
    amount: 0, 
    total_amount: 0, 
    plan_delivery: '' 
  }
}

const saveOrUpdateOrder = async () => {
  if (!orderFormRef.value) return
  
  orderFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      // 确保所有数值字段为Number类型
      const formData = { ...orderForm.value };
      
      // 转换可能的字符串数值为数字类型
      formData.quantity = Number(formData.quantity);
      formData.unit_price = Number(formData.unit_price);
      formData.amount = Number(formData.amount || 0);
      
      // 自动计算订单金额合计，保留两位小数
      formData.total_amount = formData.quantity * formData.unit_price;
      formData.total_amount = Number(formData.total_amount.toFixed(2));
      
      // 处理可选的数值字段
      if (formData.actual_quantity !== undefined && formData.actual_quantity !== null) {
        formData.actual_quantity = Number(formData.actual_quantity);
      }
      if (formData.actual_amount !== undefined && formData.actual_amount !== null) {
        formData.actual_amount = Number(formData.actual_amount);
      }
      
      if (formData.id) {
        await axios.put(`/api/orders/${formData.id}/`, formData)
        ElMessage.success('订单更新成功')
      } else {
        await axios.post('/api/orders/', formData)
        ElMessage.success('订单创建成功')
      }
      
      showOrderDialog.value = false
      await fetchOrders()
    } catch (error: any) {
      // 处理后端字段级错误
      const detail = error?.response?.data
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
    } finally {
      submitting.value = false
    }
  })
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

// 订单金额合计联动，保留两位小数
watch(() => [orderForm.value.quantity, orderForm.value.unit_price], () => {
  const total = Number(orderForm.value.quantity) * Number(orderForm.value.unit_price)
  orderForm.value.total_amount = Number.isNaN(total) ? 0 : Number(total.toFixed(2))
})

// 监听产品选择，自动带入单价
watch(() => orderForm.value.product, (newProductId) => {
  if (!Array.isArray(products.value)) {
    console.warn('Products is not an array, cannot auto-set unit price');
    return;
  }
  
  const p = products.value.find(p => p && p.id === newProductId)
  if (p && p.price !== undefined) {
    orderForm.value.unit_price = Number(p.price)
  }
})

// 实际交货金额自动计算
watch(() => [orderForm.value.actual_quantity, orderForm.value.unit_price], () => {
  orderForm.value.actual_amount = Number(orderForm.value.actual_quantity || 0) * Number(orderForm.value.unit_price || 0)
})

// 生命周期钩子
onMounted(async () => {
  await fetchCompanies()
  await fetchProducts()
  await fetchOrders()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.order-container {
  .actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
  
  .search-input {
    width: 240px;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  .form-select {
    width: 100%;
  }
}

.order-dialog {
  :deep(.el-dialog__body) {
    padding: 12px 24px 0 24px;
  }
}
</style>
