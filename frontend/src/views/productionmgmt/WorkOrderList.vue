<template>
  <div class="workorder-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工单管理</h2>
          <div class="actions">
            <el-button type="primary" @click="openAddWorkOrder">
              <el-icon><Plus /></el-icon> 新增工单
            </el-button>
            <el-button type="success" @click="openCreateByOrderDialog">
              <el-icon><Document /></el-icon> 通过订单新增
            </el-button>
            <el-button v-if="error" type="warning" @click="retryLoading">
              <el-icon><RefreshRight /></el-icon> 重试加载
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-empty 
        v-if="!loading && workorders.length === 0" 
        description="暂无工单数据"
        :image-size="200">
        <template #image>
          <div class="empty-wrapper">
            <el-icon class="empty-icon"><Document /></el-icon>
            <div v-if="error" class="error-message">
              {{ errorMessage }}
            </div>
          </div>
        </template>
        <el-button type="primary" @click="openAddWorkOrder">新增工单</el-button>
        <el-button v-if="error" @click="retryLoading">重试加载</el-button>
      </el-empty>
      
      <el-table
        v-else
        :data="workorders"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="workorder_no" label="工单号" min-width="120" />
        <el-table-column prop="order" label="订单号" min-width="120" />
        <el-table-column prop="product" label="产品" min-width="160" />
        <el-table-column prop="quantity" label="数量" min-width="80" />
        <el-table-column prop="process_code" label="工艺流程代码" min-width="130" />
        <el-table-column prop="plan_start" label="计划开始" min-width="120" />
        <el-table-column prop="plan_end" label="计划结束" min-width="120" />
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" />
        <el-table-column label="操作" fixed="right" min-width="320">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click.stop="editWorkOrder(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click.stop="confirmDeleteWorkOrder(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
              <el-button size="small" type="info" @click.stop="viewProcessDetails(row)">
                <el-icon><View /></el-icon> 查看工艺明细
              </el-button>
              <el-button 
                size="small" 
                type="success" 
                @click.stop="printWorkOrder(row)"
                v-if="row.status === 'print'"
              >
                <el-icon><Printer /></el-icon> 打印工单
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>

    <!-- 其他对话框内容保持不变，后续继续重构 -->
    <el-dialog v-model="showWorkOrderDialog" :title="workOrderForm.id ? '编辑工单' : '新增工单'" width="600px" @close="cancelWorkOrderEdit">
      <el-form :model="workOrderForm" :rules="workOrderFormRules" ref="workOrderFormRef" label-width="100px">
        <el-form-item label="工单号" prop="workorder_no"><el-input v-model="workOrderForm.workorder_no" /></el-form-item>
        <el-form-item label="订单号" prop="order">
          <el-select v-model="workOrderForm.order" filterable placeholder="请选择订单号" style="width:100%">
            <template v-if="!workOrderForm.id">
              <!-- 新增工单时只显示未关联工单的订单 -->
              <template v-for="order in ordersWithoutWorkOrder" :key="order?.id || 'none'">
                <el-option 
                  v-if="order && order.id"
                  :label="order?.order_no || '未知订单'" 
                  :value="order?.id || ''" 
                />
              </template>
              <el-option v-if="ordersWithoutWorkOrder.length === 0" key="no-order" label="没有可用订单" value="" disabled />
            </template>
            <template v-else>
              <!-- 编辑工单时显示所有订单 -->
              <template v-for="order in orders" :key="order?.id || 'none'">
                <el-option 
                  v-if="order && order.id"
                  :label="order?.order_no || '未知订单'" 
                  :value="order?.id || ''" 
                />
              </template>
              <el-option v-if="orders.length === 0" key="loading" label="加载中..." value="" disabled />
            </template>
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-select v-model="workOrderForm.product" filterable placeholder="请选择产品" style="width:100%">
            <template v-for="product in products" :key="product?.id || 'none'">
              <el-option 
                v-if="product && product.id"
                :label="product ? (product.name + '（' + product.code + '）') : '未知产品'" 
                :value="product?.id || ''" 
              />
            </template>
            <el-option v-if="products.length === 0" key="loading" label="加载中..." value="" disabled />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity"><el-input-number v-model="workOrderForm.quantity" :min="0" style="width:200px" /></el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select v-model="workOrderForm.process_code" filterable placeholder="请选择工艺流程" style="width:100%">
            <template v-for="processCode in processCodes" :key="processCode?.id || 'none'">
              <el-option 
                v-if="processCode && processCode.id"
                :label="processCode?.code && processCode?.version ? (processCode.code + ' ' + processCode.version) : '未知工艺'" 
                :value="processCode?.id || ''" 
              />
            </template>
            <el-option v-if="processCodes.length === 0" key="loading" label="加载中..." value="" disabled />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始" prop="plan_start"><el-date-picker v-model="workOrderForm.plan_start" type="datetime" style="width:300px" /></el-form-item>
        <el-form-item label="计划结束" prop="plan_end"><el-date-picker v-model="workOrderForm.plan_end" type="datetime" style="width:300px" /></el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="workOrderForm.status" style="width:200px">
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
    
    <el-dialog
      title="工单打印预览"
      v-model="showPrintDialog"
      width="90%"
      :before-close="handlePrintDialogClose"
      fullscreen
      :destroy-on-close="true"
      class="print-dialog"
    >
      <div class="print-container">
        <div class="print-actions">
          <span class="print-instruction">请检查内容后点击"打印"按钮</span>
          <div class="print-buttons">
            <el-button type="primary" @click="handlePrint" icon="Printer">打印</el-button>
            <el-button @click="handlePrintDialogClose">关闭</el-button>
          </div>
        </div>
        <iframe 
          ref="printFrame" 
          class="print-frame" 
          style="width:100%;border:none;" 
          v-if="printHtml">
        </iframe>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, View, Printer, Document, RefreshRight } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import QRCode from 'qrcode'

