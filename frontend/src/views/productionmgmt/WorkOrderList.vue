<template>
  <div class="workorder-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工单管理</h2>
          <div class="actions">
            <el-button type="primary" @click="openAddWorkOrder">
              <el-icon>
                <Plus />
              </el-icon> 新增工单
            </el-button>
            <el-button type="success" @click="openCreateByOrderDialog">
              <el-icon>
                <Document />
              </el-icon> 通过订单新增
            </el-button>
            <el-button v-if="error" type="warning" @click="retryLoading">
              <el-icon>
                <RefreshRight />
              </el-icon> 重试加载
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-empty v-if="!loading && workorders.length === 0" description="暂无工单数据" :image-size="200">
        <template #image>
          <div class="empty-wrapper">
            <el-icon class="empty-icon">
              <Document />
            </el-icon>
            <div v-if="error" class="error-message">
              {{ errorMessage }}
            </div>
          </div>
        </template>
        <el-button type="primary" @click="openAddWorkOrder">新增工单</el-button>
        <el-button v-if="error" @click="retryLoading">重试加载</el-button>
      </el-empty>

      <el-table v-else :data="workorders" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="workorder_no" label="工单号" min-width="120" />
        <el-table-column label="订单号" min-width="120">
          <template #default="{ row }">
            {{ row.order_no || row.order }}
          </template>
        </el-table-column>
        <el-table-column label="产品" min-width="160">
          <template #default="{ row }">
            {{ row.product_code && row.product_name ? `${row.product_code} - ${row.product_name}` : row.product }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" min-width="80" />
        <el-table-column label="工艺流程代码" min-width="130">
          <template #default="{ row }">
            {{ row.process_code_text || row.process_code }}
          </template>
        </el-table-column>
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
                <el-icon>
                  <Edit />
                </el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click.stop="confirmDeleteWorkOrder(row)">
                <el-icon>
                  <Delete />
                </el-icon> 删除
              </el-button>
              <el-button size="small" type="info" @click.stop="viewProcessDetails(row)">
                <el-icon>
                  <View />
                </el-icon> 查看工艺明细
              </el-button>
              <el-button size="small" type="success" @click.stop="printWorkOrder(row)" v-if="row.status === 'print'">
                <el-icon>
                  <Printer />
                </el-icon> 打印工单
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
          @update:current-page="val => currentPage = val"
          @update:page-size="val => pageSize = val"
          layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" background />
      </div>
    </el-card>

    <!-- 其他对话框内容保持不变，后续继续重构 -->
    <WorkOrderFormDialog ref="workOrderFormDialogRef" :visible="showFormDialog" @update:visible="showFormDialog = $event" @saved="refreshList"
      :id="workOrderForm.value ? workOrderForm.value.id : null"
      :workorder-no="workOrderForm.value ? workOrderForm.value.workorder_no : ''"
      :order-id="workOrderForm.value ? Number(workOrderForm.value.order) : 0"
      :product-id="workOrderForm.value ? Number(workOrderForm.value.product) : 0"
      :quantity="workOrderForm.value ? Number(workOrderForm.value.quantity) : 0"
      :process-code-id="workOrderForm.value ? Number(workOrderForm.value.process_code) : 0"
      :plan-start="workOrderForm.value ? workOrderForm.value.plan_start : ''"
      :plan-end="workOrderForm.value ? workOrderForm.value.plan_end : ''"
      :status="workOrderForm.value ? workOrderForm.value.status : 'draft'"
      :remark="workOrderForm.value ? workOrderForm.value.remark : ''" :products="products" :process-codes="processCodes"
      :orders="orders" :submitting="submitting" @update:submitting="submitting = $event" />

    <el-dialog :model-value="showCreateByOrderDialog" @update:model-value="showCreateByOrderDialog = $event" title="通过订单新增工单" width="600px">
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
        <el-button @click="showCreateByOrderDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog title="工单打印预览" :model-value="showPrintDialog" @update:model-value="showPrintDialog = $event" width="90%" :before-close="handlePrintDialogClose" fullscreen
      :destroy-on-close="true" class="print-dialog">
      <div class="print-container">
        <div class="print-actions">
          <span class="print-instruction">请检查内容后点击"打印"按钮</span>
          <div class="print-buttons">
            <el-button type="primary" @click="handlePrint" icon="Printer">打印</el-button>
            <el-button @click="handlePrintDialogClose">关闭</el-button>
          </div>
        </div>
        <iframe ref="printFrame" class="print-frame" style="width:100%;border:none;" v-if="printHtml">
        </iframe>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, View, Printer, Document, RefreshRight } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import QRCode from 'qrcode'