// 类型定义
interface WorkOrder {
  id: number;
  workorder_no: string;
  order: number | string;
  order_no?: string;
  product: number;
  product_code?: string;
  product_name?: string;
  quantity: number;
  process_code: number;
  process_code_text?: string;
  plan_start: string;
  plan_end: string;
  status: string;
  remark?: string;
  process_details?: ProcessDetail[];
}

interface ProcessDetail {
  id: number;
  step_no: number;
  process_name: string;
  pending_quantity: number;
}

interface Product {
  id: number;
  code: string;
  name: string;
}

interface ProcessCode {
  id: number;
  code: string;
  version: string;
}

interface Order {
  id: number;
  order_no: string;
  company_name?: string;
  order_date?: string;
  total_amount?: number;
}

// 状态定义
const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const workorders = ref<WorkOrder[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const products = ref<Product[]>([])
const processCodes = ref<ProcessCode[]>([])
const orders = ref<Order[]>([])
const showWorkOrderDialog = ref(false)
const showCreateByOrderDialog = ref(false)
const showPrintDialog = ref(false)
const printHtml = ref('')
const printFrame = ref<HTMLIFrameElement | null>(null)
const currentPrintWorkOrder = ref<WorkOrder | null>(null)
const workOrderFormRef = ref<FormInstance>()
const ordersWithoutWorkOrder = ref<Order[]>([])
const error = ref(false)
const errorMessage = ref('')
const retryCount = ref(0)
const maxRetries = 3

// 表单对象
const workOrderForm = ref<any>({
  id: null,
  workorder_no: '',
  order: '',
  product: '',
  quantity: 0,
  process_code: '',
  plan_start: '',
  plan_end: '',
  status: '',
  remark: ''
})

// 表单验证规则
const workOrderFormRules = {
  workorder_no: [{ required: true, message: '工单号必填', trigger: 'blur' }],
  order: [{ required: true, message: '订单号必选', trigger: 'change' }],
  product: [{ required: true, message: '产品必选', trigger: 'change' }],
  quantity: [{ required: true, message: '数量必填', trigger: 'blur' }],
  process_code: [{ required: true, message: '工艺流程必选', trigger: 'change' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}

// 状态选项
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'print', label: '待打印' },
  { value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

// 状态相关计算属性
const getStatusText = (status: string) => {
  const found = statusOptions.find(s => s.value === status)
  return found ? found.label : status
}

const getStatusType = (status: string): string => {
  switch (status) {
    case 'draft': return 'info'
    case 'print': return 'warning'
    case 'released': return 'info'
    case 'in_progress': return 'primary'
    case 'completed': return 'success'
    case 'cancelled': return 'danger'
    default: return 'info'
  }
}

// 数据加载方法
const fetchWorkOrders = async () => {
  loading.value = true
  error.value = false
  errorMessage.value = ''
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    console.log('Requesting workorders with params:', params)
    const response = await axios.get('/api/workorders/', { params })
    console.log('Raw workorders response:', response)
    
    if (response.data && response.data.results) {
      // Handle paginated response (standard DRF format)
      console.log('Paginated response detected', response.data.results)
      workorders.value = response.data.results
      total.value = response.data.count || response.data.results.length
    } else if (response.data && Array.isArray(response.data)) {
      // Handle non-paginated array response
      console.log('Array response detected', response.data)
      workorders.value = response.data
      total.value = response.data.length
    } else if (response.data && typeof response.data === 'object' && response.data.data) {
      // Handle custom response format with data field
      console.log('Custom data format detected', response.data.data) 
      if (Array.isArray(response.data.data)) {
        workorders.value = response.data.data
        total.value = response.data.data.length
      } else if (response.data.data.results) {
        workorders.value = response.data.data.results
        total.value = response.data.data.count || response.data.data.results.length
      }
    } else {
      // Fallback for other response formats
      console.warn('Unexpected API response format:', response.data)
      workorders.value = []
      total.value = 0
    }
    
    // Reset retry count after successful request
    retryCount.value = 0
    console.log('Final workorders array:', workorders.value)
  } catch (error: any) {
    console.error('获取工单列表失败:', error)
    console.error('Error details:', error.response ? error.response.data : 'No response data')
    errorMessage.value = error.response?.data?.message || error.response?.data?.detail || 
                        error.message || '获取工单列表失败，请稍后再试'
    error.value = true
    ElMessage.error('获取工单列表失败')
    workorders.value = []
    total.value = 0
    
    // Auto-retry logic
    if (retryCount.value < maxRetries) {
      retryCount.value++
      console.log(`自动重试 (${retryCount.value}/${maxRetries})`)
      setTimeout(() => {
        fetchWorkOrders()
      }, 2000 * retryCount.value) // Exponential backoff
    }
  } finally {
    loading.value = false
  }
}

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/products/')
    products.value = response.data.results || response.data
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
    products.value = []
  }
}

const fetchProcessCodes = async () => {
  try {
    const response = await axios.get('/api/process-codes/')
    processCodes.value = response.data.results || response.data
  } catch (error) {
    console.error('获取工艺流程代码列表失败:', error)
    ElMessage.error('获取工艺流程代码列表失败')
    processCodes.value = []
  }
}

const fetchOrders = async () => {
  try {
    console.log('Fetching orders data...')
    const response = await axios.get('/api/orders/')
    console.log('Orders API response:', response.data)
    
    // Handle different response formats
    if (response.data && response.data.results) {
      // Paginated format
      orders.value = response.data.results
      console.log('Loaded orders (paginated format):', orders.value)
    } else if (Array.isArray(response.data)) {
      // Array format
      orders.value = response.data
      console.log('Loaded orders (array format):', orders.value)
    } else if (response.data && typeof response.data === 'object' && response.data.data) {
      // Object with data property
      if (Array.isArray(response.data.data)) {
        orders.value = response.data.data
      } else if (response.data.data.results) {
        orders.value = response.data.data.results
      }
      console.log('Loaded orders (custom format):', orders.value)
    } else {
      console.warn('Unexpected orders API response format:', response.data)
      orders.value = []
    }
    
    // 确保所有订单都有id和order_no属性
    orders.value = orders.value.filter(o => o && o.id && o.order_no)
    console.log('Final filtered orders:', orders.value)
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
    orders.value = []
  }
}

// 获取未关联工单的订单
const fetchOrdersWithoutWorkOrder = async () => {
  try {
    console.log('Fetching orders without workorder...')
    const response = await axios.get('/api/orders-without-workorder/')
    console.log('Orders without workorder response:', response.data)
    
    if (Array.isArray(response.data)) {
      ordersWithoutWorkOrder.value = response.data
    } else if (response.data && response.data.results) {
      ordersWithoutWorkOrder.value = response.data.results
    } else {
      console.warn('Unexpected API response format for orders without workorder')
      ordersWithoutWorkOrder.value = []
    }
    
    // 确保所有订单都有id和order_no属性
    ordersWithoutWorkOrder.value = ordersWithoutWorkOrder.value.filter(o => o && o.id && o.order_no)
    console.log('Filtered orders without workorder:', ordersWithoutWorkOrder.value)
  } catch (error) {
    console.error('获取未关联工单的订单失败:', error)
    ElMessage.error('获取未关联工单的订单失败')
    ordersWithoutWorkOrder.value = []
  }
}

// 处理事件
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchWorkOrders()
}

const handleCurrentChange = () => {
  fetchWorkOrders()
}

// 其余方法保持不变，后续继续重构
const openAddWorkOrder = async () => {
  // 设置当前日期和30天后的日期
  const now = new Date()
  const futureDate = new Date()
  futureDate.setDate(now.getDate() + 30)
  
  // Set initial form data with empty values and defaults
  workOrderForm.value = { 
    id: null, 
    workorder_no: '', 
    order: '', 
    product: '', 
    quantity: 0, 
    process_code: '', 
    plan_start: now.toISOString().slice(0, 16), 
    plan_end: futureDate.toISOString().slice(0, 16), 
    status: 'draft', // Set a default status
    remark: '' 
  }
  
  // 加载未关联工单的订单数据
  const loading = ElMessage({
    message: '正在加载未关联工单的订单数据...',
    type: 'info',
    duration: 0
  })
  
  try {
    console.log('Loading orders without workorder before opening dialog')
    await fetchOrdersWithoutWorkOrder()
    if (loading.close) loading.close()
    
    // 如果没有未关联工单的订单，提示用户
    if (ordersWithoutWorkOrder.value.length === 0) {
      ElMessage.warning('没有可用的订单，所有订单已关联工单')
    }
  } catch (error) {
    console.error('Failed to load orders without workorder:', error)
    if (loading.close) loading.close()
    ElMessage.error('无法加载订单数据，请稍后再试')
    return // Don't open dialog if orders couldn't be loaded
  }
  
  // Make sure products data is loaded before opening dialog
  if (!products.value || products.value.length === 0) {
    const loading = ElMessage({
      message: '正在加载产品数据...',
      type: 'info',
      duration: 0
    })
    
    try {
      console.log('Loading products data before opening dialog')
      await fetchProducts()
      if (loading.close) loading.close()
    } catch (error) {
      console.error('Failed to load products:', error)
      if (loading.close) loading.close()
      ElMessage.error('无法加载产品数据，请稍后再试')
      return // Don't open dialog if products couldn't be loaded
    }
  }
  
  // Now open the dialog safely
  console.log('Opening add work order dialog with prepared data')
  showWorkOrderDialog.value = true
}

const editWorkOrder = async (row: any) => {
  if (!row) {
    console.error('Cannot edit work order: row data is null or undefined')
    ElMessage.error('工单数据无效，无法编辑')
    return
  }
  
  console.log('Editing work order:', row)
  
  // 确保订单数据已加载
  if (!orders.value || orders.value.length === 0) {
    const loading = ElMessage({
      message: '正在加载订单数据...',
      type: 'info',
      duration: 0
    })
    
    try {
      await fetchOrders()
      if (loading.close) loading.close()
    } catch (error) {
      console.error('Failed to load orders:', error)
      if (loading.close) loading.close()
      ElMessage.error('无法加载订单数据，请稍后再试')
      return
    }
  }
  
  try {
    // Ensure all properties exist, fill with defaults if missing
    workOrderForm.value = { 
      id: row.id || null,
      workorder_no: row.workorder_no || '',
      order: row.order || '',
      product: row.product || '',
      quantity: row.quantity ? Number(row.quantity) : 0,
      process_code: row.process_code || '',
      plan_start: row.plan_start || '',
      plan_end: row.plan_end || '',
      status: row.status || 'draft',
      remark: row.remark || ''
    }
    showWorkOrderDialog.value = true
  } catch (error) {
    console.error('Error preparing work order form:', error)
    ElMessage.error('准备编辑表单时出错，请重试')
  }
}