import { useWorkOrderStore } from '../../stores/workOrderStore'
// @ts-ignore - Vue SFC没有默认导出，但在Vue项目中可以正常工作
import WorkOrderFormDialog from '../../components/production/WorkOrderFormDialog.vue'

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
  process_content?: string;
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
const showFormDialog = ref(false)
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

const workOrderStore = useWorkOrderStore()

// 表单组件引用
const workOrderFormDialogRef = ref<{ setFormData: (data: any) => void } | null>(null)

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

    // 增强工单数据，确保订单号、产品和工艺流程代码等显示字段正确
    await enhanceWorkOrderData(workorders.value);
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
    console.log('开始获取工艺流程代码列表...')
    const response = await axios.get('/api/process-codes/')
    console.log('工艺流程代码原始响应:', response.data)
    
    // 详细处理响应数据格式
    if (response.data && response.data.results) {
      // 分页格式
      processCodes.value = response.data.results
      console.log(`成功获取工艺流程代码(分页格式)，共${processCodes.value.length}条`)
    } else if (Array.isArray(response.data)) {
      // 数组格式
      processCodes.value = response.data
      console.log(`成功获取工艺流程代码(数组格式)，共${processCodes.value.length}条`)
    } else if (response.data && typeof response.data === 'object' && response.data.data) {
      // 自定义格式，带data字段
      if (Array.isArray(response.data.data)) {
        processCodes.value = response.data.data
      } else if (response.data.data.results) {
        processCodes.value = response.data.data.results
      }
      console.log(`成功获取工艺流程代码(自定义格式)，共${processCodes.value.length}条`)
    } else {
      console.warn('工艺流程代码响应格式不符合预期:', response.data)
      processCodes.value = []
    }
    
    // 确保所有工艺流程代码都有id, code和version
    processCodes.value = processCodes.value
      .filter(code => code && code.id && (code.code || code.version))
      .map(code => ({
        ...code,
        code: code.code || '未命名',
        version: code.version || '未指定'
      }))
    
    console.log('最终工艺流程代码列表:', processCodes.value)
    return processCodes.value
  } catch (error) {
    console.error('获取工艺流程代码列表失败:', error)
    const errorDetail = error.response?.data || error.message || '未知错误'
    console.error('错误详情:', errorDetail)
    ElMessage.error(`获取工艺流程代码列表失败: ${errorDetail}`)
    processCodes.value = []
    return []
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

// 添加refreshList方法
const refreshList = () => {
  fetchWorkOrders()
}

// 修改editWorkOrder方法，使用组件引用直接设置数据
const editWorkOrder = async (row: any) => {
  if (!row) {
    console.error('Cannot edit work order: row data is null or undefined')
    ElMessage.error('工单数据无效，无法编辑')
    return
  }

  console.log('Editing work order:', JSON.stringify(row))

  try {
    // 首先获取所需数据
    const loadingMessage = ElMessage({
      message: '准备表单数据中...',
      type: 'info',
      duration: 0
    })

    // 确保订单数据已加载
    if (!orders.value || orders.value.length === 0) {
      try {
        await fetchOrders()
      } catch (error) {
        console.error('Failed to load orders:', error)
        ElMessage.error('无法加载订单数据，请稍后再试')
        if (loadingMessage.close) loadingMessage.close()
        return
      }
    }

    // 确保产品数据已加载
    if (!products.value || products.value.length === 0) {
      try {
        await fetchProducts()
      } catch (error) {
        console.error('Failed to load products:', error)
        ElMessage.error('无法加载产品数据，请稍后再试')
        if (loadingMessage.close) loadingMessage.close()
        return
      }
    }

    // 确保工艺流程数据已加载
    if (!processCodes.value || processCodes.value.length === 0) {
      try {
        await fetchProcessCodes()
      } catch (error) {
        console.error('Failed to load process codes:', error)
        ElMessage.error('无法加载工艺流程数据，请稍后再试')
        if (loadingMessage.close) loadingMessage.close()
        return
      }
    }

    // 获取最新的工单详情
    try {
      const workorderResponse = await axios.get(`/api/workorders/${row.id}/`);
      const latestWorkorderData = workorderResponse.data;

      // 使用最新数据，如果获取失败则使用列表中的数据
      if (latestWorkorderData && latestWorkorderData.id) {
        row = latestWorkorderData;
        console.log('获取到最新工单数据:', JSON.stringify(latestWorkorderData));
      } else {
        console.warn('未能获取最新工单数据，使用列表中的数据');
      }
    } catch (error) {
      console.warn('获取工单详情失败，使用列表数据:', error);
    }

    // 准备编辑工单数据
    const editingWorkOrder = {
      id: row.id || null,
      workorder_no: row.workorder_no || '',
      order: Number(row.order) || 0,
      product: Number(row.product) || 0,
      quantity: row.quantity ? Number(row.quantity) : 0,
      process_code: Number(row.process_code) || 0,
      plan_start: row.plan_start || new Date().toISOString(),
      plan_end: row.plan_end || new Date().toISOString(),
      status: row.status || 'draft',
      remark: row.remark || ''
    }

    // 彻底重置工单表单对象，而不是修改现有对象
    workOrderForm.value = { ...editingWorkOrder }

    console.log('编辑工单表单数据:', JSON.stringify(workOrderForm.value));

    if (loadingMessage.close) loadingMessage.close()

    // 先关闭对话框，然后再重新打开，防止数据不更新
    showFormDialog.value = false

    // 使用nextTick确保DOM已更新
    await nextTick()

    // 直接通过引用设置表单数据
    if (workOrderFormDialogRef.value && workOrderFormDialogRef.value.setFormData) {
      console.log('使用组件引用直接设置编辑表单数据')

      // 使用setTimeout确保对话框已完全关闭
      setTimeout(() => {
        if (workOrderFormDialogRef.value) {
          workOrderFormDialogRef.value.setFormData(editingWorkOrder)

          // 再次使用setTimeout确保数据已设置后再打开对话框
          setTimeout(() => {
            console.log('准备打开对话框(编辑)，当前数据:', JSON.stringify(workOrderForm.value))
            showFormDialog.value = true
          }, 100)
        }
      }, 100)
    } else {
      // 如果引用不可用，使用普通的对话框和props传值方式
      console.log('组件引用不可用，直接打开对话框')
      showFormDialog.value = true
    }
  } catch (error) {
    console.error('Error preparing work order form:', error)
    ElMessage.error('准备编辑表单时出错，请重试')
  }
}

// 同样修改openAddWorkOrder方法
const openAddWorkOrder = async () => {
  try {
    // 首先获取所需数据
    const loadingMessage = ElMessage({
      message: '准备表单数据中...',
      type: 'info',
      duration: 0
    })

    // 确保订单数据已加载
    if (!orders.value || orders.value.length === 0) {
      try {
        await fetchOrders()
      } catch (error) {
        console.error('Failed to load orders:', error)
        ElMessage.error('无法加载订单数据，请稍后再试')
        if (loadingMessage.close) loadingMessage.close()
        return
      }
    }

    // 确保产品数据已加载
    if (!products.value || products.value.length === 0) {
      try {
        await fetchProducts()
      } catch (error) {
        console.error('Failed to load products:', error)
        ElMessage.error('无法加载产品数据，请稍后再试')
        if (loadingMessage.close) loadingMessage.close()
        return
      }
    }

    // 确保工艺流程数据已加载
    if (!processCodes.value || processCodes.value.length === 0) {
      try {
        await fetchProcessCodes()
      } catch (error) {
        console.error('Failed to load process codes:', error)
        ElMessage.error('无法加载工艺流程数据，请稍后再试')
        if (loadingMessage.close) loadingMessage.close()
        return
      }
    }

    // 初始化为空工单表单（新建模式）
    const now = new Date().toISOString()
    const futureDate = new Date()
    futureDate.setDate(futureDate.getDate() + 30)

    // 创建新工单数据
    const newWorkOrder = {
      id: null,
      workorder_no: '',
      order: 0,
      product: 0,
      quantity: 0,
      process_code: 0,
      plan_start: now,
      plan_end: futureDate.toISOString(),
      status: 'draft',
      remark: ''
    }

    // 彻底重置工单表单对象
    workOrderForm.value = { ...newWorkOrder }

    console.log('新增工单表单数据:', JSON.stringify(workOrderForm.value))

    if (loadingMessage.close) loadingMessage.close()

    // 先关闭对话框，然后再重新打开，防止数据不更新
    showFormDialog.value = false

    // 使用nextTick确保DOM已更新
    await nextTick()

    // 直接通过引用设置表单数据
    if (workOrderFormDialogRef.value && workOrderFormDialogRef.value.setFormData) {
      console.log('使用组件引用直接设置新增表单数据')

      // 使用setTimeout确保对话框已完全关闭
      setTimeout(() => {
        if (workOrderFormDialogRef.value) {
          workOrderFormDialogRef.value.setFormData(newWorkOrder)

          // 再次使用setTimeout确保数据已设置后再打开对话框
          setTimeout(() => {
            console.log('准备打开对话框(新增)，当前数据:', JSON.stringify(workOrderForm.value))
            showFormDialog.value = true
          }, 100)
        }
      }, 100)
    } else {
      // 如果引用不可用，使用普通的对话框和props传值方式
      console.log('组件引用不可用，直接打开对话框')
      showFormDialog.value = true
    }
  } catch (error) {
    console.error('准备添加工单表单失败:', error)
    ElMessage.error('准备添加工单表单失败，请重试')
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
  showFormDialog.value = false
  workOrderForm.value = { id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' }
  fetchWorkOrders()
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

    // 检查响应数据是否有效且包含ID
    if (res.data && typeof res.data === 'object' && res.data.id) {
      console.log('从订单创建工单响应:', JSON.stringify(res.data));

      // 确保所有日期类型正确
      let planStart = res.data.plan_start;
      let planEnd = res.data.plan_end;

      if (planStart) {
        planStart = new Date(planStart).toISOString();
      } else {
        const now = new Date();
        planStart = now.toISOString();
      }

      if (planEnd) {
        planEnd = new Date(planEnd).toISOString();
      } else {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + 30);
        planEnd = futureDate.toISOString();
      }

      // 创建有效的工单数据对象
      const workOrderData = {
        id: res.data.id,
        workorder_no: String(res.data.workorder_no || ''),
        order: Number(res.data.order || order.id),
        product: Number(res.data.product || 0),
        quantity: Number(res.data.quantity || 0),
        process_code: Number(res.data.process_code || 0),
        plan_start: planStart,
        plan_end: planEnd,
        status: String(res.data.status || 'draft'),
        remark: String(res.data.remark || '')
      }

      console.log('准备设置工单表单数据:', JSON.stringify(workOrderData));

      // 更新工单表单数据
      workOrderForm.value = { ...workOrderData };

      // 刷新工单列表
      await fetchWorkOrders();

      // 先关闭对话框，然后再重新打开，防止数据不更新
      showFormDialog.value = false

      // 使用nextTick确保DOM已更新
      await nextTick()

      // 直接通过引用设置表单数据
      if (workOrderFormDialogRef.value && workOrderFormDialogRef.value.setFormData) {
        console.log('使用组件引用直接设置订单创建的工单表单数据')

        // 使用setTimeout确保对话框已完全关闭
        setTimeout(() => {
          if (workOrderFormDialogRef.value) {
            workOrderFormDialogRef.value.setFormData(workOrderData)

            // 再次使用setTimeout确保数据已设置后再打开对话框
            setTimeout(() => {
              console.log('准备打开对话框(从订单创建)，当前数据:', JSON.stringify(workOrderForm.value))
              showFormDialog.value = true
              ElMessage.success('工单已自动生成，请补充完善后保存')
            }, 100)
          }
        }, 100)
      } else {
        // 如果引用不可用，使用普通的对话框和props传值方式
        console.log('组件引用不可用，直接打开对话框')
        showFormDialog.value = true
        ElMessage.success('工单已自动生成，请补充完善后保存')
      }
    } else {
      console.warn('工单已创建但响应数据无效:', res.data);
      ElMessage.success('工单已自动生成，请刷新页面查看');
      // 刷新工单列表以显示新工单
      await fetchWorkOrders();
    }
  } catch (e: any) {
    console.error('创建工单失败:', e);
    ElMessage.error('创建失败: ' + (e?.response?.data?.detail || e.message || '未知错误'));
  } finally {
    if (loading.close) loading.close();
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
                console.log('需要获取的物料ID列表:', JSON.stringify(materialIds));

                // 并行获取所有物料详情
                const materialPromises = materialIds.map((id: any) =>
                  axios.get(`/api/materials/${id}/`).catch(error => {
                    console.error(`获取物料ID=${id}的详情失败:`, error);
                    // 返回一个带有错误信息的对象，而不是抛出错误
                    return {
                      data: {
                        id: id,
                        code: null,
                        name: '未找到',
                        error: error.response?.data?.detail || error.message
                      }
                    };
                  })
                );
                const materialResponses = await Promise.all(materialPromises);

                // 输出原始API响应以便调试
                console.log('物料API原始响应:', JSON.stringify(materialResponses.map(r => r.data)));

                // 建立ID到物料详情的映射
                materialResponses.forEach((response: any) => {
                  const material = response.data;
                  if (material && material.id) {
                    // 确保ID是数字类型，用于Map查找
                    const materialId = Number(material.id);
                    materialsMap.set(materialId, material);
                    console.log(`已映射物料ID ${materialId} 到代码 ${material.code || '无代码'}`);
                  }
                });

                // 打印最终的映射表内容
                console.log('最终物料映射表内容:');
                materialsMap.forEach((value, key) => {
                  console.log(`ID: ${key}, 代码: ${value.code || '无代码'}, 名称: ${value.name || '无名称'}`);
                });
              } catch (err) {
                console.error('获取物料详情失败:', err);
              }
            }

            // 修改处理BOM项目的方式，使用Promise.all处理异步操作
            const bomItemsPromises = bomDetails.items.map(async (item: any) => {
              const totalQuantity = (Number(item.quantity) * workorderQuantity).toFixed(2);
              // 从映射中获取物料详情
              const materialId = Number(item.material);
              console.log(`处理BOM项目: 物料ID=${materialId}, 物料名称=${item.material_name}`);

              let materialCode = '(未绑定)';  // 默认显示"未绑定"而不是空白
              const materialDetail = materialsMap.get(materialId);

              if (materialDetail) {
                materialCode = materialDetail.code || '(无代码)';
                console.log(`匹配成功 - 物料ID ${materialId} 的代码: ${materialCode}`);
              } else {
                console.warn(`匹配失败 - 未找到物料ID ${materialId} 的详情`);

                // 创建一个包含物料名称的代码作为备用
                if (item.material_name) {
                  // 从物料名称中提取可能的编码
                  const nameMatch = item.material_name.match(/^([A-Za-z0-9#-]+)/);
                  if (nameMatch && nameMatch[1]) {
                    materialCode = `${nameMatch[1]}(推断)`;
                  } else {
                    materialCode = `材料-${materialId}`;
                  }
                }
              }

              return `
                <tr>
                  <td>${materialCode}</td>
                  <td>${item.material_name || ''}</td>
                  <td>${item.quantity || 0}</td>
                  <td>${workorderQuantity}</td>
                  <td>${totalQuantity}</td>
                  <td>${item.remark || ''}</td>
                </tr>
              `;
            });

            // 等待所有BOM项目处理完成
            const bomItemsHtmlArray = await Promise.all(bomItemsPromises);
            bomItemsHtml = bomItemsHtmlArray.join('');
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
      let processDetailsHtml = '<tr><td colspan="8">无工艺流程明细</td></tr>';
      if (workorder.process_details && workorder.process_details.length > 0) {
        // 如果没有工序内容数据，尝试从工艺流程明细中获取
        if (!workorder.process_details[0].process_content && workorder.process_code) {
          try {
            console.log('工序明细中缺少工序内容，尝试从工艺流程明细中获取');
            const processDetailsResponse = await axios.get(`/api/process-codes/${workorder.process_code}/details/`);
            const processDetailsData = processDetailsResponse.data.results || processDetailsResponse.data;
            
            if (processDetailsData && processDetailsData.length > 0) {
              console.log('获取到工艺流程明细数据:', processDetailsData.length, '条');
              // 创建工序号到工序内容的映射
              const processContentMap = new Map();
              processDetailsData.forEach((detail: any) => {
                if (detail.step_no && detail.process_content) {
                  processContentMap.set(detail.step_no, detail.process_content);
                }
              });
              
              // 为工单工序明细添加工序内容字段
              workorder.process_details.forEach((detail: any) => {
                if (processContentMap.has(detail.step_no)) {
                  detail.process_content = processContentMap.get(detail.step_no);
                }
              });
            }
          } catch (err) {
            console.error('获取工艺流程明细数据失败:', err);
          }
        }
        
        processDetailsHtml = workorder.process_details.map((detail: any, index: number) => {
          // 只有第一道工序显示待加工数量，其他工序的待加工数量、已加工数量和完工数量都置空
          const pendingQty = index === 0 ? detail.pending_quantity : '';

          return `
            <tr>
              <td>${detail.step_no}</td>
              <td>${detail.process_name}</td>
              <td>${detail.process_content || ''}</td>
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
        }
        .info-row {
          display: flex;
          margin-bottom: 10px;
        }
        .info-row div {
          flex: 1;
          margin-right: 10px;
        }
        .product-info {
          flex: 2 !important;
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
          <div class="info-row">
            <div><strong>工单号：</strong>${workorder.workorder_no}</div>
            <div class="product-info"><strong>产品：</strong>${workorder.product_code} - ${workorder.product_name}</div>
            <div><strong>数量：</strong>${workorder.quantity}</div>
          </div>
          <div class="info-row">
            <div><strong>订单号：</strong>${workorder.order_no || ''}</div>
            <div><strong>计划开始：</strong>${formatDate(workorder.plan_start)}</div>
            <div><strong>计划结束：</strong>${formatDate(workorder.plan_end)}</div>
          </div>
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
                  <th>工序内容</th>
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
      html += '<script>' + printScript + '<' + '/script>';

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
onMounted(async () => {
  try {
    // 按顺序加载数据
    await fetchProcessCodes()
    console.log(`初始化完成，工艺流程代码列表包含${processCodes.value.length}条数据`)
    
    await fetchProducts()
    console.log(`产品列表包含${products.value.length}条数据`)
    
    await fetchOrders()
    console.log(`订单列表包含${orders.value.length}条数据`)
    
    await fetchWorkOrders()
    console.log(`工单列表包含${workorders.value.length}条数据`)
  } catch (error) {
    console.error('初始化数据加载失败:', error)
    ElMessage.error('初始化数据加载失败，请刷新页面重试')
  }
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

// 增强工单数据，添加可读的产品名称、订单号和工艺流程代码
const enhanceWorkOrderData = async (workorderList: any[]) => {
  try {
    if (!workorderList || workorderList.length === 0) return;

    // 先确保相关数据已加载
    if (products.value.length === 0) await fetchProducts();
    if (orders.value.length === 0) await fetchOrders();
    if (processCodes.value.length === 0) await fetchProcessCodes();

    // 创建查找映射
    const productMap = new Map(products.value.map(p => [p.id, p]));
    const orderMap = new Map(orders.value.map(o => [o.id, o]));
    const processCodeMap = new Map(processCodes.value.map(p => [p.id, p]));

    // 处理每个工单
    workorderList.forEach(workorder => {
      // 产品信息
      if (workorder.product && productMap.has(Number(workorder.product))) {
        const product = productMap.get(Number(workorder.product));
        if (product) {
          workorder.product_code = product.code;
          workorder.product_name = product.name;
        }
      }

      // 订单信息
      if (workorder.order && orderMap.has(Number(workorder.order))) {
        const order = orderMap.get(Number(workorder.order));
        if (order) {
          workorder.order_no = order.order_no;
        }
      }

      // 工艺流程代码信息
      if (workorder.process_code && processCodeMap.has(Number(workorder.process_code))) {
        const processCode = processCodeMap.get(Number(workorder.process_code));
        if (processCode) {
          workorder.process_code_text = `${processCode.code} - ${processCode.version}`;
        }
      }
    });

    console.log('工单数据增强完成，增加了可读字段');
  } catch (error) {
    console.error('增强工单数据时出错:', error);
  }
}

// 在printWorkOrder函数之前添加日期格式化函数
function formatDate(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString;
  
  // 格式化为MM/DD/YY
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const year = String(date.getFullYear()).slice(-2);
  
  return `${month}/${day}/${year}`;
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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
  height: calc(100vh - 60px);
  /* 保持高度减去操作栏 */
  min-height: 800px;
  /* 设置最小高度确保内容可见 */
  width: 100%;
  border: none;
  overflow: auto;
  /* 允许在需要时滚动 */
  background-color: white;
}

.highlight-row {
  background-color: #ecf5ff !important;
  transition: background-color 0.5s ease;
  border-left: 3px solid #409EFF;
}
</style>