const confirmDeleteWorkOrder = (row: WorkOrder) => {
  ElMessageBox.confirm(
    `确定要删除工单 "${row.workorder_no}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteWorkOrder(row.id)
  }).catch(() => {
    // 用户取消操作
  })
}

const cancelWorkOrderEdit = () => {
  showWorkOrderDialog.value = false
  workOrderForm.value = { id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' }
  fetchWorkOrders()
}

async function saveOrUpdateWorkOrder() {
  try {
    let res;
    let savedId = workOrderForm.value.id || null;
    
    if (savedId) {
      res = await axios.put(`/api/workorders/${savedId}/`, workOrderForm.value)
      ElMessage.success('工单更新成功')
    } else {
      res = await axios.post('/api/workorders/', workOrderForm.value)
      savedId = res.data.id;
      ElMessage.success('工单创建成功')
    }
    
    // 关闭窗口
    showWorkOrderDialog.value = false;
    
    // 刷新数据并在加载完成后聚焦到刚编辑的项
    await fetchWorkOrders();
    
    // 添加一个小延迟，确保DOM已更新
    setTimeout(() => {
      // 找到刚编辑的行并滚动到视图中
      const editedRow = workorders.value.find(w => w.id === savedId);
      if (editedRow) {
        // 找到对应行的索引
        const index = workorders.value.findIndex(w => w.id === savedId);
        if (index !== -1) {
          // 添加高亮效果
          highlightRow(index);
        }
      }
    }, 100);
  } catch (error: any) {
    console.error('保存工单失败:', error);
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message || '未知错误'));
  }
}

async function deleteWorkOrder(id: number) {
  await axios.delete(`/api/workorders/${id}/`)
  ElMessage.success('工单已删除')
  fetchWorkOrders()
}

// 此处省略其他未修改方法...
function viewProcessDetails(row: any) {
  router.push(`/workorder-process-details/${row.id}`)
}

function openCreateByOrderDialog() {
  const loading = ElMessage({
    message: '正在加载未关联工单的订单...',
    type: 'info',
    duration: 0
  })
  
  axios.get('/api/orders-without-workorder/').then(res => {
    ordersWithoutWorkOrder.value = res.data
    showCreateByOrderDialog.value = true
    if (ordersWithoutWorkOrder.value.length === 0) {
      ElMessage.info('没有可用的订单，所有订单已关联工单')
    }
  }).catch(error => {
    console.error('获取未关联工单的订单失败:', error)
    ElMessage.error('获取未关联工单的订单失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
  }).finally(() => {
    if (loading.close) loading.close()
  })
}

async function createWorkOrderByOrder(order: any) {
  if (!order || !order.id) {
    ElMessage.error('订单数据无效，无法创建工单')
    return
  }
  
  const loading = ElMessage({ message: '正在创建工单...', type: 'info', duration: 0 })
  try {
    const res = await axios.post('/api/workorders/create-by-order/', { order_id: order.id }, {
      headers: {
        'Content-Type': 'application/json',
      }
    })
    showCreateByOrderDialog.value = false
    await fetchWorkOrders()
    
    // Check if response data is valid and contains ID
    if (res.data && typeof res.data === 'object' && res.data.id) {
      console.log('Creating work order from order response:', res.data)
      // Make a clean copy of the data to avoid reference issues
      const workOrderData = { ...res.data }
      editWorkOrder(workOrderData)
      ElMessage.success('工单已自动生成，请补充完善后保存')
    } else {
      console.warn('Work order created but response data is invalid:', res.data)
      ElMessage.success('工单已自动生成，请刷新页面查看')
      // Refresh the list to show the new work order
      setTimeout(fetchWorkOrders, 1000)
    }
  } catch (e: any) {
    console.error('创建工单失败:', e)
    ElMessage.error('创建失败: ' + (e?.response?.data?.detail || e.message || '未知错误'))
  } finally {
    if (loading.close) loading.close()
  }
}

async function printWorkOrder(row: any) {
  currentPrintWorkOrder.value = row;
  
  // 获取完整的工单信息，包括产品参数项
  try {
    const workorderResponse = await axios.get(`/api/workorders/${row.id}/`);
    const workorder = workorderResponse.data;
    
    // 获取产品参数项
    if (workorder.product) {
      const productResponse = await axios.get(`/api/products/${workorder.product}/`);
      const product = productResponse.data;
      
      // 获取产品图纸PDF
      let productDrawingPdf = product.drawing_pdf || '';
      
      // 如果产品没有图纸PDF，则获取所属产品类的图纸PDF
      if (!productDrawingPdf && product.category) {
        try {
          const categoryResponse = await axios.get(`/api/product-categories/${product.category}/`);
          const category = categoryResponse.data;
          productDrawingPdf = category.drawing_pdf || '';
        } catch (err) {
          console.error('获取产品类别信息失败:', err);
        }
      }
      
      // 获取工艺流程PDF
      let processPdf = '';
      
      // 优先获取工单工艺流程对应的工艺PDF
      if (workorder.process_code) {
        try {
          const processCodeResponse = await axios.get(`/api/process-codes/${workorder.process_code}/`);
          const processCode = processCodeResponse.data;
          processPdf = processCode.process_pdf || '';
        } catch (err) {
          console.error('获取工艺流程PDF失败:', err);
        }
      }
      
      // 如果工艺流程没有PDF，则获取产品所属产品类的工艺PDF
      if (!processPdf && product.category) {
        try {
          const categoryResponse = await axios.get(`/api/product-categories/${product.category}/`);
          const category = categoryResponse.data;
          processPdf = category.process_pdf || '';
        } catch (err) {
          console.error('获取产品类别工艺PDF失败:', err);
        }
      }

      // 获取产品BOM信息
      let bomItemsHtml = '<tr><td colspan="6">无BOM信息</td></tr>';
      try {
        // 查询产品的BOM
        const bomsResponse = await axios.get('/api/boms/', { 
          params: { product: workorder.product } 
        });
        const boms = bomsResponse.data.results || bomsResponse.data;
        
        if (boms && boms.length > 0) {
          // 获取最新版本的BOM
          const latestBom = boms.sort((a: any, b: any) => {
            return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
          })[0];
          
          // 获取BOM明细
          const bomResponse = await axios.get(`/api/boms/${latestBom.id}/`);
          const bomDetails = bomResponse.data;
          
          if (bomDetails && bomDetails.items && bomDetails.items.length > 0) {
            // 根据工单数量计算子零件数量
            const workorderQuantity = Number(workorder.quantity) || 0;
            
            // 获取所有物料的详细信息以获取代码
            const materialIds = bomDetails.items.map((item: any) => item.material);
            const materialsMap = new Map();
            
            // 如果有物料ID，获取详细信息
            if (materialIds.length > 0) {
              try {
                // 并行获取所有物料详情
                const materialPromises = materialIds.map((id: any) => 
                  axios.get(`/api/products/${id}/`)
                );
                const materialResponses = await Promise.all(materialPromises);
                
                // 建立ID到物料详情的映射
                materialResponses.forEach((response: any) => {
                  const material = response.data;
                  if (material && material.id) {
                    materialsMap.set(material.id, material);
                  }
                });
              } catch (err) {
                console.error('获取物料详情失败:', err);
              }
            }
            
            bomItemsHtml = bomDetails.items.map((item: any) => {
              const totalQuantity = (Number(item.quantity) * workorderQuantity).toFixed(2);
              // 从映射中获取物料详情
              const materialDetail = materialsMap.get(item.material);
              const materialCode = materialDetail ? materialDetail.code : '';
              
              return `
                <tr>
                  <td>${materialCode || ''}</td>
                  <td>${item.material_name || ''}</td>
                  <td>${item.quantity || 0}</td>
                  <td>${workorderQuantity}</td>
                  <td>${totalQuantity}</td>
                  <td>${item.remark || ''}</td>
                </tr>
              `;
            }).join('');
          }
        }
      } catch (err) {
        console.error('获取BOM信息失败:', err);
      }
      
      // 使用QRCode生成二维码
      let qrCodeDataURL = '';
      try {
        qrCodeDataURL = await QRCode.toDataURL(workorder.workorder_no, { 
          errorCorrectionLevel: 'M',
          margin: 1,
          width: 150
        });
      } catch (err) {
        console.error('生成二维码失败:', err);
        // 备用方案：使用在线服务
        qrCodeDataURL = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(workorder.workorder_no)}&qzone=1`;
      }
      
      // 生成工艺流程明细表格内容
      let processDetailsHtml = '<tr><td colspan="7">无工艺流程明细</td></tr>';
      if (workorder.process_details && workorder.process_details.length > 0) {
        processDetailsHtml = workorder.process_details.map((detail: any, index: number) => {
          // 只有第一道工序显示待加工数量，其他工序的待加工数量、已加工数量和完工数量都置空
          const pendingQty = index === 0 ? detail.pending_quantity : '';
          
          return `
            <tr>
              <td>${detail.step_no}</td>
              <td>${detail.process_name}</td>
              <td>${pendingQty}</td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
          `;
        }).join('');
      }
      
      // 生成转置后的产品参数项表格内容
      let paramColumnsHtml = '<tr><td colspan="2">无参数项</td></tr>';
      let paramValuesHtml = '<tr><td colspan="2">无参数项</td></tr>';
      
      if (product.param_values && product.param_values.length > 0) {
        paramColumnsHtml = '<tr>' + product.param_values.map((param: any) => `
          <th>${param.param_name}</th>
        `).join('') + '</tr>';
        
        paramValuesHtml = '<tr>' + product.param_values.map((param: any) => `
          <td>${param.value || ''}</td>
        `).join('') + '</tr>';
      }
      
      // 定义CSS样式
      const cssStyle = `
        @page {
          size: A4 landscape;
          margin: 1cm;
        }
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          font-size: 12px;
          background: white;
        }
        .container {
          padding: 0.8cm;
          box-sizing: border-box;
          page-break-inside: avoid;
          break-inside: avoid;
        }
        .print-header { 
          text-align: center; 
          font-size: 22px; 
          font-weight: bold; 
          margin-bottom: 20px; 
          position: relative; 
        }
        .qrcode { 
          position: absolute; 
          top: 0; 
          right: 0; 
          width: 80px; 
          height: 80px; 
        }
        .print-info { 
          margin-bottom: 15px; 
          font-size: 12px;
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-gap: 10px;
        }
        .print-info div { 
          margin-bottom: 5px; 
        }
        .tables-container {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        .params-section, .bom-section, .process-section {
          margin-bottom: 15px;
        }
        table { 
          width: 100%; 
          border-collapse: collapse; 
          font-size: 11px;
        }
        th, td { 
          border: 1px solid #ddd; 
          padding: 5px; 
          text-align: left; 
        }
        th { 
          background-color: #f2f2f2; 
        }
        h3 {
          font-size: 16px;
          margin: 15px 0 10px 0;
          border-left: 4px solid #409EFF;
          padding-left: 10px;
        }
        @media print { 
          button { 
            display: none; 
          }
          .page { 
            page-break-after: always; 
          }
          .last-page {
            page-break-after: avoid !important;
          }
          body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
        }
        .drawing-container { 
          width: 100%; 
          text-align: center;
          margin: 0;
          overflow: visible;
          max-width: 100%;
          box-sizing: border-box;
          height: auto;
        }
        .drawing-img {
          max-width: 100%;
          max-height: 620px; /* 进一步减小高度 */
          object-fit: contain;
          border: 1px solid #ddd;
          margin: 0 auto;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .signatures {
          margin-top: 30px;
          display: flex;
          justify-content: space-between;
        }
      `;
      
      // 修改printScript以支持加载两个PDF
      const printScript = `
        let productPdfLoaded = false;
        let processPdfLoaded = false;

        // PDF渲染成图片
        async function renderPDFToImage(url, imgElement, loadingId, errorId) {
          try {
            // 异步加载PDF.js
            const pdfjsLib = window.pdfjsLib;
            if (!pdfjsLib) {
              console.error('PDF.js库未加载');
              document.getElementById(errorId).style.display = 'block';
              document.getElementById(loadingId).style.display = 'none';
              return false;
            }

            // 加载PDF文档
            const loadingTask = pdfjsLib.getDocument(url);
            const pdf = await loadingTask.promise;
            
            // 获取第一页
            const page = await pdf.getPage(1);
            
            // 获取PDF页面尺寸
            const originalViewport = page.getViewport({ scale: 1.0 });
            const originalWidth = originalViewport.width;
            const originalHeight = originalViewport.height;
            const originalAspectRatio = originalWidth / originalHeight;
            
            // A4纸张尺寸 (mm): 210×297
            // 转换为像素 (96 DPI): 约 794×1123
            // 横向A4: 1123×794
            // 考虑页边距和安全距离: 减去2.5cm边距 (约95px)
            const a4WidthInPx = 1123 - 95;  // A4宽度(横向)减去页边距
            const a4HeightInPx = 794 - 95;  // A4高度(横向)减去页边距
            
            // 根据PDF原始比例计算最佳尺寸
            let finalWidth, finalHeight, scale;
            
            if (originalWidth > originalHeight) {
              // 对于横向PDF，限制宽度为A4横向宽度
              finalWidth = a4WidthInPx;
              finalHeight = finalWidth / originalAspectRatio;
              
              // 如果高度超出A4高度，则按高度缩放
              if (finalHeight > a4HeightInPx) {
                finalHeight = a4HeightInPx;
                finalWidth = finalHeight * originalAspectRatio;
              }
              
              scale = finalWidth / originalWidth;
            } else {
              // 对于纵向PDF，限制高度为A4横向高度
              finalHeight = a4HeightInPx;
              finalWidth = finalHeight * originalAspectRatio;
              
              // 如果宽度超出A4宽度，则按宽度缩放
              if (finalWidth > a4WidthInPx) {
                finalWidth = a4WidthInPx;
                finalHeight = finalWidth / originalAspectRatio;
              }
              
              scale = finalHeight / originalHeight;
            }
            
            // 应用缩放，并进一步缩小5%以确保安全
            scale = scale * 0.95;
            finalWidth = finalWidth * 0.95;
            finalHeight = finalHeight * 0.95;
            
            // 应用缩放
            const viewport = page.getViewport({ scale: scale });
            
            // 创建canvas
            const canvas = document.createElement('canvas');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            
            // 渲染到canvas
            const context = canvas.getContext('2d');
            await page.render({
              canvasContext: context,
              viewport: viewport
            }).promise;
            
            // 转换为图片URL
            const imgUrl = canvas.toDataURL('image/png');
            imgElement.src = imgUrl;
            imgElement.style.display = 'block';
            
            // 根据计算设置图片尺寸
            imgElement.style.width = finalWidth + 'px';
            imgElement.style.height = finalHeight + 'px';
            imgElement.style.maxWidth = '100%';  // 在小屏幕上自适应
            imgElement.style.boxSizing = 'border-box';
            
            document.getElementById(loadingId).style.display = 'none';
            
            return true;
          } catch (error) {
            console.error('PDF渲染失败:', error);
            document.getElementById(errorId).style.display = 'block';
            document.getElementById(loadingId).style.display = 'none';
            return false;
          }
        }
        
        // 检查是否所有PDF都已加载或超时，然后执行打印
        function checkAllPdfsAndPrint() {
          // 获取URL
          const productPdfUrl = document.getElementById('pdf-url');
          const processPdfUrl = document.getElementById('process-pdf-url');
          
          // 如果没有任何PDF，直接打印
          if (!productPdfUrl && !processPdfUrl) {
            console.log('没有PDF需要加载');
            return;
          }
          
          // 检查是否所有PDF都已加载或没有PDF
          const productPdfNeeded = productPdfUrl ? true : false;
          const processPdfNeeded = processPdfUrl ? true : false;
          
          if ((!productPdfNeeded || productPdfLoaded) && (!processPdfNeeded || processPdfLoaded)) {
            console.log('所有PDF已加载完成');
            // 不自动打印，由用户手动点击打印按钮
          }
        }
        
        // 页面加载完成后执行
        window.addEventListener('load', function() {
          // 检查产品图纸PDF
          const productPdfUrl = document.getElementById('pdf-url');
          if (productPdfUrl && productPdfUrl.value) {
            const imgElement = document.getElementById('drawing-img');
            if (imgElement) {
              // 加载PDF.js库
              const script = document.createElement('script');
              script.src = '/pdfjs/pdf.js';
              script.onload = function() {
                // 设置worker路径
                window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js';
                
                // 渲染产品图纸PDF
                renderPDFToImage(
                  productPdfUrl.value, 
                  imgElement, 
                  'pdf-loading', 
                  'pdf-error'
                ).then(success => {
                  productPdfLoaded = success;
                  checkAllPdfsAndPrint();
                });
                
                // 渲染工艺流程PDF（如果存在）
                const processPdfUrl = document.getElementById('process-pdf-url');
                if (processPdfUrl && processPdfUrl.value) {
                  const processImgElement = document.getElementById('process-pdf-img');
                  if (processImgElement) {
                    renderPDFToImage(
                      processPdfUrl.value, 
                      processImgElement, 
                      'process-pdf-loading', 
                      'process-pdf-error'
                    ).then(success => {
                      processPdfLoaded = success;
                      checkAllPdfsAndPrint();
                    });
                  } else {
                    processPdfLoaded = true;
                    checkAllPdfsAndPrint();
                  }
                } else {
                  processPdfLoaded = true;
                  checkAllPdfsAndPrint();
                }
              };
              document.head.appendChild(script);
            } else {
              productPdfLoaded = true;
              checkAllPdfsAndPrint();
            }
          } else {
            productPdfLoaded = true;
            
            // 检查工艺流程PDF
            const processPdfUrl = document.getElementById('process-pdf-url');
            if (processPdfUrl && processPdfUrl.value) {
              const processImgElement = document.getElementById('process-pdf-img');
              if (processImgElement) {
                // 加载PDF.js库
                const script = document.createElement('script');
                script.src = '/pdfjs/pdf.js';
                script.onload = function() {
                  // 设置worker路径
                  window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js';
                  
                  // 渲染工艺流程PDF
                  renderPDFToImage(
                    processPdfUrl.value, 
                    processImgElement, 
                    'process-pdf-loading', 
                    'process-pdf-error'
                  ).then(success => {
                    processPdfLoaded = success;
                    checkAllPdfsAndPrint();
                  });
                };
                document.head.appendChild(script);
              } else {
                processPdfLoaded = true;
                checkAllPdfsAndPrint();
              }
            } else {
              processPdfLoaded = true;
              checkAllPdfsAndPrint();
            }
          }
        });
        
        // 打印函数
        function printContent() {
          window.print();
        }
      `;
      
      // 确保 HTML 拼接的完整性
      let html = '<!DOCTYPE html><html><head>';
      html += '<meta charset="utf-8">';
      html += '<title>工单打印 - ' + workorder.workorder_no + '</title>';
      html += '<style>' + cssStyle + '</style>';
      html += '</head><body>';
      
      // 工单信息页面
      html += '<div class="container page">';

      // 添加工单信息
      html += `
        <div class="print-header">
          生产工单
          <img class="qrcode" src="${qrCodeDataURL}" alt="工单号二维码">
        </div>
        <div class="print-info">
          <div><strong>工单号：</strong>${workorder.workorder_no}</div>
          <div><strong>产品：</strong>${workorder.product_code} - ${workorder.product_name}</div>
          <div><strong>数量：</strong>${workorder.quantity}</div>
          <div><strong>订单号：</strong>${workorder.order_no || ''}</div>
          <div><strong>计划开始：</strong>${workorder.plan_start}</div>
          <div><strong>工艺流程：</strong>${workorder.process_code_text || ''}</div>
          <div><strong>计划结束：</strong>${workorder.plan_end}</div>
          <div><strong>备注：</strong>${workorder.remark || ''}</div>
        </div>
      `;

      // 添加产品参数项表格、BOM表格和工艺流程明细表格
      html += `
        <div class="tables-container">
          <div class="params-section">
            <h3>产品参数项</h3>
            <table>
              <thead>${paramColumnsHtml}</thead>
              <tbody>${paramValuesHtml}</tbody>
            </table>
          </div>
          
          <div class="bom-section">
            <h3>BOM清单（根据工单数量计算）</h3>
            <table>
              <thead>
                <tr>
                  <th>物料代码</th>
                  <th>物料名称</th>
                  <th>单件用量</th>
                  <th>工单数量</th>
                  <th>总用量</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>${bomItemsHtml}</tbody>
            </table>
          </div>
          
          <div class="process-section">
            <h3>工艺流程明细</h3>
            <table>
              <thead>
                <tr>
                  <th>序号</th>
                  <th>工序</th>
                  <th>待加工数量</th>
                  <th>已加工数量</th>
                  <th>完工数量</th>
                  <th>不良数量</th>
                  <th>操作者</th>
                </tr>
              </thead>
              <tbody>${processDetailsHtml}</tbody>
            </table>
          </div>
        </div>
      `;

      // 添加签名区域
      html += `
        <div class="signatures">
          <div>
            <p><strong>工单制作人：</strong>_________________</p>
          </div>
          <div>
            <p><strong>审核：</strong>_________________</p>
          </div>
        </div>
      `;
      
      html += '</div>'; // 结束第一页容器

      // 添加产品图纸页面
      if (productDrawingPdf) {
        const isLastPage = !processPdf; // 如果没有工艺流程PDF，则这是最后一页
        const pageClass = isLastPage ? 'container last-page' : 'container page';
        
        html += `
          <div class="${pageClass}">
            <input type="hidden" id="pdf-url" value="${productDrawingPdf}">
            <div class="drawing-container">
              <div id="pdf-loading" style="text-align:center;padding:20px;">
                正在加载产品图纸...
              </div>
              <div id="pdf-error" style="display:none;color:red;text-align:center;padding:20px;">
                图纸加载失败，<a href="${productDrawingPdf}" target="_blank">点击此处</a>查看或下载PDF文件
              </div>
              <img id="drawing-img" class="drawing-img" style="display:none;" alt="产品图纸" />
            </div>
          </div>
        `;
      }
      
      // 添加工艺流程PDF页面
      if (processPdf) {
        html += `
          <div class="container last-page">
            <input type="hidden" id="process-pdf-url" value="${processPdf}">
            <div class="drawing-container">
              <div id="process-pdf-loading" style="text-align:center;padding:20px;">
                正在加载工艺流程图...
              </div>
              <div id="process-pdf-error" style="display:none;color:red;text-align:center;padding:20px;">
                工艺流程图加载失败，<a href="${processPdf}" target="_blank">点击此处</a>查看或下载PDF文件
              </div>
              <img id="process-pdf-img" class="drawing-img" style="display:none;" alt="工艺流程图" />
            </div>
          </div>
        `;
      }

      // 添加脚本
      html += '<script>' + printScript + '<'+'/script>';

      // 确保结束标签正确
      html += '</body></html>';
      
      // 设置打印HTML内容
      printHtml.value = html;
      
      // 显示打印对话框
      showPrintDialog.value = true;
      
      // 在下一个tick中设置iframe内容
      setTimeout(() => {
        if (printFrame.value) {
          const doc = printFrame.value.contentDocument;
          if (doc) {
            doc.open();
            doc.write(html);
            doc.close();
          }
        }
      }, 100);
      
    } else {
      ElMessage.error('工单缺少产品信息，无法打印');
    }
  } catch (error) {
    console.error('打印工单失败:', error);
    ElMessage.error('打印工单失败');
  }
}

// 处理打印操作
function handlePrint() {
  if (printFrame.value) {
    try {
      printFrame.value.contentWindow?.print();
      
      // 询问用户是否已成功打印
      setTimeout(() => {
        if (currentPrintWorkOrder.value) {
          ElMessageBox.confirm('工单是否已成功打印？', '打印确认', {
            confirmButtonText: '已打印',
            cancelButtonText: '未打印',
            type: 'info'
          }).then(() => {
            // 更新工单状态为已打印
            if (currentPrintWorkOrder.value) {
              updateWorkOrderStatus(currentPrintWorkOrder.value.id);
            }
            handlePrintDialogClose();
          }).catch(() => {
            ElMessage({
              type: 'info',
              message: '工单状态未更新，保持"待打印"状态'
            });
          });
        }
      }, 500);
    } catch (e) {
      console.error('打印失败:', e);
      ElMessage.error('打印失败，请重试');
    }
  }
}

// 关闭打印对话框
function handlePrintDialogClose() {
  showPrintDialog.value = false;
  printHtml.value = '';
  currentPrintWorkOrder.value = null;
}

// 更新工单状态为已打印
async function updateWorkOrderStatus(workorderId: number) {
  try {
    await axios.post(`/api/workorders/${workorderId}/mark-as-printed/`);
    ElMessage.success('工单状态已更新为"已下达"');
    fetchWorkOrders(); // 刷新列表
  } catch (error) {
    console.error('更新工单状态失败:', error);
    ElMessage.error('更新工单状态失败');
  }
}

// 监听产品变化，加载对应的工艺流程代码
watch(() => workOrderForm.value.product, (newProductId) => {
  if (newProductId) {
    axios.get(`/api/product-process-codes/?product=${newProductId}`).then(res => {
      const results = res.data.results || res.data;
      // 提取工艺流程代码数据
      const processCodeIds = new Set<number>();
      const filteredProcessCodes: Array<any> = [];
      
      // 遍历结果，提取工艺流程代码
      results.forEach((item: any) => {
        const processCode = item.process_code_detail || item.process_code;
        // 避免重复添加相同的工艺流程代码
        if (processCode && !processCodeIds.has(processCode.id)) {
          processCodeIds.add(processCode.id);
          filteredProcessCodes.push(processCode);
        }
      });
      
      processCodes.value = filteredProcessCodes;
      
      // 如果有默认工艺流程，自动选择
      const defaultProcess = results.find((item: any) => item.is_default);
      if (defaultProcess) {
        const processCode = defaultProcess.process_code_detail || defaultProcess.process_code;
        workOrderForm.value.process_code = processCode.id;
      } else if (filteredProcessCodes.length > 0) {
        workOrderForm.value.process_code = filteredProcessCodes[0].id;
      } else {
        workOrderForm.value.process_code = '';
      }
    }).catch(error => {
      console.error('获取工艺流程代码失败:', error);
      processCodes.value = [];
      workOrderForm.value.process_code = '';
    });
  } else {
    // 如果没有选择产品，加载所有工艺流程代码
    axios.get('/api/process-codes/').then(res => {
      processCodes.value = res.data.results || res.data;
    });
    workOrderForm.value.process_code = '';
  }
});

// Add retry function
const retryLoading = () => {
  retryCount.value = 0
  fetchWorkOrders()
}

// 生命周期钩子
onMounted(() => {
  fetchWorkOrders()
  fetchProducts()
  fetchProcessCodes()
  fetchOrders()
})

// 在合适的位置（例如fetchWorkOrders后面）添加下面的高亮行方法
const highlightRow = (index: number) => {
  const tableRows = document.querySelectorAll('.el-table__body tr');
  if (tableRows.length > index) {
    const row = tableRows[index];
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // 添加高亮效果
    row.classList.add('highlight-row');
    
    // 3秒后移除高亮
    setTimeout(() => {
      row.classList.remove('highlight-row');
    }, 3000);
  }
}
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.workorder-container {
  .action-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .actions {
    display: flex;
    gap: 10px;
  }
}

.empty-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 60px;
  color: #909399;
  margin-bottom: 20px;
}

.error-message {
  color: #f56c6c;
  max-width: 300px;
  text-align: center;
  margin: 10px 0;
}

.print-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
    overflow: hidden;
  }
  :deep(.el-dialog__header) {
    padding: 10px 20px;
  }
  :deep(.el-dialog__headerbtn) {
    top: 15px;
  }
}

.debug-container {
  h3 {
    margin: 15px 0 10px;
    font-size: 16px;
    color: #409EFF;
    border-bottom: 1px solid #EBEEF5;
    padding-bottom: 8px;
  }
  
  .debug-section {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #F8F8F8;
    border-radius: 4px;
    
    div {
      margin-bottom: 8px;
    }
  }
  
  .test-result {
    margin-top: 15px;
    
    pre {
      background-color: #F8F8F8;
      padding: 10px;
      border-radius: 4px;
      overflow: auto;
      max-height: 200px;
      font-family: monospace;
      font-size: 12px;
    }
  }
}

.print-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f5f7fa;
}

.print-actions {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #dcdfe6;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.print-instruction {
  font-size: 14px;
  color: #606266;
}

.print-buttons {
  display: flex;
  gap: 10px;
}

.print-frame {
  flex: 1;
  height: calc(100vh - 60px); /* 保持高度减去操作栏 */
  min-height: 800px; /* 设置最小高度确保内容可见 */
  width: 100%;
  border: none;
  overflow: auto; /* 允许在需要时滚动 */
  background-color: white;
}

.highlight-row {
  background-color: #ecf5ff !important;
  transition: background-color 0.5s ease;
  border-left: 3px solid #409EFF;
}
</style>
